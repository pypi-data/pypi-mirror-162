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
        rsik__iihn = func.signature
        if rsik__iihn == types.none(types.voidptr):
            hlpjg__jho = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            mlvz__agspn = cgutils.get_or_insert_function(builder.module,
                hlpjg__jho, sym._literal_value)
            builder.call(mlvz__agspn, [context.get_constant_null(rsik__iihn
                .args[0])])
        elif rsik__iihn == types.none(types.int64, types.voidptr, types.voidptr
            ):
            hlpjg__jho = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            mlvz__agspn = cgutils.get_or_insert_function(builder.module,
                hlpjg__jho, sym._literal_value)
            builder.call(mlvz__agspn, [context.get_constant(types.int64, 0),
                context.get_constant_null(rsik__iihn.args[1]), context.
                get_constant_null(rsik__iihn.args[2])])
        else:
            hlpjg__jho = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            mlvz__agspn = cgutils.get_or_insert_function(builder.module,
                hlpjg__jho, sym._literal_value)
            builder.call(mlvz__agspn, [context.get_constant_null(rsik__iihn
                .args[0]), context.get_constant_null(rsik__iihn.args[1]),
                context.get_constant_null(rsik__iihn.args[2])])
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
        hvvf__cvzmp = True
        icv__svdyd = 1
        azihn__cunl = -1
        if isinstance(rhs, ir.Expr):
            for ctsyc__hbwn in rhs.kws:
                if func_name in list_cumulative:
                    if ctsyc__hbwn[0] == 'skipna':
                        hvvf__cvzmp = guard(find_const, func_ir, ctsyc__hbwn[1]
                            )
                        if not isinstance(hvvf__cvzmp, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if ctsyc__hbwn[0] == 'dropna':
                        hvvf__cvzmp = guard(find_const, func_ir, ctsyc__hbwn[1]
                            )
                        if not isinstance(hvvf__cvzmp, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            icv__svdyd = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', icv__svdyd)
            icv__svdyd = guard(find_const, func_ir, icv__svdyd)
        if func_name == 'head':
            azihn__cunl = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(azihn__cunl, int):
                azihn__cunl = guard(find_const, func_ir, azihn__cunl)
            if azihn__cunl < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = hvvf__cvzmp
        func.periods = icv__svdyd
        func.head_n = azihn__cunl
        if func_name == 'transform':
            kws = dict(rhs.kws)
            gwok__rgrw = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            jrzwp__nvzl = typemap[gwok__rgrw.name]
            dayac__cknr = None
            if isinstance(jrzwp__nvzl, str):
                dayac__cknr = jrzwp__nvzl
            elif is_overload_constant_str(jrzwp__nvzl):
                dayac__cknr = get_overload_const_str(jrzwp__nvzl)
            elif bodo.utils.typing.is_builtin_function(jrzwp__nvzl):
                dayac__cknr = bodo.utils.typing.get_builtin_function_name(
                    jrzwp__nvzl)
            if dayac__cknr not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {dayac__cknr}'
                    )
            func.transform_func = supported_agg_funcs.index(dayac__cknr)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    gwok__rgrw = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if gwok__rgrw == '':
        jrzwp__nvzl = types.none
    else:
        jrzwp__nvzl = typemap[gwok__rgrw.name]
    if is_overload_constant_dict(jrzwp__nvzl):
        mtxyb__txn = get_overload_constant_dict(jrzwp__nvzl)
        qnu__tren = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in mtxyb__txn.values()]
        return qnu__tren
    if jrzwp__nvzl == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(jrzwp__nvzl, types.BaseTuple) or is_overload_constant_list(
        jrzwp__nvzl):
        qnu__tren = []
        hhxwy__ienfl = 0
        if is_overload_constant_list(jrzwp__nvzl):
            lzdv__ymv = get_overload_const_list(jrzwp__nvzl)
        else:
            lzdv__ymv = jrzwp__nvzl.types
        for t in lzdv__ymv:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                qnu__tren.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(lzdv__ymv) > 1:
                    func.fname = '<lambda_' + str(hhxwy__ienfl) + '>'
                    hhxwy__ienfl += 1
                qnu__tren.append(func)
        return [qnu__tren]
    if is_overload_constant_str(jrzwp__nvzl):
        func_name = get_overload_const_str(jrzwp__nvzl)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(jrzwp__nvzl):
        func_name = bodo.utils.typing.get_builtin_function_name(jrzwp__nvzl)
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
        hhxwy__ienfl = 0
        cya__gzd = []
        for reibc__pmwg in f_val:
            func = get_agg_func_udf(func_ir, reibc__pmwg, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{hhxwy__ienfl}>'
                hhxwy__ienfl += 1
            cya__gzd.append(func)
        return cya__gzd
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
    dayac__cknr = code.co_name
    return dayac__cknr


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
            tqu__umon = types.DType(args[0])
            return signature(tqu__umon, *args)


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
        return [hjf__ssk for hjf__ssk in self.in_vars if hjf__ssk is not None]

    def get_live_out_vars(self):
        return [hjf__ssk for hjf__ssk in self.out_vars if hjf__ssk is not None]

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
        bifo__mfe = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        lxu__ygrmk = list(get_index_data_arr_types(self.out_type.index))
        return bifo__mfe + lxu__ygrmk

    def update_dead_col_info(self):
        for pty__bbqv in self.dead_out_inds:
            self.gb_info_out.pop(pty__bbqv, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for dho__vcuv, nrw__xeiwi in self.gb_info_in.copy().items():
            pmvk__zebxu = []
            for reibc__pmwg, lwa__tcl in nrw__xeiwi:
                if lwa__tcl not in self.dead_out_inds:
                    pmvk__zebxu.append((reibc__pmwg, lwa__tcl))
            if not pmvk__zebxu:
                if dho__vcuv is not None and dho__vcuv not in self.in_key_inds:
                    self.dead_in_inds.add(dho__vcuv)
                self.gb_info_in.pop(dho__vcuv)
            else:
                self.gb_info_in[dho__vcuv] = pmvk__zebxu
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for akdm__jedsr in range(1, len(self.in_vars)):
                pty__bbqv = self.n_in_table_arrays + akdm__jedsr - 1
                if pty__bbqv in self.dead_in_inds:
                    self.in_vars[akdm__jedsr] = None
        else:
            for akdm__jedsr in range(len(self.in_vars)):
                if akdm__jedsr in self.dead_in_inds:
                    self.in_vars[akdm__jedsr] = None

    def __repr__(self):
        ogrl__yww = ', '.join(hjf__ssk.name for hjf__ssk in self.
            get_live_in_vars())
        hqpfs__piwge = f'{self.df_in}{{{ogrl__yww}}}'
        xbl__kvio = ', '.join(hjf__ssk.name for hjf__ssk in self.
            get_live_out_vars())
        hpsi__blny = f'{self.df_out}{{{xbl__kvio}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {hqpfs__piwge} {hpsi__blny}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({hjf__ssk.name for hjf__ssk in aggregate_node.
        get_live_in_vars()})
    def_set.update({hjf__ssk.name for hjf__ssk in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    unpj__sgoqj = agg_node.out_vars[0]
    if unpj__sgoqj is not None and unpj__sgoqj.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            fxbb__iay = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(fxbb__iay)
        else:
            agg_node.dead_out_inds.add(0)
    for akdm__jedsr in range(1, len(agg_node.out_vars)):
        hjf__ssk = agg_node.out_vars[akdm__jedsr]
        if hjf__ssk is not None and hjf__ssk.name not in lives:
            agg_node.out_vars[akdm__jedsr] = None
            pty__bbqv = agg_node.n_out_table_arrays + akdm__jedsr - 1
            agg_node.dead_out_inds.add(pty__bbqv)
    if all(hjf__ssk is None for hjf__ssk in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    rrc__xpnz = {hjf__ssk.name for hjf__ssk in aggregate_node.
        get_live_out_vars()}
    return set(), rrc__xpnz


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for akdm__jedsr in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[akdm__jedsr] is not None:
            aggregate_node.in_vars[akdm__jedsr] = replace_vars_inner(
                aggregate_node.in_vars[akdm__jedsr], var_dict)
    for akdm__jedsr in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[akdm__jedsr] is not None:
            aggregate_node.out_vars[akdm__jedsr] = replace_vars_inner(
                aggregate_node.out_vars[akdm__jedsr], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for akdm__jedsr in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[akdm__jedsr] is not None:
            aggregate_node.in_vars[akdm__jedsr] = visit_vars_inner(
                aggregate_node.in_vars[akdm__jedsr], callback, cbdata)
    for akdm__jedsr in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[akdm__jedsr] is not None:
            aggregate_node.out_vars[akdm__jedsr] = visit_vars_inner(
                aggregate_node.out_vars[akdm__jedsr], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    hmrru__kbcrr = []
    for aeoy__nyt in aggregate_node.get_live_in_vars():
        tpsg__hxieu = equiv_set.get_shape(aeoy__nyt)
        if tpsg__hxieu is not None:
            hmrru__kbcrr.append(tpsg__hxieu[0])
    if len(hmrru__kbcrr) > 1:
        equiv_set.insert_equiv(*hmrru__kbcrr)
    slc__anjxe = []
    hmrru__kbcrr = []
    for aeoy__nyt in aggregate_node.get_live_out_vars():
        lzbku__myeg = typemap[aeoy__nyt.name]
        nmul__vjviq = array_analysis._gen_shape_call(equiv_set, aeoy__nyt,
            lzbku__myeg.ndim, None, slc__anjxe)
        equiv_set.insert_equiv(aeoy__nyt, nmul__vjviq)
        hmrru__kbcrr.append(nmul__vjviq[0])
        equiv_set.define(aeoy__nyt, set())
    if len(hmrru__kbcrr) > 1:
        equiv_set.insert_equiv(*hmrru__kbcrr)
    return [], slc__anjxe


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    onvs__wjeqy = aggregate_node.get_live_in_vars()
    cgz__zjc = aggregate_node.get_live_out_vars()
    kbuk__tsrz = Distribution.OneD
    for aeoy__nyt in onvs__wjeqy:
        kbuk__tsrz = Distribution(min(kbuk__tsrz.value, array_dists[
            aeoy__nyt.name].value))
    mfoo__ghw = Distribution(min(kbuk__tsrz.value, Distribution.OneD_Var.value)
        )
    for aeoy__nyt in cgz__zjc:
        if aeoy__nyt.name in array_dists:
            mfoo__ghw = Distribution(min(mfoo__ghw.value, array_dists[
                aeoy__nyt.name].value))
    if mfoo__ghw != Distribution.OneD_Var:
        kbuk__tsrz = mfoo__ghw
    for aeoy__nyt in onvs__wjeqy:
        array_dists[aeoy__nyt.name] = kbuk__tsrz
    for aeoy__nyt in cgz__zjc:
        array_dists[aeoy__nyt.name] = mfoo__ghw


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for aeoy__nyt in agg_node.get_live_out_vars():
        definitions[aeoy__nyt.name].append(agg_node)
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
    rsc__mnkd = agg_node.get_live_in_vars()
    ftf__yqzcx = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for hjf__ssk in (rsc__mnkd + ftf__yqzcx):
            if array_dists[hjf__ssk.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                hjf__ssk.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    qnu__tren = []
    func_out_types = []
    for lwa__tcl, (dho__vcuv, func) in agg_node.gb_info_out.items():
        if dho__vcuv is not None:
            t = agg_node.in_col_types[dho__vcuv]
            in_col_typs.append(t)
        qnu__tren.append(func)
        func_out_types.append(out_col_typs[lwa__tcl])
    qqzl__vrp = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for akdm__jedsr, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            qqzl__vrp.update({f'in_cat_dtype_{akdm__jedsr}': in_col_typ})
    for akdm__jedsr, sobd__htq in enumerate(out_col_typs):
        if isinstance(sobd__htq, bodo.CategoricalArrayType):
            qqzl__vrp.update({f'out_cat_dtype_{akdm__jedsr}': sobd__htq})
    udf_func_struct = get_udf_func_struct(qnu__tren, in_col_typs, typingctx,
        targetctx)
    out_var_types = [(typemap[hjf__ssk.name] if hjf__ssk is not None else
        types.none) for hjf__ssk in agg_node.out_vars]
    cne__omgo, reqf__hxce = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    qqzl__vrp.update(reqf__hxce)
    qqzl__vrp.update({'pd': pd, 'pre_alloc_string_array':
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
            qqzl__vrp.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            qqzl__vrp.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    qeux__iegzi = {}
    exec(cne__omgo, {}, qeux__iegzi)
    sjo__dkfp = qeux__iegzi['agg_top']
    wprdp__vdc = compile_to_numba_ir(sjo__dkfp, qqzl__vrp, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[hjf__ssk.
        name] for hjf__ssk in rsc__mnkd), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(wprdp__vdc, rsc__mnkd)
    hft__wwyt = wprdp__vdc.body[-2].value.value
    loyjh__obel = wprdp__vdc.body[:-2]
    for akdm__jedsr, hjf__ssk in enumerate(ftf__yqzcx):
        gen_getitem(hjf__ssk, hft__wwyt, akdm__jedsr, calltypes, loyjh__obel)
    return loyjh__obel


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        khrq__lxaa = IntDtype(t.dtype).name
        assert khrq__lxaa.endswith('Dtype()')
        khrq__lxaa = khrq__lxaa[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{khrq__lxaa}'))"
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
        sayhk__efviz = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {sayhk__efviz}_cat_dtype_{colnum})'
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
    zadl__wazq = udf_func_struct.var_typs
    krvem__ftec = len(zadl__wazq)
    cne__omgo = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    cne__omgo += '    if is_null_pointer(in_table):\n'
    cne__omgo += '        return\n'
    cne__omgo += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in zadl__wazq]), 
        ',' if len(zadl__wazq) == 1 else '')
    exxs__monj = n_keys
    disfh__avkov = []
    redvar_offsets = []
    qbp__jxx = []
    if do_combine:
        for akdm__jedsr, reibc__pmwg in enumerate(allfuncs):
            if reibc__pmwg.ftype != 'udf':
                exxs__monj += reibc__pmwg.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(exxs__monj, exxs__monj +
                    reibc__pmwg.n_redvars))
                exxs__monj += reibc__pmwg.n_redvars
                qbp__jxx.append(data_in_typs_[func_idx_to_in_col[akdm__jedsr]])
                disfh__avkov.append(func_idx_to_in_col[akdm__jedsr] + n_keys)
    else:
        for akdm__jedsr, reibc__pmwg in enumerate(allfuncs):
            if reibc__pmwg.ftype != 'udf':
                exxs__monj += reibc__pmwg.ncols_post_shuffle
            else:
                redvar_offsets += list(range(exxs__monj + 1, exxs__monj + 1 +
                    reibc__pmwg.n_redvars))
                exxs__monj += reibc__pmwg.n_redvars + 1
                qbp__jxx.append(data_in_typs_[func_idx_to_in_col[akdm__jedsr]])
                disfh__avkov.append(func_idx_to_in_col[akdm__jedsr] + n_keys)
    assert len(redvar_offsets) == krvem__ftec
    wxl__unil = len(qbp__jxx)
    iyy__ula = []
    for akdm__jedsr, t in enumerate(qbp__jxx):
        iyy__ula.append(_gen_dummy_alloc(t, akdm__jedsr, True))
    cne__omgo += '    data_in_dummy = ({}{})\n'.format(','.join(iyy__ula), 
        ',' if len(qbp__jxx) == 1 else '')
    cne__omgo += """
    # initialize redvar cols
"""
    cne__omgo += '    init_vals = __init_func()\n'
    for akdm__jedsr in range(krvem__ftec):
        cne__omgo += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(akdm__jedsr, redvar_offsets[akdm__jedsr], akdm__jedsr))
        cne__omgo += '    incref(redvar_arr_{})\n'.format(akdm__jedsr)
        cne__omgo += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            akdm__jedsr, akdm__jedsr)
    cne__omgo += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(akdm__jedsr) for akdm__jedsr in range(krvem__ftec)]), ',' if
        krvem__ftec == 1 else '')
    cne__omgo += '\n'
    for akdm__jedsr in range(wxl__unil):
        cne__omgo += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(akdm__jedsr, disfh__avkov[akdm__jedsr], akdm__jedsr))
        cne__omgo += '    incref(data_in_{})\n'.format(akdm__jedsr)
    cne__omgo += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(akdm__jedsr) for akdm__jedsr in range(wxl__unil)]), ',' if 
        wxl__unil == 1 else '')
    cne__omgo += '\n'
    cne__omgo += '    for i in range(len(data_in_0)):\n'
    cne__omgo += '        w_ind = row_to_group[i]\n'
    cne__omgo += '        if w_ind != -1:\n'
    cne__omgo += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    qeux__iegzi = {}
    exec(cne__omgo, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, qeux__iegzi)
    return qeux__iegzi['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    zadl__wazq = udf_func_struct.var_typs
    krvem__ftec = len(zadl__wazq)
    cne__omgo = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    cne__omgo += '    if is_null_pointer(in_table):\n'
    cne__omgo += '        return\n'
    cne__omgo += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in zadl__wazq]), 
        ',' if len(zadl__wazq) == 1 else '')
    rhknt__qwr = n_keys
    mykpm__pvmlf = n_keys
    canei__vju = []
    obahb__dzhuj = []
    for reibc__pmwg in allfuncs:
        if reibc__pmwg.ftype != 'udf':
            rhknt__qwr += reibc__pmwg.ncols_pre_shuffle
            mykpm__pvmlf += reibc__pmwg.ncols_post_shuffle
        else:
            canei__vju += list(range(rhknt__qwr, rhknt__qwr + reibc__pmwg.
                n_redvars))
            obahb__dzhuj += list(range(mykpm__pvmlf + 1, mykpm__pvmlf + 1 +
                reibc__pmwg.n_redvars))
            rhknt__qwr += reibc__pmwg.n_redvars
            mykpm__pvmlf += 1 + reibc__pmwg.n_redvars
    assert len(canei__vju) == krvem__ftec
    cne__omgo += """
    # initialize redvar cols
"""
    cne__omgo += '    init_vals = __init_func()\n'
    for akdm__jedsr in range(krvem__ftec):
        cne__omgo += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(akdm__jedsr, obahb__dzhuj[akdm__jedsr], akdm__jedsr))
        cne__omgo += '    incref(redvar_arr_{})\n'.format(akdm__jedsr)
        cne__omgo += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            akdm__jedsr, akdm__jedsr)
    cne__omgo += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(akdm__jedsr) for akdm__jedsr in range(krvem__ftec)]), ',' if
        krvem__ftec == 1 else '')
    cne__omgo += '\n'
    for akdm__jedsr in range(krvem__ftec):
        cne__omgo += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(akdm__jedsr, canei__vju[akdm__jedsr], akdm__jedsr))
        cne__omgo += '    incref(recv_redvar_arr_{})\n'.format(akdm__jedsr)
    cne__omgo += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(akdm__jedsr) for akdm__jedsr in range(
        krvem__ftec)]), ',' if krvem__ftec == 1 else '')
    cne__omgo += '\n'
    if krvem__ftec:
        cne__omgo += '    for i in range(len(recv_redvar_arr_0)):\n'
        cne__omgo += '        w_ind = row_to_group[i]\n'
        cne__omgo += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    qeux__iegzi = {}
    exec(cne__omgo, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, qeux__iegzi)
    return qeux__iegzi['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    zadl__wazq = udf_func_struct.var_typs
    krvem__ftec = len(zadl__wazq)
    exxs__monj = n_keys
    redvar_offsets = []
    guz__xbhxe = []
    pwfca__stw = []
    for akdm__jedsr, reibc__pmwg in enumerate(allfuncs):
        if reibc__pmwg.ftype != 'udf':
            exxs__monj += reibc__pmwg.ncols_post_shuffle
        else:
            guz__xbhxe.append(exxs__monj)
            redvar_offsets += list(range(exxs__monj + 1, exxs__monj + 1 +
                reibc__pmwg.n_redvars))
            exxs__monj += 1 + reibc__pmwg.n_redvars
            pwfca__stw.append(out_data_typs_[akdm__jedsr])
    assert len(redvar_offsets) == krvem__ftec
    wxl__unil = len(pwfca__stw)
    cne__omgo = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    cne__omgo += '    if is_null_pointer(table):\n'
    cne__omgo += '        return\n'
    cne__omgo += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in zadl__wazq]), 
        ',' if len(zadl__wazq) == 1 else '')
    cne__omgo += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        pwfca__stw]), ',' if len(pwfca__stw) == 1 else '')
    for akdm__jedsr in range(krvem__ftec):
        cne__omgo += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(akdm__jedsr, redvar_offsets[akdm__jedsr], akdm__jedsr))
        cne__omgo += '    incref(redvar_arr_{})\n'.format(akdm__jedsr)
    cne__omgo += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(akdm__jedsr) for akdm__jedsr in range(krvem__ftec)]), ',' if
        krvem__ftec == 1 else '')
    cne__omgo += '\n'
    for akdm__jedsr in range(wxl__unil):
        cne__omgo += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(akdm__jedsr, guz__xbhxe[akdm__jedsr], akdm__jedsr))
        cne__omgo += '    incref(data_out_{})\n'.format(akdm__jedsr)
    cne__omgo += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(akdm__jedsr) for akdm__jedsr in range(wxl__unil)]), ',' if 
        wxl__unil == 1 else '')
    cne__omgo += '\n'
    cne__omgo += '    for i in range(len(data_out_0)):\n'
    cne__omgo += '        __eval_res(redvars, data_out, i)\n'
    qeux__iegzi = {}
    exec(cne__omgo, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, qeux__iegzi)
    return qeux__iegzi['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    exxs__monj = n_keys
    vihvg__tun = []
    for akdm__jedsr, reibc__pmwg in enumerate(allfuncs):
        if reibc__pmwg.ftype == 'gen_udf':
            vihvg__tun.append(exxs__monj)
            exxs__monj += 1
        elif reibc__pmwg.ftype != 'udf':
            exxs__monj += reibc__pmwg.ncols_post_shuffle
        else:
            exxs__monj += reibc__pmwg.n_redvars + 1
    cne__omgo = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    cne__omgo += '    if num_groups == 0:\n'
    cne__omgo += '        return\n'
    for akdm__jedsr, func in enumerate(udf_func_struct.general_udf_funcs):
        cne__omgo += '    # col {}\n'.format(akdm__jedsr)
        cne__omgo += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(vihvg__tun[akdm__jedsr], akdm__jedsr))
        cne__omgo += '    incref(out_col)\n'
        cne__omgo += '    for j in range(num_groups):\n'
        cne__omgo += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(akdm__jedsr, akdm__jedsr))
        cne__omgo += '        incref(in_col)\n'
        cne__omgo += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(akdm__jedsr))
    qqzl__vrp = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    mjubt__cudvk = 0
    for akdm__jedsr, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[mjubt__cudvk]
        qqzl__vrp['func_{}'.format(mjubt__cudvk)] = func
        qqzl__vrp['in_col_{}_typ'.format(mjubt__cudvk)] = in_col_typs[
            func_idx_to_in_col[akdm__jedsr]]
        qqzl__vrp['out_col_{}_typ'.format(mjubt__cudvk)] = out_col_typs[
            akdm__jedsr]
        mjubt__cudvk += 1
    qeux__iegzi = {}
    exec(cne__omgo, qqzl__vrp, qeux__iegzi)
    reibc__pmwg = qeux__iegzi['bodo_gb_apply_general_udfs{}'.format(
        label_suffix)]
    rwa__hlfqa = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(rwa__hlfqa, nopython=True)(reibc__pmwg)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    fiev__vkx = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        hdye__dett = []
        if agg_node.in_vars[0] is not None:
            hdye__dett.append('arg0')
        for akdm__jedsr in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if akdm__jedsr not in agg_node.dead_in_inds:
                hdye__dett.append(f'arg{akdm__jedsr}')
    else:
        hdye__dett = [f'arg{akdm__jedsr}' for akdm__jedsr, hjf__ssk in
            enumerate(agg_node.in_vars) if hjf__ssk is not None]
    cne__omgo = f"def agg_top({', '.join(hdye__dett)}):\n"
    imlbj__yhuxn = []
    if agg_node.is_in_table_format:
        imlbj__yhuxn = agg_node.in_key_inds + [dho__vcuv for dho__vcuv,
            ulw__asi in agg_node.gb_info_out.values() if dho__vcuv is not None]
        if agg_node.input_has_index:
            imlbj__yhuxn.append(agg_node.n_in_cols - 1)
        gpyl__xrwhm = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        dxe__afdmz = []
        for akdm__jedsr in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if akdm__jedsr in agg_node.dead_in_inds:
                dxe__afdmz.append('None')
            else:
                dxe__afdmz.append(f'arg{akdm__jedsr}')
        pgn__tolr = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        cne__omgo += f"""    table = py_data_to_cpp_table({pgn__tolr}, ({', '.join(dxe__afdmz)}{gpyl__xrwhm}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        pnx__ude = [f'arg{akdm__jedsr}' for akdm__jedsr in agg_node.in_key_inds
            ]
        fnxyf__ogu = [f'arg{dho__vcuv}' for dho__vcuv, ulw__asi in agg_node
            .gb_info_out.values() if dho__vcuv is not None]
        gmrgr__umhhb = pnx__ude + fnxyf__ogu
        if agg_node.input_has_index:
            gmrgr__umhhb.append(f'arg{len(agg_node.in_vars) - 1}')
        cne__omgo += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({qxqj__djzc})' for qxqj__djzc in gmrgr__umhhb))
        cne__omgo += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    rnbpf__bffsq = []
    func_idx_to_in_col = []
    zec__czsmb = []
    hvvf__cvzmp = False
    ksg__osejh = 1
    azihn__cunl = -1
    pevnz__bipy = 0
    xhj__khwpx = 0
    qnu__tren = [func for ulw__asi, func in agg_node.gb_info_out.values()]
    for akrl__cay, func in enumerate(qnu__tren):
        rnbpf__bffsq.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            pevnz__bipy += 1
        if hasattr(func, 'skipdropna'):
            hvvf__cvzmp = func.skipdropna
        if func.ftype == 'shift':
            ksg__osejh = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            xhj__khwpx = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            azihn__cunl = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(akrl__cay)
        if func.ftype == 'udf':
            zec__czsmb.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            zec__czsmb.append(0)
            do_combine = False
    rnbpf__bffsq.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if pevnz__bipy > 0:
        if pevnz__bipy != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    cju__npo = []
    if udf_func_struct is not None:
        edn__jwdj = next_label()
        if udf_func_struct.regular_udfs:
            rwa__hlfqa = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            bnay__gmed = numba.cfunc(rwa__hlfqa, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, edn__jwdj))
            nhnzm__zsc = numba.cfunc(rwa__hlfqa, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, edn__jwdj))
            clz__joxvq = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys,
                func_out_types, edn__jwdj))
            udf_func_struct.set_regular_cfuncs(bnay__gmed, nhnzm__zsc,
                clz__joxvq)
            for mww__ctc in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[mww__ctc.native_name] = mww__ctc
                gb_agg_cfunc_addr[mww__ctc.native_name] = mww__ctc.address
        if udf_func_struct.general_udfs:
            fwcb__lefy = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, func_out_types, func_idx_to_in_col,
                edn__jwdj)
            udf_func_struct.set_general_cfunc(fwcb__lefy)
        zadl__wazq = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        veb__tknwu = 0
        akdm__jedsr = 0
        for swdwp__hdo, reibc__pmwg in zip(agg_node.gb_info_out.keys(),
            allfuncs):
            if reibc__pmwg.ftype in ('udf', 'gen_udf'):
                cju__npo.append(out_col_typs[swdwp__hdo])
                for pbpya__mrdxl in range(veb__tknwu, veb__tknwu +
                    zec__czsmb[akdm__jedsr]):
                    cju__npo.append(dtype_to_array_type(zadl__wazq[
                        pbpya__mrdxl]))
                veb__tknwu += zec__czsmb[akdm__jedsr]
                akdm__jedsr += 1
        cne__omgo += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{akdm__jedsr}' for akdm__jedsr in range(len(cju__npo)))}{',' if len(cju__npo) == 1 else ''}))
"""
        cne__omgo += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(cju__npo)})
"""
        if udf_func_struct.regular_udfs:
            cne__omgo += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{bnay__gmed.native_name}')\n"
                )
            cne__omgo += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{nhnzm__zsc.native_name}')\n"
                )
            cne__omgo += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{clz__joxvq.native_name}')\n"
                )
            cne__omgo += (
                f"    cpp_cb_update_addr = get_agg_udf_addr('{bnay__gmed.native_name}')\n"
                )
            cne__omgo += (
                f"    cpp_cb_combine_addr = get_agg_udf_addr('{nhnzm__zsc.native_name}')\n"
                )
            cne__omgo += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{clz__joxvq.native_name}')\n"
                )
        else:
            cne__omgo += '    cpp_cb_update_addr = 0\n'
            cne__omgo += '    cpp_cb_combine_addr = 0\n'
            cne__omgo += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            mww__ctc = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[mww__ctc.native_name] = mww__ctc
            gb_agg_cfunc_addr[mww__ctc.native_name] = mww__ctc.address
            cne__omgo += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{mww__ctc.native_name}')\n"
                )
            cne__omgo += (
                f"    cpp_cb_general_addr = get_agg_udf_addr('{mww__ctc.native_name}')\n"
                )
        else:
            cne__omgo += '    cpp_cb_general_addr = 0\n'
    else:
        cne__omgo += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        cne__omgo += '    cpp_cb_update_addr = 0\n'
        cne__omgo += '    cpp_cb_combine_addr = 0\n'
        cne__omgo += '    cpp_cb_eval_addr = 0\n'
        cne__omgo += '    cpp_cb_general_addr = 0\n'
    cne__omgo += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(reibc__pmwg.ftype)) for
        reibc__pmwg in allfuncs] + ['0']))
    cne__omgo += (
        f'    func_offsets = np.array({str(rnbpf__bffsq)}, dtype=np.int32)\n')
    if len(zec__czsmb) > 0:
        cne__omgo += (
            f'    udf_ncols = np.array({str(zec__czsmb)}, dtype=np.int32)\n')
    else:
        cne__omgo += '    udf_ncols = np.array([0], np.int32)\n'
    cne__omgo += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    sjs__gham = (agg_node._num_shuffle_keys if agg_node._num_shuffle_keys !=
        -1 else n_keys)
    cne__omgo += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {hvvf__cvzmp}, {ksg__osejh}, {xhj__khwpx}, {azihn__cunl}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes, {sjs__gham})
"""
    fnhpb__lgdbt = []
    mgn__fqbw = 0
    if agg_node.return_key:
        yub__xizqz = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for akdm__jedsr in range(n_keys):
            pty__bbqv = yub__xizqz + akdm__jedsr
            fnhpb__lgdbt.append(pty__bbqv if pty__bbqv not in agg_node.
                dead_out_inds else -1)
            mgn__fqbw += 1
    for swdwp__hdo in agg_node.gb_info_out.keys():
        fnhpb__lgdbt.append(swdwp__hdo)
        mgn__fqbw += 1
    mast__vzjsd = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            fnhpb__lgdbt.append(agg_node.n_out_cols - 1)
        else:
            mast__vzjsd = True
    gpyl__xrwhm = ',' if fiev__vkx == 1 else ''
    qjq__ehw = (
        f"({', '.join(f'out_type{akdm__jedsr}' for akdm__jedsr in range(fiev__vkx))}{gpyl__xrwhm})"
        )
    lhdsn__hfy = []
    bmk__jcj = []
    for akdm__jedsr, t in enumerate(out_col_typs):
        if akdm__jedsr not in agg_node.dead_out_inds and type_has_unknown_cats(
            t):
            if akdm__jedsr in agg_node.gb_info_out:
                dho__vcuv = agg_node.gb_info_out[akdm__jedsr][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                hcbsx__yqo = akdm__jedsr - yub__xizqz
                dho__vcuv = agg_node.in_key_inds[hcbsx__yqo]
            bmk__jcj.append(akdm__jedsr)
            if (agg_node.is_in_table_format and dho__vcuv < agg_node.
                n_in_table_arrays):
                lhdsn__hfy.append(f'get_table_data(arg0, {dho__vcuv})')
            else:
                lhdsn__hfy.append(f'arg{dho__vcuv}')
    gpyl__xrwhm = ',' if len(lhdsn__hfy) == 1 else ''
    cne__omgo += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {qjq__ehw}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(lhdsn__hfy)}{gpyl__xrwhm}), unknown_cat_out_inds)
"""
    cne__omgo += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    cne__omgo += '    delete_table_decref_arrays(table)\n'
    cne__omgo += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for akdm__jedsr in range(n_keys):
            if fnhpb__lgdbt[akdm__jedsr] == -1:
                cne__omgo += (
                    f'    decref_table_array(out_table, {akdm__jedsr})\n')
    if mast__vzjsd:
        zexzl__vlnnf = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        cne__omgo += f'    decref_table_array(out_table, {zexzl__vlnnf})\n'
    cne__omgo += '    delete_table(out_table)\n'
    cne__omgo += '    ev_clean.finalize()\n'
    cne__omgo += '    return out_data\n'
    kyd__lgcp = {f'out_type{akdm__jedsr}': out_var_types[akdm__jedsr] for
        akdm__jedsr in range(fiev__vkx)}
    kyd__lgcp['out_col_inds'] = MetaType(tuple(fnhpb__lgdbt))
    kyd__lgcp['in_col_inds'] = MetaType(tuple(imlbj__yhuxn))
    kyd__lgcp['cpp_table_to_py_data'] = cpp_table_to_py_data
    kyd__lgcp['py_data_to_cpp_table'] = py_data_to_cpp_table
    kyd__lgcp.update({f'udf_type{akdm__jedsr}': t for akdm__jedsr, t in
        enumerate(cju__npo)})
    kyd__lgcp['udf_dummy_col_inds'] = MetaType(tuple(range(len(cju__npo))))
    kyd__lgcp['create_dummy_table'] = create_dummy_table
    kyd__lgcp['unknown_cat_out_inds'] = MetaType(tuple(bmk__jcj))
    kyd__lgcp['get_table_data'] = bodo.hiframes.table.get_table_data
    return cne__omgo, kyd__lgcp


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    bfu__akty = tuple(unwrap_typeref(data_types.types[akdm__jedsr]) for
        akdm__jedsr in range(len(data_types.types)))
    pia__rou = bodo.TableType(bfu__akty)
    kyd__lgcp = {'table_type': pia__rou}
    cne__omgo = 'def impl(data_types):\n'
    cne__omgo += '  py_table = init_table(table_type, False)\n'
    cne__omgo += '  py_table = set_table_len(py_table, 1)\n'
    for lzbku__myeg, tcah__lfjp in pia__rou.type_to_blk.items():
        kyd__lgcp[f'typ_list_{tcah__lfjp}'] = types.List(lzbku__myeg)
        kyd__lgcp[f'typ_{tcah__lfjp}'] = lzbku__myeg
        qvjm__jpbpb = len(pia__rou.block_to_arr_ind[tcah__lfjp])
        cne__omgo += f"""  arr_list_{tcah__lfjp} = alloc_list_like(typ_list_{tcah__lfjp}, {qvjm__jpbpb}, False)
"""
        cne__omgo += f'  for i in range(len(arr_list_{tcah__lfjp})):\n'
        cne__omgo += (
            f'    arr_list_{tcah__lfjp}[i] = alloc_type(1, typ_{tcah__lfjp}, (-1,))\n'
            )
        cne__omgo += f"""  py_table = set_table_block(py_table, arr_list_{tcah__lfjp}, {tcah__lfjp})
"""
    cne__omgo += '  return py_table\n'
    kyd__lgcp.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    qeux__iegzi = {}
    exec(cne__omgo, kyd__lgcp, qeux__iegzi)
    return qeux__iegzi['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    gghrg__prk = agg_node.in_vars[0].name
    rdt__wqpo, hzso__udp, dqfi__qkn = block_use_map[gghrg__prk]
    if hzso__udp or dqfi__qkn:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        hworl__gdpur, qgbdc__uaanx, gsz__ryif = _compute_table_column_uses(
            agg_node.out_vars[0].name, table_col_use_map, equiv_vars)
        if qgbdc__uaanx or gsz__ryif:
            hworl__gdpur = set(range(agg_node.n_out_table_arrays))
    else:
        hworl__gdpur = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            hworl__gdpur = {0}
    jqkwp__xnzne = set(akdm__jedsr for akdm__jedsr in agg_node.in_key_inds if
        akdm__jedsr < agg_node.n_in_table_arrays)
    yzu__tbedi = set(agg_node.gb_info_out[akdm__jedsr][0] for akdm__jedsr in
        hworl__gdpur if akdm__jedsr in agg_node.gb_info_out and agg_node.
        gb_info_out[akdm__jedsr][0] is not None)
    yzu__tbedi |= jqkwp__xnzne | rdt__wqpo
    cxjw__uqlh = len(set(range(agg_node.n_in_table_arrays)) - yzu__tbedi) == 0
    block_use_map[gghrg__prk] = yzu__tbedi, cxjw__uqlh, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    aaywe__miq = agg_node.n_out_table_arrays
    pkn__izss = agg_node.out_vars[0].name
    pvj__ybix = _find_used_columns(pkn__izss, aaywe__miq, column_live_map,
        equiv_vars)
    if pvj__ybix is None:
        return False
    uoy__ndfn = set(range(aaywe__miq)) - pvj__ybix
    onecq__kwdq = len(uoy__ndfn - agg_node.dead_out_inds) != 0
    if onecq__kwdq:
        agg_node.dead_out_inds.update(uoy__ndfn)
        agg_node.update_dead_col_info()
    return onecq__kwdq


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for litve__voj in block.body:
            if is_call_assign(litve__voj) and find_callname(f_ir,
                litve__voj.value) == ('len', 'builtins'
                ) and litve__voj.value.args[0].name == f_ir.arg_names[0]:
                lsdbs__trqxv = get_definition(f_ir, litve__voj.value.func)
                lsdbs__trqxv.name = 'dummy_agg_count'
                lsdbs__trqxv.value = dummy_agg_count
    eglb__xeit = get_name_var_table(f_ir.blocks)
    ljqn__qpmm = {}
    for name, ulw__asi in eglb__xeit.items():
        ljqn__qpmm[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, ljqn__qpmm)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    jdpg__aqsj = numba.core.compiler.Flags()
    jdpg__aqsj.nrt = True
    msuuz__wlhf = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, jdpg__aqsj)
    msuuz__wlhf.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, vgw__kiw, calltypes, ulw__asi = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    mysk__rboyf = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    gahgi__gjsk = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    mioe__nubf = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    yqohw__dgm = mioe__nubf(typemap, calltypes)
    pm = gahgi__gjsk(typingctx, targetctx, None, f_ir, typemap, vgw__kiw,
        calltypes, yqohw__dgm, {}, jdpg__aqsj, None)
    due__ofi = numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline(
        pm)
    pm = gahgi__gjsk(typingctx, targetctx, None, f_ir, typemap, vgw__kiw,
        calltypes, yqohw__dgm, {}, jdpg__aqsj, due__ofi)
    vcphd__bwji = numba.core.typed_passes.InlineOverloads()
    vcphd__bwji.run_pass(pm)
    bae__gvbx = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    bae__gvbx.run()
    for block in f_ir.blocks.values():
        for litve__voj in block.body:
            if is_assign(litve__voj) and isinstance(litve__voj.value, (ir.
                Arg, ir.Var)) and isinstance(typemap[litve__voj.target.name
                ], SeriesType):
                lzbku__myeg = typemap.pop(litve__voj.target.name)
                typemap[litve__voj.target.name] = lzbku__myeg.data
            if is_call_assign(litve__voj) and find_callname(f_ir,
                litve__voj.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[litve__voj.target.name].remove(litve__voj
                    .value)
                litve__voj.value = litve__voj.value.args[0]
                f_ir._definitions[litve__voj.target.name].append(litve__voj
                    .value)
            if is_call_assign(litve__voj) and find_callname(f_ir,
                litve__voj.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[litve__voj.target.name].remove(litve__voj
                    .value)
                litve__voj.value = ir.Const(False, litve__voj.loc)
                f_ir._definitions[litve__voj.target.name].append(litve__voj
                    .value)
            if is_call_assign(litve__voj) and find_callname(f_ir,
                litve__voj.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[litve__voj.target.name].remove(litve__voj
                    .value)
                litve__voj.value = ir.Const(False, litve__voj.loc)
                f_ir._definitions[litve__voj.target.name].append(litve__voj
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    mnwc__gro = numba.parfors.parfor.PreParforPass(f_ir, typemap, calltypes,
        typingctx, targetctx, mysk__rboyf)
    mnwc__gro.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    jru__dlql = numba.core.compiler.StateDict()
    jru__dlql.func_ir = f_ir
    jru__dlql.typemap = typemap
    jru__dlql.calltypes = calltypes
    jru__dlql.typingctx = typingctx
    jru__dlql.targetctx = targetctx
    jru__dlql.return_type = vgw__kiw
    numba.core.rewrites.rewrite_registry.apply('after-inference', jru__dlql)
    gfth__ydsow = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        vgw__kiw, typingctx, targetctx, mysk__rboyf, jdpg__aqsj, {})
    gfth__ydsow.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            avrn__pbkw = ctypes.pythonapi.PyCell_Get
            avrn__pbkw.restype = ctypes.py_object
            avrn__pbkw.argtypes = ctypes.py_object,
            mtxyb__txn = tuple(avrn__pbkw(dhnd__sqy) for dhnd__sqy in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            mtxyb__txn = closure.items
        assert len(code.co_freevars) == len(mtxyb__txn)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, mtxyb__txn
            )


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
        dbtrc__pfmz = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array
            (in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (dbtrc__pfmz,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        ogs__rlue, arr_var = _rm_arg_agg_block(block, pm.typemap)
        xdtd__ppdd = -1
        for akdm__jedsr, litve__voj in enumerate(ogs__rlue):
            if isinstance(litve__voj, numba.parfors.parfor.Parfor):
                assert xdtd__ppdd == -1, 'only one parfor for aggregation function'
                xdtd__ppdd = akdm__jedsr
        parfor = None
        if xdtd__ppdd != -1:
            parfor = ogs__rlue[xdtd__ppdd]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = ogs__rlue[:xdtd__ppdd] + parfor.init_block.body
        eval_nodes = ogs__rlue[xdtd__ppdd + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for litve__voj in init_nodes:
            if is_assign(litve__voj) and litve__voj.target.name in redvars:
                ind = redvars.index(litve__voj.target.name)
                reduce_vars[ind] = litve__voj.target
        var_types = [pm.typemap[hjf__ssk] for hjf__ssk in redvars]
        dek__jzy = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        pwf__taf = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        camk__kirb = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(camk__kirb)
        self.all_update_funcs.append(pwf__taf)
        self.all_combine_funcs.append(dek__jzy)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        hzlnj__horv = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        ombl__miia = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        jmbfx__ozsr = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        acll__wone = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets
            )
        return (self.all_vartypes, hzlnj__horv, ombl__miia, jmbfx__ozsr,
            acll__wone)


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
    lhjdt__uvue = []
    for t, reibc__pmwg in zip(in_col_types, agg_func):
        lhjdt__uvue.append((t, reibc__pmwg))
    ftatu__uvew = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    pki__laq = GeneralUDFGenerator()
    for in_col_typ, func in lhjdt__uvue:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            ftatu__uvew.add_udf(in_col_typ, func)
        except:
            pki__laq.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = ftatu__uvew.gen_all_func()
    general_udf_funcs = pki__laq.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    hgatd__kkpay = compute_use_defs(parfor.loop_body)
    qzqh__pluor = set()
    for vxjwa__rrj in hgatd__kkpay.usemap.values():
        qzqh__pluor |= vxjwa__rrj
    boxda__ynbux = set()
    for vxjwa__rrj in hgatd__kkpay.defmap.values():
        boxda__ynbux |= vxjwa__rrj
    wfg__pkpe = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    wfg__pkpe.body = eval_nodes
    ijcq__fjv = compute_use_defs({(0): wfg__pkpe})
    gxaa__xfod = ijcq__fjv.usemap[0]
    uhxb__zazc = set()
    uond__xrz = []
    zwxs__icu = []
    for litve__voj in reversed(init_nodes):
        omit__stl = {hjf__ssk.name for hjf__ssk in litve__voj.list_vars()}
        if is_assign(litve__voj):
            hjf__ssk = litve__voj.target.name
            omit__stl.remove(hjf__ssk)
            if (hjf__ssk in qzqh__pluor and hjf__ssk not in uhxb__zazc and 
                hjf__ssk not in gxaa__xfod and hjf__ssk not in boxda__ynbux):
                zwxs__icu.append(litve__voj)
                qzqh__pluor |= omit__stl
                boxda__ynbux.add(hjf__ssk)
                continue
        uhxb__zazc |= omit__stl
        uond__xrz.append(litve__voj)
    zwxs__icu.reverse()
    uond__xrz.reverse()
    ulmy__ygolx = min(parfor.loop_body.keys())
    wupzg__xadku = parfor.loop_body[ulmy__ygolx]
    wupzg__xadku.body = zwxs__icu + wupzg__xadku.body
    return uond__xrz


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    bwk__tcyj = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    kiqj__ajzja = set()
    xuq__oxdnr = []
    for litve__voj in init_nodes:
        if is_assign(litve__voj) and isinstance(litve__voj.value, ir.Global
            ) and isinstance(litve__voj.value.value, pytypes.FunctionType
            ) and litve__voj.value.value in bwk__tcyj:
            kiqj__ajzja.add(litve__voj.target.name)
        elif is_call_assign(litve__voj
            ) and litve__voj.value.func.name in kiqj__ajzja:
            pass
        else:
            xuq__oxdnr.append(litve__voj)
    init_nodes = xuq__oxdnr
    zzgf__bmff = types.Tuple(var_types)
    aru__lbj = lambda : None
    f_ir = compile_to_numba_ir(aru__lbj, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    azzue__jrjl = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    mczl__deiw = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        azzue__jrjl, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [mczl__deiw] + block.body
    block.body[-2].value.value = azzue__jrjl
    alndd__sat = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        zzgf__bmff, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xke__udkm = numba.core.target_extension.dispatcher_registry[cpu_target](
        aru__lbj)
    xke__udkm.add_overload(alndd__sat)
    return xke__udkm


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    xyxpc__czldh = len(update_funcs)
    avm__lxh = len(in_col_types)
    cne__omgo = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for pbpya__mrdxl in range(xyxpc__czldh):
        payre__bncw = ', '.join(['redvar_arrs[{}][w_ind]'.format(
            akdm__jedsr) for akdm__jedsr in range(redvar_offsets[
            pbpya__mrdxl], redvar_offsets[pbpya__mrdxl + 1])])
        if payre__bncw:
            cne__omgo += '  {} = update_vars_{}({},  data_in[{}][i])\n'.format(
                payre__bncw, pbpya__mrdxl, payre__bncw, 0 if avm__lxh == 1 else
                pbpya__mrdxl)
    cne__omgo += '  return\n'
    qqzl__vrp = {}
    for akdm__jedsr, reibc__pmwg in enumerate(update_funcs):
        qqzl__vrp['update_vars_{}'.format(akdm__jedsr)] = reibc__pmwg
    qeux__iegzi = {}
    exec(cne__omgo, qqzl__vrp, qeux__iegzi)
    hgne__dnzxw = qeux__iegzi['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(hgne__dnzxw)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    kln__ugwf = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types])
    arg_typs = kln__ugwf, kln__ugwf, types.intp, types.intp
    wjjtz__ljes = len(redvar_offsets) - 1
    cne__omgo = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for pbpya__mrdxl in range(wjjtz__ljes):
        payre__bncw = ', '.join(['redvar_arrs[{}][w_ind]'.format(
            akdm__jedsr) for akdm__jedsr in range(redvar_offsets[
            pbpya__mrdxl], redvar_offsets[pbpya__mrdxl + 1])])
        mesc__uuchv = ', '.join(['recv_arrs[{}][i]'.format(akdm__jedsr) for
            akdm__jedsr in range(redvar_offsets[pbpya__mrdxl],
            redvar_offsets[pbpya__mrdxl + 1])])
        if mesc__uuchv:
            cne__omgo += '  {} = combine_vars_{}({}, {})\n'.format(payre__bncw,
                pbpya__mrdxl, payre__bncw, mesc__uuchv)
    cne__omgo += '  return\n'
    qqzl__vrp = {}
    for akdm__jedsr, reibc__pmwg in enumerate(combine_funcs):
        qqzl__vrp['combine_vars_{}'.format(akdm__jedsr)] = reibc__pmwg
    qeux__iegzi = {}
    exec(cne__omgo, qqzl__vrp, qeux__iegzi)
    pksi__empnx = qeux__iegzi['combine_all_f']
    f_ir = compile_to_numba_ir(pksi__empnx, qqzl__vrp)
    jmbfx__ozsr = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xke__udkm = numba.core.target_extension.dispatcher_registry[cpu_target](
        pksi__empnx)
    xke__udkm.add_overload(jmbfx__ozsr)
    return xke__udkm


def gen_all_eval_func(eval_funcs, redvar_offsets):
    wjjtz__ljes = len(redvar_offsets) - 1
    cne__omgo = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for pbpya__mrdxl in range(wjjtz__ljes):
        payre__bncw = ', '.join(['redvar_arrs[{}][j]'.format(akdm__jedsr) for
            akdm__jedsr in range(redvar_offsets[pbpya__mrdxl],
            redvar_offsets[pbpya__mrdxl + 1])])
        cne__omgo += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
            pbpya__mrdxl, pbpya__mrdxl, payre__bncw)
    cne__omgo += '  return\n'
    qqzl__vrp = {}
    for akdm__jedsr, reibc__pmwg in enumerate(eval_funcs):
        qqzl__vrp['eval_vars_{}'.format(akdm__jedsr)] = reibc__pmwg
    qeux__iegzi = {}
    exec(cne__omgo, qqzl__vrp, qeux__iegzi)
    uoqai__npxb = qeux__iegzi['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(uoqai__npxb)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    aqg__cei = len(var_types)
    cwuxx__dcvcy = [f'in{akdm__jedsr}' for akdm__jedsr in range(aqg__cei)]
    zzgf__bmff = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    aohrn__cjte = zzgf__bmff(0)
    cne__omgo = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        cwuxx__dcvcy))
    qeux__iegzi = {}
    exec(cne__omgo, {'_zero': aohrn__cjte}, qeux__iegzi)
    kkhwn__eta = qeux__iegzi['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(kkhwn__eta, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': aohrn__cjte}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    xnn__ekov = []
    for akdm__jedsr, hjf__ssk in enumerate(reduce_vars):
        xnn__ekov.append(ir.Assign(block.body[akdm__jedsr].target, hjf__ssk,
            hjf__ssk.loc))
        for nsso__byv in hjf__ssk.versioned_names:
            xnn__ekov.append(ir.Assign(hjf__ssk, ir.Var(hjf__ssk.scope,
                nsso__byv, hjf__ssk.loc), hjf__ssk.loc))
    block.body = block.body[:aqg__cei] + xnn__ekov + eval_nodes
    camk__kirb = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        zzgf__bmff, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xke__udkm = numba.core.target_extension.dispatcher_registry[cpu_target](
        kkhwn__eta)
    xke__udkm.add_overload(camk__kirb)
    return xke__udkm


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    aqg__cei = len(redvars)
    cximn__urxt = [f'v{akdm__jedsr}' for akdm__jedsr in range(aqg__cei)]
    cwuxx__dcvcy = [f'in{akdm__jedsr}' for akdm__jedsr in range(aqg__cei)]
    cne__omgo = 'def agg_combine({}):\n'.format(', '.join(cximn__urxt +
        cwuxx__dcvcy))
    hvnp__hom = wrap_parfor_blocks(parfor)
    heufy__etp = find_topo_order(hvnp__hom)
    heufy__etp = heufy__etp[1:]
    unwrap_parfor_blocks(parfor)
    yqoht__fcvaf = {}
    vsefh__addur = []
    for hxhxz__ecqu in heufy__etp:
        tnyw__kmthe = parfor.loop_body[hxhxz__ecqu]
        for litve__voj in tnyw__kmthe.body:
            if is_assign(litve__voj) and litve__voj.target.name in redvars:
                fup__howcj = litve__voj.target.name
                ind = redvars.index(fup__howcj)
                if ind in vsefh__addur:
                    continue
                if len(f_ir._definitions[fup__howcj]) == 2:
                    var_def = f_ir._definitions[fup__howcj][0]
                    cne__omgo += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[fup__howcj][1]
                    cne__omgo += _match_reduce_def(var_def, f_ir, ind)
    cne__omgo += '    return {}'.format(', '.join(['v{}'.format(akdm__jedsr
        ) for akdm__jedsr in range(aqg__cei)]))
    qeux__iegzi = {}
    exec(cne__omgo, {}, qeux__iegzi)
    iym__btz = qeux__iegzi['agg_combine']
    arg_typs = tuple(2 * var_types)
    qqzl__vrp = {'numba': numba, 'bodo': bodo, 'np': np}
    qqzl__vrp.update(yqoht__fcvaf)
    f_ir = compile_to_numba_ir(iym__btz, qqzl__vrp, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    zzgf__bmff = pm.typemap[block.body[-1].value.name]
    dek__jzy = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        zzgf__bmff, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xke__udkm = numba.core.target_extension.dispatcher_registry[cpu_target](
        iym__btz)
    xke__udkm.add_overload(dek__jzy)
    return xke__udkm


def _match_reduce_def(var_def, f_ir, ind):
    cne__omgo = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        cne__omgo = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        wgkz__lxt = guard(find_callname, f_ir, var_def)
        if wgkz__lxt == ('min', 'builtins'):
            cne__omgo = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if wgkz__lxt == ('max', 'builtins'):
            cne__omgo = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return cne__omgo


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    aqg__cei = len(redvars)
    xlp__bxojk = 1
    in_vars = []
    for akdm__jedsr in range(xlp__bxojk):
        nfptm__fwlx = ir.Var(arr_var.scope, f'$input{akdm__jedsr}', arr_var.loc
            )
        in_vars.append(nfptm__fwlx)
    cupat__qmzr = parfor.loop_nests[0].index_variable
    nap__khuli = [0] * aqg__cei
    for tnyw__kmthe in parfor.loop_body.values():
        owe__ahpuj = []
        for litve__voj in tnyw__kmthe.body:
            if is_var_assign(litve__voj
                ) and litve__voj.value.name == cupat__qmzr.name:
                continue
            if is_getitem(litve__voj
                ) and litve__voj.value.value.name == arr_var.name:
                litve__voj.value = in_vars[0]
            if is_call_assign(litve__voj) and guard(find_callname, pm.
                func_ir, litve__voj.value) == ('isna',
                'bodo.libs.array_kernels') and litve__voj.value.args[0
                ].name == arr_var.name:
                litve__voj.value = ir.Const(False, litve__voj.target.loc)
            if is_assign(litve__voj) and litve__voj.target.name in redvars:
                ind = redvars.index(litve__voj.target.name)
                nap__khuli[ind] = litve__voj.target
            owe__ahpuj.append(litve__voj)
        tnyw__kmthe.body = owe__ahpuj
    cximn__urxt = ['v{}'.format(akdm__jedsr) for akdm__jedsr in range(aqg__cei)
        ]
    cwuxx__dcvcy = ['in{}'.format(akdm__jedsr) for akdm__jedsr in range(
        xlp__bxojk)]
    cne__omgo = 'def agg_update({}):\n'.format(', '.join(cximn__urxt +
        cwuxx__dcvcy))
    cne__omgo += '    __update_redvars()\n'
    cne__omgo += '    return {}'.format(', '.join(['v{}'.format(akdm__jedsr
        ) for akdm__jedsr in range(aqg__cei)]))
    qeux__iegzi = {}
    exec(cne__omgo, {}, qeux__iegzi)
    rytu__vrcg = qeux__iegzi['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * xlp__bxojk)
    f_ir = compile_to_numba_ir(rytu__vrcg, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    pen__ofr = f_ir.blocks.popitem()[1].body
    zzgf__bmff = pm.typemap[pen__ofr[-1].value.name]
    hvnp__hom = wrap_parfor_blocks(parfor)
    heufy__etp = find_topo_order(hvnp__hom)
    heufy__etp = heufy__etp[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    wupzg__xadku = f_ir.blocks[heufy__etp[0]]
    rhmai__efw = f_ir.blocks[heufy__etp[-1]]
    dthgd__ysl = pen__ofr[:aqg__cei + xlp__bxojk]
    if aqg__cei > 1:
        eusle__gul = pen__ofr[-3:]
        assert is_assign(eusle__gul[0]) and isinstance(eusle__gul[0].value,
            ir.Expr) and eusle__gul[0].value.op == 'build_tuple'
    else:
        eusle__gul = pen__ofr[-2:]
    for akdm__jedsr in range(aqg__cei):
        fubpd__ikgh = pen__ofr[akdm__jedsr].target
        dkhyn__rqdp = ir.Assign(fubpd__ikgh, nap__khuli[akdm__jedsr],
            fubpd__ikgh.loc)
        dthgd__ysl.append(dkhyn__rqdp)
    for akdm__jedsr in range(aqg__cei, aqg__cei + xlp__bxojk):
        fubpd__ikgh = pen__ofr[akdm__jedsr].target
        dkhyn__rqdp = ir.Assign(fubpd__ikgh, in_vars[akdm__jedsr - aqg__cei
            ], fubpd__ikgh.loc)
        dthgd__ysl.append(dkhyn__rqdp)
    wupzg__xadku.body = dthgd__ysl + wupzg__xadku.body
    szrs__ianni = []
    for akdm__jedsr in range(aqg__cei):
        fubpd__ikgh = pen__ofr[akdm__jedsr].target
        dkhyn__rqdp = ir.Assign(nap__khuli[akdm__jedsr], fubpd__ikgh,
            fubpd__ikgh.loc)
        szrs__ianni.append(dkhyn__rqdp)
    rhmai__efw.body += szrs__ianni + eusle__gul
    sqwz__ygojv = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        zzgf__bmff, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    xke__udkm = numba.core.target_extension.dispatcher_registry[cpu_target](
        rytu__vrcg)
    xke__udkm.add_overload(sqwz__ygojv)
    return xke__udkm


def _rm_arg_agg_block(block, typemap):
    ogs__rlue = []
    arr_var = None
    for akdm__jedsr, litve__voj in enumerate(block.body):
        if is_assign(litve__voj) and isinstance(litve__voj.value, ir.Arg):
            arr_var = litve__voj.target
            diqc__lgbve = typemap[arr_var.name]
            if not isinstance(diqc__lgbve, types.ArrayCompatible):
                ogs__rlue += block.body[akdm__jedsr + 1:]
                break
            ayuh__mkqjp = block.body[akdm__jedsr + 1]
            assert is_assign(ayuh__mkqjp) and isinstance(ayuh__mkqjp.value,
                ir.Expr
                ) and ayuh__mkqjp.value.op == 'getattr' and ayuh__mkqjp.value.attr == 'shape' and ayuh__mkqjp.value.value.name == arr_var.name
            nwpz__cbe = ayuh__mkqjp.target
            mxppp__ztwqm = block.body[akdm__jedsr + 2]
            assert is_assign(mxppp__ztwqm) and isinstance(mxppp__ztwqm.
                value, ir.Expr
                ) and mxppp__ztwqm.value.op == 'static_getitem' and mxppp__ztwqm.value.value.name == nwpz__cbe.name
            ogs__rlue += block.body[akdm__jedsr + 3:]
            break
        ogs__rlue.append(litve__voj)
    return ogs__rlue, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    hvnp__hom = wrap_parfor_blocks(parfor)
    heufy__etp = find_topo_order(hvnp__hom)
    heufy__etp = heufy__etp[1:]
    unwrap_parfor_blocks(parfor)
    for hxhxz__ecqu in reversed(heufy__etp):
        for litve__voj in reversed(parfor.loop_body[hxhxz__ecqu].body):
            if isinstance(litve__voj, ir.Assign) and (litve__voj.target.
                name in parfor_params or litve__voj.target.name in var_to_param
                ):
                wle__urhj = litve__voj.target.name
                rhs = litve__voj.value
                appyg__zhk = (wle__urhj if wle__urhj in parfor_params else
                    var_to_param[wle__urhj])
                gsoef__jhl = []
                if isinstance(rhs, ir.Var):
                    gsoef__jhl = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    gsoef__jhl = [hjf__ssk.name for hjf__ssk in litve__voj.
                        value.list_vars()]
                param_uses[appyg__zhk].extend(gsoef__jhl)
                for hjf__ssk in gsoef__jhl:
                    var_to_param[hjf__ssk] = appyg__zhk
            if isinstance(litve__voj, Parfor):
                get_parfor_reductions(litve__voj, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for ggcjt__bkmqs, gsoef__jhl in param_uses.items():
        if ggcjt__bkmqs in gsoef__jhl and ggcjt__bkmqs not in reduce_varnames:
            reduce_varnames.append(ggcjt__bkmqs)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
