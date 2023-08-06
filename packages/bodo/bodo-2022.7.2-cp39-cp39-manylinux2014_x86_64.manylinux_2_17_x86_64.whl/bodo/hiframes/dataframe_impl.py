"""
Implementation of DataFrame attributes and methods using overload.
"""
import operator
import re
import warnings
from collections import namedtuple
from typing import Tuple
import numba
import numpy as np
import pandas as pd
from numba.core import cgutils, ir, types
from numba.core.imputils import RefType, impl_ret_borrowed, impl_ret_new_ref, iternext_impl, lower_builtin
from numba.core.ir_utils import mk_unique_var, next_label
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_getattr, models, overload, overload_attribute, overload_method, register_model, type_callable
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import _no_input, datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported, handle_inplace_df_type_change
from bodo.hiframes.pd_index_ext import DatetimeIndexType, RangeIndexType, StringIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType, if_series_to_array_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array, boolean_dtype
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils import tracing
from bodo.utils.transform import bodo_types_with_params, gen_const_tup, no_side_effect_call_tuples
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, dtype_to_array_type, ensure_constant_arg, ensure_constant_values, get_index_data_arr_types, get_index_names, get_literal_value, get_nullable_and_non_nullable_types, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_overload_constant_dict, get_overload_constant_series, is_common_scalar_dtype, is_literal_type, is_overload_bool, is_overload_bool_list, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_series, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, parse_dtype, raise_bodo_error, unliteral_val
from bodo.utils.utils import is_array_typ


@overload_attribute(DataFrameType, 'index', inline='always')
def overload_dataframe_index(df):
    return lambda df: bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)


def generate_col_to_index_func_text(col_names: Tuple):
    if all(isinstance(a, str) for a in col_names) or all(isinstance(a,
        bytes) for a in col_names):
        frz__uaywy = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({frz__uaywy})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    eqvpl__klnl = 'def impl(df):\n'
    if df.has_runtime_cols:
        eqvpl__klnl += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        dzknw__livtg = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        eqvpl__klnl += f'  return {dzknw__livtg}'
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo}, php__dced)
    impl = php__dced['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    xka__jnytf = len(df.columns)
    twxhd__kex = set(i for i in range(xka__jnytf) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in twxhd__kex else '') for i in
        range(xka__jnytf))
    eqvpl__klnl = 'def f(df):\n'.format()
    eqvpl__klnl += '    return np.stack(({},), 1)\n'.format(data_args)
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo, 'np': np}, php__dced)
    lflzt__iijm = php__dced['f']
    return lflzt__iijm


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    yhgff__eagi = {'dtype': dtype, 'na_value': na_value}
    cep__fvt = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', yhgff__eagi, cep__fvt,
        package_name='pandas', module_name='DataFrame')

    def impl(df, dtype=None, copy=False, na_value=_no_input):
        return df.values
    return impl


@overload_attribute(DataFrameType, 'ndim', inline='always')
def overload_dataframe_ndim(df):
    return lambda df: 2


@overload_attribute(DataFrameType, 'size')
def overload_dataframe_size(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            amaq__gbsi = bodo.hiframes.table.compute_num_runtime_columns(t)
            return amaq__gbsi * len(t)
        return impl
    ncols = len(df.columns)
    return lambda df: ncols * len(df)


@lower_getattr(DataFrameType, 'shape')
def lower_dataframe_shape(context, builder, typ, val):
    impl = overload_dataframe_shape(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def overload_dataframe_shape(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            amaq__gbsi = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), amaq__gbsi
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    eqvpl__klnl = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    zmf__lvgqa = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    eqvpl__klnl += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{zmf__lvgqa}), {index}, None)
"""
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo}, php__dced)
    impl = php__dced['impl']
    return impl


@overload_attribute(DataFrameType, 'empty')
def overload_dataframe_empty(df):
    check_runtime_cols_unsupported(df, 'DataFrame.empty')
    if len(df.columns) == 0:
        return lambda df: True
    return lambda df: len(df) == 0


@overload_method(DataFrameType, 'assign', no_unliteral=True)
def overload_dataframe_assign(df, **kwargs):
    check_runtime_cols_unsupported(df, 'DataFrame.assign()')
    raise_bodo_error('Invalid df.assign() call')


@overload_method(DataFrameType, 'insert', no_unliteral=True)
def overload_dataframe_insert(df, loc, column, value, allow_duplicates=False):
    check_runtime_cols_unsupported(df, 'DataFrame.insert()')
    raise_bodo_error('Invalid df.insert() call')


def _get_dtype_str(dtype):
    if isinstance(dtype, types.Function):
        if dtype.key[0] == str:
            return "'str'"
        elif dtype.key[0] == float:
            return 'float'
        elif dtype.key[0] == int:
            return 'int'
        elif dtype.key[0] == bool:
            return 'bool'
        else:
            raise BodoError(f'invalid dtype: {dtype}')
    if type(dtype) in bodo.libs.int_arr_ext.pd_int_dtype_classes:
        return dtype.name
    if isinstance(dtype, types.DTypeSpec):
        dtype = dtype.dtype
    if isinstance(dtype, types.functions.NumberClass):
        return f"'{dtype.key}'"
    if isinstance(dtype, types.PyObject) or dtype in (object, 'object'):
        return "'object'"
    if dtype in (bodo.libs.str_arr_ext.string_dtype, pd.StringDtype()):
        return 'str'
    return f"'{dtype}'"


@overload_method(DataFrameType, 'astype', inline='always', no_unliteral=True)
def overload_dataframe_astype(df, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True, _bodo_object_typeref=None):
    check_runtime_cols_unsupported(df, 'DataFrame.astype()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.astype()')
    yhgff__eagi = {'copy': copy, 'errors': errors}
    cep__fvt = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', yhgff__eagi, cep__fvt, package_name
        ='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    extra_globals = None
    header = """def impl(df, dtype, copy=True, errors='raise', _bodo_nan_to_str=True, _bodo_object_typeref=None):
"""
    if df.is_table_format:
        extra_globals = {}
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        zamh__nzmkv = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        aejdr__xouan = _bodo_object_typeref.instance_type
        assert isinstance(aejdr__xouan, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in aejdr__xouan.column_index:
                    idx = aejdr__xouan.column_index[name]
                    arr_typ = aejdr__xouan.data[idx]
                else:
                    arr_typ = df.data[i]
                zamh__nzmkv.append(arr_typ)
        else:
            extra_globals = {}
            gxit__tvao = {}
            for i, name in enumerate(aejdr__xouan.columns):
                arr_typ = aejdr__xouan.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    vbxvh__ufw = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    vbxvh__ufw = boolean_dtype
                else:
                    vbxvh__ufw = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = vbxvh__ufw
                gxit__tvao[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {gxit__tvao[olf__njln]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if olf__njln in gxit__tvao else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, olf__njln in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        cekz__cdtxc = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            cekz__cdtxc = {name: dtype_to_array_type(parse_dtype(dtype)) for
                name, dtype in cekz__cdtxc.items()}
            for i, name in enumerate(df.columns):
                if name in cekz__cdtxc:
                    arr_typ = cekz__cdtxc[name]
                else:
                    arr_typ = df.data[i]
                zamh__nzmkv.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(cekz__cdtxc[olf__njln])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if olf__njln in cekz__cdtxc else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, olf__njln in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        zamh__nzmkv = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        qfha__mdsy = bodo.TableType(tuple(zamh__nzmkv))
        extra_globals['out_table_typ'] = qfha__mdsy
        data_args = (
            'bodo.utils.table_utils.table_astype(table, out_table_typ, copy, _bodo_nan_to_str)'
            )
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'copy', inline='always', no_unliteral=True)
def overload_dataframe_copy(df, deep=True):
    check_runtime_cols_unsupported(df, 'DataFrame.copy()')
    header = 'def impl(df, deep=True):\n'
    extra_globals = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        yumlc__yxxb = types.none
        extra_globals = {'output_arr_typ': yumlc__yxxb}
        if is_overload_false(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if deep else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        fjd__odz = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                fjd__odz.append(arr + '.copy()')
            elif is_overload_false(deep):
                fjd__odz.append(arr)
            else:
                fjd__odz.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(fjd__odz)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    yhgff__eagi = {'index': index, 'level': level, 'errors': errors}
    cep__fvt = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', yhgff__eagi, cep__fvt,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.rename(): 'inplace' keyword only supports boolean constant assignment"
            )
    if not is_overload_none(mapper):
        if not is_overload_none(columns):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'mapper' and 'columns'"
                )
        if not (is_overload_constant_int(axis) and get_overload_const_int(
            axis) == 1):
            raise BodoError(
                "DataFrame.rename(): 'mapper' only supported with axis=1")
        if not is_overload_constant_dict(mapper):
            raise_bodo_error(
                "'mapper' argument to DataFrame.rename() should be a constant dictionary"
                )
        ocu__awnb = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        ocu__awnb = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    bouh__rwr = tuple([ocu__awnb.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    bhyq__bxsgt = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        bhyq__bxsgt = df.copy(columns=bouh__rwr)
        yumlc__yxxb = types.none
        extra_globals = {'output_arr_typ': yumlc__yxxb}
        if is_overload_false(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if copy else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        fjd__odz = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                fjd__odz.append(arr + '.copy()')
            elif is_overload_false(copy):
                fjd__odz.append(arr)
            else:
                fjd__odz.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(fjd__odz)
    return _gen_init_df(header, bouh__rwr, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    rpsz__gpaw = not is_overload_none(items)
    ibe__wfpu = not is_overload_none(like)
    pvuj__aulro = not is_overload_none(regex)
    pgytl__cuvi = rpsz__gpaw ^ ibe__wfpu ^ pvuj__aulro
    axq__veqgx = not (rpsz__gpaw or ibe__wfpu or pvuj__aulro)
    if axq__veqgx:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not pgytl__cuvi:
        raise BodoError(
            'DataFrame.filter(): keyword arguments `items`, `like`, and `regex` are mutually exclusive'
            )
    if is_overload_none(axis):
        axis = 'columns'
    if is_overload_constant_str(axis):
        axis = get_overload_const_str(axis)
        if axis not in {'index', 'columns'}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either "index" or "columns" if string'
                )
        tkp__ejem = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        tkp__ejem = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert tkp__ejem in {0, 1}
    eqvpl__klnl = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if tkp__ejem == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if tkp__ejem == 1:
        vrqw__mxkv = []
        pouff__qsb = []
        nvrb__jnv = []
        if rpsz__gpaw:
            if is_overload_constant_list(items):
                yrnt__cdz = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if ibe__wfpu:
            if is_overload_constant_str(like):
                rjlht__ltrt = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if pvuj__aulro:
            if is_overload_constant_str(regex):
                ppkn__mvp = get_overload_const_str(regex)
                mwkaw__gcad = re.compile(ppkn__mvp)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, olf__njln in enumerate(df.columns):
            if not is_overload_none(items
                ) and olf__njln in yrnt__cdz or not is_overload_none(like
                ) and rjlht__ltrt in str(olf__njln) or not is_overload_none(
                regex) and mwkaw__gcad.search(str(olf__njln)):
                pouff__qsb.append(olf__njln)
                nvrb__jnv.append(i)
        for i in nvrb__jnv:
            var_name = f'data_{i}'
            vrqw__mxkv.append(var_name)
            eqvpl__klnl += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(vrqw__mxkv)
        return _gen_init_df(eqvpl__klnl, pouff__qsb, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    bhyq__bxsgt = None
    if df.is_table_format:
        yumlc__yxxb = types.Array(types.bool_, 1, 'C')
        bhyq__bxsgt = DataFrameType(tuple([yumlc__yxxb] * len(df.data)), df
            .index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': yumlc__yxxb}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'select_dtypes', inline='always',
    no_unliteral=True)
def overload_dataframe_select_dtypes(df, include=None, exclude=None):
    check_runtime_cols_unsupported(df, 'DataFrame.select_dtypes')
    spjr__bvena = is_overload_none(include)
    yro__siu = is_overload_none(exclude)
    hvje__lyawm = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if spjr__bvena and yro__siu:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not spjr__bvena:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            kbii__suuo = [dtype_to_array_type(parse_dtype(elem, hvje__lyawm
                )) for elem in include]
        elif is_legal_input(include):
            kbii__suuo = [dtype_to_array_type(parse_dtype(include,
                hvje__lyawm))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        kbii__suuo = get_nullable_and_non_nullable_types(kbii__suuo)
        fll__fakff = tuple(olf__njln for i, olf__njln in enumerate(df.
            columns) if df.data[i] in kbii__suuo)
    else:
        fll__fakff = df.columns
    if not yro__siu:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            xzoo__guy = [dtype_to_array_type(parse_dtype(elem, hvje__lyawm)
                ) for elem in exclude]
        elif is_legal_input(exclude):
            xzoo__guy = [dtype_to_array_type(parse_dtype(exclude, hvje__lyawm))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        xzoo__guy = get_nullable_and_non_nullable_types(xzoo__guy)
        fll__fakff = tuple(olf__njln for olf__njln in fll__fakff if df.data
            [df.column_index[olf__njln]] not in xzoo__guy)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[olf__njln]})'
         for olf__njln in fll__fakff)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, fll__fakff, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    bhyq__bxsgt = None
    if df.is_table_format:
        yumlc__yxxb = types.Array(types.bool_, 1, 'C')
        bhyq__bxsgt = DataFrameType(tuple([yumlc__yxxb] * len(df.data)), df
            .index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': yumlc__yxxb}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'~bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})) == False'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


def overload_dataframe_head(df, n=5):
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[:n]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:n]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:n]'
    return _gen_init_df(header, df.columns, data_args, index)


@lower_builtin('df.head', DataFrameType, types.Integer)
@lower_builtin('df.head', DataFrameType, types.Omitted)
def dataframe_head_lower(context, builder, sig, args):
    impl = overload_dataframe_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'tail', inline='always', no_unliteral=True)
def overload_dataframe_tail(df, n=5):
    check_runtime_cols_unsupported(df, 'DataFrame.tail()')
    if not is_overload_int(n):
        raise BodoError("Dataframe.tail(): 'n' must be an Integer")
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[m:]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[m:]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    header += '  m = bodo.hiframes.series_impl.tail_slice(len(df), n)\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[m:]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'first', inline='always', no_unliteral=True)
def overload_dataframe_first(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.first()')
    pgj__xhuo = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in pgj__xhuo:
        raise BodoError(
            "DataFrame.first(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.first()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:valid_entries]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:valid_entries]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    start_date = df_index[0]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, start_date, False)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'last', inline='always', no_unliteral=True)
def overload_dataframe_last(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.last()')
    pgj__xhuo = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in pgj__xhuo:
        raise BodoError(
            "DataFrame.last(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.last()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[len(df)-valid_entries:]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[len(df)-valid_entries:]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    final_date = df_index[-1]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, final_date, True)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'to_string', no_unliteral=True)
def to_string_overload(df, buf=None, columns=None, col_space=None, header=
    True, index=True, na_rep='NaN', formatters=None, float_format=None,
    sparsify=None, index_names=True, justify=None, max_rows=None, min_rows=
    None, max_cols=None, show_dimensions=False, decimal='.', line_width=
    None, max_colwidth=None, encoding=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_string()')

    def impl(df, buf=None, columns=None, col_space=None, header=True, index
        =True, na_rep='NaN', formatters=None, float_format=None, sparsify=
        None, index_names=True, justify=None, max_rows=None, min_rows=None,
        max_cols=None, show_dimensions=False, decimal='.', line_width=None,
        max_colwidth=None, encoding=None):
        with numba.objmode(res='string'):
            res = df.to_string(buf=buf, columns=columns, col_space=
                col_space, header=header, index=index, na_rep=na_rep,
                formatters=formatters, float_format=float_format, sparsify=
                sparsify, index_names=index_names, justify=justify,
                max_rows=max_rows, min_rows=min_rows, max_cols=max_cols,
                show_dimensions=show_dimensions, decimal=decimal,
                line_width=line_width, max_colwidth=max_colwidth, encoding=
                encoding)
        return res
    return impl


@overload_method(DataFrameType, 'isin', inline='always', no_unliteral=True)
def overload_dataframe_isin(df, values):
    check_runtime_cols_unsupported(df, 'DataFrame.isin()')
    from bodo.utils.typing import is_iterable_type
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.isin()')
    eqvpl__klnl = 'def impl(df, values):\n'
    hiehk__ilvcs = {}
    nkyl__xivj = False
    if isinstance(values, DataFrameType):
        nkyl__xivj = True
        for i, olf__njln in enumerate(df.columns):
            if olf__njln in values.column_index:
                zmjik__odqcr = 'val{}'.format(i)
                eqvpl__klnl += f"""  {zmjik__odqcr} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[olf__njln]})
"""
                hiehk__ilvcs[olf__njln] = zmjik__odqcr
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        hiehk__ilvcs = {olf__njln: 'values' for olf__njln in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        zmjik__odqcr = 'data{}'.format(i)
        eqvpl__klnl += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(zmjik__odqcr, i))
        data.append(zmjik__odqcr)
    uyahj__vah = ['out{}'.format(i) for i in range(len(df.columns))]
    jugit__dbw = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    rcss__dvv = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    cnwub__dkc = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, ytxdr__wgasu) in enumerate(zip(df.columns, data)):
        if cname in hiehk__ilvcs:
            horf__lsch = hiehk__ilvcs[cname]
            if nkyl__xivj:
                eqvpl__klnl += jugit__dbw.format(ytxdr__wgasu, horf__lsch,
                    uyahj__vah[i])
            else:
                eqvpl__klnl += rcss__dvv.format(ytxdr__wgasu, horf__lsch,
                    uyahj__vah[i])
        else:
            eqvpl__klnl += cnwub__dkc.format(uyahj__vah[i])
    return _gen_init_df(eqvpl__klnl, df.columns, ','.join(uyahj__vah))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    xka__jnytf = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(xka__jnytf))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    qzgi__xyddf = [olf__njln for olf__njln, lqd__ovr in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(lqd__ovr.dtype)]
    assert len(qzgi__xyddf) != 0
    zqju__blghn = ''
    if not any(lqd__ovr == types.float64 for lqd__ovr in df.data):
        zqju__blghn = '.astype(np.float64)'
    now__oiwrj = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[olf__njln], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[olf__njln]], IntegerArrayType) or
        df.data[df.column_index[olf__njln]] == boolean_array else '') for
        olf__njln in qzgi__xyddf)
    sglr__qxq = 'np.stack(({},), 1){}'.format(now__oiwrj, zqju__blghn)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(
        qzgi__xyddf)))
    index = f'{generate_col_to_index_func_text(qzgi__xyddf)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(sglr__qxq)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, qzgi__xyddf, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    mztud__ninf = dict(ddof=ddof)
    png__mzmj = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    llpys__fwuif = '1' if is_overload_none(min_periods) else 'min_periods'
    qzgi__xyddf = [olf__njln for olf__njln, lqd__ovr in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(lqd__ovr.dtype)]
    if len(qzgi__xyddf) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    zqju__blghn = ''
    if not any(lqd__ovr == types.float64 for lqd__ovr in df.data):
        zqju__blghn = '.astype(np.float64)'
    now__oiwrj = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[olf__njln], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[olf__njln]], IntegerArrayType) or
        df.data[df.column_index[olf__njln]] == boolean_array else '') for
        olf__njln in qzgi__xyddf)
    sglr__qxq = 'np.stack(({},), 1){}'.format(now__oiwrj, zqju__blghn)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(
        qzgi__xyddf)))
    index = f'pd.Index({qzgi__xyddf})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(sglr__qxq)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        llpys__fwuif)
    return _gen_init_df(header, qzgi__xyddf, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    mztud__ninf = dict(axis=axis, level=level, numeric_only=numeric_only)
    png__mzmj = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    eqvpl__klnl = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    eqvpl__klnl += '  data = np.array([{}])\n'.format(data_args)
    dzknw__livtg = (bodo.hiframes.dataframe_impl.
        generate_col_to_index_func_text(df.columns))
    eqvpl__klnl += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {dzknw__livtg})\n'
        )
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo, 'np': np}, php__dced)
    impl = php__dced['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    mztud__ninf = dict(axis=axis)
    png__mzmj = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    eqvpl__klnl = 'def impl(df, axis=0, dropna=True):\n'
    eqvpl__klnl += '  data = np.asarray(({},))\n'.format(data_args)
    dzknw__livtg = (bodo.hiframes.dataframe_impl.
        generate_col_to_index_func_text(df.columns))
    eqvpl__klnl += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {dzknw__livtg})\n'
        )
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo, 'np': np}, php__dced)
    impl = php__dced['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    mztud__ninf = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    png__mzmj = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    mztud__ninf = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    png__mzmj = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    mztud__ninf = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    png__mzmj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    mztud__ninf = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    png__mzmj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    mztud__ninf = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    png__mzmj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    mztud__ninf = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    png__mzmj = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    mztud__ninf = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    png__mzmj = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    mztud__ninf = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    png__mzmj = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    mztud__ninf = dict(numeric_only=numeric_only, interpolation=interpolation)
    png__mzmj = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    mztud__ninf = dict(axis=axis, skipna=skipna)
    png__mzmj = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for uuvhn__fxqfq in df.data:
        if not (bodo.utils.utils.is_np_array_typ(uuvhn__fxqfq) and (
            uuvhn__fxqfq.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(uuvhn__fxqfq.dtype, (types.Number, types.Boolean))) or
            isinstance(uuvhn__fxqfq, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or uuvhn__fxqfq in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {uuvhn__fxqfq} not supported.'
                )
        if isinstance(uuvhn__fxqfq, bodo.CategoricalArrayType
            ) and not uuvhn__fxqfq.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    mztud__ninf = dict(axis=axis, skipna=skipna)
    png__mzmj = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for uuvhn__fxqfq in df.data:
        if not (bodo.utils.utils.is_np_array_typ(uuvhn__fxqfq) and (
            uuvhn__fxqfq.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(uuvhn__fxqfq.dtype, (types.Number, types.Boolean))) or
            isinstance(uuvhn__fxqfq, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or uuvhn__fxqfq in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {uuvhn__fxqfq} not supported.'
                )
        if isinstance(uuvhn__fxqfq, bodo.CategoricalArrayType
            ) and not uuvhn__fxqfq.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmin(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmin', axis=axis)


@overload_method(DataFrameType, 'infer_objects', inline='always')
def overload_dataframe_infer_objects(df):
    check_runtime_cols_unsupported(df, 'DataFrame.infer_objects()')
    return lambda df: df.copy()


def _gen_reduce_impl(df, func_name, args=None, axis=None):
    args = '' if is_overload_none(args) else args
    if is_overload_none(axis):
        axis = 0
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
    else:
        raise_bodo_error(
            f'DataFrame.{func_name}: axis must be a constant Integer')
    assert axis in (0, 1), f'invalid axis argument for DataFrame.{func_name}'
    if func_name in ('idxmax', 'idxmin'):
        out_colnames = df.columns
    else:
        qzgi__xyddf = tuple(olf__njln for olf__njln, lqd__ovr in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (lqd__ovr.dtype))
        out_colnames = qzgi__xyddf
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            ecuc__rbqjx = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[olf__njln]].dtype) for olf__njln in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(ecuc__rbqjx, []))
    except NotImplementedError as oomy__ldue:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    ktxer__bwuw = ''
    if func_name in ('sum', 'prod'):
        ktxer__bwuw = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    eqvpl__klnl = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, ktxer__bwuw))
    if func_name == 'quantile':
        eqvpl__klnl = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        eqvpl__klnl = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        eqvpl__klnl += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        eqvpl__klnl += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        php__dced)
    impl = php__dced['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    mei__ivpc = ''
    if func_name in ('min', 'max'):
        mei__ivpc = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        mei__ivpc = ', dtype=np.float32'
    kbi__derxq = f'bodo.libs.array_ops.array_op_{func_name}'
    ktr__xoxp = ''
    if func_name in ['sum', 'prod']:
        ktr__xoxp = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        ktr__xoxp = 'index'
    elif func_name == 'quantile':
        ktr__xoxp = 'q'
    elif func_name in ['std', 'var']:
        ktr__xoxp = 'True, ddof'
    elif func_name == 'median':
        ktr__xoxp = 'True'
    data_args = ', '.join(
        f'{kbi__derxq}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[olf__njln]}), {ktr__xoxp})'
         for olf__njln in out_colnames)
    eqvpl__klnl = ''
    if func_name in ('idxmax', 'idxmin'):
        eqvpl__klnl += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        eqvpl__klnl += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        eqvpl__klnl += '  data = np.asarray(({},){})\n'.format(data_args,
            mei__ivpc)
    eqvpl__klnl += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return eqvpl__klnl


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    qzj__mugv = [df_type.column_index[olf__njln] for olf__njln in out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in qzj__mugv)
    jhzdk__rhf = '\n        '.join(f'row[{i}] = arr_{qzj__mugv[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    owl__tdcu = f'len(arr_{qzj__mugv[0]})'
    vor__dtwqm = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in vor__dtwqm:
        dbrhc__ccaug = vor__dtwqm[func_name]
        rgdc__oepnc = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        eqvpl__klnl = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {owl__tdcu}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{rgdc__oepnc})
    for i in numba.parfors.parfor.internal_prange(n):
        {jhzdk__rhf}
        A[i] = {dbrhc__ccaug}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return eqvpl__klnl
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    mztud__ninf = dict(fill_method=fill_method, limit=limit, freq=freq)
    png__mzmj = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.pct_change()')
    data_args = ', '.join(
        f'bodo.hiframes.rolling.pct_change(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = (
        "def impl(df, periods=1, fill_method='pad', limit=None, freq=None):\n")
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumprod', inline='always', no_unliteral=True)
def overload_dataframe_cumprod(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumprod()')
    mztud__ninf = dict(axis=axis, skipna=skipna)
    png__mzmj = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumprod()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    mztud__ninf = dict(skipna=skipna)
    png__mzmj = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumsum()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumsum()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


def _is_describe_type(data):
    return isinstance(data, IntegerArrayType) or isinstance(data, types.Array
        ) and isinstance(data.dtype, types.Number
        ) or data.dtype == bodo.datetime64ns


@overload_method(DataFrameType, 'describe', inline='always', no_unliteral=True)
def overload_dataframe_describe(df, percentiles=None, include=None, exclude
    =None, datetime_is_numeric=True):
    check_runtime_cols_unsupported(df, 'DataFrame.describe()')
    mztud__ninf = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    png__mzmj = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    qzgi__xyddf = [olf__njln for olf__njln, lqd__ovr in zip(df.columns, df.
        data) if _is_describe_type(lqd__ovr)]
    if len(qzgi__xyddf) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    cnt__bfh = sum(df.data[df.column_index[olf__njln]].dtype == bodo.
        datetime64ns for olf__njln in qzgi__xyddf)

    def _get_describe(col_ind):
        zgyuj__rbqu = df.data[col_ind].dtype == bodo.datetime64ns
        if cnt__bfh and cnt__bfh != len(qzgi__xyddf):
            if zgyuj__rbqu:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for olf__njln in qzgi__xyddf:
        col_ind = df.column_index[olf__njln]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[olf__njln]) for
        olf__njln in qzgi__xyddf)
    pdej__apgm = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if cnt__bfh == len(qzgi__xyddf):
        pdej__apgm = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif cnt__bfh:
        pdej__apgm = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({pdej__apgm})'
    return _gen_init_df(header, qzgi__xyddf, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    mztud__ninf = dict(axis=axis, convert=convert, is_copy=is_copy)
    png__mzmj = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[indices_t]'
        .format(i) for i in range(len(df.columns)))
    header = 'def impl(df, indices, axis=0, convert=None, is_copy=True):\n'
    header += (
        '  indices_t = bodo.utils.conversion.coerce_to_ndarray(indices)\n')
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[indices_t]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'shift', inline='always', no_unliteral=True)
def overload_dataframe_shift(df, periods=1, freq=None, axis=0, fill_value=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.shift()')
    mztud__ninf = dict(freq=freq, axis=axis, fill_value=fill_value)
    png__mzmj = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for dcwrk__hhr in df.data:
        if not is_supported_shift_array_type(dcwrk__hhr):
            raise BodoError(
                f'Dataframe.shift() column input type {dcwrk__hhr.dtype} not supported yet.'
                )
    if not is_overload_int(periods):
        raise BodoError(
            "DataFrame.shift(): 'periods' input must be an integer.")
    data_args = ', '.join(
        f'bodo.hiframes.rolling.shift(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = 'def impl(df, periods=1, freq=None, axis=0, fill_value=None):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'diff', inline='always', no_unliteral=True)
def overload_dataframe_diff(df, periods=1, axis=0):
    check_runtime_cols_unsupported(df, 'DataFrame.diff()')
    mztud__ninf = dict(axis=axis)
    png__mzmj = dict(axis=0)
    check_unsupported_args('DataFrame.diff', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for dcwrk__hhr in df.data:
        if not (isinstance(dcwrk__hhr, types.Array) and (isinstance(
            dcwrk__hhr.dtype, types.Number) or dcwrk__hhr.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {dcwrk__hhr.dtype} not supported.'
                )
    if not is_overload_int(periods):
        raise BodoError("DataFrame.diff(): 'periods' input must be an integer."
            )
    header = 'def impl(df, periods=1, axis= 0):\n'
    for i in range(len(df.columns)):
        header += (
            f'  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    data_args = ', '.join(
        f'bodo.hiframes.series_impl.dt64_arr_sub(data_{i}, bodo.hiframes.rolling.shift(data_{i}, periods, False))'
         if df.data[i] == types.Array(bodo.datetime64ns, 1, 'C') else
        f'data_{i} - bodo.hiframes.rolling.shift(data_{i}, periods, False)' for
        i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'explode', inline='always', no_unliteral=True)
def overload_dataframe_explode(df, column, ignore_index=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.explode()')
    hqh__jrui = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(hqh__jrui)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        fwfcg__sxzy = get_overload_const_list(column)
    else:
        fwfcg__sxzy = [get_literal_value(column)]
    peebi__poojn = [df.column_index[olf__njln] for olf__njln in fwfcg__sxzy]
    for i in peebi__poojn:
        if not isinstance(df.data[i], ArrayItemArrayType) and df.data[i
            ].dtype != string_array_split_view_type:
            raise BodoError(
                f'DataFrame.explode(): columns must have array-like entries')
    n = len(df.columns)
    header = 'def impl(df, column, ignore_index=False):\n'
    header += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    header += '  index_arr = bodo.utils.conversion.index_to_array(index)\n'
    for i in range(n):
        header += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    header += (
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{peebi__poojn[0]})\n'
        )
    for i in range(n):
        if i in peebi__poojn:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.explode_no_index(data{i}, counts)\n'
                )
        else:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.repeat_kernel(data{i}, counts)\n'
                )
    header += (
        '  new_index = bodo.libs.array_kernels.repeat_kernel(index_arr, counts)\n'
        )
    data_args = ', '.join(f'out_data{i}' for i in range(n))
    index = 'bodo.utils.conversion.convert_to_index(new_index)'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'set_index', inline='always', no_unliteral=True
    )
def overload_dataframe_set_index(df, keys, drop=True, append=False, inplace
    =False, verify_integrity=False):
    check_runtime_cols_unsupported(df, 'DataFrame.set_index()')
    yhgff__eagi = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    cep__fvt = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', yhgff__eagi, cep__fvt,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_str(keys):
        raise_bodo_error(
            "DataFrame.set_index(): 'keys' must be a constant string")
    col_name = get_overload_const_str(keys)
    col_ind = df.columns.index(col_name)
    header = """def impl(df, keys, drop=True, append=False, inplace=False, verify_integrity=False):
"""
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'.format(
        i) for i in range(len(df.columns)) if i != col_ind)
    columns = tuple(olf__njln for olf__njln in df.columns if olf__njln !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    yhgff__eagi = {'inplace': inplace}
    cep__fvt = {'inplace': False}
    check_unsupported_args('query', yhgff__eagi, cep__fvt, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        pxgl__rmnus = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[pxgl__rmnus]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    yhgff__eagi = {'subset': subset, 'keep': keep}
    cep__fvt = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', yhgff__eagi, cep__fvt,
        package_name='pandas', module_name='DataFrame')
    xka__jnytf = len(df.columns)
    eqvpl__klnl = "def impl(df, subset=None, keep='first'):\n"
    for i in range(xka__jnytf):
        eqvpl__klnl += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    yqwao__dpyk = ', '.join(f'data_{i}' for i in range(xka__jnytf))
    yqwao__dpyk += ',' if xka__jnytf == 1 else ''
    eqvpl__klnl += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({yqwao__dpyk}))\n'
        )
    eqvpl__klnl += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    eqvpl__klnl += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo}, php__dced)
    impl = php__dced['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    yhgff__eagi = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    cep__fvt = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    oqa__pfbv = []
    if is_overload_constant_list(subset):
        oqa__pfbv = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        oqa__pfbv = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        oqa__pfbv = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    hnmm__nbv = []
    for col_name in oqa__pfbv:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        hnmm__nbv.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', yhgff__eagi,
        cep__fvt, package_name='pandas', module_name='DataFrame')
    ffbg__nyil = []
    if hnmm__nbv:
        for gwhy__znxl in hnmm__nbv:
            if isinstance(df.data[gwhy__znxl], bodo.MapArrayType):
                ffbg__nyil.append(df.columns[gwhy__znxl])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                ffbg__nyil.append(col_name)
    if ffbg__nyil:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {ffbg__nyil} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    xka__jnytf = len(df.columns)
    yyh__rher = ['data_{}'.format(i) for i in hnmm__nbv]
    ltwt__eydg = ['data_{}'.format(i) for i in range(xka__jnytf) if i not in
        hnmm__nbv]
    if yyh__rher:
        zlkx__wwi = len(yyh__rher)
    else:
        zlkx__wwi = xka__jnytf
    ymp__htc = ', '.join(yyh__rher + ltwt__eydg)
    data_args = ', '.join('data_{}'.format(i) for i in range(xka__jnytf))
    eqvpl__klnl = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(xka__jnytf):
        eqvpl__klnl += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    eqvpl__klnl += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(ymp__htc, index, zlkx__wwi))
    eqvpl__klnl += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(eqvpl__klnl, df.columns, data_args, 'index')


def create_dataframe_mask_where_overload(func_name):

    def overload_dataframe_mask_where(df, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
            f'DataFrame.{func_name}()')
        _validate_arguments_mask_where(f'DataFrame.{func_name}', df, cond,
            other, inplace, axis, level, errors, try_cast)
        header = """def impl(df, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise', try_cast=False):
"""
        if func_name == 'mask':
            header += '  cond = ~cond\n'
        gen_all_false = [False]
        if cond.ndim == 1:
            cond_str = lambda i, _: 'cond'
        elif cond.ndim == 2:
            if isinstance(cond, DataFrameType):

                def cond_str(i, gen_all_false):
                    if df.columns[i] in cond.column_index:
                        return (
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(cond, {cond.column_index[df.columns[i]]})'
                            )
                    else:
                        gen_all_false[0] = True
                        return 'all_false'
            elif isinstance(cond, types.Array):
                cond_str = lambda i, _: f'cond[:,{i}]'
        if not hasattr(other, 'ndim') or other.ndim == 1:
            cssjh__fhfe = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                cssjh__fhfe = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                cssjh__fhfe = lambda i: f'other[:,{i}]'
        xka__jnytf = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {cssjh__fhfe(i)})'
             for i in range(xka__jnytf))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        syhlc__sro = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(syhlc__sro
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    mztud__ninf = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    png__mzmj = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        (cond.ndim == 1 or cond.ndim == 2) and cond.dtype == types.bool_
        ) and not (isinstance(cond, DataFrameType) and cond.ndim == 2 and
        all(cond.data[i].dtype == types.bool_ for i in range(len(df.columns)))
        ):
        raise BodoError(
            f"{func_name}(): 'cond' argument must be a DataFrame, Series, 1- or 2-dimensional array of booleans"
            )
    xka__jnytf = len(df.columns)
    if hasattr(other, 'ndim') and (other.ndim != 1 or other.ndim != 2):
        if other.ndim == 2:
            if not isinstance(other, (DataFrameType, types.Array)):
                raise BodoError(
                    f"{func_name}(): 'other', if 2-dimensional, must be a DataFrame or array."
                    )
        elif other.ndim != 1:
            raise BodoError(
                f"{func_name}(): 'other' must be either 1 or 2-dimensional")
    if isinstance(other, DataFrameType):
        for i in range(xka__jnytf):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(xka__jnytf):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(xka__jnytf):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    bcs__weytp = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    eqvpl__klnl = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    php__dced = {}
    hynuq__aain = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': bcs__weytp}
    hynuq__aain.update(extra_globals)
    exec(eqvpl__klnl, hynuq__aain, php__dced)
    impl = php__dced['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        yxi__xna = pd.Index(lhs.columns)
        qvmcs__egeu = pd.Index(rhs.columns)
        lzmdc__alf, omhp__hja, wlur__lqm = yxi__xna.join(qvmcs__egeu, how=
            'left' if is_inplace else 'outer', level=None, return_indexers=True
            )
        return tuple(lzmdc__alf), omhp__hja, wlur__lqm
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        nkc__pfpai = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        cjq__yjhzt = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, nkc__pfpai)
        check_runtime_cols_unsupported(rhs, nkc__pfpai)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                lzmdc__alf, omhp__hja, wlur__lqm = _get_binop_columns(lhs, rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {otv__ctu}) {nkc__pfpai}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {hplzv__mtsj})'
                     if otv__ctu != -1 and hplzv__mtsj != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for otv__ctu, hplzv__mtsj in zip(omhp__hja, wlur__lqm))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, lzmdc__alf, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            pdgyp__vnm = []
            acvwp__dbqh = []
            if op in cjq__yjhzt:
                for i, wnnmn__cgg in enumerate(lhs.data):
                    if is_common_scalar_dtype([wnnmn__cgg.dtype, rhs]):
                        pdgyp__vnm.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {nkc__pfpai} rhs'
                            )
                    else:
                        wftfj__ooq = f'arr{i}'
                        acvwp__dbqh.append(wftfj__ooq)
                        pdgyp__vnm.append(wftfj__ooq)
                data_args = ', '.join(pdgyp__vnm)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {nkc__pfpai} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(acvwp__dbqh) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {wftfj__ooq} = np.empty(n, dtype=np.bool_)\n' for
                    wftfj__ooq in acvwp__dbqh)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(wftfj__ooq, 
                    op == operator.ne) for wftfj__ooq in acvwp__dbqh)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            pdgyp__vnm = []
            acvwp__dbqh = []
            if op in cjq__yjhzt:
                for i, wnnmn__cgg in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, wnnmn__cgg.dtype]):
                        pdgyp__vnm.append(
                            f'lhs {nkc__pfpai} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        wftfj__ooq = f'arr{i}'
                        acvwp__dbqh.append(wftfj__ooq)
                        pdgyp__vnm.append(wftfj__ooq)
                data_args = ', '.join(pdgyp__vnm)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, nkc__pfpai) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(acvwp__dbqh) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(wftfj__ooq) for wftfj__ooq in acvwp__dbqh)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(wftfj__ooq, 
                    op == operator.ne) for wftfj__ooq in acvwp__dbqh)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(rhs)'
            return _gen_init_df(header, rhs.columns, data_args, index)
    return overload_dataframe_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        syhlc__sro = create_binary_op_overload(op)
        overload(op)(syhlc__sro)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        nkc__pfpai = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, nkc__pfpai)
        check_runtime_cols_unsupported(right, nkc__pfpai)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                lzmdc__alf, _, wlur__lqm = _get_binop_columns(left, right, True
                    )
                eqvpl__klnl = 'def impl(left, right):\n'
                for i, hplzv__mtsj in enumerate(wlur__lqm):
                    if hplzv__mtsj == -1:
                        eqvpl__klnl += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    eqvpl__klnl += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    eqvpl__klnl += f"""  df_arr{i} {nkc__pfpai} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {hplzv__mtsj})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    lzmdc__alf)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(eqvpl__klnl, lzmdc__alf, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            eqvpl__klnl = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                eqvpl__klnl += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                eqvpl__klnl += '  df_arr{0} {1} right\n'.format(i, nkc__pfpai)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(eqvpl__klnl, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        syhlc__sro = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(syhlc__sro)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            nkc__pfpai = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, nkc__pfpai)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, nkc__pfpai) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        syhlc__sro = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(syhlc__sro)


_install_unary_ops()


def overload_isna(obj):
    check_runtime_cols_unsupported(obj, 'pd.isna()')
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj):
        return lambda obj: obj.isna()
    if is_array_typ(obj):

        def impl(obj):
            numba.parfors.parfor.init_prange()
            n = len(obj)
            jrjp__gufwd = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                jrjp__gufwd[i] = bodo.libs.array_kernels.isna(obj, i)
            return jrjp__gufwd
        return impl


overload(pd.isna, inline='always')(overload_isna)
overload(pd.isnull, inline='always')(overload_isna)


@overload(pd.isna)
@overload(pd.isnull)
def overload_isna_scalar(obj):
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj) or is_array_typ(
        obj):
        return
    if isinstance(obj, (types.List, types.UniTuple)):

        def impl(obj):
            n = len(obj)
            jrjp__gufwd = np.empty(n, np.bool_)
            for i in range(n):
                jrjp__gufwd[i] = pd.isna(obj[i])
            return jrjp__gufwd
        return impl
    obj = types.unliteral(obj)
    if obj == bodo.string_type:
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Integer):
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Float):
        return lambda obj: np.isnan(obj)
    if isinstance(obj, (types.NPDatetime, types.NPTimedelta)):
        return lambda obj: np.isnat(obj)
    if obj == types.none:
        return lambda obj: unliteral_val(True)
    if isinstance(obj, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_dt64(obj.value))
    if obj == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(obj.value))
    if isinstance(obj, types.Optional):
        return lambda obj: obj is None
    return lambda obj: unliteral_val(False)


@overload(operator.setitem, no_unliteral=True)
def overload_setitem_arr_none(A, idx, val):
    if is_array_typ(A, False) and isinstance(idx, types.Integer
        ) and val == types.none:
        return lambda A, idx, val: bodo.libs.array_kernels.setna(A, idx)


def overload_notna(obj):
    check_runtime_cols_unsupported(obj, 'pd.notna()')
    if isinstance(obj, (DataFrameType, SeriesType)):
        return lambda obj: obj.notna()
    if isinstance(obj, (types.List, types.UniTuple)) or is_array_typ(obj,
        include_index_series=True):
        return lambda obj: ~pd.isna(obj)
    return lambda obj: not pd.isna(obj)


overload(pd.notna, inline='always', no_unliteral=True)(overload_notna)
overload(pd.notnull, inline='always', no_unliteral=True)(overload_notna)


def _get_pd_dtype_str(t):
    if t.dtype == types.NPDatetime('ns'):
        return "'datetime64[ns]'"
    return bodo.ir.csv_ext._get_pd_dtype_str(t)


@overload_method(DataFrameType, 'replace', inline='always', no_unliteral=True)
def overload_dataframe_replace(df, to_replace=None, value=None, inplace=
    False, limit=None, regex=False, method='pad'):
    check_runtime_cols_unsupported(df, 'DataFrame.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.replace()')
    if is_overload_none(to_replace):
        raise BodoError('replace(): to_replace value of None is not supported')
    yhgff__eagi = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    cep__fvt = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', yhgff__eagi, cep__fvt, package_name=
        'pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    pdyrs__zyv = str(expr_node)
    return pdyrs__zyv.startswith('left.') or pdyrs__zyv.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    yyrfi__hah = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (yyrfi__hah,))
    mxz__nzkhy = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        qaz__qdfh = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        umuk__fwvxi = {('NOT_NA', mxz__nzkhy(wnnmn__cgg)): wnnmn__cgg for
            wnnmn__cgg in null_set}
        mkgnz__gmr, _, _ = _parse_query_expr(qaz__qdfh, env, [], [], None,
            join_cleaned_cols=umuk__fwvxi)
        nlrs__ongan = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            icfs__eko = pd.core.computation.ops.BinOp('&', mkgnz__gmr,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = nlrs__ongan
        return icfs__eko

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                kqmak__esbo = set()
                ujv__hyfdm = set()
                fud__axdwv = _insert_NA_cond_body(expr_node.lhs, kqmak__esbo)
                uwnkl__hwoy = _insert_NA_cond_body(expr_node.rhs, ujv__hyfdm)
                rrvz__oof = kqmak__esbo.intersection(ujv__hyfdm)
                kqmak__esbo.difference_update(rrvz__oof)
                ujv__hyfdm.difference_update(rrvz__oof)
                null_set.update(rrvz__oof)
                expr_node.lhs = append_null_checks(fud__axdwv, kqmak__esbo)
                expr_node.rhs = append_null_checks(uwnkl__hwoy, ujv__hyfdm)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            wkqw__bjy = expr_node.name
            ogr__tlzqs, col_name = wkqw__bjy.split('.')
            if ogr__tlzqs == 'left':
                jnn__irii = left_columns
                data = left_data
            else:
                jnn__irii = right_columns
                data = right_data
            ytaj__ohino = data[jnn__irii.index(col_name)]
            if bodo.utils.typing.is_nullable(ytaj__ohino):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    skq__mhx = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        zaebl__fhlt = str(expr_node.lhs)
        yhdlp__wxmj = str(expr_node.rhs)
        if zaebl__fhlt.startswith('left.') and yhdlp__wxmj.startswith('left.'
            ) or zaebl__fhlt.startswith('right.') and yhdlp__wxmj.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [zaebl__fhlt.split('.')[1]]
        right_on = [yhdlp__wxmj.split('.')[1]]
        if zaebl__fhlt.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        nzmph__hpqsw, kxdmy__gvh, vrk__yzex = _extract_equal_conds(expr_node
            .lhs)
        kow__uzag, psqh__qsvs, dzsnv__owjm = _extract_equal_conds(expr_node.rhs
            )
        left_on = nzmph__hpqsw + kow__uzag
        right_on = kxdmy__gvh + psqh__qsvs
        if vrk__yzex is None:
            return left_on, right_on, dzsnv__owjm
        if dzsnv__owjm is None:
            return left_on, right_on, vrk__yzex
        expr_node.lhs = vrk__yzex
        expr_node.rhs = dzsnv__owjm
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    yyrfi__hah = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (yyrfi__hah,))
    ocu__awnb = dict()
    mxz__nzkhy = pd.core.computation.parsing.clean_column_name
    for name, gvgqc__iohtl in (('left', left_columns), ('right', right_columns)
        ):
        for wnnmn__cgg in gvgqc__iohtl:
            jghb__jhe = mxz__nzkhy(wnnmn__cgg)
            pej__uhk = name, jghb__jhe
            if pej__uhk in ocu__awnb:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{wnnmn__cgg}' and '{ocu__awnb[jghb__jhe]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            ocu__awnb[pej__uhk] = wnnmn__cgg
    tdrll__hknx, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=ocu__awnb)
    left_on, right_on, pef__vmdc = _extract_equal_conds(tdrll__hknx.terms)
    return left_on, right_on, _insert_NA_cond(pef__vmdc, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    mztud__ninf = dict(sort=sort, copy=copy, validate=validate)
    png__mzmj = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    yij__labq = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    qax__tngxb = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in yij__labq and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, hbw__ndv = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if hbw__ndv is None:
                    qax__tngxb = ''
                else:
                    qax__tngxb = str(hbw__ndv)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = yij__labq
        right_keys = yij__labq
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    if (not left_on or not right_on) and not is_overload_none(on):
        raise BodoError(
            f"DataFrame.merge(): Merge condition '{get_overload_const_str(on)}' requires a cross join to implement, but cross join is not supported."
            )
    if not is_overload_bool(indicator):
        raise_bodo_error(
            'DataFrame.merge(): indicator must be a constant boolean')
    indicator_val = get_overload_const_bool(indicator)
    if not is_overload_bool(_bodo_na_equal):
        raise_bodo_error(
            'DataFrame.merge(): bodo extension _bodo_na_equal must be a constant boolean'
            )
    kgubp__ghfcc = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        mda__uhpbz = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        mda__uhpbz = list(get_overload_const_list(suffixes))
    suffix_x = mda__uhpbz[0]
    suffix_y = mda__uhpbz[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    eqvpl__klnl = (
        "def _impl(left, right, how='inner', on=None, left_on=None,\n")
    eqvpl__klnl += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    eqvpl__klnl += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    eqvpl__klnl += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, kgubp__ghfcc, qax__tngxb))
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo}, php__dced)
    _impl = php__dced['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType, bodo.
        DatetimeArrayType)
    rkqc__chts = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    bjwzn__abz = {get_overload_const_str(wyoa__wqxe) for wyoa__wqxe in (
        left_on, right_on, on) if is_overload_constant_str(wyoa__wqxe)}
    for df in (left, right):
        for i, wnnmn__cgg in enumerate(df.data):
            if not isinstance(wnnmn__cgg, valid_dataframe_column_types
                ) and wnnmn__cgg not in rkqc__chts:
                raise BodoError(
                    f'{name_func}(): use of column with {type(wnnmn__cgg)} in merge unsupported'
                    )
            if df.columns[i] in bjwzn__abz and isinstance(wnnmn__cgg,
                MapArrayType):
                raise BodoError(
                    f'{name_func}(): merge on MapArrayType unsupported')
    ensure_constant_arg(name_func, 'left_index', left_index, bool)
    ensure_constant_arg(name_func, 'right_index', right_index, bool)
    if not is_overload_constant_tuple(suffixes
        ) and not is_overload_constant_list(suffixes):
        raise_bodo_error(name_func +
            "(): suffixes parameters should be ['_left', '_right']")
    if is_overload_constant_tuple(suffixes):
        mda__uhpbz = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        mda__uhpbz = list(get_overload_const_list(suffixes))
    if len(mda__uhpbz) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    yij__labq = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        sqtw__nbu = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            sqtw__nbu = on_str not in yij__labq and ('left.' in on_str or 
                'right.' in on_str)
        if len(yij__labq) == 0 and not sqtw__nbu:
            raise_bodo_error(name_func +
                '(): No common columns to perform merge on. Merge options: left_on={lon}, right_on={ron}, left_index={lidx}, right_index={ridx}'
                .format(lon=is_overload_true(left_on), ron=is_overload_true
                (right_on), lidx=is_overload_true(left_index), ridx=
                is_overload_true(right_index)))
        if not is_overload_none(left_on) or not is_overload_none(right_on):
            raise BodoError(name_func +
                '(): Can only pass argument "on" OR "left_on" and "right_on", not a combination of both.'
                )
    if (is_overload_true(left_index) or not is_overload_none(left_on)
        ) and is_overload_none(right_on) and not is_overload_true(right_index):
        raise BodoError(name_func +
            '(): Must pass right_on or right_index=True')
    if (is_overload_true(right_index) or not is_overload_none(right_on)
        ) and is_overload_none(left_on) and not is_overload_true(left_index):
        raise BodoError(name_func + '(): Must pass left_on or left_index=True')


def validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
    right_index, sort, suffixes, copy, indicator, validate):
    common_validate_merge_merge_asof_spec('merge', left, right, on, left_on,
        right_on, left_index, right_index, suffixes)
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))


def validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
    right_index, by, left_by, right_by, suffixes, tolerance,
    allow_exact_matches, direction):
    common_validate_merge_merge_asof_spec('merge_asof', left, right, on,
        left_on, right_on, left_index, right_index, suffixes)
    if not is_overload_true(allow_exact_matches):
        raise BodoError(
            'merge_asof(): allow_exact_matches parameter only supports default value True'
            )
    if not is_overload_none(tolerance):
        raise BodoError(
            'merge_asof(): tolerance parameter only supports default value None'
            )
    if not is_overload_none(by):
        raise BodoError(
            'merge_asof(): by parameter only supports default value None')
    if not is_overload_none(left_by):
        raise BodoError(
            'merge_asof(): left_by parameter only supports default value None')
    if not is_overload_none(right_by):
        raise BodoError(
            'merge_asof(): right_by parameter only supports default value None'
            )
    if not is_overload_constant_str(direction):
        raise BodoError(
            'merge_asof(): direction parameter should be of type str')
    else:
        direction = get_overload_const_str(direction)
        if direction != 'backward':
            raise BodoError(
                "merge_asof(): direction parameter only supports default value 'backward'"
                )


def validate_merge_asof_keys_length(left_on, right_on, left_index,
    right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if not is_overload_none(left_on) and is_overload_true(right_index):
        raise BodoError(
            'merge(): right_index = True and specifying left_on is not suppported yet.'
            )
    if not is_overload_none(right_on) and is_overload_true(left_index):
        raise BodoError(
            'merge(): left_index = True and specifying right_on is not suppported yet.'
            )


def validate_keys_length(left_index, right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if is_overload_true(right_index):
        if len(left_keys) != 1:
            raise BodoError(
                'merge(): len(left_on) must equal the number of levels in the index of "right", which is 1'
                )
    if is_overload_true(left_index):
        if len(right_keys) != 1:
            raise BodoError(
                'merge(): len(right_on) must equal the number of levels in the index of "left", which is 1'
                )


def validate_keys_dtypes(left, right, left_index, right_index, left_keys,
    right_keys):
    exs__izzvk = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            iod__gnjd = left.index
            nbk__rcls = isinstance(iod__gnjd, StringIndexType)
            mzqxw__lhouq = right.index
            ttk__ancxr = isinstance(mzqxw__lhouq, StringIndexType)
        elif is_overload_true(left_index):
            iod__gnjd = left.index
            nbk__rcls = isinstance(iod__gnjd, StringIndexType)
            mzqxw__lhouq = right.data[right.columns.index(right_keys[0])]
            ttk__ancxr = mzqxw__lhouq.dtype == string_type
        elif is_overload_true(right_index):
            iod__gnjd = left.data[left.columns.index(left_keys[0])]
            nbk__rcls = iod__gnjd.dtype == string_type
            mzqxw__lhouq = right.index
            ttk__ancxr = isinstance(mzqxw__lhouq, StringIndexType)
        if nbk__rcls and ttk__ancxr:
            return
        iod__gnjd = iod__gnjd.dtype
        mzqxw__lhouq = mzqxw__lhouq.dtype
        try:
            wnen__oafpq = exs__izzvk.resolve_function_type(operator.eq, (
                iod__gnjd, mzqxw__lhouq), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=iod__gnjd, rk_dtype=mzqxw__lhouq))
    else:
        for zct__ccjhv, dqy__gsyj in zip(left_keys, right_keys):
            iod__gnjd = left.data[left.columns.index(zct__ccjhv)].dtype
            yfptp__ueasl = left.data[left.columns.index(zct__ccjhv)]
            mzqxw__lhouq = right.data[right.columns.index(dqy__gsyj)].dtype
            pjr__scnvy = right.data[right.columns.index(dqy__gsyj)]
            if yfptp__ueasl == pjr__scnvy:
                continue
            hufed__uhy = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=zct__ccjhv, lk_dtype=iod__gnjd, rk=dqy__gsyj,
                rk_dtype=mzqxw__lhouq))
            onq__nmbti = iod__gnjd == string_type
            tphb__xim = mzqxw__lhouq == string_type
            if onq__nmbti ^ tphb__xim:
                raise_bodo_error(hufed__uhy)
            try:
                wnen__oafpq = exs__izzvk.resolve_function_type(operator.eq,
                    (iod__gnjd, mzqxw__lhouq), {})
            except:
                raise_bodo_error(hufed__uhy)


def validate_keys(keys, df):
    esugy__tgrz = set(keys).difference(set(df.columns))
    if len(esugy__tgrz) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in esugy__tgrz:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {esugy__tgrz} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    mztud__ninf = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    png__mzmj = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort)
    how = get_overload_const_str(how)
    if not is_overload_none(on):
        left_keys = get_overload_const_list(on)
    else:
        left_keys = ['$_bodo_index_']
    right_keys = ['$_bodo_index_']
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    eqvpl__klnl = "def _impl(left, other, on=None, how='left',\n"
    eqvpl__klnl += "    lsuffix='', rsuffix='', sort=False):\n"
    eqvpl__klnl += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo}, php__dced)
    _impl = php__dced['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        whp__abxju = get_overload_const_list(on)
        validate_keys(whp__abxju, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    yij__labq = tuple(set(left.columns) & set(other.columns))
    if len(yij__labq) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=yij__labq))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    dszci__rbqs = set(left_keys) & set(right_keys)
    tzv__kwanq = set(left_columns) & set(right_columns)
    ptngm__iqg = tzv__kwanq - dszci__rbqs
    ikvv__cpd = set(left_columns) - tzv__kwanq
    jfi__vuy = set(right_columns) - tzv__kwanq
    pyf__epu = {}

    def insertOutColumn(col_name):
        if col_name in pyf__epu:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        pyf__epu[col_name] = 0
    for zurxu__xovos in dszci__rbqs:
        insertOutColumn(zurxu__xovos)
    for zurxu__xovos in ptngm__iqg:
        rvat__trja = str(zurxu__xovos) + suffix_x
        dklj__mha = str(zurxu__xovos) + suffix_y
        insertOutColumn(rvat__trja)
        insertOutColumn(dklj__mha)
    for zurxu__xovos in ikvv__cpd:
        insertOutColumn(zurxu__xovos)
    for zurxu__xovos in jfi__vuy:
        insertOutColumn(zurxu__xovos)
    if indicator_val:
        insertOutColumn('_merge')


@overload(pd.merge_asof, inline='always', no_unliteral=True)
def overload_dataframe_merge_asof(left, right, on=None, left_on=None,
    right_on=None, left_index=False, right_index=False, by=None, left_by=
    None, right_by=None, suffixes=('_x', '_y'), tolerance=None,
    allow_exact_matches=True, direction='backward'):
    raise BodoError('pandas.merge_asof() not support yet')
    validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
        right_index, by, left_by, right_by, suffixes, tolerance,
        allow_exact_matches, direction)
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError('merge_asof() requires dataframe inputs')
    yij__labq = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = yij__labq
        right_keys = yij__labq
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    validate_merge_asof_keys_length(left_on, right_on, left_index,
        right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    if isinstance(suffixes, tuple):
        mda__uhpbz = suffixes
    if is_overload_constant_list(suffixes):
        mda__uhpbz = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        mda__uhpbz = suffixes.value
    suffix_x = mda__uhpbz[0]
    suffix_y = mda__uhpbz[1]
    eqvpl__klnl = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    eqvpl__klnl += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    eqvpl__klnl += (
        "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n")
    eqvpl__klnl += "    allow_exact_matches=True, direction='backward'):\n"
    eqvpl__klnl += '  suffix_x = suffixes[0]\n'
    eqvpl__klnl += '  suffix_y = suffixes[1]\n'
    eqvpl__klnl += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo}, php__dced)
    _impl = php__dced['_impl']
    return _impl


@overload_method(DataFrameType, 'groupby', inline='always', no_unliteral=True)
def overload_dataframe_groupby(df, by=None, axis=0, level=None, as_index=
    True, sort=False, group_keys=True, squeeze=False, observed=True, dropna
    =True, _bodo_num_shuffle_keys=-1):
    check_runtime_cols_unsupported(df, 'DataFrame.groupby()')
    validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
        squeeze, observed, dropna, _bodo_num_shuffle_keys)

    def _impl(df, by=None, axis=0, level=None, as_index=True, sort=False,
        group_keys=True, squeeze=False, observed=True, dropna=True,
        _bodo_num_shuffle_keys=-1):
        return bodo.hiframes.pd_groupby_ext.init_groupby(df, by, as_index,
            dropna, _bodo_num_shuffle_keys)
    return _impl


def validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
    squeeze, observed, dropna, _num_shuffle_keys):
    if is_overload_none(by):
        raise BodoError("groupby(): 'by' must be supplied.")
    if not is_overload_zero(axis):
        raise BodoError(
            "groupby(): 'axis' parameter only supports integer value 0.")
    if not is_overload_none(level):
        raise BodoError(
            "groupby(): 'level' is not supported since MultiIndex is not supported."
            )
    if not is_literal_type(by) and not is_overload_constant_list(by):
        raise_bodo_error(
            f"groupby(): 'by' parameter only supports a constant column label or column labels, not {by}."
            )
    if len(set(get_overload_const_list(by)).difference(set(df.columns))) > 0:
        raise_bodo_error(
            "groupby(): invalid key {} for 'by' (not available in columns {})."
            .format(get_overload_const_list(by), df.columns))
    if not is_overload_constant_bool(as_index):
        raise_bodo_error(
            "groupby(): 'as_index' parameter must be a constant bool, not {}."
            .format(as_index))
    if not is_overload_constant_bool(dropna):
        raise_bodo_error(
            "groupby(): 'dropna' parameter must be a constant bool, not {}."
            .format(dropna))
    if not is_overload_constant_int(_num_shuffle_keys):
        raise_bodo_error(
            f"groupby(): '_num_shuffle_keys' parameter must be a constant integer, not {_num_shuffle_keys}."
            )
    mztud__ninf = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    cvrlb__mrz = dict(sort=False, group_keys=True, squeeze=False, observed=True
        )
    check_unsupported_args('Dataframe.groupby', mztud__ninf, cvrlb__mrz,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    ptch__ljhf = func_name == 'DataFrame.pivot_table'
    if ptch__ljhf:
        if is_overload_none(index) or not is_literal_type(index):
            raise_bodo_error(
                f"DataFrame.pivot_table(): 'index' argument is required and must be constant column labels"
                )
    elif not is_overload_none(index) and not is_literal_type(index):
        raise_bodo_error(
            f"{func_name}(): if 'index' argument is provided it must be constant column labels"
            )
    if is_overload_none(columns) or not is_literal_type(columns):
        raise_bodo_error(
            f"{func_name}(): 'columns' argument is required and must be a constant column label"
            )
    if not is_overload_none(values) and not is_literal_type(values):
        raise_bodo_error(
            f"{func_name}(): if 'values' argument is provided it must be constant column labels"
            )
    pfzo__add = get_literal_value(columns)
    if isinstance(pfzo__add, (list, tuple)):
        if len(pfzo__add) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {pfzo__add}"
                )
        pfzo__add = pfzo__add[0]
    if pfzo__add not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {pfzo__add} not found in DataFrame {df}."
            )
    svpcz__mfi = df.column_index[pfzo__add]
    if is_overload_none(index):
        oyas__bux = []
        wnisk__iwzy = []
    else:
        wnisk__iwzy = get_literal_value(index)
        if not isinstance(wnisk__iwzy, (list, tuple)):
            wnisk__iwzy = [wnisk__iwzy]
        oyas__bux = []
        for index in wnisk__iwzy:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            oyas__bux.append(df.column_index[index])
    if not (all(isinstance(olf__njln, int) for olf__njln in wnisk__iwzy) or
        all(isinstance(olf__njln, str) for olf__njln in wnisk__iwzy)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        xhbwy__gng = []
        isd__nnyyd = []
        qec__gknmj = oyas__bux + [svpcz__mfi]
        for i, olf__njln in enumerate(df.columns):
            if i not in qec__gknmj:
                xhbwy__gng.append(i)
                isd__nnyyd.append(olf__njln)
    else:
        isd__nnyyd = get_literal_value(values)
        if not isinstance(isd__nnyyd, (list, tuple)):
            isd__nnyyd = [isd__nnyyd]
        xhbwy__gng = []
        for val in isd__nnyyd:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            xhbwy__gng.append(df.column_index[val])
    gmkcc__dfo = set(xhbwy__gng) | set(oyas__bux) | {svpcz__mfi}
    if len(gmkcc__dfo) != len(xhbwy__gng) + len(oyas__bux) + 1:
        raise BodoError(
            f"{func_name}(): 'index', 'columns', and 'values' must all refer to different columns"
            )

    def check_valid_index_typ(index_column):
        if isinstance(index_column, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType, bodo.
            IntervalArrayType)):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column must have scalar rows"
                )
        if isinstance(index_column, bodo.CategoricalArrayType):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column does not support categorical data"
                )
    if len(oyas__bux) == 0:
        index = df.index
        if isinstance(index, MultiIndexType):
            raise BodoError(
                f"{func_name}(): 'index' cannot be None with a DataFrame with a multi-index"
                )
        if not isinstance(index, RangeIndexType):
            check_valid_index_typ(index.data)
        if not is_literal_type(df.index.name_typ):
            raise BodoError(
                f"{func_name}(): If 'index' is None, the name of the DataFrame's Index must be constant at compile-time"
                )
    else:
        for yhmk__jwjt in oyas__bux:
            index_column = df.data[yhmk__jwjt]
            check_valid_index_typ(index_column)
    ydtd__nwggb = df.data[svpcz__mfi]
    if isinstance(ydtd__nwggb, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(ydtd__nwggb, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for isxig__wtwtl in xhbwy__gng:
        pra__zpx = df.data[isxig__wtwtl]
        if isinstance(pra__zpx, (bodo.ArrayItemArrayType, bodo.MapArrayType,
            bodo.StructArrayType, bodo.TupleArrayType)
            ) or pra__zpx == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (wnisk__iwzy, pfzo__add, isd__nnyyd, oyas__bux, svpcz__mfi,
        xhbwy__gng)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (wnisk__iwzy, pfzo__add, isd__nnyyd, yhmk__jwjt, svpcz__mfi, sso__rlsj) = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(wnisk__iwzy) == 0:
        if is_overload_none(data.index.name_typ):
            zgk__vuqva = None,
        else:
            zgk__vuqva = get_literal_value(data.index.name_typ),
    else:
        zgk__vuqva = tuple(wnisk__iwzy)
    wnisk__iwzy = ColNamesMetaType(zgk__vuqva)
    isd__nnyyd = ColNamesMetaType(tuple(isd__nnyyd))
    pfzo__add = ColNamesMetaType((pfzo__add,))
    eqvpl__klnl = 'def impl(data, index=None, columns=None, values=None):\n'
    eqvpl__klnl += "    ev = tracing.Event('df.pivot')\n"
    eqvpl__klnl += f'    pivot_values = data.iloc[:, {svpcz__mfi}].unique()\n'
    eqvpl__klnl += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(yhmk__jwjt) == 0:
        eqvpl__klnl += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        eqvpl__klnl += '        (\n'
        for zro__ybkdo in yhmk__jwjt:
            eqvpl__klnl += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {zro__ybkdo}),
"""
        eqvpl__klnl += '        ),\n'
    eqvpl__klnl += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {svpcz__mfi}),),
"""
    eqvpl__klnl += '        (\n'
    for isxig__wtwtl in sso__rlsj:
        eqvpl__klnl += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {isxig__wtwtl}),
"""
    eqvpl__klnl += '        ),\n'
    eqvpl__klnl += '        pivot_values,\n'
    eqvpl__klnl += '        index_lit,\n'
    eqvpl__klnl += '        columns_lit,\n'
    eqvpl__klnl += '        values_lit,\n'
    eqvpl__klnl += '    )\n'
    eqvpl__klnl += '    ev.finalize()\n'
    eqvpl__klnl += '    return result\n'
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo, 'index_lit': wnisk__iwzy,
        'columns_lit': pfzo__add, 'values_lit': isd__nnyyd, 'tracing':
        tracing}, php__dced)
    impl = php__dced['impl']
    return impl


@overload(pd.pivot_table, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(data, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot_table()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot_table()')
    mztud__ninf = dict(fill_value=fill_value, margins=margins, dropna=
        dropna, margins_name=margins_name, observed=observed, sort=sort)
    png__mzmj = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (wnisk__iwzy, pfzo__add, isd__nnyyd, yhmk__jwjt, svpcz__mfi, sso__rlsj) = (
        pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    rbzwd__rlib = wnisk__iwzy
    wnisk__iwzy = ColNamesMetaType(tuple(wnisk__iwzy))
    isd__nnyyd = ColNamesMetaType(tuple(isd__nnyyd))
    vpx__qwq = pfzo__add
    pfzo__add = ColNamesMetaType((pfzo__add,))
    eqvpl__klnl = 'def impl(\n'
    eqvpl__klnl += '    data,\n'
    eqvpl__klnl += '    values=None,\n'
    eqvpl__klnl += '    index=None,\n'
    eqvpl__klnl += '    columns=None,\n'
    eqvpl__klnl += '    aggfunc="mean",\n'
    eqvpl__klnl += '    fill_value=None,\n'
    eqvpl__klnl += '    margins=False,\n'
    eqvpl__klnl += '    dropna=True,\n'
    eqvpl__klnl += '    margins_name="All",\n'
    eqvpl__klnl += '    observed=False,\n'
    eqvpl__klnl += '    sort=True,\n'
    eqvpl__klnl += '    _pivot_values=None,\n'
    eqvpl__klnl += '):\n'
    eqvpl__klnl += "    ev = tracing.Event('df.pivot_table')\n"
    qfj__tld = yhmk__jwjt + [svpcz__mfi] + sso__rlsj
    eqvpl__klnl += f'    data = data.iloc[:, {qfj__tld}]\n'
    lqo__wnbpz = rbzwd__rlib + [vpx__qwq]
    if not is_overload_none(_pivot_values):
        nwjc__btdf = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(nwjc__btdf)
        eqvpl__klnl += '    pivot_values = _pivot_values_arr\n'
        eqvpl__klnl += (
            f'    data = data[data.iloc[:, {len(yhmk__jwjt)}].isin(pivot_values)]\n'
            )
        if all(isinstance(olf__njln, str) for olf__njln in nwjc__btdf):
            ozno__ctd = pd.array(nwjc__btdf, 'string')
        elif all(isinstance(olf__njln, int) for olf__njln in nwjc__btdf):
            ozno__ctd = np.array(nwjc__btdf, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        ozno__ctd = None
    eztaz__zcay = is_overload_constant_str(aggfunc) and get_overload_const_str(
        aggfunc) == 'nunique'
    ddutv__kjrue = len(lqo__wnbpz) if eztaz__zcay else len(rbzwd__rlib)
    eqvpl__klnl += f"""    data = data.groupby({lqo__wnbpz!r}, as_index=False, _bodo_num_shuffle_keys={ddutv__kjrue}).agg(aggfunc)
"""
    if is_overload_none(_pivot_values):
        eqvpl__klnl += (
            f'    pivot_values = data.iloc[:, {len(yhmk__jwjt)}].unique()\n')
    eqvpl__klnl += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    eqvpl__klnl += '        (\n'
    for i in range(0, len(yhmk__jwjt)):
        eqvpl__klnl += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    eqvpl__klnl += '        ),\n'
    eqvpl__klnl += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(yhmk__jwjt)}),),
"""
    eqvpl__klnl += '        (\n'
    for i in range(len(yhmk__jwjt) + 1, len(sso__rlsj) + len(yhmk__jwjt) + 1):
        eqvpl__klnl += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    eqvpl__klnl += '        ),\n'
    eqvpl__klnl += '        pivot_values,\n'
    eqvpl__klnl += '        index_lit,\n'
    eqvpl__klnl += '        columns_lit,\n'
    eqvpl__klnl += '        values_lit,\n'
    eqvpl__klnl += '        check_duplicates=False,\n'
    eqvpl__klnl += f'        is_already_shuffled={not eztaz__zcay},\n'
    eqvpl__klnl += '        _constant_pivot_values=_constant_pivot_values,\n'
    eqvpl__klnl += '    )\n'
    eqvpl__klnl += '    ev.finalize()\n'
    eqvpl__klnl += '    return result\n'
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo, 'numba': numba, 'index_lit':
        wnisk__iwzy, 'columns_lit': pfzo__add, 'values_lit': isd__nnyyd,
        '_pivot_values_arr': ozno__ctd, '_constant_pivot_values':
        _pivot_values, 'tracing': tracing}, php__dced)
    impl = php__dced['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    mztud__ninf = dict(col_level=col_level, ignore_index=ignore_index)
    png__mzmj = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(frame, DataFrameType):
        raise BodoError("pandas.melt(): 'frame' argument must be a DataFrame.")
    if not is_overload_none(id_vars) and not is_literal_type(id_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'id_vars', if specified, must be a literal.")
    if not is_overload_none(value_vars) and not is_literal_type(value_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'value_vars', if specified, must be a literal.")
    if not is_overload_none(var_name) and not (is_literal_type(var_name) and
        (is_scalar_type(var_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'var_name', if specified, must be a literal.")
    if value_name != 'value' and not (is_literal_type(value_name) and (
        is_scalar_type(value_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'value_name', if specified, must be a literal.")
    var_name = get_literal_value(var_name) if not is_overload_none(var_name
        ) else 'variable'
    value_name = get_literal_value(value_name
        ) if value_name != 'value' else 'value'
    yfvwt__yenh = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(yfvwt__yenh, (list, tuple)):
        yfvwt__yenh = [yfvwt__yenh]
    for olf__njln in yfvwt__yenh:
        if olf__njln not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {olf__njln} not found in {frame}."
                )
    axzkx__etdu = [frame.column_index[i] for i in yfvwt__yenh]
    if is_overload_none(value_vars):
        vnn__rczhu = []
        kzs__dse = []
        for i, olf__njln in enumerate(frame.columns):
            if i not in axzkx__etdu:
                vnn__rczhu.append(i)
                kzs__dse.append(olf__njln)
    else:
        kzs__dse = get_literal_value(value_vars)
        if not isinstance(kzs__dse, (list, tuple)):
            kzs__dse = [kzs__dse]
        kzs__dse = [v for v in kzs__dse if v not in yfvwt__yenh]
        if not kzs__dse:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        vnn__rczhu = []
        for val in kzs__dse:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            vnn__rczhu.append(frame.column_index[val])
    for olf__njln in kzs__dse:
        if olf__njln not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {olf__njln} not found in {frame}."
                )
    if not (all(isinstance(olf__njln, int) for olf__njln in kzs__dse) or
        all(isinstance(olf__njln, str) for olf__njln in kzs__dse)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    zmfs__tlg = frame.data[vnn__rczhu[0]]
    lmqmu__sjl = [frame.data[i].dtype for i in vnn__rczhu]
    vnn__rczhu = np.array(vnn__rczhu, dtype=np.int64)
    axzkx__etdu = np.array(axzkx__etdu, dtype=np.int64)
    _, psghz__qqxur = bodo.utils.typing.get_common_scalar_dtype(lmqmu__sjl)
    if not psghz__qqxur:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': kzs__dse, 'val_type': zmfs__tlg}
    header = 'def impl(\n'
    header += '  frame,\n'
    header += '  id_vars=None,\n'
    header += '  value_vars=None,\n'
    header += '  var_name=None,\n'
    header += "  value_name='value',\n"
    header += '  col_level=None,\n'
    header += '  ignore_index=True,\n'
    header += '):\n'
    header += (
        '  dummy_id = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, 0)\n'
        )
    if frame.is_table_format and all(v == zmfs__tlg.dtype for v in lmqmu__sjl):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            vnn__rczhu))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(kzs__dse) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {vnn__rczhu[0]})
"""
    else:
        ueda__ntzu = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in vnn__rczhu)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({ueda__ntzu},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in axzkx__etdu:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(kzs__dse)})\n'
            )
    vhpan__mbehu = ', '.join(f'out_id{i}' for i in axzkx__etdu) + (', ' if 
        len(axzkx__etdu) > 0 else '')
    data_args = vhpan__mbehu + 'var_col, val_col'
    columns = tuple(yfvwt__yenh + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(kzs__dse)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    mztud__ninf = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    png__mzmj = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(index,
        'pandas.crosstab()')
    if not isinstance(index, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'index' argument only supported for Series types, found {index}"
            )
    if not isinstance(columns, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'columns' argument only supported for Series types, found {columns}"
            )

    def _impl(index, columns, values=None, rownames=None, colnames=None,
        aggfunc=None, margins=False, margins_name='All', dropna=True,
        normalize=False, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.crosstab_dummy(index, columns,
            _pivot_values)
    return _impl


@overload_method(DataFrameType, 'sort_values', inline='always',
    no_unliteral=True)
def overload_dataframe_sort_values(df, by, axis=0, ascending=True, inplace=
    False, kind='quicksort', na_position='last', ignore_index=False, key=
    None, _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_values()')
    mztud__ninf = dict(ignore_index=ignore_index, key=key)
    png__mzmj = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'sort_values')
    validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
        na_position)

    def _impl(df, by, axis=0, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', ignore_index=False, key=None,
        _bodo_transformed=False):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df, by,
            ascending, inplace, na_position)
    return _impl


def validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
    na_position):
    if is_overload_none(by) or not is_literal_type(by
        ) and not is_overload_constant_list(by):
        raise_bodo_error(
            "sort_values(): 'by' parameter only supports a constant column label or column labels. by={}"
            .format(by))
    lgm__gcse = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        lgm__gcse.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        glefg__cxxm = [get_overload_const_tuple(by)]
    else:
        glefg__cxxm = get_overload_const_list(by)
    glefg__cxxm = set((k, '') if (k, '') in lgm__gcse else k for k in
        glefg__cxxm)
    if len(glefg__cxxm.difference(lgm__gcse)) > 0:
        chdq__htwm = list(set(get_overload_const_list(by)).difference(
            lgm__gcse))
        raise_bodo_error(f'sort_values(): invalid keys {chdq__htwm} for by.')
    if not is_overload_zero(axis):
        raise_bodo_error(
            "sort_values(): 'axis' parameter only supports integer value 0.")
    if not is_overload_bool(ascending) and not is_overload_bool_list(ascending
        ):
        raise_bodo_error(
            "sort_values(): 'ascending' parameter must be of type bool or list of bool, not {}."
            .format(ascending))
    if not is_overload_bool(inplace):
        raise_bodo_error(
            "sort_values(): 'inplace' parameter must be of type bool, not {}."
            .format(inplace))
    if kind != 'quicksort' and not isinstance(kind, types.Omitted):
        warnings.warn(BodoWarning(
            'sort_values(): specifying sorting algorithm is not supported in Bodo. Bodo uses stable sort.'
            ))
    if is_overload_constant_str(na_position):
        na_position = get_overload_const_str(na_position)
        if na_position not in ('first', 'last'):
            raise BodoError(
                "sort_values(): na_position should either be 'first' or 'last'"
                )
    elif is_overload_constant_list(na_position):
        tykj__qmii = get_overload_const_list(na_position)
        for na_position in tykj__qmii:
            if na_position not in ('first', 'last'):
                raise BodoError(
                    "sort_values(): Every value in na_position should either be 'first' or 'last'"
                    )
    else:
        raise_bodo_error(
            f'sort_values(): na_position parameter must be a literal constant of type str or a constant list of str with 1 entry per key column, not {na_position}'
            )
    na_position = get_overload_const_str(na_position)
    if na_position not in ['first', 'last']:
        raise BodoError(
            "sort_values(): na_position should either be 'first' or 'last'")


@overload_method(DataFrameType, 'sort_index', inline='always', no_unliteral
    =True)
def overload_dataframe_sort_index(df, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_index()')
    mztud__ninf = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    png__mzmj = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_bool(ascending):
        raise BodoError(
            "DataFrame.sort_index(): 'ascending' parameter must be of type bool"
            )
    if not is_overload_bool(inplace):
        raise BodoError(
            "DataFrame.sort_index(): 'inplace' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "DataFrame.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def _impl(df, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df,
            '$_bodo_index_', ascending, inplace, na_position)
    return _impl


@overload_method(DataFrameType, 'rank', inline='always', no_unliteral=True)
def overload_dataframe_rank(df, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    eqvpl__klnl = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    xka__jnytf = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(xka__jnytf))
    for i in range(xka__jnytf):
        eqvpl__klnl += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(eqvpl__klnl, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    mztud__ninf = dict(limit=limit, downcast=downcast)
    png__mzmj = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    ypc__hhdl = not is_overload_none(value)
    dyslp__knsx = not is_overload_none(method)
    if ypc__hhdl and dyslp__knsx:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not ypc__hhdl and not dyslp__knsx:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if ypc__hhdl:
        gjg__sltr = 'value=value'
    else:
        gjg__sltr = 'method=method'
    data_args = [(f"df['{olf__njln}'].fillna({gjg__sltr}, inplace=inplace)" if
        isinstance(olf__njln, str) else
        f'df[{olf__njln}].fillna({gjg__sltr}, inplace=inplace)') for
        olf__njln in df.columns]
    eqvpl__klnl = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        eqvpl__klnl += '  ' + '  \n'.join(data_args) + '\n'
        php__dced = {}
        exec(eqvpl__klnl, {}, php__dced)
        impl = php__dced['impl']
        return impl
    else:
        return _gen_init_df(eqvpl__klnl, df.columns, ', '.join(lqd__ovr +
            '.values' for lqd__ovr in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    mztud__ninf = dict(col_level=col_level, col_fill=col_fill)
    png__mzmj = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'reset_index')
    if not _is_all_levels(df, level):
        raise_bodo_error(
            'DataFrame.reset_index(): only dropping all index levels supported'
            )
    if not is_overload_constant_bool(drop):
        raise BodoError(
            "DataFrame.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.reset_index(): 'inplace' parameter should be a constant boolean value"
            )
    eqvpl__klnl = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    eqvpl__klnl += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(df), 1, None)\n'
        )
    drop = is_overload_true(drop)
    inplace = is_overload_true(inplace)
    columns = df.columns
    data_args = [
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}\n'.
        format(i, '' if inplace else '.copy()') for i in range(len(df.columns))
        ]
    if not drop:
        rwdmc__bziij = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            rwdmc__bziij)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            eqvpl__klnl += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            iroy__vax = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = iroy__vax + data_args
        else:
            edp__wiew = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [edp__wiew] + data_args
    return _gen_init_df(eqvpl__klnl, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    yhzh__tedcd = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and yhzh__tedcd == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(yhzh__tedcd))


@overload_method(DataFrameType, 'dropna', inline='always', no_unliteral=True)
def overload_dataframe_dropna(df, axis=0, how='any', thresh=None, subset=
    None, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.dropna()')
    if not is_overload_constant_bool(inplace) or is_overload_true(inplace):
        raise BodoError('DataFrame.dropna(): inplace=True is not supported')
    if not is_overload_zero(axis):
        raise_bodo_error(f'df.dropna(): only axis=0 supported')
    ensure_constant_values('dropna', 'how', how, ('any', 'all'))
    if is_overload_none(subset):
        akd__iiffe = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        qbm__sksg = get_overload_const_list(subset)
        akd__iiffe = []
        for wjzy__jif in qbm__sksg:
            if wjzy__jif not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{wjzy__jif}' not in data frame columns {df}"
                    )
            akd__iiffe.append(df.column_index[wjzy__jif])
    xka__jnytf = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(xka__jnytf))
    eqvpl__klnl = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(xka__jnytf):
        eqvpl__klnl += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    eqvpl__klnl += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in akd__iiffe)))
    eqvpl__klnl += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(eqvpl__klnl, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    mztud__ninf = dict(index=index, level=level, errors=errors)
    png__mzmj = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', mztud__ninf, png__mzmj,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'drop')
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "DataFrame.drop(): 'inplace' parameter should be a constant bool")
    if not is_overload_none(labels):
        if not is_overload_none(columns):
            raise BodoError(
                "Dataframe.drop(): Cannot specify both 'labels' and 'columns'")
        if not is_overload_constant_int(axis) or get_overload_const_int(axis
            ) != 1:
            raise_bodo_error('DataFrame.drop(): only axis=1 supported')
        if is_overload_constant_str(labels):
            xrpb__dxut = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            xrpb__dxut = get_overload_const_list(labels)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    else:
        if is_overload_none(columns):
            raise BodoError(
                "DataFrame.drop(): Need to specify at least one of 'labels' or 'columns'"
                )
        if is_overload_constant_str(columns):
            xrpb__dxut = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            xrpb__dxut = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for olf__njln in xrpb__dxut:
        if olf__njln not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(olf__njln, df.columns))
    if len(set(xrpb__dxut)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    bouh__rwr = tuple(olf__njln for olf__njln in df.columns if olf__njln not in
        xrpb__dxut)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[olf__njln], '.copy()' if not inplace else ''
        ) for olf__njln in bouh__rwr)
    eqvpl__klnl = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    eqvpl__klnl += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(eqvpl__klnl, bouh__rwr, data_args, index)


@overload_method(DataFrameType, 'append', inline='always', no_unliteral=True)
def overload_dataframe_append(df, other, ignore_index=False,
    verify_integrity=False, sort=None):
    check_runtime_cols_unsupported(df, 'DataFrame.append()')
    check_runtime_cols_unsupported(other, 'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'DataFrame.append()')
    if isinstance(other, DataFrameType):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df, other), ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.BaseTuple):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df,) + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.List) and isinstance(other.dtype, DataFrameType
        ):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat([df] + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    raise BodoError(
        'invalid df.append() input. Only dataframe and list/tuple of dataframes supported'
        )


@overload_method(DataFrameType, 'sample', inline='always', no_unliteral=True)
def overload_dataframe_sample(df, n=None, frac=None, replace=False, weights
    =None, random_state=None, axis=None, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sample()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sample()')
    mztud__ninf = dict(random_state=random_state, weights=weights, axis=
        axis, ignore_index=ignore_index)
    eone__cjqzq = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', mztud__ninf, eone__cjqzq,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    xka__jnytf = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(xka__jnytf))
    xwsms__lkb = ', '.join('rhs_data_{}'.format(i) for i in range(xka__jnytf))
    eqvpl__klnl = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    eqvpl__klnl += '  if (frac == 1 or n == len(df)) and not replace:\n'
    eqvpl__klnl += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(xka__jnytf):
        eqvpl__klnl += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    eqvpl__klnl += '  if frac is None:\n'
    eqvpl__klnl += '    frac_d = -1.0\n'
    eqvpl__klnl += '  else:\n'
    eqvpl__klnl += '    frac_d = frac\n'
    eqvpl__klnl += '  if n is None:\n'
    eqvpl__klnl += '    n_i = 0\n'
    eqvpl__klnl += '  else:\n'
    eqvpl__klnl += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    eqvpl__klnl += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({xwsms__lkb},), {index}, n_i, frac_d, replace)
"""
    eqvpl__klnl += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(eqvpl__klnl, df.
        columns, data_args, 'index')


@numba.njit
def _sizeof_fmt(num, size_qualifier=''):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f'{num:3.1f}{size_qualifier} {x}'
        num /= 1024.0
    return f'{num:3.1f}{size_qualifier} PB'


@overload_method(DataFrameType, 'info', no_unliteral=True)
def overload_dataframe_info(df, verbose=None, buf=None, max_cols=None,
    memory_usage=None, show_counts=None, null_counts=None):
    check_runtime_cols_unsupported(df, 'DataFrame.info()')
    yhgff__eagi = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    cep__fvt = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', yhgff__eagi, cep__fvt,
        package_name='pandas', module_name='DataFrame')
    hhs__cmcfb = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            xfz__lwh = hhs__cmcfb + '\n'
            xfz__lwh += 'Index: 0 entries\n'
            xfz__lwh += 'Empty DataFrame'
            print(xfz__lwh)
        return _info_impl
    else:
        eqvpl__klnl = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        eqvpl__klnl += '    ncols = df.shape[1]\n'
        eqvpl__klnl += f'    lines = "{hhs__cmcfb}\\n"\n'
        eqvpl__klnl += f'    lines += "{df.index}: "\n'
        eqvpl__klnl += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            eqvpl__klnl += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            eqvpl__klnl += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            eqvpl__klnl += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        eqvpl__klnl += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        eqvpl__klnl += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        eqvpl__klnl += '    column_width = max(space, 7)\n'
        eqvpl__klnl += '    column= "Column"\n'
        eqvpl__klnl += '    underl= "------"\n'
        eqvpl__klnl += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        eqvpl__klnl += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        eqvpl__klnl += '    mem_size = 0\n'
        eqvpl__klnl += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        eqvpl__klnl += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        eqvpl__klnl += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        goqcl__pqale = dict()
        for i in range(len(df.columns)):
            eqvpl__klnl += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            gecuo__pti = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                gecuo__pti = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                gfrz__vwu = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                gecuo__pti = f'{gfrz__vwu[:-7]}'
            eqvpl__klnl += f'    col_dtype[{i}] = "{gecuo__pti}"\n'
            if gecuo__pti in goqcl__pqale:
                goqcl__pqale[gecuo__pti] += 1
            else:
                goqcl__pqale[gecuo__pti] = 1
            eqvpl__klnl += f'    col_name[{i}] = "{df.columns[i]}"\n'
            eqvpl__klnl += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        eqvpl__klnl += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        eqvpl__klnl += '    for i in column_info:\n'
        eqvpl__klnl += "        lines += f'{i}\\n'\n"
        zzmc__qejn = ', '.join(f'{k}({goqcl__pqale[k]})' for k in sorted(
            goqcl__pqale))
        eqvpl__klnl += f"    lines += 'dtypes: {zzmc__qejn}\\n'\n"
        eqvpl__klnl += '    mem_size += df.index.nbytes\n'
        eqvpl__klnl += '    total_size = _sizeof_fmt(mem_size)\n'
        eqvpl__klnl += "    lines += f'memory usage: {total_size}'\n"
        eqvpl__klnl += '    print(lines)\n'
        php__dced = {}
        exec(eqvpl__klnl, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, php__dced)
        _info_impl = php__dced['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    eqvpl__klnl = 'def impl(df, index=True, deep=False):\n'
    yknlb__soz = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    pksyz__xvw = is_overload_true(index)
    columns = df.columns
    if pksyz__xvw:
        columns = ('Index',) + columns
    if len(columns) == 0:
        sbpd__uxz = ()
    elif all(isinstance(olf__njln, int) for olf__njln in columns):
        sbpd__uxz = np.array(columns, 'int64')
    elif all(isinstance(olf__njln, str) for olf__njln in columns):
        sbpd__uxz = pd.array(columns, 'string')
    else:
        sbpd__uxz = columns
    if df.is_table_format and len(df.columns) > 0:
        xlfvw__fyqw = int(pksyz__xvw)
        amaq__gbsi = len(columns)
        eqvpl__klnl += f'  nbytes_arr = np.empty({amaq__gbsi}, np.int64)\n'
        eqvpl__klnl += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        eqvpl__klnl += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {xlfvw__fyqw})
"""
        if pksyz__xvw:
            eqvpl__klnl += f'  nbytes_arr[0] = {yknlb__soz}\n'
        eqvpl__klnl += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if pksyz__xvw:
            data = f'{yknlb__soz},{data}'
        else:
            zmf__lvgqa = ',' if len(columns) == 1 else ''
            data = f'{data}{zmf__lvgqa}'
        eqvpl__klnl += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        sbpd__uxz}, php__dced)
    impl = php__dced['impl']
    return impl


@overload(pd.read_excel, no_unliteral=True)
def overload_read_excel(io, sheet_name=0, header=0, names=None, index_col=
    None, usecols=None, squeeze=False, dtype=None, engine=None, converters=
    None, true_values=None, false_values=None, skiprows=None, nrows=None,
    na_values=None, keep_default_na=True, na_filter=True, verbose=False,
    parse_dates=False, date_parser=None, thousands=None, comment=None,
    skipfooter=0, convert_float=True, mangle_dupe_cols=True, _bodo_df_type=None
    ):
    df_type = _bodo_df_type.instance_type
    kwb__xuay = 'read_excel_df{}'.format(next_label())
    setattr(types, kwb__xuay, df_type)
    tyb__nlwup = False
    if is_overload_constant_list(parse_dates):
        tyb__nlwup = get_overload_const_list(parse_dates)
    itas__ynhb = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    eqvpl__klnl = f"""
def impl(
    io,
    sheet_name=0,
    header=0,
    names=None,
    index_col=None,
    usecols=None,
    squeeze=False,
    dtype=None,
    engine=None,
    converters=None,
    true_values=None,
    false_values=None,
    skiprows=None,
    nrows=None,
    na_values=None,
    keep_default_na=True,
    na_filter=True,
    verbose=False,
    parse_dates=False,
    date_parser=None,
    thousands=None,
    comment=None,
    skipfooter=0,
    convert_float=True,
    mangle_dupe_cols=True,
    _bodo_df_type=None,
):
    with numba.objmode(df="{kwb__xuay}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{itas__ynhb}}},
            engine=engine,
            converters=converters,
            true_values=true_values,
            false_values=false_values,
            skiprows=skiprows,
            nrows=nrows,
            na_values=na_values,
            keep_default_na=keep_default_na,
            na_filter=na_filter,
            verbose=verbose,
            parse_dates={tyb__nlwup},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    php__dced = {}
    exec(eqvpl__klnl, globals(), php__dced)
    impl = php__dced['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as oomy__ldue:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    eqvpl__klnl = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    eqvpl__klnl += (
        '    ylabel=None, title=None, legend=True, fontsize=None, \n')
    eqvpl__klnl += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        eqvpl__klnl += '   fig, ax = plt.subplots()\n'
    else:
        eqvpl__klnl += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        eqvpl__klnl += '   fig.set_figwidth(figsize[0])\n'
        eqvpl__klnl += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        eqvpl__klnl += '   xlabel = x\n'
    eqvpl__klnl += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        eqvpl__klnl += '   ylabel = y\n'
    else:
        eqvpl__klnl += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        eqvpl__klnl += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        eqvpl__klnl += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    eqvpl__klnl += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            eqvpl__klnl += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            gocod__svek = get_overload_const_str(x)
            qfk__mmyvp = df.columns.index(gocod__svek)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if qfk__mmyvp != i:
                        eqvpl__klnl += f"""   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])
"""
        else:
            eqvpl__klnl += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        eqvpl__klnl += '   ax.scatter(df[x], df[y], s=20)\n'
        eqvpl__klnl += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        eqvpl__klnl += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        eqvpl__klnl += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        eqvpl__klnl += '   ax.legend()\n'
    eqvpl__klnl += '   return ax\n'
    php__dced = {}
    exec(eqvpl__klnl, {'bodo': bodo, 'plt': plt}, php__dced)
    impl = php__dced['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for jfp__olq in df_typ.data:
        if not (isinstance(jfp__olq, IntegerArrayType) or isinstance(
            jfp__olq.dtype, types.Number) or jfp__olq.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns)):
            return False
    return True


def typeref_to_type(v):
    if isinstance(v, types.BaseTuple):
        return types.BaseTuple.from_types(tuple(typeref_to_type(a) for a in v))
    return v.instance_type if isinstance(v, (types.TypeRef, types.NumberClass)
        ) else v


def _install_typer_for_type(type_name, typ):

    @type_callable(typ)
    def type_call_type(context):

        def typer(*args, **kws):
            args = tuple(typeref_to_type(v) for v in args)
            kws = {name: typeref_to_type(v) for name, v in kws.items()}
            return types.TypeRef(typ(*args, **kws))
        return typer
    no_side_effect_call_tuples.add((type_name, bodo))
    no_side_effect_call_tuples.add((typ,))


def _install_type_call_typers():
    for type_name in bodo_types_with_params:
        typ = getattr(bodo, type_name)
        _install_typer_for_type(type_name, typ)


_install_type_call_typers()


def set_df_col(df, cname, arr, inplace):
    df[cname] = arr


@infer_global(set_df_col)
class SetDfColInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 4
        assert isinstance(args[1], types.Literal)
        lvx__gte = args[0]
        ucr__pfclp = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        vbgl__lfte = lvx__gte
        check_runtime_cols_unsupported(lvx__gte, 'set_df_col()')
        if isinstance(lvx__gte, DataFrameType):
            index = lvx__gte.index
            if len(lvx__gte.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(lvx__gte.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if is_overload_constant_str(val) or val == types.unicode_type:
                val = bodo.dict_str_arr_type
            elif not is_array_typ(val):
                val = dtype_to_array_type(val)
            if ucr__pfclp in lvx__gte.columns:
                bouh__rwr = lvx__gte.columns
                evgu__lfenw = lvx__gte.columns.index(ucr__pfclp)
                plwog__kmhq = list(lvx__gte.data)
                plwog__kmhq[evgu__lfenw] = val
                plwog__kmhq = tuple(plwog__kmhq)
            else:
                bouh__rwr = lvx__gte.columns + (ucr__pfclp,)
                plwog__kmhq = lvx__gte.data + (val,)
            vbgl__lfte = DataFrameType(plwog__kmhq, index, bouh__rwr,
                lvx__gte.dist, lvx__gte.is_table_format)
        return vbgl__lfte(*args)


SetDfColInfer.prefer_literal = True


def __bodosql_replace_columns_dummy(df, col_names_to_replace,
    cols_to_replace_with):
    for i in range(len(col_names_to_replace)):
        df[col_names_to_replace[i]] = cols_to_replace_with[i]


@infer_global(__bodosql_replace_columns_dummy)
class BodoSQLReplaceColsInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 3
        assert is_overload_constant_tuple(args[1])
        assert isinstance(args[2], types.BaseTuple)
        xfabf__puea = args[0]
        assert isinstance(xfabf__puea, DataFrameType) and len(xfabf__puea.
            columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        zbxzx__fpq = args[2]
        assert len(col_names_to_replace) == len(zbxzx__fpq
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(xfabf__puea.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in xfabf__puea.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(xfabf__puea,
            '__bodosql_replace_columns_dummy()')
        index = xfabf__puea.index
        bouh__rwr = xfabf__puea.columns
        plwog__kmhq = list(xfabf__puea.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            ednzm__pobs = zbxzx__fpq[i]
            assert isinstance(ednzm__pobs, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(ednzm__pobs, SeriesType):
                ednzm__pobs = ednzm__pobs.data
            gwhy__znxl = xfabf__puea.column_index[col_name]
            plwog__kmhq[gwhy__znxl] = ednzm__pobs
        plwog__kmhq = tuple(plwog__kmhq)
        vbgl__lfte = DataFrameType(plwog__kmhq, index, bouh__rwr,
            xfabf__puea.dist, xfabf__puea.is_table_format)
        return vbgl__lfte(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    tovjm__ezhd = {}

    def _rewrite_membership_op(self, node, left, right):
        wxoiz__thfw = node.op
        op = self.visit(wxoiz__thfw)
        return op, wxoiz__thfw, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    ikn__madby = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in ikn__madby:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in ikn__madby:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        vjsj__tsr = node.attr
        value = node.value
        cmbrw__gwwb = pd.core.computation.ops.LOCAL_TAG
        if vjsj__tsr in ('str', 'dt'):
            try:
                qgg__uqq = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as fskhp__wjeea:
                col_name = fskhp__wjeea.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            qgg__uqq = str(self.visit(value))
        pej__uhk = qgg__uqq, vjsj__tsr
        if pej__uhk in join_cleaned_cols:
            vjsj__tsr = join_cleaned_cols[pej__uhk]
        name = qgg__uqq + '.' + vjsj__tsr
        if name.startswith(cmbrw__gwwb):
            name = name[len(cmbrw__gwwb):]
        if vjsj__tsr in ('str', 'dt'):
            ohec__kqcv = columns[cleaned_columns.index(qgg__uqq)]
            tovjm__ezhd[ohec__kqcv] = qgg__uqq
            self.env.scope[name] = 0
            return self.term_type(cmbrw__gwwb + name, self.env)
        ikn__madby.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in ikn__madby:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        kwn__qdce = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        ucr__pfclp = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(kwn__qdce), ucr__pfclp))

    def op__str__(self):
        vaas__ajkl = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            wjkzi__ptsuz)) for wjkzi__ptsuz in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(vaas__ajkl)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(vaas__ajkl)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(vaas__ajkl))
    vcsc__hysm = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    eplmh__oowfl = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_evaluate_binop)
    qund__vlh = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    nci__xiw = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    otap__twtsb = pd.core.computation.ops.Term.__str__
    lyiqp__nzfr = pd.core.computation.ops.MathCall.__str__
    gqznz__bxrep = pd.core.computation.ops.Op.__str__
    nlrs__ongan = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
    try:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            _rewrite_membership_op)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            _maybe_evaluate_binop)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = (
            visit_Attribute)
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = lambda self, left, right: (left, right)
        pd.core.computation.ops.Term.__str__ = __str__
        pd.core.computation.ops.MathCall.__str__ = math__str__
        pd.core.computation.ops.Op.__str__ = op__str__
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        tdrll__hknx = pd.core.computation.expr.Expr(expr, env=env)
        dhxq__rpcsk = str(tdrll__hknx)
    except pd.core.computation.ops.UndefinedVariableError as fskhp__wjeea:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == fskhp__wjeea.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {fskhp__wjeea}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            vcsc__hysm)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            eplmh__oowfl)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = qund__vlh
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = nci__xiw
        pd.core.computation.ops.Term.__str__ = otap__twtsb
        pd.core.computation.ops.MathCall.__str__ = lyiqp__nzfr
        pd.core.computation.ops.Op.__str__ = gqznz__bxrep
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            nlrs__ongan)
    fqb__lwk = pd.core.computation.parsing.clean_column_name
    tovjm__ezhd.update({olf__njln: fqb__lwk(olf__njln) for olf__njln in
        columns if fqb__lwk(olf__njln) in tdrll__hknx.names})
    return tdrll__hknx, dhxq__rpcsk, tovjm__ezhd


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        xorzb__zxrr = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(xorzb__zxrr))
        hkw__tzqhd = namedtuple('Pandas', col_names)
        bucya__nnd = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], hkw__tzqhd)
        super(DataFrameTupleIterator, self).__init__(name, bucya__nnd)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_series_dtype(arr_typ):
    if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return pd_timestamp_type
    return arr_typ.dtype


def get_itertuples():
    pass


@infer_global(get_itertuples)
class TypeIterTuples(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) % 2 == 0, 'name and column pairs expected'
        col_names = [a.literal_value for a in args[:len(args) // 2]]
        cttqa__nxxf = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        cttqa__nxxf = [types.Array(types.int64, 1, 'C')] + cttqa__nxxf
        lyfc__qql = DataFrameTupleIterator(col_names, cttqa__nxxf)
        return lyfc__qql(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hvm__dzjcp = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            hvm__dzjcp)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    qjkea__aopeq = args[len(args) // 2:]
    bnqgz__wbkw = sig.args[len(sig.args) // 2:]
    utr__taqs = context.make_helper(builder, sig.return_type)
    gyc__dzr = context.get_constant(types.intp, 0)
    yeu__ktgd = cgutils.alloca_once_value(builder, gyc__dzr)
    utr__taqs.index = yeu__ktgd
    for i, arr in enumerate(qjkea__aopeq):
        setattr(utr__taqs, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(qjkea__aopeq, bnqgz__wbkw):
        context.nrt.incref(builder, arr_typ, arr)
    res = utr__taqs._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    sapx__hgelt, = sig.args
    uinoa__yxv, = args
    utr__taqs = context.make_helper(builder, sapx__hgelt, value=uinoa__yxv)
    ohkku__dkif = signature(types.intp, sapx__hgelt.array_types[1])
    hplgo__ytv = context.compile_internal(builder, lambda a: len(a),
        ohkku__dkif, [utr__taqs.array0])
    index = builder.load(utr__taqs.index)
    iozw__fxjsf = builder.icmp_signed('<', index, hplgo__ytv)
    result.set_valid(iozw__fxjsf)
    with builder.if_then(iozw__fxjsf):
        values = [index]
        for i, arr_typ in enumerate(sapx__hgelt.array_types[1:]):
            gumwr__xjkmv = getattr(utr__taqs, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                xslk__zdcjq = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    xslk__zdcjq, [gumwr__xjkmv, index])
            else:
                xslk__zdcjq = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    xslk__zdcjq, [gumwr__xjkmv, index])
            values.append(val)
        value = context.make_tuple(builder, sapx__hgelt.yield_type, values)
        result.yield_(value)
        uwh__idp = cgutils.increment_index(builder, index)
        builder.store(uwh__idp, utr__taqs.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    ose__uzxgh = ir.Assign(rhs, lhs, expr.loc)
    hxhko__iyg = lhs
    cjn__mlvim = []
    fdhu__bsnu = []
    bpvzc__ferzu = typ.count
    for i in range(bpvzc__ferzu):
        otcc__lecv = ir.Var(hxhko__iyg.scope, mk_unique_var('{}_size{}'.
            format(hxhko__iyg.name, i)), hxhko__iyg.loc)
        pzphg__yrns = ir.Expr.static_getitem(lhs, i, None, hxhko__iyg.loc)
        self.calltypes[pzphg__yrns] = None
        cjn__mlvim.append(ir.Assign(pzphg__yrns, otcc__lecv, hxhko__iyg.loc))
        self._define(equiv_set, otcc__lecv, types.intp, pzphg__yrns)
        fdhu__bsnu.append(otcc__lecv)
    ily__daoab = tuple(fdhu__bsnu)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        ily__daoab, pre=[ose__uzxgh] + cjn__mlvim)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
