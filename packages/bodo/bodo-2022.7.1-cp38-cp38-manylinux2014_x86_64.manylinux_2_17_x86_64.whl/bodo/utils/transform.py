"""
Helper functions for transformations.
"""
import itertools
import math
import operator
import types as pytypes
from collections import namedtuple
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, types
from numba.core.ir_utils import GuardException, build_definitions, compile_to_numba_ir, compute_cfg_from_blocks, find_callname, find_const, get_definition, guard, is_setitem, mk_unique_var, replace_arg_nodes, require
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import fold_arguments
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoConstUpdatedError, BodoError, can_literalize_type, get_literal_value, get_overload_const_bool, get_overload_const_list, is_literal_type, is_overload_constant_bool
from bodo.utils.utils import is_array_typ, is_assign, is_call, is_expr
ReplaceFunc = namedtuple('ReplaceFunc', ['func', 'arg_types', 'args',
    'glbls', 'inline_bodo_calls', 'run_full_pipeline', 'pre_nodes'])
bodo_types_with_params = {'ArrayItemArrayType', 'CSRMatrixType',
    'CategoricalArrayType', 'CategoricalIndexType', 'DataFrameType',
    'DatetimeIndexType', 'Decimal128Type', 'DecimalArrayType',
    'IntegerArrayType', 'IntervalArrayType', 'IntervalIndexType', 'List',
    'MapArrayType', 'NumericIndexType', 'PDCategoricalDtype',
    'PeriodIndexType', 'RangeIndexType', 'SeriesType', 'StringIndexType',
    'BinaryIndexType', 'StructArrayType', 'TimedeltaIndexType',
    'TupleArrayType'}
container_update_method_names = ('clear', 'pop', 'popitem', 'update', 'add',
    'difference_update', 'discard', 'intersection_update', 'remove',
    'symmetric_difference_update', 'append', 'extend', 'insert', 'reverse',
    'sort')
no_side_effect_call_tuples = {(int,), (list,), (set,), (dict,), (min,), (
    max,), (abs,), (len,), (bool,), (str,), ('ceil', math), ('init_series',
    'pd_series_ext', 'hiframes', bodo), ('get_series_data', 'pd_series_ext',
    'hiframes', bodo), ('get_series_index', 'pd_series_ext', 'hiframes',
    bodo), ('get_series_name', 'pd_series_ext', 'hiframes', bodo), (
    'get_index_data', 'pd_index_ext', 'hiframes', bodo), ('get_index_name',
    'pd_index_ext', 'hiframes', bodo), ('init_binary_str_index',
    'pd_index_ext', 'hiframes', bodo), ('init_numeric_index',
    'pd_index_ext', 'hiframes', bodo), ('init_categorical_index',
    'pd_index_ext', 'hiframes', bodo), ('_dti_val_finalize', 'pd_index_ext',
    'hiframes', bodo), ('init_datetime_index', 'pd_index_ext', 'hiframes',
    bodo), ('init_timedelta_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_range_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_heter_index', 'pd_index_ext', 'hiframes', bodo), (
    'get_int_arr_data', 'int_arr_ext', 'libs', bodo), ('get_int_arr_bitmap',
    'int_arr_ext', 'libs', bodo), ('init_integer_array', 'int_arr_ext',
    'libs', bodo), ('alloc_int_array', 'int_arr_ext', 'libs', bodo), (
    'inplace_eq', 'str_arr_ext', 'libs', bodo), ('get_bool_arr_data',
    'bool_arr_ext', 'libs', bodo), ('get_bool_arr_bitmap', 'bool_arr_ext',
    'libs', bodo), ('init_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'alloc_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'datetime_date_arr_to_dt64_arr', 'pd_timestamp_ext', 'hiframes', bodo),
    (bodo.libs.bool_arr_ext.compute_or_body,), (bodo.libs.bool_arr_ext.
    compute_and_body,), ('alloc_datetime_date_array', 'datetime_date_ext',
    'hiframes', bodo), ('alloc_datetime_timedelta_array',
    'datetime_timedelta_ext', 'hiframes', bodo), ('cat_replace',
    'pd_categorical_ext', 'hiframes', bodo), ('init_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('alloc_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('get_categorical_arr_codes',
    'pd_categorical_ext', 'hiframes', bodo), ('_sum_handle_nan',
    'series_kernels', 'hiframes', bodo), ('_box_cat_val', 'series_kernels',
    'hiframes', bodo), ('_mean_handle_nan', 'series_kernels', 'hiframes',
    bodo), ('_var_handle_mincount', 'series_kernels', 'hiframes', bodo), (
    '_compute_var_nan_count_ddof', 'series_kernels', 'hiframes', bodo), (
    '_sem_handle_nan', 'series_kernels', 'hiframes', bodo), ('dist_return',
    'distributed_api', 'libs', bodo), ('rep_return', 'distributed_api',
    'libs', bodo), ('init_dataframe', 'pd_dataframe_ext', 'hiframes', bodo),
    ('get_dataframe_data', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_all_data', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_table', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_column_names', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_table_data', 'table', 'hiframes', bodo), ('get_dataframe_index',
    'pd_dataframe_ext', 'hiframes', bodo), ('init_rolling',
    'pd_rolling_ext', 'hiframes', bodo), ('init_groupby', 'pd_groupby_ext',
    'hiframes', bodo), ('calc_nitems', 'array_kernels', 'libs', bodo), (
    'concat', 'array_kernels', 'libs', bodo), ('unique', 'array_kernels',
    'libs', bodo), ('nunique', 'array_kernels', 'libs', bodo), ('quantile',
    'array_kernels', 'libs', bodo), ('explode', 'array_kernels', 'libs',
    bodo), ('explode_no_index', 'array_kernels', 'libs', bodo), (
    'get_arr_lens', 'array_kernels', 'libs', bodo), (
    'str_arr_from_sequence', 'str_arr_ext', 'libs', bodo), (
    'get_str_arr_str_length', 'str_arr_ext', 'libs', bodo), (
    'parse_datetime_str', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_dt64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'dt64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'timedelta64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_timedelta64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'npy_datetimestruct_to_datetime', 'pd_timestamp_ext', 'hiframes', bodo),
    ('isna', 'array_kernels', 'libs', bodo), ('copy',), (
    'from_iterable_impl', 'typing', 'utils', bodo), ('chain', itertools), (
    'groupby',), ('rolling',), (pd.CategoricalDtype,), (bodo.hiframes.
    pd_categorical_ext.get_code_for_value,), ('asarray', np), ('int32', np),
    ('int64', np), ('float64', np), ('float32', np), ('bool_', np), ('full',
    np), ('round', np), ('isnan', np), ('isnat', np), ('arange', np), (
    'internal_prange', 'parfor', numba), ('internal_prange', 'parfor',
    'parfors', numba), ('empty_inferred', 'ndarray', 'unsafe', numba), (
    '_slice_span', 'unicode', numba), ('_normalize_slice', 'unicode', numba
    ), ('init_session_builder', 'pyspark_ext', 'libs', bodo), (
    'init_session', 'pyspark_ext', 'libs', bodo), ('init_spark_df',
    'pyspark_ext', 'libs', bodo), ('h5size', 'h5_api', 'io', bodo), (
    'pre_alloc_struct_array', 'struct_arr_ext', 'libs', bodo), (bodo.libs.
    struct_arr_ext.pre_alloc_struct_array,), ('pre_alloc_tuple_array',
    'tuple_arr_ext', 'libs', bodo), (bodo.libs.tuple_arr_ext.
    pre_alloc_tuple_array,), ('pre_alloc_array_item_array',
    'array_item_arr_ext', 'libs', bodo), (bodo.libs.array_item_arr_ext.
    pre_alloc_array_item_array,), ('dist_reduce', 'distributed_api', 'libs',
    bodo), (bodo.libs.distributed_api.dist_reduce,), (
    'pre_alloc_string_array', 'str_arr_ext', 'libs', bodo), (bodo.libs.
    str_arr_ext.pre_alloc_string_array,), ('pre_alloc_binary_array',
    'binary_arr_ext', 'libs', bodo), (bodo.libs.binary_arr_ext.
    pre_alloc_binary_array,), ('pre_alloc_map_array', 'map_arr_ext', 'libs',
    bodo), (bodo.libs.map_arr_ext.pre_alloc_map_array,), (
    'convert_dict_arr_to_int', 'dict_arr_ext', 'libs', bodo), (
    'cat_dict_str', 'dict_arr_ext', 'libs', bodo), ('str_replace',
    'dict_arr_ext', 'libs', bodo), ('dict_arr_eq', 'dict_arr_ext', 'libs',
    bodo), ('dict_arr_ne', 'dict_arr_ext', 'libs', bodo), ('str_startswith',
    'dict_arr_ext', 'libs', bodo), ('str_endswith', 'dict_arr_ext', 'libs',
    bodo), ('str_contains_non_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_series_contains_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_capitalize', 'dict_arr_ext', 'libs', bodo), ('str_lower',
    'dict_arr_ext', 'libs', bodo), ('str_swapcase', 'dict_arr_ext', 'libs',
    bodo), ('str_title', 'dict_arr_ext', 'libs', bodo), ('str_upper',
    'dict_arr_ext', 'libs', bodo), ('str_center', 'dict_arr_ext', 'libs',
    bodo), ('str_get', 'dict_arr_ext', 'libs', bodo), ('str_repeat_int',
    'dict_arr_ext', 'libs', bodo), ('str_lstrip', 'dict_arr_ext', 'libs',
    bodo), ('str_rstrip', 'dict_arr_ext', 'libs', bodo), ('str_strip',
    'dict_arr_ext', 'libs', bodo), ('str_zfill', 'dict_arr_ext', 'libs',
    bodo), ('str_ljust', 'dict_arr_ext', 'libs', bodo), ('str_rjust',
    'dict_arr_ext', 'libs', bodo), ('str_find', 'dict_arr_ext', 'libs',
    bodo), ('str_rfind', 'dict_arr_ext', 'libs', bodo), ('str_slice',
    'dict_arr_ext', 'libs', bodo), ('str_extract', 'dict_arr_ext', 'libs',
    bodo), ('str_extractall', 'dict_arr_ext', 'libs', bodo), (
    'str_extractall_multi', 'dict_arr_ext', 'libs', bodo), ('str_len',
    'dict_arr_ext', 'libs', bodo), ('str_count', 'dict_arr_ext', 'libs',
    bodo), ('str_isalnum', 'dict_arr_ext', 'libs', bodo), ('str_isalpha',
    'dict_arr_ext', 'libs', bodo), ('str_isdigit', 'dict_arr_ext', 'libs',
    bodo), ('str_isspace', 'dict_arr_ext', 'libs', bodo), ('str_islower',
    'dict_arr_ext', 'libs', bodo), ('str_isupper', 'dict_arr_ext', 'libs',
    bodo), ('str_istitle', 'dict_arr_ext', 'libs', bodo), ('str_isnumeric',
    'dict_arr_ext', 'libs', bodo), ('str_isdecimal', 'dict_arr_ext', 'libs',
    bodo), ('str_match', 'dict_arr_ext', 'libs', bodo), ('prange', bodo), (
    bodo.prange,), ('objmode', bodo), (bodo.objmode,), (
    'get_label_dict_from_categories', 'pd_categorial_ext', 'hiframes', bodo
    ), ('get_label_dict_from_categories_no_duplicates', 'pd_categorial_ext',
    'hiframes', bodo), ('build_nullable_tuple', 'nullable_tuple_ext',
    'libs', bodo), ('generate_mappable_table_func', 'table_utils', 'utils',
    bodo), ('table_astype', 'table_utils', 'utils', bodo), ('table_concat',
    'table_utils', 'utils', bodo), ('table_filter', 'table', 'hiframes',
    bodo), ('table_subset', 'table', 'hiframes', bodo), (
    'logical_table_to_table', 'table', 'hiframes', bodo), ('startswith',),
    ('endswith',)}


def remove_hiframes(rhs, lives, call_list):
    vfmsb__kcx = tuple(call_list)
    if vfmsb__kcx in no_side_effect_call_tuples:
        return True
    if vfmsb__kcx == (bodo.hiframes.pd_index_ext.init_range_index,):
        return True
    if len(call_list) == 4 and call_list[1:] == ['conversion', 'utils', bodo]:
        return True
    if isinstance(call_list[-1], pytypes.ModuleType) and call_list[-1
        ].__name__ == 'bodosql':
        return True
    if len(call_list) == 2 and call_list[0] == 'copy':
        return True
    if call_list == ['h5read', 'h5_api', 'io', bodo] and rhs.args[5
        ].name not in lives:
        return True
    if call_list == ['move_str_binary_arr_payload', 'str_arr_ext', 'libs', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['setna', 'array_kernels', 'libs', bodo] and rhs.args[0
        ].name not in lives:
        return True
    if call_list == ['set_table_data', 'table', 'hiframes', bodo] and rhs.args[
        0].name not in lives:
        return True
    if call_list == ['set_table_data_null', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['ensure_column_unboxed', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives and rhs.args[1].name not in lives:
        return True
    if call_list == ['generate_table_nbytes', 'table_utils', 'utils', bodo
        ] and rhs.args[1].name not in lives:
        return True
    if len(vfmsb__kcx) == 1 and tuple in getattr(vfmsb__kcx[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        dcypx__wksf = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        dcypx__wksf = func.__globals__
    if extra_globals is not None:
        dcypx__wksf.update(extra_globals)
    if add_default_globals:
        dcypx__wksf.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd':
            pd, 'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, dcypx__wksf, typingctx=typing_info
            .typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[ywl__fxvt.name] for ywl__fxvt in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, dcypx__wksf)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        sgoj__ovuly = tuple(typing_info.typemap[ywl__fxvt.name] for
            ywl__fxvt in args)
        ihlw__wfv = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, sgoj__ovuly, {}, {}, flags)
        ihlw__wfv.run()
    brmhy__usenk = f_ir.blocks.popitem()[1]
    replace_arg_nodes(brmhy__usenk, args)
    yxw__zxaw = brmhy__usenk.body[:-2]
    update_locs(yxw__zxaw[len(args):], loc)
    for stmt in yxw__zxaw[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        mxy__rswru = brmhy__usenk.body[-2]
        assert is_assign(mxy__rswru) and is_expr(mxy__rswru.value, 'cast')
        cht__nyxl = mxy__rswru.value.value
        yxw__zxaw.append(ir.Assign(cht__nyxl, ret_var, loc))
    return yxw__zxaw


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for tyja__vdckn in stmt.list_vars():
            tyja__vdckn.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        xrrgo__jlgsg = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        xoo__rrr, bxcw__zcg = xrrgo__jlgsg(stmt)
        return bxcw__zcg
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        hyw__upx = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(hyw__upx, ir.UndefinedType):
            iqd__nobc = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{iqd__nobc}' is not defined", loc=loc)
    except GuardException as jmj__mkqnt:
        raise BodoError(err_msg, loc=loc)
    return hyw__upx


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    kehrg__coqlh = get_definition(func_ir, var)
    jcrzs__mmjq = None
    if typemap is not None:
        jcrzs__mmjq = typemap.get(var.name, None)
    if isinstance(kehrg__coqlh, ir.Arg) and arg_types is not None:
        jcrzs__mmjq = arg_types[kehrg__coqlh.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(jcrzs__mmjq):
        return get_literal_value(jcrzs__mmjq)
    if isinstance(kehrg__coqlh, (ir.Const, ir.Global, ir.FreeVar)):
        hyw__upx = kehrg__coqlh.value
        return hyw__upx
    if literalize_args and isinstance(kehrg__coqlh, ir.Arg
        ) and can_literalize_type(jcrzs__mmjq, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({kehrg__coqlh.index}, loc=
            var.loc, file_infos={kehrg__coqlh.index: file_info} if 
            file_info is not None else None)
    if is_expr(kehrg__coqlh, 'binop'):
        if file_info and kehrg__coqlh.fn == operator.add:
            try:
                myzw__dstnm = get_const_value_inner(func_ir, kehrg__coqlh.
                    lhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(myzw__dstnm, True)
                zxwa__bukn = get_const_value_inner(func_ir, kehrg__coqlh.
                    rhs, arg_types, typemap, updated_containers, file_info)
                return kehrg__coqlh.fn(myzw__dstnm, zxwa__bukn)
            except (GuardException, BodoConstUpdatedError) as jmj__mkqnt:
                pass
            try:
                zxwa__bukn = get_const_value_inner(func_ir, kehrg__coqlh.
                    rhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(zxwa__bukn, False)
                myzw__dstnm = get_const_value_inner(func_ir, kehrg__coqlh.
                    lhs, arg_types, typemap, updated_containers, file_info)
                return kehrg__coqlh.fn(myzw__dstnm, zxwa__bukn)
            except (GuardException, BodoConstUpdatedError) as jmj__mkqnt:
                pass
        myzw__dstnm = get_const_value_inner(func_ir, kehrg__coqlh.lhs,
            arg_types, typemap, updated_containers)
        zxwa__bukn = get_const_value_inner(func_ir, kehrg__coqlh.rhs,
            arg_types, typemap, updated_containers)
        return kehrg__coqlh.fn(myzw__dstnm, zxwa__bukn)
    if is_expr(kehrg__coqlh, 'unary'):
        hyw__upx = get_const_value_inner(func_ir, kehrg__coqlh.value,
            arg_types, typemap, updated_containers)
        return kehrg__coqlh.fn(hyw__upx)
    if is_expr(kehrg__coqlh, 'getattr') and typemap:
        nem__jzrk = typemap.get(kehrg__coqlh.value.name, None)
        if isinstance(nem__jzrk, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and kehrg__coqlh.attr == 'columns':
            return pd.Index(nem__jzrk.columns)
        if isinstance(nem__jzrk, types.SliceType):
            vaoyg__gxi = get_definition(func_ir, kehrg__coqlh.value)
            require(is_call(vaoyg__gxi))
            ocoyk__glgo = find_callname(func_ir, vaoyg__gxi)
            oqgku__laws = False
            if ocoyk__glgo == ('_normalize_slice', 'numba.cpython.unicode'):
                require(kehrg__coqlh.attr in ('start', 'step'))
                vaoyg__gxi = get_definition(func_ir, vaoyg__gxi.args[0])
                oqgku__laws = True
            require(find_callname(func_ir, vaoyg__gxi) == ('slice', 'builtins')
                )
            if len(vaoyg__gxi.args) == 1:
                if kehrg__coqlh.attr == 'start':
                    return 0
                if kehrg__coqlh.attr == 'step':
                    return 1
                require(kehrg__coqlh.attr == 'stop')
                return get_const_value_inner(func_ir, vaoyg__gxi.args[0],
                    arg_types, typemap, updated_containers)
            if kehrg__coqlh.attr == 'start':
                hyw__upx = get_const_value_inner(func_ir, vaoyg__gxi.args[0
                    ], arg_types, typemap, updated_containers)
                if hyw__upx is None:
                    hyw__upx = 0
                if oqgku__laws:
                    require(hyw__upx == 0)
                return hyw__upx
            if kehrg__coqlh.attr == 'stop':
                assert not oqgku__laws
                return get_const_value_inner(func_ir, vaoyg__gxi.args[1],
                    arg_types, typemap, updated_containers)
            require(kehrg__coqlh.attr == 'step')
            if len(vaoyg__gxi.args) == 2:
                return 1
            else:
                hyw__upx = get_const_value_inner(func_ir, vaoyg__gxi.args[2
                    ], arg_types, typemap, updated_containers)
                if hyw__upx is None:
                    hyw__upx = 1
                if oqgku__laws:
                    require(hyw__upx == 1)
                return hyw__upx
    if is_expr(kehrg__coqlh, 'getattr'):
        return getattr(get_const_value_inner(func_ir, kehrg__coqlh.value,
            arg_types, typemap, updated_containers), kehrg__coqlh.attr)
    if is_expr(kehrg__coqlh, 'getitem'):
        value = get_const_value_inner(func_ir, kehrg__coqlh.value,
            arg_types, typemap, updated_containers)
        index = get_const_value_inner(func_ir, kehrg__coqlh.index,
            arg_types, typemap, updated_containers)
        return value[index]
    vwu__yye = guard(find_callname, func_ir, kehrg__coqlh, typemap)
    if vwu__yye is not None and len(vwu__yye) == 2 and vwu__yye[0
        ] == 'keys' and isinstance(vwu__yye[1], ir.Var):
        eiukl__anfg = kehrg__coqlh.func
        kehrg__coqlh = get_definition(func_ir, vwu__yye[1])
        pfhy__xewjc = vwu__yye[1].name
        if updated_containers and pfhy__xewjc in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                pfhy__xewjc, updated_containers[pfhy__xewjc]))
        require(is_expr(kehrg__coqlh, 'build_map'))
        vals = [tyja__vdckn[0] for tyja__vdckn in kehrg__coqlh.items]
        jhw__jddew = guard(get_definition, func_ir, eiukl__anfg)
        assert isinstance(jhw__jddew, ir.Expr) and jhw__jddew.attr == 'keys'
        jhw__jddew.attr = 'copy'
        return [get_const_value_inner(func_ir, tyja__vdckn, arg_types,
            typemap, updated_containers) for tyja__vdckn in vals]
    if is_expr(kehrg__coqlh, 'build_map'):
        return {get_const_value_inner(func_ir, tyja__vdckn[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            tyja__vdckn[1], arg_types, typemap, updated_containers) for
            tyja__vdckn in kehrg__coqlh.items}
    if is_expr(kehrg__coqlh, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, tyja__vdckn, arg_types,
            typemap, updated_containers) for tyja__vdckn in kehrg__coqlh.items)
    if is_expr(kehrg__coqlh, 'build_list'):
        return [get_const_value_inner(func_ir, tyja__vdckn, arg_types,
            typemap, updated_containers) for tyja__vdckn in kehrg__coqlh.items]
    if is_expr(kehrg__coqlh, 'build_set'):
        return {get_const_value_inner(func_ir, tyja__vdckn, arg_types,
            typemap, updated_containers) for tyja__vdckn in kehrg__coqlh.items}
    if vwu__yye == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if vwu__yye == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers))
    if vwu__yye == ('range', 'builtins') and len(kehrg__coqlh.args) == 1:
        return range(get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers))
    if vwu__yye == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, tyja__vdckn,
            arg_types, typemap, updated_containers) for tyja__vdckn in
            kehrg__coqlh.args))
    if vwu__yye == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers))
    if vwu__yye == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers))
    if vwu__yye == ('format', 'builtins'):
        ywl__fxvt = get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers)
        wlbdh__drwjj = get_const_value_inner(func_ir, kehrg__coqlh.args[1],
            arg_types, typemap, updated_containers) if len(kehrg__coqlh.args
            ) > 1 else ''
        return format(ywl__fxvt, wlbdh__drwjj)
    if vwu__yye in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'),
        ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers))
    if vwu__yye == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers))
    if vwu__yye == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, kehrg__coqlh.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, kehrg__coqlh.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            kehrg__coqlh.args[2], arg_types, typemap, updated_containers))
    if vwu__yye == ('len', 'builtins') and typemap and isinstance(typemap.
        get(kehrg__coqlh.args[0].name, None), types.BaseTuple):
        return len(typemap[kehrg__coqlh.args[0].name])
    if vwu__yye == ('len', 'builtins'):
        eqqc__tnma = guard(get_definition, func_ir, kehrg__coqlh.args[0])
        if isinstance(eqqc__tnma, ir.Expr) and eqqc__tnma.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(eqqc__tnma.items)
        return len(get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers))
    if vwu__yye == ('CategoricalDtype', 'pandas'):
        kws = dict(kehrg__coqlh.kws)
        pzfsi__dyn = get_call_expr_arg('CategoricalDtype', kehrg__coqlh.
            args, kws, 0, 'categories', '')
        fslgq__etxiw = get_call_expr_arg('CategoricalDtype', kehrg__coqlh.
            args, kws, 1, 'ordered', False)
        if fslgq__etxiw is not False:
            fslgq__etxiw = get_const_value_inner(func_ir, fslgq__etxiw,
                arg_types, typemap, updated_containers)
        if pzfsi__dyn == '':
            pzfsi__dyn = None
        else:
            pzfsi__dyn = get_const_value_inner(func_ir, pzfsi__dyn,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(pzfsi__dyn, fslgq__etxiw)
    if vwu__yye == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, kehrg__coqlh.args[0],
            arg_types, typemap, updated_containers))
    if vwu__yye is not None and len(vwu__yye) == 2 and vwu__yye[1
        ] == 'pandas' and vwu__yye[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, vwu__yye[0])()
    if vwu__yye is not None and len(vwu__yye) == 2 and isinstance(vwu__yye[
        1], ir.Var):
        hyw__upx = get_const_value_inner(func_ir, vwu__yye[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, tyja__vdckn, arg_types,
            typemap, updated_containers) for tyja__vdckn in kehrg__coqlh.args]
        kws = {xfyq__wrvcb[0]: get_const_value_inner(func_ir, xfyq__wrvcb[1
            ], arg_types, typemap, updated_containers) for xfyq__wrvcb in
            kehrg__coqlh.kws}
        return getattr(hyw__upx, vwu__yye[0])(*args, **kws)
    if vwu__yye is not None and len(vwu__yye) == 2 and vwu__yye[1
        ] == 'bodo' and vwu__yye[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, tyja__vdckn, arg_types,
            typemap, updated_containers) for tyja__vdckn in kehrg__coqlh.args)
        kwargs = {iqd__nobc: get_const_value_inner(func_ir, tyja__vdckn,
            arg_types, typemap, updated_containers) for iqd__nobc,
            tyja__vdckn in dict(kehrg__coqlh.kws).items()}
        return getattr(bodo, vwu__yye[0])(*args, **kwargs)
    if is_call(kehrg__coqlh) and typemap and isinstance(typemap.get(
        kehrg__coqlh.func.name, None), types.Dispatcher):
        py_func = typemap[kehrg__coqlh.func.name].dispatcher.py_func
        require(kehrg__coqlh.vararg is None)
        args = tuple(get_const_value_inner(func_ir, tyja__vdckn, arg_types,
            typemap, updated_containers) for tyja__vdckn in kehrg__coqlh.args)
        kwargs = {iqd__nobc: get_const_value_inner(func_ir, tyja__vdckn,
            arg_types, typemap, updated_containers) for iqd__nobc,
            tyja__vdckn in dict(kehrg__coqlh.kws).items()}
        arg_types = tuple(bodo.typeof(tyja__vdckn) for tyja__vdckn in args)
        kw_types = {byrto__wpbii: bodo.typeof(tyja__vdckn) for byrto__wpbii,
            tyja__vdckn in kwargs.items()}
        require(_func_is_pure(py_func, arg_types, kw_types))
        return py_func(*args, **kwargs)
    raise GuardException('Constant value not found')


def _func_is_pure(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.ir.csv_ext import CsvReader
    from bodo.ir.json_ext import JsonReader
    from bodo.ir.parquet_ext import ParquetReader
    from bodo.ir.sql_ext import SqlReader
    f_ir, typemap, lpyts__arikk, lpyts__arikk = (bodo.compiler.
        get_func_type_info(py_func, arg_types, kw_types))
    for block in f_ir.blocks.values():
        for stmt in block.body:
            if isinstance(stmt, ir.Print):
                return False
            if isinstance(stmt, (CsvReader, JsonReader, ParquetReader,
                SqlReader)):
                return False
            if is_setitem(stmt) and isinstance(guard(get_definition, f_ir,
                stmt.target), ir.Arg):
                return False
            if is_assign(stmt):
                rhs = stmt.value
                if isinstance(rhs, ir.Yield):
                    return False
                if is_call(rhs):
                    lvu__xzzq = guard(get_definition, f_ir, rhs.func)
                    if isinstance(lvu__xzzq, ir.Const) and isinstance(lvu__xzzq
                        .value, numba.core.dispatcher.ObjModeLiftedWith):
                        return False
                    iojp__brtke = guard(find_callname, f_ir, rhs)
                    if iojp__brtke is None:
                        return False
                    func_name, rnla__xmuj = iojp__brtke
                    if rnla__xmuj == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if iojp__brtke in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if iojp__brtke == ('File', 'h5py'):
                        return False
                    if isinstance(rnla__xmuj, ir.Var):
                        jcrzs__mmjq = typemap[rnla__xmuj.name]
                        if isinstance(jcrzs__mmjq, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(jcrzs__mmjq, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(jcrzs__mmjq, bodo.LoggingLoggerType):
                            return False
                        if str(jcrzs__mmjq).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            rnla__xmuj), ir.Arg)):
                            return False
                    if rnla__xmuj in ('numpy.random', 'time', 'logging',
                        'matplotlib.pyplot'):
                        return False
    return True


def fold_argument_types(pysig, args, kws):

    def normal_handler(index, param, value):
        return value

    def default_handler(index, param, default):
        return types.Omitted(default)

    def stararg_handler(index, param, values):
        return types.StarArgTuple(values)
    args = fold_arguments(pysig, args, kws, normal_handler, default_handler,
        stararg_handler)
    return args


def get_const_func_output_type(func, arg_types, kw_types, typing_context,
    target_context, is_udf=True):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    py_func = None
    if isinstance(func, types.MakeFunctionLiteral):
        yap__rlok = func.literal_value.code
        pjp__gltim = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            pjp__gltim = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(pjp__gltim, yap__rlok)
        fix_struct_return(f_ir)
        typemap, gakod__uav, iaey__volcx, lpyts__arikk = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, iaey__volcx, gakod__uav = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, iaey__volcx, gakod__uav = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, iaey__volcx, gakod__uav = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(gakod__uav, types.DictType):
        iri__kxvir = guard(get_struct_keynames, f_ir, typemap)
        if iri__kxvir is not None:
            gakod__uav = StructType((gakod__uav.value_type,) * len(
                iri__kxvir), iri__kxvir)
    if is_udf and isinstance(gakod__uav, (SeriesType, HeterogeneousSeriesType)
        ):
        wql__zgufo = numba.core.registry.cpu_target.typing_context
        pqrz__wcny = numba.core.registry.cpu_target.target_context
        bwgkx__dbi = bodo.transforms.series_pass.SeriesPass(f_ir,
            wql__zgufo, pqrz__wcny, typemap, iaey__volcx, {})
        bwgkx__dbi.run()
        bwgkx__dbi.run()
        bwgkx__dbi.run()
        jmm__xyf = compute_cfg_from_blocks(f_ir.blocks)
        wrdt__arnv = [guard(_get_const_series_info, f_ir.blocks[
            vkpbh__yrjyh], f_ir, typemap) for vkpbh__yrjyh in jmm__xyf.
            exit_points() if isinstance(f_ir.blocks[vkpbh__yrjyh].body[-1],
            ir.Return)]
        if None in wrdt__arnv or len(pd.Series(wrdt__arnv).unique()) != 1:
            gakod__uav.const_info = None
        else:
            gakod__uav.const_info = wrdt__arnv[0]
    return gakod__uav


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    ryiyi__plwnm = block.body[-1].value
    wkdwa__cvoq = get_definition(f_ir, ryiyi__plwnm)
    require(is_expr(wkdwa__cvoq, 'cast'))
    wkdwa__cvoq = get_definition(f_ir, wkdwa__cvoq.value)
    require(is_call(wkdwa__cvoq) and find_callname(f_ir, wkdwa__cvoq) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    ndwrf__zoox = wkdwa__cvoq.args[1]
    gwiy__ckupr = tuple(get_const_value_inner(f_ir, ndwrf__zoox, typemap=
        typemap))
    if isinstance(typemap[ryiyi__plwnm.name], HeterogeneousSeriesType):
        return len(typemap[ryiyi__plwnm.name].data), gwiy__ckupr
    cgh__zvk = wkdwa__cvoq.args[0]
    roz__wab = get_definition(f_ir, cgh__zvk)
    func_name, kira__lhj = find_callname(f_ir, roz__wab)
    if is_call(roz__wab) and bodo.utils.utils.is_alloc_callname(func_name,
        kira__lhj):
        mkq__ltp = roz__wab.args[0]
        vfu__kei = get_const_value_inner(f_ir, mkq__ltp, typemap=typemap)
        return vfu__kei, gwiy__ckupr
    if is_call(roz__wab) and find_callname(f_ir, roz__wab) in [('asarray',
        'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'), (
        'build_nullable_tuple', 'bodo.libs.nullable_tuple_ext')]:
        cgh__zvk = roz__wab.args[0]
        roz__wab = get_definition(f_ir, cgh__zvk)
    require(is_expr(roz__wab, 'build_tuple') or is_expr(roz__wab, 'build_list')
        )
    return len(roz__wab.items), gwiy__ckupr


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    tykkb__mqq = []
    ymrz__cwxk = []
    values = []
    for byrto__wpbii, tyja__vdckn in build_map.items:
        ywrqk__lcb = find_const(f_ir, byrto__wpbii)
        require(isinstance(ywrqk__lcb, str))
        ymrz__cwxk.append(ywrqk__lcb)
        tykkb__mqq.append(byrto__wpbii)
        values.append(tyja__vdckn)
    blufx__oop = ir.Var(scope, mk_unique_var('val_tup'), loc)
    fcf__uevfx = ir.Assign(ir.Expr.build_tuple(values, loc), blufx__oop, loc)
    f_ir._definitions[blufx__oop.name] = [fcf__uevfx.value]
    dpnd__ucz = ir.Var(scope, mk_unique_var('key_tup'), loc)
    rjhb__ncvr = ir.Assign(ir.Expr.build_tuple(tykkb__mqq, loc), dpnd__ucz, loc
        )
    f_ir._definitions[dpnd__ucz.name] = [rjhb__ncvr.value]
    if typemap is not None:
        typemap[blufx__oop.name] = types.Tuple([typemap[tyja__vdckn.name] for
            tyja__vdckn in values])
        typemap[dpnd__ucz.name] = types.Tuple([typemap[tyja__vdckn.name] for
            tyja__vdckn in tykkb__mqq])
    return ymrz__cwxk, blufx__oop, fcf__uevfx, dpnd__ucz, rjhb__ncvr


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    ydml__jqrz = block.body[-1].value
    yzqq__oazsy = guard(get_definition, f_ir, ydml__jqrz)
    require(is_expr(yzqq__oazsy, 'cast'))
    wkdwa__cvoq = guard(get_definition, f_ir, yzqq__oazsy.value)
    require(is_expr(wkdwa__cvoq, 'build_map'))
    require(len(wkdwa__cvoq.items) > 0)
    loc = block.loc
    scope = block.scope
    ymrz__cwxk, blufx__oop, fcf__uevfx, dpnd__ucz, rjhb__ncvr = (
        extract_keyvals_from_struct_map(f_ir, wkdwa__cvoq, loc, scope))
    wrpt__cjsx = ir.Var(scope, mk_unique_var('conv_call'), loc)
    gsu__illo = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), wrpt__cjsx, loc)
    f_ir._definitions[wrpt__cjsx.name] = [gsu__illo.value]
    yaq__klzfa = ir.Var(scope, mk_unique_var('struct_val'), loc)
    eal__cbsf = ir.Assign(ir.Expr.call(wrpt__cjsx, [blufx__oop, dpnd__ucz],
        {}, loc), yaq__klzfa, loc)
    f_ir._definitions[yaq__klzfa.name] = [eal__cbsf.value]
    yzqq__oazsy.value = yaq__klzfa
    wkdwa__cvoq.items = [(byrto__wpbii, byrto__wpbii) for byrto__wpbii,
        lpyts__arikk in wkdwa__cvoq.items]
    block.body = block.body[:-2] + [fcf__uevfx, rjhb__ncvr, gsu__illo,
        eal__cbsf] + block.body[-2:]
    return tuple(ymrz__cwxk)


def get_struct_keynames(f_ir, typemap):
    jmm__xyf = compute_cfg_from_blocks(f_ir.blocks)
    cps__fukdd = list(jmm__xyf.exit_points())[0]
    block = f_ir.blocks[cps__fukdd]
    require(isinstance(block.body[-1], ir.Return))
    ydml__jqrz = block.body[-1].value
    yzqq__oazsy = guard(get_definition, f_ir, ydml__jqrz)
    require(is_expr(yzqq__oazsy, 'cast'))
    wkdwa__cvoq = guard(get_definition, f_ir, yzqq__oazsy.value)
    require(is_call(wkdwa__cvoq) and find_callname(f_ir, wkdwa__cvoq) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[wkdwa__cvoq.args[1].name])


def fix_struct_return(f_ir):
    ljar__dtut = None
    jmm__xyf = compute_cfg_from_blocks(f_ir.blocks)
    for cps__fukdd in jmm__xyf.exit_points():
        ljar__dtut = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            cps__fukdd], cps__fukdd)
    return ljar__dtut


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    lkvmf__tqm = ir.Block(ir.Scope(None, loc), loc)
    lkvmf__tqm.body = node_list
    build_definitions({(0): lkvmf__tqm}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(tyja__vdckn) for tyja__vdckn in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    zujor__cdc = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(zujor__cdc, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for qdlyz__tffm in range(len(vals) - 1, -1, -1):
        tyja__vdckn = vals[qdlyz__tffm]
        if isinstance(tyja__vdckn, str) and tyja__vdckn.startswith(
            NESTED_TUP_SENTINEL):
            qdaw__mlej = int(tyja__vdckn[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:qdlyz__tffm]) + (
                tuple(vals[qdlyz__tffm + 1:qdlyz__tffm + qdaw__mlej + 1]),) +
                tuple(vals[qdlyz__tffm + qdaw__mlej + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    ywl__fxvt = None
    if len(args) > arg_no and arg_no >= 0:
        ywl__fxvt = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        ywl__fxvt = kws[arg_name]
    if ywl__fxvt is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return ywl__fxvt


def set_call_expr_arg(var, args, kws, arg_no, arg_name, add_if_missing=False):
    if len(args) > arg_no:
        args[arg_no] = var
    elif add_if_missing or arg_name in kws:
        kws[arg_name] = var
    else:
        raise BodoError('cannot set call argument since does not exist')


def avoid_udf_inline(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    f_ir = numba.core.compiler.run_frontend(py_func, inline_closures=True)
    if '_bodo_inline' in kw_types and is_overload_constant_bool(kw_types[
        '_bodo_inline']):
        return not get_overload_const_bool(kw_types['_bodo_inline'])
    if any(isinstance(t, DataFrameType) for t in arg_types + tuple(kw_types
        .values())):
        return True
    for block in f_ir.blocks.values():
        if isinstance(block.body[-1], (ir.Raise, ir.StaticRaise)):
            return True
        for stmt in block.body:
            if isinstance(stmt, ir.EnterWith):
                return True
    return False


def replace_func(pass_info, func, args, const=False, pre_nodes=None,
    extra_globals=None, pysig=None, kws=None, inline_bodo_calls=False,
    run_full_pipeline=False):
    dcypx__wksf = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        dcypx__wksf.update(extra_globals)
    func.__globals__.update(dcypx__wksf)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            sfow__fgf = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[sfow__fgf.name] = types.literal(default)
            except:
                pass_info.typemap[sfow__fgf.name] = numba.typeof(default)
            bvipb__sre = ir.Assign(ir.Const(default, loc), sfow__fgf, loc)
            pre_nodes.append(bvipb__sre)
            return sfow__fgf
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    sgoj__ovuly = tuple(pass_info.typemap[tyja__vdckn.name] for tyja__vdckn in
        args)
    if const:
        zayrv__tjxek = []
        for qdlyz__tffm, ywl__fxvt in enumerate(args):
            hyw__upx = guard(find_const, pass_info.func_ir, ywl__fxvt)
            if hyw__upx:
                zayrv__tjxek.append(types.literal(hyw__upx))
            else:
                zayrv__tjxek.append(sgoj__ovuly[qdlyz__tffm])
        sgoj__ovuly = tuple(zayrv__tjxek)
    return ReplaceFunc(func, sgoj__ovuly, args, dcypx__wksf,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(mjwo__hwgqw) for mjwo__hwgqw in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        lfiw__odz = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {lfiw__odz} = 0\n', (lfiw__odz,)
    if isinstance(t, ArrayItemArrayType):
        wris__xyqj, hwbu__owkq = gen_init_varsize_alloc_sizes(t.dtype)
        lfiw__odz = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {lfiw__odz} = 0\n' + wris__xyqj, (lfiw__odz,) + hwbu__owkq
    return '', ()


def gen_varsize_item_sizes(t, item, var_names):
    if t == string_array_type:
        return '    {} += bodo.libs.str_arr_ext.get_utf8_size({})\n'.format(
            var_names[0], item)
    if isinstance(t, ArrayItemArrayType):
        return '    {} += len({})\n'.format(var_names[0], item
            ) + gen_varsize_array_counts(t.dtype, item, var_names[1:])
    return ''


def gen_varsize_array_counts(t, item, var_names):
    if t == string_array_type:
        return ('    {} += bodo.libs.str_arr_ext.get_num_total_chars({})\n'
            .format(var_names[0], item))
    return ''


def get_type_alloc_counts(t):
    if isinstance(t, (StructArrayType, TupleArrayType)):
        return 1 + sum(get_type_alloc_counts(mjwo__hwgqw.dtype) for
            mjwo__hwgqw in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(mjwo__hwgqw) for mjwo__hwgqw in t.data
            )
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(mjwo__hwgqw) for mjwo__hwgqw in t.
            types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    oakd__ixvw = typing_context.resolve_getattr(obj_dtype, func_name)
    if oakd__ixvw is None:
        lexrx__vip = types.misc.Module(np)
        try:
            oakd__ixvw = typing_context.resolve_getattr(lexrx__vip, func_name)
        except AttributeError as jmj__mkqnt:
            oakd__ixvw = None
        if oakd__ixvw is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return oakd__ixvw


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    oakd__ixvw = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(oakd__ixvw, types.BoundFunction):
        if axis is not None:
            xfcmh__beehv = oakd__ixvw.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            xfcmh__beehv = oakd__ixvw.get_call_type(typing_context, (), {})
        return xfcmh__beehv.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(oakd__ixvw):
            xfcmh__beehv = oakd__ixvw.get_call_type(typing_context, (
                obj_dtype,), {})
            return xfcmh__beehv.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    oakd__ixvw = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(oakd__ixvw, types.BoundFunction):
        ottxj__wtbh = oakd__ixvw.template
        if axis is not None:
            return ottxj__wtbh._overload_func(obj_dtype, axis=axis)
        else:
            return ottxj__wtbh._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    fkfj__saosc = get_definition(func_ir, dict_var)
    require(isinstance(fkfj__saosc, ir.Expr))
    require(fkfj__saosc.op == 'build_map')
    vbp__svh = fkfj__saosc.items
    tykkb__mqq = []
    values = []
    mnnl__zyzto = False
    for qdlyz__tffm in range(len(vbp__svh)):
        oowi__xuhn, value = vbp__svh[qdlyz__tffm]
        try:
            avqz__ezhre = get_const_value_inner(func_ir, oowi__xuhn,
                arg_types, typemap, updated_containers)
            tykkb__mqq.append(avqz__ezhre)
            values.append(value)
        except GuardException as jmj__mkqnt:
            require_const_map[oowi__xuhn] = label
            mnnl__zyzto = True
    if mnnl__zyzto:
        raise GuardException
    return tykkb__mqq, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        tykkb__mqq = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as jmj__mkqnt:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in tykkb__mqq):
        raise BodoError(err_msg, loc)
    return tykkb__mqq


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    tykkb__mqq = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    bqbgc__vqfb = []
    giw__lio = [bodo.transforms.typing_pass._create_const_var(byrto__wpbii,
        'dict_key', scope, loc, bqbgc__vqfb) for byrto__wpbii in tykkb__mqq]
    mnc__skt = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        szdcn__dpbqt = ir.Var(scope, mk_unique_var('sentinel'), loc)
        rntnt__zicd = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        bqbgc__vqfb.append(ir.Assign(ir.Const('__bodo_tup', loc),
            szdcn__dpbqt, loc))
        dylar__gesw = [szdcn__dpbqt] + giw__lio + mnc__skt
        bqbgc__vqfb.append(ir.Assign(ir.Expr.build_tuple(dylar__gesw, loc),
            rntnt__zicd, loc))
        return (rntnt__zicd,), bqbgc__vqfb
    else:
        edhmu__lytk = ir.Var(scope, mk_unique_var('values_tup'), loc)
        hgji__wlrjd = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        bqbgc__vqfb.append(ir.Assign(ir.Expr.build_tuple(mnc__skt, loc),
            edhmu__lytk, loc))
        bqbgc__vqfb.append(ir.Assign(ir.Expr.build_tuple(giw__lio, loc),
            hgji__wlrjd, loc))
        return (edhmu__lytk, hgji__wlrjd), bqbgc__vqfb
