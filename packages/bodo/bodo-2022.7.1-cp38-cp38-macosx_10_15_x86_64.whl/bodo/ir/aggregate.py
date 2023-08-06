"""IR node for the groupby"""
import ctypes
import operator
import types as pytypes
from collections import defaultdict, namedtuple
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, compiler, ir, ir_utils, types
from numba.core.analysis import compute_use_defs
from numba.core.ir_utils import build_definitions, compile_to_numba_ir, find_callname, find_const, find_topo_order, get_definition, get_ir_of_code, get_name_var_table, guard, is_getitem, mk_unique_var, next_label, remove_dels, replace_arg_nodes, replace_var_names, replace_vars_inner, visit_vars_inner
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic
from numba.parfors.parfor import Parfor, unwrap_parfor_blocks, wrap_parfor_blocks
import bodo
from bodo.hiframes.datetime_date_ext import DatetimeDateArrayType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, decref_table_array, delete_info_decref_array, delete_table, delete_table_decref_arrays, groupby_and_aggregate, info_from_table, info_to_array, py_data_to_cpp_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, pre_alloc_array_item_array
from bodo.libs.binary_arr_ext import BinaryArrayType, pre_alloc_binary_array
from bodo.libs.bool_arr_ext import BooleanArrayType
from bodo.libs.decimal_arr_ext import DecimalArrayType, alloc_decimal_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, _find_used_columns, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.transform import get_call_expr_arg
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, list_cumulative, to_str_arr_if_dict_array, type_has_unknown_cats, unwrap_typeref
from bodo.utils.utils import gen_getitem, incref, is_assign, is_call_assign, is_expr, is_null_pointer, is_var_assign
gb_agg_cfunc = {}
gb_agg_cfunc_addr = {}


@intrinsic
def add_agg_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        vncay__kcb = func.signature
        if vncay__kcb == types.none(types.voidptr):
            uner__hqrn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            npg__awfn = cgutils.get_or_insert_function(builder.module,
                uner__hqrn, sym._literal_value)
            builder.call(npg__awfn, [context.get_constant_null(vncay__kcb.
                args[0])])
        elif vncay__kcb == types.none(types.int64, types.voidptr, types.voidptr
            ):
            uner__hqrn = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            npg__awfn = cgutils.get_or_insert_function(builder.module,
                uner__hqrn, sym._literal_value)
            builder.call(npg__awfn, [context.get_constant(types.int64, 0),
                context.get_constant_null(vncay__kcb.args[1]), context.
                get_constant_null(vncay__kcb.args[2])])
        else:
            uner__hqrn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            npg__awfn = cgutils.get_or_insert_function(builder.module,
                uner__hqrn, sym._literal_value)
            builder.call(npg__awfn, [context.get_constant_null(vncay__kcb.
                args[0]), context.get_constant_null(vncay__kcb.args[1]),
                context.get_constant_null(vncay__kcb.args[2])])
        context.add_linking_libs([gb_agg_cfunc[sym._literal_value]._library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_agg_udf_addr(name):
    with numba.objmode(addr='int64'):
        addr = gb_agg_cfunc_addr[name]
    return addr


class AggUDFStruct(object):

    def __init__(self, regular_udf_funcs=None, general_udf_funcs=None):
        assert regular_udf_funcs is not None or general_udf_funcs is not None
        self.regular_udfs = False
        self.general_udfs = False
        self.regular_udf_cfuncs = None
        self.general_udf_cfunc = None
        if regular_udf_funcs is not None:
            (self.var_typs, self.init_func, self.update_all_func, self.
                combine_all_func, self.eval_all_func) = regular_udf_funcs
            self.regular_udfs = True
        if general_udf_funcs is not None:
            self.general_udf_funcs = general_udf_funcs
            self.general_udfs = True

    def set_regular_cfuncs(self, update_cb, combine_cb, eval_cb):
        assert self.regular_udfs and self.regular_udf_cfuncs is None
        self.regular_udf_cfuncs = [update_cb, combine_cb, eval_cb]

    def set_general_cfunc(self, general_udf_cb):
        assert self.general_udfs and self.general_udf_cfunc is None
        self.general_udf_cfunc = general_udf_cb


AggFuncStruct = namedtuple('AggFuncStruct', ['func', 'ftype'])
supported_agg_funcs = ['no_op', 'ngroup', 'head', 'transform', 'size',
    'shift', 'sum', 'count', 'nunique', 'median', 'cumsum', 'cumprod',
    'cummin', 'cummax', 'mean', 'min', 'max', 'prod', 'first', 'last',
    'idxmin', 'idxmax', 'var', 'std', 'udf', 'gen_udf']
supported_transform_funcs = ['no_op', 'sum', 'count', 'nunique', 'median',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'var', 'std']


def get_agg_func(func_ir, func_name, rhs, series_type=None, typemap=None):
    if func_name == 'no_op':
        raise BodoError('Unknown aggregation function used in groupby.')
    if series_type is None:
        series_type = SeriesType(types.float64)
    if func_name in {'var', 'std'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 3
        func.ncols_post_shuffle = 4
        return func
    if func_name in {'first', 'last'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        return func
    if func_name in {'idxmin', 'idxmax'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 2
        func.ncols_post_shuffle = 2
        return func
    if func_name in supported_agg_funcs[:-8]:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        bagwn__qir = True
        aetc__numyp = 1
        hkt__xif = -1
        if isinstance(rhs, ir.Expr):
            for dhjo__gpki in rhs.kws:
                if func_name in list_cumulative:
                    if dhjo__gpki[0] == 'skipna':
                        bagwn__qir = guard(find_const, func_ir, dhjo__gpki[1])
                        if not isinstance(bagwn__qir, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if dhjo__gpki[0] == 'dropna':
                        bagwn__qir = guard(find_const, func_ir, dhjo__gpki[1])
                        if not isinstance(bagwn__qir, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            aetc__numyp = get_call_expr_arg('shift', rhs.args, dict(rhs.kws
                ), 0, 'periods', aetc__numyp)
            aetc__numyp = guard(find_const, func_ir, aetc__numyp)
        if func_name == 'head':
            hkt__xif = get_call_expr_arg('head', rhs.args, dict(rhs.kws), 0,
                'n', 5)
            if not isinstance(hkt__xif, int):
                hkt__xif = guard(find_const, func_ir, hkt__xif)
            if hkt__xif < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = bagwn__qir
        func.periods = aetc__numyp
        func.head_n = hkt__xif
        if func_name == 'transform':
            kws = dict(rhs.kws)
            wgg__egu = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            gsceg__zwr = typemap[wgg__egu.name]
            khtct__pgr = None
            if isinstance(gsceg__zwr, str):
                khtct__pgr = gsceg__zwr
            elif is_overload_constant_str(gsceg__zwr):
                khtct__pgr = get_overload_const_str(gsceg__zwr)
            elif bodo.utils.typing.is_builtin_function(gsceg__zwr):
                khtct__pgr = bodo.utils.typing.get_builtin_function_name(
                    gsceg__zwr)
            if khtct__pgr not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {khtct__pgr}')
            func.transform_func = supported_agg_funcs.index(khtct__pgr)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    wgg__egu = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if wgg__egu == '':
        gsceg__zwr = types.none
    else:
        gsceg__zwr = typemap[wgg__egu.name]
    if is_overload_constant_dict(gsceg__zwr):
        etk__vur = get_overload_constant_dict(gsceg__zwr)
        gspr__sjsc = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in etk__vur.values()]
        return gspr__sjsc
    if gsceg__zwr == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(gsceg__zwr, types.BaseTuple) or is_overload_constant_list(
        gsceg__zwr):
        gspr__sjsc = []
        once__grnr = 0
        if is_overload_constant_list(gsceg__zwr):
            ehko__dtg = get_overload_const_list(gsceg__zwr)
        else:
            ehko__dtg = gsceg__zwr.types
        for t in ehko__dtg:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                gspr__sjsc.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(ehko__dtg) > 1:
                    func.fname = '<lambda_' + str(once__grnr) + '>'
                    once__grnr += 1
                gspr__sjsc.append(func)
        return [gspr__sjsc]
    if is_overload_constant_str(gsceg__zwr):
        func_name = get_overload_const_str(gsceg__zwr)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(gsceg__zwr):
        func_name = bodo.utils.typing.get_builtin_function_name(gsceg__zwr)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    assert typemap is not None, 'typemap is required for agg UDF handling'
    func = _get_const_agg_func(typemap[rhs.args[0].name], func_ir)
    func.ftype = 'udf'
    func.fname = _get_udf_name(func)
    return func


def get_agg_func_udf(func_ir, f_val, rhs, series_type, typemap):
    if isinstance(f_val, str):
        return get_agg_func(func_ir, f_val, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(f_val):
        func_name = bodo.utils.typing.get_builtin_function_name(f_val)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if isinstance(f_val, (tuple, list)):
        once__grnr = 0
        nymbq__zgt = []
        for ngi__guv in f_val:
            func = get_agg_func_udf(func_ir, ngi__guv, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{once__grnr}>'
                once__grnr += 1
            nymbq__zgt.append(func)
        return nymbq__zgt
    else:
        assert is_expr(f_val, 'make_function') or isinstance(f_val, (numba.
            core.registry.CPUDispatcher, types.Dispatcher))
        assert typemap is not None, 'typemap is required for agg UDF handling'
        func = _get_const_agg_func(f_val, func_ir)
        func.ftype = 'udf'
        func.fname = _get_udf_name(func)
        return func


def _get_udf_name(func):
    code = func.code if hasattr(func, 'code') else func.__code__
    khtct__pgr = code.co_name
    return khtct__pgr


def _get_const_agg_func(func_typ, func_ir):
    agg_func = get_overload_const_func(func_typ, func_ir)
    if is_expr(agg_func, 'make_function'):

        def agg_func_wrapper(A):
            return A
        agg_func_wrapper.__code__ = agg_func.code
        agg_func = agg_func_wrapper
        return agg_func
    return agg_func


@infer_global(type)
class TypeDt64(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if len(args) == 1 and isinstance(args[0], (types.NPDatetime, types.
            NPTimedelta)):
            lopwy__dngdo = types.DType(args[0])
            return signature(lopwy__dngdo, *args)


class Aggregate(ir.Stmt):

    def __init__(self, df_out, df_in, key_names, gb_info_in, gb_info_out,
        out_vars, in_vars, in_key_inds, df_in_type, out_type,
        input_has_index, same_index, return_key, loc, func_name, dropna,
        _num_shuffle_keys):
        self.df_out = df_out
        self.df_in = df_in
        self.key_names = key_names
        self.gb_info_in = gb_info_in
        self.gb_info_out = gb_info_out
        self.out_vars = out_vars
        self.in_vars = in_vars
        self.in_key_inds = in_key_inds
        self.df_in_type = df_in_type
        self.out_type = out_type
        self.input_has_index = input_has_index
        self.same_index = same_index
        self.return_key = return_key
        self.loc = loc
        self.func_name = func_name
        self.dropna = dropna
        self._num_shuffle_keys = _num_shuffle_keys
        self.dead_in_inds = set()
        self.dead_out_inds = set()

    def get_live_in_vars(self):
        return [kybzi__sgmtc for kybzi__sgmtc in self.in_vars if 
            kybzi__sgmtc is not None]

    def get_live_out_vars(self):
        return [kybzi__sgmtc for kybzi__sgmtc in self.out_vars if 
            kybzi__sgmtc is not None]

    @property
    def is_in_table_format(self):
        return self.df_in_type.is_table_format

    @property
    def n_in_table_arrays(self):
        return len(self.df_in_type.columns
            ) if self.df_in_type.is_table_format else 1

    @property
    def n_in_cols(self):
        return self.n_in_table_arrays + len(self.in_vars) - 1

    @property
    def in_col_types(self):
        return list(self.df_in_type.data) + list(get_index_data_arr_types(
            self.df_in_type.index))

    @property
    def is_output_table(self):
        return not isinstance(self.out_type, SeriesType)

    @property
    def n_out_table_arrays(self):
        return len(self.out_type.table_type.arr_types) if not isinstance(self
            .out_type, SeriesType) else 1

    @property
    def n_out_cols(self):
        return self.n_out_table_arrays + len(self.out_vars) - 1

    @property
    def out_col_types(self):
        eao__tjado = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        gwpc__euerg = list(get_index_data_arr_types(self.out_type.index))
        return eao__tjado + gwpc__euerg

    def update_dead_col_info(self):
        for tkzqc__kut in self.dead_out_inds:
            self.gb_info_out.pop(tkzqc__kut, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for udwi__zkiwq, zkdw__hesl in self.gb_info_in.copy().items():
            ttn__czer = []
            for ngi__guv, ejo__gtoz in zkdw__hesl:
                if ejo__gtoz not in self.dead_out_inds:
                    ttn__czer.append((ngi__guv, ejo__gtoz))
            if not ttn__czer:
                if (udwi__zkiwq is not None and udwi__zkiwq not in self.
                    in_key_inds):
                    self.dead_in_inds.add(udwi__zkiwq)
                self.gb_info_in.pop(udwi__zkiwq)
            else:
                self.gb_info_in[udwi__zkiwq] = ttn__czer
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for jrd__hta in range(1, len(self.in_vars)):
                tkzqc__kut = self.n_in_table_arrays + jrd__hta - 1
                if tkzqc__kut in self.dead_in_inds:
                    self.in_vars[jrd__hta] = None
        else:
            for jrd__hta in range(len(self.in_vars)):
                if jrd__hta in self.dead_in_inds:
                    self.in_vars[jrd__hta] = None

    def __repr__(self):
        cgen__prfe = ', '.join(kybzi__sgmtc.name for kybzi__sgmtc in self.
            get_live_in_vars())
        nduq__vtdu = f'{self.df_in}{{{cgen__prfe}}}'
        wkkbe__wctlw = ', '.join(kybzi__sgmtc.name for kybzi__sgmtc in self
            .get_live_out_vars())
        ugfh__xmpr = f'{self.df_out}{{{wkkbe__wctlw}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {nduq__vtdu} {ugfh__xmpr}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({kybzi__sgmtc.name for kybzi__sgmtc in aggregate_node.
        get_live_in_vars()})
    def_set.update({kybzi__sgmtc.name for kybzi__sgmtc in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    jgei__imq = agg_node.out_vars[0]
    if jgei__imq is not None and jgei__imq.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            csh__wgxto = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(csh__wgxto)
        else:
            agg_node.dead_out_inds.add(0)
    for jrd__hta in range(1, len(agg_node.out_vars)):
        kybzi__sgmtc = agg_node.out_vars[jrd__hta]
        if kybzi__sgmtc is not None and kybzi__sgmtc.name not in lives:
            agg_node.out_vars[jrd__hta] = None
            tkzqc__kut = agg_node.n_out_table_arrays + jrd__hta - 1
            agg_node.dead_out_inds.add(tkzqc__kut)
    if all(kybzi__sgmtc is None for kybzi__sgmtc in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    mpn__twn = {kybzi__sgmtc.name for kybzi__sgmtc in aggregate_node.
        get_live_out_vars()}
    return set(), mpn__twn


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for jrd__hta in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[jrd__hta] is not None:
            aggregate_node.in_vars[jrd__hta] = replace_vars_inner(
                aggregate_node.in_vars[jrd__hta], var_dict)
    for jrd__hta in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[jrd__hta] is not None:
            aggregate_node.out_vars[jrd__hta] = replace_vars_inner(
                aggregate_node.out_vars[jrd__hta], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for jrd__hta in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[jrd__hta] is not None:
            aggregate_node.in_vars[jrd__hta] = visit_vars_inner(aggregate_node
                .in_vars[jrd__hta], callback, cbdata)
    for jrd__hta in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[jrd__hta] is not None:
            aggregate_node.out_vars[jrd__hta] = visit_vars_inner(aggregate_node
                .out_vars[jrd__hta], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    lmwdw__ntv = []
    for xogze__mlbki in aggregate_node.get_live_in_vars():
        xal__cag = equiv_set.get_shape(xogze__mlbki)
        if xal__cag is not None:
            lmwdw__ntv.append(xal__cag[0])
    if len(lmwdw__ntv) > 1:
        equiv_set.insert_equiv(*lmwdw__ntv)
    nbel__vddk = []
    lmwdw__ntv = []
    for xogze__mlbki in aggregate_node.get_live_out_vars():
        eceuc__wdfn = typemap[xogze__mlbki.name]
        czhvb__ops = array_analysis._gen_shape_call(equiv_set, xogze__mlbki,
            eceuc__wdfn.ndim, None, nbel__vddk)
        equiv_set.insert_equiv(xogze__mlbki, czhvb__ops)
        lmwdw__ntv.append(czhvb__ops[0])
        equiv_set.define(xogze__mlbki, set())
    if len(lmwdw__ntv) > 1:
        equiv_set.insert_equiv(*lmwdw__ntv)
    return [], nbel__vddk


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    enokv__meim = aggregate_node.get_live_in_vars()
    llnl__npxmb = aggregate_node.get_live_out_vars()
    zqb__aujth = Distribution.OneD
    for xogze__mlbki in enokv__meim:
        zqb__aujth = Distribution(min(zqb__aujth.value, array_dists[
            xogze__mlbki.name].value))
    bejzx__rot = Distribution(min(zqb__aujth.value, Distribution.OneD_Var.
        value))
    for xogze__mlbki in llnl__npxmb:
        if xogze__mlbki.name in array_dists:
            bejzx__rot = Distribution(min(bejzx__rot.value, array_dists[
                xogze__mlbki.name].value))
    if bejzx__rot != Distribution.OneD_Var:
        zqb__aujth = bejzx__rot
    for xogze__mlbki in enokv__meim:
        array_dists[xogze__mlbki.name] = zqb__aujth
    for xogze__mlbki in llnl__npxmb:
        array_dists[xogze__mlbki.name] = bejzx__rot


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for xogze__mlbki in agg_node.get_live_out_vars():
        definitions[xogze__mlbki.name].append(agg_node)
    return definitions


ir_utils.build_defs_extensions[Aggregate] = build_agg_definitions


def __update_redvars():
    pass


@infer_global(__update_redvars)
class UpdateDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __combine_redvars():
    pass


@infer_global(__combine_redvars)
class CombineDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __eval_res():
    pass


@infer_global(__eval_res)
class EvalDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(args[0].dtype, *args)


def agg_distributed_run(agg_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    dnmv__dewsd = agg_node.get_live_in_vars()
    ckzkr__yggpm = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for kybzi__sgmtc in (dnmv__dewsd + ckzkr__yggpm):
            if array_dists[kybzi__sgmtc.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                kybzi__sgmtc.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    gspr__sjsc = []
    func_out_types = []
    for ejo__gtoz, (udwi__zkiwq, func) in agg_node.gb_info_out.items():
        if udwi__zkiwq is not None:
            t = agg_node.in_col_types[udwi__zkiwq]
            in_col_typs.append(t)
        gspr__sjsc.append(func)
        func_out_types.append(out_col_typs[ejo__gtoz])
    jgmo__nch = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for jrd__hta, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            jgmo__nch.update({f'in_cat_dtype_{jrd__hta}': in_col_typ})
    for jrd__hta, tufuz__wzv in enumerate(out_col_typs):
        if isinstance(tufuz__wzv, bodo.CategoricalArrayType):
            jgmo__nch.update({f'out_cat_dtype_{jrd__hta}': tufuz__wzv})
    udf_func_struct = get_udf_func_struct(gspr__sjsc, in_col_typs,
        typingctx, targetctx)
    out_var_types = [(typemap[kybzi__sgmtc.name] if kybzi__sgmtc is not
        None else types.none) for kybzi__sgmtc in agg_node.out_vars]
    uyjvw__asgk, utzl__mzz = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    jgmo__nch.update(utzl__mzz)
    jgmo__nch.update({'pd': pd, 'pre_alloc_string_array':
        pre_alloc_string_array, 'pre_alloc_binary_array':
        pre_alloc_binary_array, 'pre_alloc_array_item_array':
        pre_alloc_array_item_array, 'string_array_type': string_array_type,
        'alloc_decimal_array': alloc_decimal_array, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'coerce_to_array': bodo.utils.conversion.coerce_to_array,
        'groupby_and_aggregate': groupby_and_aggregate, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array,
        'delete_info_decref_array': delete_info_decref_array,
        'delete_table': delete_table, 'add_agg_cfunc_sym':
        add_agg_cfunc_sym, 'get_agg_udf_addr': get_agg_udf_addr,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'decref_table_array': decref_table_array, 'decode_if_dict_array':
        decode_if_dict_array, 'set_table_data': bodo.hiframes.table.
        set_table_data, 'get_table_data': bodo.hiframes.table.
        get_table_data, 'out_typs': out_col_typs})
    if udf_func_struct is not None:
        if udf_func_struct.regular_udfs:
            jgmo__nch.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            jgmo__nch.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    jnvb__etfq = {}
    exec(uyjvw__asgk, {}, jnvb__etfq)
    uhlii__fbevu = jnvb__etfq['agg_top']
    mvoi__ppt = compile_to_numba_ir(uhlii__fbevu, jgmo__nch, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[kybzi__sgmtc
        .name] for kybzi__sgmtc in dnmv__dewsd), typemap=typemap, calltypes
        =calltypes).blocks.popitem()[1]
    replace_arg_nodes(mvoi__ppt, dnmv__dewsd)
    tpk__hbc = mvoi__ppt.body[-2].value.value
    wyj__dyn = mvoi__ppt.body[:-2]
    for jrd__hta, kybzi__sgmtc in enumerate(ckzkr__yggpm):
        gen_getitem(kybzi__sgmtc, tpk__hbc, jrd__hta, calltypes, wyj__dyn)
    return wyj__dyn


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        awvip__pza = IntDtype(t.dtype).name
        assert awvip__pza.endswith('Dtype()')
        awvip__pza = awvip__pza[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{awvip__pza}'))"
            )
    elif isinstance(t, BooleanArrayType):
        return (
            'bodo.libs.bool_arr_ext.init_bool_array(np.empty(0, np.bool_), np.empty(0, np.uint8))'
            )
    elif isinstance(t, StringArrayType):
        return 'pre_alloc_string_array(1, 1)'
    elif t == bodo.dict_str_arr_type:
        return (
            'bodo.libs.dict_arr_ext.init_dict_arr(pre_alloc_string_array(1, 1), bodo.libs.int_arr_ext.alloc_int_array(1, np.int32), False)'
            )
    elif isinstance(t, BinaryArrayType):
        return 'pre_alloc_binary_array(1, 1)'
    elif t == ArrayItemArrayType(string_array_type):
        return 'pre_alloc_array_item_array(1, (1, 1), string_array_type)'
    elif isinstance(t, DecimalArrayType):
        return 'alloc_decimal_array(1, {}, {})'.format(t.precision, t.scale)
    elif isinstance(t, DatetimeDateArrayType):
        return (
            'bodo.hiframes.datetime_date_ext.init_datetime_date_array(np.empty(1, np.int64), np.empty(1, np.uint8))'
            )
    elif isinstance(t, bodo.CategoricalArrayType):
        if t.dtype.categories is None:
            raise BodoError(
                'Groupby agg operations on Categorical types require constant categories'
                )
        rydt__nmey = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {rydt__nmey}_cat_dtype_{colnum})')
    else:
        return 'np.empty(1, {})'.format(_get_np_dtype(t.dtype))


def _get_np_dtype(t):
    if t == types.bool_:
        return 'np.bool_'
    if t == types.NPDatetime('ns'):
        return 'dt64_dtype'
    if t == types.NPTimedelta('ns'):
        return 'td64_dtype'
    return 'np.{}'.format(t)


def gen_update_cb(udf_func_struct, allfuncs, n_keys, data_in_typs_,
    do_combine, func_idx_to_in_col, label_suffix):
    vwmdj__bah = udf_func_struct.var_typs
    agajn__tnpx = len(vwmdj__bah)
    uyjvw__asgk = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    uyjvw__asgk += '    if is_null_pointer(in_table):\n'
    uyjvw__asgk += '        return\n'
    uyjvw__asgk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in vwmdj__bah]), 
        ',' if len(vwmdj__bah) == 1 else '')
    ygo__yqwc = n_keys
    mbc__euj = []
    redvar_offsets = []
    ryvc__dtox = []
    if do_combine:
        for jrd__hta, ngi__guv in enumerate(allfuncs):
            if ngi__guv.ftype != 'udf':
                ygo__yqwc += ngi__guv.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(ygo__yqwc, ygo__yqwc +
                    ngi__guv.n_redvars))
                ygo__yqwc += ngi__guv.n_redvars
                ryvc__dtox.append(data_in_typs_[func_idx_to_in_col[jrd__hta]])
                mbc__euj.append(func_idx_to_in_col[jrd__hta] + n_keys)
    else:
        for jrd__hta, ngi__guv in enumerate(allfuncs):
            if ngi__guv.ftype != 'udf':
                ygo__yqwc += ngi__guv.ncols_post_shuffle
            else:
                redvar_offsets += list(range(ygo__yqwc + 1, ygo__yqwc + 1 +
                    ngi__guv.n_redvars))
                ygo__yqwc += ngi__guv.n_redvars + 1
                ryvc__dtox.append(data_in_typs_[func_idx_to_in_col[jrd__hta]])
                mbc__euj.append(func_idx_to_in_col[jrd__hta] + n_keys)
    assert len(redvar_offsets) == agajn__tnpx
    ndx__umrs = len(ryvc__dtox)
    pzwz__qbula = []
    for jrd__hta, t in enumerate(ryvc__dtox):
        pzwz__qbula.append(_gen_dummy_alloc(t, jrd__hta, True))
    uyjvw__asgk += '    data_in_dummy = ({}{})\n'.format(','.join(
        pzwz__qbula), ',' if len(ryvc__dtox) == 1 else '')
    uyjvw__asgk += """
    # initialize redvar cols
"""
    uyjvw__asgk += '    init_vals = __init_func()\n'
    for jrd__hta in range(agajn__tnpx):
        uyjvw__asgk += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(jrd__hta, redvar_offsets[jrd__hta], jrd__hta))
        uyjvw__asgk += '    incref(redvar_arr_{})\n'.format(jrd__hta)
        uyjvw__asgk += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            jrd__hta, jrd__hta)
    uyjvw__asgk += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(jrd__hta) for jrd__hta in range(agajn__tnpx)
        ]), ',' if agajn__tnpx == 1 else '')
    uyjvw__asgk += '\n'
    for jrd__hta in range(ndx__umrs):
        uyjvw__asgk += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(jrd__hta, mbc__euj[jrd__hta], jrd__hta))
        uyjvw__asgk += '    incref(data_in_{})\n'.format(jrd__hta)
    uyjvw__asgk += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(jrd__hta) for jrd__hta in range(ndx__umrs)]), ',' if 
        ndx__umrs == 1 else '')
    uyjvw__asgk += '\n'
    uyjvw__asgk += '    for i in range(len(data_in_0)):\n'
    uyjvw__asgk += '        w_ind = row_to_group[i]\n'
    uyjvw__asgk += '        if w_ind != -1:\n'
    uyjvw__asgk += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    jnvb__etfq = {}
    exec(uyjvw__asgk, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, jnvb__etfq)
    return jnvb__etfq['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    vwmdj__bah = udf_func_struct.var_typs
    agajn__tnpx = len(vwmdj__bah)
    uyjvw__asgk = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    uyjvw__asgk += '    if is_null_pointer(in_table):\n'
    uyjvw__asgk += '        return\n'
    uyjvw__asgk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in vwmdj__bah]), 
        ',' if len(vwmdj__bah) == 1 else '')
    munls__nskmn = n_keys
    fkklx__yrnd = n_keys
    dwx__uhlc = []
    utdj__rmn = []
    for ngi__guv in allfuncs:
        if ngi__guv.ftype != 'udf':
            munls__nskmn += ngi__guv.ncols_pre_shuffle
            fkklx__yrnd += ngi__guv.ncols_post_shuffle
        else:
            dwx__uhlc += list(range(munls__nskmn, munls__nskmn + ngi__guv.
                n_redvars))
            utdj__rmn += list(range(fkklx__yrnd + 1, fkklx__yrnd + 1 +
                ngi__guv.n_redvars))
            munls__nskmn += ngi__guv.n_redvars
            fkklx__yrnd += 1 + ngi__guv.n_redvars
    assert len(dwx__uhlc) == agajn__tnpx
    uyjvw__asgk += """
    # initialize redvar cols
"""
    uyjvw__asgk += '    init_vals = __init_func()\n'
    for jrd__hta in range(agajn__tnpx):
        uyjvw__asgk += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(jrd__hta, utdj__rmn[jrd__hta], jrd__hta))
        uyjvw__asgk += '    incref(redvar_arr_{})\n'.format(jrd__hta)
        uyjvw__asgk += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            jrd__hta, jrd__hta)
    uyjvw__asgk += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(jrd__hta) for jrd__hta in range(agajn__tnpx)
        ]), ',' if agajn__tnpx == 1 else '')
    uyjvw__asgk += '\n'
    for jrd__hta in range(agajn__tnpx):
        uyjvw__asgk += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(jrd__hta, dwx__uhlc[jrd__hta], jrd__hta))
        uyjvw__asgk += '    incref(recv_redvar_arr_{})\n'.format(jrd__hta)
    uyjvw__asgk += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(jrd__hta) for jrd__hta in range(
        agajn__tnpx)]), ',' if agajn__tnpx == 1 else '')
    uyjvw__asgk += '\n'
    if agajn__tnpx:
        uyjvw__asgk += '    for i in range(len(recv_redvar_arr_0)):\n'
        uyjvw__asgk += '        w_ind = row_to_group[i]\n'
        uyjvw__asgk += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    jnvb__etfq = {}
    exec(uyjvw__asgk, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, jnvb__etfq)
    return jnvb__etfq['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    vwmdj__bah = udf_func_struct.var_typs
    agajn__tnpx = len(vwmdj__bah)
    ygo__yqwc = n_keys
    redvar_offsets = []
    xhopp__dmzgp = []
    pnc__lwl = []
    for jrd__hta, ngi__guv in enumerate(allfuncs):
        if ngi__guv.ftype != 'udf':
            ygo__yqwc += ngi__guv.ncols_post_shuffle
        else:
            xhopp__dmzgp.append(ygo__yqwc)
            redvar_offsets += list(range(ygo__yqwc + 1, ygo__yqwc + 1 +
                ngi__guv.n_redvars))
            ygo__yqwc += 1 + ngi__guv.n_redvars
            pnc__lwl.append(out_data_typs_[jrd__hta])
    assert len(redvar_offsets) == agajn__tnpx
    ndx__umrs = len(pnc__lwl)
    uyjvw__asgk = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    uyjvw__asgk += '    if is_null_pointer(table):\n'
    uyjvw__asgk += '        return\n'
    uyjvw__asgk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in vwmdj__bah]), 
        ',' if len(vwmdj__bah) == 1 else '')
    uyjvw__asgk += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in pnc__lwl]
        ), ',' if len(pnc__lwl) == 1 else '')
    for jrd__hta in range(agajn__tnpx):
        uyjvw__asgk += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(jrd__hta, redvar_offsets[jrd__hta], jrd__hta))
        uyjvw__asgk += '    incref(redvar_arr_{})\n'.format(jrd__hta)
    uyjvw__asgk += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(jrd__hta) for jrd__hta in range(agajn__tnpx)
        ]), ',' if agajn__tnpx == 1 else '')
    uyjvw__asgk += '\n'
    for jrd__hta in range(ndx__umrs):
        uyjvw__asgk += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(jrd__hta, xhopp__dmzgp[jrd__hta], jrd__hta))
        uyjvw__asgk += '    incref(data_out_{})\n'.format(jrd__hta)
    uyjvw__asgk += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'
        .format(jrd__hta) for jrd__hta in range(ndx__umrs)]), ',' if 
        ndx__umrs == 1 else '')
    uyjvw__asgk += '\n'
    uyjvw__asgk += '    for i in range(len(data_out_0)):\n'
    uyjvw__asgk += '        __eval_res(redvars, data_out, i)\n'
    jnvb__etfq = {}
    exec(uyjvw__asgk, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, jnvb__etfq)
    return jnvb__etfq['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    ygo__yqwc = n_keys
    utkh__pgts = []
    for jrd__hta, ngi__guv in enumerate(allfuncs):
        if ngi__guv.ftype == 'gen_udf':
            utkh__pgts.append(ygo__yqwc)
            ygo__yqwc += 1
        elif ngi__guv.ftype != 'udf':
            ygo__yqwc += ngi__guv.ncols_post_shuffle
        else:
            ygo__yqwc += ngi__guv.n_redvars + 1
    uyjvw__asgk = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    uyjvw__asgk += '    if num_groups == 0:\n'
    uyjvw__asgk += '        return\n'
    for jrd__hta, func in enumerate(udf_func_struct.general_udf_funcs):
        uyjvw__asgk += '    # col {}\n'.format(jrd__hta)
        uyjvw__asgk += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(utkh__pgts[jrd__hta], jrd__hta))
        uyjvw__asgk += '    incref(out_col)\n'
        uyjvw__asgk += '    for j in range(num_groups):\n'
        uyjvw__asgk += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(jrd__hta, jrd__hta))
        uyjvw__asgk += '        incref(in_col)\n'
        uyjvw__asgk += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(jrd__hta))
    jgmo__nch = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    jyv__zqln = 0
    for jrd__hta, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[jyv__zqln]
        jgmo__nch['func_{}'.format(jyv__zqln)] = func
        jgmo__nch['in_col_{}_typ'.format(jyv__zqln)] = in_col_typs[
            func_idx_to_in_col[jrd__hta]]
        jgmo__nch['out_col_{}_typ'.format(jyv__zqln)] = out_col_typs[jrd__hta]
        jyv__zqln += 1
    jnvb__etfq = {}
    exec(uyjvw__asgk, jgmo__nch, jnvb__etfq)
    ngi__guv = jnvb__etfq['bodo_gb_apply_general_udfs{}'.format(label_suffix)]
    iaxln__hfqdo = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(iaxln__hfqdo, nopython=True)(ngi__guv)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    xusz__xvvo = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        gns__lknoy = []
        if agg_node.in_vars[0] is not None:
            gns__lknoy.append('arg0')
        for jrd__hta in range(agg_node.n_in_table_arrays, agg_node.n_in_cols):
            if jrd__hta not in agg_node.dead_in_inds:
                gns__lknoy.append(f'arg{jrd__hta}')
    else:
        gns__lknoy = [f'arg{jrd__hta}' for jrd__hta, kybzi__sgmtc in
            enumerate(agg_node.in_vars) if kybzi__sgmtc is not None]
    uyjvw__asgk = f"def agg_top({', '.join(gns__lknoy)}):\n"
    lrmjp__ssw = []
    if agg_node.is_in_table_format:
        lrmjp__ssw = agg_node.in_key_inds + [udwi__zkiwq for udwi__zkiwq,
            ocuac__keryc in agg_node.gb_info_out.values() if udwi__zkiwq is not
            None]
        if agg_node.input_has_index:
            lrmjp__ssw.append(agg_node.n_in_cols - 1)
        tey__sng = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        vrwyv__uvta = []
        for jrd__hta in range(agg_node.n_in_table_arrays, agg_node.n_in_cols):
            if jrd__hta in agg_node.dead_in_inds:
                vrwyv__uvta.append('None')
            else:
                vrwyv__uvta.append(f'arg{jrd__hta}')
        sils__ycy = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        uyjvw__asgk += f"""    table = py_data_to_cpp_table({sils__ycy}, ({', '.join(vrwyv__uvta)}{tey__sng}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        raci__sfodt = [f'arg{jrd__hta}' for jrd__hta in agg_node.in_key_inds]
        kuk__rhloq = [f'arg{udwi__zkiwq}' for udwi__zkiwq, ocuac__keryc in
            agg_node.gb_info_out.values() if udwi__zkiwq is not None]
        zvacq__gah = raci__sfodt + kuk__rhloq
        if agg_node.input_has_index:
            zvacq__gah.append(f'arg{len(agg_node.in_vars) - 1}')
        uyjvw__asgk += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({nwlb__aqedh})' for nwlb__aqedh in zvacq__gah))
        uyjvw__asgk += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    oojg__uzh = []
    func_idx_to_in_col = []
    bjn__xgzqx = []
    bagwn__qir = False
    oqae__yrcmz = 1
    hkt__xif = -1
    kne__ohq = 0
    jwm__mda = 0
    gspr__sjsc = [func for ocuac__keryc, func in agg_node.gb_info_out.values()]
    for uiu__ggtg, func in enumerate(gspr__sjsc):
        oojg__uzh.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            kne__ohq += 1
        if hasattr(func, 'skipdropna'):
            bagwn__qir = func.skipdropna
        if func.ftype == 'shift':
            oqae__yrcmz = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            jwm__mda = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            hkt__xif = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(uiu__ggtg)
        if func.ftype == 'udf':
            bjn__xgzqx.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            bjn__xgzqx.append(0)
            do_combine = False
    oojg__uzh.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if kne__ohq > 0:
        if kne__ohq != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    eyi__iqf = []
    if udf_func_struct is not None:
        ihvdg__fkf = next_label()
        if udf_func_struct.regular_udfs:
            iaxln__hfqdo = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            dfnc__ankj = numba.cfunc(iaxln__hfqdo, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, ihvdg__fkf))
            rouk__tnb = numba.cfunc(iaxln__hfqdo, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, ihvdg__fkf))
            gsipa__gtzsz = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys,
                func_out_types, ihvdg__fkf))
            udf_func_struct.set_regular_cfuncs(dfnc__ankj, rouk__tnb,
                gsipa__gtzsz)
            for hbv__qjzwd in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[hbv__qjzwd.native_name] = hbv__qjzwd
                gb_agg_cfunc_addr[hbv__qjzwd.native_name] = hbv__qjzwd.address
        if udf_func_struct.general_udfs:
            vyg__fycr = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, func_out_types, func_idx_to_in_col,
                ihvdg__fkf)
            udf_func_struct.set_general_cfunc(vyg__fycr)
        vwmdj__bah = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        sin__gzzk = 0
        jrd__hta = 0
        for jzvs__fzwsc, ngi__guv in zip(agg_node.gb_info_out.keys(), allfuncs
            ):
            if ngi__guv.ftype in ('udf', 'gen_udf'):
                eyi__iqf.append(out_col_typs[jzvs__fzwsc])
                for gpd__uov in range(sin__gzzk, sin__gzzk + bjn__xgzqx[
                    jrd__hta]):
                    eyi__iqf.append(dtype_to_array_type(vwmdj__bah[gpd__uov]))
                sin__gzzk += bjn__xgzqx[jrd__hta]
                jrd__hta += 1
        uyjvw__asgk += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{jrd__hta}' for jrd__hta in range(len(eyi__iqf)))}{',' if len(eyi__iqf) == 1 else ''}))
"""
        uyjvw__asgk += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(eyi__iqf)})
"""
        if udf_func_struct.regular_udfs:
            uyjvw__asgk += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{dfnc__ankj.native_name}')\n"
                )
            uyjvw__asgk += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{rouk__tnb.native_name}')\n"
                )
            uyjvw__asgk += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{gsipa__gtzsz.native_name}')\n"
                )
            uyjvw__asgk += f"""    cpp_cb_update_addr = get_agg_udf_addr('{dfnc__ankj.native_name}')
"""
            uyjvw__asgk += f"""    cpp_cb_combine_addr = get_agg_udf_addr('{rouk__tnb.native_name}')
"""
            uyjvw__asgk += f"""    cpp_cb_eval_addr = get_agg_udf_addr('{gsipa__gtzsz.native_name}')
"""
        else:
            uyjvw__asgk += '    cpp_cb_update_addr = 0\n'
            uyjvw__asgk += '    cpp_cb_combine_addr = 0\n'
            uyjvw__asgk += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            hbv__qjzwd = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[hbv__qjzwd.native_name] = hbv__qjzwd
            gb_agg_cfunc_addr[hbv__qjzwd.native_name] = hbv__qjzwd.address
            uyjvw__asgk += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{hbv__qjzwd.native_name}')\n"
                )
            uyjvw__asgk += f"""    cpp_cb_general_addr = get_agg_udf_addr('{hbv__qjzwd.native_name}')
"""
        else:
            uyjvw__asgk += '    cpp_cb_general_addr = 0\n'
    else:
        uyjvw__asgk += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        uyjvw__asgk += '    cpp_cb_update_addr = 0\n'
        uyjvw__asgk += '    cpp_cb_combine_addr = 0\n'
        uyjvw__asgk += '    cpp_cb_eval_addr = 0\n'
        uyjvw__asgk += '    cpp_cb_general_addr = 0\n'
    uyjvw__asgk += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(ngi__guv.ftype)) for
        ngi__guv in allfuncs] + ['0']))
    uyjvw__asgk += (
        f'    func_offsets = np.array({str(oojg__uzh)}, dtype=np.int32)\n')
    if len(bjn__xgzqx) > 0:
        uyjvw__asgk += (
            f'    udf_ncols = np.array({str(bjn__xgzqx)}, dtype=np.int32)\n')
    else:
        uyjvw__asgk += '    udf_ncols = np.array([0], np.int32)\n'
    uyjvw__asgk += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    eqv__amc = (agg_node._num_shuffle_keys if agg_node._num_shuffle_keys !=
        -1 else n_keys)
    uyjvw__asgk += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {bagwn__qir}, {oqae__yrcmz}, {jwm__mda}, {hkt__xif}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes, {eqv__amc})
"""
    uhs__uxjq = []
    rxz__nqncf = 0
    if agg_node.return_key:
        vcicl__iif = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for jrd__hta in range(n_keys):
            tkzqc__kut = vcicl__iif + jrd__hta
            uhs__uxjq.append(tkzqc__kut if tkzqc__kut not in agg_node.
                dead_out_inds else -1)
            rxz__nqncf += 1
    for jzvs__fzwsc in agg_node.gb_info_out.keys():
        uhs__uxjq.append(jzvs__fzwsc)
        rxz__nqncf += 1
    umg__eglo = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            uhs__uxjq.append(agg_node.n_out_cols - 1)
        else:
            umg__eglo = True
    tey__sng = ',' if xusz__xvvo == 1 else ''
    llph__brb = (
        f"({', '.join(f'out_type{jrd__hta}' for jrd__hta in range(xusz__xvvo))}{tey__sng})"
        )
    iywws__otf = []
    tio__bivxk = []
    for jrd__hta, t in enumerate(out_col_typs):
        if jrd__hta not in agg_node.dead_out_inds and type_has_unknown_cats(t):
            if jrd__hta in agg_node.gb_info_out:
                udwi__zkiwq = agg_node.gb_info_out[jrd__hta][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                lgalm__wmmuk = jrd__hta - vcicl__iif
                udwi__zkiwq = agg_node.in_key_inds[lgalm__wmmuk]
            tio__bivxk.append(jrd__hta)
            if (agg_node.is_in_table_format and udwi__zkiwq < agg_node.
                n_in_table_arrays):
                iywws__otf.append(f'get_table_data(arg0, {udwi__zkiwq})')
            else:
                iywws__otf.append(f'arg{udwi__zkiwq}')
    tey__sng = ',' if len(iywws__otf) == 1 else ''
    uyjvw__asgk += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {llph__brb}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(iywws__otf)}{tey__sng}), unknown_cat_out_inds)
"""
    uyjvw__asgk += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    uyjvw__asgk += '    delete_table_decref_arrays(table)\n'
    uyjvw__asgk += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for jrd__hta in range(n_keys):
            if uhs__uxjq[jrd__hta] == -1:
                uyjvw__asgk += (
                    f'    decref_table_array(out_table, {jrd__hta})\n')
    if umg__eglo:
        ngy__pht = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        uyjvw__asgk += f'    decref_table_array(out_table, {ngy__pht})\n'
    uyjvw__asgk += '    delete_table(out_table)\n'
    uyjvw__asgk += '    ev_clean.finalize()\n'
    uyjvw__asgk += '    return out_data\n'
    lpzp__zqe = {f'out_type{jrd__hta}': out_var_types[jrd__hta] for
        jrd__hta in range(xusz__xvvo)}
    lpzp__zqe['out_col_inds'] = MetaType(tuple(uhs__uxjq))
    lpzp__zqe['in_col_inds'] = MetaType(tuple(lrmjp__ssw))
    lpzp__zqe['cpp_table_to_py_data'] = cpp_table_to_py_data
    lpzp__zqe['py_data_to_cpp_table'] = py_data_to_cpp_table
    lpzp__zqe.update({f'udf_type{jrd__hta}': t for jrd__hta, t in enumerate
        (eyi__iqf)})
    lpzp__zqe['udf_dummy_col_inds'] = MetaType(tuple(range(len(eyi__iqf))))
    lpzp__zqe['create_dummy_table'] = create_dummy_table
    lpzp__zqe['unknown_cat_out_inds'] = MetaType(tuple(tio__bivxk))
    lpzp__zqe['get_table_data'] = bodo.hiframes.table.get_table_data
    return uyjvw__asgk, lpzp__zqe


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    nxq__pjie = tuple(unwrap_typeref(data_types.types[jrd__hta]) for
        jrd__hta in range(len(data_types.types)))
    bzj__xffyw = bodo.TableType(nxq__pjie)
    lpzp__zqe = {'table_type': bzj__xffyw}
    uyjvw__asgk = 'def impl(data_types):\n'
    uyjvw__asgk += '  py_table = init_table(table_type, False)\n'
    uyjvw__asgk += '  py_table = set_table_len(py_table, 1)\n'
    for eceuc__wdfn, dbtzt__cfd in bzj__xffyw.type_to_blk.items():
        lpzp__zqe[f'typ_list_{dbtzt__cfd}'] = types.List(eceuc__wdfn)
        lpzp__zqe[f'typ_{dbtzt__cfd}'] = eceuc__wdfn
        wxw__bqq = len(bzj__xffyw.block_to_arr_ind[dbtzt__cfd])
        uyjvw__asgk += f"""  arr_list_{dbtzt__cfd} = alloc_list_like(typ_list_{dbtzt__cfd}, {wxw__bqq}, False)
"""
        uyjvw__asgk += f'  for i in range(len(arr_list_{dbtzt__cfd})):\n'
        uyjvw__asgk += (
            f'    arr_list_{dbtzt__cfd}[i] = alloc_type(1, typ_{dbtzt__cfd}, (-1,))\n'
            )
        uyjvw__asgk += f"""  py_table = set_table_block(py_table, arr_list_{dbtzt__cfd}, {dbtzt__cfd})
"""
    uyjvw__asgk += '  return py_table\n'
    lpzp__zqe.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    jnvb__etfq = {}
    exec(uyjvw__asgk, lpzp__zqe, jnvb__etfq)
    return jnvb__etfq['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    lgnr__jhwi = agg_node.in_vars[0].name
    eev__vmi, kllb__iypqi, kqu__ywl = block_use_map[lgnr__jhwi]
    if kllb__iypqi or kqu__ywl:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        ifzdv__pdih, dbbr__gwqzl, wqt__uopx = _compute_table_column_uses(
            agg_node.out_vars[0].name, table_col_use_map, equiv_vars)
        if dbbr__gwqzl or wqt__uopx:
            ifzdv__pdih = set(range(agg_node.n_out_table_arrays))
    else:
        ifzdv__pdih = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            ifzdv__pdih = {0}
    bbe__aftic = set(jrd__hta for jrd__hta in agg_node.in_key_inds if 
        jrd__hta < agg_node.n_in_table_arrays)
    zdmz__weuat = set(agg_node.gb_info_out[jrd__hta][0] for jrd__hta in
        ifzdv__pdih if jrd__hta in agg_node.gb_info_out and agg_node.
        gb_info_out[jrd__hta][0] is not None)
    zdmz__weuat |= bbe__aftic | eev__vmi
    ifen__wxxt = len(set(range(agg_node.n_in_table_arrays)) - zdmz__weuat) == 0
    block_use_map[lgnr__jhwi] = zdmz__weuat, ifen__wxxt, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    etnvr__nowfi = agg_node.n_out_table_arrays
    qdr__zpfz = agg_node.out_vars[0].name
    cgpv__kksg = _find_used_columns(qdr__zpfz, etnvr__nowfi,
        column_live_map, equiv_vars)
    if cgpv__kksg is None:
        return False
    fiwfe__mfxl = set(range(etnvr__nowfi)) - cgpv__kksg
    oxsl__jxn = len(fiwfe__mfxl - agg_node.dead_out_inds) != 0
    if oxsl__jxn:
        agg_node.dead_out_inds.update(fiwfe__mfxl)
        agg_node.update_dead_col_info()
    return oxsl__jxn


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for iwdlr__pofub in block.body:
            if is_call_assign(iwdlr__pofub) and find_callname(f_ir,
                iwdlr__pofub.value) == ('len', 'builtins'
                ) and iwdlr__pofub.value.args[0].name == f_ir.arg_names[0]:
                hbt__xpxd = get_definition(f_ir, iwdlr__pofub.value.func)
                hbt__xpxd.name = 'dummy_agg_count'
                hbt__xpxd.value = dummy_agg_count
    njhno__hru = get_name_var_table(f_ir.blocks)
    nly__wok = {}
    for name, ocuac__keryc in njhno__hru.items():
        nly__wok[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, nly__wok)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    ignym__bmob = numba.core.compiler.Flags()
    ignym__bmob.nrt = True
    ult__gjp = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, ignym__bmob)
    ult__gjp.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, elzhw__epv, calltypes, ocuac__keryc = (numba.core.typed_passes
        .type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    yhlr__lvabr = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    fcz__fqqc = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    xel__wnhn = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    kru__nie = xel__wnhn(typemap, calltypes)
    pm = fcz__fqqc(typingctx, targetctx, None, f_ir, typemap, elzhw__epv,
        calltypes, kru__nie, {}, ignym__bmob, None)
    mtgf__ejun = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = fcz__fqqc(typingctx, targetctx, None, f_ir, typemap, elzhw__epv,
        calltypes, kru__nie, {}, ignym__bmob, mtgf__ejun)
    kheak__aeat = numba.core.typed_passes.InlineOverloads()
    kheak__aeat.run_pass(pm)
    rjdmq__nkt = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    rjdmq__nkt.run()
    for block in f_ir.blocks.values():
        for iwdlr__pofub in block.body:
            if is_assign(iwdlr__pofub) and isinstance(iwdlr__pofub.value, (
                ir.Arg, ir.Var)) and isinstance(typemap[iwdlr__pofub.target
                .name], SeriesType):
                eceuc__wdfn = typemap.pop(iwdlr__pofub.target.name)
                typemap[iwdlr__pofub.target.name] = eceuc__wdfn.data
            if is_call_assign(iwdlr__pofub) and find_callname(f_ir,
                iwdlr__pofub.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[iwdlr__pofub.target.name].remove(iwdlr__pofub
                    .value)
                iwdlr__pofub.value = iwdlr__pofub.value.args[0]
                f_ir._definitions[iwdlr__pofub.target.name].append(iwdlr__pofub
                    .value)
            if is_call_assign(iwdlr__pofub) and find_callname(f_ir,
                iwdlr__pofub.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[iwdlr__pofub.target.name].remove(iwdlr__pofub
                    .value)
                iwdlr__pofub.value = ir.Const(False, iwdlr__pofub.loc)
                f_ir._definitions[iwdlr__pofub.target.name].append(iwdlr__pofub
                    .value)
            if is_call_assign(iwdlr__pofub) and find_callname(f_ir,
                iwdlr__pofub.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[iwdlr__pofub.target.name].remove(iwdlr__pofub
                    .value)
                iwdlr__pofub.value = ir.Const(False, iwdlr__pofub.loc)
                f_ir._definitions[iwdlr__pofub.target.name].append(iwdlr__pofub
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    ibmdo__yuhxt = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, yhlr__lvabr)
    ibmdo__yuhxt.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    xeof__yqn = numba.core.compiler.StateDict()
    xeof__yqn.func_ir = f_ir
    xeof__yqn.typemap = typemap
    xeof__yqn.calltypes = calltypes
    xeof__yqn.typingctx = typingctx
    xeof__yqn.targetctx = targetctx
    xeof__yqn.return_type = elzhw__epv
    numba.core.rewrites.rewrite_registry.apply('after-inference', xeof__yqn)
    jzmdv__aug = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        elzhw__epv, typingctx, targetctx, yhlr__lvabr, ignym__bmob, {})
    jzmdv__aug.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            vlmfy__khl = ctypes.pythonapi.PyCell_Get
            vlmfy__khl.restype = ctypes.py_object
            vlmfy__khl.argtypes = ctypes.py_object,
            etk__vur = tuple(vlmfy__khl(wxvib__eysz) for wxvib__eysz in closure
                )
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            etk__vur = closure.items
        assert len(code.co_freevars) == len(etk__vur)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, etk__vur)


class RegularUDFGenerator:

    def __init__(self, in_col_types, typingctx, targetctx):
        self.in_col_types = in_col_types
        self.typingctx = typingctx
        self.targetctx = targetctx
        self.all_reduce_vars = []
        self.all_vartypes = []
        self.all_init_nodes = []
        self.all_eval_funcs = []
        self.all_update_funcs = []
        self.all_combine_funcs = []
        self.curr_offset = 0
        self.redvar_offsets = [0]

    def add_udf(self, in_col_typ, func):
        pxnpa__ggc = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array(
            in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (pxnpa__ggc,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        uvibq__btm, arr_var = _rm_arg_agg_block(block, pm.typemap)
        lxf__lenv = -1
        for jrd__hta, iwdlr__pofub in enumerate(uvibq__btm):
            if isinstance(iwdlr__pofub, numba.parfors.parfor.Parfor):
                assert lxf__lenv == -1, 'only one parfor for aggregation function'
                lxf__lenv = jrd__hta
        parfor = None
        if lxf__lenv != -1:
            parfor = uvibq__btm[lxf__lenv]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = uvibq__btm[:lxf__lenv] + parfor.init_block.body
        eval_nodes = uvibq__btm[lxf__lenv + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for iwdlr__pofub in init_nodes:
            if is_assign(iwdlr__pofub) and iwdlr__pofub.target.name in redvars:
                ind = redvars.index(iwdlr__pofub.target.name)
                reduce_vars[ind] = iwdlr__pofub.target
        var_types = [pm.typemap[kybzi__sgmtc] for kybzi__sgmtc in redvars]
        amys__wjev = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        fhtv__egmid = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        xlmzi__iwuj = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(xlmzi__iwuj)
        self.all_update_funcs.append(fhtv__egmid)
        self.all_combine_funcs.append(amys__wjev)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        qpath__wuwky = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        nkpwk__uiokg = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        ono__vcsi = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        dsz__etpv = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets)
        return (self.all_vartypes, qpath__wuwky, nkpwk__uiokg, ono__vcsi,
            dsz__etpv)


class GeneralUDFGenerator(object):

    def __init__(self):
        self.funcs = []

    def add_udf(self, func):
        self.funcs.append(bodo.jit(distributed=False)(func))
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        func.n_redvars = 0

    def gen_all_func(self):
        if len(self.funcs) > 0:
            return self.funcs
        else:
            return None


def get_udf_func_struct(agg_func, in_col_types, typingctx, targetctx):
    amf__fps = []
    for t, ngi__guv in zip(in_col_types, agg_func):
        amf__fps.append((t, ngi__guv))
    qhx__limi = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    pvfyz__aylj = GeneralUDFGenerator()
    for in_col_typ, func in amf__fps:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            qhx__limi.add_udf(in_col_typ, func)
        except:
            pvfyz__aylj.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = qhx__limi.gen_all_func()
    general_udf_funcs = pvfyz__aylj.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    soxd__bubyo = compute_use_defs(parfor.loop_body)
    vko__lab = set()
    for xttk__skr in soxd__bubyo.usemap.values():
        vko__lab |= xttk__skr
    qje__whw = set()
    for xttk__skr in soxd__bubyo.defmap.values():
        qje__whw |= xttk__skr
    hqmua__aow = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    hqmua__aow.body = eval_nodes
    fvk__jvjkf = compute_use_defs({(0): hqmua__aow})
    sik__dmrb = fvk__jvjkf.usemap[0]
    lxmci__gjkj = set()
    mny__vvbbx = []
    hkpbr__fqdu = []
    for iwdlr__pofub in reversed(init_nodes):
        oswcv__snulr = {kybzi__sgmtc.name for kybzi__sgmtc in iwdlr__pofub.
            list_vars()}
        if is_assign(iwdlr__pofub):
            kybzi__sgmtc = iwdlr__pofub.target.name
            oswcv__snulr.remove(kybzi__sgmtc)
            if (kybzi__sgmtc in vko__lab and kybzi__sgmtc not in
                lxmci__gjkj and kybzi__sgmtc not in sik__dmrb and 
                kybzi__sgmtc not in qje__whw):
                hkpbr__fqdu.append(iwdlr__pofub)
                vko__lab |= oswcv__snulr
                qje__whw.add(kybzi__sgmtc)
                continue
        lxmci__gjkj |= oswcv__snulr
        mny__vvbbx.append(iwdlr__pofub)
    hkpbr__fqdu.reverse()
    mny__vvbbx.reverse()
    jce__snsbb = min(parfor.loop_body.keys())
    ycd__sxns = parfor.loop_body[jce__snsbb]
    ycd__sxns.body = hkpbr__fqdu + ycd__sxns.body
    return mny__vvbbx


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    litw__rtnf = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    xvgsq__pam = set()
    todz__nghjl = []
    for iwdlr__pofub in init_nodes:
        if is_assign(iwdlr__pofub) and isinstance(iwdlr__pofub.value, ir.Global
            ) and isinstance(iwdlr__pofub.value.value, pytypes.FunctionType
            ) and iwdlr__pofub.value.value in litw__rtnf:
            xvgsq__pam.add(iwdlr__pofub.target.name)
        elif is_call_assign(iwdlr__pofub
            ) and iwdlr__pofub.value.func.name in xvgsq__pam:
            pass
        else:
            todz__nghjl.append(iwdlr__pofub)
    init_nodes = todz__nghjl
    enrzc__yss = types.Tuple(var_types)
    fhve__mef = lambda : None
    f_ir = compile_to_numba_ir(fhve__mef, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    ndskg__ulfp = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    jsas__don = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        ndskg__ulfp, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [jsas__don] + block.body
    block.body[-2].value.value = ndskg__ulfp
    uzs__yqfnn = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        enrzc__yss, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rev__gnytk = numba.core.target_extension.dispatcher_registry[cpu_target](
        fhve__mef)
    rev__gnytk.add_overload(uzs__yqfnn)
    return rev__gnytk


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    ebdk__dcv = len(update_funcs)
    oqkhx__oyq = len(in_col_types)
    uyjvw__asgk = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for gpd__uov in range(ebdk__dcv):
        smn__pqx = ', '.join(['redvar_arrs[{}][w_ind]'.format(jrd__hta) for
            jrd__hta in range(redvar_offsets[gpd__uov], redvar_offsets[
            gpd__uov + 1])])
        if smn__pqx:
            uyjvw__asgk += ('  {} = update_vars_{}({},  data_in[{}][i])\n'.
                format(smn__pqx, gpd__uov, smn__pqx, 0 if oqkhx__oyq == 1 else
                gpd__uov))
    uyjvw__asgk += '  return\n'
    jgmo__nch = {}
    for jrd__hta, ngi__guv in enumerate(update_funcs):
        jgmo__nch['update_vars_{}'.format(jrd__hta)] = ngi__guv
    jnvb__etfq = {}
    exec(uyjvw__asgk, jgmo__nch, jnvb__etfq)
    mjga__fmuj = jnvb__etfq['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(mjga__fmuj)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    wvz__drbq = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types])
    arg_typs = wvz__drbq, wvz__drbq, types.intp, types.intp
    ifcun__arr = len(redvar_offsets) - 1
    uyjvw__asgk = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for gpd__uov in range(ifcun__arr):
        smn__pqx = ', '.join(['redvar_arrs[{}][w_ind]'.format(jrd__hta) for
            jrd__hta in range(redvar_offsets[gpd__uov], redvar_offsets[
            gpd__uov + 1])])
        owu__rplop = ', '.join(['recv_arrs[{}][i]'.format(jrd__hta) for
            jrd__hta in range(redvar_offsets[gpd__uov], redvar_offsets[
            gpd__uov + 1])])
        if owu__rplop:
            uyjvw__asgk += '  {} = combine_vars_{}({}, {})\n'.format(smn__pqx,
                gpd__uov, smn__pqx, owu__rplop)
    uyjvw__asgk += '  return\n'
    jgmo__nch = {}
    for jrd__hta, ngi__guv in enumerate(combine_funcs):
        jgmo__nch['combine_vars_{}'.format(jrd__hta)] = ngi__guv
    jnvb__etfq = {}
    exec(uyjvw__asgk, jgmo__nch, jnvb__etfq)
    jbj__cjt = jnvb__etfq['combine_all_f']
    f_ir = compile_to_numba_ir(jbj__cjt, jgmo__nch)
    ono__vcsi = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rev__gnytk = numba.core.target_extension.dispatcher_registry[cpu_target](
        jbj__cjt)
    rev__gnytk.add_overload(ono__vcsi)
    return rev__gnytk


def gen_all_eval_func(eval_funcs, redvar_offsets):
    ifcun__arr = len(redvar_offsets) - 1
    uyjvw__asgk = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for gpd__uov in range(ifcun__arr):
        smn__pqx = ', '.join(['redvar_arrs[{}][j]'.format(jrd__hta) for
            jrd__hta in range(redvar_offsets[gpd__uov], redvar_offsets[
            gpd__uov + 1])])
        uyjvw__asgk += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(gpd__uov
            , gpd__uov, smn__pqx)
    uyjvw__asgk += '  return\n'
    jgmo__nch = {}
    for jrd__hta, ngi__guv in enumerate(eval_funcs):
        jgmo__nch['eval_vars_{}'.format(jrd__hta)] = ngi__guv
    jnvb__etfq = {}
    exec(uyjvw__asgk, jgmo__nch, jnvb__etfq)
    fpof__fjw = jnvb__etfq['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(fpof__fjw)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    zdwn__wqh = len(var_types)
    hkgeb__wfrra = [f'in{jrd__hta}' for jrd__hta in range(zdwn__wqh)]
    enrzc__yss = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    elro__wmzjp = enrzc__yss(0)
    uyjvw__asgk = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        hkgeb__wfrra))
    jnvb__etfq = {}
    exec(uyjvw__asgk, {'_zero': elro__wmzjp}, jnvb__etfq)
    utgw__nlgfp = jnvb__etfq['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(utgw__nlgfp, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': elro__wmzjp}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    qqso__iil = []
    for jrd__hta, kybzi__sgmtc in enumerate(reduce_vars):
        qqso__iil.append(ir.Assign(block.body[jrd__hta].target,
            kybzi__sgmtc, kybzi__sgmtc.loc))
        for shkop__wwc in kybzi__sgmtc.versioned_names:
            qqso__iil.append(ir.Assign(kybzi__sgmtc, ir.Var(kybzi__sgmtc.
                scope, shkop__wwc, kybzi__sgmtc.loc), kybzi__sgmtc.loc))
    block.body = block.body[:zdwn__wqh] + qqso__iil + eval_nodes
    xlmzi__iwuj = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        enrzc__yss, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rev__gnytk = numba.core.target_extension.dispatcher_registry[cpu_target](
        utgw__nlgfp)
    rev__gnytk.add_overload(xlmzi__iwuj)
    return rev__gnytk


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    zdwn__wqh = len(redvars)
    cmi__jfry = [f'v{jrd__hta}' for jrd__hta in range(zdwn__wqh)]
    hkgeb__wfrra = [f'in{jrd__hta}' for jrd__hta in range(zdwn__wqh)]
    uyjvw__asgk = 'def agg_combine({}):\n'.format(', '.join(cmi__jfry +
        hkgeb__wfrra))
    xxrs__tpolb = wrap_parfor_blocks(parfor)
    ppkae__csctq = find_topo_order(xxrs__tpolb)
    ppkae__csctq = ppkae__csctq[1:]
    unwrap_parfor_blocks(parfor)
    kdakt__asqp = {}
    vhdr__ixej = []
    for kdas__zqkwh in ppkae__csctq:
        uud__vkuw = parfor.loop_body[kdas__zqkwh]
        for iwdlr__pofub in uud__vkuw.body:
            if is_assign(iwdlr__pofub) and iwdlr__pofub.target.name in redvars:
                hrprl__ghx = iwdlr__pofub.target.name
                ind = redvars.index(hrprl__ghx)
                if ind in vhdr__ixej:
                    continue
                if len(f_ir._definitions[hrprl__ghx]) == 2:
                    var_def = f_ir._definitions[hrprl__ghx][0]
                    uyjvw__asgk += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[hrprl__ghx][1]
                    uyjvw__asgk += _match_reduce_def(var_def, f_ir, ind)
    uyjvw__asgk += '    return {}'.format(', '.join(['v{}'.format(jrd__hta) for
        jrd__hta in range(zdwn__wqh)]))
    jnvb__etfq = {}
    exec(uyjvw__asgk, {}, jnvb__etfq)
    ruiws__ntb = jnvb__etfq['agg_combine']
    arg_typs = tuple(2 * var_types)
    jgmo__nch = {'numba': numba, 'bodo': bodo, 'np': np}
    jgmo__nch.update(kdakt__asqp)
    f_ir = compile_to_numba_ir(ruiws__ntb, jgmo__nch, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    enrzc__yss = pm.typemap[block.body[-1].value.name]
    amys__wjev = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        enrzc__yss, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rev__gnytk = numba.core.target_extension.dispatcher_registry[cpu_target](
        ruiws__ntb)
    rev__gnytk.add_overload(amys__wjev)
    return rev__gnytk


def _match_reduce_def(var_def, f_ir, ind):
    uyjvw__asgk = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        uyjvw__asgk = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        zavw__enzb = guard(find_callname, f_ir, var_def)
        if zavw__enzb == ('min', 'builtins'):
            uyjvw__asgk = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if zavw__enzb == ('max', 'builtins'):
            uyjvw__asgk = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return uyjvw__asgk


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    zdwn__wqh = len(redvars)
    egfse__umn = 1
    in_vars = []
    for jrd__hta in range(egfse__umn):
        mpss__hkh = ir.Var(arr_var.scope, f'$input{jrd__hta}', arr_var.loc)
        in_vars.append(mpss__hkh)
    libl__xzq = parfor.loop_nests[0].index_variable
    pozv__iiwee = [0] * zdwn__wqh
    for uud__vkuw in parfor.loop_body.values():
        lil__aps = []
        for iwdlr__pofub in uud__vkuw.body:
            if is_var_assign(iwdlr__pofub
                ) and iwdlr__pofub.value.name == libl__xzq.name:
                continue
            if is_getitem(iwdlr__pofub
                ) and iwdlr__pofub.value.value.name == arr_var.name:
                iwdlr__pofub.value = in_vars[0]
            if is_call_assign(iwdlr__pofub) and guard(find_callname, pm.
                func_ir, iwdlr__pofub.value) == ('isna',
                'bodo.libs.array_kernels') and iwdlr__pofub.value.args[0
                ].name == arr_var.name:
                iwdlr__pofub.value = ir.Const(False, iwdlr__pofub.target.loc)
            if is_assign(iwdlr__pofub) and iwdlr__pofub.target.name in redvars:
                ind = redvars.index(iwdlr__pofub.target.name)
                pozv__iiwee[ind] = iwdlr__pofub.target
            lil__aps.append(iwdlr__pofub)
        uud__vkuw.body = lil__aps
    cmi__jfry = ['v{}'.format(jrd__hta) for jrd__hta in range(zdwn__wqh)]
    hkgeb__wfrra = ['in{}'.format(jrd__hta) for jrd__hta in range(egfse__umn)]
    uyjvw__asgk = 'def agg_update({}):\n'.format(', '.join(cmi__jfry +
        hkgeb__wfrra))
    uyjvw__asgk += '    __update_redvars()\n'
    uyjvw__asgk += '    return {}'.format(', '.join(['v{}'.format(jrd__hta) for
        jrd__hta in range(zdwn__wqh)]))
    jnvb__etfq = {}
    exec(uyjvw__asgk, {}, jnvb__etfq)
    vcv__cntp = jnvb__etfq['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * egfse__umn)
    f_ir = compile_to_numba_ir(vcv__cntp, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    hgtg__ajyp = f_ir.blocks.popitem()[1].body
    enrzc__yss = pm.typemap[hgtg__ajyp[-1].value.name]
    xxrs__tpolb = wrap_parfor_blocks(parfor)
    ppkae__csctq = find_topo_order(xxrs__tpolb)
    ppkae__csctq = ppkae__csctq[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    ycd__sxns = f_ir.blocks[ppkae__csctq[0]]
    aac__fkd = f_ir.blocks[ppkae__csctq[-1]]
    qiyx__qqt = hgtg__ajyp[:zdwn__wqh + egfse__umn]
    if zdwn__wqh > 1:
        qvn__mvar = hgtg__ajyp[-3:]
        assert is_assign(qvn__mvar[0]) and isinstance(qvn__mvar[0].value,
            ir.Expr) and qvn__mvar[0].value.op == 'build_tuple'
    else:
        qvn__mvar = hgtg__ajyp[-2:]
    for jrd__hta in range(zdwn__wqh):
        udm__cfc = hgtg__ajyp[jrd__hta].target
        tjuo__ahxh = ir.Assign(udm__cfc, pozv__iiwee[jrd__hta], udm__cfc.loc)
        qiyx__qqt.append(tjuo__ahxh)
    for jrd__hta in range(zdwn__wqh, zdwn__wqh + egfse__umn):
        udm__cfc = hgtg__ajyp[jrd__hta].target
        tjuo__ahxh = ir.Assign(udm__cfc, in_vars[jrd__hta - zdwn__wqh],
            udm__cfc.loc)
        qiyx__qqt.append(tjuo__ahxh)
    ycd__sxns.body = qiyx__qqt + ycd__sxns.body
    ngfqf__gwz = []
    for jrd__hta in range(zdwn__wqh):
        udm__cfc = hgtg__ajyp[jrd__hta].target
        tjuo__ahxh = ir.Assign(pozv__iiwee[jrd__hta], udm__cfc, udm__cfc.loc)
        ngfqf__gwz.append(tjuo__ahxh)
    aac__fkd.body += ngfqf__gwz + qvn__mvar
    qkmiq__nxfr = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        enrzc__yss, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    rev__gnytk = numba.core.target_extension.dispatcher_registry[cpu_target](
        vcv__cntp)
    rev__gnytk.add_overload(qkmiq__nxfr)
    return rev__gnytk


def _rm_arg_agg_block(block, typemap):
    uvibq__btm = []
    arr_var = None
    for jrd__hta, iwdlr__pofub in enumerate(block.body):
        if is_assign(iwdlr__pofub) and isinstance(iwdlr__pofub.value, ir.Arg):
            arr_var = iwdlr__pofub.target
            fqiuc__mbwgy = typemap[arr_var.name]
            if not isinstance(fqiuc__mbwgy, types.ArrayCompatible):
                uvibq__btm += block.body[jrd__hta + 1:]
                break
            ieydl__xaqhr = block.body[jrd__hta + 1]
            assert is_assign(ieydl__xaqhr) and isinstance(ieydl__xaqhr.
                value, ir.Expr
                ) and ieydl__xaqhr.value.op == 'getattr' and ieydl__xaqhr.value.attr == 'shape' and ieydl__xaqhr.value.value.name == arr_var.name
            vcf__oiumw = ieydl__xaqhr.target
            oadu__bjlxp = block.body[jrd__hta + 2]
            assert is_assign(oadu__bjlxp) and isinstance(oadu__bjlxp.value,
                ir.Expr
                ) and oadu__bjlxp.value.op == 'static_getitem' and oadu__bjlxp.value.value.name == vcf__oiumw.name
            uvibq__btm += block.body[jrd__hta + 3:]
            break
        uvibq__btm.append(iwdlr__pofub)
    return uvibq__btm, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    xxrs__tpolb = wrap_parfor_blocks(parfor)
    ppkae__csctq = find_topo_order(xxrs__tpolb)
    ppkae__csctq = ppkae__csctq[1:]
    unwrap_parfor_blocks(parfor)
    for kdas__zqkwh in reversed(ppkae__csctq):
        for iwdlr__pofub in reversed(parfor.loop_body[kdas__zqkwh].body):
            if isinstance(iwdlr__pofub, ir.Assign) and (iwdlr__pofub.target
                .name in parfor_params or iwdlr__pofub.target.name in
                var_to_param):
                qpt__vode = iwdlr__pofub.target.name
                rhs = iwdlr__pofub.value
                zdvp__mcm = (qpt__vode if qpt__vode in parfor_params else
                    var_to_param[qpt__vode])
                pbz__thyi = []
                if isinstance(rhs, ir.Var):
                    pbz__thyi = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    pbz__thyi = [kybzi__sgmtc.name for kybzi__sgmtc in
                        iwdlr__pofub.value.list_vars()]
                param_uses[zdvp__mcm].extend(pbz__thyi)
                for kybzi__sgmtc in pbz__thyi:
                    var_to_param[kybzi__sgmtc] = zdvp__mcm
            if isinstance(iwdlr__pofub, Parfor):
                get_parfor_reductions(iwdlr__pofub, parfor_params,
                    calltypes, reduce_varnames, param_uses, var_to_param)
    for nfo__nhlc, pbz__thyi in param_uses.items():
        if nfo__nhlc in pbz__thyi and nfo__nhlc not in reduce_varnames:
            reduce_varnames.append(nfo__nhlc)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
