"""
Class information for DataFrame iterators returned by pd.read_csv. This is used
to handle situations in which pd.read_csv is used to return chunks with separate
read calls instead of just a single read.
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, models, register_model
import bodo
import bodo.ir.connector
import bodo.ir.csv_ext
from bodo import objmode
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.table import Table, TableType
from bodo.io import csv_cpp
from bodo.ir.csv_ext import _gen_read_csv_objmode, astype
from bodo.utils.typing import ColNamesMetaType
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname
ll.add_symbol('update_csv_reader', csv_cpp.update_csv_reader)
ll.add_symbol('initialize_csv_reader', csv_cpp.initialize_csv_reader)


class CSVIteratorType(types.SimpleIteratorType):

    def __init__(self, df_type, out_colnames, out_types, usecols, sep,
        index_ind, index_arr_typ, index_name, escapechar, storage_options):
        assert isinstance(df_type, DataFrameType
            ), 'CSVIterator must return a DataFrame'
        cpr__qyj = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(cpr__qyj)
        self._yield_type = df_type
        self._out_colnames = out_colnames
        self._out_types = out_types
        self._usecols = usecols
        self._sep = sep
        self._index_ind = index_ind
        self._index_arr_typ = index_arr_typ
        self._index_name = index_name
        self._escapechar = escapechar
        self._storage_options = storage_options

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(CSVIteratorType)
class CSVIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fpn__idgrw = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, fpn__idgrw)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    jpyn__blhh = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    fzhk__xzmko = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    pgvy__wrkwf = cgutils.get_or_insert_function(builder.module,
        fzhk__xzmko, name='initialize_csv_reader')
    orkrt__sokdb = cgutils.create_struct_proxy(types.stream_reader_type)(
        context, builder, value=jpyn__blhh.csv_reader)
    builder.call(pgvy__wrkwf, [orkrt__sokdb.pyobj])
    builder.store(context.get_constant(types.uint64, 0), jpyn__blhh.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [yjbft__wwdjh] = sig.args
    [obvz__jbjyx] = args
    jpyn__blhh = cgutils.create_struct_proxy(yjbft__wwdjh)(context, builder,
        value=obvz__jbjyx)
    fzhk__xzmko = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    pgvy__wrkwf = cgutils.get_or_insert_function(builder.module,
        fzhk__xzmko, name='update_csv_reader')
    orkrt__sokdb = cgutils.create_struct_proxy(types.stream_reader_type)(
        context, builder, value=jpyn__blhh.csv_reader)
    rtmt__ywymr = builder.call(pgvy__wrkwf, [orkrt__sokdb.pyobj])
    result.set_valid(rtmt__ywymr)
    with builder.if_then(rtmt__ywymr):
        yajgf__epfuy = builder.load(jpyn__blhh.index)
        jef__mjfu = types.Tuple([sig.return_type.first_type, types.int64])
        gkvbp__qxm = gen_read_csv_objmode(sig.args[0])
        tkeqa__pltq = signature(jef__mjfu, types.stream_reader_type, types.
            int64)
        dman__tufux = context.compile_internal(builder, gkvbp__qxm,
            tkeqa__pltq, [jpyn__blhh.csv_reader, yajgf__epfuy])
        rba__pdtx, fofb__reeqt = cgutils.unpack_tuple(builder, dman__tufux)
        waqw__wtdgi = builder.add(yajgf__epfuy, fofb__reeqt, flags=['nsw'])
        builder.store(waqw__wtdgi, jpyn__blhh.index)
        result.yield_(rba__pdtx)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        htz__xkucg = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        htz__xkucg.csv_reader = args[0]
        jzp__qkdqa = context.get_constant(types.uintp, 0)
        htz__xkucg.index = cgutils.alloca_once_value(builder, jzp__qkdqa)
        return htz__xkucg._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    nmzps__xtrn = csv_iterator_typeref.instance_type
    sig = signature(nmzps__xtrn, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    adw__czx = 'def read_csv_objmode(f_reader):\n'
    rhz__ttu = [sanitize_varname(ldfy__onz) for ldfy__onz in
        csv_iterator_type._out_colnames]
    lpjt__nucdd = ir_utils.next_label()
    xfwf__ikwx = globals()
    out_types = csv_iterator_type._out_types
    xfwf__ikwx[f'table_type_{lpjt__nucdd}'] = TableType(tuple(out_types))
    xfwf__ikwx[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    tdwkj__dff = list(range(len(csv_iterator_type._usecols)))
    adw__czx += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        rhz__ttu, out_types, csv_iterator_type._usecols, tdwkj__dff,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, lpjt__nucdd, xfwf__ikwx,
        parallel=False, check_parallel_runtime=True, idx_col_index=
        csv_iterator_type._index_ind, idx_col_typ=csv_iterator_type.
        _index_arr_typ)
    ppyta__yylez = bodo.ir.csv_ext._gen_parallel_flag_name(rhz__ttu)
    ztwi__cuy = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [ppyta__yylez]
    adw__czx += f"  return {', '.join(ztwi__cuy)}"
    xfwf__ikwx = globals()
    mmti__cea = {}
    exec(adw__czx, xfwf__ikwx, mmti__cea)
    sshi__nwfk = mmti__cea['read_csv_objmode']
    ssp__sjk = numba.njit(sshi__nwfk)
    bodo.ir.csv_ext.compiled_funcs.append(ssp__sjk)
    kqasb__ypx = 'def read_func(reader, local_start):\n'
    kqasb__ypx += f"  {', '.join(ztwi__cuy)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        kqasb__ypx += f'  local_len = len(T)\n'
        kqasb__ypx += '  total_size = local_len\n'
        kqasb__ypx += f'  if ({ppyta__yylez}):\n'
        kqasb__ypx += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        kqasb__ypx += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        flco__rly = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        kqasb__ypx += '  total_size = 0\n'
        flco__rly = (
            f'bodo.utils.conversion.convert_to_index({ztwi__cuy[1]}, {csv_iterator_type._index_name!r})'
            )
    kqasb__ypx += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({ztwi__cuy[0]},), {flco__rly}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(kqasb__ypx, {'bodo': bodo, 'objmode_func': ssp__sjk, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, mmti__cea)
    return mmti__cea['read_func']
