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
        gkr__jjxf = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({gkr__jjxf})\n')
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    lltre__dbvc = 'def impl(df):\n'
    if df.has_runtime_cols:
        lltre__dbvc += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        akz__jxg = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        lltre__dbvc += f'  return {akz__jxg}'
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo}, xfz__aecj)
    impl = xfz__aecj['impl']
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
    wgwk__pqkdz = len(df.columns)
    cxz__dexro = set(i for i in range(wgwk__pqkdz) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in cxz__dexro else '') for i in
        range(wgwk__pqkdz))
    lltre__dbvc = 'def f(df):\n'.format()
    lltre__dbvc += '    return np.stack(({},), 1)\n'.format(data_args)
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo, 'np': np}, xfz__aecj)
    fwcva__hqc = xfz__aecj['f']
    return fwcva__hqc


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
    kajif__qtweh = {'dtype': dtype, 'na_value': na_value}
    ttfg__zrq = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', kajif__qtweh, ttfg__zrq,
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
            gwt__zmhj = bodo.hiframes.table.compute_num_runtime_columns(t)
            return gwt__zmhj * len(t)
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
            gwt__zmhj = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), gwt__zmhj
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    lltre__dbvc = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    ygtr__foa = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    lltre__dbvc += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{ygtr__foa}), {index}, None)
"""
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo}, xfz__aecj)
    impl = xfz__aecj['impl']
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
    kajif__qtweh = {'copy': copy, 'errors': errors}
    ttfg__zrq = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', kajif__qtweh, ttfg__zrq,
        package_name='pandas', module_name='DataFrame')
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
        cvmh__ovx = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        hapfw__ifg = _bodo_object_typeref.instance_type
        assert isinstance(hapfw__ifg, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in hapfw__ifg.column_index:
                    idx = hapfw__ifg.column_index[name]
                    arr_typ = hapfw__ifg.data[idx]
                else:
                    arr_typ = df.data[i]
                cvmh__ovx.append(arr_typ)
        else:
            extra_globals = {}
            fbo__mvc = {}
            for i, name in enumerate(hapfw__ifg.columns):
                arr_typ = hapfw__ifg.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    rvp__axd = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    rvp__axd = boolean_dtype
                else:
                    rvp__axd = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = rvp__axd
                fbo__mvc[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {fbo__mvc[selg__nvge]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if selg__nvge in fbo__mvc else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, selg__nvge in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        rmiq__pfi = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            rmiq__pfi = {name: dtype_to_array_type(parse_dtype(dtype)) for 
                name, dtype in rmiq__pfi.items()}
            for i, name in enumerate(df.columns):
                if name in rmiq__pfi:
                    arr_typ = rmiq__pfi[name]
                else:
                    arr_typ = df.data[i]
                cvmh__ovx.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(rmiq__pfi[selg__nvge])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if selg__nvge in rmiq__pfi else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, selg__nvge in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        cvmh__ovx = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        mrfma__pfziu = bodo.TableType(tuple(cvmh__ovx))
        extra_globals['out_table_typ'] = mrfma__pfziu
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
        wat__sxko = types.none
        extra_globals = {'output_arr_typ': wat__sxko}
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
        caftz__edn = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                caftz__edn.append(arr + '.copy()')
            elif is_overload_false(deep):
                caftz__edn.append(arr)
            else:
                caftz__edn.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(caftz__edn)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    kajif__qtweh = {'index': index, 'level': level, 'errors': errors}
    ttfg__zrq = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', kajif__qtweh, ttfg__zrq,
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
        vsw__lhkra = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        vsw__lhkra = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    qus__bjtlh = tuple([vsw__lhkra.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    xzskn__wgq = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        xzskn__wgq = df.copy(columns=qus__bjtlh)
        wat__sxko = types.none
        extra_globals = {'output_arr_typ': wat__sxko}
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
        caftz__edn = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                caftz__edn.append(arr + '.copy()')
            elif is_overload_false(copy):
                caftz__edn.append(arr)
            else:
                caftz__edn.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(caftz__edn)
    return _gen_init_df(header, qus__bjtlh, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    fph__uytt = not is_overload_none(items)
    kpua__jpbu = not is_overload_none(like)
    ddg__imetw = not is_overload_none(regex)
    crw__fkdf = fph__uytt ^ kpua__jpbu ^ ddg__imetw
    tud__yowv = not (fph__uytt or kpua__jpbu or ddg__imetw)
    if tud__yowv:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not crw__fkdf:
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
        lqzm__dsnl = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        lqzm__dsnl = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert lqzm__dsnl in {0, 1}
    lltre__dbvc = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if lqzm__dsnl == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if lqzm__dsnl == 1:
        onp__vmz = []
        fxqy__xuat = []
        tfdu__dccz = []
        if fph__uytt:
            if is_overload_constant_list(items):
                wmgku__txa = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if kpua__jpbu:
            if is_overload_constant_str(like):
                sfvnk__mbti = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if ddg__imetw:
            if is_overload_constant_str(regex):
                dujj__caw = get_overload_const_str(regex)
                lfge__ejdi = re.compile(dujj__caw)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, selg__nvge in enumerate(df.columns):
            if not is_overload_none(items
                ) and selg__nvge in wmgku__txa or not is_overload_none(like
                ) and sfvnk__mbti in str(selg__nvge) or not is_overload_none(
                regex) and lfge__ejdi.search(str(selg__nvge)):
                fxqy__xuat.append(selg__nvge)
                tfdu__dccz.append(i)
        for i in tfdu__dccz:
            var_name = f'data_{i}'
            onp__vmz.append(var_name)
            lltre__dbvc += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(onp__vmz)
        return _gen_init_df(lltre__dbvc, fxqy__xuat, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    xzskn__wgq = None
    if df.is_table_format:
        wat__sxko = types.Array(types.bool_, 1, 'C')
        xzskn__wgq = DataFrameType(tuple([wat__sxko] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': wat__sxko}
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
    qrl__fvthi = is_overload_none(include)
    qtqa__lofmm = is_overload_none(exclude)
    qgjil__bno = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if qrl__fvthi and qtqa__lofmm:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not qrl__fvthi:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            epnvm__jsp = [dtype_to_array_type(parse_dtype(elem, qgjil__bno)
                ) for elem in include]
        elif is_legal_input(include):
            epnvm__jsp = [dtype_to_array_type(parse_dtype(include, qgjil__bno))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        epnvm__jsp = get_nullable_and_non_nullable_types(epnvm__jsp)
        blig__oyc = tuple(selg__nvge for i, selg__nvge in enumerate(df.
            columns) if df.data[i] in epnvm__jsp)
    else:
        blig__oyc = df.columns
    if not qtqa__lofmm:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            pqld__vkaoz = [dtype_to_array_type(parse_dtype(elem, qgjil__bno
                )) for elem in exclude]
        elif is_legal_input(exclude):
            pqld__vkaoz = [dtype_to_array_type(parse_dtype(exclude,
                qgjil__bno))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        pqld__vkaoz = get_nullable_and_non_nullable_types(pqld__vkaoz)
        blig__oyc = tuple(selg__nvge for selg__nvge in blig__oyc if df.data
            [df.column_index[selg__nvge]] not in pqld__vkaoz)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[selg__nvge]})'
         for selg__nvge in blig__oyc)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, blig__oyc, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    xzskn__wgq = None
    if df.is_table_format:
        wat__sxko = types.Array(types.bool_, 1, 'C')
        xzskn__wgq = DataFrameType(tuple([wat__sxko] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': wat__sxko}
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
    hhhie__dkb = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in hhhie__dkb:
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
    hhhie__dkb = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in hhhie__dkb:
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
    lltre__dbvc = 'def impl(df, values):\n'
    uvw__kwzks = {}
    dxcd__hkx = False
    if isinstance(values, DataFrameType):
        dxcd__hkx = True
        for i, selg__nvge in enumerate(df.columns):
            if selg__nvge in values.column_index:
                uizzn__toy = 'val{}'.format(i)
                lltre__dbvc += f"""  {uizzn__toy} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[selg__nvge]})
"""
                uvw__kwzks[selg__nvge] = uizzn__toy
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        uvw__kwzks = {selg__nvge: 'values' for selg__nvge in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        uizzn__toy = 'data{}'.format(i)
        lltre__dbvc += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(uizzn__toy, i))
        data.append(uizzn__toy)
    cmv__zvek = ['out{}'.format(i) for i in range(len(df.columns))]
    xie__gvuj = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    cjq__blxg = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    yzy__vaub = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, ycpsu__krx) in enumerate(zip(df.columns, data)):
        if cname in uvw__kwzks:
            shz__hpyji = uvw__kwzks[cname]
            if dxcd__hkx:
                lltre__dbvc += xie__gvuj.format(ycpsu__krx, shz__hpyji,
                    cmv__zvek[i])
            else:
                lltre__dbvc += cjq__blxg.format(ycpsu__krx, shz__hpyji,
                    cmv__zvek[i])
        else:
            lltre__dbvc += yzy__vaub.format(cmv__zvek[i])
    return _gen_init_df(lltre__dbvc, df.columns, ','.join(cmv__zvek))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    wgwk__pqkdz = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(wgwk__pqkdz))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    dbiqf__qqf = [selg__nvge for selg__nvge, vafg__rzihu in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(vafg__rzihu.
        dtype)]
    assert len(dbiqf__qqf) != 0
    agn__wcc = ''
    if not any(vafg__rzihu == types.float64 for vafg__rzihu in df.data):
        agn__wcc = '.astype(np.float64)'
    ecejt__ozfbk = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[selg__nvge], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[selg__nvge]], IntegerArrayType) or
        df.data[df.column_index[selg__nvge]] == boolean_array else '') for
        selg__nvge in dbiqf__qqf)
    maof__mpj = 'np.stack(({},), 1){}'.format(ecejt__ozfbk, agn__wcc)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(dbiqf__qqf))
        )
    index = f'{generate_col_to_index_func_text(dbiqf__qqf)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(maof__mpj)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, dbiqf__qqf, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    mmgj__nygc = dict(ddof=ddof)
    fph__hpqi = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    lgz__ckfpp = '1' if is_overload_none(min_periods) else 'min_periods'
    dbiqf__qqf = [selg__nvge for selg__nvge, vafg__rzihu in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(vafg__rzihu.
        dtype)]
    if len(dbiqf__qqf) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    agn__wcc = ''
    if not any(vafg__rzihu == types.float64 for vafg__rzihu in df.data):
        agn__wcc = '.astype(np.float64)'
    ecejt__ozfbk = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[selg__nvge], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[selg__nvge]], IntegerArrayType) or
        df.data[df.column_index[selg__nvge]] == boolean_array else '') for
        selg__nvge in dbiqf__qqf)
    maof__mpj = 'np.stack(({},), 1){}'.format(ecejt__ozfbk, agn__wcc)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(dbiqf__qqf))
        )
    index = f'pd.Index({dbiqf__qqf})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(maof__mpj)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        lgz__ckfpp)
    return _gen_init_df(header, dbiqf__qqf, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    mmgj__nygc = dict(axis=axis, level=level, numeric_only=numeric_only)
    fph__hpqi = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    lltre__dbvc = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    lltre__dbvc += '  data = np.array([{}])\n'.format(data_args)
    akz__jxg = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    lltre__dbvc += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {akz__jxg})\n'
        )
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo, 'np': np}, xfz__aecj)
    impl = xfz__aecj['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    mmgj__nygc = dict(axis=axis)
    fph__hpqi = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    lltre__dbvc = 'def impl(df, axis=0, dropna=True):\n'
    lltre__dbvc += '  data = np.asarray(({},))\n'.format(data_args)
    akz__jxg = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    lltre__dbvc += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {akz__jxg})\n'
        )
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo, 'np': np}, xfz__aecj)
    impl = xfz__aecj['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    mmgj__nygc = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    fph__hpqi = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    mmgj__nygc = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    fph__hpqi = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    mmgj__nygc = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fph__hpqi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    mmgj__nygc = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fph__hpqi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    mmgj__nygc = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fph__hpqi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    mmgj__nygc = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fph__hpqi = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    mmgj__nygc = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fph__hpqi = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    mmgj__nygc = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fph__hpqi = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    mmgj__nygc = dict(numeric_only=numeric_only, interpolation=interpolation)
    fph__hpqi = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    mmgj__nygc = dict(axis=axis, skipna=skipna)
    fph__hpqi = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for fyxv__utm in df.data:
        if not (bodo.utils.utils.is_np_array_typ(fyxv__utm) and (fyxv__utm.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            fyxv__utm.dtype, (types.Number, types.Boolean))) or isinstance(
            fyxv__utm, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            fyxv__utm in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {fyxv__utm} not supported.'
                )
        if isinstance(fyxv__utm, bodo.CategoricalArrayType
            ) and not fyxv__utm.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    mmgj__nygc = dict(axis=axis, skipna=skipna)
    fph__hpqi = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for fyxv__utm in df.data:
        if not (bodo.utils.utils.is_np_array_typ(fyxv__utm) and (fyxv__utm.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            fyxv__utm.dtype, (types.Number, types.Boolean))) or isinstance(
            fyxv__utm, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            fyxv__utm in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {fyxv__utm} not supported.'
                )
        if isinstance(fyxv__utm, bodo.CategoricalArrayType
            ) and not fyxv__utm.dtype.ordered:
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
        dbiqf__qqf = tuple(selg__nvge for selg__nvge, vafg__rzihu in zip(df
            .columns, df.data) if bodo.utils.typing.
            _is_pandas_numeric_dtype(vafg__rzihu.dtype))
        out_colnames = dbiqf__qqf
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            zsssp__uikv = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[selg__nvge]].dtype) for selg__nvge in out_colnames
                ]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(zsssp__uikv, []))
    except NotImplementedError as vev__sofb:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    ffwiv__kap = ''
    if func_name in ('sum', 'prod'):
        ffwiv__kap = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    lltre__dbvc = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, ffwiv__kap))
    if func_name == 'quantile':
        lltre__dbvc = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        lltre__dbvc = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        lltre__dbvc += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        lltre__dbvc += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        xfz__aecj)
    impl = xfz__aecj['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    fdisb__yof = ''
    if func_name in ('min', 'max'):
        fdisb__yof = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        fdisb__yof = ', dtype=np.float32'
    ujivf__xzgnl = f'bodo.libs.array_ops.array_op_{func_name}'
    qqgre__cbdvo = ''
    if func_name in ['sum', 'prod']:
        qqgre__cbdvo = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        qqgre__cbdvo = 'index'
    elif func_name == 'quantile':
        qqgre__cbdvo = 'q'
    elif func_name in ['std', 'var']:
        qqgre__cbdvo = 'True, ddof'
    elif func_name == 'median':
        qqgre__cbdvo = 'True'
    data_args = ', '.join(
        f'{ujivf__xzgnl}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[selg__nvge]}), {qqgre__cbdvo})'
         for selg__nvge in out_colnames)
    lltre__dbvc = ''
    if func_name in ('idxmax', 'idxmin'):
        lltre__dbvc += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        lltre__dbvc += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        lltre__dbvc += '  data = np.asarray(({},){})\n'.format(data_args,
            fdisb__yof)
    lltre__dbvc += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return lltre__dbvc


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    jetw__igqn = [df_type.column_index[selg__nvge] for selg__nvge in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in jetw__igqn)
    aai__bwgpc = '\n        '.join(f'row[{i}] = arr_{jetw__igqn[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    bcm__ddsy = f'len(arr_{jetw__igqn[0]})'
    jhlff__ojo = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in jhlff__ojo:
        owtn__xyibd = jhlff__ojo[func_name]
        lrgrw__mys = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        lltre__dbvc = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {bcm__ddsy}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{lrgrw__mys})
    for i in numba.parfors.parfor.internal_prange(n):
        {aai__bwgpc}
        A[i] = {owtn__xyibd}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return lltre__dbvc
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    mmgj__nygc = dict(fill_method=fill_method, limit=limit, freq=freq)
    fph__hpqi = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', mmgj__nygc, fph__hpqi,
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
    mmgj__nygc = dict(axis=axis, skipna=skipna)
    fph__hpqi = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', mmgj__nygc, fph__hpqi,
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
    mmgj__nygc = dict(skipna=skipna)
    fph__hpqi = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', mmgj__nygc, fph__hpqi,
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
    mmgj__nygc = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    fph__hpqi = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    dbiqf__qqf = [selg__nvge for selg__nvge, vafg__rzihu in zip(df.columns,
        df.data) if _is_describe_type(vafg__rzihu)]
    if len(dbiqf__qqf) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    gitb__oui = sum(df.data[df.column_index[selg__nvge]].dtype == bodo.
        datetime64ns for selg__nvge in dbiqf__qqf)

    def _get_describe(col_ind):
        sska__quesb = df.data[col_ind].dtype == bodo.datetime64ns
        if gitb__oui and gitb__oui != len(dbiqf__qqf):
            if sska__quesb:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for selg__nvge in dbiqf__qqf:
        col_ind = df.column_index[selg__nvge]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[selg__nvge]) for
        selg__nvge in dbiqf__qqf)
    zsxh__rmjpj = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if gitb__oui == len(dbiqf__qqf):
        zsxh__rmjpj = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif gitb__oui:
        zsxh__rmjpj = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({zsxh__rmjpj})'
    return _gen_init_df(header, dbiqf__qqf, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    mmgj__nygc = dict(axis=axis, convert=convert, is_copy=is_copy)
    fph__hpqi = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', mmgj__nygc, fph__hpqi,
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
    mmgj__nygc = dict(freq=freq, axis=axis, fill_value=fill_value)
    fph__hpqi = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for wylt__vfb in df.data:
        if not is_supported_shift_array_type(wylt__vfb):
            raise BodoError(
                f'Dataframe.shift() column input type {wylt__vfb.dtype} not supported yet.'
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
    mmgj__nygc = dict(axis=axis)
    fph__hpqi = dict(axis=0)
    check_unsupported_args('DataFrame.diff', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for wylt__vfb in df.data:
        if not (isinstance(wylt__vfb, types.Array) and (isinstance(
            wylt__vfb.dtype, types.Number) or wylt__vfb.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {wylt__vfb.dtype} not supported.'
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
    qfjg__bxb = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(qfjg__bxb)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        vgpgd__ebn = get_overload_const_list(column)
    else:
        vgpgd__ebn = [get_literal_value(column)]
    tur__lurac = [df.column_index[selg__nvge] for selg__nvge in vgpgd__ebn]
    for i in tur__lurac:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{tur__lurac[0]})\n'
        )
    for i in range(n):
        if i in tur__lurac:
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
    kajif__qtweh = {'inplace': inplace, 'append': append,
        'verify_integrity': verify_integrity}
    ttfg__zrq = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', kajif__qtweh, ttfg__zrq,
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
    columns = tuple(selg__nvge for selg__nvge in df.columns if selg__nvge !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    kajif__qtweh = {'inplace': inplace}
    ttfg__zrq = {'inplace': False}
    check_unsupported_args('query', kajif__qtweh, ttfg__zrq, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        wshh__clq = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[wshh__clq]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    kajif__qtweh = {'subset': subset, 'keep': keep}
    ttfg__zrq = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', kajif__qtweh, ttfg__zrq,
        package_name='pandas', module_name='DataFrame')
    wgwk__pqkdz = len(df.columns)
    lltre__dbvc = "def impl(df, subset=None, keep='first'):\n"
    for i in range(wgwk__pqkdz):
        lltre__dbvc += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    jqakc__dgzs = ', '.join(f'data_{i}' for i in range(wgwk__pqkdz))
    jqakc__dgzs += ',' if wgwk__pqkdz == 1 else ''
    lltre__dbvc += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({jqakc__dgzs}))\n'
        )
    lltre__dbvc += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    lltre__dbvc += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo}, xfz__aecj)
    impl = xfz__aecj['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    kajif__qtweh = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    ttfg__zrq = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    zdlxh__jit = []
    if is_overload_constant_list(subset):
        zdlxh__jit = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        zdlxh__jit = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        zdlxh__jit = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    cpmyz__ehrh = []
    for col_name in zdlxh__jit:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        cpmyz__ehrh.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', kajif__qtweh,
        ttfg__zrq, package_name='pandas', module_name='DataFrame')
    xrrxo__jaovw = []
    if cpmyz__ehrh:
        for tglx__nkzr in cpmyz__ehrh:
            if isinstance(df.data[tglx__nkzr], bodo.MapArrayType):
                xrrxo__jaovw.append(df.columns[tglx__nkzr])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                xrrxo__jaovw.append(col_name)
    if xrrxo__jaovw:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {xrrxo__jaovw} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    wgwk__pqkdz = len(df.columns)
    lbsx__qdamj = ['data_{}'.format(i) for i in cpmyz__ehrh]
    mwvq__fea = ['data_{}'.format(i) for i in range(wgwk__pqkdz) if i not in
        cpmyz__ehrh]
    if lbsx__qdamj:
        bwf__qdm = len(lbsx__qdamj)
    else:
        bwf__qdm = wgwk__pqkdz
    corwx__krmz = ', '.join(lbsx__qdamj + mwvq__fea)
    data_args = ', '.join('data_{}'.format(i) for i in range(wgwk__pqkdz))
    lltre__dbvc = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(wgwk__pqkdz):
        lltre__dbvc += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    lltre__dbvc += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(corwx__krmz, index, bwf__qdm))
    lltre__dbvc += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(lltre__dbvc, df.columns, data_args, 'index')


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
            uymx__hksy = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                uymx__hksy = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                uymx__hksy = lambda i: f'other[:,{i}]'
        wgwk__pqkdz = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {uymx__hksy(i)})'
             for i in range(wgwk__pqkdz))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        ffs__orea = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(ffs__orea)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    mmgj__nygc = dict(inplace=inplace, level=level, errors=errors, try_cast
        =try_cast)
    fph__hpqi = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', mmgj__nygc, fph__hpqi,
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
    wgwk__pqkdz = len(df.columns)
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
        for i in range(wgwk__pqkdz):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(wgwk__pqkdz):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(wgwk__pqkdz):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    mqb__hng = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    lltre__dbvc = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    xfz__aecj = {}
    yueyd__vsb = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': mqb__hng}
    yueyd__vsb.update(extra_globals)
    exec(lltre__dbvc, yueyd__vsb, xfz__aecj)
    impl = xfz__aecj['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        uldj__vfjxi = pd.Index(lhs.columns)
        jts__iqjy = pd.Index(rhs.columns)
        uomb__eaux, zpsws__abay, elln__qenp = uldj__vfjxi.join(jts__iqjy,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(uomb__eaux), zpsws__abay, elln__qenp
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        jrfxi__fskeg = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        wfk__nmr = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, jrfxi__fskeg)
        check_runtime_cols_unsupported(rhs, jrfxi__fskeg)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                uomb__eaux, zpsws__abay, elln__qenp = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {kgyi__smil}) {jrfxi__fskeg}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {atm__vjel})'
                     if kgyi__smil != -1 and atm__vjel != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for kgyi__smil, atm__vjel in zip(zpsws__abay, elln__qenp))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, uomb__eaux, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            cghv__ibvyt = []
            bar__fdb = []
            if op in wfk__nmr:
                for i, ydukp__oqmby in enumerate(lhs.data):
                    if is_common_scalar_dtype([ydukp__oqmby.dtype, rhs]):
                        cghv__ibvyt.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {jrfxi__fskeg} rhs'
                            )
                    else:
                        ddyc__mokmq = f'arr{i}'
                        bar__fdb.append(ddyc__mokmq)
                        cghv__ibvyt.append(ddyc__mokmq)
                data_args = ', '.join(cghv__ibvyt)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {jrfxi__fskeg} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(bar__fdb) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {ddyc__mokmq} = np.empty(n, dtype=np.bool_)\n' for
                    ddyc__mokmq in bar__fdb)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(ddyc__mokmq, 
                    op == operator.ne) for ddyc__mokmq in bar__fdb)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            cghv__ibvyt = []
            bar__fdb = []
            if op in wfk__nmr:
                for i, ydukp__oqmby in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, ydukp__oqmby.dtype]):
                        cghv__ibvyt.append(
                            f'lhs {jrfxi__fskeg} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        ddyc__mokmq = f'arr{i}'
                        bar__fdb.append(ddyc__mokmq)
                        cghv__ibvyt.append(ddyc__mokmq)
                data_args = ', '.join(cghv__ibvyt)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, jrfxi__fskeg) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(bar__fdb) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(ddyc__mokmq) for ddyc__mokmq in bar__fdb)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(ddyc__mokmq, 
                    op == operator.ne) for ddyc__mokmq in bar__fdb)
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
        ffs__orea = create_binary_op_overload(op)
        overload(op)(ffs__orea)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        jrfxi__fskeg = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, jrfxi__fskeg)
        check_runtime_cols_unsupported(right, jrfxi__fskeg)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                uomb__eaux, _, elln__qenp = _get_binop_columns(left, right,
                    True)
                lltre__dbvc = 'def impl(left, right):\n'
                for i, atm__vjel in enumerate(elln__qenp):
                    if atm__vjel == -1:
                        lltre__dbvc += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    lltre__dbvc += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    lltre__dbvc += f"""  df_arr{i} {jrfxi__fskeg} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {atm__vjel})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    uomb__eaux)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(lltre__dbvc, uomb__eaux, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            lltre__dbvc = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                lltre__dbvc += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                lltre__dbvc += '  df_arr{0} {1} right\n'.format(i, jrfxi__fskeg
                    )
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(lltre__dbvc, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        ffs__orea = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(ffs__orea)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            jrfxi__fskeg = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, jrfxi__fskeg)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, jrfxi__fskeg) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        ffs__orea = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(ffs__orea)


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
            wrm__iofpv = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                wrm__iofpv[i] = bodo.libs.array_kernels.isna(obj, i)
            return wrm__iofpv
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
            wrm__iofpv = np.empty(n, np.bool_)
            for i in range(n):
                wrm__iofpv[i] = pd.isna(obj[i])
            return wrm__iofpv
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
    kajif__qtweh = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    ttfg__zrq = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', kajif__qtweh, ttfg__zrq, package_name
        ='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    pux__qvlyq = str(expr_node)
    return pux__qvlyq.startswith('left.') or pux__qvlyq.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    xqnl__bhpo = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (xqnl__bhpo,))
    utq__nwt = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        tdhrv__apclb = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        zftsi__mpti = {('NOT_NA', utq__nwt(ydukp__oqmby)): ydukp__oqmby for
            ydukp__oqmby in null_set}
        qrenz__dlc, _, _ = _parse_query_expr(tdhrv__apclb, env, [], [],
            None, join_cleaned_cols=zftsi__mpti)
        ncjs__mpdi = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            bhgei__rvmwo = pd.core.computation.ops.BinOp('&', qrenz__dlc,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = ncjs__mpdi
        return bhgei__rvmwo

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                sivs__jio = set()
                fmyuo__ywop = set()
                ngug__qerfc = _insert_NA_cond_body(expr_node.lhs, sivs__jio)
                gea__ikiie = _insert_NA_cond_body(expr_node.rhs, fmyuo__ywop)
                pqiv__udmrq = sivs__jio.intersection(fmyuo__ywop)
                sivs__jio.difference_update(pqiv__udmrq)
                fmyuo__ywop.difference_update(pqiv__udmrq)
                null_set.update(pqiv__udmrq)
                expr_node.lhs = append_null_checks(ngug__qerfc, sivs__jio)
                expr_node.rhs = append_null_checks(gea__ikiie, fmyuo__ywop)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            hqi__myel = expr_node.name
            zfom__rwdd, col_name = hqi__myel.split('.')
            if zfom__rwdd == 'left':
                quhhe__sfjs = left_columns
                data = left_data
            else:
                quhhe__sfjs = right_columns
                data = right_data
            hhm__agho = data[quhhe__sfjs.index(col_name)]
            if bodo.utils.typing.is_nullable(hhm__agho):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    pebpj__qmz = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        otyfq__tixwr = str(expr_node.lhs)
        rglw__gmnv = str(expr_node.rhs)
        if otyfq__tixwr.startswith('left.') and rglw__gmnv.startswith('left.'
            ) or otyfq__tixwr.startswith('right.') and rglw__gmnv.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [otyfq__tixwr.split('.')[1]]
        right_on = [rglw__gmnv.split('.')[1]]
        if otyfq__tixwr.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        cbr__bqxe, gce__xvyzp, mhf__zdn = _extract_equal_conds(expr_node.lhs)
        aholm__wryqk, yid__btloo, frvwy__vtri = _extract_equal_conds(expr_node
            .rhs)
        left_on = cbr__bqxe + aholm__wryqk
        right_on = gce__xvyzp + yid__btloo
        if mhf__zdn is None:
            return left_on, right_on, frvwy__vtri
        if frvwy__vtri is None:
            return left_on, right_on, mhf__zdn
        expr_node.lhs = mhf__zdn
        expr_node.rhs = frvwy__vtri
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    xqnl__bhpo = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (xqnl__bhpo,))
    vsw__lhkra = dict()
    utq__nwt = pd.core.computation.parsing.clean_column_name
    for name, fupe__bwi in (('left', left_columns), ('right', right_columns)):
        for ydukp__oqmby in fupe__bwi:
            gdyr__yaqj = utq__nwt(ydukp__oqmby)
            urggr__bxvyk = name, gdyr__yaqj
            if urggr__bxvyk in vsw__lhkra:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{ydukp__oqmby}' and '{vsw__lhkra[gdyr__yaqj]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            vsw__lhkra[urggr__bxvyk] = ydukp__oqmby
    zbxxm__bki, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=vsw__lhkra)
    left_on, right_on, esfn__yyc = _extract_equal_conds(zbxxm__bki.terms)
    return left_on, right_on, _insert_NA_cond(esfn__yyc, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    mmgj__nygc = dict(sort=sort, copy=copy, validate=validate)
    fph__hpqi = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    mxr__lscxc = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    vta__ofksu = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in mxr__lscxc and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, zohfa__axcdx = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if zohfa__axcdx is None:
                    vta__ofksu = ''
                else:
                    vta__ofksu = str(zohfa__axcdx)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = mxr__lscxc
        right_keys = mxr__lscxc
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
    hlvm__srxh = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        zbf__aexeb = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        zbf__aexeb = list(get_overload_const_list(suffixes))
    suffix_x = zbf__aexeb[0]
    suffix_y = zbf__aexeb[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    lltre__dbvc = (
        "def _impl(left, right, how='inner', on=None, left_on=None,\n")
    lltre__dbvc += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    lltre__dbvc += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    lltre__dbvc += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, hlvm__srxh, vta__ofksu))
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo}, xfz__aecj)
    _impl = xfz__aecj['_impl']
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
    ahk__cgpo = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    yutin__fczm = {get_overload_const_str(okll__iji) for okll__iji in (
        left_on, right_on, on) if is_overload_constant_str(okll__iji)}
    for df in (left, right):
        for i, ydukp__oqmby in enumerate(df.data):
            if not isinstance(ydukp__oqmby, valid_dataframe_column_types
                ) and ydukp__oqmby not in ahk__cgpo:
                raise BodoError(
                    f'{name_func}(): use of column with {type(ydukp__oqmby)} in merge unsupported'
                    )
            if df.columns[i] in yutin__fczm and isinstance(ydukp__oqmby,
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
        zbf__aexeb = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        zbf__aexeb = list(get_overload_const_list(suffixes))
    if len(zbf__aexeb) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    mxr__lscxc = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        xeb__oinhx = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            xeb__oinhx = on_str not in mxr__lscxc and ('left.' in on_str or
                'right.' in on_str)
        if len(mxr__lscxc) == 0 and not xeb__oinhx:
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
    qux__xgpe = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            zsabc__yakee = left.index
            aeso__ixd = isinstance(zsabc__yakee, StringIndexType)
            gjhp__anr = right.index
            ucuzz__fhc = isinstance(gjhp__anr, StringIndexType)
        elif is_overload_true(left_index):
            zsabc__yakee = left.index
            aeso__ixd = isinstance(zsabc__yakee, StringIndexType)
            gjhp__anr = right.data[right.columns.index(right_keys[0])]
            ucuzz__fhc = gjhp__anr.dtype == string_type
        elif is_overload_true(right_index):
            zsabc__yakee = left.data[left.columns.index(left_keys[0])]
            aeso__ixd = zsabc__yakee.dtype == string_type
            gjhp__anr = right.index
            ucuzz__fhc = isinstance(gjhp__anr, StringIndexType)
        if aeso__ixd and ucuzz__fhc:
            return
        zsabc__yakee = zsabc__yakee.dtype
        gjhp__anr = gjhp__anr.dtype
        try:
            hzqg__pws = qux__xgpe.resolve_function_type(operator.eq, (
                zsabc__yakee, gjhp__anr), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=zsabc__yakee, rk_dtype=gjhp__anr))
    else:
        for wys__nkpk, mhms__syzl in zip(left_keys, right_keys):
            zsabc__yakee = left.data[left.columns.index(wys__nkpk)].dtype
            lusls__fmr = left.data[left.columns.index(wys__nkpk)]
            gjhp__anr = right.data[right.columns.index(mhms__syzl)].dtype
            clej__metb = right.data[right.columns.index(mhms__syzl)]
            if lusls__fmr == clej__metb:
                continue
            kvl__lmyq = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=wys__nkpk, lk_dtype=zsabc__yakee, rk=mhms__syzl,
                rk_dtype=gjhp__anr))
            upboc__fxcd = zsabc__yakee == string_type
            muow__trrd = gjhp__anr == string_type
            if upboc__fxcd ^ muow__trrd:
                raise_bodo_error(kvl__lmyq)
            try:
                hzqg__pws = qux__xgpe.resolve_function_type(operator.eq, (
                    zsabc__yakee, gjhp__anr), {})
            except:
                raise_bodo_error(kvl__lmyq)


def validate_keys(keys, df):
    fwu__fzhih = set(keys).difference(set(df.columns))
    if len(fwu__fzhih) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in fwu__fzhih:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {fwu__fzhih} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    mmgj__nygc = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    fph__hpqi = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', mmgj__nygc, fph__hpqi,
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
    lltre__dbvc = "def _impl(left, other, on=None, how='left',\n"
    lltre__dbvc += "    lsuffix='', rsuffix='', sort=False):\n"
    lltre__dbvc += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo}, xfz__aecj)
    _impl = xfz__aecj['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        veh__vxxu = get_overload_const_list(on)
        validate_keys(veh__vxxu, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    mxr__lscxc = tuple(set(left.columns) & set(other.columns))
    if len(mxr__lscxc) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=mxr__lscxc))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    ssfjs__ozax = set(left_keys) & set(right_keys)
    gfjri__bnjbo = set(left_columns) & set(right_columns)
    clx__kqlx = gfjri__bnjbo - ssfjs__ozax
    ohxb__wkdmh = set(left_columns) - gfjri__bnjbo
    lagoj__sxx = set(right_columns) - gfjri__bnjbo
    eou__vmkm = {}

    def insertOutColumn(col_name):
        if col_name in eou__vmkm:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        eou__vmkm[col_name] = 0
    for rmdwt__lkvvt in ssfjs__ozax:
        insertOutColumn(rmdwt__lkvvt)
    for rmdwt__lkvvt in clx__kqlx:
        hgih__pde = str(rmdwt__lkvvt) + suffix_x
        qyor__rytib = str(rmdwt__lkvvt) + suffix_y
        insertOutColumn(hgih__pde)
        insertOutColumn(qyor__rytib)
    for rmdwt__lkvvt in ohxb__wkdmh:
        insertOutColumn(rmdwt__lkvvt)
    for rmdwt__lkvvt in lagoj__sxx:
        insertOutColumn(rmdwt__lkvvt)
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
    mxr__lscxc = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = mxr__lscxc
        right_keys = mxr__lscxc
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
        zbf__aexeb = suffixes
    if is_overload_constant_list(suffixes):
        zbf__aexeb = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        zbf__aexeb = suffixes.value
    suffix_x = zbf__aexeb[0]
    suffix_y = zbf__aexeb[1]
    lltre__dbvc = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    lltre__dbvc += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    lltre__dbvc += (
        "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n")
    lltre__dbvc += "    allow_exact_matches=True, direction='backward'):\n"
    lltre__dbvc += '  suffix_x = suffixes[0]\n'
    lltre__dbvc += '  suffix_y = suffixes[1]\n'
    lltre__dbvc += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo}, xfz__aecj)
    _impl = xfz__aecj['_impl']
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
    mmgj__nygc = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    hnnao__lhu = dict(sort=False, group_keys=True, squeeze=False, observed=True
        )
    check_unsupported_args('Dataframe.groupby', mmgj__nygc, hnnao__lhu,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    moo__hwuq = func_name == 'DataFrame.pivot_table'
    if moo__hwuq:
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
    spojd__sbl = get_literal_value(columns)
    if isinstance(spojd__sbl, (list, tuple)):
        if len(spojd__sbl) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {spojd__sbl}"
                )
        spojd__sbl = spojd__sbl[0]
    if spojd__sbl not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {spojd__sbl} not found in DataFrame {df}."
            )
    yfqnl__mqoi = df.column_index[spojd__sbl]
    if is_overload_none(index):
        dfniq__vgkc = []
        qrl__ymp = []
    else:
        qrl__ymp = get_literal_value(index)
        if not isinstance(qrl__ymp, (list, tuple)):
            qrl__ymp = [qrl__ymp]
        dfniq__vgkc = []
        for index in qrl__ymp:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            dfniq__vgkc.append(df.column_index[index])
    if not (all(isinstance(selg__nvge, int) for selg__nvge in qrl__ymp) or
        all(isinstance(selg__nvge, str) for selg__nvge in qrl__ymp)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        vbh__iwmsz = []
        qjw__vdav = []
        ytk__hhn = dfniq__vgkc + [yfqnl__mqoi]
        for i, selg__nvge in enumerate(df.columns):
            if i not in ytk__hhn:
                vbh__iwmsz.append(i)
                qjw__vdav.append(selg__nvge)
    else:
        qjw__vdav = get_literal_value(values)
        if not isinstance(qjw__vdav, (list, tuple)):
            qjw__vdav = [qjw__vdav]
        vbh__iwmsz = []
        for val in qjw__vdav:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            vbh__iwmsz.append(df.column_index[val])
    ikfds__gtj = set(vbh__iwmsz) | set(dfniq__vgkc) | {yfqnl__mqoi}
    if len(ikfds__gtj) != len(vbh__iwmsz) + len(dfniq__vgkc) + 1:
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
    if len(dfniq__vgkc) == 0:
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
        for dfbq__wlkke in dfniq__vgkc:
            index_column = df.data[dfbq__wlkke]
            check_valid_index_typ(index_column)
    qjppp__saktj = df.data[yfqnl__mqoi]
    if isinstance(qjppp__saktj, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(qjppp__saktj, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for gjpoa__hux in vbh__iwmsz:
        dpw__ftxql = df.data[gjpoa__hux]
        if isinstance(dpw__ftxql, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or dpw__ftxql == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (qrl__ymp, spojd__sbl, qjw__vdav, dfniq__vgkc, yfqnl__mqoi,
        vbh__iwmsz)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (qrl__ymp, spojd__sbl, qjw__vdav, dfbq__wlkke, yfqnl__mqoi, ldl__dbqf) = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(qrl__ymp) == 0:
        if is_overload_none(data.index.name_typ):
            rjany__yig = None,
        else:
            rjany__yig = get_literal_value(data.index.name_typ),
    else:
        rjany__yig = tuple(qrl__ymp)
    qrl__ymp = ColNamesMetaType(rjany__yig)
    qjw__vdav = ColNamesMetaType(tuple(qjw__vdav))
    spojd__sbl = ColNamesMetaType((spojd__sbl,))
    lltre__dbvc = 'def impl(data, index=None, columns=None, values=None):\n'
    lltre__dbvc += "    ev = tracing.Event('df.pivot')\n"
    lltre__dbvc += f'    pivot_values = data.iloc[:, {yfqnl__mqoi}].unique()\n'
    lltre__dbvc += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(dfbq__wlkke) == 0:
        lltre__dbvc += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        lltre__dbvc += '        (\n'
        for idjn__sovdc in dfbq__wlkke:
            lltre__dbvc += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {idjn__sovdc}),
"""
        lltre__dbvc += '        ),\n'
    lltre__dbvc += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {yfqnl__mqoi}),),
"""
    lltre__dbvc += '        (\n'
    for gjpoa__hux in ldl__dbqf:
        lltre__dbvc += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {gjpoa__hux}),
"""
    lltre__dbvc += '        ),\n'
    lltre__dbvc += '        pivot_values,\n'
    lltre__dbvc += '        index_lit,\n'
    lltre__dbvc += '        columns_lit,\n'
    lltre__dbvc += '        values_lit,\n'
    lltre__dbvc += '    )\n'
    lltre__dbvc += '    ev.finalize()\n'
    lltre__dbvc += '    return result\n'
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo, 'index_lit': qrl__ymp, 'columns_lit':
        spojd__sbl, 'values_lit': qjw__vdav, 'tracing': tracing}, xfz__aecj)
    impl = xfz__aecj['impl']
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
    mmgj__nygc = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    fph__hpqi = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (qrl__ymp, spojd__sbl, qjw__vdav, dfbq__wlkke, yfqnl__mqoi, ldl__dbqf) = (
        pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    srlqg__cik = qrl__ymp
    qrl__ymp = ColNamesMetaType(tuple(qrl__ymp))
    qjw__vdav = ColNamesMetaType(tuple(qjw__vdav))
    fef__xcte = spojd__sbl
    spojd__sbl = ColNamesMetaType((spojd__sbl,))
    lltre__dbvc = 'def impl(\n'
    lltre__dbvc += '    data,\n'
    lltre__dbvc += '    values=None,\n'
    lltre__dbvc += '    index=None,\n'
    lltre__dbvc += '    columns=None,\n'
    lltre__dbvc += '    aggfunc="mean",\n'
    lltre__dbvc += '    fill_value=None,\n'
    lltre__dbvc += '    margins=False,\n'
    lltre__dbvc += '    dropna=True,\n'
    lltre__dbvc += '    margins_name="All",\n'
    lltre__dbvc += '    observed=False,\n'
    lltre__dbvc += '    sort=True,\n'
    lltre__dbvc += '    _pivot_values=None,\n'
    lltre__dbvc += '):\n'
    lltre__dbvc += "    ev = tracing.Event('df.pivot_table')\n"
    ywg__ozbuw = dfbq__wlkke + [yfqnl__mqoi] + ldl__dbqf
    lltre__dbvc += f'    data = data.iloc[:, {ywg__ozbuw}]\n'
    yqf__wxjw = srlqg__cik + [fef__xcte]
    if not is_overload_none(_pivot_values):
        yeu__uxtb = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(yeu__uxtb)
        lltre__dbvc += '    pivot_values = _pivot_values_arr\n'
        lltre__dbvc += (
            f'    data = data[data.iloc[:, {len(dfbq__wlkke)}].isin(pivot_values)]\n'
            )
        if all(isinstance(selg__nvge, str) for selg__nvge in yeu__uxtb):
            opedm__vgc = pd.array(yeu__uxtb, 'string')
        elif all(isinstance(selg__nvge, int) for selg__nvge in yeu__uxtb):
            opedm__vgc = np.array(yeu__uxtb, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        opedm__vgc = None
    cew__scz = is_overload_constant_str(aggfunc) and get_overload_const_str(
        aggfunc) == 'nunique'
    xbnji__qyxin = len(yqf__wxjw) if cew__scz else len(srlqg__cik)
    lltre__dbvc += f"""    data = data.groupby({yqf__wxjw!r}, as_index=False, _bodo_num_shuffle_keys={xbnji__qyxin}).agg(aggfunc)
"""
    if is_overload_none(_pivot_values):
        lltre__dbvc += (
            f'    pivot_values = data.iloc[:, {len(dfbq__wlkke)}].unique()\n')
    lltre__dbvc += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    lltre__dbvc += '        (\n'
    for i in range(0, len(dfbq__wlkke)):
        lltre__dbvc += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    lltre__dbvc += '        ),\n'
    lltre__dbvc += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(dfbq__wlkke)}),),
"""
    lltre__dbvc += '        (\n'
    for i in range(len(dfbq__wlkke) + 1, len(ldl__dbqf) + len(dfbq__wlkke) + 1
        ):
        lltre__dbvc += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    lltre__dbvc += '        ),\n'
    lltre__dbvc += '        pivot_values,\n'
    lltre__dbvc += '        index_lit,\n'
    lltre__dbvc += '        columns_lit,\n'
    lltre__dbvc += '        values_lit,\n'
    lltre__dbvc += '        check_duplicates=False,\n'
    lltre__dbvc += f'        is_already_shuffled={not cew__scz},\n'
    lltre__dbvc += '        _constant_pivot_values=_constant_pivot_values,\n'
    lltre__dbvc += '    )\n'
    lltre__dbvc += '    ev.finalize()\n'
    lltre__dbvc += '    return result\n'
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo, 'numba': numba, 'index_lit': qrl__ymp,
        'columns_lit': spojd__sbl, 'values_lit': qjw__vdav,
        '_pivot_values_arr': opedm__vgc, '_constant_pivot_values':
        _pivot_values, 'tracing': tracing}, xfz__aecj)
    impl = xfz__aecj['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    mmgj__nygc = dict(col_level=col_level, ignore_index=ignore_index)
    fph__hpqi = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', mmgj__nygc, fph__hpqi,
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
    ankz__fsqu = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(ankz__fsqu, (list, tuple)):
        ankz__fsqu = [ankz__fsqu]
    for selg__nvge in ankz__fsqu:
        if selg__nvge not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {selg__nvge} not found in {frame}."
                )
    btvrw__goy = [frame.column_index[i] for i in ankz__fsqu]
    if is_overload_none(value_vars):
        fucg__xlkv = []
        dqrr__sgof = []
        for i, selg__nvge in enumerate(frame.columns):
            if i not in btvrw__goy:
                fucg__xlkv.append(i)
                dqrr__sgof.append(selg__nvge)
    else:
        dqrr__sgof = get_literal_value(value_vars)
        if not isinstance(dqrr__sgof, (list, tuple)):
            dqrr__sgof = [dqrr__sgof]
        dqrr__sgof = [v for v in dqrr__sgof if v not in ankz__fsqu]
        if not dqrr__sgof:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        fucg__xlkv = []
        for val in dqrr__sgof:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            fucg__xlkv.append(frame.column_index[val])
    for selg__nvge in dqrr__sgof:
        if selg__nvge not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {selg__nvge} not found in {frame}."
                )
    if not (all(isinstance(selg__nvge, int) for selg__nvge in dqrr__sgof) or
        all(isinstance(selg__nvge, str) for selg__nvge in dqrr__sgof)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    rjzk__aka = frame.data[fucg__xlkv[0]]
    tzuhe__fihok = [frame.data[i].dtype for i in fucg__xlkv]
    fucg__xlkv = np.array(fucg__xlkv, dtype=np.int64)
    btvrw__goy = np.array(btvrw__goy, dtype=np.int64)
    _, zifl__tsw = bodo.utils.typing.get_common_scalar_dtype(tzuhe__fihok)
    if not zifl__tsw:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': dqrr__sgof, 'val_type': rjzk__aka}
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
    if frame.is_table_format and all(v == rjzk__aka.dtype for v in tzuhe__fihok
        ):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            fucg__xlkv))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(dqrr__sgof) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {fucg__xlkv[0]})
"""
    else:
        qube__zvl = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in fucg__xlkv)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({qube__zvl},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in btvrw__goy:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(dqrr__sgof)})\n'
            )
    kycv__qgqr = ', '.join(f'out_id{i}' for i in btvrw__goy) + (', ' if len
        (btvrw__goy) > 0 else '')
    data_args = kycv__qgqr + 'var_col, val_col'
    columns = tuple(ankz__fsqu + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(dqrr__sgof)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    mmgj__nygc = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    fph__hpqi = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', mmgj__nygc, fph__hpqi,
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
    mmgj__nygc = dict(ignore_index=ignore_index, key=key)
    fph__hpqi = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', mmgj__nygc, fph__hpqi,
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
    iqb__wiwnq = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        iqb__wiwnq.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        cisev__xoat = [get_overload_const_tuple(by)]
    else:
        cisev__xoat = get_overload_const_list(by)
    cisev__xoat = set((k, '') if (k, '') in iqb__wiwnq else k for k in
        cisev__xoat)
    if len(cisev__xoat.difference(iqb__wiwnq)) > 0:
        gek__ogjpb = list(set(get_overload_const_list(by)).difference(
            iqb__wiwnq))
        raise_bodo_error(f'sort_values(): invalid keys {gek__ogjpb} for by.')
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
        yoy__sqj = get_overload_const_list(na_position)
        for na_position in yoy__sqj:
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
    mmgj__nygc = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    fph__hpqi = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', mmgj__nygc, fph__hpqi,
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
    lltre__dbvc = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    wgwk__pqkdz = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(wgwk__pqkdz))
    for i in range(wgwk__pqkdz):
        lltre__dbvc += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(lltre__dbvc, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    mmgj__nygc = dict(limit=limit, downcast=downcast)
    fph__hpqi = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', mmgj__nygc, fph__hpqi,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    ssq__vigp = not is_overload_none(value)
    uuym__rlb = not is_overload_none(method)
    if ssq__vigp and uuym__rlb:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not ssq__vigp and not uuym__rlb:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if ssq__vigp:
        nuggo__ljwnr = 'value=value'
    else:
        nuggo__ljwnr = 'method=method'
    data_args = [(
        f"df['{selg__nvge}'].fillna({nuggo__ljwnr}, inplace=inplace)" if
        isinstance(selg__nvge, str) else
        f'df[{selg__nvge}].fillna({nuggo__ljwnr}, inplace=inplace)') for
        selg__nvge in df.columns]
    lltre__dbvc = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        lltre__dbvc += '  ' + '  \n'.join(data_args) + '\n'
        xfz__aecj = {}
        exec(lltre__dbvc, {}, xfz__aecj)
        impl = xfz__aecj['impl']
        return impl
    else:
        return _gen_init_df(lltre__dbvc, df.columns, ', '.join(vafg__rzihu +
            '.values' for vafg__rzihu in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    mmgj__nygc = dict(col_level=col_level, col_fill=col_fill)
    fph__hpqi = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', mmgj__nygc, fph__hpqi,
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
    lltre__dbvc = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    lltre__dbvc += (
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
        qdfht__otwl = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            qdfht__otwl)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            lltre__dbvc += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            tiugx__kwyr = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = tiugx__kwyr + data_args
        else:
            ipga__jqki = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [ipga__jqki] + data_args
    return _gen_init_df(lltre__dbvc, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    vep__mjf = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and vep__mjf == 1 or is_overload_constant_list(level) and list(
        get_overload_const_list(level)) == list(range(vep__mjf))


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
        qqm__avjms = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        mljv__ilng = get_overload_const_list(subset)
        qqm__avjms = []
        for cdyn__yokj in mljv__ilng:
            if cdyn__yokj not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{cdyn__yokj}' not in data frame columns {df}"
                    )
            qqm__avjms.append(df.column_index[cdyn__yokj])
    wgwk__pqkdz = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(wgwk__pqkdz))
    lltre__dbvc = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(wgwk__pqkdz):
        lltre__dbvc += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    lltre__dbvc += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in qqm__avjms)))
    lltre__dbvc += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(lltre__dbvc, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    mmgj__nygc = dict(index=index, level=level, errors=errors)
    fph__hpqi = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', mmgj__nygc, fph__hpqi,
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
            wtuu__ladlr = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            wtuu__ladlr = get_overload_const_list(labels)
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
            wtuu__ladlr = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            wtuu__ladlr = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for selg__nvge in wtuu__ladlr:
        if selg__nvge not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(selg__nvge, df.columns))
    if len(set(wtuu__ladlr)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    qus__bjtlh = tuple(selg__nvge for selg__nvge in df.columns if 
        selg__nvge not in wtuu__ladlr)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[selg__nvge], '.copy()' if not inplace else
        '') for selg__nvge in qus__bjtlh)
    lltre__dbvc = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    lltre__dbvc += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(lltre__dbvc, qus__bjtlh, data_args, index)


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
    mmgj__nygc = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    bzfh__urj = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', mmgj__nygc, bzfh__urj,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    wgwk__pqkdz = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(wgwk__pqkdz))
    xtble__vbuxp = ', '.join('rhs_data_{}'.format(i) for i in range(
        wgwk__pqkdz))
    lltre__dbvc = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    lltre__dbvc += '  if (frac == 1 or n == len(df)) and not replace:\n'
    lltre__dbvc += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(wgwk__pqkdz):
        lltre__dbvc += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    lltre__dbvc += '  if frac is None:\n'
    lltre__dbvc += '    frac_d = -1.0\n'
    lltre__dbvc += '  else:\n'
    lltre__dbvc += '    frac_d = frac\n'
    lltre__dbvc += '  if n is None:\n'
    lltre__dbvc += '    n_i = 0\n'
    lltre__dbvc += '  else:\n'
    lltre__dbvc += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    lltre__dbvc += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({xtble__vbuxp},), {index}, n_i, frac_d, replace)
"""
    lltre__dbvc += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(lltre__dbvc, df.
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
    kajif__qtweh = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    ttfg__zrq = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', kajif__qtweh, ttfg__zrq,
        package_name='pandas', module_name='DataFrame')
    zyyrb__tca = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            ukzqd__jdjn = zyyrb__tca + '\n'
            ukzqd__jdjn += 'Index: 0 entries\n'
            ukzqd__jdjn += 'Empty DataFrame'
            print(ukzqd__jdjn)
        return _info_impl
    else:
        lltre__dbvc = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        lltre__dbvc += '    ncols = df.shape[1]\n'
        lltre__dbvc += f'    lines = "{zyyrb__tca}\\n"\n'
        lltre__dbvc += f'    lines += "{df.index}: "\n'
        lltre__dbvc += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            lltre__dbvc += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            lltre__dbvc += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            lltre__dbvc += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        lltre__dbvc += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        lltre__dbvc += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        lltre__dbvc += '    column_width = max(space, 7)\n'
        lltre__dbvc += '    column= "Column"\n'
        lltre__dbvc += '    underl= "------"\n'
        lltre__dbvc += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        lltre__dbvc += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        lltre__dbvc += '    mem_size = 0\n'
        lltre__dbvc += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        lltre__dbvc += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        lltre__dbvc += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        rww__ymiaz = dict()
        for i in range(len(df.columns)):
            lltre__dbvc += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            vycg__ozs = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                vycg__ozs = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                gjcnz__maa = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                vycg__ozs = f'{gjcnz__maa[:-7]}'
            lltre__dbvc += f'    col_dtype[{i}] = "{vycg__ozs}"\n'
            if vycg__ozs in rww__ymiaz:
                rww__ymiaz[vycg__ozs] += 1
            else:
                rww__ymiaz[vycg__ozs] = 1
            lltre__dbvc += f'    col_name[{i}] = "{df.columns[i]}"\n'
            lltre__dbvc += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        lltre__dbvc += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        lltre__dbvc += '    for i in column_info:\n'
        lltre__dbvc += "        lines += f'{i}\\n'\n"
        ailsp__dph = ', '.join(f'{k}({rww__ymiaz[k]})' for k in sorted(
            rww__ymiaz))
        lltre__dbvc += f"    lines += 'dtypes: {ailsp__dph}\\n'\n"
        lltre__dbvc += '    mem_size += df.index.nbytes\n'
        lltre__dbvc += '    total_size = _sizeof_fmt(mem_size)\n'
        lltre__dbvc += "    lines += f'memory usage: {total_size}'\n"
        lltre__dbvc += '    print(lines)\n'
        xfz__aecj = {}
        exec(lltre__dbvc, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, xfz__aecj)
        _info_impl = xfz__aecj['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    lltre__dbvc = 'def impl(df, index=True, deep=False):\n'
    ayra__feeo = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    aczxg__yyxvu = is_overload_true(index)
    columns = df.columns
    if aczxg__yyxvu:
        columns = ('Index',) + columns
    if len(columns) == 0:
        wjvp__nmw = ()
    elif all(isinstance(selg__nvge, int) for selg__nvge in columns):
        wjvp__nmw = np.array(columns, 'int64')
    elif all(isinstance(selg__nvge, str) for selg__nvge in columns):
        wjvp__nmw = pd.array(columns, 'string')
    else:
        wjvp__nmw = columns
    if df.is_table_format and len(df.columns) > 0:
        xom__gnkvh = int(aczxg__yyxvu)
        gwt__zmhj = len(columns)
        lltre__dbvc += f'  nbytes_arr = np.empty({gwt__zmhj}, np.int64)\n'
        lltre__dbvc += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        lltre__dbvc += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {xom__gnkvh})
"""
        if aczxg__yyxvu:
            lltre__dbvc += f'  nbytes_arr[0] = {ayra__feeo}\n'
        lltre__dbvc += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if aczxg__yyxvu:
            data = f'{ayra__feeo},{data}'
        else:
            ygtr__foa = ',' if len(columns) == 1 else ''
            data = f'{data}{ygtr__foa}'
        lltre__dbvc += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        wjvp__nmw}, xfz__aecj)
    impl = xfz__aecj['impl']
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
    axzmu__ogp = 'read_excel_df{}'.format(next_label())
    setattr(types, axzmu__ogp, df_type)
    zmk__zsuqk = False
    if is_overload_constant_list(parse_dates):
        zmk__zsuqk = get_overload_const_list(parse_dates)
    tpmq__bjhlb = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    lltre__dbvc = f"""
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
    with numba.objmode(df="{axzmu__ogp}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{tpmq__bjhlb}}},
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
            parse_dates={zmk__zsuqk},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    xfz__aecj = {}
    exec(lltre__dbvc, globals(), xfz__aecj)
    impl = xfz__aecj['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as vev__sofb:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    lltre__dbvc = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    lltre__dbvc += (
        '    ylabel=None, title=None, legend=True, fontsize=None, \n')
    lltre__dbvc += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        lltre__dbvc += '   fig, ax = plt.subplots()\n'
    else:
        lltre__dbvc += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        lltre__dbvc += '   fig.set_figwidth(figsize[0])\n'
        lltre__dbvc += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        lltre__dbvc += '   xlabel = x\n'
    lltre__dbvc += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        lltre__dbvc += '   ylabel = y\n'
    else:
        lltre__dbvc += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        lltre__dbvc += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        lltre__dbvc += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    lltre__dbvc += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            lltre__dbvc += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            nmyg__mmfu = get_overload_const_str(x)
            cqu__jklp = df.columns.index(nmyg__mmfu)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if cqu__jklp != i:
                        lltre__dbvc += f"""   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])
"""
        else:
            lltre__dbvc += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        lltre__dbvc += '   ax.scatter(df[x], df[y], s=20)\n'
        lltre__dbvc += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        lltre__dbvc += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        lltre__dbvc += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        lltre__dbvc += '   ax.legend()\n'
    lltre__dbvc += '   return ax\n'
    xfz__aecj = {}
    exec(lltre__dbvc, {'bodo': bodo, 'plt': plt}, xfz__aecj)
    impl = xfz__aecj['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for oidn__vuud in df_typ.data:
        if not (isinstance(oidn__vuud, IntegerArrayType) or isinstance(
            oidn__vuud.dtype, types.Number) or oidn__vuud.dtype in (bodo.
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
        cctx__pabks = args[0]
        mhel__qrbu = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        oha__ygy = cctx__pabks
        check_runtime_cols_unsupported(cctx__pabks, 'set_df_col()')
        if isinstance(cctx__pabks, DataFrameType):
            index = cctx__pabks.index
            if len(cctx__pabks.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(cctx__pabks.columns) == 0:
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
            if mhel__qrbu in cctx__pabks.columns:
                qus__bjtlh = cctx__pabks.columns
                jtjp__afhz = cctx__pabks.columns.index(mhel__qrbu)
                kim__cbygh = list(cctx__pabks.data)
                kim__cbygh[jtjp__afhz] = val
                kim__cbygh = tuple(kim__cbygh)
            else:
                qus__bjtlh = cctx__pabks.columns + (mhel__qrbu,)
                kim__cbygh = cctx__pabks.data + (val,)
            oha__ygy = DataFrameType(kim__cbygh, index, qus__bjtlh,
                cctx__pabks.dist, cctx__pabks.is_table_format)
        return oha__ygy(*args)


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
        vpgrl__ihv = args[0]
        assert isinstance(vpgrl__ihv, DataFrameType) and len(vpgrl__ihv.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        xoz__udhhk = args[2]
        assert len(col_names_to_replace) == len(xoz__udhhk
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(vpgrl__ihv.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in vpgrl__ihv.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(vpgrl__ihv,
            '__bodosql_replace_columns_dummy()')
        index = vpgrl__ihv.index
        qus__bjtlh = vpgrl__ihv.columns
        kim__cbygh = list(vpgrl__ihv.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            ydhp__pkh = xoz__udhhk[i]
            assert isinstance(ydhp__pkh, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(ydhp__pkh, SeriesType):
                ydhp__pkh = ydhp__pkh.data
            tglx__nkzr = vpgrl__ihv.column_index[col_name]
            kim__cbygh[tglx__nkzr] = ydhp__pkh
        kim__cbygh = tuple(kim__cbygh)
        oha__ygy = DataFrameType(kim__cbygh, index, qus__bjtlh, vpgrl__ihv.
            dist, vpgrl__ihv.is_table_format)
        return oha__ygy(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    titcq__ptpvo = {}

    def _rewrite_membership_op(self, node, left, right):
        mmmuq__aqmk = node.op
        op = self.visit(mmmuq__aqmk)
        return op, mmmuq__aqmk, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    qncg__jsxm = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in qncg__jsxm:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in qncg__jsxm:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        esod__odxbv = node.attr
        value = node.value
        dvpia__ezuwc = pd.core.computation.ops.LOCAL_TAG
        if esod__odxbv in ('str', 'dt'):
            try:
                oycqs__ysc = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as mgms__gjrc:
                col_name = mgms__gjrc.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            oycqs__ysc = str(self.visit(value))
        urggr__bxvyk = oycqs__ysc, esod__odxbv
        if urggr__bxvyk in join_cleaned_cols:
            esod__odxbv = join_cleaned_cols[urggr__bxvyk]
        name = oycqs__ysc + '.' + esod__odxbv
        if name.startswith(dvpia__ezuwc):
            name = name[len(dvpia__ezuwc):]
        if esod__odxbv in ('str', 'dt'):
            hofxe__sznq = columns[cleaned_columns.index(oycqs__ysc)]
            titcq__ptpvo[hofxe__sznq] = oycqs__ysc
            self.env.scope[name] = 0
            return self.term_type(dvpia__ezuwc + name, self.env)
        qncg__jsxm.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in qncg__jsxm:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        otc__tsb = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        mhel__qrbu = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(otc__tsb), mhel__qrbu))

    def op__str__(self):
        fxfj__htdej = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            qeo__bjn)) for qeo__bjn in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(fxfj__htdej)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(fxfj__htdej)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(fxfj__htdej))
    huhdc__tyh = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    bpa__vvn = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    buf__qwzh = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    onerh__weuo = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    hozlh__gsut = pd.core.computation.ops.Term.__str__
    qfbcg__jnrq = pd.core.computation.ops.MathCall.__str__
    odx__kjf = pd.core.computation.ops.Op.__str__
    ncjs__mpdi = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        zbxxm__bki = pd.core.computation.expr.Expr(expr, env=env)
        edhc__hdxxb = str(zbxxm__bki)
    except pd.core.computation.ops.UndefinedVariableError as mgms__gjrc:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == mgms__gjrc.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {mgms__gjrc}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            huhdc__tyh)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            bpa__vvn)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = buf__qwzh
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = onerh__weuo
        pd.core.computation.ops.Term.__str__ = hozlh__gsut
        pd.core.computation.ops.MathCall.__str__ = qfbcg__jnrq
        pd.core.computation.ops.Op.__str__ = odx__kjf
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            ncjs__mpdi)
    jtz__fzwdx = pd.core.computation.parsing.clean_column_name
    titcq__ptpvo.update({selg__nvge: jtz__fzwdx(selg__nvge) for selg__nvge in
        columns if jtz__fzwdx(selg__nvge) in zbxxm__bki.names})
    return zbxxm__bki, edhc__hdxxb, titcq__ptpvo


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        yjsgf__dai = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(yjsgf__dai))
        asmb__imy = namedtuple('Pandas', col_names)
        tbahd__nat = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], asmb__imy)
        super(DataFrameTupleIterator, self).__init__(name, tbahd__nat)

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
        ekvh__cune = [if_series_to_array_type(a) for a in args[len(args) // 2:]
            ]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        ekvh__cune = [types.Array(types.int64, 1, 'C')] + ekvh__cune
        xbpr__rmzzl = DataFrameTupleIterator(col_names, ekvh__cune)
        return xbpr__rmzzl(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kzs__pkpe = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            kzs__pkpe)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    jakf__jtliy = args[len(args) // 2:]
    ovw__bebpv = sig.args[len(sig.args) // 2:]
    rcwh__ketxd = context.make_helper(builder, sig.return_type)
    dgq__thhzw = context.get_constant(types.intp, 0)
    wks__kke = cgutils.alloca_once_value(builder, dgq__thhzw)
    rcwh__ketxd.index = wks__kke
    for i, arr in enumerate(jakf__jtliy):
        setattr(rcwh__ketxd, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(jakf__jtliy, ovw__bebpv):
        context.nrt.incref(builder, arr_typ, arr)
    res = rcwh__ketxd._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    tqyjm__hjxry, = sig.args
    htrh__silvf, = args
    rcwh__ketxd = context.make_helper(builder, tqyjm__hjxry, value=htrh__silvf)
    ztxdi__bjz = signature(types.intp, tqyjm__hjxry.array_types[1])
    dwo__nfsw = context.compile_internal(builder, lambda a: len(a),
        ztxdi__bjz, [rcwh__ketxd.array0])
    index = builder.load(rcwh__ketxd.index)
    azteb__alxfi = builder.icmp_signed('<', index, dwo__nfsw)
    result.set_valid(azteb__alxfi)
    with builder.if_then(azteb__alxfi):
        values = [index]
        for i, arr_typ in enumerate(tqyjm__hjxry.array_types[1:]):
            lziwc__xgct = getattr(rcwh__ketxd, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                rpc__iyju = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    rpc__iyju, [lziwc__xgct, index])
            else:
                rpc__iyju = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    rpc__iyju, [lziwc__xgct, index])
            values.append(val)
        value = context.make_tuple(builder, tqyjm__hjxry.yield_type, values)
        result.yield_(value)
        vei__dtv = cgutils.increment_index(builder, index)
        builder.store(vei__dtv, rcwh__ketxd.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    nxxhe__rxnn = ir.Assign(rhs, lhs, expr.loc)
    kxo__hqmjf = lhs
    ywea__vcno = []
    etv__lunoq = []
    nqjj__fqoo = typ.count
    for i in range(nqjj__fqoo):
        qcjf__cbzyq = ir.Var(kxo__hqmjf.scope, mk_unique_var('{}_size{}'.
            format(kxo__hqmjf.name, i)), kxo__hqmjf.loc)
        qfgt__gelhk = ir.Expr.static_getitem(lhs, i, None, kxo__hqmjf.loc)
        self.calltypes[qfgt__gelhk] = None
        ywea__vcno.append(ir.Assign(qfgt__gelhk, qcjf__cbzyq, kxo__hqmjf.loc))
        self._define(equiv_set, qcjf__cbzyq, types.intp, qfgt__gelhk)
        etv__lunoq.append(qcjf__cbzyq)
    tybrl__cfpl = tuple(etv__lunoq)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        tybrl__cfpl, pre=[nxxhe__rxnn] + ywea__vcno)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
