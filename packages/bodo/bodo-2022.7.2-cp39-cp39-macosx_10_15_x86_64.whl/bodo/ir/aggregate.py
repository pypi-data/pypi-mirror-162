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
        xfacg__gszc = func.signature
        if xfacg__gszc == types.none(types.voidptr):
            wphx__eadkz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            vzzg__fwyx = cgutils.get_or_insert_function(builder.module,
                wphx__eadkz, sym._literal_value)
            builder.call(vzzg__fwyx, [context.get_constant_null(xfacg__gszc
                .args[0])])
        elif xfacg__gszc == types.none(types.int64, types.voidptr, types.
            voidptr):
            wphx__eadkz = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            vzzg__fwyx = cgutils.get_or_insert_function(builder.module,
                wphx__eadkz, sym._literal_value)
            builder.call(vzzg__fwyx, [context.get_constant(types.int64, 0),
                context.get_constant_null(xfacg__gszc.args[1]), context.
                get_constant_null(xfacg__gszc.args[2])])
        else:
            wphx__eadkz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            vzzg__fwyx = cgutils.get_or_insert_function(builder.module,
                wphx__eadkz, sym._literal_value)
            builder.call(vzzg__fwyx, [context.get_constant_null(xfacg__gszc
                .args[0]), context.get_constant_null(xfacg__gszc.args[1]),
                context.get_constant_null(xfacg__gszc.args[2])])
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
        dym__cago = True
        exl__hcupy = 1
        nmwi__sbfyy = -1
        if isinstance(rhs, ir.Expr):
            for sxedv__klfh in rhs.kws:
                if func_name in list_cumulative:
                    if sxedv__klfh[0] == 'skipna':
                        dym__cago = guard(find_const, func_ir, sxedv__klfh[1])
                        if not isinstance(dym__cago, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if sxedv__klfh[0] == 'dropna':
                        dym__cago = guard(find_const, func_ir, sxedv__klfh[1])
                        if not isinstance(dym__cago, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            exl__hcupy = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', exl__hcupy)
            exl__hcupy = guard(find_const, func_ir, exl__hcupy)
        if func_name == 'head':
            nmwi__sbfyy = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(nmwi__sbfyy, int):
                nmwi__sbfyy = guard(find_const, func_ir, nmwi__sbfyy)
            if nmwi__sbfyy < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = dym__cago
        func.periods = exl__hcupy
        func.head_n = nmwi__sbfyy
        if func_name == 'transform':
            kws = dict(rhs.kws)
            aedfb__oxl = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            vekk__sjb = typemap[aedfb__oxl.name]
            tssfx__xmmfw = None
            if isinstance(vekk__sjb, str):
                tssfx__xmmfw = vekk__sjb
            elif is_overload_constant_str(vekk__sjb):
                tssfx__xmmfw = get_overload_const_str(vekk__sjb)
            elif bodo.utils.typing.is_builtin_function(vekk__sjb):
                tssfx__xmmfw = bodo.utils.typing.get_builtin_function_name(
                    vekk__sjb)
            if tssfx__xmmfw not in bodo.ir.aggregate.supported_transform_funcs[
                :]:
                raise BodoError(
                    f'unsupported transform function {tssfx__xmmfw}')
            func.transform_func = supported_agg_funcs.index(tssfx__xmmfw)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    aedfb__oxl = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if aedfb__oxl == '':
        vekk__sjb = types.none
    else:
        vekk__sjb = typemap[aedfb__oxl.name]
    if is_overload_constant_dict(vekk__sjb):
        inoz__oqo = get_overload_constant_dict(vekk__sjb)
        xqnvk__ffm = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in inoz__oqo.values()]
        return xqnvk__ffm
    if vekk__sjb == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(vekk__sjb, types.BaseTuple) or is_overload_constant_list(
        vekk__sjb):
        xqnvk__ffm = []
        lvqyj__gpb = 0
        if is_overload_constant_list(vekk__sjb):
            pbdu__ghoeo = get_overload_const_list(vekk__sjb)
        else:
            pbdu__ghoeo = vekk__sjb.types
        for t in pbdu__ghoeo:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                xqnvk__ffm.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(pbdu__ghoeo) > 1:
                    func.fname = '<lambda_' + str(lvqyj__gpb) + '>'
                    lvqyj__gpb += 1
                xqnvk__ffm.append(func)
        return [xqnvk__ffm]
    if is_overload_constant_str(vekk__sjb):
        func_name = get_overload_const_str(vekk__sjb)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(vekk__sjb):
        func_name = bodo.utils.typing.get_builtin_function_name(vekk__sjb)
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
        lvqyj__gpb = 0
        wwot__kas = []
        for wlsw__zboh in f_val:
            func = get_agg_func_udf(func_ir, wlsw__zboh, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{lvqyj__gpb}>'
                lvqyj__gpb += 1
            wwot__kas.append(func)
        return wwot__kas
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
    tssfx__xmmfw = code.co_name
    return tssfx__xmmfw


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
            swjsc__svv = types.DType(args[0])
            return signature(swjsc__svv, *args)


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
        return [pdbvh__xsjkv for pdbvh__xsjkv in self.in_vars if 
            pdbvh__xsjkv is not None]

    def get_live_out_vars(self):
        return [pdbvh__xsjkv for pdbvh__xsjkv in self.out_vars if 
            pdbvh__xsjkv is not None]

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
        vkuz__jqwjz = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        ujva__hagc = list(get_index_data_arr_types(self.out_type.index))
        return vkuz__jqwjz + ujva__hagc

    def update_dead_col_info(self):
        for afz__iyi in self.dead_out_inds:
            self.gb_info_out.pop(afz__iyi, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for dec__ypdjf, run__jlne in self.gb_info_in.copy().items():
            vjylu__ufhq = []
            for wlsw__zboh, hyc__eho in run__jlne:
                if hyc__eho not in self.dead_out_inds:
                    vjylu__ufhq.append((wlsw__zboh, hyc__eho))
            if not vjylu__ufhq:
                if (dec__ypdjf is not None and dec__ypdjf not in self.
                    in_key_inds):
                    self.dead_in_inds.add(dec__ypdjf)
                self.gb_info_in.pop(dec__ypdjf)
            else:
                self.gb_info_in[dec__ypdjf] = vjylu__ufhq
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for xywa__qfsb in range(1, len(self.in_vars)):
                afz__iyi = self.n_in_table_arrays + xywa__qfsb - 1
                if afz__iyi in self.dead_in_inds:
                    self.in_vars[xywa__qfsb] = None
        else:
            for xywa__qfsb in range(len(self.in_vars)):
                if xywa__qfsb in self.dead_in_inds:
                    self.in_vars[xywa__qfsb] = None

    def __repr__(self):
        lju__tser = ', '.join(pdbvh__xsjkv.name for pdbvh__xsjkv in self.
            get_live_in_vars())
        lji__iqgxs = f'{self.df_in}{{{lju__tser}}}'
        jjxw__dxxw = ', '.join(pdbvh__xsjkv.name for pdbvh__xsjkv in self.
            get_live_out_vars())
        hral__dgh = f'{self.df_out}{{{jjxw__dxxw}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {lji__iqgxs} {hral__dgh}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({pdbvh__xsjkv.name for pdbvh__xsjkv in aggregate_node.
        get_live_in_vars()})
    def_set.update({pdbvh__xsjkv.name for pdbvh__xsjkv in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    odr__ntz = agg_node.out_vars[0]
    if odr__ntz is not None and odr__ntz.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            qjx__lue = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(qjx__lue)
        else:
            agg_node.dead_out_inds.add(0)
    for xywa__qfsb in range(1, len(agg_node.out_vars)):
        pdbvh__xsjkv = agg_node.out_vars[xywa__qfsb]
        if pdbvh__xsjkv is not None and pdbvh__xsjkv.name not in lives:
            agg_node.out_vars[xywa__qfsb] = None
            afz__iyi = agg_node.n_out_table_arrays + xywa__qfsb - 1
            agg_node.dead_out_inds.add(afz__iyi)
    if all(pdbvh__xsjkv is None for pdbvh__xsjkv in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    klpm__vet = {pdbvh__xsjkv.name for pdbvh__xsjkv in aggregate_node.
        get_live_out_vars()}
    return set(), klpm__vet


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for xywa__qfsb in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[xywa__qfsb] is not None:
            aggregate_node.in_vars[xywa__qfsb] = replace_vars_inner(
                aggregate_node.in_vars[xywa__qfsb], var_dict)
    for xywa__qfsb in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[xywa__qfsb] is not None:
            aggregate_node.out_vars[xywa__qfsb] = replace_vars_inner(
                aggregate_node.out_vars[xywa__qfsb], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for xywa__qfsb in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[xywa__qfsb] is not None:
            aggregate_node.in_vars[xywa__qfsb] = visit_vars_inner(
                aggregate_node.in_vars[xywa__qfsb], callback, cbdata)
    for xywa__qfsb in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[xywa__qfsb] is not None:
            aggregate_node.out_vars[xywa__qfsb] = visit_vars_inner(
                aggregate_node.out_vars[xywa__qfsb], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    suvk__mzsnj = []
    for wigdx__tgq in aggregate_node.get_live_in_vars():
        ybpxm__ikopv = equiv_set.get_shape(wigdx__tgq)
        if ybpxm__ikopv is not None:
            suvk__mzsnj.append(ybpxm__ikopv[0])
    if len(suvk__mzsnj) > 1:
        equiv_set.insert_equiv(*suvk__mzsnj)
    nylpw__fdpy = []
    suvk__mzsnj = []
    for wigdx__tgq in aggregate_node.get_live_out_vars():
        cri__lznlk = typemap[wigdx__tgq.name]
        ryr__wvp = array_analysis._gen_shape_call(equiv_set, wigdx__tgq,
            cri__lznlk.ndim, None, nylpw__fdpy)
        equiv_set.insert_equiv(wigdx__tgq, ryr__wvp)
        suvk__mzsnj.append(ryr__wvp[0])
        equiv_set.define(wigdx__tgq, set())
    if len(suvk__mzsnj) > 1:
        equiv_set.insert_equiv(*suvk__mzsnj)
    return [], nylpw__fdpy


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    zdyub__cxb = aggregate_node.get_live_in_vars()
    kuzjv__nou = aggregate_node.get_live_out_vars()
    umcq__grfa = Distribution.OneD
    for wigdx__tgq in zdyub__cxb:
        umcq__grfa = Distribution(min(umcq__grfa.value, array_dists[
            wigdx__tgq.name].value))
    vawab__ipsr = Distribution(min(umcq__grfa.value, Distribution.OneD_Var.
        value))
    for wigdx__tgq in kuzjv__nou:
        if wigdx__tgq.name in array_dists:
            vawab__ipsr = Distribution(min(vawab__ipsr.value, array_dists[
                wigdx__tgq.name].value))
    if vawab__ipsr != Distribution.OneD_Var:
        umcq__grfa = vawab__ipsr
    for wigdx__tgq in zdyub__cxb:
        array_dists[wigdx__tgq.name] = umcq__grfa
    for wigdx__tgq in kuzjv__nou:
        array_dists[wigdx__tgq.name] = vawab__ipsr


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for wigdx__tgq in agg_node.get_live_out_vars():
        definitions[wigdx__tgq.name].append(agg_node)
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
    xhuyc__lid = agg_node.get_live_in_vars()
    wkzv__eogpd = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for pdbvh__xsjkv in (xhuyc__lid + wkzv__eogpd):
            if array_dists[pdbvh__xsjkv.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                pdbvh__xsjkv.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    xqnvk__ffm = []
    func_out_types = []
    for hyc__eho, (dec__ypdjf, func) in agg_node.gb_info_out.items():
        if dec__ypdjf is not None:
            t = agg_node.in_col_types[dec__ypdjf]
            in_col_typs.append(t)
        xqnvk__ffm.append(func)
        func_out_types.append(out_col_typs[hyc__eho])
    itbzm__srtf = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for xywa__qfsb, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            itbzm__srtf.update({f'in_cat_dtype_{xywa__qfsb}': in_col_typ})
    for xywa__qfsb, fud__wkxuo in enumerate(out_col_typs):
        if isinstance(fud__wkxuo, bodo.CategoricalArrayType):
            itbzm__srtf.update({f'out_cat_dtype_{xywa__qfsb}': fud__wkxuo})
    udf_func_struct = get_udf_func_struct(xqnvk__ffm, in_col_typs,
        typingctx, targetctx)
    out_var_types = [(typemap[pdbvh__xsjkv.name] if pdbvh__xsjkv is not
        None else types.none) for pdbvh__xsjkv in agg_node.out_vars]
    zecoo__hxygk, izr__ltm = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    itbzm__srtf.update(izr__ltm)
    itbzm__srtf.update({'pd': pd, 'pre_alloc_string_array':
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
            itbzm__srtf.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            itbzm__srtf.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    sksf__cwzg = {}
    exec(zecoo__hxygk, {}, sksf__cwzg)
    yij__kqb = sksf__cwzg['agg_top']
    mlrg__pop = compile_to_numba_ir(yij__kqb, itbzm__srtf, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[pdbvh__xsjkv
        .name] for pdbvh__xsjkv in xhuyc__lid), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(mlrg__pop, xhuyc__lid)
    wte__qkoh = mlrg__pop.body[-2].value.value
    cyx__zlnis = mlrg__pop.body[:-2]
    for xywa__qfsb, pdbvh__xsjkv in enumerate(wkzv__eogpd):
        gen_getitem(pdbvh__xsjkv, wte__qkoh, xywa__qfsb, calltypes, cyx__zlnis)
    return cyx__zlnis


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        epxa__hywax = IntDtype(t.dtype).name
        assert epxa__hywax.endswith('Dtype()')
        epxa__hywax = epxa__hywax[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{epxa__hywax}'))"
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
        ujgs__rdhgz = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {ujgs__rdhgz}_cat_dtype_{colnum})'
            )
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
    osnh__wfx = udf_func_struct.var_typs
    wbglz__mynki = len(osnh__wfx)
    zecoo__hxygk = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    zecoo__hxygk += '    if is_null_pointer(in_table):\n'
    zecoo__hxygk += '        return\n'
    zecoo__hxygk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in osnh__wfx]), 
        ',' if len(osnh__wfx) == 1 else '')
    ihts__aluk = n_keys
    zilx__nwem = []
    redvar_offsets = []
    qjb__mhm = []
    if do_combine:
        for xywa__qfsb, wlsw__zboh in enumerate(allfuncs):
            if wlsw__zboh.ftype != 'udf':
                ihts__aluk += wlsw__zboh.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(ihts__aluk, ihts__aluk +
                    wlsw__zboh.n_redvars))
                ihts__aluk += wlsw__zboh.n_redvars
                qjb__mhm.append(data_in_typs_[func_idx_to_in_col[xywa__qfsb]])
                zilx__nwem.append(func_idx_to_in_col[xywa__qfsb] + n_keys)
    else:
        for xywa__qfsb, wlsw__zboh in enumerate(allfuncs):
            if wlsw__zboh.ftype != 'udf':
                ihts__aluk += wlsw__zboh.ncols_post_shuffle
            else:
                redvar_offsets += list(range(ihts__aluk + 1, ihts__aluk + 1 +
                    wlsw__zboh.n_redvars))
                ihts__aluk += wlsw__zboh.n_redvars + 1
                qjb__mhm.append(data_in_typs_[func_idx_to_in_col[xywa__qfsb]])
                zilx__nwem.append(func_idx_to_in_col[xywa__qfsb] + n_keys)
    assert len(redvar_offsets) == wbglz__mynki
    vvsg__ncfwp = len(qjb__mhm)
    zwid__vdjkn = []
    for xywa__qfsb, t in enumerate(qjb__mhm):
        zwid__vdjkn.append(_gen_dummy_alloc(t, xywa__qfsb, True))
    zecoo__hxygk += '    data_in_dummy = ({}{})\n'.format(','.join(
        zwid__vdjkn), ',' if len(qjb__mhm) == 1 else '')
    zecoo__hxygk += """
    # initialize redvar cols
"""
    zecoo__hxygk += '    init_vals = __init_func()\n'
    for xywa__qfsb in range(wbglz__mynki):
        zecoo__hxygk += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(xywa__qfsb, redvar_offsets[xywa__qfsb], xywa__qfsb))
        zecoo__hxygk += '    incref(redvar_arr_{})\n'.format(xywa__qfsb)
        zecoo__hxygk += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            xywa__qfsb, xywa__qfsb)
    zecoo__hxygk += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(xywa__qfsb) for xywa__qfsb in range(
        wbglz__mynki)]), ',' if wbglz__mynki == 1 else '')
    zecoo__hxygk += '\n'
    for xywa__qfsb in range(vvsg__ncfwp):
        zecoo__hxygk += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(xywa__qfsb, zilx__nwem[xywa__qfsb], xywa__qfsb))
        zecoo__hxygk += '    incref(data_in_{})\n'.format(xywa__qfsb)
    zecoo__hxygk += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(xywa__qfsb) for xywa__qfsb in range(vvsg__ncfwp)]), ',' if 
        vvsg__ncfwp == 1 else '')
    zecoo__hxygk += '\n'
    zecoo__hxygk += '    for i in range(len(data_in_0)):\n'
    zecoo__hxygk += '        w_ind = row_to_group[i]\n'
    zecoo__hxygk += '        if w_ind != -1:\n'
    zecoo__hxygk += (
        '            __update_redvars(redvars, data_in, w_ind, i)\n')
    sksf__cwzg = {}
    exec(zecoo__hxygk, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, sksf__cwzg)
    return sksf__cwzg['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    osnh__wfx = udf_func_struct.var_typs
    wbglz__mynki = len(osnh__wfx)
    zecoo__hxygk = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    zecoo__hxygk += '    if is_null_pointer(in_table):\n'
    zecoo__hxygk += '        return\n'
    zecoo__hxygk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in osnh__wfx]), 
        ',' if len(osnh__wfx) == 1 else '')
    btptq__wlbij = n_keys
    tawh__dsshg = n_keys
    uomn__edg = []
    hcoz__cmttc = []
    for wlsw__zboh in allfuncs:
        if wlsw__zboh.ftype != 'udf':
            btptq__wlbij += wlsw__zboh.ncols_pre_shuffle
            tawh__dsshg += wlsw__zboh.ncols_post_shuffle
        else:
            uomn__edg += list(range(btptq__wlbij, btptq__wlbij + wlsw__zboh
                .n_redvars))
            hcoz__cmttc += list(range(tawh__dsshg + 1, tawh__dsshg + 1 +
                wlsw__zboh.n_redvars))
            btptq__wlbij += wlsw__zboh.n_redvars
            tawh__dsshg += 1 + wlsw__zboh.n_redvars
    assert len(uomn__edg) == wbglz__mynki
    zecoo__hxygk += """
    # initialize redvar cols
"""
    zecoo__hxygk += '    init_vals = __init_func()\n'
    for xywa__qfsb in range(wbglz__mynki):
        zecoo__hxygk += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(xywa__qfsb, hcoz__cmttc[xywa__qfsb], xywa__qfsb))
        zecoo__hxygk += '    incref(redvar_arr_{})\n'.format(xywa__qfsb)
        zecoo__hxygk += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            xywa__qfsb, xywa__qfsb)
    zecoo__hxygk += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(xywa__qfsb) for xywa__qfsb in range(
        wbglz__mynki)]), ',' if wbglz__mynki == 1 else '')
    zecoo__hxygk += '\n'
    for xywa__qfsb in range(wbglz__mynki):
        zecoo__hxygk += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(xywa__qfsb, uomn__edg[xywa__qfsb], xywa__qfsb))
        zecoo__hxygk += '    incref(recv_redvar_arr_{})\n'.format(xywa__qfsb)
    zecoo__hxygk += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(xywa__qfsb) for xywa__qfsb in range(
        wbglz__mynki)]), ',' if wbglz__mynki == 1 else '')
    zecoo__hxygk += '\n'
    if wbglz__mynki:
        zecoo__hxygk += '    for i in range(len(recv_redvar_arr_0)):\n'
        zecoo__hxygk += '        w_ind = row_to_group[i]\n'
        zecoo__hxygk += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    sksf__cwzg = {}
    exec(zecoo__hxygk, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, sksf__cwzg)
    return sksf__cwzg['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    osnh__wfx = udf_func_struct.var_typs
    wbglz__mynki = len(osnh__wfx)
    ihts__aluk = n_keys
    redvar_offsets = []
    fyws__gbps = []
    shz__kqxg = []
    for xywa__qfsb, wlsw__zboh in enumerate(allfuncs):
        if wlsw__zboh.ftype != 'udf':
            ihts__aluk += wlsw__zboh.ncols_post_shuffle
        else:
            fyws__gbps.append(ihts__aluk)
            redvar_offsets += list(range(ihts__aluk + 1, ihts__aluk + 1 +
                wlsw__zboh.n_redvars))
            ihts__aluk += 1 + wlsw__zboh.n_redvars
            shz__kqxg.append(out_data_typs_[xywa__qfsb])
    assert len(redvar_offsets) == wbglz__mynki
    vvsg__ncfwp = len(shz__kqxg)
    zecoo__hxygk = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    zecoo__hxygk += '    if is_null_pointer(table):\n'
    zecoo__hxygk += '        return\n'
    zecoo__hxygk += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in osnh__wfx]), 
        ',' if len(osnh__wfx) == 1 else '')
    zecoo__hxygk += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in shz__kqxg
        ]), ',' if len(shz__kqxg) == 1 else '')
    for xywa__qfsb in range(wbglz__mynki):
        zecoo__hxygk += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(xywa__qfsb, redvar_offsets[xywa__qfsb], xywa__qfsb))
        zecoo__hxygk += '    incref(redvar_arr_{})\n'.format(xywa__qfsb)
    zecoo__hxygk += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(xywa__qfsb) for xywa__qfsb in range(
        wbglz__mynki)]), ',' if wbglz__mynki == 1 else '')
    zecoo__hxygk += '\n'
    for xywa__qfsb in range(vvsg__ncfwp):
        zecoo__hxygk += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(xywa__qfsb, fyws__gbps[xywa__qfsb], xywa__qfsb))
        zecoo__hxygk += '    incref(data_out_{})\n'.format(xywa__qfsb)
    zecoo__hxygk += '    data_out = ({}{})\n'.format(','.join([
        'data_out_{}'.format(xywa__qfsb) for xywa__qfsb in range(
        vvsg__ncfwp)]), ',' if vvsg__ncfwp == 1 else '')
    zecoo__hxygk += '\n'
    zecoo__hxygk += '    for i in range(len(data_out_0)):\n'
    zecoo__hxygk += '        __eval_res(redvars, data_out, i)\n'
    sksf__cwzg = {}
    exec(zecoo__hxygk, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, sksf__cwzg)
    return sksf__cwzg['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    ihts__aluk = n_keys
    gnode__hqqtu = []
    for xywa__qfsb, wlsw__zboh in enumerate(allfuncs):
        if wlsw__zboh.ftype == 'gen_udf':
            gnode__hqqtu.append(ihts__aluk)
            ihts__aluk += 1
        elif wlsw__zboh.ftype != 'udf':
            ihts__aluk += wlsw__zboh.ncols_post_shuffle
        else:
            ihts__aluk += wlsw__zboh.n_redvars + 1
    zecoo__hxygk = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    zecoo__hxygk += '    if num_groups == 0:\n'
    zecoo__hxygk += '        return\n'
    for xywa__qfsb, func in enumerate(udf_func_struct.general_udf_funcs):
        zecoo__hxygk += '    # col {}\n'.format(xywa__qfsb)
        zecoo__hxygk += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(gnode__hqqtu[xywa__qfsb], xywa__qfsb))
        zecoo__hxygk += '    incref(out_col)\n'
        zecoo__hxygk += '    for j in range(num_groups):\n'
        zecoo__hxygk += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(xywa__qfsb, xywa__qfsb))
        zecoo__hxygk += '        incref(in_col)\n'
        zecoo__hxygk += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(xywa__qfsb))
    itbzm__srtf = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    esw__gaux = 0
    for xywa__qfsb, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[esw__gaux]
        itbzm__srtf['func_{}'.format(esw__gaux)] = func
        itbzm__srtf['in_col_{}_typ'.format(esw__gaux)] = in_col_typs[
            func_idx_to_in_col[xywa__qfsb]]
        itbzm__srtf['out_col_{}_typ'.format(esw__gaux)] = out_col_typs[
            xywa__qfsb]
        esw__gaux += 1
    sksf__cwzg = {}
    exec(zecoo__hxygk, itbzm__srtf, sksf__cwzg)
    wlsw__zboh = sksf__cwzg['bodo_gb_apply_general_udfs{}'.format(label_suffix)
        ]
    imrco__cuwqk = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(imrco__cuwqk, nopython=True)(wlsw__zboh)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    wtxre__rke = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        luloj__mgfh = []
        if agg_node.in_vars[0] is not None:
            luloj__mgfh.append('arg0')
        for xywa__qfsb in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if xywa__qfsb not in agg_node.dead_in_inds:
                luloj__mgfh.append(f'arg{xywa__qfsb}')
    else:
        luloj__mgfh = [f'arg{xywa__qfsb}' for xywa__qfsb, pdbvh__xsjkv in
            enumerate(agg_node.in_vars) if pdbvh__xsjkv is not None]
    zecoo__hxygk = f"def agg_top({', '.join(luloj__mgfh)}):\n"
    umpg__bbtpq = []
    if agg_node.is_in_table_format:
        umpg__bbtpq = agg_node.in_key_inds + [dec__ypdjf for dec__ypdjf,
            foe__mesw in agg_node.gb_info_out.values() if dec__ypdjf is not
            None]
        if agg_node.input_has_index:
            umpg__bbtpq.append(agg_node.n_in_cols - 1)
        bdhc__yevfr = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        qtice__cybe = []
        for xywa__qfsb in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if xywa__qfsb in agg_node.dead_in_inds:
                qtice__cybe.append('None')
            else:
                qtice__cybe.append(f'arg{xywa__qfsb}')
        bre__ahezq = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        zecoo__hxygk += f"""    table = py_data_to_cpp_table({bre__ahezq}, ({', '.join(qtice__cybe)}{bdhc__yevfr}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        fncm__xzyni = [f'arg{xywa__qfsb}' for xywa__qfsb in agg_node.
            in_key_inds]
        dri__ryki = [f'arg{dec__ypdjf}' for dec__ypdjf, foe__mesw in
            agg_node.gb_info_out.values() if dec__ypdjf is not None]
        yydok__qho = fncm__xzyni + dri__ryki
        if agg_node.input_has_index:
            yydok__qho.append(f'arg{len(agg_node.in_vars) - 1}')
        zecoo__hxygk += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({jzrhd__avek})' for jzrhd__avek in yydok__qho))
        zecoo__hxygk += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    shvx__miwz = []
    func_idx_to_in_col = []
    ktxw__orc = []
    dym__cago = False
    phtlt__clcg = 1
    nmwi__sbfyy = -1
    cdes__ccqcg = 0
    jwaf__ppd = 0
    xqnvk__ffm = [func for foe__mesw, func in agg_node.gb_info_out.values()]
    for gkxrd__dljag, func in enumerate(xqnvk__ffm):
        shvx__miwz.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            cdes__ccqcg += 1
        if hasattr(func, 'skipdropna'):
            dym__cago = func.skipdropna
        if func.ftype == 'shift':
            phtlt__clcg = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            jwaf__ppd = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            nmwi__sbfyy = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(gkxrd__dljag)
        if func.ftype == 'udf':
            ktxw__orc.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            ktxw__orc.append(0)
            do_combine = False
    shvx__miwz.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if cdes__ccqcg > 0:
        if cdes__ccqcg != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    dagr__tvzv = []
    if udf_func_struct is not None:
        ndc__wrggu = next_label()
        if udf_func_struct.regular_udfs:
            imrco__cuwqk = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            auao__sfjoi = numba.cfunc(imrco__cuwqk, nopython=True)(
                gen_update_cb(udf_func_struct, allfuncs, n_keys,
                in_col_typs, do_combine, func_idx_to_in_col, ndc__wrggu))
            nfq__xzid = numba.cfunc(imrco__cuwqk, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, ndc__wrggu))
            zoyfj__saq = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys,
                func_out_types, ndc__wrggu))
            udf_func_struct.set_regular_cfuncs(auao__sfjoi, nfq__xzid,
                zoyfj__saq)
            for ptvb__friyf in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[ptvb__friyf.native_name] = ptvb__friyf
                gb_agg_cfunc_addr[ptvb__friyf.native_name
                    ] = ptvb__friyf.address
        if udf_func_struct.general_udfs:
            xlyw__hnq = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, func_out_types, func_idx_to_in_col,
                ndc__wrggu)
            udf_func_struct.set_general_cfunc(xlyw__hnq)
        osnh__wfx = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        bfk__bsis = 0
        xywa__qfsb = 0
        for voc__yuwcb, wlsw__zboh in zip(agg_node.gb_info_out.keys(), allfuncs
            ):
            if wlsw__zboh.ftype in ('udf', 'gen_udf'):
                dagr__tvzv.append(out_col_typs[voc__yuwcb])
                for ueu__rqj in range(bfk__bsis, bfk__bsis + ktxw__orc[
                    xywa__qfsb]):
                    dagr__tvzv.append(dtype_to_array_type(osnh__wfx[ueu__rqj]))
                bfk__bsis += ktxw__orc[xywa__qfsb]
                xywa__qfsb += 1
        zecoo__hxygk += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{xywa__qfsb}' for xywa__qfsb in range(len(dagr__tvzv)))}{',' if len(dagr__tvzv) == 1 else ''}))
"""
        zecoo__hxygk += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(dagr__tvzv)})
"""
        if udf_func_struct.regular_udfs:
            zecoo__hxygk += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{auao__sfjoi.native_name}')\n"
                )
            zecoo__hxygk += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{nfq__xzid.native_name}')\n"
                )
            zecoo__hxygk += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{zoyfj__saq.native_name}')\n"
                )
            zecoo__hxygk += f"""    cpp_cb_update_addr = get_agg_udf_addr('{auao__sfjoi.native_name}')
"""
            zecoo__hxygk += f"""    cpp_cb_combine_addr = get_agg_udf_addr('{nfq__xzid.native_name}')
"""
            zecoo__hxygk += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{zoyfj__saq.native_name}')\n"
                )
        else:
            zecoo__hxygk += '    cpp_cb_update_addr = 0\n'
            zecoo__hxygk += '    cpp_cb_combine_addr = 0\n'
            zecoo__hxygk += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            ptvb__friyf = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[ptvb__friyf.native_name] = ptvb__friyf
            gb_agg_cfunc_addr[ptvb__friyf.native_name] = ptvb__friyf.address
            zecoo__hxygk += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{ptvb__friyf.native_name}')\n"
                )
            zecoo__hxygk += f"""    cpp_cb_general_addr = get_agg_udf_addr('{ptvb__friyf.native_name}')
"""
        else:
            zecoo__hxygk += '    cpp_cb_general_addr = 0\n'
    else:
        zecoo__hxygk += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        zecoo__hxygk += '    cpp_cb_update_addr = 0\n'
        zecoo__hxygk += '    cpp_cb_combine_addr = 0\n'
        zecoo__hxygk += '    cpp_cb_eval_addr = 0\n'
        zecoo__hxygk += '    cpp_cb_general_addr = 0\n'
    zecoo__hxygk += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(wlsw__zboh.ftype)) for
        wlsw__zboh in allfuncs] + ['0']))
    zecoo__hxygk += (
        f'    func_offsets = np.array({str(shvx__miwz)}, dtype=np.int32)\n')
    if len(ktxw__orc) > 0:
        zecoo__hxygk += (
            f'    udf_ncols = np.array({str(ktxw__orc)}, dtype=np.int32)\n')
    else:
        zecoo__hxygk += '    udf_ncols = np.array([0], np.int32)\n'
    zecoo__hxygk += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    bxyz__kqf = (agg_node._num_shuffle_keys if agg_node._num_shuffle_keys !=
        -1 else n_keys)
    zecoo__hxygk += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {dym__cago}, {phtlt__clcg}, {jwaf__ppd}, {nmwi__sbfyy}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes, {bxyz__kqf})
"""
    vrrer__kwb = []
    mhb__siyph = 0
    if agg_node.return_key:
        stxst__rif = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for xywa__qfsb in range(n_keys):
            afz__iyi = stxst__rif + xywa__qfsb
            vrrer__kwb.append(afz__iyi if afz__iyi not in agg_node.
                dead_out_inds else -1)
            mhb__siyph += 1
    for voc__yuwcb in agg_node.gb_info_out.keys():
        vrrer__kwb.append(voc__yuwcb)
        mhb__siyph += 1
    jjfbb__vjpxt = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            vrrer__kwb.append(agg_node.n_out_cols - 1)
        else:
            jjfbb__vjpxt = True
    bdhc__yevfr = ',' if wtxre__rke == 1 else ''
    isj__hacr = (
        f"({', '.join(f'out_type{xywa__qfsb}' for xywa__qfsb in range(wtxre__rke))}{bdhc__yevfr})"
        )
    izwco__imtyr = []
    pdse__mkteq = []
    for xywa__qfsb, t in enumerate(out_col_typs):
        if xywa__qfsb not in agg_node.dead_out_inds and type_has_unknown_cats(t
            ):
            if xywa__qfsb in agg_node.gb_info_out:
                dec__ypdjf = agg_node.gb_info_out[xywa__qfsb][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                arfyh__xjhb = xywa__qfsb - stxst__rif
                dec__ypdjf = agg_node.in_key_inds[arfyh__xjhb]
            pdse__mkteq.append(xywa__qfsb)
            if (agg_node.is_in_table_format and dec__ypdjf < agg_node.
                n_in_table_arrays):
                izwco__imtyr.append(f'get_table_data(arg0, {dec__ypdjf})')
            else:
                izwco__imtyr.append(f'arg{dec__ypdjf}')
    bdhc__yevfr = ',' if len(izwco__imtyr) == 1 else ''
    zecoo__hxygk += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {isj__hacr}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(izwco__imtyr)}{bdhc__yevfr}), unknown_cat_out_inds)
"""
    zecoo__hxygk += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    zecoo__hxygk += '    delete_table_decref_arrays(table)\n'
    zecoo__hxygk += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for xywa__qfsb in range(n_keys):
            if vrrer__kwb[xywa__qfsb] == -1:
                zecoo__hxygk += (
                    f'    decref_table_array(out_table, {xywa__qfsb})\n')
    if jjfbb__vjpxt:
        ggi__hhw = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        zecoo__hxygk += f'    decref_table_array(out_table, {ggi__hhw})\n'
    zecoo__hxygk += '    delete_table(out_table)\n'
    zecoo__hxygk += '    ev_clean.finalize()\n'
    zecoo__hxygk += '    return out_data\n'
    xxzq__apwn = {f'out_type{xywa__qfsb}': out_var_types[xywa__qfsb] for
        xywa__qfsb in range(wtxre__rke)}
    xxzq__apwn['out_col_inds'] = MetaType(tuple(vrrer__kwb))
    xxzq__apwn['in_col_inds'] = MetaType(tuple(umpg__bbtpq))
    xxzq__apwn['cpp_table_to_py_data'] = cpp_table_to_py_data
    xxzq__apwn['py_data_to_cpp_table'] = py_data_to_cpp_table
    xxzq__apwn.update({f'udf_type{xywa__qfsb}': t for xywa__qfsb, t in
        enumerate(dagr__tvzv)})
    xxzq__apwn['udf_dummy_col_inds'] = MetaType(tuple(range(len(dagr__tvzv))))
    xxzq__apwn['create_dummy_table'] = create_dummy_table
    xxzq__apwn['unknown_cat_out_inds'] = MetaType(tuple(pdse__mkteq))
    xxzq__apwn['get_table_data'] = bodo.hiframes.table.get_table_data
    return zecoo__hxygk, xxzq__apwn


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    trxf__ghmve = tuple(unwrap_typeref(data_types.types[xywa__qfsb]) for
        xywa__qfsb in range(len(data_types.types)))
    lrox__jfys = bodo.TableType(trxf__ghmve)
    xxzq__apwn = {'table_type': lrox__jfys}
    zecoo__hxygk = 'def impl(data_types):\n'
    zecoo__hxygk += '  py_table = init_table(table_type, False)\n'
    zecoo__hxygk += '  py_table = set_table_len(py_table, 1)\n'
    for cri__lznlk, hxa__tzjx in lrox__jfys.type_to_blk.items():
        xxzq__apwn[f'typ_list_{hxa__tzjx}'] = types.List(cri__lznlk)
        xxzq__apwn[f'typ_{hxa__tzjx}'] = cri__lznlk
        zlmks__vtg = len(lrox__jfys.block_to_arr_ind[hxa__tzjx])
        zecoo__hxygk += f"""  arr_list_{hxa__tzjx} = alloc_list_like(typ_list_{hxa__tzjx}, {zlmks__vtg}, False)
"""
        zecoo__hxygk += f'  for i in range(len(arr_list_{hxa__tzjx})):\n'
        zecoo__hxygk += (
            f'    arr_list_{hxa__tzjx}[i] = alloc_type(1, typ_{hxa__tzjx}, (-1,))\n'
            )
        zecoo__hxygk += f"""  py_table = set_table_block(py_table, arr_list_{hxa__tzjx}, {hxa__tzjx})
"""
    zecoo__hxygk += '  return py_table\n'
    xxzq__apwn.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    sksf__cwzg = {}
    exec(zecoo__hxygk, xxzq__apwn, sksf__cwzg)
    return sksf__cwzg['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    aukbq__hip = agg_node.in_vars[0].name
    doo__jhdbm, tmk__vbu, nvwr__bmg = block_use_map[aukbq__hip]
    if tmk__vbu or nvwr__bmg:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        kjx__akhhs, sscdn__iyv, csch__cun = _compute_table_column_uses(agg_node
            .out_vars[0].name, table_col_use_map, equiv_vars)
        if sscdn__iyv or csch__cun:
            kjx__akhhs = set(range(agg_node.n_out_table_arrays))
    else:
        kjx__akhhs = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            kjx__akhhs = {0}
    ddz__vqev = set(xywa__qfsb for xywa__qfsb in agg_node.in_key_inds if 
        xywa__qfsb < agg_node.n_in_table_arrays)
    obue__ducc = set(agg_node.gb_info_out[xywa__qfsb][0] for xywa__qfsb in
        kjx__akhhs if xywa__qfsb in agg_node.gb_info_out and agg_node.
        gb_info_out[xywa__qfsb][0] is not None)
    obue__ducc |= ddz__vqev | doo__jhdbm
    gca__odvjn = len(set(range(agg_node.n_in_table_arrays)) - obue__ducc) == 0
    block_use_map[aukbq__hip] = obue__ducc, gca__odvjn, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    yrypx__imtq = agg_node.n_out_table_arrays
    gyj__ksno = agg_node.out_vars[0].name
    puuh__gwnf = _find_used_columns(gyj__ksno, yrypx__imtq, column_live_map,
        equiv_vars)
    if puuh__gwnf is None:
        return False
    wwhc__cxr = set(range(yrypx__imtq)) - puuh__gwnf
    ktz__jmpih = len(wwhc__cxr - agg_node.dead_out_inds) != 0
    if ktz__jmpih:
        agg_node.dead_out_inds.update(wwhc__cxr)
        agg_node.update_dead_col_info()
    return ktz__jmpih


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for kqh__uelbc in block.body:
            if is_call_assign(kqh__uelbc) and find_callname(f_ir,
                kqh__uelbc.value) == ('len', 'builtins'
                ) and kqh__uelbc.value.args[0].name == f_ir.arg_names[0]:
                phxkd__albod = get_definition(f_ir, kqh__uelbc.value.func)
                phxkd__albod.name = 'dummy_agg_count'
                phxkd__albod.value = dummy_agg_count
    kxnbi__caty = get_name_var_table(f_ir.blocks)
    gnczr__gdqw = {}
    for name, foe__mesw in kxnbi__caty.items():
        gnczr__gdqw[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, gnczr__gdqw)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    auqra__wcg = numba.core.compiler.Flags()
    auqra__wcg.nrt = True
    peknh__nrr = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, auqra__wcg)
    peknh__nrr.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, gvwye__wsfa, calltypes, foe__mesw = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    xtnkv__ijdi = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    lwgw__egiau = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    nbp__maqi = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    nvus__mongp = nbp__maqi(typemap, calltypes)
    pm = lwgw__egiau(typingctx, targetctx, None, f_ir, typemap, gvwye__wsfa,
        calltypes, nvus__mongp, {}, auqra__wcg, None)
    fmql__ugtav = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = lwgw__egiau(typingctx, targetctx, None, f_ir, typemap, gvwye__wsfa,
        calltypes, nvus__mongp, {}, auqra__wcg, fmql__ugtav)
    bupnp__kjavf = numba.core.typed_passes.InlineOverloads()
    bupnp__kjavf.run_pass(pm)
    uyb__etgn = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    uyb__etgn.run()
    for block in f_ir.blocks.values():
        for kqh__uelbc in block.body:
            if is_assign(kqh__uelbc) and isinstance(kqh__uelbc.value, (ir.
                Arg, ir.Var)) and isinstance(typemap[kqh__uelbc.target.name
                ], SeriesType):
                cri__lznlk = typemap.pop(kqh__uelbc.target.name)
                typemap[kqh__uelbc.target.name] = cri__lznlk.data
            if is_call_assign(kqh__uelbc) and find_callname(f_ir,
                kqh__uelbc.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[kqh__uelbc.target.name].remove(kqh__uelbc
                    .value)
                kqh__uelbc.value = kqh__uelbc.value.args[0]
                f_ir._definitions[kqh__uelbc.target.name].append(kqh__uelbc
                    .value)
            if is_call_assign(kqh__uelbc) and find_callname(f_ir,
                kqh__uelbc.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[kqh__uelbc.target.name].remove(kqh__uelbc
                    .value)
                kqh__uelbc.value = ir.Const(False, kqh__uelbc.loc)
                f_ir._definitions[kqh__uelbc.target.name].append(kqh__uelbc
                    .value)
            if is_call_assign(kqh__uelbc) and find_callname(f_ir,
                kqh__uelbc.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[kqh__uelbc.target.name].remove(kqh__uelbc
                    .value)
                kqh__uelbc.value = ir.Const(False, kqh__uelbc.loc)
                f_ir._definitions[kqh__uelbc.target.name].append(kqh__uelbc
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    wmvmr__ulj = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, xtnkv__ijdi)
    wmvmr__ulj.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    vlc__wzmu = numba.core.compiler.StateDict()
    vlc__wzmu.func_ir = f_ir
    vlc__wzmu.typemap = typemap
    vlc__wzmu.calltypes = calltypes
    vlc__wzmu.typingctx = typingctx
    vlc__wzmu.targetctx = targetctx
    vlc__wzmu.return_type = gvwye__wsfa
    numba.core.rewrites.rewrite_registry.apply('after-inference', vlc__wzmu)
    lusbi__voyz = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        gvwye__wsfa, typingctx, targetctx, xtnkv__ijdi, auqra__wcg, {})
    lusbi__voyz.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            gzdz__mod = ctypes.pythonapi.PyCell_Get
            gzdz__mod.restype = ctypes.py_object
            gzdz__mod.argtypes = ctypes.py_object,
            inoz__oqo = tuple(gzdz__mod(jds__llvfl) for jds__llvfl in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            inoz__oqo = closure.items
        assert len(code.co_freevars) == len(inoz__oqo)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, inoz__oqo)


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
        zju__xrdq = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array(
            in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (zju__xrdq,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        bxaym__pedys, arr_var = _rm_arg_agg_block(block, pm.typemap)
        fyv__zodr = -1
        for xywa__qfsb, kqh__uelbc in enumerate(bxaym__pedys):
            if isinstance(kqh__uelbc, numba.parfors.parfor.Parfor):
                assert fyv__zodr == -1, 'only one parfor for aggregation function'
                fyv__zodr = xywa__qfsb
        parfor = None
        if fyv__zodr != -1:
            parfor = bxaym__pedys[fyv__zodr]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = bxaym__pedys[:fyv__zodr] + parfor.init_block.body
        eval_nodes = bxaym__pedys[fyv__zodr + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for kqh__uelbc in init_nodes:
            if is_assign(kqh__uelbc) and kqh__uelbc.target.name in redvars:
                ind = redvars.index(kqh__uelbc.target.name)
                reduce_vars[ind] = kqh__uelbc.target
        var_types = [pm.typemap[pdbvh__xsjkv] for pdbvh__xsjkv in redvars]
        jsmog__bex = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        uudm__dnv = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        ptac__cktg = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(ptac__cktg)
        self.all_update_funcs.append(uudm__dnv)
        self.all_combine_funcs.append(jsmog__bex)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        muvh__uvou = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        jqy__zbzu = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        xpnzt__odx = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        ssbm__rceo = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets
            )
        return self.all_vartypes, muvh__uvou, jqy__zbzu, xpnzt__odx, ssbm__rceo


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
    ejkz__jgv = []
    for t, wlsw__zboh in zip(in_col_types, agg_func):
        ejkz__jgv.append((t, wlsw__zboh))
    lvvkp__jms = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    yww__pphbu = GeneralUDFGenerator()
    for in_col_typ, func in ejkz__jgv:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            lvvkp__jms.add_udf(in_col_typ, func)
        except:
            yww__pphbu.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = lvvkp__jms.gen_all_func()
    general_udf_funcs = yww__pphbu.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    ugmx__qtak = compute_use_defs(parfor.loop_body)
    djh__zssce = set()
    for bdup__lsrg in ugmx__qtak.usemap.values():
        djh__zssce |= bdup__lsrg
    hdug__mxp = set()
    for bdup__lsrg in ugmx__qtak.defmap.values():
        hdug__mxp |= bdup__lsrg
    sdyh__gtizg = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    sdyh__gtizg.body = eval_nodes
    xwk__grwmi = compute_use_defs({(0): sdyh__gtizg})
    ixpzx__wlp = xwk__grwmi.usemap[0]
    hhdpe__qvsn = set()
    gqsx__dnm = []
    mebbo__izloh = []
    for kqh__uelbc in reversed(init_nodes):
        hvsw__uiif = {pdbvh__xsjkv.name for pdbvh__xsjkv in kqh__uelbc.
            list_vars()}
        if is_assign(kqh__uelbc):
            pdbvh__xsjkv = kqh__uelbc.target.name
            hvsw__uiif.remove(pdbvh__xsjkv)
            if (pdbvh__xsjkv in djh__zssce and pdbvh__xsjkv not in
                hhdpe__qvsn and pdbvh__xsjkv not in ixpzx__wlp and 
                pdbvh__xsjkv not in hdug__mxp):
                mebbo__izloh.append(kqh__uelbc)
                djh__zssce |= hvsw__uiif
                hdug__mxp.add(pdbvh__xsjkv)
                continue
        hhdpe__qvsn |= hvsw__uiif
        gqsx__dnm.append(kqh__uelbc)
    mebbo__izloh.reverse()
    gqsx__dnm.reverse()
    ziyv__xjjhg = min(parfor.loop_body.keys())
    jvqwf__xbkxx = parfor.loop_body[ziyv__xjjhg]
    jvqwf__xbkxx.body = mebbo__izloh + jvqwf__xbkxx.body
    return gqsx__dnm


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    rrfvs__qeq = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    ckcxu__ckugh = set()
    exh__suplc = []
    for kqh__uelbc in init_nodes:
        if is_assign(kqh__uelbc) and isinstance(kqh__uelbc.value, ir.Global
            ) and isinstance(kqh__uelbc.value.value, pytypes.FunctionType
            ) and kqh__uelbc.value.value in rrfvs__qeq:
            ckcxu__ckugh.add(kqh__uelbc.target.name)
        elif is_call_assign(kqh__uelbc
            ) and kqh__uelbc.value.func.name in ckcxu__ckugh:
            pass
        else:
            exh__suplc.append(kqh__uelbc)
    init_nodes = exh__suplc
    gmw__uhse = types.Tuple(var_types)
    bqbxy__jysnl = lambda : None
    f_ir = compile_to_numba_ir(bqbxy__jysnl, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    wnlca__jnjzf = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    ohe__xbb = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        wnlca__jnjzf, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [ohe__xbb] + block.body
    block.body[-2].value.value = wnlca__jnjzf
    wkasi__hndlx = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        gmw__uhse, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sjae__qumn = numba.core.target_extension.dispatcher_registry[cpu_target](
        bqbxy__jysnl)
    sjae__qumn.add_overload(wkasi__hndlx)
    return sjae__qumn


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    qjt__dfhz = len(update_funcs)
    xuzd__aml = len(in_col_types)
    zecoo__hxygk = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for ueu__rqj in range(qjt__dfhz):
        tlg__zlep = ', '.join(['redvar_arrs[{}][w_ind]'.format(xywa__qfsb) for
            xywa__qfsb in range(redvar_offsets[ueu__rqj], redvar_offsets[
            ueu__rqj + 1])])
        if tlg__zlep:
            zecoo__hxygk += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                .format(tlg__zlep, ueu__rqj, tlg__zlep, 0 if xuzd__aml == 1
                 else ueu__rqj))
    zecoo__hxygk += '  return\n'
    itbzm__srtf = {}
    for xywa__qfsb, wlsw__zboh in enumerate(update_funcs):
        itbzm__srtf['update_vars_{}'.format(xywa__qfsb)] = wlsw__zboh
    sksf__cwzg = {}
    exec(zecoo__hxygk, itbzm__srtf, sksf__cwzg)
    toslm__fmyun = sksf__cwzg['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(toslm__fmyun)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    gwh__dkzhy = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    arg_typs = gwh__dkzhy, gwh__dkzhy, types.intp, types.intp
    axq__imz = len(redvar_offsets) - 1
    zecoo__hxygk = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for ueu__rqj in range(axq__imz):
        tlg__zlep = ', '.join(['redvar_arrs[{}][w_ind]'.format(xywa__qfsb) for
            xywa__qfsb in range(redvar_offsets[ueu__rqj], redvar_offsets[
            ueu__rqj + 1])])
        wtah__pgx = ', '.join(['recv_arrs[{}][i]'.format(xywa__qfsb) for
            xywa__qfsb in range(redvar_offsets[ueu__rqj], redvar_offsets[
            ueu__rqj + 1])])
        if wtah__pgx:
            zecoo__hxygk += '  {} = combine_vars_{}({}, {})\n'.format(tlg__zlep
                , ueu__rqj, tlg__zlep, wtah__pgx)
    zecoo__hxygk += '  return\n'
    itbzm__srtf = {}
    for xywa__qfsb, wlsw__zboh in enumerate(combine_funcs):
        itbzm__srtf['combine_vars_{}'.format(xywa__qfsb)] = wlsw__zboh
    sksf__cwzg = {}
    exec(zecoo__hxygk, itbzm__srtf, sksf__cwzg)
    dpxv__dpfq = sksf__cwzg['combine_all_f']
    f_ir = compile_to_numba_ir(dpxv__dpfq, itbzm__srtf)
    xpnzt__odx = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sjae__qumn = numba.core.target_extension.dispatcher_registry[cpu_target](
        dpxv__dpfq)
    sjae__qumn.add_overload(xpnzt__odx)
    return sjae__qumn


def gen_all_eval_func(eval_funcs, redvar_offsets):
    axq__imz = len(redvar_offsets) - 1
    zecoo__hxygk = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for ueu__rqj in range(axq__imz):
        tlg__zlep = ', '.join(['redvar_arrs[{}][j]'.format(xywa__qfsb) for
            xywa__qfsb in range(redvar_offsets[ueu__rqj], redvar_offsets[
            ueu__rqj + 1])])
        zecoo__hxygk += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
            ueu__rqj, ueu__rqj, tlg__zlep)
    zecoo__hxygk += '  return\n'
    itbzm__srtf = {}
    for xywa__qfsb, wlsw__zboh in enumerate(eval_funcs):
        itbzm__srtf['eval_vars_{}'.format(xywa__qfsb)] = wlsw__zboh
    sksf__cwzg = {}
    exec(zecoo__hxygk, itbzm__srtf, sksf__cwzg)
    zmevq__ceyhg = sksf__cwzg['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(zmevq__ceyhg)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    uwsot__gdmhw = len(var_types)
    eqrf__jqew = [f'in{xywa__qfsb}' for xywa__qfsb in range(uwsot__gdmhw)]
    gmw__uhse = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    oqv__ani = gmw__uhse(0)
    zecoo__hxygk = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        eqrf__jqew))
    sksf__cwzg = {}
    exec(zecoo__hxygk, {'_zero': oqv__ani}, sksf__cwzg)
    gff__zsu = sksf__cwzg['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(gff__zsu, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': oqv__ani}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    cbio__kqjg = []
    for xywa__qfsb, pdbvh__xsjkv in enumerate(reduce_vars):
        cbio__kqjg.append(ir.Assign(block.body[xywa__qfsb].target,
            pdbvh__xsjkv, pdbvh__xsjkv.loc))
        for kpzm__vcq in pdbvh__xsjkv.versioned_names:
            cbio__kqjg.append(ir.Assign(pdbvh__xsjkv, ir.Var(pdbvh__xsjkv.
                scope, kpzm__vcq, pdbvh__xsjkv.loc), pdbvh__xsjkv.loc))
    block.body = block.body[:uwsot__gdmhw] + cbio__kqjg + eval_nodes
    ptac__cktg = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        gmw__uhse, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sjae__qumn = numba.core.target_extension.dispatcher_registry[cpu_target](
        gff__zsu)
    sjae__qumn.add_overload(ptac__cktg)
    return sjae__qumn


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    uwsot__gdmhw = len(redvars)
    tpxot__fhbfb = [f'v{xywa__qfsb}' for xywa__qfsb in range(uwsot__gdmhw)]
    eqrf__jqew = [f'in{xywa__qfsb}' for xywa__qfsb in range(uwsot__gdmhw)]
    zecoo__hxygk = 'def agg_combine({}):\n'.format(', '.join(tpxot__fhbfb +
        eqrf__jqew))
    vdq__dxbj = wrap_parfor_blocks(parfor)
    lmlvb__fgx = find_topo_order(vdq__dxbj)
    lmlvb__fgx = lmlvb__fgx[1:]
    unwrap_parfor_blocks(parfor)
    noly__pfciq = {}
    cvjq__qcvl = []
    for rxri__nqhb in lmlvb__fgx:
        fhycf__odhdk = parfor.loop_body[rxri__nqhb]
        for kqh__uelbc in fhycf__odhdk.body:
            if is_assign(kqh__uelbc) and kqh__uelbc.target.name in redvars:
                fdea__ueym = kqh__uelbc.target.name
                ind = redvars.index(fdea__ueym)
                if ind in cvjq__qcvl:
                    continue
                if len(f_ir._definitions[fdea__ueym]) == 2:
                    var_def = f_ir._definitions[fdea__ueym][0]
                    zecoo__hxygk += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[fdea__ueym][1]
                    zecoo__hxygk += _match_reduce_def(var_def, f_ir, ind)
    zecoo__hxygk += '    return {}'.format(', '.join(['v{}'.format(
        xywa__qfsb) for xywa__qfsb in range(uwsot__gdmhw)]))
    sksf__cwzg = {}
    exec(zecoo__hxygk, {}, sksf__cwzg)
    vgcu__ptv = sksf__cwzg['agg_combine']
    arg_typs = tuple(2 * var_types)
    itbzm__srtf = {'numba': numba, 'bodo': bodo, 'np': np}
    itbzm__srtf.update(noly__pfciq)
    f_ir = compile_to_numba_ir(vgcu__ptv, itbzm__srtf, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    gmw__uhse = pm.typemap[block.body[-1].value.name]
    jsmog__bex = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        gmw__uhse, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sjae__qumn = numba.core.target_extension.dispatcher_registry[cpu_target](
        vgcu__ptv)
    sjae__qumn.add_overload(jsmog__bex)
    return sjae__qumn


def _match_reduce_def(var_def, f_ir, ind):
    zecoo__hxygk = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        zecoo__hxygk = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        vfg__msxaw = guard(find_callname, f_ir, var_def)
        if vfg__msxaw == ('min', 'builtins'):
            zecoo__hxygk = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if vfg__msxaw == ('max', 'builtins'):
            zecoo__hxygk = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return zecoo__hxygk


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    uwsot__gdmhw = len(redvars)
    bku__lso = 1
    in_vars = []
    for xywa__qfsb in range(bku__lso):
        lfrgl__vjak = ir.Var(arr_var.scope, f'$input{xywa__qfsb}', arr_var.loc)
        in_vars.append(lfrgl__vjak)
    pee__vmhu = parfor.loop_nests[0].index_variable
    vwuet__dktt = [0] * uwsot__gdmhw
    for fhycf__odhdk in parfor.loop_body.values():
        kzbd__lks = []
        for kqh__uelbc in fhycf__odhdk.body:
            if is_var_assign(kqh__uelbc
                ) and kqh__uelbc.value.name == pee__vmhu.name:
                continue
            if is_getitem(kqh__uelbc
                ) and kqh__uelbc.value.value.name == arr_var.name:
                kqh__uelbc.value = in_vars[0]
            if is_call_assign(kqh__uelbc) and guard(find_callname, pm.
                func_ir, kqh__uelbc.value) == ('isna',
                'bodo.libs.array_kernels') and kqh__uelbc.value.args[0
                ].name == arr_var.name:
                kqh__uelbc.value = ir.Const(False, kqh__uelbc.target.loc)
            if is_assign(kqh__uelbc) and kqh__uelbc.target.name in redvars:
                ind = redvars.index(kqh__uelbc.target.name)
                vwuet__dktt[ind] = kqh__uelbc.target
            kzbd__lks.append(kqh__uelbc)
        fhycf__odhdk.body = kzbd__lks
    tpxot__fhbfb = ['v{}'.format(xywa__qfsb) for xywa__qfsb in range(
        uwsot__gdmhw)]
    eqrf__jqew = ['in{}'.format(xywa__qfsb) for xywa__qfsb in range(bku__lso)]
    zecoo__hxygk = 'def agg_update({}):\n'.format(', '.join(tpxot__fhbfb +
        eqrf__jqew))
    zecoo__hxygk += '    __update_redvars()\n'
    zecoo__hxygk += '    return {}'.format(', '.join(['v{}'.format(
        xywa__qfsb) for xywa__qfsb in range(uwsot__gdmhw)]))
    sksf__cwzg = {}
    exec(zecoo__hxygk, {}, sksf__cwzg)
    mwdnw__bik = sksf__cwzg['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * bku__lso)
    f_ir = compile_to_numba_ir(mwdnw__bik, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    crf__ofsi = f_ir.blocks.popitem()[1].body
    gmw__uhse = pm.typemap[crf__ofsi[-1].value.name]
    vdq__dxbj = wrap_parfor_blocks(parfor)
    lmlvb__fgx = find_topo_order(vdq__dxbj)
    lmlvb__fgx = lmlvb__fgx[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    jvqwf__xbkxx = f_ir.blocks[lmlvb__fgx[0]]
    zorqb__xfw = f_ir.blocks[lmlvb__fgx[-1]]
    pjnt__tvle = crf__ofsi[:uwsot__gdmhw + bku__lso]
    if uwsot__gdmhw > 1:
        egdc__eob = crf__ofsi[-3:]
        assert is_assign(egdc__eob[0]) and isinstance(egdc__eob[0].value,
            ir.Expr) and egdc__eob[0].value.op == 'build_tuple'
    else:
        egdc__eob = crf__ofsi[-2:]
    for xywa__qfsb in range(uwsot__gdmhw):
        onya__vkus = crf__ofsi[xywa__qfsb].target
        mtqhe__juaz = ir.Assign(onya__vkus, vwuet__dktt[xywa__qfsb],
            onya__vkus.loc)
        pjnt__tvle.append(mtqhe__juaz)
    for xywa__qfsb in range(uwsot__gdmhw, uwsot__gdmhw + bku__lso):
        onya__vkus = crf__ofsi[xywa__qfsb].target
        mtqhe__juaz = ir.Assign(onya__vkus, in_vars[xywa__qfsb -
            uwsot__gdmhw], onya__vkus.loc)
        pjnt__tvle.append(mtqhe__juaz)
    jvqwf__xbkxx.body = pjnt__tvle + jvqwf__xbkxx.body
    yhw__zzy = []
    for xywa__qfsb in range(uwsot__gdmhw):
        onya__vkus = crf__ofsi[xywa__qfsb].target
        mtqhe__juaz = ir.Assign(vwuet__dktt[xywa__qfsb], onya__vkus,
            onya__vkus.loc)
        yhw__zzy.append(mtqhe__juaz)
    zorqb__xfw.body += yhw__zzy + egdc__eob
    grmp__ujaj = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        gmw__uhse, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    sjae__qumn = numba.core.target_extension.dispatcher_registry[cpu_target](
        mwdnw__bik)
    sjae__qumn.add_overload(grmp__ujaj)
    return sjae__qumn


def _rm_arg_agg_block(block, typemap):
    bxaym__pedys = []
    arr_var = None
    for xywa__qfsb, kqh__uelbc in enumerate(block.body):
        if is_assign(kqh__uelbc) and isinstance(kqh__uelbc.value, ir.Arg):
            arr_var = kqh__uelbc.target
            authf__hkf = typemap[arr_var.name]
            if not isinstance(authf__hkf, types.ArrayCompatible):
                bxaym__pedys += block.body[xywa__qfsb + 1:]
                break
            pjquw__szy = block.body[xywa__qfsb + 1]
            assert is_assign(pjquw__szy) and isinstance(pjquw__szy.value,
                ir.Expr
                ) and pjquw__szy.value.op == 'getattr' and pjquw__szy.value.attr == 'shape' and pjquw__szy.value.value.name == arr_var.name
            uje__wnuck = pjquw__szy.target
            fkb__zdp = block.body[xywa__qfsb + 2]
            assert is_assign(fkb__zdp) and isinstance(fkb__zdp.value, ir.Expr
                ) and fkb__zdp.value.op == 'static_getitem' and fkb__zdp.value.value.name == uje__wnuck.name
            bxaym__pedys += block.body[xywa__qfsb + 3:]
            break
        bxaym__pedys.append(kqh__uelbc)
    return bxaym__pedys, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    vdq__dxbj = wrap_parfor_blocks(parfor)
    lmlvb__fgx = find_topo_order(vdq__dxbj)
    lmlvb__fgx = lmlvb__fgx[1:]
    unwrap_parfor_blocks(parfor)
    for rxri__nqhb in reversed(lmlvb__fgx):
        for kqh__uelbc in reversed(parfor.loop_body[rxri__nqhb].body):
            if isinstance(kqh__uelbc, ir.Assign) and (kqh__uelbc.target.
                name in parfor_params or kqh__uelbc.target.name in var_to_param
                ):
                zcbgv__ldw = kqh__uelbc.target.name
                rhs = kqh__uelbc.value
                yjouw__ixmbf = (zcbgv__ldw if zcbgv__ldw in parfor_params else
                    var_to_param[zcbgv__ldw])
                sbf__dssvk = []
                if isinstance(rhs, ir.Var):
                    sbf__dssvk = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    sbf__dssvk = [pdbvh__xsjkv.name for pdbvh__xsjkv in
                        kqh__uelbc.value.list_vars()]
                param_uses[yjouw__ixmbf].extend(sbf__dssvk)
                for pdbvh__xsjkv in sbf__dssvk:
                    var_to_param[pdbvh__xsjkv] = yjouw__ixmbf
            if isinstance(kqh__uelbc, Parfor):
                get_parfor_reductions(kqh__uelbc, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for evnau__dgl, sbf__dssvk in param_uses.items():
        if evnau__dgl in sbf__dssvk and evnau__dgl not in reduce_varnames:
            reduce_varnames.append(evnau__dgl)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
