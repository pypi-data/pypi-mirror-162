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
        awnk__jiuux = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({awnk__jiuux})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    wfv__gduo = 'def impl(df):\n'
    if df.has_runtime_cols:
        wfv__gduo += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        fot__kulk = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        wfv__gduo += f'  return {fot__kulk}'
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo}, kpz__lmilc)
    impl = kpz__lmilc['impl']
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
    zxrv__ita = len(df.columns)
    ndp__hfouf = set(i for i in range(zxrv__ita) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in ndp__hfouf else '') for i in
        range(zxrv__ita))
    wfv__gduo = 'def f(df):\n'.format()
    wfv__gduo += '    return np.stack(({},), 1)\n'.format(data_args)
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo, 'np': np}, kpz__lmilc)
    iuo__yyb = kpz__lmilc['f']
    return iuo__yyb


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
    wdi__eufgy = {'dtype': dtype, 'na_value': na_value}
    xbex__bxmx = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', wdi__eufgy, xbex__bxmx,
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
            bfy__rxj = bodo.hiframes.table.compute_num_runtime_columns(t)
            return bfy__rxj * len(t)
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
            bfy__rxj = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), bfy__rxj
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    wfv__gduo = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    dgt__cgpuw = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    wfv__gduo += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{dgt__cgpuw}), {index}, None)
"""
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo}, kpz__lmilc)
    impl = kpz__lmilc['impl']
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
    wdi__eufgy = {'copy': copy, 'errors': errors}
    xbex__bxmx = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', wdi__eufgy, xbex__bxmx,
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
        mylqr__vis = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        gevl__oer = _bodo_object_typeref.instance_type
        assert isinstance(gevl__oer, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in gevl__oer.column_index:
                    idx = gevl__oer.column_index[name]
                    arr_typ = gevl__oer.data[idx]
                else:
                    arr_typ = df.data[i]
                mylqr__vis.append(arr_typ)
        else:
            extra_globals = {}
            sqr__wstj = {}
            for i, name in enumerate(gevl__oer.columns):
                arr_typ = gevl__oer.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    tgn__gaa = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    tgn__gaa = boolean_dtype
                else:
                    tgn__gaa = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = tgn__gaa
                sqr__wstj[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {sqr__wstj[bits__qai]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if bits__qai in sqr__wstj else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, bits__qai in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        odkag__kubb = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            odkag__kubb = {name: dtype_to_array_type(parse_dtype(dtype)) for
                name, dtype in odkag__kubb.items()}
            for i, name in enumerate(df.columns):
                if name in odkag__kubb:
                    arr_typ = odkag__kubb[name]
                else:
                    arr_typ = df.data[i]
                mylqr__vis.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(odkag__kubb[bits__qai])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if bits__qai in odkag__kubb else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, bits__qai in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        mylqr__vis = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        quk__xycc = bodo.TableType(tuple(mylqr__vis))
        extra_globals['out_table_typ'] = quk__xycc
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
        xyi__qwm = types.none
        extra_globals = {'output_arr_typ': xyi__qwm}
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
        nued__iue = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                nued__iue.append(arr + '.copy()')
            elif is_overload_false(deep):
                nued__iue.append(arr)
            else:
                nued__iue.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(nued__iue)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    wdi__eufgy = {'index': index, 'level': level, 'errors': errors}
    xbex__bxmx = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', wdi__eufgy, xbex__bxmx,
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
        ajcsm__oito = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        ajcsm__oito = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    aqqk__rjofv = tuple([ajcsm__oito.get(df.columns[i], df.columns[i]) for
        i in range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    exhxi__rayst = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        exhxi__rayst = df.copy(columns=aqqk__rjofv)
        xyi__qwm = types.none
        extra_globals = {'output_arr_typ': xyi__qwm}
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
        nued__iue = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                nued__iue.append(arr + '.copy()')
            elif is_overload_false(copy):
                nued__iue.append(arr)
            else:
                nued__iue.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(nued__iue)
    return _gen_init_df(header, aqqk__rjofv, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    vgnr__vit = not is_overload_none(items)
    ugwlv__jqpew = not is_overload_none(like)
    ilag__jhjh = not is_overload_none(regex)
    vbh__vdp = vgnr__vit ^ ugwlv__jqpew ^ ilag__jhjh
    uwihp__ayg = not (vgnr__vit or ugwlv__jqpew or ilag__jhjh)
    if uwihp__ayg:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not vbh__vdp:
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
        yff__gllb = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        yff__gllb = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert yff__gllb in {0, 1}
    wfv__gduo = 'def impl(df, items=None, like=None, regex=None, axis=None):\n'
    if yff__gllb == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if yff__gllb == 1:
        pgztg__ienup = []
        lgbvs__oedwz = []
        uza__mxmp = []
        if vgnr__vit:
            if is_overload_constant_list(items):
                rahxo__oukga = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if ugwlv__jqpew:
            if is_overload_constant_str(like):
                usc__cpeyx = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if ilag__jhjh:
            if is_overload_constant_str(regex):
                kqo__frgi = get_overload_const_str(regex)
                iekez__pijez = re.compile(kqo__frgi)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, bits__qai in enumerate(df.columns):
            if not is_overload_none(items
                ) and bits__qai in rahxo__oukga or not is_overload_none(like
                ) and usc__cpeyx in str(bits__qai) or not is_overload_none(
                regex) and iekez__pijez.search(str(bits__qai)):
                lgbvs__oedwz.append(bits__qai)
                uza__mxmp.append(i)
        for i in uza__mxmp:
            var_name = f'data_{i}'
            pgztg__ienup.append(var_name)
            wfv__gduo += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(pgztg__ienup)
        return _gen_init_df(wfv__gduo, lgbvs__oedwz, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    exhxi__rayst = None
    if df.is_table_format:
        xyi__qwm = types.Array(types.bool_, 1, 'C')
        exhxi__rayst = DataFrameType(tuple([xyi__qwm] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': xyi__qwm}
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
    zdo__dbc = is_overload_none(include)
    lpwb__rwsg = is_overload_none(exclude)
    axacf__nqq = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if zdo__dbc and lpwb__rwsg:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not zdo__dbc:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            ano__lgwke = [dtype_to_array_type(parse_dtype(elem, axacf__nqq)
                ) for elem in include]
        elif is_legal_input(include):
            ano__lgwke = [dtype_to_array_type(parse_dtype(include, axacf__nqq))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        ano__lgwke = get_nullable_and_non_nullable_types(ano__lgwke)
        gnfax__mlllu = tuple(bits__qai for i, bits__qai in enumerate(df.
            columns) if df.data[i] in ano__lgwke)
    else:
        gnfax__mlllu = df.columns
    if not lpwb__rwsg:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            ydoc__mlpm = [dtype_to_array_type(parse_dtype(elem, axacf__nqq)
                ) for elem in exclude]
        elif is_legal_input(exclude):
            ydoc__mlpm = [dtype_to_array_type(parse_dtype(exclude, axacf__nqq))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        ydoc__mlpm = get_nullable_and_non_nullable_types(ydoc__mlpm)
        gnfax__mlllu = tuple(bits__qai for bits__qai in gnfax__mlllu if df.
            data[df.column_index[bits__qai]] not in ydoc__mlpm)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[bits__qai]})'
         for bits__qai in gnfax__mlllu)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, gnfax__mlllu, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    exhxi__rayst = None
    if df.is_table_format:
        xyi__qwm = types.Array(types.bool_, 1, 'C')
        exhxi__rayst = DataFrameType(tuple([xyi__qwm] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': xyi__qwm}
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
    lbcv__cnpbs = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in lbcv__cnpbs:
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
    lbcv__cnpbs = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in lbcv__cnpbs:
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
    wfv__gduo = 'def impl(df, values):\n'
    azm__hzy = {}
    xisq__phor = False
    if isinstance(values, DataFrameType):
        xisq__phor = True
        for i, bits__qai in enumerate(df.columns):
            if bits__qai in values.column_index:
                ktlrh__ijfd = 'val{}'.format(i)
                wfv__gduo += f"""  {ktlrh__ijfd} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[bits__qai]})
"""
                azm__hzy[bits__qai] = ktlrh__ijfd
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        azm__hzy = {bits__qai: 'values' for bits__qai in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        ktlrh__ijfd = 'data{}'.format(i)
        wfv__gduo += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(ktlrh__ijfd, i))
        data.append(ktlrh__ijfd)
    rlgax__vvr = ['out{}'.format(i) for i in range(len(df.columns))]
    xks__xfeba = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    njj__kqzf = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    dene__aepna = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, cupks__jjnrk) in enumerate(zip(df.columns, data)):
        if cname in azm__hzy:
            ibwbp__qiy = azm__hzy[cname]
            if xisq__phor:
                wfv__gduo += xks__xfeba.format(cupks__jjnrk, ibwbp__qiy,
                    rlgax__vvr[i])
            else:
                wfv__gduo += njj__kqzf.format(cupks__jjnrk, ibwbp__qiy,
                    rlgax__vvr[i])
        else:
            wfv__gduo += dene__aepna.format(rlgax__vvr[i])
    return _gen_init_df(wfv__gduo, df.columns, ','.join(rlgax__vvr))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    zxrv__ita = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(zxrv__ita))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    csf__sssyg = [bits__qai for bits__qai, mawml__hasjg in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(mawml__hasjg
        .dtype)]
    assert len(csf__sssyg) != 0
    koxtm__eadqz = ''
    if not any(mawml__hasjg == types.float64 for mawml__hasjg in df.data):
        koxtm__eadqz = '.astype(np.float64)'
    euu__wxdbx = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[bits__qai], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[bits__qai]], IntegerArrayType) or
        df.data[df.column_index[bits__qai]] == boolean_array else '') for
        bits__qai in csf__sssyg)
    ciy__lqmn = 'np.stack(({},), 1){}'.format(euu__wxdbx, koxtm__eadqz)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(csf__sssyg))
        )
    index = f'{generate_col_to_index_func_text(csf__sssyg)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(ciy__lqmn)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, csf__sssyg, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    mfmhd__vhtys = dict(ddof=ddof)
    fos__nta = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    gbre__xjny = '1' if is_overload_none(min_periods) else 'min_periods'
    csf__sssyg = [bits__qai for bits__qai, mawml__hasjg in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(mawml__hasjg
        .dtype)]
    if len(csf__sssyg) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    koxtm__eadqz = ''
    if not any(mawml__hasjg == types.float64 for mawml__hasjg in df.data):
        koxtm__eadqz = '.astype(np.float64)'
    euu__wxdbx = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[bits__qai], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[bits__qai]], IntegerArrayType) or
        df.data[df.column_index[bits__qai]] == boolean_array else '') for
        bits__qai in csf__sssyg)
    ciy__lqmn = 'np.stack(({},), 1){}'.format(euu__wxdbx, koxtm__eadqz)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(csf__sssyg))
        )
    index = f'pd.Index({csf__sssyg})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(ciy__lqmn)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        gbre__xjny)
    return _gen_init_df(header, csf__sssyg, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    mfmhd__vhtys = dict(axis=axis, level=level, numeric_only=numeric_only)
    fos__nta = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    wfv__gduo = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    wfv__gduo += '  data = np.array([{}])\n'.format(data_args)
    fot__kulk = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    wfv__gduo += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {fot__kulk})\n'
        )
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo, 'np': np}, kpz__lmilc)
    impl = kpz__lmilc['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    mfmhd__vhtys = dict(axis=axis)
    fos__nta = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    wfv__gduo = 'def impl(df, axis=0, dropna=True):\n'
    wfv__gduo += '  data = np.asarray(({},))\n'.format(data_args)
    fot__kulk = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    wfv__gduo += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {fot__kulk})\n'
        )
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo, 'np': np}, kpz__lmilc)
    impl = kpz__lmilc['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    mfmhd__vhtys = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    fos__nta = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    mfmhd__vhtys = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    fos__nta = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    mfmhd__vhtys = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fos__nta = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    mfmhd__vhtys = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fos__nta = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    mfmhd__vhtys = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fos__nta = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    mfmhd__vhtys = dict(skipna=skipna, level=level, ddof=ddof, numeric_only
        =numeric_only)
    fos__nta = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    mfmhd__vhtys = dict(skipna=skipna, level=level, ddof=ddof, numeric_only
        =numeric_only)
    fos__nta = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    mfmhd__vhtys = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fos__nta = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    mfmhd__vhtys = dict(numeric_only=numeric_only, interpolation=interpolation)
    fos__nta = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    mfmhd__vhtys = dict(axis=axis, skipna=skipna)
    fos__nta = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for iguv__uufzs in df.data:
        if not (bodo.utils.utils.is_np_array_typ(iguv__uufzs) and (
            iguv__uufzs.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(iguv__uufzs.dtype, (types.Number, types.Boolean))) or
            isinstance(iguv__uufzs, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or iguv__uufzs in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {iguv__uufzs} not supported.'
                )
        if isinstance(iguv__uufzs, bodo.CategoricalArrayType
            ) and not iguv__uufzs.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    mfmhd__vhtys = dict(axis=axis, skipna=skipna)
    fos__nta = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for iguv__uufzs in df.data:
        if not (bodo.utils.utils.is_np_array_typ(iguv__uufzs) and (
            iguv__uufzs.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(iguv__uufzs.dtype, (types.Number, types.Boolean))) or
            isinstance(iguv__uufzs, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or iguv__uufzs in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {iguv__uufzs} not supported.'
                )
        if isinstance(iguv__uufzs, bodo.CategoricalArrayType
            ) and not iguv__uufzs.dtype.ordered:
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
        csf__sssyg = tuple(bits__qai for bits__qai, mawml__hasjg in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (mawml__hasjg.dtype))
        out_colnames = csf__sssyg
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            zlbp__xsyto = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[bits__qai]].dtype) for bits__qai in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(zlbp__xsyto, []))
    except NotImplementedError as zqcc__joas:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    yroh__uxv = ''
    if func_name in ('sum', 'prod'):
        yroh__uxv = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    wfv__gduo = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, yroh__uxv))
    if func_name == 'quantile':
        wfv__gduo = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        wfv__gduo = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        wfv__gduo += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        wfv__gduo += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        kpz__lmilc)
    impl = kpz__lmilc['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    xss__cjfqa = ''
    if func_name in ('min', 'max'):
        xss__cjfqa = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        xss__cjfqa = ', dtype=np.float32'
    cquf__uyiji = f'bodo.libs.array_ops.array_op_{func_name}'
    ridmj__acpfq = ''
    if func_name in ['sum', 'prod']:
        ridmj__acpfq = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        ridmj__acpfq = 'index'
    elif func_name == 'quantile':
        ridmj__acpfq = 'q'
    elif func_name in ['std', 'var']:
        ridmj__acpfq = 'True, ddof'
    elif func_name == 'median':
        ridmj__acpfq = 'True'
    data_args = ', '.join(
        f'{cquf__uyiji}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[bits__qai]}), {ridmj__acpfq})'
         for bits__qai in out_colnames)
    wfv__gduo = ''
    if func_name in ('idxmax', 'idxmin'):
        wfv__gduo += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        wfv__gduo += ('  data = bodo.utils.conversion.coerce_to_array(({},))\n'
            .format(data_args))
    else:
        wfv__gduo += '  data = np.asarray(({},){})\n'.format(data_args,
            xss__cjfqa)
    wfv__gduo += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return wfv__gduo


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    yaxsn__zva = [df_type.column_index[bits__qai] for bits__qai in out_colnames
        ]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in yaxsn__zva)
    anjfj__ttxn = '\n        '.join(f'row[{i}] = arr_{yaxsn__zva[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    bgu__bcidm = f'len(arr_{yaxsn__zva[0]})'
    zkur__abqde = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in zkur__abqde:
        pmth__vbtrx = zkur__abqde[func_name]
        kbkni__owo = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        wfv__gduo = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {bgu__bcidm}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{kbkni__owo})
    for i in numba.parfors.parfor.internal_prange(n):
        {anjfj__ttxn}
        A[i] = {pmth__vbtrx}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return wfv__gduo
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    mfmhd__vhtys = dict(fill_method=fill_method, limit=limit, freq=freq)
    fos__nta = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', mfmhd__vhtys, fos__nta,
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
    mfmhd__vhtys = dict(axis=axis, skipna=skipna)
    fos__nta = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', mfmhd__vhtys, fos__nta,
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
    mfmhd__vhtys = dict(skipna=skipna)
    fos__nta = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', mfmhd__vhtys, fos__nta,
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
    mfmhd__vhtys = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    fos__nta = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    csf__sssyg = [bits__qai for bits__qai, mawml__hasjg in zip(df.columns,
        df.data) if _is_describe_type(mawml__hasjg)]
    if len(csf__sssyg) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    lbh__ncj = sum(df.data[df.column_index[bits__qai]].dtype == bodo.
        datetime64ns for bits__qai in csf__sssyg)

    def _get_describe(col_ind):
        xxni__lww = df.data[col_ind].dtype == bodo.datetime64ns
        if lbh__ncj and lbh__ncj != len(csf__sssyg):
            if xxni__lww:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for bits__qai in csf__sssyg:
        col_ind = df.column_index[bits__qai]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[bits__qai]) for
        bits__qai in csf__sssyg)
    jbtvz__dni = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if lbh__ncj == len(csf__sssyg):
        jbtvz__dni = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif lbh__ncj:
        jbtvz__dni = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({jbtvz__dni})'
    return _gen_init_df(header, csf__sssyg, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    mfmhd__vhtys = dict(axis=axis, convert=convert, is_copy=is_copy)
    fos__nta = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', mfmhd__vhtys, fos__nta,
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
    mfmhd__vhtys = dict(freq=freq, axis=axis, fill_value=fill_value)
    fos__nta = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for uhoc__dmrk in df.data:
        if not is_supported_shift_array_type(uhoc__dmrk):
            raise BodoError(
                f'Dataframe.shift() column input type {uhoc__dmrk.dtype} not supported yet.'
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
    mfmhd__vhtys = dict(axis=axis)
    fos__nta = dict(axis=0)
    check_unsupported_args('DataFrame.diff', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for uhoc__dmrk in df.data:
        if not (isinstance(uhoc__dmrk, types.Array) and (isinstance(
            uhoc__dmrk.dtype, types.Number) or uhoc__dmrk.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {uhoc__dmrk.dtype} not supported.'
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
    dlzkl__ngpfo = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(dlzkl__ngpfo)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        spn__cma = get_overload_const_list(column)
    else:
        spn__cma = [get_literal_value(column)]
    nulrv__zcl = [df.column_index[bits__qai] for bits__qai in spn__cma]
    for i in nulrv__zcl:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{nulrv__zcl[0]})\n'
        )
    for i in range(n):
        if i in nulrv__zcl:
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
    wdi__eufgy = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    xbex__bxmx = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', wdi__eufgy, xbex__bxmx,
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
    columns = tuple(bits__qai for bits__qai in df.columns if bits__qai !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    wdi__eufgy = {'inplace': inplace}
    xbex__bxmx = {'inplace': False}
    check_unsupported_args('query', wdi__eufgy, xbex__bxmx, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        akh__makum = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[akh__makum]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    wdi__eufgy = {'subset': subset, 'keep': keep}
    xbex__bxmx = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', wdi__eufgy, xbex__bxmx,
        package_name='pandas', module_name='DataFrame')
    zxrv__ita = len(df.columns)
    wfv__gduo = "def impl(df, subset=None, keep='first'):\n"
    for i in range(zxrv__ita):
        wfv__gduo += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    rvohy__yyxsk = ', '.join(f'data_{i}' for i in range(zxrv__ita))
    rvohy__yyxsk += ',' if zxrv__ita == 1 else ''
    wfv__gduo += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({rvohy__yyxsk}))\n'
        )
    wfv__gduo += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    wfv__gduo += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo}, kpz__lmilc)
    impl = kpz__lmilc['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    wdi__eufgy = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    xbex__bxmx = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    baef__tfy = []
    if is_overload_constant_list(subset):
        baef__tfy = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        baef__tfy = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        baef__tfy = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    uzg__blpat = []
    for col_name in baef__tfy:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        uzg__blpat.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', wdi__eufgy,
        xbex__bxmx, package_name='pandas', module_name='DataFrame')
    fcg__ntld = []
    if uzg__blpat:
        for gvj__bpwqj in uzg__blpat:
            if isinstance(df.data[gvj__bpwqj], bodo.MapArrayType):
                fcg__ntld.append(df.columns[gvj__bpwqj])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                fcg__ntld.append(col_name)
    if fcg__ntld:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {fcg__ntld} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    zxrv__ita = len(df.columns)
    qsmbg__vct = ['data_{}'.format(i) for i in uzg__blpat]
    tvyqg__dcsf = ['data_{}'.format(i) for i in range(zxrv__ita) if i not in
        uzg__blpat]
    if qsmbg__vct:
        pdpax__mlu = len(qsmbg__vct)
    else:
        pdpax__mlu = zxrv__ita
    gznhw__cck = ', '.join(qsmbg__vct + tvyqg__dcsf)
    data_args = ', '.join('data_{}'.format(i) for i in range(zxrv__ita))
    wfv__gduo = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(zxrv__ita):
        wfv__gduo += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    wfv__gduo += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(gznhw__cck, index, pdpax__mlu))
    wfv__gduo += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(wfv__gduo, df.columns, data_args, 'index')


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
            bihr__pvrdm = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                bihr__pvrdm = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                bihr__pvrdm = lambda i: f'other[:,{i}]'
        zxrv__ita = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {bihr__pvrdm(i)})'
             for i in range(zxrv__ita))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        zfy__nlu = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(zfy__nlu)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    mfmhd__vhtys = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    fos__nta = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', mfmhd__vhtys, fos__nta,
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
    zxrv__ita = len(df.columns)
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
        for i in range(zxrv__ita):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(zxrv__ita):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(zxrv__ita):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    yyt__hcj = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    wfv__gduo = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    kpz__lmilc = {}
    oag__trrvh = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': yyt__hcj}
    oag__trrvh.update(extra_globals)
    exec(wfv__gduo, oag__trrvh, kpz__lmilc)
    impl = kpz__lmilc['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        yfpsn__cfzpo = pd.Index(lhs.columns)
        awt__pnknr = pd.Index(rhs.columns)
        zzbbo__tspow, bdy__ljap, earp__yqyy = yfpsn__cfzpo.join(awt__pnknr,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(zzbbo__tspow), bdy__ljap, earp__yqyy
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        rtrkt__lsij = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        wivr__fxbt = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, rtrkt__lsij)
        check_runtime_cols_unsupported(rhs, rtrkt__lsij)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                zzbbo__tspow, bdy__ljap, earp__yqyy = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {xyoot__rxg}) {rtrkt__lsij}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {ggcb__lkfa})'
                     if xyoot__rxg != -1 and ggcb__lkfa != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for xyoot__rxg, ggcb__lkfa in zip(bdy__ljap, earp__yqyy))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, zzbbo__tspow, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            fnfk__kmqq = []
            puro__tgeso = []
            if op in wivr__fxbt:
                for i, lyxum__cdvvy in enumerate(lhs.data):
                    if is_common_scalar_dtype([lyxum__cdvvy.dtype, rhs]):
                        fnfk__kmqq.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {rtrkt__lsij} rhs'
                            )
                    else:
                        tfxg__rtrj = f'arr{i}'
                        puro__tgeso.append(tfxg__rtrj)
                        fnfk__kmqq.append(tfxg__rtrj)
                data_args = ', '.join(fnfk__kmqq)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {rtrkt__lsij} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(puro__tgeso) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {tfxg__rtrj} = np.empty(n, dtype=np.bool_)\n' for
                    tfxg__rtrj in puro__tgeso)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(tfxg__rtrj, 
                    op == operator.ne) for tfxg__rtrj in puro__tgeso)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            fnfk__kmqq = []
            puro__tgeso = []
            if op in wivr__fxbt:
                for i, lyxum__cdvvy in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, lyxum__cdvvy.dtype]):
                        fnfk__kmqq.append(
                            f'lhs {rtrkt__lsij} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        tfxg__rtrj = f'arr{i}'
                        puro__tgeso.append(tfxg__rtrj)
                        fnfk__kmqq.append(tfxg__rtrj)
                data_args = ', '.join(fnfk__kmqq)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, rtrkt__lsij) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(puro__tgeso) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(tfxg__rtrj) for tfxg__rtrj in puro__tgeso)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(tfxg__rtrj, 
                    op == operator.ne) for tfxg__rtrj in puro__tgeso)
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
        zfy__nlu = create_binary_op_overload(op)
        overload(op)(zfy__nlu)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        rtrkt__lsij = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, rtrkt__lsij)
        check_runtime_cols_unsupported(right, rtrkt__lsij)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                zzbbo__tspow, _, earp__yqyy = _get_binop_columns(left,
                    right, True)
                wfv__gduo = 'def impl(left, right):\n'
                for i, ggcb__lkfa in enumerate(earp__yqyy):
                    if ggcb__lkfa == -1:
                        wfv__gduo += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    wfv__gduo += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    wfv__gduo += f"""  df_arr{i} {rtrkt__lsij} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {ggcb__lkfa})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    zzbbo__tspow)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(wfv__gduo, zzbbo__tspow, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            wfv__gduo = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                wfv__gduo += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                wfv__gduo += '  df_arr{0} {1} right\n'.format(i, rtrkt__lsij)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(wfv__gduo, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        zfy__nlu = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(zfy__nlu)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            rtrkt__lsij = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, rtrkt__lsij)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, rtrkt__lsij) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        zfy__nlu = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(zfy__nlu)


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
            lvedd__rseou = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                lvedd__rseou[i] = bodo.libs.array_kernels.isna(obj, i)
            return lvedd__rseou
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
            lvedd__rseou = np.empty(n, np.bool_)
            for i in range(n):
                lvedd__rseou[i] = pd.isna(obj[i])
            return lvedd__rseou
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
    wdi__eufgy = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    xbex__bxmx = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', wdi__eufgy, xbex__bxmx, package_name=
        'pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    fifjr__oci = str(expr_node)
    return fifjr__oci.startswith('left.') or fifjr__oci.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    mvh__cglfm = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (mvh__cglfm,))
    kakpr__xjv = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        bqq__ixjq = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        vgjni__fbc = {('NOT_NA', kakpr__xjv(lyxum__cdvvy)): lyxum__cdvvy for
            lyxum__cdvvy in null_set}
        yrsp__vnel, _, _ = _parse_query_expr(bqq__ixjq, env, [], [], None,
            join_cleaned_cols=vgjni__fbc)
        uui__niy = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            hwkrf__qxsr = pd.core.computation.ops.BinOp('&', yrsp__vnel,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = uui__niy
        return hwkrf__qxsr

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                yekz__etxg = set()
                aiklq__gffvg = set()
                qqgir__omi = _insert_NA_cond_body(expr_node.lhs, yekz__etxg)
                sjudv__lpty = _insert_NA_cond_body(expr_node.rhs, aiklq__gffvg)
                ttmy__bucva = yekz__etxg.intersection(aiklq__gffvg)
                yekz__etxg.difference_update(ttmy__bucva)
                aiklq__gffvg.difference_update(ttmy__bucva)
                null_set.update(ttmy__bucva)
                expr_node.lhs = append_null_checks(qqgir__omi, yekz__etxg)
                expr_node.rhs = append_null_checks(sjudv__lpty, aiklq__gffvg)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            nbvt__izk = expr_node.name
            gpgvj__krc, col_name = nbvt__izk.split('.')
            if gpgvj__krc == 'left':
                npdi__mqy = left_columns
                data = left_data
            else:
                npdi__mqy = right_columns
                data = right_data
            rwv__fmub = data[npdi__mqy.index(col_name)]
            if bodo.utils.typing.is_nullable(rwv__fmub):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    zrip__ncka = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        gos__bvz = str(expr_node.lhs)
        fxj__xmigs = str(expr_node.rhs)
        if gos__bvz.startswith('left.') and fxj__xmigs.startswith('left.'
            ) or gos__bvz.startswith('right.') and fxj__xmigs.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [gos__bvz.split('.')[1]]
        right_on = [fxj__xmigs.split('.')[1]]
        if gos__bvz.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        lwni__reojt, uzk__cctd, gzpp__awmyq = _extract_equal_conds(expr_node
            .lhs)
        lauuf__xfasw, edd__dumtx, eznq__bnhxq = _extract_equal_conds(expr_node
            .rhs)
        left_on = lwni__reojt + lauuf__xfasw
        right_on = uzk__cctd + edd__dumtx
        if gzpp__awmyq is None:
            return left_on, right_on, eznq__bnhxq
        if eznq__bnhxq is None:
            return left_on, right_on, gzpp__awmyq
        expr_node.lhs = gzpp__awmyq
        expr_node.rhs = eznq__bnhxq
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    mvh__cglfm = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (mvh__cglfm,))
    ajcsm__oito = dict()
    kakpr__xjv = pd.core.computation.parsing.clean_column_name
    for name, lulbk__fali in (('left', left_columns), ('right', right_columns)
        ):
        for lyxum__cdvvy in lulbk__fali:
            xyt__jglrx = kakpr__xjv(lyxum__cdvvy)
            xgooo__kzqtd = name, xyt__jglrx
            if xgooo__kzqtd in ajcsm__oito:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{lyxum__cdvvy}' and '{ajcsm__oito[xyt__jglrx]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            ajcsm__oito[xgooo__kzqtd] = lyxum__cdvvy
    gkh__mojkd, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=ajcsm__oito)
    left_on, right_on, dvg__tox = _extract_equal_conds(gkh__mojkd.terms)
    return left_on, right_on, _insert_NA_cond(dvg__tox, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    mfmhd__vhtys = dict(sort=sort, copy=copy, validate=validate)
    fos__nta = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    ieqry__ilwhc = tuple(sorted(set(left.columns) & set(right.columns), key
        =lambda k: str(k)))
    qcvea__ypl = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in ieqry__ilwhc and ('left.' in on_str or 
                'right.' in on_str):
                left_on, right_on, zqxg__jjbb = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if zqxg__jjbb is None:
                    qcvea__ypl = ''
                else:
                    qcvea__ypl = str(zqxg__jjbb)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = ieqry__ilwhc
        right_keys = ieqry__ilwhc
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
    ertx__sypw = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        lrulx__jewqz = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        lrulx__jewqz = list(get_overload_const_list(suffixes))
    suffix_x = lrulx__jewqz[0]
    suffix_y = lrulx__jewqz[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    wfv__gduo = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    wfv__gduo += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    wfv__gduo += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    wfv__gduo += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, ertx__sypw, qcvea__ypl))
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo}, kpz__lmilc)
    _impl = kpz__lmilc['_impl']
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
    uclo__wnrs = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    zmzu__rba = {get_overload_const_str(itgnj__gwvue) for itgnj__gwvue in (
        left_on, right_on, on) if is_overload_constant_str(itgnj__gwvue)}
    for df in (left, right):
        for i, lyxum__cdvvy in enumerate(df.data):
            if not isinstance(lyxum__cdvvy, valid_dataframe_column_types
                ) and lyxum__cdvvy not in uclo__wnrs:
                raise BodoError(
                    f'{name_func}(): use of column with {type(lyxum__cdvvy)} in merge unsupported'
                    )
            if df.columns[i] in zmzu__rba and isinstance(lyxum__cdvvy,
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
        lrulx__jewqz = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        lrulx__jewqz = list(get_overload_const_list(suffixes))
    if len(lrulx__jewqz) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    ieqry__ilwhc = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        lrnip__hike = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            lrnip__hike = on_str not in ieqry__ilwhc and ('left.' in on_str or
                'right.' in on_str)
        if len(ieqry__ilwhc) == 0 and not lrnip__hike:
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
    vmqof__dggou = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            brlsd__fmjc = left.index
            fkzn__dsu = isinstance(brlsd__fmjc, StringIndexType)
            kdxtv__mtorw = right.index
            yjjzy__gsqd = isinstance(kdxtv__mtorw, StringIndexType)
        elif is_overload_true(left_index):
            brlsd__fmjc = left.index
            fkzn__dsu = isinstance(brlsd__fmjc, StringIndexType)
            kdxtv__mtorw = right.data[right.columns.index(right_keys[0])]
            yjjzy__gsqd = kdxtv__mtorw.dtype == string_type
        elif is_overload_true(right_index):
            brlsd__fmjc = left.data[left.columns.index(left_keys[0])]
            fkzn__dsu = brlsd__fmjc.dtype == string_type
            kdxtv__mtorw = right.index
            yjjzy__gsqd = isinstance(kdxtv__mtorw, StringIndexType)
        if fkzn__dsu and yjjzy__gsqd:
            return
        brlsd__fmjc = brlsd__fmjc.dtype
        kdxtv__mtorw = kdxtv__mtorw.dtype
        try:
            hezw__rmxm = vmqof__dggou.resolve_function_type(operator.eq, (
                brlsd__fmjc, kdxtv__mtorw), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=brlsd__fmjc, rk_dtype=kdxtv__mtorw))
    else:
        for dun__xqh, egkn__wfjn in zip(left_keys, right_keys):
            brlsd__fmjc = left.data[left.columns.index(dun__xqh)].dtype
            qli__nlvs = left.data[left.columns.index(dun__xqh)]
            kdxtv__mtorw = right.data[right.columns.index(egkn__wfjn)].dtype
            sdgn__tobn = right.data[right.columns.index(egkn__wfjn)]
            if qli__nlvs == sdgn__tobn:
                continue
            glz__ruez = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=dun__xqh, lk_dtype=brlsd__fmjc, rk=egkn__wfjn,
                rk_dtype=kdxtv__mtorw))
            xxgxk__lvsb = brlsd__fmjc == string_type
            wtdl__axo = kdxtv__mtorw == string_type
            if xxgxk__lvsb ^ wtdl__axo:
                raise_bodo_error(glz__ruez)
            try:
                hezw__rmxm = vmqof__dggou.resolve_function_type(operator.eq,
                    (brlsd__fmjc, kdxtv__mtorw), {})
            except:
                raise_bodo_error(glz__ruez)


def validate_keys(keys, df):
    rlx__kuvuh = set(keys).difference(set(df.columns))
    if len(rlx__kuvuh) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in rlx__kuvuh:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {rlx__kuvuh} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    mfmhd__vhtys = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    fos__nta = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', mfmhd__vhtys, fos__nta,
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
    wfv__gduo = "def _impl(left, other, on=None, how='left',\n"
    wfv__gduo += "    lsuffix='', rsuffix='', sort=False):\n"
    wfv__gduo += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo}, kpz__lmilc)
    _impl = kpz__lmilc['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        khio__wsg = get_overload_const_list(on)
        validate_keys(khio__wsg, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    ieqry__ilwhc = tuple(set(left.columns) & set(other.columns))
    if len(ieqry__ilwhc) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=ieqry__ilwhc))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    frzd__sbwti = set(left_keys) & set(right_keys)
    ktif__jgm = set(left_columns) & set(right_columns)
    sobd__xwyu = ktif__jgm - frzd__sbwti
    crlv__ulm = set(left_columns) - ktif__jgm
    rka__fmw = set(right_columns) - ktif__jgm
    ccr__gzkjs = {}

    def insertOutColumn(col_name):
        if col_name in ccr__gzkjs:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        ccr__gzkjs[col_name] = 0
    for urq__sjeuy in frzd__sbwti:
        insertOutColumn(urq__sjeuy)
    for urq__sjeuy in sobd__xwyu:
        zoc__jwjah = str(urq__sjeuy) + suffix_x
        swu__ntlk = str(urq__sjeuy) + suffix_y
        insertOutColumn(zoc__jwjah)
        insertOutColumn(swu__ntlk)
    for urq__sjeuy in crlv__ulm:
        insertOutColumn(urq__sjeuy)
    for urq__sjeuy in rka__fmw:
        insertOutColumn(urq__sjeuy)
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
    ieqry__ilwhc = tuple(sorted(set(left.columns) & set(right.columns), key
        =lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = ieqry__ilwhc
        right_keys = ieqry__ilwhc
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
        lrulx__jewqz = suffixes
    if is_overload_constant_list(suffixes):
        lrulx__jewqz = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        lrulx__jewqz = suffixes.value
    suffix_x = lrulx__jewqz[0]
    suffix_y = lrulx__jewqz[1]
    wfv__gduo = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    wfv__gduo += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    wfv__gduo += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    wfv__gduo += "    allow_exact_matches=True, direction='backward'):\n"
    wfv__gduo += '  suffix_x = suffixes[0]\n'
    wfv__gduo += '  suffix_y = suffixes[1]\n'
    wfv__gduo += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo}, kpz__lmilc)
    _impl = kpz__lmilc['_impl']
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
    mfmhd__vhtys = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    rbq__akz = dict(sort=False, group_keys=True, squeeze=False, observed=True)
    check_unsupported_args('Dataframe.groupby', mfmhd__vhtys, rbq__akz,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    zcjo__hgbg = func_name == 'DataFrame.pivot_table'
    if zcjo__hgbg:
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
    mnnb__cbg = get_literal_value(columns)
    if isinstance(mnnb__cbg, (list, tuple)):
        if len(mnnb__cbg) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {mnnb__cbg}"
                )
        mnnb__cbg = mnnb__cbg[0]
    if mnnb__cbg not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {mnnb__cbg} not found in DataFrame {df}."
            )
    rfcew__xhqcf = df.column_index[mnnb__cbg]
    if is_overload_none(index):
        bfn__pqen = []
        tgmmg__epqrj = []
    else:
        tgmmg__epqrj = get_literal_value(index)
        if not isinstance(tgmmg__epqrj, (list, tuple)):
            tgmmg__epqrj = [tgmmg__epqrj]
        bfn__pqen = []
        for index in tgmmg__epqrj:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            bfn__pqen.append(df.column_index[index])
    if not (all(isinstance(bits__qai, int) for bits__qai in tgmmg__epqrj) or
        all(isinstance(bits__qai, str) for bits__qai in tgmmg__epqrj)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        los__fpuzw = []
        smm__ywchc = []
        vwen__nyoo = bfn__pqen + [rfcew__xhqcf]
        for i, bits__qai in enumerate(df.columns):
            if i not in vwen__nyoo:
                los__fpuzw.append(i)
                smm__ywchc.append(bits__qai)
    else:
        smm__ywchc = get_literal_value(values)
        if not isinstance(smm__ywchc, (list, tuple)):
            smm__ywchc = [smm__ywchc]
        los__fpuzw = []
        for val in smm__ywchc:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            los__fpuzw.append(df.column_index[val])
    xsd__rxe = set(los__fpuzw) | set(bfn__pqen) | {rfcew__xhqcf}
    if len(xsd__rxe) != len(los__fpuzw) + len(bfn__pqen) + 1:
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
    if len(bfn__pqen) == 0:
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
        for bihe__bhf in bfn__pqen:
            index_column = df.data[bihe__bhf]
            check_valid_index_typ(index_column)
    ajfly__yhcxq = df.data[rfcew__xhqcf]
    if isinstance(ajfly__yhcxq, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(ajfly__yhcxq, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for ugugf__zgd in los__fpuzw:
        bxkzl__dawu = df.data[ugugf__zgd]
        if isinstance(bxkzl__dawu, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or bxkzl__dawu == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (tgmmg__epqrj, mnnb__cbg, smm__ywchc, bfn__pqen, rfcew__xhqcf,
        los__fpuzw)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (tgmmg__epqrj, mnnb__cbg, smm__ywchc, bihe__bhf, rfcew__xhqcf, odyxe__nkho
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot'))
    if len(tgmmg__epqrj) == 0:
        if is_overload_none(data.index.name_typ):
            nqq__rjyy = None,
        else:
            nqq__rjyy = get_literal_value(data.index.name_typ),
    else:
        nqq__rjyy = tuple(tgmmg__epqrj)
    tgmmg__epqrj = ColNamesMetaType(nqq__rjyy)
    smm__ywchc = ColNamesMetaType(tuple(smm__ywchc))
    mnnb__cbg = ColNamesMetaType((mnnb__cbg,))
    wfv__gduo = 'def impl(data, index=None, columns=None, values=None):\n'
    wfv__gduo += "    ev = tracing.Event('df.pivot')\n"
    wfv__gduo += f'    pivot_values = data.iloc[:, {rfcew__xhqcf}].unique()\n'
    wfv__gduo += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(bihe__bhf) == 0:
        wfv__gduo += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        wfv__gduo += '        (\n'
        for hth__iyia in bihe__bhf:
            wfv__gduo += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {hth__iyia}),
"""
        wfv__gduo += '        ),\n'
    wfv__gduo += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {rfcew__xhqcf}),),
"""
    wfv__gduo += '        (\n'
    for ugugf__zgd in odyxe__nkho:
        wfv__gduo += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {ugugf__zgd}),
"""
    wfv__gduo += '        ),\n'
    wfv__gduo += '        pivot_values,\n'
    wfv__gduo += '        index_lit,\n'
    wfv__gduo += '        columns_lit,\n'
    wfv__gduo += '        values_lit,\n'
    wfv__gduo += '    )\n'
    wfv__gduo += '    ev.finalize()\n'
    wfv__gduo += '    return result\n'
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo, 'index_lit': tgmmg__epqrj, 'columns_lit':
        mnnb__cbg, 'values_lit': smm__ywchc, 'tracing': tracing}, kpz__lmilc)
    impl = kpz__lmilc['impl']
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
    mfmhd__vhtys = dict(fill_value=fill_value, margins=margins, dropna=
        dropna, margins_name=margins_name, observed=observed, sort=sort)
    fos__nta = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (tgmmg__epqrj, mnnb__cbg, smm__ywchc, bihe__bhf, rfcew__xhqcf, odyxe__nkho
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    txta__lwejv = tgmmg__epqrj
    tgmmg__epqrj = ColNamesMetaType(tuple(tgmmg__epqrj))
    smm__ywchc = ColNamesMetaType(tuple(smm__ywchc))
    udua__zpy = mnnb__cbg
    mnnb__cbg = ColNamesMetaType((mnnb__cbg,))
    wfv__gduo = 'def impl(\n'
    wfv__gduo += '    data,\n'
    wfv__gduo += '    values=None,\n'
    wfv__gduo += '    index=None,\n'
    wfv__gduo += '    columns=None,\n'
    wfv__gduo += '    aggfunc="mean",\n'
    wfv__gduo += '    fill_value=None,\n'
    wfv__gduo += '    margins=False,\n'
    wfv__gduo += '    dropna=True,\n'
    wfv__gduo += '    margins_name="All",\n'
    wfv__gduo += '    observed=False,\n'
    wfv__gduo += '    sort=True,\n'
    wfv__gduo += '    _pivot_values=None,\n'
    wfv__gduo += '):\n'
    wfv__gduo += "    ev = tracing.Event('df.pivot_table')\n"
    hwyc__lxmd = bihe__bhf + [rfcew__xhqcf] + odyxe__nkho
    wfv__gduo += f'    data = data.iloc[:, {hwyc__lxmd}]\n'
    jpudd__chpve = txta__lwejv + [udua__zpy]
    if not is_overload_none(_pivot_values):
        rfho__xgpkl = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(rfho__xgpkl)
        wfv__gduo += '    pivot_values = _pivot_values_arr\n'
        wfv__gduo += (
            f'    data = data[data.iloc[:, {len(bihe__bhf)}].isin(pivot_values)]\n'
            )
        if all(isinstance(bits__qai, str) for bits__qai in rfho__xgpkl):
            zkli__adqml = pd.array(rfho__xgpkl, 'string')
        elif all(isinstance(bits__qai, int) for bits__qai in rfho__xgpkl):
            zkli__adqml = np.array(rfho__xgpkl, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        zkli__adqml = None
    uvuhx__ewtzl = is_overload_constant_str(aggfunc
        ) and get_overload_const_str(aggfunc) == 'nunique'
    elvh__qxlfs = len(jpudd__chpve) if uvuhx__ewtzl else len(txta__lwejv)
    wfv__gduo += f"""    data = data.groupby({jpudd__chpve!r}, as_index=False, _bodo_num_shuffle_keys={elvh__qxlfs}).agg(aggfunc)
"""
    if is_overload_none(_pivot_values):
        wfv__gduo += (
            f'    pivot_values = data.iloc[:, {len(bihe__bhf)}].unique()\n')
    wfv__gduo += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    wfv__gduo += '        (\n'
    for i in range(0, len(bihe__bhf)):
        wfv__gduo += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    wfv__gduo += '        ),\n'
    wfv__gduo += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(bihe__bhf)}),),
"""
    wfv__gduo += '        (\n'
    for i in range(len(bihe__bhf) + 1, len(odyxe__nkho) + len(bihe__bhf) + 1):
        wfv__gduo += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    wfv__gduo += '        ),\n'
    wfv__gduo += '        pivot_values,\n'
    wfv__gduo += '        index_lit,\n'
    wfv__gduo += '        columns_lit,\n'
    wfv__gduo += '        values_lit,\n'
    wfv__gduo += '        check_duplicates=False,\n'
    wfv__gduo += f'        is_already_shuffled={not uvuhx__ewtzl},\n'
    wfv__gduo += '        _constant_pivot_values=_constant_pivot_values,\n'
    wfv__gduo += '    )\n'
    wfv__gduo += '    ev.finalize()\n'
    wfv__gduo += '    return result\n'
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo, 'numba': numba, 'index_lit':
        tgmmg__epqrj, 'columns_lit': mnnb__cbg, 'values_lit': smm__ywchc,
        '_pivot_values_arr': zkli__adqml, '_constant_pivot_values':
        _pivot_values, 'tracing': tracing}, kpz__lmilc)
    impl = kpz__lmilc['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    mfmhd__vhtys = dict(col_level=col_level, ignore_index=ignore_index)
    fos__nta = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', mfmhd__vhtys, fos__nta,
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
    vvy__cee = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(vvy__cee, (list, tuple)):
        vvy__cee = [vvy__cee]
    for bits__qai in vvy__cee:
        if bits__qai not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {bits__qai} not found in {frame}."
                )
    rve__yvrdw = [frame.column_index[i] for i in vvy__cee]
    if is_overload_none(value_vars):
        bnmzm__lhum = []
        zmrw__ttabi = []
        for i, bits__qai in enumerate(frame.columns):
            if i not in rve__yvrdw:
                bnmzm__lhum.append(i)
                zmrw__ttabi.append(bits__qai)
    else:
        zmrw__ttabi = get_literal_value(value_vars)
        if not isinstance(zmrw__ttabi, (list, tuple)):
            zmrw__ttabi = [zmrw__ttabi]
        zmrw__ttabi = [v for v in zmrw__ttabi if v not in vvy__cee]
        if not zmrw__ttabi:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        bnmzm__lhum = []
        for val in zmrw__ttabi:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            bnmzm__lhum.append(frame.column_index[val])
    for bits__qai in zmrw__ttabi:
        if bits__qai not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {bits__qai} not found in {frame}."
                )
    if not (all(isinstance(bits__qai, int) for bits__qai in zmrw__ttabi) or
        all(isinstance(bits__qai, str) for bits__qai in zmrw__ttabi)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    inp__onvfh = frame.data[bnmzm__lhum[0]]
    rwci__ysb = [frame.data[i].dtype for i in bnmzm__lhum]
    bnmzm__lhum = np.array(bnmzm__lhum, dtype=np.int64)
    rve__yvrdw = np.array(rve__yvrdw, dtype=np.int64)
    _, eqkk__vdeu = bodo.utils.typing.get_common_scalar_dtype(rwci__ysb)
    if not eqkk__vdeu:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': zmrw__ttabi, 'val_type': inp__onvfh
        }
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
    if frame.is_table_format and all(v == inp__onvfh.dtype for v in rwci__ysb):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            bnmzm__lhum))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(zmrw__ttabi) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {bnmzm__lhum[0]})
"""
    else:
        fgk__grr = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in bnmzm__lhum)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({fgk__grr},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in rve__yvrdw:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(zmrw__ttabi)})\n'
            )
    iftsh__aekl = ', '.join(f'out_id{i}' for i in rve__yvrdw) + (', ' if 
        len(rve__yvrdw) > 0 else '')
    data_args = iftsh__aekl + 'var_col, val_col'
    columns = tuple(vvy__cee + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(zmrw__ttabi)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    mfmhd__vhtys = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    fos__nta = dict(values=None, rownames=None, colnames=None, aggfunc=None,
        margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', mfmhd__vhtys, fos__nta,
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
    mfmhd__vhtys = dict(ignore_index=ignore_index, key=key)
    fos__nta = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', mfmhd__vhtys, fos__nta,
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
    yhz__qqsso = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        yhz__qqsso.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        nkqkl__gql = [get_overload_const_tuple(by)]
    else:
        nkqkl__gql = get_overload_const_list(by)
    nkqkl__gql = set((k, '') if (k, '') in yhz__qqsso else k for k in
        nkqkl__gql)
    if len(nkqkl__gql.difference(yhz__qqsso)) > 0:
        zohvo__qlsqv = list(set(get_overload_const_list(by)).difference(
            yhz__qqsso))
        raise_bodo_error(f'sort_values(): invalid keys {zohvo__qlsqv} for by.')
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
        twbff__ddlv = get_overload_const_list(na_position)
        for na_position in twbff__ddlv:
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
    mfmhd__vhtys = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    fos__nta = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', mfmhd__vhtys, fos__nta,
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
    wfv__gduo = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    zxrv__ita = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(zxrv__ita))
    for i in range(zxrv__ita):
        wfv__gduo += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(wfv__gduo, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    mfmhd__vhtys = dict(limit=limit, downcast=downcast)
    fos__nta = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', mfmhd__vhtys, fos__nta,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    sde__vwss = not is_overload_none(value)
    vgqr__bcwhe = not is_overload_none(method)
    if sde__vwss and vgqr__bcwhe:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not sde__vwss and not vgqr__bcwhe:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if sde__vwss:
        oiwmh__akud = 'value=value'
    else:
        oiwmh__akud = 'method=method'
    data_args = [(
        f"df['{bits__qai}'].fillna({oiwmh__akud}, inplace=inplace)" if
        isinstance(bits__qai, str) else
        f'df[{bits__qai}].fillna({oiwmh__akud}, inplace=inplace)') for
        bits__qai in df.columns]
    wfv__gduo = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        wfv__gduo += '  ' + '  \n'.join(data_args) + '\n'
        kpz__lmilc = {}
        exec(wfv__gduo, {}, kpz__lmilc)
        impl = kpz__lmilc['impl']
        return impl
    else:
        return _gen_init_df(wfv__gduo, df.columns, ', '.join(mawml__hasjg +
            '.values' for mawml__hasjg in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    mfmhd__vhtys = dict(col_level=col_level, col_fill=col_fill)
    fos__nta = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', mfmhd__vhtys, fos__nta,
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
    wfv__gduo = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    wfv__gduo += (
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
        lslz__hylt = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            lslz__hylt)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            wfv__gduo += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            seek__xxge = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = seek__xxge + data_args
        else:
            fona__piz = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [fona__piz] + data_args
    return _gen_init_df(wfv__gduo, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    pizl__ssnw = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and pizl__ssnw == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(pizl__ssnw))


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
        zemwu__ndunx = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        ddkg__usrs = get_overload_const_list(subset)
        zemwu__ndunx = []
        for biqzp__ytjyu in ddkg__usrs:
            if biqzp__ytjyu not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{biqzp__ytjyu}' not in data frame columns {df}"
                    )
            zemwu__ndunx.append(df.column_index[biqzp__ytjyu])
    zxrv__ita = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(zxrv__ita))
    wfv__gduo = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(zxrv__ita):
        wfv__gduo += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    wfv__gduo += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in zemwu__ndunx)))
    wfv__gduo += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(wfv__gduo, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    mfmhd__vhtys = dict(index=index, level=level, errors=errors)
    fos__nta = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', mfmhd__vhtys, fos__nta,
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
            ycwpw__vdb = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            ycwpw__vdb = get_overload_const_list(labels)
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
            ycwpw__vdb = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            ycwpw__vdb = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for bits__qai in ycwpw__vdb:
        if bits__qai not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(bits__qai, df.columns))
    if len(set(ycwpw__vdb)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    aqqk__rjofv = tuple(bits__qai for bits__qai in df.columns if bits__qai
         not in ycwpw__vdb)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[bits__qai], '.copy()' if not inplace else ''
        ) for bits__qai in aqqk__rjofv)
    wfv__gduo = 'def impl(df, labels=None, axis=0, index=None, columns=None,\n'
    wfv__gduo += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(wfv__gduo, aqqk__rjofv, data_args, index)


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
    mfmhd__vhtys = dict(random_state=random_state, weights=weights, axis=
        axis, ignore_index=ignore_index)
    eftmj__mfi = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', mfmhd__vhtys, eftmj__mfi,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    zxrv__ita = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(zxrv__ita))
    zqvqw__ebfar = ', '.join('rhs_data_{}'.format(i) for i in range(zxrv__ita))
    wfv__gduo = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    wfv__gduo += '  if (frac == 1 or n == len(df)) and not replace:\n'
    wfv__gduo += '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n'
    for i in range(zxrv__ita):
        wfv__gduo += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    wfv__gduo += '  if frac is None:\n'
    wfv__gduo += '    frac_d = -1.0\n'
    wfv__gduo += '  else:\n'
    wfv__gduo += '    frac_d = frac\n'
    wfv__gduo += '  if n is None:\n'
    wfv__gduo += '    n_i = 0\n'
    wfv__gduo += '  else:\n'
    wfv__gduo += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    wfv__gduo += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({zqvqw__ebfar},), {index}, n_i, frac_d, replace)
"""
    wfv__gduo += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(wfv__gduo, df.columns,
        data_args, 'index')


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
    wdi__eufgy = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    xbex__bxmx = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', wdi__eufgy, xbex__bxmx,
        package_name='pandas', module_name='DataFrame')
    oljla__brfzu = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            hyjnm__fhmp = oljla__brfzu + '\n'
            hyjnm__fhmp += 'Index: 0 entries\n'
            hyjnm__fhmp += 'Empty DataFrame'
            print(hyjnm__fhmp)
        return _info_impl
    else:
        wfv__gduo = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        wfv__gduo += '    ncols = df.shape[1]\n'
        wfv__gduo += f'    lines = "{oljla__brfzu}\\n"\n'
        wfv__gduo += f'    lines += "{df.index}: "\n'
        wfv__gduo += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            wfv__gduo += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            wfv__gduo += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            wfv__gduo += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        wfv__gduo += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        wfv__gduo += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        wfv__gduo += '    column_width = max(space, 7)\n'
        wfv__gduo += '    column= "Column"\n'
        wfv__gduo += '    underl= "------"\n'
        wfv__gduo += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        wfv__gduo += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        wfv__gduo += '    mem_size = 0\n'
        wfv__gduo += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        wfv__gduo += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        wfv__gduo += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        hexnc__cct = dict()
        for i in range(len(df.columns)):
            wfv__gduo += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            cqi__mwoj = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                cqi__mwoj = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                cofk__plz = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                cqi__mwoj = f'{cofk__plz[:-7]}'
            wfv__gduo += f'    col_dtype[{i}] = "{cqi__mwoj}"\n'
            if cqi__mwoj in hexnc__cct:
                hexnc__cct[cqi__mwoj] += 1
            else:
                hexnc__cct[cqi__mwoj] = 1
            wfv__gduo += f'    col_name[{i}] = "{df.columns[i]}"\n'
            wfv__gduo += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        wfv__gduo += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        wfv__gduo += '    for i in column_info:\n'
        wfv__gduo += "        lines += f'{i}\\n'\n"
        kgcg__qufpf = ', '.join(f'{k}({hexnc__cct[k]})' for k in sorted(
            hexnc__cct))
        wfv__gduo += f"    lines += 'dtypes: {kgcg__qufpf}\\n'\n"
        wfv__gduo += '    mem_size += df.index.nbytes\n'
        wfv__gduo += '    total_size = _sizeof_fmt(mem_size)\n'
        wfv__gduo += "    lines += f'memory usage: {total_size}'\n"
        wfv__gduo += '    print(lines)\n'
        kpz__lmilc = {}
        exec(wfv__gduo, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo': bodo,
            'np': np}, kpz__lmilc)
        _info_impl = kpz__lmilc['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    wfv__gduo = 'def impl(df, index=True, deep=False):\n'
    qonqx__hnzpz = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    rph__vqbhp = is_overload_true(index)
    columns = df.columns
    if rph__vqbhp:
        columns = ('Index',) + columns
    if len(columns) == 0:
        ddp__gnjt = ()
    elif all(isinstance(bits__qai, int) for bits__qai in columns):
        ddp__gnjt = np.array(columns, 'int64')
    elif all(isinstance(bits__qai, str) for bits__qai in columns):
        ddp__gnjt = pd.array(columns, 'string')
    else:
        ddp__gnjt = columns
    if df.is_table_format and len(df.columns) > 0:
        qccf__zrrkh = int(rph__vqbhp)
        bfy__rxj = len(columns)
        wfv__gduo += f'  nbytes_arr = np.empty({bfy__rxj}, np.int64)\n'
        wfv__gduo += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        wfv__gduo += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {qccf__zrrkh})
"""
        if rph__vqbhp:
            wfv__gduo += f'  nbytes_arr[0] = {qonqx__hnzpz}\n'
        wfv__gduo += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if rph__vqbhp:
            data = f'{qonqx__hnzpz},{data}'
        else:
            dgt__cgpuw = ',' if len(columns) == 1 else ''
            data = f'{data}{dgt__cgpuw}'
        wfv__gduo += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        ddp__gnjt}, kpz__lmilc)
    impl = kpz__lmilc['impl']
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
    qmqpi__xbpt = 'read_excel_df{}'.format(next_label())
    setattr(types, qmqpi__xbpt, df_type)
    wmeor__ivpq = False
    if is_overload_constant_list(parse_dates):
        wmeor__ivpq = get_overload_const_list(parse_dates)
    waamm__phz = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    wfv__gduo = f"""
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
    with numba.objmode(df="{qmqpi__xbpt}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{waamm__phz}}},
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
            parse_dates={wmeor__ivpq},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    kpz__lmilc = {}
    exec(wfv__gduo, globals(), kpz__lmilc)
    impl = kpz__lmilc['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as zqcc__joas:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    wfv__gduo = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    wfv__gduo += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    wfv__gduo += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        wfv__gduo += '   fig, ax = plt.subplots()\n'
    else:
        wfv__gduo += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        wfv__gduo += '   fig.set_figwidth(figsize[0])\n'
        wfv__gduo += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        wfv__gduo += '   xlabel = x\n'
    wfv__gduo += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        wfv__gduo += '   ylabel = y\n'
    else:
        wfv__gduo += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        wfv__gduo += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        wfv__gduo += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    wfv__gduo += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            wfv__gduo += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            duvcb__ckln = get_overload_const_str(x)
            den__tnffb = df.columns.index(duvcb__ckln)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if den__tnffb != i:
                        wfv__gduo += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            wfv__gduo += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        wfv__gduo += '   ax.scatter(df[x], df[y], s=20)\n'
        wfv__gduo += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        wfv__gduo += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        wfv__gduo += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        wfv__gduo += '   ax.legend()\n'
    wfv__gduo += '   return ax\n'
    kpz__lmilc = {}
    exec(wfv__gduo, {'bodo': bodo, 'plt': plt}, kpz__lmilc)
    impl = kpz__lmilc['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for ggkzw__ona in df_typ.data:
        if not (isinstance(ggkzw__ona, IntegerArrayType) or isinstance(
            ggkzw__ona.dtype, types.Number) or ggkzw__ona.dtype in (bodo.
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
        doaw__ajeuh = args[0]
        dfvgc__mhz = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        cuias__uio = doaw__ajeuh
        check_runtime_cols_unsupported(doaw__ajeuh, 'set_df_col()')
        if isinstance(doaw__ajeuh, DataFrameType):
            index = doaw__ajeuh.index
            if len(doaw__ajeuh.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(doaw__ajeuh.columns) == 0:
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
            if dfvgc__mhz in doaw__ajeuh.columns:
                aqqk__rjofv = doaw__ajeuh.columns
                kinh__vxh = doaw__ajeuh.columns.index(dfvgc__mhz)
                vqxyu__dref = list(doaw__ajeuh.data)
                vqxyu__dref[kinh__vxh] = val
                vqxyu__dref = tuple(vqxyu__dref)
            else:
                aqqk__rjofv = doaw__ajeuh.columns + (dfvgc__mhz,)
                vqxyu__dref = doaw__ajeuh.data + (val,)
            cuias__uio = DataFrameType(vqxyu__dref, index, aqqk__rjofv,
                doaw__ajeuh.dist, doaw__ajeuh.is_table_format)
        return cuias__uio(*args)


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
        rzz__wlg = args[0]
        assert isinstance(rzz__wlg, DataFrameType) and len(rzz__wlg.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        oca__kfk = args[2]
        assert len(col_names_to_replace) == len(oca__kfk
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(rzz__wlg.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in rzz__wlg.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(rzz__wlg,
            '__bodosql_replace_columns_dummy()')
        index = rzz__wlg.index
        aqqk__rjofv = rzz__wlg.columns
        vqxyu__dref = list(rzz__wlg.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            hxz__mag = oca__kfk[i]
            assert isinstance(hxz__mag, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(hxz__mag, SeriesType):
                hxz__mag = hxz__mag.data
            gvj__bpwqj = rzz__wlg.column_index[col_name]
            vqxyu__dref[gvj__bpwqj] = hxz__mag
        vqxyu__dref = tuple(vqxyu__dref)
        cuias__uio = DataFrameType(vqxyu__dref, index, aqqk__rjofv,
            rzz__wlg.dist, rzz__wlg.is_table_format)
        return cuias__uio(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    pfbhy__vpwn = {}

    def _rewrite_membership_op(self, node, left, right):
        swzs__zyd = node.op
        op = self.visit(swzs__zyd)
        return op, swzs__zyd, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    kwvmo__ukek = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in kwvmo__ukek:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in kwvmo__ukek:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        gdgu__xdnt = node.attr
        value = node.value
        grcgk__cndm = pd.core.computation.ops.LOCAL_TAG
        if gdgu__xdnt in ('str', 'dt'):
            try:
                rgae__rpgx = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as eifb__wzpxf:
                col_name = eifb__wzpxf.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            rgae__rpgx = str(self.visit(value))
        xgooo__kzqtd = rgae__rpgx, gdgu__xdnt
        if xgooo__kzqtd in join_cleaned_cols:
            gdgu__xdnt = join_cleaned_cols[xgooo__kzqtd]
        name = rgae__rpgx + '.' + gdgu__xdnt
        if name.startswith(grcgk__cndm):
            name = name[len(grcgk__cndm):]
        if gdgu__xdnt in ('str', 'dt'):
            ovvlb__daff = columns[cleaned_columns.index(rgae__rpgx)]
            pfbhy__vpwn[ovvlb__daff] = rgae__rpgx
            self.env.scope[name] = 0
            return self.term_type(grcgk__cndm + name, self.env)
        kwvmo__ukek.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in kwvmo__ukek:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        ujg__iiz = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        dfvgc__mhz = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(ujg__iiz), dfvgc__mhz))

    def op__str__(self):
        hztv__ozkfe = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            xvv__pgfu)) for xvv__pgfu in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(hztv__ozkfe)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(hztv__ozkfe)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(hztv__ozkfe))
    rtjc__rskri = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    xixu__knt = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    elokc__dmqf = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    jrzvp__cre = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    cvd__hvmty = pd.core.computation.ops.Term.__str__
    kre__xobu = pd.core.computation.ops.MathCall.__str__
    lzm__ktv = pd.core.computation.ops.Op.__str__
    uui__niy = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        gkh__mojkd = pd.core.computation.expr.Expr(expr, env=env)
        pkgfp__mwpxn = str(gkh__mojkd)
    except pd.core.computation.ops.UndefinedVariableError as eifb__wzpxf:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == eifb__wzpxf.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {eifb__wzpxf}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            rtjc__rskri)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            xixu__knt)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = elokc__dmqf
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = jrzvp__cre
        pd.core.computation.ops.Term.__str__ = cvd__hvmty
        pd.core.computation.ops.MathCall.__str__ = kre__xobu
        pd.core.computation.ops.Op.__str__ = lzm__ktv
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = uui__niy
    uptel__ocdbn = pd.core.computation.parsing.clean_column_name
    pfbhy__vpwn.update({bits__qai: uptel__ocdbn(bits__qai) for bits__qai in
        columns if uptel__ocdbn(bits__qai) in gkh__mojkd.names})
    return gkh__mojkd, pkgfp__mwpxn, pfbhy__vpwn


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        yyl__koic = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(yyl__koic))
        uazno__fytlt = namedtuple('Pandas', col_names)
        xjyy__nqerb = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], uazno__fytlt)
        super(DataFrameTupleIterator, self).__init__(name, xjyy__nqerb)

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
        jpwg__irhzr = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        jpwg__irhzr = [types.Array(types.int64, 1, 'C')] + jpwg__irhzr
        ldik__jub = DataFrameTupleIterator(col_names, jpwg__irhzr)
        return ldik__jub(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wrkaw__qno = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            wrkaw__qno)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    zct__aatfp = args[len(args) // 2:]
    yknjw__hgpc = sig.args[len(sig.args) // 2:]
    dxtq__tobh = context.make_helper(builder, sig.return_type)
    evka__egc = context.get_constant(types.intp, 0)
    nzjj__xjnek = cgutils.alloca_once_value(builder, evka__egc)
    dxtq__tobh.index = nzjj__xjnek
    for i, arr in enumerate(zct__aatfp):
        setattr(dxtq__tobh, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(zct__aatfp, yknjw__hgpc):
        context.nrt.incref(builder, arr_typ, arr)
    res = dxtq__tobh._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    erfmq__yrve, = sig.args
    vmtzs__twr, = args
    dxtq__tobh = context.make_helper(builder, erfmq__yrve, value=vmtzs__twr)
    wyhn__jtz = signature(types.intp, erfmq__yrve.array_types[1])
    pgri__htw = context.compile_internal(builder, lambda a: len(a),
        wyhn__jtz, [dxtq__tobh.array0])
    index = builder.load(dxtq__tobh.index)
    rgnbi__vgk = builder.icmp_signed('<', index, pgri__htw)
    result.set_valid(rgnbi__vgk)
    with builder.if_then(rgnbi__vgk):
        values = [index]
        for i, arr_typ in enumerate(erfmq__yrve.array_types[1:]):
            sveje__iez = getattr(dxtq__tobh, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                xrltl__ztor = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    xrltl__ztor, [sveje__iez, index])
            else:
                xrltl__ztor = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    xrltl__ztor, [sveje__iez, index])
            values.append(val)
        value = context.make_tuple(builder, erfmq__yrve.yield_type, values)
        result.yield_(value)
        uwrg__ohfj = cgutils.increment_index(builder, index)
        builder.store(uwrg__ohfj, dxtq__tobh.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    rmla__okry = ir.Assign(rhs, lhs, expr.loc)
    daft__vosd = lhs
    icav__aqi = []
    mpqm__bgvm = []
    ligqc__wmxx = typ.count
    for i in range(ligqc__wmxx):
        hln__fpag = ir.Var(daft__vosd.scope, mk_unique_var('{}_size{}'.
            format(daft__vosd.name, i)), daft__vosd.loc)
        rlc__wknp = ir.Expr.static_getitem(lhs, i, None, daft__vosd.loc)
        self.calltypes[rlc__wknp] = None
        icav__aqi.append(ir.Assign(rlc__wknp, hln__fpag, daft__vosd.loc))
        self._define(equiv_set, hln__fpag, types.intp, rlc__wknp)
        mpqm__bgvm.append(hln__fpag)
    kfkt__ueesn = tuple(mpqm__bgvm)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        kfkt__ueesn, pre=[rmla__okry] + icav__aqi)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
