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
        eizp__txp = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(eizp__txp)
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
        aiji__bpkuy = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, aiji__bpkuy)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    bdyjy__zjkkk = cgutils.create_struct_proxy(sig.args[0])(context,
        builder, value=args[0])
    ogi__kvpl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer()])
    fhj__veiud = cgutils.get_or_insert_function(builder.module, ogi__kvpl,
        name='initialize_csv_reader')
    hsqyc__ujkuk = cgutils.create_struct_proxy(types.stream_reader_type)(
        context, builder, value=bdyjy__zjkkk.csv_reader)
    builder.call(fhj__veiud, [hsqyc__ujkuk.pyobj])
    builder.store(context.get_constant(types.uint64, 0), bdyjy__zjkkk.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [cxyq__lbgdj] = sig.args
    [beox__amic] = args
    bdyjy__zjkkk = cgutils.create_struct_proxy(cxyq__lbgdj)(context,
        builder, value=beox__amic)
    ogi__kvpl = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer()])
    fhj__veiud = cgutils.get_or_insert_function(builder.module, ogi__kvpl,
        name='update_csv_reader')
    hsqyc__ujkuk = cgutils.create_struct_proxy(types.stream_reader_type)(
        context, builder, value=bdyjy__zjkkk.csv_reader)
    pnmg__gozj = builder.call(fhj__veiud, [hsqyc__ujkuk.pyobj])
    result.set_valid(pnmg__gozj)
    with builder.if_then(pnmg__gozj):
        rii__wxdv = builder.load(bdyjy__zjkkk.index)
        jsci__bhmr = types.Tuple([sig.return_type.first_type, types.int64])
        zzs__uka = gen_read_csv_objmode(sig.args[0])
        wqauj__lvh = signature(jsci__bhmr, types.stream_reader_type, types.
            int64)
        prn__xolif = context.compile_internal(builder, zzs__uka, wqauj__lvh,
            [bdyjy__zjkkk.csv_reader, rii__wxdv])
        krl__gdygx, ckbpn__jazom = cgutils.unpack_tuple(builder, prn__xolif)
        hljr__renq = builder.add(rii__wxdv, ckbpn__jazom, flags=['nsw'])
        builder.store(hljr__renq, bdyjy__zjkkk.index)
        result.yield_(krl__gdygx)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        fgg__qgrqi = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        fgg__qgrqi.csv_reader = args[0]
        bjoyv__tvvrq = context.get_constant(types.uintp, 0)
        fgg__qgrqi.index = cgutils.alloca_once_value(builder, bjoyv__tvvrq)
        return fgg__qgrqi._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    dbt__ujfbf = csv_iterator_typeref.instance_type
    sig = signature(dbt__ujfbf, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    zniw__jsv = 'def read_csv_objmode(f_reader):\n'
    hyuv__xbnub = [sanitize_varname(lcoo__myfqc) for lcoo__myfqc in
        csv_iterator_type._out_colnames]
    giq__yyul = ir_utils.next_label()
    abg__ocw = globals()
    out_types = csv_iterator_type._out_types
    abg__ocw[f'table_type_{giq__yyul}'] = TableType(tuple(out_types))
    abg__ocw[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    tyju__ogv = list(range(len(csv_iterator_type._usecols)))
    zniw__jsv += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        hyuv__xbnub, out_types, csv_iterator_type._usecols, tyju__ogv,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, giq__yyul, abg__ocw, parallel=
        False, check_parallel_runtime=True, idx_col_index=csv_iterator_type
        ._index_ind, idx_col_typ=csv_iterator_type._index_arr_typ)
    fvbal__zets = bodo.ir.csv_ext._gen_parallel_flag_name(hyuv__xbnub)
    qrg__xna = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [fvbal__zets]
    zniw__jsv += f"  return {', '.join(qrg__xna)}"
    abg__ocw = globals()
    wmfsf__xsd = {}
    exec(zniw__jsv, abg__ocw, wmfsf__xsd)
    ywpt__rnw = wmfsf__xsd['read_csv_objmode']
    hdn__zekr = numba.njit(ywpt__rnw)
    bodo.ir.csv_ext.compiled_funcs.append(hdn__zekr)
    yff__xon = 'def read_func(reader, local_start):\n'
    yff__xon += f"  {', '.join(qrg__xna)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        yff__xon += f'  local_len = len(T)\n'
        yff__xon += '  total_size = local_len\n'
        yff__xon += f'  if ({fvbal__zets}):\n'
        yff__xon += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        yff__xon += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        rxn__tqipt = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        yff__xon += '  total_size = 0\n'
        rxn__tqipt = (
            f'bodo.utils.conversion.convert_to_index({qrg__xna[1]}, {csv_iterator_type._index_name!r})'
            )
    yff__xon += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({qrg__xna[0]},), {rxn__tqipt}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(yff__xon, {'bodo': bodo, 'objmode_func': hdn__zekr, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, wmfsf__xsd)
    return wmfsf__xsd['read_func']
