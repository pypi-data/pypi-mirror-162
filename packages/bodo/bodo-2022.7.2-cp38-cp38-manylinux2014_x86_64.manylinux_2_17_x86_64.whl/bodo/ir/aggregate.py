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
        lnfph__tzt = func.signature
        if lnfph__tzt == types.none(types.voidptr):
            cbody__zntxo = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer()])
            scq__geng = cgutils.get_or_insert_function(builder.module,
                cbody__zntxo, sym._literal_value)
            builder.call(scq__geng, [context.get_constant_null(lnfph__tzt.
                args[0])])
        elif lnfph__tzt == types.none(types.int64, types.voidptr, types.voidptr
            ):
            cbody__zntxo = lir.FunctionType(lir.VoidType(), [lir.IntType(64
                ), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            scq__geng = cgutils.get_or_insert_function(builder.module,
                cbody__zntxo, sym._literal_value)
            builder.call(scq__geng, [context.get_constant(types.int64, 0),
                context.get_constant_null(lnfph__tzt.args[1]), context.
                get_constant_null(lnfph__tzt.args[2])])
        else:
            cbody__zntxo = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)
                .as_pointer()])
            scq__geng = cgutils.get_or_insert_function(builder.module,
                cbody__zntxo, sym._literal_value)
            builder.call(scq__geng, [context.get_constant_null(lnfph__tzt.
                args[0]), context.get_constant_null(lnfph__tzt.args[1]),
                context.get_constant_null(lnfph__tzt.args[2])])
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
        jlh__maw = True
        hkknt__hfrme = 1
        kjo__iujo = -1
        if isinstance(rhs, ir.Expr):
            for liy__wnlen in rhs.kws:
                if func_name in list_cumulative:
                    if liy__wnlen[0] == 'skipna':
                        jlh__maw = guard(find_const, func_ir, liy__wnlen[1])
                        if not isinstance(jlh__maw, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if liy__wnlen[0] == 'dropna':
                        jlh__maw = guard(find_const, func_ir, liy__wnlen[1])
                        if not isinstance(jlh__maw, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            hkknt__hfrme = get_call_expr_arg('shift', rhs.args, dict(rhs.
                kws), 0, 'periods', hkknt__hfrme)
            hkknt__hfrme = guard(find_const, func_ir, hkknt__hfrme)
        if func_name == 'head':
            kjo__iujo = get_call_expr_arg('head', rhs.args, dict(rhs.kws), 
                0, 'n', 5)
            if not isinstance(kjo__iujo, int):
                kjo__iujo = guard(find_const, func_ir, kjo__iujo)
            if kjo__iujo < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = jlh__maw
        func.periods = hkknt__hfrme
        func.head_n = kjo__iujo
        if func_name == 'transform':
            kws = dict(rhs.kws)
            zurht__jxvrt = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            ujlkt__kvadb = typemap[zurht__jxvrt.name]
            ywz__fmqdo = None
            if isinstance(ujlkt__kvadb, str):
                ywz__fmqdo = ujlkt__kvadb
            elif is_overload_constant_str(ujlkt__kvadb):
                ywz__fmqdo = get_overload_const_str(ujlkt__kvadb)
            elif bodo.utils.typing.is_builtin_function(ujlkt__kvadb):
                ywz__fmqdo = bodo.utils.typing.get_builtin_function_name(
                    ujlkt__kvadb)
            if ywz__fmqdo not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {ywz__fmqdo}')
            func.transform_func = supported_agg_funcs.index(ywz__fmqdo)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    zurht__jxvrt = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if zurht__jxvrt == '':
        ujlkt__kvadb = types.none
    else:
        ujlkt__kvadb = typemap[zurht__jxvrt.name]
    if is_overload_constant_dict(ujlkt__kvadb):
        rbv__ras = get_overload_constant_dict(ujlkt__kvadb)
        hjtap__nbw = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in rbv__ras.values()]
        return hjtap__nbw
    if ujlkt__kvadb == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(ujlkt__kvadb, types.BaseTuple) or is_overload_constant_list(
        ujlkt__kvadb):
        hjtap__nbw = []
        giqfp__wxzis = 0
        if is_overload_constant_list(ujlkt__kvadb):
            jzvft__dijmg = get_overload_const_list(ujlkt__kvadb)
        else:
            jzvft__dijmg = ujlkt__kvadb.types
        for t in jzvft__dijmg:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                hjtap__nbw.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(jzvft__dijmg) > 1:
                    func.fname = '<lambda_' + str(giqfp__wxzis) + '>'
                    giqfp__wxzis += 1
                hjtap__nbw.append(func)
        return [hjtap__nbw]
    if is_overload_constant_str(ujlkt__kvadb):
        func_name = get_overload_const_str(ujlkt__kvadb)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(ujlkt__kvadb):
        func_name = bodo.utils.typing.get_builtin_function_name(ujlkt__kvadb)
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
        giqfp__wxzis = 0
        vgo__momuv = []
        for dpxt__sehv in f_val:
            func = get_agg_func_udf(func_ir, dpxt__sehv, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{giqfp__wxzis}>'
                giqfp__wxzis += 1
            vgo__momuv.append(func)
        return vgo__momuv
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
    ywz__fmqdo = code.co_name
    return ywz__fmqdo


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
            qqwa__tegib = types.DType(args[0])
            return signature(qqwa__tegib, *args)


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
        return [fxdc__otd for fxdc__otd in self.in_vars if fxdc__otd is not
            None]

    def get_live_out_vars(self):
        return [fxdc__otd for fxdc__otd in self.out_vars if fxdc__otd is not
            None]

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
        vaqn__zntv = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        puzl__afsy = list(get_index_data_arr_types(self.out_type.index))
        return vaqn__zntv + puzl__afsy

    def update_dead_col_info(self):
        for sjb__wqn in self.dead_out_inds:
            self.gb_info_out.pop(sjb__wqn, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for ufnp__bgg, hmo__bkd in self.gb_info_in.copy().items():
            cogcm__nvrz = []
            for dpxt__sehv, wnmdp__mwxbd in hmo__bkd:
                if wnmdp__mwxbd not in self.dead_out_inds:
                    cogcm__nvrz.append((dpxt__sehv, wnmdp__mwxbd))
            if not cogcm__nvrz:
                if ufnp__bgg is not None and ufnp__bgg not in self.in_key_inds:
                    self.dead_in_inds.add(ufnp__bgg)
                self.gb_info_in.pop(ufnp__bgg)
            else:
                self.gb_info_in[ufnp__bgg] = cogcm__nvrz
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for oenf__bhqaq in range(1, len(self.in_vars)):
                sjb__wqn = self.n_in_table_arrays + oenf__bhqaq - 1
                if sjb__wqn in self.dead_in_inds:
                    self.in_vars[oenf__bhqaq] = None
        else:
            for oenf__bhqaq in range(len(self.in_vars)):
                if oenf__bhqaq in self.dead_in_inds:
                    self.in_vars[oenf__bhqaq] = None

    def __repr__(self):
        szdmj__jehl = ', '.join(fxdc__otd.name for fxdc__otd in self.
            get_live_in_vars())
        ntazv__pxdy = f'{self.df_in}{{{szdmj__jehl}}}'
        roar__vyol = ', '.join(fxdc__otd.name for fxdc__otd in self.
            get_live_out_vars())
        oteou__xnozc = f'{self.df_out}{{{roar__vyol}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {ntazv__pxdy} {oteou__xnozc}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({fxdc__otd.name for fxdc__otd in aggregate_node.
        get_live_in_vars()})
    def_set.update({fxdc__otd.name for fxdc__otd in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    tqykp__ccxj = agg_node.out_vars[0]
    if tqykp__ccxj is not None and tqykp__ccxj.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            mvnlc__ewhf = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(mvnlc__ewhf)
        else:
            agg_node.dead_out_inds.add(0)
    for oenf__bhqaq in range(1, len(agg_node.out_vars)):
        fxdc__otd = agg_node.out_vars[oenf__bhqaq]
        if fxdc__otd is not None and fxdc__otd.name not in lives:
            agg_node.out_vars[oenf__bhqaq] = None
            sjb__wqn = agg_node.n_out_table_arrays + oenf__bhqaq - 1
            agg_node.dead_out_inds.add(sjb__wqn)
    if all(fxdc__otd is None for fxdc__otd in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    pafz__qolio = {fxdc__otd.name for fxdc__otd in aggregate_node.
        get_live_out_vars()}
    return set(), pafz__qolio


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for oenf__bhqaq in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[oenf__bhqaq] is not None:
            aggregate_node.in_vars[oenf__bhqaq] = replace_vars_inner(
                aggregate_node.in_vars[oenf__bhqaq], var_dict)
    for oenf__bhqaq in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[oenf__bhqaq] is not None:
            aggregate_node.out_vars[oenf__bhqaq] = replace_vars_inner(
                aggregate_node.out_vars[oenf__bhqaq], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for oenf__bhqaq in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[oenf__bhqaq] is not None:
            aggregate_node.in_vars[oenf__bhqaq] = visit_vars_inner(
                aggregate_node.in_vars[oenf__bhqaq], callback, cbdata)
    for oenf__bhqaq in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[oenf__bhqaq] is not None:
            aggregate_node.out_vars[oenf__bhqaq] = visit_vars_inner(
                aggregate_node.out_vars[oenf__bhqaq], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    dyml__cob = []
    for enq__dwg in aggregate_node.get_live_in_vars():
        gmty__aqv = equiv_set.get_shape(enq__dwg)
        if gmty__aqv is not None:
            dyml__cob.append(gmty__aqv[0])
    if len(dyml__cob) > 1:
        equiv_set.insert_equiv(*dyml__cob)
    sun__imyt = []
    dyml__cob = []
    for enq__dwg in aggregate_node.get_live_out_vars():
        trt__ghg = typemap[enq__dwg.name]
        tfkc__tdszb = array_analysis._gen_shape_call(equiv_set, enq__dwg,
            trt__ghg.ndim, None, sun__imyt)
        equiv_set.insert_equiv(enq__dwg, tfkc__tdszb)
        dyml__cob.append(tfkc__tdszb[0])
        equiv_set.define(enq__dwg, set())
    if len(dyml__cob) > 1:
        equiv_set.insert_equiv(*dyml__cob)
    return [], sun__imyt


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    emvxe__yth = aggregate_node.get_live_in_vars()
    tfjwc__kotij = aggregate_node.get_live_out_vars()
    bsep__skzkm = Distribution.OneD
    for enq__dwg in emvxe__yth:
        bsep__skzkm = Distribution(min(bsep__skzkm.value, array_dists[
            enq__dwg.name].value))
    zdagg__asrc = Distribution(min(bsep__skzkm.value, Distribution.OneD_Var
        .value))
    for enq__dwg in tfjwc__kotij:
        if enq__dwg.name in array_dists:
            zdagg__asrc = Distribution(min(zdagg__asrc.value, array_dists[
                enq__dwg.name].value))
    if zdagg__asrc != Distribution.OneD_Var:
        bsep__skzkm = zdagg__asrc
    for enq__dwg in emvxe__yth:
        array_dists[enq__dwg.name] = bsep__skzkm
    for enq__dwg in tfjwc__kotij:
        array_dists[enq__dwg.name] = zdagg__asrc


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for enq__dwg in agg_node.get_live_out_vars():
        definitions[enq__dwg.name].append(agg_node)
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
    ypdfc__rpd = agg_node.get_live_in_vars()
    txuv__dwa = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for fxdc__otd in (ypdfc__rpd + txuv__dwa):
            if array_dists[fxdc__otd.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                fxdc__otd.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    hjtap__nbw = []
    func_out_types = []
    for wnmdp__mwxbd, (ufnp__bgg, func) in agg_node.gb_info_out.items():
        if ufnp__bgg is not None:
            t = agg_node.in_col_types[ufnp__bgg]
            in_col_typs.append(t)
        hjtap__nbw.append(func)
        func_out_types.append(out_col_typs[wnmdp__mwxbd])
    uks__zwkan = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for oenf__bhqaq, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            uks__zwkan.update({f'in_cat_dtype_{oenf__bhqaq}': in_col_typ})
    for oenf__bhqaq, mnddf__ozsx in enumerate(out_col_typs):
        if isinstance(mnddf__ozsx, bodo.CategoricalArrayType):
            uks__zwkan.update({f'out_cat_dtype_{oenf__bhqaq}': mnddf__ozsx})
    udf_func_struct = get_udf_func_struct(hjtap__nbw, in_col_typs,
        typingctx, targetctx)
    out_var_types = [(typemap[fxdc__otd.name] if fxdc__otd is not None else
        types.none) for fxdc__otd in agg_node.out_vars]
    depe__xvu, regx__gxm = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    uks__zwkan.update(regx__gxm)
    uks__zwkan.update({'pd': pd, 'pre_alloc_string_array':
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
            uks__zwkan.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            uks__zwkan.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    thf__uxmwd = {}
    exec(depe__xvu, {}, thf__uxmwd)
    tjapw__oqg = thf__uxmwd['agg_top']
    evsrh__svda = compile_to_numba_ir(tjapw__oqg, uks__zwkan, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[fxdc__otd.
        name] for fxdc__otd in ypdfc__rpd), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(evsrh__svda, ypdfc__rpd)
    eoxnj__yaly = evsrh__svda.body[-2].value.value
    apwym__dhmou = evsrh__svda.body[:-2]
    for oenf__bhqaq, fxdc__otd in enumerate(txuv__dwa):
        gen_getitem(fxdc__otd, eoxnj__yaly, oenf__bhqaq, calltypes,
            apwym__dhmou)
    return apwym__dhmou


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        rcbh__isyc = IntDtype(t.dtype).name
        assert rcbh__isyc.endswith('Dtype()')
        rcbh__isyc = rcbh__isyc[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{rcbh__isyc}'))"
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
        iuj__qxzb = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {iuj__qxzb}_cat_dtype_{colnum})')
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
    lycei__ohp = udf_func_struct.var_typs
    vagwg__iom = len(lycei__ohp)
    depe__xvu = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    depe__xvu += '    if is_null_pointer(in_table):\n'
    depe__xvu += '        return\n'
    depe__xvu += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lycei__ohp]), 
        ',' if len(lycei__ohp) == 1 else '')
    uybvx__nmk = n_keys
    zcwgc__zincw = []
    redvar_offsets = []
    fycp__oot = []
    if do_combine:
        for oenf__bhqaq, dpxt__sehv in enumerate(allfuncs):
            if dpxt__sehv.ftype != 'udf':
                uybvx__nmk += dpxt__sehv.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(uybvx__nmk, uybvx__nmk +
                    dpxt__sehv.n_redvars))
                uybvx__nmk += dpxt__sehv.n_redvars
                fycp__oot.append(data_in_typs_[func_idx_to_in_col[oenf__bhqaq]]
                    )
                zcwgc__zincw.append(func_idx_to_in_col[oenf__bhqaq] + n_keys)
    else:
        for oenf__bhqaq, dpxt__sehv in enumerate(allfuncs):
            if dpxt__sehv.ftype != 'udf':
                uybvx__nmk += dpxt__sehv.ncols_post_shuffle
            else:
                redvar_offsets += list(range(uybvx__nmk + 1, uybvx__nmk + 1 +
                    dpxt__sehv.n_redvars))
                uybvx__nmk += dpxt__sehv.n_redvars + 1
                fycp__oot.append(data_in_typs_[func_idx_to_in_col[oenf__bhqaq]]
                    )
                zcwgc__zincw.append(func_idx_to_in_col[oenf__bhqaq] + n_keys)
    assert len(redvar_offsets) == vagwg__iom
    zuyy__svq = len(fycp__oot)
    zkiyg__qlbyu = []
    for oenf__bhqaq, t in enumerate(fycp__oot):
        zkiyg__qlbyu.append(_gen_dummy_alloc(t, oenf__bhqaq, True))
    depe__xvu += '    data_in_dummy = ({}{})\n'.format(','.join(
        zkiyg__qlbyu), ',' if len(fycp__oot) == 1 else '')
    depe__xvu += """
    # initialize redvar cols
"""
    depe__xvu += '    init_vals = __init_func()\n'
    for oenf__bhqaq in range(vagwg__iom):
        depe__xvu += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(oenf__bhqaq, redvar_offsets[oenf__bhqaq], oenf__bhqaq))
        depe__xvu += '    incref(redvar_arr_{})\n'.format(oenf__bhqaq)
        depe__xvu += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            oenf__bhqaq, oenf__bhqaq)
    depe__xvu += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(oenf__bhqaq) for oenf__bhqaq in range(vagwg__iom)]), ',' if 
        vagwg__iom == 1 else '')
    depe__xvu += '\n'
    for oenf__bhqaq in range(zuyy__svq):
        depe__xvu += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(oenf__bhqaq, zcwgc__zincw[oenf__bhqaq], oenf__bhqaq))
        depe__xvu += '    incref(data_in_{})\n'.format(oenf__bhqaq)
    depe__xvu += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(oenf__bhqaq) for oenf__bhqaq in range(zuyy__svq)]), ',' if 
        zuyy__svq == 1 else '')
    depe__xvu += '\n'
    depe__xvu += '    for i in range(len(data_in_0)):\n'
    depe__xvu += '        w_ind = row_to_group[i]\n'
    depe__xvu += '        if w_ind != -1:\n'
    depe__xvu += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    thf__uxmwd = {}
    exec(depe__xvu, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, thf__uxmwd)
    return thf__uxmwd['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    lycei__ohp = udf_func_struct.var_typs
    vagwg__iom = len(lycei__ohp)
    depe__xvu = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    depe__xvu += '    if is_null_pointer(in_table):\n'
    depe__xvu += '        return\n'
    depe__xvu += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lycei__ohp]), 
        ',' if len(lycei__ohp) == 1 else '')
    mnlo__ueyfp = n_keys
    cvm__yyszv = n_keys
    kvsm__diavp = []
    vaqxb__lzr = []
    for dpxt__sehv in allfuncs:
        if dpxt__sehv.ftype != 'udf':
            mnlo__ueyfp += dpxt__sehv.ncols_pre_shuffle
            cvm__yyszv += dpxt__sehv.ncols_post_shuffle
        else:
            kvsm__diavp += list(range(mnlo__ueyfp, mnlo__ueyfp + dpxt__sehv
                .n_redvars))
            vaqxb__lzr += list(range(cvm__yyszv + 1, cvm__yyszv + 1 +
                dpxt__sehv.n_redvars))
            mnlo__ueyfp += dpxt__sehv.n_redvars
            cvm__yyszv += 1 + dpxt__sehv.n_redvars
    assert len(kvsm__diavp) == vagwg__iom
    depe__xvu += """
    # initialize redvar cols
"""
    depe__xvu += '    init_vals = __init_func()\n'
    for oenf__bhqaq in range(vagwg__iom):
        depe__xvu += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(oenf__bhqaq, vaqxb__lzr[oenf__bhqaq], oenf__bhqaq))
        depe__xvu += '    incref(redvar_arr_{})\n'.format(oenf__bhqaq)
        depe__xvu += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            oenf__bhqaq, oenf__bhqaq)
    depe__xvu += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(oenf__bhqaq) for oenf__bhqaq in range(vagwg__iom)]), ',' if 
        vagwg__iom == 1 else '')
    depe__xvu += '\n'
    for oenf__bhqaq in range(vagwg__iom):
        depe__xvu += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(oenf__bhqaq, kvsm__diavp[oenf__bhqaq], oenf__bhqaq))
        depe__xvu += '    incref(recv_redvar_arr_{})\n'.format(oenf__bhqaq)
    depe__xvu += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(oenf__bhqaq) for oenf__bhqaq in range(
        vagwg__iom)]), ',' if vagwg__iom == 1 else '')
    depe__xvu += '\n'
    if vagwg__iom:
        depe__xvu += '    for i in range(len(recv_redvar_arr_0)):\n'
        depe__xvu += '        w_ind = row_to_group[i]\n'
        depe__xvu += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    thf__uxmwd = {}
    exec(depe__xvu, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, thf__uxmwd)
    return thf__uxmwd['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    lycei__ohp = udf_func_struct.var_typs
    vagwg__iom = len(lycei__ohp)
    uybvx__nmk = n_keys
    redvar_offsets = []
    nky__uxbhp = []
    efqwn__rcitm = []
    for oenf__bhqaq, dpxt__sehv in enumerate(allfuncs):
        if dpxt__sehv.ftype != 'udf':
            uybvx__nmk += dpxt__sehv.ncols_post_shuffle
        else:
            nky__uxbhp.append(uybvx__nmk)
            redvar_offsets += list(range(uybvx__nmk + 1, uybvx__nmk + 1 +
                dpxt__sehv.n_redvars))
            uybvx__nmk += 1 + dpxt__sehv.n_redvars
            efqwn__rcitm.append(out_data_typs_[oenf__bhqaq])
    assert len(redvar_offsets) == vagwg__iom
    zuyy__svq = len(efqwn__rcitm)
    depe__xvu = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    depe__xvu += '    if is_null_pointer(table):\n'
    depe__xvu += '        return\n'
    depe__xvu += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lycei__ohp]), 
        ',' if len(lycei__ohp) == 1 else '')
    depe__xvu += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        efqwn__rcitm]), ',' if len(efqwn__rcitm) == 1 else '')
    for oenf__bhqaq in range(vagwg__iom):
        depe__xvu += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(oenf__bhqaq, redvar_offsets[oenf__bhqaq], oenf__bhqaq))
        depe__xvu += '    incref(redvar_arr_{})\n'.format(oenf__bhqaq)
    depe__xvu += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(oenf__bhqaq) for oenf__bhqaq in range(vagwg__iom)]), ',' if 
        vagwg__iom == 1 else '')
    depe__xvu += '\n'
    for oenf__bhqaq in range(zuyy__svq):
        depe__xvu += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(oenf__bhqaq, nky__uxbhp[oenf__bhqaq], oenf__bhqaq))
        depe__xvu += '    incref(data_out_{})\n'.format(oenf__bhqaq)
    depe__xvu += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(oenf__bhqaq) for oenf__bhqaq in range(zuyy__svq)]), ',' if 
        zuyy__svq == 1 else '')
    depe__xvu += '\n'
    depe__xvu += '    for i in range(len(data_out_0)):\n'
    depe__xvu += '        __eval_res(redvars, data_out, i)\n'
    thf__uxmwd = {}
    exec(depe__xvu, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, thf__uxmwd)
    return thf__uxmwd['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    uybvx__nmk = n_keys
    leutv__efzzh = []
    for oenf__bhqaq, dpxt__sehv in enumerate(allfuncs):
        if dpxt__sehv.ftype == 'gen_udf':
            leutv__efzzh.append(uybvx__nmk)
            uybvx__nmk += 1
        elif dpxt__sehv.ftype != 'udf':
            uybvx__nmk += dpxt__sehv.ncols_post_shuffle
        else:
            uybvx__nmk += dpxt__sehv.n_redvars + 1
    depe__xvu = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    depe__xvu += '    if num_groups == 0:\n'
    depe__xvu += '        return\n'
    for oenf__bhqaq, func in enumerate(udf_func_struct.general_udf_funcs):
        depe__xvu += '    # col {}\n'.format(oenf__bhqaq)
        depe__xvu += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(leutv__efzzh[oenf__bhqaq], oenf__bhqaq))
        depe__xvu += '    incref(out_col)\n'
        depe__xvu += '    for j in range(num_groups):\n'
        depe__xvu += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(oenf__bhqaq, oenf__bhqaq))
        depe__xvu += '        incref(in_col)\n'
        depe__xvu += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(oenf__bhqaq))
    uks__zwkan = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    kped__qtgsb = 0
    for oenf__bhqaq, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[kped__qtgsb]
        uks__zwkan['func_{}'.format(kped__qtgsb)] = func
        uks__zwkan['in_col_{}_typ'.format(kped__qtgsb)] = in_col_typs[
            func_idx_to_in_col[oenf__bhqaq]]
        uks__zwkan['out_col_{}_typ'.format(kped__qtgsb)] = out_col_typs[
            oenf__bhqaq]
        kped__qtgsb += 1
    thf__uxmwd = {}
    exec(depe__xvu, uks__zwkan, thf__uxmwd)
    dpxt__sehv = thf__uxmwd['bodo_gb_apply_general_udfs{}'.format(label_suffix)
        ]
    xdc__gdn = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(xdc__gdn, nopython=True)(dpxt__sehv)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    vosc__mowka = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        xzkm__wcky = []
        if agg_node.in_vars[0] is not None:
            xzkm__wcky.append('arg0')
        for oenf__bhqaq in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if oenf__bhqaq not in agg_node.dead_in_inds:
                xzkm__wcky.append(f'arg{oenf__bhqaq}')
    else:
        xzkm__wcky = [f'arg{oenf__bhqaq}' for oenf__bhqaq, fxdc__otd in
            enumerate(agg_node.in_vars) if fxdc__otd is not None]
    depe__xvu = f"def agg_top({', '.join(xzkm__wcky)}):\n"
    rreqi__naa = []
    if agg_node.is_in_table_format:
        rreqi__naa = agg_node.in_key_inds + [ufnp__bgg for ufnp__bgg,
            hfl__alh in agg_node.gb_info_out.values() if ufnp__bgg is not None]
        if agg_node.input_has_index:
            rreqi__naa.append(agg_node.n_in_cols - 1)
        cra__oofzw = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        ksgf__actt = []
        for oenf__bhqaq in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if oenf__bhqaq in agg_node.dead_in_inds:
                ksgf__actt.append('None')
            else:
                ksgf__actt.append(f'arg{oenf__bhqaq}')
        uroyq__gncy = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        depe__xvu += f"""    table = py_data_to_cpp_table({uroyq__gncy}, ({', '.join(ksgf__actt)}{cra__oofzw}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        uyu__ulq = [f'arg{oenf__bhqaq}' for oenf__bhqaq in agg_node.in_key_inds
            ]
        mtq__njl = [f'arg{ufnp__bgg}' for ufnp__bgg, hfl__alh in agg_node.
            gb_info_out.values() if ufnp__bgg is not None]
        biu__cdrf = uyu__ulq + mtq__njl
        if agg_node.input_has_index:
            biu__cdrf.append(f'arg{len(agg_node.in_vars) - 1}')
        depe__xvu += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({ixx__ogk})' for ixx__ogk in biu__cdrf))
        depe__xvu += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    bjp__vfkly = []
    func_idx_to_in_col = []
    dihy__yrc = []
    jlh__maw = False
    aoc__xkrka = 1
    kjo__iujo = -1
    qgwml__jxdlk = 0
    ssxed__hiz = 0
    hjtap__nbw = [func for hfl__alh, func in agg_node.gb_info_out.values()]
    for ltavr__jzc, func in enumerate(hjtap__nbw):
        bjp__vfkly.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            qgwml__jxdlk += 1
        if hasattr(func, 'skipdropna'):
            jlh__maw = func.skipdropna
        if func.ftype == 'shift':
            aoc__xkrka = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            ssxed__hiz = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            kjo__iujo = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(ltavr__jzc)
        if func.ftype == 'udf':
            dihy__yrc.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            dihy__yrc.append(0)
            do_combine = False
    bjp__vfkly.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if qgwml__jxdlk > 0:
        if qgwml__jxdlk != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    fbcq__deche = []
    if udf_func_struct is not None:
        hktra__wah = next_label()
        if udf_func_struct.regular_udfs:
            xdc__gdn = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            ckhq__ujx = numba.cfunc(xdc__gdn, nopython=True)(gen_update_cb(
                udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, hktra__wah))
            hzo__fxzn = numba.cfunc(xdc__gdn, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, hktra__wah))
            tpe__lkpi = numba.cfunc('void(voidptr)', nopython=True)(gen_eval_cb
                (udf_func_struct, allfuncs, n_keys, func_out_types, hktra__wah)
                )
            udf_func_struct.set_regular_cfuncs(ckhq__ujx, hzo__fxzn, tpe__lkpi)
            for axu__lsz in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[axu__lsz.native_name] = axu__lsz
                gb_agg_cfunc_addr[axu__lsz.native_name] = axu__lsz.address
        if udf_func_struct.general_udfs:
            bzej__drvv = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, func_out_types, func_idx_to_in_col,
                hktra__wah)
            udf_func_struct.set_general_cfunc(bzej__drvv)
        lycei__ohp = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        gdos__nxnfx = 0
        oenf__bhqaq = 0
        for zlqh__zcl, dpxt__sehv in zip(agg_node.gb_info_out.keys(), allfuncs
            ):
            if dpxt__sehv.ftype in ('udf', 'gen_udf'):
                fbcq__deche.append(out_col_typs[zlqh__zcl])
                for zrls__hklno in range(gdos__nxnfx, gdos__nxnfx +
                    dihy__yrc[oenf__bhqaq]):
                    fbcq__deche.append(dtype_to_array_type(lycei__ohp[
                        zrls__hklno]))
                gdos__nxnfx += dihy__yrc[oenf__bhqaq]
                oenf__bhqaq += 1
        depe__xvu += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{oenf__bhqaq}' for oenf__bhqaq in range(len(fbcq__deche)))}{',' if len(fbcq__deche) == 1 else ''}))
"""
        depe__xvu += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(fbcq__deche)})
"""
        if udf_func_struct.regular_udfs:
            depe__xvu += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{ckhq__ujx.native_name}')\n"
                )
            depe__xvu += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{hzo__fxzn.native_name}')\n"
                )
            depe__xvu += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{tpe__lkpi.native_name}')\n"
                )
            depe__xvu += (
                f"    cpp_cb_update_addr = get_agg_udf_addr('{ckhq__ujx.native_name}')\n"
                )
            depe__xvu += (
                f"    cpp_cb_combine_addr = get_agg_udf_addr('{hzo__fxzn.native_name}')\n"
                )
            depe__xvu += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{tpe__lkpi.native_name}')\n"
                )
        else:
            depe__xvu += '    cpp_cb_update_addr = 0\n'
            depe__xvu += '    cpp_cb_combine_addr = 0\n'
            depe__xvu += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            axu__lsz = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[axu__lsz.native_name] = axu__lsz
            gb_agg_cfunc_addr[axu__lsz.native_name] = axu__lsz.address
            depe__xvu += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{axu__lsz.native_name}')\n"
                )
            depe__xvu += (
                f"    cpp_cb_general_addr = get_agg_udf_addr('{axu__lsz.native_name}')\n"
                )
        else:
            depe__xvu += '    cpp_cb_general_addr = 0\n'
    else:
        depe__xvu += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        depe__xvu += '    cpp_cb_update_addr = 0\n'
        depe__xvu += '    cpp_cb_combine_addr = 0\n'
        depe__xvu += '    cpp_cb_eval_addr = 0\n'
        depe__xvu += '    cpp_cb_general_addr = 0\n'
    depe__xvu += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(dpxt__sehv.ftype)) for
        dpxt__sehv in allfuncs] + ['0']))
    depe__xvu += (
        f'    func_offsets = np.array({str(bjp__vfkly)}, dtype=np.int32)\n')
    if len(dihy__yrc) > 0:
        depe__xvu += (
            f'    udf_ncols = np.array({str(dihy__yrc)}, dtype=np.int32)\n')
    else:
        depe__xvu += '    udf_ncols = np.array([0], np.int32)\n'
    depe__xvu += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    zooq__zgvoy = (agg_node._num_shuffle_keys if agg_node._num_shuffle_keys !=
        -1 else n_keys)
    depe__xvu += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {jlh__maw}, {aoc__xkrka}, {ssxed__hiz}, {kjo__iujo}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes, {zooq__zgvoy})
"""
    wdesc__omp = []
    pkqc__xrqdm = 0
    if agg_node.return_key:
        ecsv__qmio = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for oenf__bhqaq in range(n_keys):
            sjb__wqn = ecsv__qmio + oenf__bhqaq
            wdesc__omp.append(sjb__wqn if sjb__wqn not in agg_node.
                dead_out_inds else -1)
            pkqc__xrqdm += 1
    for zlqh__zcl in agg_node.gb_info_out.keys():
        wdesc__omp.append(zlqh__zcl)
        pkqc__xrqdm += 1
    pkfqv__pzuae = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            wdesc__omp.append(agg_node.n_out_cols - 1)
        else:
            pkfqv__pzuae = True
    cra__oofzw = ',' if vosc__mowka == 1 else ''
    tuamd__tcxc = (
        f"({', '.join(f'out_type{oenf__bhqaq}' for oenf__bhqaq in range(vosc__mowka))}{cra__oofzw})"
        )
    knhqs__onuwh = []
    yxui__nvub = []
    for oenf__bhqaq, t in enumerate(out_col_typs):
        if oenf__bhqaq not in agg_node.dead_out_inds and type_has_unknown_cats(
            t):
            if oenf__bhqaq in agg_node.gb_info_out:
                ufnp__bgg = agg_node.gb_info_out[oenf__bhqaq][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                ptm__dkbb = oenf__bhqaq - ecsv__qmio
                ufnp__bgg = agg_node.in_key_inds[ptm__dkbb]
            yxui__nvub.append(oenf__bhqaq)
            if (agg_node.is_in_table_format and ufnp__bgg < agg_node.
                n_in_table_arrays):
                knhqs__onuwh.append(f'get_table_data(arg0, {ufnp__bgg})')
            else:
                knhqs__onuwh.append(f'arg{ufnp__bgg}')
    cra__oofzw = ',' if len(knhqs__onuwh) == 1 else ''
    depe__xvu += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {tuamd__tcxc}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(knhqs__onuwh)}{cra__oofzw}), unknown_cat_out_inds)
"""
    depe__xvu += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    depe__xvu += '    delete_table_decref_arrays(table)\n'
    depe__xvu += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for oenf__bhqaq in range(n_keys):
            if wdesc__omp[oenf__bhqaq] == -1:
                depe__xvu += (
                    f'    decref_table_array(out_table, {oenf__bhqaq})\n')
    if pkfqv__pzuae:
        esf__kofey = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        depe__xvu += f'    decref_table_array(out_table, {esf__kofey})\n'
    depe__xvu += '    delete_table(out_table)\n'
    depe__xvu += '    ev_clean.finalize()\n'
    depe__xvu += '    return out_data\n'
    bnh__ibug = {f'out_type{oenf__bhqaq}': out_var_types[oenf__bhqaq] for
        oenf__bhqaq in range(vosc__mowka)}
    bnh__ibug['out_col_inds'] = MetaType(tuple(wdesc__omp))
    bnh__ibug['in_col_inds'] = MetaType(tuple(rreqi__naa))
    bnh__ibug['cpp_table_to_py_data'] = cpp_table_to_py_data
    bnh__ibug['py_data_to_cpp_table'] = py_data_to_cpp_table
    bnh__ibug.update({f'udf_type{oenf__bhqaq}': t for oenf__bhqaq, t in
        enumerate(fbcq__deche)})
    bnh__ibug['udf_dummy_col_inds'] = MetaType(tuple(range(len(fbcq__deche))))
    bnh__ibug['create_dummy_table'] = create_dummy_table
    bnh__ibug['unknown_cat_out_inds'] = MetaType(tuple(yxui__nvub))
    bnh__ibug['get_table_data'] = bodo.hiframes.table.get_table_data
    return depe__xvu, bnh__ibug


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    qwm__emj = tuple(unwrap_typeref(data_types.types[oenf__bhqaq]) for
        oenf__bhqaq in range(len(data_types.types)))
    frr__ybxp = bodo.TableType(qwm__emj)
    bnh__ibug = {'table_type': frr__ybxp}
    depe__xvu = 'def impl(data_types):\n'
    depe__xvu += '  py_table = init_table(table_type, False)\n'
    depe__xvu += '  py_table = set_table_len(py_table, 1)\n'
    for trt__ghg, ijgkl__rzslm in frr__ybxp.type_to_blk.items():
        bnh__ibug[f'typ_list_{ijgkl__rzslm}'] = types.List(trt__ghg)
        bnh__ibug[f'typ_{ijgkl__rzslm}'] = trt__ghg
        tpwf__zxbzs = len(frr__ybxp.block_to_arr_ind[ijgkl__rzslm])
        depe__xvu += f"""  arr_list_{ijgkl__rzslm} = alloc_list_like(typ_list_{ijgkl__rzslm}, {tpwf__zxbzs}, False)
"""
        depe__xvu += f'  for i in range(len(arr_list_{ijgkl__rzslm})):\n'
        depe__xvu += (
            f'    arr_list_{ijgkl__rzslm}[i] = alloc_type(1, typ_{ijgkl__rzslm}, (-1,))\n'
            )
        depe__xvu += f"""  py_table = set_table_block(py_table, arr_list_{ijgkl__rzslm}, {ijgkl__rzslm})
"""
    depe__xvu += '  return py_table\n'
    bnh__ibug.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    thf__uxmwd = {}
    exec(depe__xvu, bnh__ibug, thf__uxmwd)
    return thf__uxmwd['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    lslwi__weest = agg_node.in_vars[0].name
    hwi__ugg, ffprb__lbnvo, rkvmx__wse = block_use_map[lslwi__weest]
    if ffprb__lbnvo or rkvmx__wse:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        brgvb__vht, ymfz__djgdw, qrtu__wqtw = _compute_table_column_uses(
            agg_node.out_vars[0].name, table_col_use_map, equiv_vars)
        if ymfz__djgdw or qrtu__wqtw:
            brgvb__vht = set(range(agg_node.n_out_table_arrays))
    else:
        brgvb__vht = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            brgvb__vht = {0}
    vuf__ixlxj = set(oenf__bhqaq for oenf__bhqaq in agg_node.in_key_inds if
        oenf__bhqaq < agg_node.n_in_table_arrays)
    vqvh__nxkrz = set(agg_node.gb_info_out[oenf__bhqaq][0] for oenf__bhqaq in
        brgvb__vht if oenf__bhqaq in agg_node.gb_info_out and agg_node.
        gb_info_out[oenf__bhqaq][0] is not None)
    vqvh__nxkrz |= vuf__ixlxj | hwi__ugg
    gwse__fdhdu = len(set(range(agg_node.n_in_table_arrays)) - vqvh__nxkrz
        ) == 0
    block_use_map[lslwi__weest] = vqvh__nxkrz, gwse__fdhdu, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    ijvq__dcd = agg_node.n_out_table_arrays
    dwbe__hvkar = agg_node.out_vars[0].name
    mrw__jjo = _find_used_columns(dwbe__hvkar, ijvq__dcd, column_live_map,
        equiv_vars)
    if mrw__jjo is None:
        return False
    rxrct__etha = set(range(ijvq__dcd)) - mrw__jjo
    jwgv__avqvh = len(rxrct__etha - agg_node.dead_out_inds) != 0
    if jwgv__avqvh:
        agg_node.dead_out_inds.update(rxrct__etha)
        agg_node.update_dead_col_info()
    return jwgv__avqvh


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for wlvg__adc in block.body:
            if is_call_assign(wlvg__adc) and find_callname(f_ir, wlvg__adc.
                value) == ('len', 'builtins') and wlvg__adc.value.args[0
                ].name == f_ir.arg_names[0]:
                req__yzjbc = get_definition(f_ir, wlvg__adc.value.func)
                req__yzjbc.name = 'dummy_agg_count'
                req__yzjbc.value = dummy_agg_count
    krdh__cyp = get_name_var_table(f_ir.blocks)
    wks__djle = {}
    for name, hfl__alh in krdh__cyp.items():
        wks__djle[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, wks__djle)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    tpwr__fbkt = numba.core.compiler.Flags()
    tpwr__fbkt.nrt = True
    atp__ysdng = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, tpwr__fbkt)
    atp__ysdng.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, iyncf__thr, calltypes, hfl__alh = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    kxmus__mum = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    ekci__xvvgt = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    gfuk__axh = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    jhnfy__czum = gfuk__axh(typemap, calltypes)
    pm = ekci__xvvgt(typingctx, targetctx, None, f_ir, typemap, iyncf__thr,
        calltypes, jhnfy__czum, {}, tpwr__fbkt, None)
    emmq__vtl = numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline(
        pm)
    pm = ekci__xvvgt(typingctx, targetctx, None, f_ir, typemap, iyncf__thr,
        calltypes, jhnfy__czum, {}, tpwr__fbkt, emmq__vtl)
    ldqb__zefc = numba.core.typed_passes.InlineOverloads()
    ldqb__zefc.run_pass(pm)
    qjh__eqeo = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    qjh__eqeo.run()
    for block in f_ir.blocks.values():
        for wlvg__adc in block.body:
            if is_assign(wlvg__adc) and isinstance(wlvg__adc.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[wlvg__adc.target.name],
                SeriesType):
                trt__ghg = typemap.pop(wlvg__adc.target.name)
                typemap[wlvg__adc.target.name] = trt__ghg.data
            if is_call_assign(wlvg__adc) and find_callname(f_ir, wlvg__adc.
                value) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[wlvg__adc.target.name].remove(wlvg__adc.value
                    )
                wlvg__adc.value = wlvg__adc.value.args[0]
                f_ir._definitions[wlvg__adc.target.name].append(wlvg__adc.value
                    )
            if is_call_assign(wlvg__adc) and find_callname(f_ir, wlvg__adc.
                value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[wlvg__adc.target.name].remove(wlvg__adc.value
                    )
                wlvg__adc.value = ir.Const(False, wlvg__adc.loc)
                f_ir._definitions[wlvg__adc.target.name].append(wlvg__adc.value
                    )
            if is_call_assign(wlvg__adc) and find_callname(f_ir, wlvg__adc.
                value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[wlvg__adc.target.name].remove(wlvg__adc.value
                    )
                wlvg__adc.value = ir.Const(False, wlvg__adc.loc)
                f_ir._definitions[wlvg__adc.target.name].append(wlvg__adc.value
                    )
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    emikx__fvx = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, kxmus__mum)
    emikx__fvx.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    mqje__wkik = numba.core.compiler.StateDict()
    mqje__wkik.func_ir = f_ir
    mqje__wkik.typemap = typemap
    mqje__wkik.calltypes = calltypes
    mqje__wkik.typingctx = typingctx
    mqje__wkik.targetctx = targetctx
    mqje__wkik.return_type = iyncf__thr
    numba.core.rewrites.rewrite_registry.apply('after-inference', mqje__wkik)
    tutyn__hca = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        iyncf__thr, typingctx, targetctx, kxmus__mum, tpwr__fbkt, {})
    tutyn__hca.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            cje__wqm = ctypes.pythonapi.PyCell_Get
            cje__wqm.restype = ctypes.py_object
            cje__wqm.argtypes = ctypes.py_object,
            rbv__ras = tuple(cje__wqm(twy__bazwe) for twy__bazwe in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            rbv__ras = closure.items
        assert len(code.co_freevars) == len(rbv__ras)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, rbv__ras)


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
        heql__rfr = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array(
            in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (heql__rfr,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        esks__yos, arr_var = _rm_arg_agg_block(block, pm.typemap)
        gptm__qcar = -1
        for oenf__bhqaq, wlvg__adc in enumerate(esks__yos):
            if isinstance(wlvg__adc, numba.parfors.parfor.Parfor):
                assert gptm__qcar == -1, 'only one parfor for aggregation function'
                gptm__qcar = oenf__bhqaq
        parfor = None
        if gptm__qcar != -1:
            parfor = esks__yos[gptm__qcar]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = esks__yos[:gptm__qcar] + parfor.init_block.body
        eval_nodes = esks__yos[gptm__qcar + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for wlvg__adc in init_nodes:
            if is_assign(wlvg__adc) and wlvg__adc.target.name in redvars:
                ind = redvars.index(wlvg__adc.target.name)
                reduce_vars[ind] = wlvg__adc.target
        var_types = [pm.typemap[fxdc__otd] for fxdc__otd in redvars]
        azg__itg = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        bepw__slmxq = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        jysn__ewzqb = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(jysn__ewzqb)
        self.all_update_funcs.append(bepw__slmxq)
        self.all_combine_funcs.append(azg__itg)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        rqqic__yecyx = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        ygn__aahm = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        isp__fmdn = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        mccxy__ouloh = gen_all_eval_func(self.all_eval_funcs, self.
            redvar_offsets)
        return (self.all_vartypes, rqqic__yecyx, ygn__aahm, isp__fmdn,
            mccxy__ouloh)


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
    bxre__rre = []
    for t, dpxt__sehv in zip(in_col_types, agg_func):
        bxre__rre.append((t, dpxt__sehv))
    kbvwy__qlcq = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    yguh__nzc = GeneralUDFGenerator()
    for in_col_typ, func in bxre__rre:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            kbvwy__qlcq.add_udf(in_col_typ, func)
        except:
            yguh__nzc.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = kbvwy__qlcq.gen_all_func()
    general_udf_funcs = yguh__nzc.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    ajh__tait = compute_use_defs(parfor.loop_body)
    bet__tnw = set()
    for cqz__bnrh in ajh__tait.usemap.values():
        bet__tnw |= cqz__bnrh
    ftqj__xrnge = set()
    for cqz__bnrh in ajh__tait.defmap.values():
        ftqj__xrnge |= cqz__bnrh
    bwe__uuwfb = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    bwe__uuwfb.body = eval_nodes
    ttplq__pyvnv = compute_use_defs({(0): bwe__uuwfb})
    ykgfl__bkgi = ttplq__pyvnv.usemap[0]
    usxz__qqh = set()
    msymz__gde = []
    hippz__mhrqr = []
    for wlvg__adc in reversed(init_nodes):
        wobr__srcsi = {fxdc__otd.name for fxdc__otd in wlvg__adc.list_vars()}
        if is_assign(wlvg__adc):
            fxdc__otd = wlvg__adc.target.name
            wobr__srcsi.remove(fxdc__otd)
            if (fxdc__otd in bet__tnw and fxdc__otd not in usxz__qqh and 
                fxdc__otd not in ykgfl__bkgi and fxdc__otd not in ftqj__xrnge):
                hippz__mhrqr.append(wlvg__adc)
                bet__tnw |= wobr__srcsi
                ftqj__xrnge.add(fxdc__otd)
                continue
        usxz__qqh |= wobr__srcsi
        msymz__gde.append(wlvg__adc)
    hippz__mhrqr.reverse()
    msymz__gde.reverse()
    meqtt__hqyu = min(parfor.loop_body.keys())
    ticlr__pxmw = parfor.loop_body[meqtt__hqyu]
    ticlr__pxmw.body = hippz__mhrqr + ticlr__pxmw.body
    return msymz__gde


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    golb__xqanw = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    obfc__kdkey = set()
    mxw__zyoxu = []
    for wlvg__adc in init_nodes:
        if is_assign(wlvg__adc) and isinstance(wlvg__adc.value, ir.Global
            ) and isinstance(wlvg__adc.value.value, pytypes.FunctionType
            ) and wlvg__adc.value.value in golb__xqanw:
            obfc__kdkey.add(wlvg__adc.target.name)
        elif is_call_assign(wlvg__adc
            ) and wlvg__adc.value.func.name in obfc__kdkey:
            pass
        else:
            mxw__zyoxu.append(wlvg__adc)
    init_nodes = mxw__zyoxu
    lane__fjde = types.Tuple(var_types)
    wga__xzcf = lambda : None
    f_ir = compile_to_numba_ir(wga__xzcf, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    gfhx__wtk = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    edef__hjybu = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        gfhx__wtk, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [edef__hjybu] + block.body
    block.body[-2].value.value = gfhx__wtk
    gub__guv = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        lane__fjde, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uxdq__cdat = numba.core.target_extension.dispatcher_registry[cpu_target](
        wga__xzcf)
    uxdq__cdat.add_overload(gub__guv)
    return uxdq__cdat


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    pnbm__izjj = len(update_funcs)
    aee__uuxif = len(in_col_types)
    depe__xvu = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for zrls__hklno in range(pnbm__izjj):
        fjv__hhzz = ', '.join(['redvar_arrs[{}][w_ind]'.format(oenf__bhqaq) for
            oenf__bhqaq in range(redvar_offsets[zrls__hklno],
            redvar_offsets[zrls__hklno + 1])])
        if fjv__hhzz:
            depe__xvu += '  {} = update_vars_{}({},  data_in[{}][i])\n'.format(
                fjv__hhzz, zrls__hklno, fjv__hhzz, 0 if aee__uuxif == 1 else
                zrls__hklno)
    depe__xvu += '  return\n'
    uks__zwkan = {}
    for oenf__bhqaq, dpxt__sehv in enumerate(update_funcs):
        uks__zwkan['update_vars_{}'.format(oenf__bhqaq)] = dpxt__sehv
    thf__uxmwd = {}
    exec(depe__xvu, uks__zwkan, thf__uxmwd)
    bfk__nyttj = thf__uxmwd['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(bfk__nyttj)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    jabau__shtns = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    arg_typs = jabau__shtns, jabau__shtns, types.intp, types.intp
    kjnuo__btte = len(redvar_offsets) - 1
    depe__xvu = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for zrls__hklno in range(kjnuo__btte):
        fjv__hhzz = ', '.join(['redvar_arrs[{}][w_ind]'.format(oenf__bhqaq) for
            oenf__bhqaq in range(redvar_offsets[zrls__hklno],
            redvar_offsets[zrls__hklno + 1])])
        fxltu__vts = ', '.join(['recv_arrs[{}][i]'.format(oenf__bhqaq) for
            oenf__bhqaq in range(redvar_offsets[zrls__hklno],
            redvar_offsets[zrls__hklno + 1])])
        if fxltu__vts:
            depe__xvu += '  {} = combine_vars_{}({}, {})\n'.format(fjv__hhzz,
                zrls__hklno, fjv__hhzz, fxltu__vts)
    depe__xvu += '  return\n'
    uks__zwkan = {}
    for oenf__bhqaq, dpxt__sehv in enumerate(combine_funcs):
        uks__zwkan['combine_vars_{}'.format(oenf__bhqaq)] = dpxt__sehv
    thf__uxmwd = {}
    exec(depe__xvu, uks__zwkan, thf__uxmwd)
    ukft__nnse = thf__uxmwd['combine_all_f']
    f_ir = compile_to_numba_ir(ukft__nnse, uks__zwkan)
    isp__fmdn = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uxdq__cdat = numba.core.target_extension.dispatcher_registry[cpu_target](
        ukft__nnse)
    uxdq__cdat.add_overload(isp__fmdn)
    return uxdq__cdat


def gen_all_eval_func(eval_funcs, redvar_offsets):
    kjnuo__btte = len(redvar_offsets) - 1
    depe__xvu = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for zrls__hklno in range(kjnuo__btte):
        fjv__hhzz = ', '.join(['redvar_arrs[{}][j]'.format(oenf__bhqaq) for
            oenf__bhqaq in range(redvar_offsets[zrls__hklno],
            redvar_offsets[zrls__hklno + 1])])
        depe__xvu += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
            zrls__hklno, zrls__hklno, fjv__hhzz)
    depe__xvu += '  return\n'
    uks__zwkan = {}
    for oenf__bhqaq, dpxt__sehv in enumerate(eval_funcs):
        uks__zwkan['eval_vars_{}'.format(oenf__bhqaq)] = dpxt__sehv
    thf__uxmwd = {}
    exec(depe__xvu, uks__zwkan, thf__uxmwd)
    vbnpn__pxyey = thf__uxmwd['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(vbnpn__pxyey)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    kntbe__arc = len(var_types)
    kivz__bkl = [f'in{oenf__bhqaq}' for oenf__bhqaq in range(kntbe__arc)]
    lane__fjde = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    lrcec__npxe = lane__fjde(0)
    depe__xvu = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        kivz__bkl))
    thf__uxmwd = {}
    exec(depe__xvu, {'_zero': lrcec__npxe}, thf__uxmwd)
    jivy__oewsu = thf__uxmwd['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(jivy__oewsu, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': lrcec__npxe}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    setup__jcup = []
    for oenf__bhqaq, fxdc__otd in enumerate(reduce_vars):
        setup__jcup.append(ir.Assign(block.body[oenf__bhqaq].target,
            fxdc__otd, fxdc__otd.loc))
        for nhls__hgf in fxdc__otd.versioned_names:
            setup__jcup.append(ir.Assign(fxdc__otd, ir.Var(fxdc__otd.scope,
                nhls__hgf, fxdc__otd.loc), fxdc__otd.loc))
    block.body = block.body[:kntbe__arc] + setup__jcup + eval_nodes
    jysn__ewzqb = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        lane__fjde, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uxdq__cdat = numba.core.target_extension.dispatcher_registry[cpu_target](
        jivy__oewsu)
    uxdq__cdat.add_overload(jysn__ewzqb)
    return uxdq__cdat


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    kntbe__arc = len(redvars)
    gfslz__kgc = [f'v{oenf__bhqaq}' for oenf__bhqaq in range(kntbe__arc)]
    kivz__bkl = [f'in{oenf__bhqaq}' for oenf__bhqaq in range(kntbe__arc)]
    depe__xvu = 'def agg_combine({}):\n'.format(', '.join(gfslz__kgc +
        kivz__bkl))
    iizj__pbo = wrap_parfor_blocks(parfor)
    zrpp__xwlvs = find_topo_order(iizj__pbo)
    zrpp__xwlvs = zrpp__xwlvs[1:]
    unwrap_parfor_blocks(parfor)
    lrt__escmk = {}
    vygau__wwq = []
    for ypvf__rkocv in zrpp__xwlvs:
        cyg__ycc = parfor.loop_body[ypvf__rkocv]
        for wlvg__adc in cyg__ycc.body:
            if is_assign(wlvg__adc) and wlvg__adc.target.name in redvars:
                jxugv__vreq = wlvg__adc.target.name
                ind = redvars.index(jxugv__vreq)
                if ind in vygau__wwq:
                    continue
                if len(f_ir._definitions[jxugv__vreq]) == 2:
                    var_def = f_ir._definitions[jxugv__vreq][0]
                    depe__xvu += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[jxugv__vreq][1]
                    depe__xvu += _match_reduce_def(var_def, f_ir, ind)
    depe__xvu += '    return {}'.format(', '.join(['v{}'.format(oenf__bhqaq
        ) for oenf__bhqaq in range(kntbe__arc)]))
    thf__uxmwd = {}
    exec(depe__xvu, {}, thf__uxmwd)
    kyf__gipxk = thf__uxmwd['agg_combine']
    arg_typs = tuple(2 * var_types)
    uks__zwkan = {'numba': numba, 'bodo': bodo, 'np': np}
    uks__zwkan.update(lrt__escmk)
    f_ir = compile_to_numba_ir(kyf__gipxk, uks__zwkan, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    lane__fjde = pm.typemap[block.body[-1].value.name]
    azg__itg = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        lane__fjde, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uxdq__cdat = numba.core.target_extension.dispatcher_registry[cpu_target](
        kyf__gipxk)
    uxdq__cdat.add_overload(azg__itg)
    return uxdq__cdat


def _match_reduce_def(var_def, f_ir, ind):
    depe__xvu = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        depe__xvu = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        vfd__apwk = guard(find_callname, f_ir, var_def)
        if vfd__apwk == ('min', 'builtins'):
            depe__xvu = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if vfd__apwk == ('max', 'builtins'):
            depe__xvu = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return depe__xvu


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    kntbe__arc = len(redvars)
    tpbt__praf = 1
    in_vars = []
    for oenf__bhqaq in range(tpbt__praf):
        xfgml__irq = ir.Var(arr_var.scope, f'$input{oenf__bhqaq}', arr_var.loc)
        in_vars.append(xfgml__irq)
    jops__hhwja = parfor.loop_nests[0].index_variable
    dhdc__rlw = [0] * kntbe__arc
    for cyg__ycc in parfor.loop_body.values():
        zsu__zcgpa = []
        for wlvg__adc in cyg__ycc.body:
            if is_var_assign(wlvg__adc
                ) and wlvg__adc.value.name == jops__hhwja.name:
                continue
            if is_getitem(wlvg__adc
                ) and wlvg__adc.value.value.name == arr_var.name:
                wlvg__adc.value = in_vars[0]
            if is_call_assign(wlvg__adc) and guard(find_callname, pm.
                func_ir, wlvg__adc.value) == ('isna', 'bodo.libs.array_kernels'
                ) and wlvg__adc.value.args[0].name == arr_var.name:
                wlvg__adc.value = ir.Const(False, wlvg__adc.target.loc)
            if is_assign(wlvg__adc) and wlvg__adc.target.name in redvars:
                ind = redvars.index(wlvg__adc.target.name)
                dhdc__rlw[ind] = wlvg__adc.target
            zsu__zcgpa.append(wlvg__adc)
        cyg__ycc.body = zsu__zcgpa
    gfslz__kgc = ['v{}'.format(oenf__bhqaq) for oenf__bhqaq in range(
        kntbe__arc)]
    kivz__bkl = ['in{}'.format(oenf__bhqaq) for oenf__bhqaq in range(
        tpbt__praf)]
    depe__xvu = 'def agg_update({}):\n'.format(', '.join(gfslz__kgc +
        kivz__bkl))
    depe__xvu += '    __update_redvars()\n'
    depe__xvu += '    return {}'.format(', '.join(['v{}'.format(oenf__bhqaq
        ) for oenf__bhqaq in range(kntbe__arc)]))
    thf__uxmwd = {}
    exec(depe__xvu, {}, thf__uxmwd)
    ycyly__rexk = thf__uxmwd['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * tpbt__praf)
    f_ir = compile_to_numba_ir(ycyly__rexk, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    ppnl__fvw = f_ir.blocks.popitem()[1].body
    lane__fjde = pm.typemap[ppnl__fvw[-1].value.name]
    iizj__pbo = wrap_parfor_blocks(parfor)
    zrpp__xwlvs = find_topo_order(iizj__pbo)
    zrpp__xwlvs = zrpp__xwlvs[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    ticlr__pxmw = f_ir.blocks[zrpp__xwlvs[0]]
    dzjzm__byrh = f_ir.blocks[zrpp__xwlvs[-1]]
    iih__bpqq = ppnl__fvw[:kntbe__arc + tpbt__praf]
    if kntbe__arc > 1:
        pnzp__saktt = ppnl__fvw[-3:]
        assert is_assign(pnzp__saktt[0]) and isinstance(pnzp__saktt[0].
            value, ir.Expr) and pnzp__saktt[0].value.op == 'build_tuple'
    else:
        pnzp__saktt = ppnl__fvw[-2:]
    for oenf__bhqaq in range(kntbe__arc):
        vcf__thz = ppnl__fvw[oenf__bhqaq].target
        itako__xufgm = ir.Assign(vcf__thz, dhdc__rlw[oenf__bhqaq], vcf__thz.loc
            )
        iih__bpqq.append(itako__xufgm)
    for oenf__bhqaq in range(kntbe__arc, kntbe__arc + tpbt__praf):
        vcf__thz = ppnl__fvw[oenf__bhqaq].target
        itako__xufgm = ir.Assign(vcf__thz, in_vars[oenf__bhqaq - kntbe__arc
            ], vcf__thz.loc)
        iih__bpqq.append(itako__xufgm)
    ticlr__pxmw.body = iih__bpqq + ticlr__pxmw.body
    cam__dxms = []
    for oenf__bhqaq in range(kntbe__arc):
        vcf__thz = ppnl__fvw[oenf__bhqaq].target
        itako__xufgm = ir.Assign(dhdc__rlw[oenf__bhqaq], vcf__thz, vcf__thz.loc
            )
        cam__dxms.append(itako__xufgm)
    dzjzm__byrh.body += cam__dxms + pnzp__saktt
    gmtdi__flcli = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        lane__fjde, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    uxdq__cdat = numba.core.target_extension.dispatcher_registry[cpu_target](
        ycyly__rexk)
    uxdq__cdat.add_overload(gmtdi__flcli)
    return uxdq__cdat


def _rm_arg_agg_block(block, typemap):
    esks__yos = []
    arr_var = None
    for oenf__bhqaq, wlvg__adc in enumerate(block.body):
        if is_assign(wlvg__adc) and isinstance(wlvg__adc.value, ir.Arg):
            arr_var = wlvg__adc.target
            ndqwd__yyrsf = typemap[arr_var.name]
            if not isinstance(ndqwd__yyrsf, types.ArrayCompatible):
                esks__yos += block.body[oenf__bhqaq + 1:]
                break
            egf__cbxil = block.body[oenf__bhqaq + 1]
            assert is_assign(egf__cbxil) and isinstance(egf__cbxil.value,
                ir.Expr
                ) and egf__cbxil.value.op == 'getattr' and egf__cbxil.value.attr == 'shape' and egf__cbxil.value.value.name == arr_var.name
            dqdj__jaaeo = egf__cbxil.target
            mdsw__ruy = block.body[oenf__bhqaq + 2]
            assert is_assign(mdsw__ruy) and isinstance(mdsw__ruy.value, ir.Expr
                ) and mdsw__ruy.value.op == 'static_getitem' and mdsw__ruy.value.value.name == dqdj__jaaeo.name
            esks__yos += block.body[oenf__bhqaq + 3:]
            break
        esks__yos.append(wlvg__adc)
    return esks__yos, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    iizj__pbo = wrap_parfor_blocks(parfor)
    zrpp__xwlvs = find_topo_order(iizj__pbo)
    zrpp__xwlvs = zrpp__xwlvs[1:]
    unwrap_parfor_blocks(parfor)
    for ypvf__rkocv in reversed(zrpp__xwlvs):
        for wlvg__adc in reversed(parfor.loop_body[ypvf__rkocv].body):
            if isinstance(wlvg__adc, ir.Assign) and (wlvg__adc.target.name in
                parfor_params or wlvg__adc.target.name in var_to_param):
                mwov__mmckb = wlvg__adc.target.name
                rhs = wlvg__adc.value
                sbyc__zghqi = (mwov__mmckb if mwov__mmckb in parfor_params else
                    var_to_param[mwov__mmckb])
                lcglx__shyh = []
                if isinstance(rhs, ir.Var):
                    lcglx__shyh = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    lcglx__shyh = [fxdc__otd.name for fxdc__otd in
                        wlvg__adc.value.list_vars()]
                param_uses[sbyc__zghqi].extend(lcglx__shyh)
                for fxdc__otd in lcglx__shyh:
                    var_to_param[fxdc__otd] = sbyc__zghqi
            if isinstance(wlvg__adc, Parfor):
                get_parfor_reductions(wlvg__adc, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for usga__wso, lcglx__shyh in param_uses.items():
        if usga__wso in lcglx__shyh and usga__wso not in reduce_varnames:
            reduce_varnames.append(usga__wso)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
