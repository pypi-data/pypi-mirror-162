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
    sdtc__kslg = tuple(call_list)
    if sdtc__kslg in no_side_effect_call_tuples:
        return True
    if sdtc__kslg == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(sdtc__kslg) == 1 and tuple in getattr(sdtc__kslg[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        dhsc__zano = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        dhsc__zano = func.__globals__
    if extra_globals is not None:
        dhsc__zano.update(extra_globals)
    if add_default_globals:
        dhsc__zano.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, dhsc__zano, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[tpmv__myiue.name] for tpmv__myiue in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, dhsc__zano)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        qfskt__rvym = tuple(typing_info.typemap[tpmv__myiue.name] for
            tpmv__myiue in args)
        gzz__mpd = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, qfskt__rvym, {}, {}, flags)
        gzz__mpd.run()
    epdh__utsjb = f_ir.blocks.popitem()[1]
    replace_arg_nodes(epdh__utsjb, args)
    rykf__mwn = epdh__utsjb.body[:-2]
    update_locs(rykf__mwn[len(args):], loc)
    for stmt in rykf__mwn[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        bkth__wuq = epdh__utsjb.body[-2]
        assert is_assign(bkth__wuq) and is_expr(bkth__wuq.value, 'cast')
        taaf__lzyl = bkth__wuq.value.value
        rykf__mwn.append(ir.Assign(taaf__lzyl, ret_var, loc))
    return rykf__mwn


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for hwz__tjm in stmt.list_vars():
            hwz__tjm.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        akd__efx = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        qutsz__gcypf, marqk__wpla = akd__efx(stmt)
        return marqk__wpla
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        hjf__fzhsr = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(hjf__fzhsr, ir.UndefinedType):
            qqtt__qkra = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{qqtt__qkra}' is not defined", loc=loc)
    except GuardException as fwa__romhb:
        raise BodoError(err_msg, loc=loc)
    return hjf__fzhsr


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    bjsfp__grop = get_definition(func_ir, var)
    bwxfs__huqw = None
    if typemap is not None:
        bwxfs__huqw = typemap.get(var.name, None)
    if isinstance(bjsfp__grop, ir.Arg) and arg_types is not None:
        bwxfs__huqw = arg_types[bjsfp__grop.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(bwxfs__huqw):
        return get_literal_value(bwxfs__huqw)
    if isinstance(bjsfp__grop, (ir.Const, ir.Global, ir.FreeVar)):
        hjf__fzhsr = bjsfp__grop.value
        return hjf__fzhsr
    if literalize_args and isinstance(bjsfp__grop, ir.Arg
        ) and can_literalize_type(bwxfs__huqw, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({bjsfp__grop.index}, loc=
            var.loc, file_infos={bjsfp__grop.index: file_info} if file_info
             is not None else None)
    if is_expr(bjsfp__grop, 'binop'):
        if file_info and bjsfp__grop.fn == operator.add:
            try:
                nlrl__bfdr = get_const_value_inner(func_ir, bjsfp__grop.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(nlrl__bfdr, True)
                obcui__otq = get_const_value_inner(func_ir, bjsfp__grop.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return bjsfp__grop.fn(nlrl__bfdr, obcui__otq)
            except (GuardException, BodoConstUpdatedError) as fwa__romhb:
                pass
            try:
                obcui__otq = get_const_value_inner(func_ir, bjsfp__grop.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(obcui__otq, False)
                nlrl__bfdr = get_const_value_inner(func_ir, bjsfp__grop.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return bjsfp__grop.fn(nlrl__bfdr, obcui__otq)
            except (GuardException, BodoConstUpdatedError) as fwa__romhb:
                pass
        nlrl__bfdr = get_const_value_inner(func_ir, bjsfp__grop.lhs,
            arg_types, typemap, updated_containers)
        obcui__otq = get_const_value_inner(func_ir, bjsfp__grop.rhs,
            arg_types, typemap, updated_containers)
        return bjsfp__grop.fn(nlrl__bfdr, obcui__otq)
    if is_expr(bjsfp__grop, 'unary'):
        hjf__fzhsr = get_const_value_inner(func_ir, bjsfp__grop.value,
            arg_types, typemap, updated_containers)
        return bjsfp__grop.fn(hjf__fzhsr)
    if is_expr(bjsfp__grop, 'getattr') and typemap:
        rnam__nrnr = typemap.get(bjsfp__grop.value.name, None)
        if isinstance(rnam__nrnr, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and bjsfp__grop.attr == 'columns':
            return pd.Index(rnam__nrnr.columns)
        if isinstance(rnam__nrnr, types.SliceType):
            bph__zsua = get_definition(func_ir, bjsfp__grop.value)
            require(is_call(bph__zsua))
            verw__uje = find_callname(func_ir, bph__zsua)
            smi__gpze = False
            if verw__uje == ('_normalize_slice', 'numba.cpython.unicode'):
                require(bjsfp__grop.attr in ('start', 'step'))
                bph__zsua = get_definition(func_ir, bph__zsua.args[0])
                smi__gpze = True
            require(find_callname(func_ir, bph__zsua) == ('slice', 'builtins'))
            if len(bph__zsua.args) == 1:
                if bjsfp__grop.attr == 'start':
                    return 0
                if bjsfp__grop.attr == 'step':
                    return 1
                require(bjsfp__grop.attr == 'stop')
                return get_const_value_inner(func_ir, bph__zsua.args[0],
                    arg_types, typemap, updated_containers)
            if bjsfp__grop.attr == 'start':
                hjf__fzhsr = get_const_value_inner(func_ir, bph__zsua.args[
                    0], arg_types, typemap, updated_containers)
                if hjf__fzhsr is None:
                    hjf__fzhsr = 0
                if smi__gpze:
                    require(hjf__fzhsr == 0)
                return hjf__fzhsr
            if bjsfp__grop.attr == 'stop':
                assert not smi__gpze
                return get_const_value_inner(func_ir, bph__zsua.args[1],
                    arg_types, typemap, updated_containers)
            require(bjsfp__grop.attr == 'step')
            if len(bph__zsua.args) == 2:
                return 1
            else:
                hjf__fzhsr = get_const_value_inner(func_ir, bph__zsua.args[
                    2], arg_types, typemap, updated_containers)
                if hjf__fzhsr is None:
                    hjf__fzhsr = 1
                if smi__gpze:
                    require(hjf__fzhsr == 1)
                return hjf__fzhsr
    if is_expr(bjsfp__grop, 'getattr'):
        return getattr(get_const_value_inner(func_ir, bjsfp__grop.value,
            arg_types, typemap, updated_containers), bjsfp__grop.attr)
    if is_expr(bjsfp__grop, 'getitem'):
        value = get_const_value_inner(func_ir, bjsfp__grop.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, bjsfp__grop.index, arg_types,
            typemap, updated_containers)
        return value[index]
    mhi__owz = guard(find_callname, func_ir, bjsfp__grop, typemap)
    if mhi__owz is not None and len(mhi__owz) == 2 and mhi__owz[0
        ] == 'keys' and isinstance(mhi__owz[1], ir.Var):
        cxg__jpeh = bjsfp__grop.func
        bjsfp__grop = get_definition(func_ir, mhi__owz[1])
        nxn__vlc = mhi__owz[1].name
        if updated_containers and nxn__vlc in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                nxn__vlc, updated_containers[nxn__vlc]))
        require(is_expr(bjsfp__grop, 'build_map'))
        vals = [hwz__tjm[0] for hwz__tjm in bjsfp__grop.items]
        rwo__sndwc = guard(get_definition, func_ir, cxg__jpeh)
        assert isinstance(rwo__sndwc, ir.Expr) and rwo__sndwc.attr == 'keys'
        rwo__sndwc.attr = 'copy'
        return [get_const_value_inner(func_ir, hwz__tjm, arg_types, typemap,
            updated_containers) for hwz__tjm in vals]
    if is_expr(bjsfp__grop, 'build_map'):
        return {get_const_value_inner(func_ir, hwz__tjm[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            hwz__tjm[1], arg_types, typemap, updated_containers) for
            hwz__tjm in bjsfp__grop.items}
    if is_expr(bjsfp__grop, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, hwz__tjm, arg_types,
            typemap, updated_containers) for hwz__tjm in bjsfp__grop.items)
    if is_expr(bjsfp__grop, 'build_list'):
        return [get_const_value_inner(func_ir, hwz__tjm, arg_types, typemap,
            updated_containers) for hwz__tjm in bjsfp__grop.items]
    if is_expr(bjsfp__grop, 'build_set'):
        return {get_const_value_inner(func_ir, hwz__tjm, arg_types, typemap,
            updated_containers) for hwz__tjm in bjsfp__grop.items}
    if mhi__owz == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if mhi__owz == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers))
    if mhi__owz == ('range', 'builtins') and len(bjsfp__grop.args) == 1:
        return range(get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers))
    if mhi__owz == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, hwz__tjm,
            arg_types, typemap, updated_containers) for hwz__tjm in
            bjsfp__grop.args))
    if mhi__owz == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers))
    if mhi__owz == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers))
    if mhi__owz == ('format', 'builtins'):
        tpmv__myiue = get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers)
        etmst__tii = get_const_value_inner(func_ir, bjsfp__grop.args[1],
            arg_types, typemap, updated_containers) if len(bjsfp__grop.args
            ) > 1 else ''
        return format(tpmv__myiue, etmst__tii)
    if mhi__owz in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'),
        ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers))
    if mhi__owz == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers))
    if mhi__owz == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, bjsfp__grop.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, bjsfp__grop.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            bjsfp__grop.args[2], arg_types, typemap, updated_containers))
    if mhi__owz == ('len', 'builtins') and typemap and isinstance(typemap.
        get(bjsfp__grop.args[0].name, None), types.BaseTuple):
        return len(typemap[bjsfp__grop.args[0].name])
    if mhi__owz == ('len', 'builtins'):
        fzknr__xfop = guard(get_definition, func_ir, bjsfp__grop.args[0])
        if isinstance(fzknr__xfop, ir.Expr) and fzknr__xfop.op in (
            'build_tuple', 'build_list', 'build_set', 'build_map'):
            return len(fzknr__xfop.items)
        return len(get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers))
    if mhi__owz == ('CategoricalDtype', 'pandas'):
        kws = dict(bjsfp__grop.kws)
        oape__phipu = get_call_expr_arg('CategoricalDtype', bjsfp__grop.
            args, kws, 0, 'categories', '')
        kth__qyhvy = get_call_expr_arg('CategoricalDtype', bjsfp__grop.args,
            kws, 1, 'ordered', False)
        if kth__qyhvy is not False:
            kth__qyhvy = get_const_value_inner(func_ir, kth__qyhvy,
                arg_types, typemap, updated_containers)
        if oape__phipu == '':
            oape__phipu = None
        else:
            oape__phipu = get_const_value_inner(func_ir, oape__phipu,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(oape__phipu, kth__qyhvy)
    if mhi__owz == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, bjsfp__grop.args[0],
            arg_types, typemap, updated_containers))
    if mhi__owz is not None and len(mhi__owz) == 2 and mhi__owz[1
        ] == 'pandas' and mhi__owz[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, mhi__owz[0])()
    if mhi__owz is not None and len(mhi__owz) == 2 and isinstance(mhi__owz[
        1], ir.Var):
        hjf__fzhsr = get_const_value_inner(func_ir, mhi__owz[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, hwz__tjm, arg_types, typemap,
            updated_containers) for hwz__tjm in bjsfp__grop.args]
        kws = {qsev__axbv[0]: get_const_value_inner(func_ir, qsev__axbv[1],
            arg_types, typemap, updated_containers) for qsev__axbv in
            bjsfp__grop.kws}
        return getattr(hjf__fzhsr, mhi__owz[0])(*args, **kws)
    if mhi__owz is not None and len(mhi__owz) == 2 and mhi__owz[1
        ] == 'bodo' and mhi__owz[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, hwz__tjm, arg_types,
            typemap, updated_containers) for hwz__tjm in bjsfp__grop.args)
        kwargs = {qqtt__qkra: get_const_value_inner(func_ir, hwz__tjm,
            arg_types, typemap, updated_containers) for qqtt__qkra,
            hwz__tjm in dict(bjsfp__grop.kws).items()}
        return getattr(bodo, mhi__owz[0])(*args, **kwargs)
    if is_call(bjsfp__grop) and typemap and isinstance(typemap.get(
        bjsfp__grop.func.name, None), types.Dispatcher):
        py_func = typemap[bjsfp__grop.func.name].dispatcher.py_func
        require(bjsfp__grop.vararg is None)
        args = tuple(get_const_value_inner(func_ir, hwz__tjm, arg_types,
            typemap, updated_containers) for hwz__tjm in bjsfp__grop.args)
        kwargs = {qqtt__qkra: get_const_value_inner(func_ir, hwz__tjm,
            arg_types, typemap, updated_containers) for qqtt__qkra,
            hwz__tjm in dict(bjsfp__grop.kws).items()}
        arg_types = tuple(bodo.typeof(hwz__tjm) for hwz__tjm in args)
        kw_types = {wur__nep: bodo.typeof(hwz__tjm) for wur__nep, hwz__tjm in
            kwargs.items()}
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
    f_ir, typemap, fkn__zickv, fkn__zickv = bodo.compiler.get_func_type_info(
        py_func, arg_types, kw_types)
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
                    wwv__sjrfm = guard(get_definition, f_ir, rhs.func)
                    if isinstance(wwv__sjrfm, ir.Const) and isinstance(
                        wwv__sjrfm.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    uls__sac = guard(find_callname, f_ir, rhs)
                    if uls__sac is None:
                        return False
                    func_name, ikn__hkwaa = uls__sac
                    if ikn__hkwaa == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if uls__sac in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if uls__sac == ('File', 'h5py'):
                        return False
                    if isinstance(ikn__hkwaa, ir.Var):
                        bwxfs__huqw = typemap[ikn__hkwaa.name]
                        if isinstance(bwxfs__huqw, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(bwxfs__huqw, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(bwxfs__huqw, bodo.LoggingLoggerType):
                            return False
                        if str(bwxfs__huqw).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            ikn__hkwaa), ir.Arg)):
                            return False
                    if ikn__hkwaa in ('numpy.random', 'time', 'logging',
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
        zipqz__smix = func.literal_value.code
        sxsb__hpx = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            sxsb__hpx = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(sxsb__hpx, zipqz__smix)
        fix_struct_return(f_ir)
        typemap, dvxnb__mee, qtklt__wcpr, fkn__zickv = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, qtklt__wcpr, dvxnb__mee = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, qtklt__wcpr, dvxnb__mee = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, qtklt__wcpr, dvxnb__mee = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(dvxnb__mee, types.DictType):
        asrfg__yfcm = guard(get_struct_keynames, f_ir, typemap)
        if asrfg__yfcm is not None:
            dvxnb__mee = StructType((dvxnb__mee.value_type,) * len(
                asrfg__yfcm), asrfg__yfcm)
    if is_udf and isinstance(dvxnb__mee, (SeriesType, HeterogeneousSeriesType)
        ):
        rkg__enol = numba.core.registry.cpu_target.typing_context
        wlku__uxl = numba.core.registry.cpu_target.target_context
        fpth__kchc = bodo.transforms.series_pass.SeriesPass(f_ir, rkg__enol,
            wlku__uxl, typemap, qtklt__wcpr, {})
        fpth__kchc.run()
        fpth__kchc.run()
        fpth__kchc.run()
        wplpz__mjatj = compute_cfg_from_blocks(f_ir.blocks)
        gusw__slz = [guard(_get_const_series_info, f_ir.blocks[hhwux__wakfc
            ], f_ir, typemap) for hhwux__wakfc in wplpz__mjatj.exit_points(
            ) if isinstance(f_ir.blocks[hhwux__wakfc].body[-1], ir.Return)]
        if None in gusw__slz or len(pd.Series(gusw__slz).unique()) != 1:
            dvxnb__mee.const_info = None
        else:
            dvxnb__mee.const_info = gusw__slz[0]
    return dvxnb__mee


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    qghba__uxn = block.body[-1].value
    shggz__zvkj = get_definition(f_ir, qghba__uxn)
    require(is_expr(shggz__zvkj, 'cast'))
    shggz__zvkj = get_definition(f_ir, shggz__zvkj.value)
    require(is_call(shggz__zvkj) and find_callname(f_ir, shggz__zvkj) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    bcqlc__yajk = shggz__zvkj.args[1]
    uqx__vda = tuple(get_const_value_inner(f_ir, bcqlc__yajk, typemap=typemap))
    if isinstance(typemap[qghba__uxn.name], HeterogeneousSeriesType):
        return len(typemap[qghba__uxn.name].data), uqx__vda
    wsvh__pcb = shggz__zvkj.args[0]
    scsrv__oyrz = get_definition(f_ir, wsvh__pcb)
    func_name, uvs__spb = find_callname(f_ir, scsrv__oyrz)
    if is_call(scsrv__oyrz) and bodo.utils.utils.is_alloc_callname(func_name,
        uvs__spb):
        wgte__ieka = scsrv__oyrz.args[0]
        gzta__rgu = get_const_value_inner(f_ir, wgte__ieka, typemap=typemap)
        return gzta__rgu, uqx__vda
    if is_call(scsrv__oyrz) and find_callname(f_ir, scsrv__oyrz) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        wsvh__pcb = scsrv__oyrz.args[0]
        scsrv__oyrz = get_definition(f_ir, wsvh__pcb)
    require(is_expr(scsrv__oyrz, 'build_tuple') or is_expr(scsrv__oyrz,
        'build_list'))
    return len(scsrv__oyrz.items), uqx__vda


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    alko__vuit = []
    okwwj__pqz = []
    values = []
    for wur__nep, hwz__tjm in build_map.items:
        anjg__bsun = find_const(f_ir, wur__nep)
        require(isinstance(anjg__bsun, str))
        okwwj__pqz.append(anjg__bsun)
        alko__vuit.append(wur__nep)
        values.append(hwz__tjm)
    jywuu__wak = ir.Var(scope, mk_unique_var('val_tup'), loc)
    nyj__vugdj = ir.Assign(ir.Expr.build_tuple(values, loc), jywuu__wak, loc)
    f_ir._definitions[jywuu__wak.name] = [nyj__vugdj.value]
    hru__uoo = ir.Var(scope, mk_unique_var('key_tup'), loc)
    xnei__cinh = ir.Assign(ir.Expr.build_tuple(alko__vuit, loc), hru__uoo, loc)
    f_ir._definitions[hru__uoo.name] = [xnei__cinh.value]
    if typemap is not None:
        typemap[jywuu__wak.name] = types.Tuple([typemap[hwz__tjm.name] for
            hwz__tjm in values])
        typemap[hru__uoo.name] = types.Tuple([typemap[hwz__tjm.name] for
            hwz__tjm in alko__vuit])
    return okwwj__pqz, jywuu__wak, nyj__vugdj, hru__uoo, xnei__cinh


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    cavi__ovewu = block.body[-1].value
    wrtnx__pddpe = guard(get_definition, f_ir, cavi__ovewu)
    require(is_expr(wrtnx__pddpe, 'cast'))
    shggz__zvkj = guard(get_definition, f_ir, wrtnx__pddpe.value)
    require(is_expr(shggz__zvkj, 'build_map'))
    require(len(shggz__zvkj.items) > 0)
    loc = block.loc
    scope = block.scope
    okwwj__pqz, jywuu__wak, nyj__vugdj, hru__uoo, xnei__cinh = (
        extract_keyvals_from_struct_map(f_ir, shggz__zvkj, loc, scope))
    zze__hzhf = ir.Var(scope, mk_unique_var('conv_call'), loc)
    xtj__eth = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), zze__hzhf, loc)
    f_ir._definitions[zze__hzhf.name] = [xtj__eth.value]
    vljm__tbg = ir.Var(scope, mk_unique_var('struct_val'), loc)
    znaes__kdmkc = ir.Assign(ir.Expr.call(zze__hzhf, [jywuu__wak, hru__uoo],
        {}, loc), vljm__tbg, loc)
    f_ir._definitions[vljm__tbg.name] = [znaes__kdmkc.value]
    wrtnx__pddpe.value = vljm__tbg
    shggz__zvkj.items = [(wur__nep, wur__nep) for wur__nep, fkn__zickv in
        shggz__zvkj.items]
    block.body = block.body[:-2] + [nyj__vugdj, xnei__cinh, xtj__eth,
        znaes__kdmkc] + block.body[-2:]
    return tuple(okwwj__pqz)


def get_struct_keynames(f_ir, typemap):
    wplpz__mjatj = compute_cfg_from_blocks(f_ir.blocks)
    qccp__lisem = list(wplpz__mjatj.exit_points())[0]
    block = f_ir.blocks[qccp__lisem]
    require(isinstance(block.body[-1], ir.Return))
    cavi__ovewu = block.body[-1].value
    wrtnx__pddpe = guard(get_definition, f_ir, cavi__ovewu)
    require(is_expr(wrtnx__pddpe, 'cast'))
    shggz__zvkj = guard(get_definition, f_ir, wrtnx__pddpe.value)
    require(is_call(shggz__zvkj) and find_callname(f_ir, shggz__zvkj) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[shggz__zvkj.args[1].name])


def fix_struct_return(f_ir):
    okdb__bmq = None
    wplpz__mjatj = compute_cfg_from_blocks(f_ir.blocks)
    for qccp__lisem in wplpz__mjatj.exit_points():
        okdb__bmq = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            qccp__lisem], qccp__lisem)
    return okdb__bmq


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    uns__uphx = ir.Block(ir.Scope(None, loc), loc)
    uns__uphx.body = node_list
    build_definitions({(0): uns__uphx}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(hwz__tjm) for hwz__tjm in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    fpzn__xjhs = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(fpzn__xjhs, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for tbmfv__hkjj in range(len(vals) - 1, -1, -1):
        hwz__tjm = vals[tbmfv__hkjj]
        if isinstance(hwz__tjm, str) and hwz__tjm.startswith(
            NESTED_TUP_SENTINEL):
            yanh__mlaa = int(hwz__tjm[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:tbmfv__hkjj]) + (
                tuple(vals[tbmfv__hkjj + 1:tbmfv__hkjj + yanh__mlaa + 1]),) +
                tuple(vals[tbmfv__hkjj + yanh__mlaa + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    tpmv__myiue = None
    if len(args) > arg_no and arg_no >= 0:
        tpmv__myiue = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        tpmv__myiue = kws[arg_name]
    if tpmv__myiue is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return tpmv__myiue


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
    dhsc__zano = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        dhsc__zano.update(extra_globals)
    func.__globals__.update(dhsc__zano)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            iskxg__edd = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[iskxg__edd.name] = types.literal(default)
            except:
                pass_info.typemap[iskxg__edd.name] = numba.typeof(default)
            bkwz__hll = ir.Assign(ir.Const(default, loc), iskxg__edd, loc)
            pre_nodes.append(bkwz__hll)
            return iskxg__edd
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    qfskt__rvym = tuple(pass_info.typemap[hwz__tjm.name] for hwz__tjm in args)
    if const:
        tvq__okqu = []
        for tbmfv__hkjj, tpmv__myiue in enumerate(args):
            hjf__fzhsr = guard(find_const, pass_info.func_ir, tpmv__myiue)
            if hjf__fzhsr:
                tvq__okqu.append(types.literal(hjf__fzhsr))
            else:
                tvq__okqu.append(qfskt__rvym[tbmfv__hkjj])
        qfskt__rvym = tuple(tvq__okqu)
    return ReplaceFunc(func, qfskt__rvym, args, dhsc__zano,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(cejw__jafq) for cejw__jafq in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        dhec__pgx = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {dhec__pgx} = 0\n', (dhec__pgx,)
    if isinstance(t, ArrayItemArrayType):
        rqhj__epy, ulzo__lqujl = gen_init_varsize_alloc_sizes(t.dtype)
        dhec__pgx = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {dhec__pgx} = 0\n' + rqhj__epy, (dhec__pgx,) + ulzo__lqujl
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
        return 1 + sum(get_type_alloc_counts(cejw__jafq.dtype) for
            cejw__jafq in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(cejw__jafq) for cejw__jafq in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(cejw__jafq) for cejw__jafq in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    vhn__snqqp = typing_context.resolve_getattr(obj_dtype, func_name)
    if vhn__snqqp is None:
        zje__dofl = types.misc.Module(np)
        try:
            vhn__snqqp = typing_context.resolve_getattr(zje__dofl, func_name)
        except AttributeError as fwa__romhb:
            vhn__snqqp = None
        if vhn__snqqp is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return vhn__snqqp


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    vhn__snqqp = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(vhn__snqqp, types.BoundFunction):
        if axis is not None:
            flehe__jzvu = vhn__snqqp.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            flehe__jzvu = vhn__snqqp.get_call_type(typing_context, (), {})
        return flehe__jzvu.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(vhn__snqqp):
            flehe__jzvu = vhn__snqqp.get_call_type(typing_context, (
                obj_dtype,), {})
            return flehe__jzvu.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    vhn__snqqp = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(vhn__snqqp, types.BoundFunction):
        rwdyd__quuzd = vhn__snqqp.template
        if axis is not None:
            return rwdyd__quuzd._overload_func(obj_dtype, axis=axis)
        else:
            return rwdyd__quuzd._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    rjhw__iic = get_definition(func_ir, dict_var)
    require(isinstance(rjhw__iic, ir.Expr))
    require(rjhw__iic.op == 'build_map')
    ucuf__mctjx = rjhw__iic.items
    alko__vuit = []
    values = []
    zgb__qzyu = False
    for tbmfv__hkjj in range(len(ucuf__mctjx)):
        ezstz__nxt, value = ucuf__mctjx[tbmfv__hkjj]
        try:
            lhbq__hda = get_const_value_inner(func_ir, ezstz__nxt,
                arg_types, typemap, updated_containers)
            alko__vuit.append(lhbq__hda)
            values.append(value)
        except GuardException as fwa__romhb:
            require_const_map[ezstz__nxt] = label
            zgb__qzyu = True
    if zgb__qzyu:
        raise GuardException
    return alko__vuit, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        alko__vuit = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as fwa__romhb:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in alko__vuit):
        raise BodoError(err_msg, loc)
    return alko__vuit


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    alko__vuit = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    bocu__bomv = []
    hhje__ffzc = [bodo.transforms.typing_pass._create_const_var(wur__nep,
        'dict_key', scope, loc, bocu__bomv) for wur__nep in alko__vuit]
    ktwus__gkj = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        hud__klhc = ir.Var(scope, mk_unique_var('sentinel'), loc)
        qvgz__cjpe = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        bocu__bomv.append(ir.Assign(ir.Const('__bodo_tup', loc), hud__klhc,
            loc))
        crj__cgjo = [hud__klhc] + hhje__ffzc + ktwus__gkj
        bocu__bomv.append(ir.Assign(ir.Expr.build_tuple(crj__cgjo, loc),
            qvgz__cjpe, loc))
        return (qvgz__cjpe,), bocu__bomv
    else:
        dlzxo__pqpzu = ir.Var(scope, mk_unique_var('values_tup'), loc)
        yxc__biad = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        bocu__bomv.append(ir.Assign(ir.Expr.build_tuple(ktwus__gkj, loc),
            dlzxo__pqpzu, loc))
        bocu__bomv.append(ir.Assign(ir.Expr.build_tuple(hhje__ffzc, loc),
            yxc__biad, loc))
        return (dlzxo__pqpzu, yxc__biad), bocu__bomv
