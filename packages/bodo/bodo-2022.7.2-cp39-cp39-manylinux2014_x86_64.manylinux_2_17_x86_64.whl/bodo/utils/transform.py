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
    mfng__foczg = tuple(call_list)
    if mfng__foczg in no_side_effect_call_tuples:
        return True
    if mfng__foczg == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(mfng__foczg) == 1 and tuple in getattr(mfng__foczg[0], '__mro__', ()
        ):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        bmd__sjaw = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        bmd__sjaw = func.__globals__
    if extra_globals is not None:
        bmd__sjaw.update(extra_globals)
    if add_default_globals:
        bmd__sjaw.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, bmd__sjaw, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[humk__usrh.name] for humk__usrh in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, bmd__sjaw)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        zfcyk__iqrto = tuple(typing_info.typemap[humk__usrh.name] for
            humk__usrh in args)
        dxfq__biw = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, zfcyk__iqrto, {}, {}, flags)
        dxfq__biw.run()
    csmp__vtgq = f_ir.blocks.popitem()[1]
    replace_arg_nodes(csmp__vtgq, args)
    sau__gwbs = csmp__vtgq.body[:-2]
    update_locs(sau__gwbs[len(args):], loc)
    for stmt in sau__gwbs[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        ftkhh__uso = csmp__vtgq.body[-2]
        assert is_assign(ftkhh__uso) and is_expr(ftkhh__uso.value, 'cast')
        dyzdw__ylxn = ftkhh__uso.value.value
        sau__gwbs.append(ir.Assign(dyzdw__ylxn, ret_var, loc))
    return sau__gwbs


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for eaxq__vge in stmt.list_vars():
            eaxq__vge.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        elulv__zxqw = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        ioizb__gor, xxgkp__gqsey = elulv__zxqw(stmt)
        return xxgkp__gqsey
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        fetc__ehgh = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(fetc__ehgh, ir.UndefinedType):
            zvqr__kmrc = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{zvqr__kmrc}' is not defined", loc=loc)
    except GuardException as wsij__hfo:
        raise BodoError(err_msg, loc=loc)
    return fetc__ehgh


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    pyp__sno = get_definition(func_ir, var)
    gif__uby = None
    if typemap is not None:
        gif__uby = typemap.get(var.name, None)
    if isinstance(pyp__sno, ir.Arg) and arg_types is not None:
        gif__uby = arg_types[pyp__sno.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(gif__uby):
        return get_literal_value(gif__uby)
    if isinstance(pyp__sno, (ir.Const, ir.Global, ir.FreeVar)):
        fetc__ehgh = pyp__sno.value
        return fetc__ehgh
    if literalize_args and isinstance(pyp__sno, ir.Arg
        ) and can_literalize_type(gif__uby, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({pyp__sno.index}, loc=var.
            loc, file_infos={pyp__sno.index: file_info} if file_info is not
            None else None)
    if is_expr(pyp__sno, 'binop'):
        if file_info and pyp__sno.fn == operator.add:
            try:
                dlzre__ivucr = get_const_value_inner(func_ir, pyp__sno.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(dlzre__ivucr, True)
                vju__kcmmi = get_const_value_inner(func_ir, pyp__sno.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return pyp__sno.fn(dlzre__ivucr, vju__kcmmi)
            except (GuardException, BodoConstUpdatedError) as wsij__hfo:
                pass
            try:
                vju__kcmmi = get_const_value_inner(func_ir, pyp__sno.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(vju__kcmmi, False)
                dlzre__ivucr = get_const_value_inner(func_ir, pyp__sno.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return pyp__sno.fn(dlzre__ivucr, vju__kcmmi)
            except (GuardException, BodoConstUpdatedError) as wsij__hfo:
                pass
        dlzre__ivucr = get_const_value_inner(func_ir, pyp__sno.lhs,
            arg_types, typemap, updated_containers)
        vju__kcmmi = get_const_value_inner(func_ir, pyp__sno.rhs, arg_types,
            typemap, updated_containers)
        return pyp__sno.fn(dlzre__ivucr, vju__kcmmi)
    if is_expr(pyp__sno, 'unary'):
        fetc__ehgh = get_const_value_inner(func_ir, pyp__sno.value,
            arg_types, typemap, updated_containers)
        return pyp__sno.fn(fetc__ehgh)
    if is_expr(pyp__sno, 'getattr') and typemap:
        sdwo__ugitt = typemap.get(pyp__sno.value.name, None)
        if isinstance(sdwo__ugitt, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and pyp__sno.attr == 'columns':
            return pd.Index(sdwo__ugitt.columns)
        if isinstance(sdwo__ugitt, types.SliceType):
            say__ugnt = get_definition(func_ir, pyp__sno.value)
            require(is_call(say__ugnt))
            rgc__grcz = find_callname(func_ir, say__ugnt)
            ith__sfnug = False
            if rgc__grcz == ('_normalize_slice', 'numba.cpython.unicode'):
                require(pyp__sno.attr in ('start', 'step'))
                say__ugnt = get_definition(func_ir, say__ugnt.args[0])
                ith__sfnug = True
            require(find_callname(func_ir, say__ugnt) == ('slice', 'builtins'))
            if len(say__ugnt.args) == 1:
                if pyp__sno.attr == 'start':
                    return 0
                if pyp__sno.attr == 'step':
                    return 1
                require(pyp__sno.attr == 'stop')
                return get_const_value_inner(func_ir, say__ugnt.args[0],
                    arg_types, typemap, updated_containers)
            if pyp__sno.attr == 'start':
                fetc__ehgh = get_const_value_inner(func_ir, say__ugnt.args[
                    0], arg_types, typemap, updated_containers)
                if fetc__ehgh is None:
                    fetc__ehgh = 0
                if ith__sfnug:
                    require(fetc__ehgh == 0)
                return fetc__ehgh
            if pyp__sno.attr == 'stop':
                assert not ith__sfnug
                return get_const_value_inner(func_ir, say__ugnt.args[1],
                    arg_types, typemap, updated_containers)
            require(pyp__sno.attr == 'step')
            if len(say__ugnt.args) == 2:
                return 1
            else:
                fetc__ehgh = get_const_value_inner(func_ir, say__ugnt.args[
                    2], arg_types, typemap, updated_containers)
                if fetc__ehgh is None:
                    fetc__ehgh = 1
                if ith__sfnug:
                    require(fetc__ehgh == 1)
                return fetc__ehgh
    if is_expr(pyp__sno, 'getattr'):
        return getattr(get_const_value_inner(func_ir, pyp__sno.value,
            arg_types, typemap, updated_containers), pyp__sno.attr)
    if is_expr(pyp__sno, 'getitem'):
        value = get_const_value_inner(func_ir, pyp__sno.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, pyp__sno.index, arg_types,
            typemap, updated_containers)
        return value[index]
    yhnfw__miijl = guard(find_callname, func_ir, pyp__sno, typemap)
    if yhnfw__miijl is not None and len(yhnfw__miijl) == 2 and yhnfw__miijl[0
        ] == 'keys' and isinstance(yhnfw__miijl[1], ir.Var):
        neqbx__sdkr = pyp__sno.func
        pyp__sno = get_definition(func_ir, yhnfw__miijl[1])
        cfijh__kbu = yhnfw__miijl[1].name
        if updated_containers and cfijh__kbu in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                cfijh__kbu, updated_containers[cfijh__kbu]))
        require(is_expr(pyp__sno, 'build_map'))
        vals = [eaxq__vge[0] for eaxq__vge in pyp__sno.items]
        efcz__rad = guard(get_definition, func_ir, neqbx__sdkr)
        assert isinstance(efcz__rad, ir.Expr) and efcz__rad.attr == 'keys'
        efcz__rad.attr = 'copy'
        return [get_const_value_inner(func_ir, eaxq__vge, arg_types,
            typemap, updated_containers) for eaxq__vge in vals]
    if is_expr(pyp__sno, 'build_map'):
        return {get_const_value_inner(func_ir, eaxq__vge[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            eaxq__vge[1], arg_types, typemap, updated_containers) for
            eaxq__vge in pyp__sno.items}
    if is_expr(pyp__sno, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, eaxq__vge, arg_types,
            typemap, updated_containers) for eaxq__vge in pyp__sno.items)
    if is_expr(pyp__sno, 'build_list'):
        return [get_const_value_inner(func_ir, eaxq__vge, arg_types,
            typemap, updated_containers) for eaxq__vge in pyp__sno.items]
    if is_expr(pyp__sno, 'build_set'):
        return {get_const_value_inner(func_ir, eaxq__vge, arg_types,
            typemap, updated_containers) for eaxq__vge in pyp__sno.items}
    if yhnfw__miijl == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, pyp__sno.args[0], arg_types,
            typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if yhnfw__miijl == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers))
    if yhnfw__miijl == ('range', 'builtins') and len(pyp__sno.args) == 1:
        return range(get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers))
    if yhnfw__miijl == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, eaxq__vge,
            arg_types, typemap, updated_containers) for eaxq__vge in
            pyp__sno.args))
    if yhnfw__miijl == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers))
    if yhnfw__miijl == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers))
    if yhnfw__miijl == ('format', 'builtins'):
        humk__usrh = get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers)
        fabiz__vttxc = get_const_value_inner(func_ir, pyp__sno.args[1],
            arg_types, typemap, updated_containers) if len(pyp__sno.args
            ) > 1 else ''
        return format(humk__usrh, fabiz__vttxc)
    if yhnfw__miijl in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers))
    if yhnfw__miijl == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers))
    if yhnfw__miijl == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, pyp__sno.args[0
            ], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, pyp__sno.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            pyp__sno.args[2], arg_types, typemap, updated_containers))
    if yhnfw__miijl == ('len', 'builtins') and typemap and isinstance(typemap
        .get(pyp__sno.args[0].name, None), types.BaseTuple):
        return len(typemap[pyp__sno.args[0].name])
    if yhnfw__miijl == ('len', 'builtins'):
        tmy__myfm = guard(get_definition, func_ir, pyp__sno.args[0])
        if isinstance(tmy__myfm, ir.Expr) and tmy__myfm.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(tmy__myfm.items)
        return len(get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers))
    if yhnfw__miijl == ('CategoricalDtype', 'pandas'):
        kws = dict(pyp__sno.kws)
        fahq__ogdpn = get_call_expr_arg('CategoricalDtype', pyp__sno.args,
            kws, 0, 'categories', '')
        mnb__ttfb = get_call_expr_arg('CategoricalDtype', pyp__sno.args,
            kws, 1, 'ordered', False)
        if mnb__ttfb is not False:
            mnb__ttfb = get_const_value_inner(func_ir, mnb__ttfb, arg_types,
                typemap, updated_containers)
        if fahq__ogdpn == '':
            fahq__ogdpn = None
        else:
            fahq__ogdpn = get_const_value_inner(func_ir, fahq__ogdpn,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(fahq__ogdpn, mnb__ttfb)
    if yhnfw__miijl == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, pyp__sno.args[0],
            arg_types, typemap, updated_containers))
    if yhnfw__miijl is not None and len(yhnfw__miijl) == 2 and yhnfw__miijl[1
        ] == 'pandas' and yhnfw__miijl[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, yhnfw__miijl[0])()
    if yhnfw__miijl is not None and len(yhnfw__miijl) == 2 and isinstance(
        yhnfw__miijl[1], ir.Var):
        fetc__ehgh = get_const_value_inner(func_ir, yhnfw__miijl[1],
            arg_types, typemap, updated_containers)
        args = [get_const_value_inner(func_ir, eaxq__vge, arg_types,
            typemap, updated_containers) for eaxq__vge in pyp__sno.args]
        kws = {yofm__vaeka[0]: get_const_value_inner(func_ir, yofm__vaeka[1
            ], arg_types, typemap, updated_containers) for yofm__vaeka in
            pyp__sno.kws}
        return getattr(fetc__ehgh, yhnfw__miijl[0])(*args, **kws)
    if yhnfw__miijl is not None and len(yhnfw__miijl) == 2 and yhnfw__miijl[1
        ] == 'bodo' and yhnfw__miijl[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, eaxq__vge, arg_types,
            typemap, updated_containers) for eaxq__vge in pyp__sno.args)
        kwargs = {zvqr__kmrc: get_const_value_inner(func_ir, eaxq__vge,
            arg_types, typemap, updated_containers) for zvqr__kmrc,
            eaxq__vge in dict(pyp__sno.kws).items()}
        return getattr(bodo, yhnfw__miijl[0])(*args, **kwargs)
    if is_call(pyp__sno) and typemap and isinstance(typemap.get(pyp__sno.
        func.name, None), types.Dispatcher):
        py_func = typemap[pyp__sno.func.name].dispatcher.py_func
        require(pyp__sno.vararg is None)
        args = tuple(get_const_value_inner(func_ir, eaxq__vge, arg_types,
            typemap, updated_containers) for eaxq__vge in pyp__sno.args)
        kwargs = {zvqr__kmrc: get_const_value_inner(func_ir, eaxq__vge,
            arg_types, typemap, updated_containers) for zvqr__kmrc,
            eaxq__vge in dict(pyp__sno.kws).items()}
        arg_types = tuple(bodo.typeof(eaxq__vge) for eaxq__vge in args)
        kw_types = {racf__imbz: bodo.typeof(eaxq__vge) for racf__imbz,
            eaxq__vge in kwargs.items()}
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
    f_ir, typemap, larf__nrfog, larf__nrfog = bodo.compiler.get_func_type_info(
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
                    tydpx__wppi = guard(get_definition, f_ir, rhs.func)
                    if isinstance(tydpx__wppi, ir.Const) and isinstance(
                        tydpx__wppi.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    cjye__vxaw = guard(find_callname, f_ir, rhs)
                    if cjye__vxaw is None:
                        return False
                    func_name, aatu__lon = cjye__vxaw
                    if aatu__lon == 'pandas' and func_name.startswith('read_'):
                        return False
                    if cjye__vxaw in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if cjye__vxaw == ('File', 'h5py'):
                        return False
                    if isinstance(aatu__lon, ir.Var):
                        gif__uby = typemap[aatu__lon.name]
                        if isinstance(gif__uby, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(gif__uby, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(gif__uby, bodo.LoggingLoggerType):
                            return False
                        if str(gif__uby).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            aatu__lon), ir.Arg)):
                            return False
                    if aatu__lon in ('numpy.random', 'time', 'logging',
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
        dmlsf__kain = func.literal_value.code
        aamp__oyxol = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            aamp__oyxol = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(aamp__oyxol, dmlsf__kain)
        fix_struct_return(f_ir)
        typemap, omhu__uojet, nobxf__shug, larf__nrfog = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, nobxf__shug, omhu__uojet = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, nobxf__shug, omhu__uojet = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, nobxf__shug, omhu__uojet = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(omhu__uojet, types.DictType):
        voami__woe = guard(get_struct_keynames, f_ir, typemap)
        if voami__woe is not None:
            omhu__uojet = StructType((omhu__uojet.value_type,) * len(
                voami__woe), voami__woe)
    if is_udf and isinstance(omhu__uojet, (SeriesType, HeterogeneousSeriesType)
        ):
        ucgh__djbp = numba.core.registry.cpu_target.typing_context
        qcco__ydca = numba.core.registry.cpu_target.target_context
        dyfko__ebbk = bodo.transforms.series_pass.SeriesPass(f_ir,
            ucgh__djbp, qcco__ydca, typemap, nobxf__shug, {})
        dyfko__ebbk.run()
        dyfko__ebbk.run()
        dyfko__ebbk.run()
        mkd__wvzz = compute_cfg_from_blocks(f_ir.blocks)
        ulf__apw = [guard(_get_const_series_info, f_ir.blocks[flr__hmkaq],
            f_ir, typemap) for flr__hmkaq in mkd__wvzz.exit_points() if
            isinstance(f_ir.blocks[flr__hmkaq].body[-1], ir.Return)]
        if None in ulf__apw or len(pd.Series(ulf__apw).unique()) != 1:
            omhu__uojet.const_info = None
        else:
            omhu__uojet.const_info = ulf__apw[0]
    return omhu__uojet


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    mapaa__rnwh = block.body[-1].value
    hatd__smxli = get_definition(f_ir, mapaa__rnwh)
    require(is_expr(hatd__smxli, 'cast'))
    hatd__smxli = get_definition(f_ir, hatd__smxli.value)
    require(is_call(hatd__smxli) and find_callname(f_ir, hatd__smxli) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    sjlo__jypl = hatd__smxli.args[1]
    gur__gxil = tuple(get_const_value_inner(f_ir, sjlo__jypl, typemap=typemap))
    if isinstance(typemap[mapaa__rnwh.name], HeterogeneousSeriesType):
        return len(typemap[mapaa__rnwh.name].data), gur__gxil
    gprp__xafgn = hatd__smxli.args[0]
    wipw__tkxh = get_definition(f_ir, gprp__xafgn)
    func_name, upv__nmvo = find_callname(f_ir, wipw__tkxh)
    if is_call(wipw__tkxh) and bodo.utils.utils.is_alloc_callname(func_name,
        upv__nmvo):
        vmmws__qqbya = wipw__tkxh.args[0]
        kkhwn__xtos = get_const_value_inner(f_ir, vmmws__qqbya, typemap=typemap
            )
        return kkhwn__xtos, gur__gxil
    if is_call(wipw__tkxh) and find_callname(f_ir, wipw__tkxh) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        gprp__xafgn = wipw__tkxh.args[0]
        wipw__tkxh = get_definition(f_ir, gprp__xafgn)
    require(is_expr(wipw__tkxh, 'build_tuple') or is_expr(wipw__tkxh,
        'build_list'))
    return len(wipw__tkxh.items), gur__gxil


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    yfmp__ttbr = []
    vprw__amn = []
    values = []
    for racf__imbz, eaxq__vge in build_map.items:
        oecv__jtghc = find_const(f_ir, racf__imbz)
        require(isinstance(oecv__jtghc, str))
        vprw__amn.append(oecv__jtghc)
        yfmp__ttbr.append(racf__imbz)
        values.append(eaxq__vge)
    wyfr__eef = ir.Var(scope, mk_unique_var('val_tup'), loc)
    xmrn__vbtj = ir.Assign(ir.Expr.build_tuple(values, loc), wyfr__eef, loc)
    f_ir._definitions[wyfr__eef.name] = [xmrn__vbtj.value]
    uii__kmh = ir.Var(scope, mk_unique_var('key_tup'), loc)
    xfr__uinmc = ir.Assign(ir.Expr.build_tuple(yfmp__ttbr, loc), uii__kmh, loc)
    f_ir._definitions[uii__kmh.name] = [xfr__uinmc.value]
    if typemap is not None:
        typemap[wyfr__eef.name] = types.Tuple([typemap[eaxq__vge.name] for
            eaxq__vge in values])
        typemap[uii__kmh.name] = types.Tuple([typemap[eaxq__vge.name] for
            eaxq__vge in yfmp__ttbr])
    return vprw__amn, wyfr__eef, xmrn__vbtj, uii__kmh, xfr__uinmc


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    hudyb__exd = block.body[-1].value
    rpezi__tjim = guard(get_definition, f_ir, hudyb__exd)
    require(is_expr(rpezi__tjim, 'cast'))
    hatd__smxli = guard(get_definition, f_ir, rpezi__tjim.value)
    require(is_expr(hatd__smxli, 'build_map'))
    require(len(hatd__smxli.items) > 0)
    loc = block.loc
    scope = block.scope
    vprw__amn, wyfr__eef, xmrn__vbtj, uii__kmh, xfr__uinmc = (
        extract_keyvals_from_struct_map(f_ir, hatd__smxli, loc, scope))
    spc__xmvxf = ir.Var(scope, mk_unique_var('conv_call'), loc)
    jox__hopk = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), spc__xmvxf, loc)
    f_ir._definitions[spc__xmvxf.name] = [jox__hopk.value]
    pyubp__ycz = ir.Var(scope, mk_unique_var('struct_val'), loc)
    slu__tpb = ir.Assign(ir.Expr.call(spc__xmvxf, [wyfr__eef, uii__kmh], {},
        loc), pyubp__ycz, loc)
    f_ir._definitions[pyubp__ycz.name] = [slu__tpb.value]
    rpezi__tjim.value = pyubp__ycz
    hatd__smxli.items = [(racf__imbz, racf__imbz) for racf__imbz,
        larf__nrfog in hatd__smxli.items]
    block.body = block.body[:-2] + [xmrn__vbtj, xfr__uinmc, jox__hopk, slu__tpb
        ] + block.body[-2:]
    return tuple(vprw__amn)


def get_struct_keynames(f_ir, typemap):
    mkd__wvzz = compute_cfg_from_blocks(f_ir.blocks)
    pgoe__dcca = list(mkd__wvzz.exit_points())[0]
    block = f_ir.blocks[pgoe__dcca]
    require(isinstance(block.body[-1], ir.Return))
    hudyb__exd = block.body[-1].value
    rpezi__tjim = guard(get_definition, f_ir, hudyb__exd)
    require(is_expr(rpezi__tjim, 'cast'))
    hatd__smxli = guard(get_definition, f_ir, rpezi__tjim.value)
    require(is_call(hatd__smxli) and find_callname(f_ir, hatd__smxli) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[hatd__smxli.args[1].name])


def fix_struct_return(f_ir):
    ucsr__kdg = None
    mkd__wvzz = compute_cfg_from_blocks(f_ir.blocks)
    for pgoe__dcca in mkd__wvzz.exit_points():
        ucsr__kdg = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            pgoe__dcca], pgoe__dcca)
    return ucsr__kdg


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    wyuyy__rkrx = ir.Block(ir.Scope(None, loc), loc)
    wyuyy__rkrx.body = node_list
    build_definitions({(0): wyuyy__rkrx}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(eaxq__vge) for eaxq__vge in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    ica__fcdhm = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(ica__fcdhm, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for oswu__ektur in range(len(vals) - 1, -1, -1):
        eaxq__vge = vals[oswu__ektur]
        if isinstance(eaxq__vge, str) and eaxq__vge.startswith(
            NESTED_TUP_SENTINEL):
            egswo__vaoi = int(eaxq__vge[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:oswu__ektur]) + (
                tuple(vals[oswu__ektur + 1:oswu__ektur + egswo__vaoi + 1]),
                ) + tuple(vals[oswu__ektur + egswo__vaoi + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    humk__usrh = None
    if len(args) > arg_no and arg_no >= 0:
        humk__usrh = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        humk__usrh = kws[arg_name]
    if humk__usrh is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return humk__usrh


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
    bmd__sjaw = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        bmd__sjaw.update(extra_globals)
    func.__globals__.update(bmd__sjaw)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            mdk__fny = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[mdk__fny.name] = types.literal(default)
            except:
                pass_info.typemap[mdk__fny.name] = numba.typeof(default)
            ljttd__vyv = ir.Assign(ir.Const(default, loc), mdk__fny, loc)
            pre_nodes.append(ljttd__vyv)
            return mdk__fny
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    zfcyk__iqrto = tuple(pass_info.typemap[eaxq__vge.name] for eaxq__vge in
        args)
    if const:
        rusv__dzq = []
        for oswu__ektur, humk__usrh in enumerate(args):
            fetc__ehgh = guard(find_const, pass_info.func_ir, humk__usrh)
            if fetc__ehgh:
                rusv__dzq.append(types.literal(fetc__ehgh))
            else:
                rusv__dzq.append(zfcyk__iqrto[oswu__ektur])
        zfcyk__iqrto = tuple(rusv__dzq)
    return ReplaceFunc(func, zfcyk__iqrto, args, bmd__sjaw,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(tczz__swssq) for tczz__swssq in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        fzl__ipgsh = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {fzl__ipgsh} = 0\n', (fzl__ipgsh,)
    if isinstance(t, ArrayItemArrayType):
        wvizl__vmyta, rkfc__oxp = gen_init_varsize_alloc_sizes(t.dtype)
        fzl__ipgsh = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {fzl__ipgsh} = 0\n' + wvizl__vmyta, (fzl__ipgsh,
            ) + rkfc__oxp
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
        return 1 + sum(get_type_alloc_counts(tczz__swssq.dtype) for
            tczz__swssq in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(tczz__swssq) for tczz__swssq in t.data
            )
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(tczz__swssq) for tczz__swssq in t.
            types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    ogpba__yhuv = typing_context.resolve_getattr(obj_dtype, func_name)
    if ogpba__yhuv is None:
        pdyd__qmaj = types.misc.Module(np)
        try:
            ogpba__yhuv = typing_context.resolve_getattr(pdyd__qmaj, func_name)
        except AttributeError as wsij__hfo:
            ogpba__yhuv = None
        if ogpba__yhuv is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return ogpba__yhuv


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    ogpba__yhuv = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(ogpba__yhuv, types.BoundFunction):
        if axis is not None:
            vug__kpdyx = ogpba__yhuv.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            vug__kpdyx = ogpba__yhuv.get_call_type(typing_context, (), {})
        return vug__kpdyx.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(ogpba__yhuv):
            vug__kpdyx = ogpba__yhuv.get_call_type(typing_context, (
                obj_dtype,), {})
            return vug__kpdyx.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    ogpba__yhuv = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(ogpba__yhuv, types.BoundFunction):
        iugb__dnev = ogpba__yhuv.template
        if axis is not None:
            return iugb__dnev._overload_func(obj_dtype, axis=axis)
        else:
            return iugb__dnev._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    qudty__wujk = get_definition(func_ir, dict_var)
    require(isinstance(qudty__wujk, ir.Expr))
    require(qudty__wujk.op == 'build_map')
    jen__wps = qudty__wujk.items
    yfmp__ttbr = []
    values = []
    suv__tmsf = False
    for oswu__ektur in range(len(jen__wps)):
        asatk__wnk, value = jen__wps[oswu__ektur]
        try:
            idfoj__mduws = get_const_value_inner(func_ir, asatk__wnk,
                arg_types, typemap, updated_containers)
            yfmp__ttbr.append(idfoj__mduws)
            values.append(value)
        except GuardException as wsij__hfo:
            require_const_map[asatk__wnk] = label
            suv__tmsf = True
    if suv__tmsf:
        raise GuardException
    return yfmp__ttbr, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        yfmp__ttbr = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as wsij__hfo:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in yfmp__ttbr):
        raise BodoError(err_msg, loc)
    return yfmp__ttbr


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    yfmp__ttbr = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    kjv__khzct = []
    zbeu__csrft = [bodo.transforms.typing_pass._create_const_var(racf__imbz,
        'dict_key', scope, loc, kjv__khzct) for racf__imbz in yfmp__ttbr]
    tenq__vjm = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        igyq__rzqu = ir.Var(scope, mk_unique_var('sentinel'), loc)
        hvccw__nrwb = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        kjv__khzct.append(ir.Assign(ir.Const('__bodo_tup', loc), igyq__rzqu,
            loc))
        rywz__ufpcd = [igyq__rzqu] + zbeu__csrft + tenq__vjm
        kjv__khzct.append(ir.Assign(ir.Expr.build_tuple(rywz__ufpcd, loc),
            hvccw__nrwb, loc))
        return (hvccw__nrwb,), kjv__khzct
    else:
        jfrrm__jmqm = ir.Var(scope, mk_unique_var('values_tup'), loc)
        ymgzj__trtbs = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        kjv__khzct.append(ir.Assign(ir.Expr.build_tuple(tenq__vjm, loc),
            jfrrm__jmqm, loc))
        kjv__khzct.append(ir.Assign(ir.Expr.build_tuple(zbeu__csrft, loc),
            ymgzj__trtbs, loc))
        return (jfrrm__jmqm, ymgzj__trtbs), kjv__khzct
