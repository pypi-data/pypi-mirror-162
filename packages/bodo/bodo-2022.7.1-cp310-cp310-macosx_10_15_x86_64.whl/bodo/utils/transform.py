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
    ogzy__brhvk = tuple(call_list)
    if ogzy__brhvk in no_side_effect_call_tuples:
        return True
    if ogzy__brhvk == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(ogzy__brhvk) == 1 and tuple in getattr(ogzy__brhvk[0], '__mro__', ()
        ):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        dxx__hqqq = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        dxx__hqqq = func.__globals__
    if extra_globals is not None:
        dxx__hqqq.update(extra_globals)
    if add_default_globals:
        dxx__hqqq.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, dxx__hqqq, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[pfrki__oive.name] for pfrki__oive in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, dxx__hqqq)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        duior__ier = tuple(typing_info.typemap[pfrki__oive.name] for
            pfrki__oive in args)
        alsi__npkja = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, duior__ier, {}, {}, flags)
        alsi__npkja.run()
    gvbf__zqk = f_ir.blocks.popitem()[1]
    replace_arg_nodes(gvbf__zqk, args)
    aza__xcgn = gvbf__zqk.body[:-2]
    update_locs(aza__xcgn[len(args):], loc)
    for stmt in aza__xcgn[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        pdfo__furf = gvbf__zqk.body[-2]
        assert is_assign(pdfo__furf) and is_expr(pdfo__furf.value, 'cast')
        onzu__ygyfe = pdfo__furf.value.value
        aza__xcgn.append(ir.Assign(onzu__ygyfe, ret_var, loc))
    return aza__xcgn


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for lxpb__cnsvw in stmt.list_vars():
            lxpb__cnsvw.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        anuu__cxcn = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        fjpz__tboi, pfhu__von = anuu__cxcn(stmt)
        return pfhu__von
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        ifm__nuz = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(ifm__nuz, ir.UndefinedType):
            qkq__wallf = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{qkq__wallf}' is not defined", loc=loc)
    except GuardException as bcfmq__hvr:
        raise BodoError(err_msg, loc=loc)
    return ifm__nuz


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    tgo__nwcby = get_definition(func_ir, var)
    nemo__pxa = None
    if typemap is not None:
        nemo__pxa = typemap.get(var.name, None)
    if isinstance(tgo__nwcby, ir.Arg) and arg_types is not None:
        nemo__pxa = arg_types[tgo__nwcby.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(nemo__pxa):
        return get_literal_value(nemo__pxa)
    if isinstance(tgo__nwcby, (ir.Const, ir.Global, ir.FreeVar)):
        ifm__nuz = tgo__nwcby.value
        return ifm__nuz
    if literalize_args and isinstance(tgo__nwcby, ir.Arg
        ) and can_literalize_type(nemo__pxa, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({tgo__nwcby.index}, loc=var
            .loc, file_infos={tgo__nwcby.index: file_info} if file_info is not
            None else None)
    if is_expr(tgo__nwcby, 'binop'):
        if file_info and tgo__nwcby.fn == operator.add:
            try:
                tlgr__alg = get_const_value_inner(func_ir, tgo__nwcby.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(tlgr__alg, True)
                ycjbl__ormuc = get_const_value_inner(func_ir, tgo__nwcby.
                    rhs, arg_types, typemap, updated_containers, file_info)
                return tgo__nwcby.fn(tlgr__alg, ycjbl__ormuc)
            except (GuardException, BodoConstUpdatedError) as bcfmq__hvr:
                pass
            try:
                ycjbl__ormuc = get_const_value_inner(func_ir, tgo__nwcby.
                    rhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(ycjbl__ormuc, False)
                tlgr__alg = get_const_value_inner(func_ir, tgo__nwcby.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return tgo__nwcby.fn(tlgr__alg, ycjbl__ormuc)
            except (GuardException, BodoConstUpdatedError) as bcfmq__hvr:
                pass
        tlgr__alg = get_const_value_inner(func_ir, tgo__nwcby.lhs,
            arg_types, typemap, updated_containers)
        ycjbl__ormuc = get_const_value_inner(func_ir, tgo__nwcby.rhs,
            arg_types, typemap, updated_containers)
        return tgo__nwcby.fn(tlgr__alg, ycjbl__ormuc)
    if is_expr(tgo__nwcby, 'unary'):
        ifm__nuz = get_const_value_inner(func_ir, tgo__nwcby.value,
            arg_types, typemap, updated_containers)
        return tgo__nwcby.fn(ifm__nuz)
    if is_expr(tgo__nwcby, 'getattr') and typemap:
        bimim__uyb = typemap.get(tgo__nwcby.value.name, None)
        if isinstance(bimim__uyb, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and tgo__nwcby.attr == 'columns':
            return pd.Index(bimim__uyb.columns)
        if isinstance(bimim__uyb, types.SliceType):
            hxt__ngl = get_definition(func_ir, tgo__nwcby.value)
            require(is_call(hxt__ngl))
            tkqmv__kha = find_callname(func_ir, hxt__ngl)
            sduo__yup = False
            if tkqmv__kha == ('_normalize_slice', 'numba.cpython.unicode'):
                require(tgo__nwcby.attr in ('start', 'step'))
                hxt__ngl = get_definition(func_ir, hxt__ngl.args[0])
                sduo__yup = True
            require(find_callname(func_ir, hxt__ngl) == ('slice', 'builtins'))
            if len(hxt__ngl.args) == 1:
                if tgo__nwcby.attr == 'start':
                    return 0
                if tgo__nwcby.attr == 'step':
                    return 1
                require(tgo__nwcby.attr == 'stop')
                return get_const_value_inner(func_ir, hxt__ngl.args[0],
                    arg_types, typemap, updated_containers)
            if tgo__nwcby.attr == 'start':
                ifm__nuz = get_const_value_inner(func_ir, hxt__ngl.args[0],
                    arg_types, typemap, updated_containers)
                if ifm__nuz is None:
                    ifm__nuz = 0
                if sduo__yup:
                    require(ifm__nuz == 0)
                return ifm__nuz
            if tgo__nwcby.attr == 'stop':
                assert not sduo__yup
                return get_const_value_inner(func_ir, hxt__ngl.args[1],
                    arg_types, typemap, updated_containers)
            require(tgo__nwcby.attr == 'step')
            if len(hxt__ngl.args) == 2:
                return 1
            else:
                ifm__nuz = get_const_value_inner(func_ir, hxt__ngl.args[2],
                    arg_types, typemap, updated_containers)
                if ifm__nuz is None:
                    ifm__nuz = 1
                if sduo__yup:
                    require(ifm__nuz == 1)
                return ifm__nuz
    if is_expr(tgo__nwcby, 'getattr'):
        return getattr(get_const_value_inner(func_ir, tgo__nwcby.value,
            arg_types, typemap, updated_containers), tgo__nwcby.attr)
    if is_expr(tgo__nwcby, 'getitem'):
        value = get_const_value_inner(func_ir, tgo__nwcby.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, tgo__nwcby.index, arg_types,
            typemap, updated_containers)
        return value[index]
    hlo__scin = guard(find_callname, func_ir, tgo__nwcby, typemap)
    if hlo__scin is not None and len(hlo__scin) == 2 and hlo__scin[0
        ] == 'keys' and isinstance(hlo__scin[1], ir.Var):
        zpg__mlj = tgo__nwcby.func
        tgo__nwcby = get_definition(func_ir, hlo__scin[1])
        zyx__mcny = hlo__scin[1].name
        if updated_containers and zyx__mcny in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                zyx__mcny, updated_containers[zyx__mcny]))
        require(is_expr(tgo__nwcby, 'build_map'))
        vals = [lxpb__cnsvw[0] for lxpb__cnsvw in tgo__nwcby.items]
        rhqi__mfbg = guard(get_definition, func_ir, zpg__mlj)
        assert isinstance(rhqi__mfbg, ir.Expr) and rhqi__mfbg.attr == 'keys'
        rhqi__mfbg.attr = 'copy'
        return [get_const_value_inner(func_ir, lxpb__cnsvw, arg_types,
            typemap, updated_containers) for lxpb__cnsvw in vals]
    if is_expr(tgo__nwcby, 'build_map'):
        return {get_const_value_inner(func_ir, lxpb__cnsvw[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            lxpb__cnsvw[1], arg_types, typemap, updated_containers) for
            lxpb__cnsvw in tgo__nwcby.items}
    if is_expr(tgo__nwcby, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, lxpb__cnsvw, arg_types,
            typemap, updated_containers) for lxpb__cnsvw in tgo__nwcby.items)
    if is_expr(tgo__nwcby, 'build_list'):
        return [get_const_value_inner(func_ir, lxpb__cnsvw, arg_types,
            typemap, updated_containers) for lxpb__cnsvw in tgo__nwcby.items]
    if is_expr(tgo__nwcby, 'build_set'):
        return {get_const_value_inner(func_ir, lxpb__cnsvw, arg_types,
            typemap, updated_containers) for lxpb__cnsvw in tgo__nwcby.items}
    if hlo__scin == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if hlo__scin == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers))
    if hlo__scin == ('range', 'builtins') and len(tgo__nwcby.args) == 1:
        return range(get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers))
    if hlo__scin == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, lxpb__cnsvw,
            arg_types, typemap, updated_containers) for lxpb__cnsvw in
            tgo__nwcby.args))
    if hlo__scin == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers))
    if hlo__scin == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers))
    if hlo__scin == ('format', 'builtins'):
        pfrki__oive = get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers)
        dyt__uael = get_const_value_inner(func_ir, tgo__nwcby.args[1],
            arg_types, typemap, updated_containers) if len(tgo__nwcby.args
            ) > 1 else ''
        return format(pfrki__oive, dyt__uael)
    if hlo__scin in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'
        ), ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers))
    if hlo__scin == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers))
    if hlo__scin == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, tgo__nwcby.args
            [0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, tgo__nwcby.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            tgo__nwcby.args[2], arg_types, typemap, updated_containers))
    if hlo__scin == ('len', 'builtins') and typemap and isinstance(typemap.
        get(tgo__nwcby.args[0].name, None), types.BaseTuple):
        return len(typemap[tgo__nwcby.args[0].name])
    if hlo__scin == ('len', 'builtins'):
        kfqzl__ocja = guard(get_definition, func_ir, tgo__nwcby.args[0])
        if isinstance(kfqzl__ocja, ir.Expr) and kfqzl__ocja.op in (
            'build_tuple', 'build_list', 'build_set', 'build_map'):
            return len(kfqzl__ocja.items)
        return len(get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers))
    if hlo__scin == ('CategoricalDtype', 'pandas'):
        kws = dict(tgo__nwcby.kws)
        oozc__vyb = get_call_expr_arg('CategoricalDtype', tgo__nwcby.args,
            kws, 0, 'categories', '')
        uydz__jbrt = get_call_expr_arg('CategoricalDtype', tgo__nwcby.args,
            kws, 1, 'ordered', False)
        if uydz__jbrt is not False:
            uydz__jbrt = get_const_value_inner(func_ir, uydz__jbrt,
                arg_types, typemap, updated_containers)
        if oozc__vyb == '':
            oozc__vyb = None
        else:
            oozc__vyb = get_const_value_inner(func_ir, oozc__vyb, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(oozc__vyb, uydz__jbrt)
    if hlo__scin == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, tgo__nwcby.args[0],
            arg_types, typemap, updated_containers))
    if hlo__scin is not None and len(hlo__scin) == 2 and hlo__scin[1
        ] == 'pandas' and hlo__scin[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, hlo__scin[0])()
    if hlo__scin is not None and len(hlo__scin) == 2 and isinstance(hlo__scin
        [1], ir.Var):
        ifm__nuz = get_const_value_inner(func_ir, hlo__scin[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, lxpb__cnsvw, arg_types,
            typemap, updated_containers) for lxpb__cnsvw in tgo__nwcby.args]
        kws = {csmj__hfy[0]: get_const_value_inner(func_ir, csmj__hfy[1],
            arg_types, typemap, updated_containers) for csmj__hfy in
            tgo__nwcby.kws}
        return getattr(ifm__nuz, hlo__scin[0])(*args, **kws)
    if hlo__scin is not None and len(hlo__scin) == 2 and hlo__scin[1
        ] == 'bodo' and hlo__scin[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, lxpb__cnsvw, arg_types,
            typemap, updated_containers) for lxpb__cnsvw in tgo__nwcby.args)
        kwargs = {qkq__wallf: get_const_value_inner(func_ir, lxpb__cnsvw,
            arg_types, typemap, updated_containers) for qkq__wallf,
            lxpb__cnsvw in dict(tgo__nwcby.kws).items()}
        return getattr(bodo, hlo__scin[0])(*args, **kwargs)
    if is_call(tgo__nwcby) and typemap and isinstance(typemap.get(
        tgo__nwcby.func.name, None), types.Dispatcher):
        py_func = typemap[tgo__nwcby.func.name].dispatcher.py_func
        require(tgo__nwcby.vararg is None)
        args = tuple(get_const_value_inner(func_ir, lxpb__cnsvw, arg_types,
            typemap, updated_containers) for lxpb__cnsvw in tgo__nwcby.args)
        kwargs = {qkq__wallf: get_const_value_inner(func_ir, lxpb__cnsvw,
            arg_types, typemap, updated_containers) for qkq__wallf,
            lxpb__cnsvw in dict(tgo__nwcby.kws).items()}
        arg_types = tuple(bodo.typeof(lxpb__cnsvw) for lxpb__cnsvw in args)
        kw_types = {wpbm__lmux: bodo.typeof(lxpb__cnsvw) for wpbm__lmux,
            lxpb__cnsvw in kwargs.items()}
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
    f_ir, typemap, salxg__stqt, salxg__stqt = bodo.compiler.get_func_type_info(
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
                    aiun__sals = guard(get_definition, f_ir, rhs.func)
                    if isinstance(aiun__sals, ir.Const) and isinstance(
                        aiun__sals.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    saaeb__kag = guard(find_callname, f_ir, rhs)
                    if saaeb__kag is None:
                        return False
                    func_name, mpnr__pwtj = saaeb__kag
                    if mpnr__pwtj == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if saaeb__kag in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if saaeb__kag == ('File', 'h5py'):
                        return False
                    if isinstance(mpnr__pwtj, ir.Var):
                        nemo__pxa = typemap[mpnr__pwtj.name]
                        if isinstance(nemo__pxa, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(nemo__pxa, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(nemo__pxa, bodo.LoggingLoggerType):
                            return False
                        if str(nemo__pxa).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            mpnr__pwtj), ir.Arg)):
                            return False
                    if mpnr__pwtj in ('numpy.random', 'time', 'logging',
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
        ekfxu__lfe = func.literal_value.code
        rgam__hgayn = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            rgam__hgayn = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(rgam__hgayn, ekfxu__lfe)
        fix_struct_return(f_ir)
        typemap, gnlby__znvr, zsgul__caodp, salxg__stqt = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, zsgul__caodp, gnlby__znvr = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, zsgul__caodp, gnlby__znvr = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, zsgul__caodp, gnlby__znvr = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(gnlby__znvr, types.DictType):
        cfgg__psxw = guard(get_struct_keynames, f_ir, typemap)
        if cfgg__psxw is not None:
            gnlby__znvr = StructType((gnlby__znvr.value_type,) * len(
                cfgg__psxw), cfgg__psxw)
    if is_udf and isinstance(gnlby__znvr, (SeriesType, HeterogeneousSeriesType)
        ):
        fstev__ngkgp = numba.core.registry.cpu_target.typing_context
        tuaax__uaes = numba.core.registry.cpu_target.target_context
        wlm__cmdv = bodo.transforms.series_pass.SeriesPass(f_ir,
            fstev__ngkgp, tuaax__uaes, typemap, zsgul__caodp, {})
        wlm__cmdv.run()
        wlm__cmdv.run()
        wlm__cmdv.run()
        vsu__grrga = compute_cfg_from_blocks(f_ir.blocks)
        oikmv__unkgz = [guard(_get_const_series_info, f_ir.blocks[
            iolg__qecl], f_ir, typemap) for iolg__qecl in vsu__grrga.
            exit_points() if isinstance(f_ir.blocks[iolg__qecl].body[-1],
            ir.Return)]
        if None in oikmv__unkgz or len(pd.Series(oikmv__unkgz).unique()) != 1:
            gnlby__znvr.const_info = None
        else:
            gnlby__znvr.const_info = oikmv__unkgz[0]
    return gnlby__znvr


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    irbv__btxl = block.body[-1].value
    kfrcl__cwuft = get_definition(f_ir, irbv__btxl)
    require(is_expr(kfrcl__cwuft, 'cast'))
    kfrcl__cwuft = get_definition(f_ir, kfrcl__cwuft.value)
    require(is_call(kfrcl__cwuft) and find_callname(f_ir, kfrcl__cwuft) ==
        ('init_series', 'bodo.hiframes.pd_series_ext'))
    joym__fpzqn = kfrcl__cwuft.args[1]
    ugcu__vaovp = tuple(get_const_value_inner(f_ir, joym__fpzqn, typemap=
        typemap))
    if isinstance(typemap[irbv__btxl.name], HeterogeneousSeriesType):
        return len(typemap[irbv__btxl.name].data), ugcu__vaovp
    lfxj__brom = kfrcl__cwuft.args[0]
    sim__dsile = get_definition(f_ir, lfxj__brom)
    func_name, xnm__vvs = find_callname(f_ir, sim__dsile)
    if is_call(sim__dsile) and bodo.utils.utils.is_alloc_callname(func_name,
        xnm__vvs):
        ytr__jiai = sim__dsile.args[0]
        mknjz__ntck = get_const_value_inner(f_ir, ytr__jiai, typemap=typemap)
        return mknjz__ntck, ugcu__vaovp
    if is_call(sim__dsile) and find_callname(f_ir, sim__dsile) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        lfxj__brom = sim__dsile.args[0]
        sim__dsile = get_definition(f_ir, lfxj__brom)
    require(is_expr(sim__dsile, 'build_tuple') or is_expr(sim__dsile,
        'build_list'))
    return len(sim__dsile.items), ugcu__vaovp


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    lkkbl__znh = []
    hau__nraio = []
    values = []
    for wpbm__lmux, lxpb__cnsvw in build_map.items:
        wqswh__ntzat = find_const(f_ir, wpbm__lmux)
        require(isinstance(wqswh__ntzat, str))
        hau__nraio.append(wqswh__ntzat)
        lkkbl__znh.append(wpbm__lmux)
        values.append(lxpb__cnsvw)
    ppi__hfd = ir.Var(scope, mk_unique_var('val_tup'), loc)
    nbs__dxzz = ir.Assign(ir.Expr.build_tuple(values, loc), ppi__hfd, loc)
    f_ir._definitions[ppi__hfd.name] = [nbs__dxzz.value]
    neue__sucap = ir.Var(scope, mk_unique_var('key_tup'), loc)
    cfo__sfxl = ir.Assign(ir.Expr.build_tuple(lkkbl__znh, loc), neue__sucap,
        loc)
    f_ir._definitions[neue__sucap.name] = [cfo__sfxl.value]
    if typemap is not None:
        typemap[ppi__hfd.name] = types.Tuple([typemap[lxpb__cnsvw.name] for
            lxpb__cnsvw in values])
        typemap[neue__sucap.name] = types.Tuple([typemap[lxpb__cnsvw.name] for
            lxpb__cnsvw in lkkbl__znh])
    return hau__nraio, ppi__hfd, nbs__dxzz, neue__sucap, cfo__sfxl


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    gclmz__ddo = block.body[-1].value
    ayoo__cteii = guard(get_definition, f_ir, gclmz__ddo)
    require(is_expr(ayoo__cteii, 'cast'))
    kfrcl__cwuft = guard(get_definition, f_ir, ayoo__cteii.value)
    require(is_expr(kfrcl__cwuft, 'build_map'))
    require(len(kfrcl__cwuft.items) > 0)
    loc = block.loc
    scope = block.scope
    hau__nraio, ppi__hfd, nbs__dxzz, neue__sucap, cfo__sfxl = (
        extract_keyvals_from_struct_map(f_ir, kfrcl__cwuft, loc, scope))
    ikze__znit = ir.Var(scope, mk_unique_var('conv_call'), loc)
    qrt__cbaf = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), ikze__znit, loc)
    f_ir._definitions[ikze__znit.name] = [qrt__cbaf.value]
    lwt__hthzt = ir.Var(scope, mk_unique_var('struct_val'), loc)
    bxc__agi = ir.Assign(ir.Expr.call(ikze__znit, [ppi__hfd, neue__sucap],
        {}, loc), lwt__hthzt, loc)
    f_ir._definitions[lwt__hthzt.name] = [bxc__agi.value]
    ayoo__cteii.value = lwt__hthzt
    kfrcl__cwuft.items = [(wpbm__lmux, wpbm__lmux) for wpbm__lmux,
        salxg__stqt in kfrcl__cwuft.items]
    block.body = block.body[:-2] + [nbs__dxzz, cfo__sfxl, qrt__cbaf, bxc__agi
        ] + block.body[-2:]
    return tuple(hau__nraio)


def get_struct_keynames(f_ir, typemap):
    vsu__grrga = compute_cfg_from_blocks(f_ir.blocks)
    dtz__ulvw = list(vsu__grrga.exit_points())[0]
    block = f_ir.blocks[dtz__ulvw]
    require(isinstance(block.body[-1], ir.Return))
    gclmz__ddo = block.body[-1].value
    ayoo__cteii = guard(get_definition, f_ir, gclmz__ddo)
    require(is_expr(ayoo__cteii, 'cast'))
    kfrcl__cwuft = guard(get_definition, f_ir, ayoo__cteii.value)
    require(is_call(kfrcl__cwuft) and find_callname(f_ir, kfrcl__cwuft) ==
        ('struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[kfrcl__cwuft.args[1].name])


def fix_struct_return(f_ir):
    yuj__vua = None
    vsu__grrga = compute_cfg_from_blocks(f_ir.blocks)
    for dtz__ulvw in vsu__grrga.exit_points():
        yuj__vua = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            dtz__ulvw], dtz__ulvw)
    return yuj__vua


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    suma__kfqm = ir.Block(ir.Scope(None, loc), loc)
    suma__kfqm.body = node_list
    build_definitions({(0): suma__kfqm}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(lxpb__cnsvw) for lxpb__cnsvw in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    awki__cvm = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(awki__cvm, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for obqja__bgq in range(len(vals) - 1, -1, -1):
        lxpb__cnsvw = vals[obqja__bgq]
        if isinstance(lxpb__cnsvw, str) and lxpb__cnsvw.startswith(
            NESTED_TUP_SENTINEL):
            pjb__sbtwm = int(lxpb__cnsvw[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:obqja__bgq]) + (
                tuple(vals[obqja__bgq + 1:obqja__bgq + pjb__sbtwm + 1]),) +
                tuple(vals[obqja__bgq + pjb__sbtwm + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    pfrki__oive = None
    if len(args) > arg_no and arg_no >= 0:
        pfrki__oive = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        pfrki__oive = kws[arg_name]
    if pfrki__oive is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return pfrki__oive


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
    dxx__hqqq = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        dxx__hqqq.update(extra_globals)
    func.__globals__.update(dxx__hqqq)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            rssda__mhsr = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[rssda__mhsr.name] = types.literal(default)
            except:
                pass_info.typemap[rssda__mhsr.name] = numba.typeof(default)
            lxvpx__fkj = ir.Assign(ir.Const(default, loc), rssda__mhsr, loc)
            pre_nodes.append(lxvpx__fkj)
            return rssda__mhsr
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    duior__ier = tuple(pass_info.typemap[lxpb__cnsvw.name] for lxpb__cnsvw in
        args)
    if const:
        lgi__latr = []
        for obqja__bgq, pfrki__oive in enumerate(args):
            ifm__nuz = guard(find_const, pass_info.func_ir, pfrki__oive)
            if ifm__nuz:
                lgi__latr.append(types.literal(ifm__nuz))
            else:
                lgi__latr.append(duior__ier[obqja__bgq])
        duior__ier = tuple(lgi__latr)
    return ReplaceFunc(func, duior__ier, args, dxx__hqqq, inline_bodo_calls,
        run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(duij__wmo) for duij__wmo in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        pvv__xnm = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {pvv__xnm} = 0\n', (pvv__xnm,)
    if isinstance(t, ArrayItemArrayType):
        cov__ogun, xnr__buqs = gen_init_varsize_alloc_sizes(t.dtype)
        pvv__xnm = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {pvv__xnm} = 0\n' + cov__ogun, (pvv__xnm,) + xnr__buqs
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
        return 1 + sum(get_type_alloc_counts(duij__wmo.dtype) for duij__wmo in
            t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(duij__wmo) for duij__wmo in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(duij__wmo) for duij__wmo in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    yjt__ytlh = typing_context.resolve_getattr(obj_dtype, func_name)
    if yjt__ytlh is None:
        twl__bixy = types.misc.Module(np)
        try:
            yjt__ytlh = typing_context.resolve_getattr(twl__bixy, func_name)
        except AttributeError as bcfmq__hvr:
            yjt__ytlh = None
        if yjt__ytlh is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return yjt__ytlh


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    yjt__ytlh = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(yjt__ytlh, types.BoundFunction):
        if axis is not None:
            tcev__fhe = yjt__ytlh.get_call_type(typing_context, (), {'axis':
                axis})
        else:
            tcev__fhe = yjt__ytlh.get_call_type(typing_context, (), {})
        return tcev__fhe.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(yjt__ytlh):
            tcev__fhe = yjt__ytlh.get_call_type(typing_context, (obj_dtype,
                ), {})
            return tcev__fhe.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    yjt__ytlh = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(yjt__ytlh, types.BoundFunction):
        xdid__donvd = yjt__ytlh.template
        if axis is not None:
            return xdid__donvd._overload_func(obj_dtype, axis=axis)
        else:
            return xdid__donvd._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    rmgzk__axmnk = get_definition(func_ir, dict_var)
    require(isinstance(rmgzk__axmnk, ir.Expr))
    require(rmgzk__axmnk.op == 'build_map')
    vnu__kylg = rmgzk__axmnk.items
    lkkbl__znh = []
    values = []
    tayw__jrt = False
    for obqja__bgq in range(len(vnu__kylg)):
        ywf__ufmvj, value = vnu__kylg[obqja__bgq]
        try:
            tvf__qua = get_const_value_inner(func_ir, ywf__ufmvj, arg_types,
                typemap, updated_containers)
            lkkbl__znh.append(tvf__qua)
            values.append(value)
        except GuardException as bcfmq__hvr:
            require_const_map[ywf__ufmvj] = label
            tayw__jrt = True
    if tayw__jrt:
        raise GuardException
    return lkkbl__znh, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        lkkbl__znh = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as bcfmq__hvr:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in lkkbl__znh):
        raise BodoError(err_msg, loc)
    return lkkbl__znh


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    lkkbl__znh = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    cgcw__rhoe = []
    yri__anhp = [bodo.transforms.typing_pass._create_const_var(wpbm__lmux,
        'dict_key', scope, loc, cgcw__rhoe) for wpbm__lmux in lkkbl__znh]
    ixi__ohxf = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        aalvm__rdt = ir.Var(scope, mk_unique_var('sentinel'), loc)
        hpqzf__bachb = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        cgcw__rhoe.append(ir.Assign(ir.Const('__bodo_tup', loc), aalvm__rdt,
            loc))
        ugrao__gsix = [aalvm__rdt] + yri__anhp + ixi__ohxf
        cgcw__rhoe.append(ir.Assign(ir.Expr.build_tuple(ugrao__gsix, loc),
            hpqzf__bachb, loc))
        return (hpqzf__bachb,), cgcw__rhoe
    else:
        wxdr__oti = ir.Var(scope, mk_unique_var('values_tup'), loc)
        uei__iqhiv = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        cgcw__rhoe.append(ir.Assign(ir.Expr.build_tuple(ixi__ohxf, loc),
            wxdr__oti, loc))
        cgcw__rhoe.append(ir.Assign(ir.Expr.build_tuple(yri__anhp, loc),
            uei__iqhiv, loc))
        return (wxdr__oti, uei__iqhiv), cgcw__rhoe
