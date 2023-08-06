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
        jegle__gfbsd = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(jegle__gfbsd)
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
        reciw__oto = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, reciw__oto)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    mpw__cuqu = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    ycqx__lcjmq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    dnnm__ddjn = cgutils.get_or_insert_function(builder.module, ycqx__lcjmq,
        name='initialize_csv_reader')
    zmc__equre = cgutils.create_struct_proxy(types.stream_reader_type)(context,
        builder, value=mpw__cuqu.csv_reader)
    builder.call(dnnm__ddjn, [zmc__equre.pyobj])
    builder.store(context.get_constant(types.uint64, 0), mpw__cuqu.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [bhyhx__kst] = sig.args
    [rlaa__jpe] = args
    mpw__cuqu = cgutils.create_struct_proxy(bhyhx__kst)(context, builder,
        value=rlaa__jpe)
    ycqx__lcjmq = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    dnnm__ddjn = cgutils.get_or_insert_function(builder.module, ycqx__lcjmq,
        name='update_csv_reader')
    zmc__equre = cgutils.create_struct_proxy(types.stream_reader_type)(context,
        builder, value=mpw__cuqu.csv_reader)
    mncni__quvhh = builder.call(dnnm__ddjn, [zmc__equre.pyobj])
    result.set_valid(mncni__quvhh)
    with builder.if_then(mncni__quvhh):
        mdxs__ltw = builder.load(mpw__cuqu.index)
        aoya__xrh = types.Tuple([sig.return_type.first_type, types.int64])
        grl__wrhv = gen_read_csv_objmode(sig.args[0])
        kan__hvx = signature(aoya__xrh, types.stream_reader_type, types.int64)
        msq__ziz = context.compile_internal(builder, grl__wrhv, kan__hvx, [
            mpw__cuqu.csv_reader, mdxs__ltw])
        qsvb__rfuz, hsg__jgkmd = cgutils.unpack_tuple(builder, msq__ziz)
        hvjbj__dvwgh = builder.add(mdxs__ltw, hsg__jgkmd, flags=['nsw'])
        builder.store(hvjbj__dvwgh, mpw__cuqu.index)
        result.yield_(qsvb__rfuz)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        qsqsj__exg = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        qsqsj__exg.csv_reader = args[0]
        wyi__ppivk = context.get_constant(types.uintp, 0)
        qsqsj__exg.index = cgutils.alloca_once_value(builder, wyi__ppivk)
        return qsqsj__exg._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    ogfol__vcb = csv_iterator_typeref.instance_type
    sig = signature(ogfol__vcb, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    bbli__haow = 'def read_csv_objmode(f_reader):\n'
    pxb__qgzf = [sanitize_varname(clkuq__ugb) for clkuq__ugb in
        csv_iterator_type._out_colnames]
    qxrmy__bpi = ir_utils.next_label()
    tpu__aiwp = globals()
    out_types = csv_iterator_type._out_types
    tpu__aiwp[f'table_type_{qxrmy__bpi}'] = TableType(tuple(out_types))
    tpu__aiwp[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    iiwp__evkcq = list(range(len(csv_iterator_type._usecols)))
    bbli__haow += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        pxb__qgzf, out_types, csv_iterator_type._usecols, iiwp__evkcq,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, qxrmy__bpi, tpu__aiwp, parallel
        =False, check_parallel_runtime=True, idx_col_index=
        csv_iterator_type._index_ind, idx_col_typ=csv_iterator_type.
        _index_arr_typ)
    qcrcq__lgy = bodo.ir.csv_ext._gen_parallel_flag_name(pxb__qgzf)
    wrk__wtgpz = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [qcrcq__lgy]
    bbli__haow += f"  return {', '.join(wrk__wtgpz)}"
    tpu__aiwp = globals()
    sto__hkbx = {}
    exec(bbli__haow, tpu__aiwp, sto__hkbx)
    yzvl__eqxgl = sto__hkbx['read_csv_objmode']
    rpq__gjj = numba.njit(yzvl__eqxgl)
    bodo.ir.csv_ext.compiled_funcs.append(rpq__gjj)
    sojf__epj = 'def read_func(reader, local_start):\n'
    sojf__epj += f"  {', '.join(wrk__wtgpz)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        sojf__epj += f'  local_len = len(T)\n'
        sojf__epj += '  total_size = local_len\n'
        sojf__epj += f'  if ({qcrcq__lgy}):\n'
        sojf__epj += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        sojf__epj += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        egqip__hdi = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        sojf__epj += '  total_size = 0\n'
        egqip__hdi = (
            f'bodo.utils.conversion.convert_to_index({wrk__wtgpz[1]}, {csv_iterator_type._index_name!r})'
            )
    sojf__epj += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({wrk__wtgpz[0]},), {egqip__hdi}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(sojf__epj, {'bodo': bodo, 'objmode_func': rpq__gjj, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, sto__hkbx)
    return sto__hkbx['read_func']
