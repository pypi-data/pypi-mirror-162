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
        rzg__xhmo = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({rzg__xhmo})\n')
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    poj__yrp = 'def impl(df):\n'
    if df.has_runtime_cols:
        poj__yrp += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        bsn__bwqr = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        poj__yrp += f'  return {bsn__bwqr}'
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo}, minem__dyhx)
    impl = minem__dyhx['impl']
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
    gru__scpyp = len(df.columns)
    wtbsf__gcz = set(i for i in range(gru__scpyp) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in wtbsf__gcz else '') for i in
        range(gru__scpyp))
    poj__yrp = 'def f(df):\n'.format()
    poj__yrp += '    return np.stack(({},), 1)\n'.format(data_args)
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo, 'np': np}, minem__dyhx)
    lxe__zbbj = minem__dyhx['f']
    return lxe__zbbj


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
    tbzw__lqlan = {'dtype': dtype, 'na_value': na_value}
    dym__gpxcp = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', tbzw__lqlan, dym__gpxcp,
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
            dirh__ytyp = bodo.hiframes.table.compute_num_runtime_columns(t)
            return dirh__ytyp * len(t)
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
            dirh__ytyp = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), dirh__ytyp
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    poj__yrp = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    jtu__efj = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    poj__yrp += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{jtu__efj}), {index}, None)
"""
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo}, minem__dyhx)
    impl = minem__dyhx['impl']
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
    tbzw__lqlan = {'copy': copy, 'errors': errors}
    dym__gpxcp = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', tbzw__lqlan, dym__gpxcp,
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
        aodp__adp = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        ixcoz__mwqw = _bodo_object_typeref.instance_type
        assert isinstance(ixcoz__mwqw, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in ixcoz__mwqw.column_index:
                    idx = ixcoz__mwqw.column_index[name]
                    arr_typ = ixcoz__mwqw.data[idx]
                else:
                    arr_typ = df.data[i]
                aodp__adp.append(arr_typ)
        else:
            extra_globals = {}
            vuti__jof = {}
            for i, name in enumerate(ixcoz__mwqw.columns):
                arr_typ = ixcoz__mwqw.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    umyb__zbhh = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    umyb__zbhh = boolean_dtype
                else:
                    umyb__zbhh = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = umyb__zbhh
                vuti__jof[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {vuti__jof[wzxif__doz]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if wzxif__doz in vuti__jof else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, wzxif__doz in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        xdh__eje = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            xdh__eje = {name: dtype_to_array_type(parse_dtype(dtype)) for 
                name, dtype in xdh__eje.items()}
            for i, name in enumerate(df.columns):
                if name in xdh__eje:
                    arr_typ = xdh__eje[name]
                else:
                    arr_typ = df.data[i]
                aodp__adp.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(xdh__eje[wzxif__doz])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if wzxif__doz in xdh__eje else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, wzxif__doz in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        aodp__adp = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        xrz__dund = bodo.TableType(tuple(aodp__adp))
        extra_globals['out_table_typ'] = xrz__dund
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
        ypx__mibmw = types.none
        extra_globals = {'output_arr_typ': ypx__mibmw}
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
        vbyg__ahusc = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                vbyg__ahusc.append(arr + '.copy()')
            elif is_overload_false(deep):
                vbyg__ahusc.append(arr)
            else:
                vbyg__ahusc.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(vbyg__ahusc)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    tbzw__lqlan = {'index': index, 'level': level, 'errors': errors}
    dym__gpxcp = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', tbzw__lqlan, dym__gpxcp,
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
        hqr__ziajl = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        hqr__ziajl = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    nkrmp__aleic = tuple([hqr__ziajl.get(df.columns[i], df.columns[i]) for
        i in range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    ghq__wymq = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        ghq__wymq = df.copy(columns=nkrmp__aleic)
        ypx__mibmw = types.none
        extra_globals = {'output_arr_typ': ypx__mibmw}
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
        vbyg__ahusc = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                vbyg__ahusc.append(arr + '.copy()')
            elif is_overload_false(copy):
                vbyg__ahusc.append(arr)
            else:
                vbyg__ahusc.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(vbyg__ahusc)
    return _gen_init_df(header, nkrmp__aleic, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    colhx__xmkff = not is_overload_none(items)
    npm__kgpn = not is_overload_none(like)
    niu__guks = not is_overload_none(regex)
    qnt__guyb = colhx__xmkff ^ npm__kgpn ^ niu__guks
    wla__vboke = not (colhx__xmkff or npm__kgpn or niu__guks)
    if wla__vboke:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not qnt__guyb:
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
        jarl__qlgg = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        jarl__qlgg = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert jarl__qlgg in {0, 1}
    poj__yrp = 'def impl(df, items=None, like=None, regex=None, axis=None):\n'
    if jarl__qlgg == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if jarl__qlgg == 1:
        inwk__kdtef = []
        yczan__cgyvd = []
        hksxm__fbxkz = []
        if colhx__xmkff:
            if is_overload_constant_list(items):
                ibge__wxtld = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if npm__kgpn:
            if is_overload_constant_str(like):
                ogcm__txqx = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if niu__guks:
            if is_overload_constant_str(regex):
                tfcg__lfvr = get_overload_const_str(regex)
                tlvk__smvyz = re.compile(tfcg__lfvr)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, wzxif__doz in enumerate(df.columns):
            if not is_overload_none(items
                ) and wzxif__doz in ibge__wxtld or not is_overload_none(like
                ) and ogcm__txqx in str(wzxif__doz) or not is_overload_none(
                regex) and tlvk__smvyz.search(str(wzxif__doz)):
                yczan__cgyvd.append(wzxif__doz)
                hksxm__fbxkz.append(i)
        for i in hksxm__fbxkz:
            var_name = f'data_{i}'
            inwk__kdtef.append(var_name)
            poj__yrp += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(inwk__kdtef)
        return _gen_init_df(poj__yrp, yczan__cgyvd, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    ghq__wymq = None
    if df.is_table_format:
        ypx__mibmw = types.Array(types.bool_, 1, 'C')
        ghq__wymq = DataFrameType(tuple([ypx__mibmw] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': ypx__mibmw}
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
    zrax__vhk = is_overload_none(include)
    qcjv__uvxki = is_overload_none(exclude)
    qrfo__dblc = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if zrax__vhk and qcjv__uvxki:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not zrax__vhk:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            jidmo__aopy = [dtype_to_array_type(parse_dtype(elem, qrfo__dblc
                )) for elem in include]
        elif is_legal_input(include):
            jidmo__aopy = [dtype_to_array_type(parse_dtype(include,
                qrfo__dblc))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        jidmo__aopy = get_nullable_and_non_nullable_types(jidmo__aopy)
        qutr__gqxqk = tuple(wzxif__doz for i, wzxif__doz in enumerate(df.
            columns) if df.data[i] in jidmo__aopy)
    else:
        qutr__gqxqk = df.columns
    if not qcjv__uvxki:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            opju__ktqqg = [dtype_to_array_type(parse_dtype(elem, qrfo__dblc
                )) for elem in exclude]
        elif is_legal_input(exclude):
            opju__ktqqg = [dtype_to_array_type(parse_dtype(exclude,
                qrfo__dblc))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        opju__ktqqg = get_nullable_and_non_nullable_types(opju__ktqqg)
        qutr__gqxqk = tuple(wzxif__doz for wzxif__doz in qutr__gqxqk if df.
            data[df.column_index[wzxif__doz]] not in opju__ktqqg)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[wzxif__doz]})'
         for wzxif__doz in qutr__gqxqk)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, qutr__gqxqk, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    ghq__wymq = None
    if df.is_table_format:
        ypx__mibmw = types.Array(types.bool_, 1, 'C')
        ghq__wymq = DataFrameType(tuple([ypx__mibmw] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': ypx__mibmw}
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
    dwkm__xuypn = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in dwkm__xuypn:
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
    dwkm__xuypn = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in dwkm__xuypn:
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
    poj__yrp = 'def impl(df, values):\n'
    tgbt__ohrq = {}
    pqeu__cosk = False
    if isinstance(values, DataFrameType):
        pqeu__cosk = True
        for i, wzxif__doz in enumerate(df.columns):
            if wzxif__doz in values.column_index:
                cek__gvze = 'val{}'.format(i)
                poj__yrp += f"""  {cek__gvze} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[wzxif__doz]})
"""
                tgbt__ohrq[wzxif__doz] = cek__gvze
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        tgbt__ohrq = {wzxif__doz: 'values' for wzxif__doz in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        cek__gvze = 'data{}'.format(i)
        poj__yrp += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(cek__gvze, i))
        data.append(cek__gvze)
    tuvwo__ecq = ['out{}'.format(i) for i in range(len(df.columns))]
    mfds__wkfjp = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    qodpo__lzr = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    tho__tja = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, eqiw__sqogt) in enumerate(zip(df.columns, data)):
        if cname in tgbt__ohrq:
            pjdit__elhv = tgbt__ohrq[cname]
            if pqeu__cosk:
                poj__yrp += mfds__wkfjp.format(eqiw__sqogt, pjdit__elhv,
                    tuvwo__ecq[i])
            else:
                poj__yrp += qodpo__lzr.format(eqiw__sqogt, pjdit__elhv,
                    tuvwo__ecq[i])
        else:
            poj__yrp += tho__tja.format(tuvwo__ecq[i])
    return _gen_init_df(poj__yrp, df.columns, ','.join(tuvwo__ecq))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    gru__scpyp = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(gru__scpyp))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    fki__wppbj = [wzxif__doz for wzxif__doz, qbgwd__ccezu in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(qbgwd__ccezu
        .dtype)]
    assert len(fki__wppbj) != 0
    kuko__cjtw = ''
    if not any(qbgwd__ccezu == types.float64 for qbgwd__ccezu in df.data):
        kuko__cjtw = '.astype(np.float64)'
    dfqkk__prul = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[wzxif__doz], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[wzxif__doz]], IntegerArrayType) or
        df.data[df.column_index[wzxif__doz]] == boolean_array else '') for
        wzxif__doz in fki__wppbj)
    cjz__unzhg = 'np.stack(({},), 1){}'.format(dfqkk__prul, kuko__cjtw)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(fki__wppbj))
        )
    index = f'{generate_col_to_index_func_text(fki__wppbj)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(cjz__unzhg)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, fki__wppbj, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    inu__venp = dict(ddof=ddof)
    tisnf__uro = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    tfhb__psfpc = '1' if is_overload_none(min_periods) else 'min_periods'
    fki__wppbj = [wzxif__doz for wzxif__doz, qbgwd__ccezu in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(qbgwd__ccezu
        .dtype)]
    if len(fki__wppbj) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    kuko__cjtw = ''
    if not any(qbgwd__ccezu == types.float64 for qbgwd__ccezu in df.data):
        kuko__cjtw = '.astype(np.float64)'
    dfqkk__prul = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[wzxif__doz], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[wzxif__doz]], IntegerArrayType) or
        df.data[df.column_index[wzxif__doz]] == boolean_array else '') for
        wzxif__doz in fki__wppbj)
    cjz__unzhg = 'np.stack(({},), 1){}'.format(dfqkk__prul, kuko__cjtw)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(fki__wppbj))
        )
    index = f'pd.Index({fki__wppbj})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(cjz__unzhg)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        tfhb__psfpc)
    return _gen_init_df(header, fki__wppbj, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    inu__venp = dict(axis=axis, level=level, numeric_only=numeric_only)
    tisnf__uro = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    poj__yrp = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    poj__yrp += '  data = np.array([{}])\n'.format(data_args)
    bsn__bwqr = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    poj__yrp += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {bsn__bwqr})\n'
        )
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo, 'np': np}, minem__dyhx)
    impl = minem__dyhx['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    inu__venp = dict(axis=axis)
    tisnf__uro = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    poj__yrp = 'def impl(df, axis=0, dropna=True):\n'
    poj__yrp += '  data = np.asarray(({},))\n'.format(data_args)
    bsn__bwqr = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    poj__yrp += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {bsn__bwqr})\n'
        )
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo, 'np': np}, minem__dyhx)
    impl = minem__dyhx['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    inu__venp = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    tisnf__uro = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    inu__venp = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    tisnf__uro = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    inu__venp = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    tisnf__uro = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    inu__venp = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    tisnf__uro = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    inu__venp = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    tisnf__uro = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    inu__venp = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    tisnf__uro = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    inu__venp = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    tisnf__uro = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    inu__venp = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    tisnf__uro = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    inu__venp = dict(numeric_only=numeric_only, interpolation=interpolation)
    tisnf__uro = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    inu__venp = dict(axis=axis, skipna=skipna)
    tisnf__uro = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for aiiqs__yecvm in df.data:
        if not (bodo.utils.utils.is_np_array_typ(aiiqs__yecvm) and (
            aiiqs__yecvm.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(aiiqs__yecvm.dtype, (types.Number, types.Boolean))) or
            isinstance(aiiqs__yecvm, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or aiiqs__yecvm in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {aiiqs__yecvm} not supported.'
                )
        if isinstance(aiiqs__yecvm, bodo.CategoricalArrayType
            ) and not aiiqs__yecvm.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    inu__venp = dict(axis=axis, skipna=skipna)
    tisnf__uro = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for aiiqs__yecvm in df.data:
        if not (bodo.utils.utils.is_np_array_typ(aiiqs__yecvm) and (
            aiiqs__yecvm.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(aiiqs__yecvm.dtype, (types.Number, types.Boolean))) or
            isinstance(aiiqs__yecvm, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or aiiqs__yecvm in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {aiiqs__yecvm} not supported.'
                )
        if isinstance(aiiqs__yecvm, bodo.CategoricalArrayType
            ) and not aiiqs__yecvm.dtype.ordered:
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
        fki__wppbj = tuple(wzxif__doz for wzxif__doz, qbgwd__ccezu in zip(
            df.columns, df.data) if bodo.utils.typing.
            _is_pandas_numeric_dtype(qbgwd__ccezu.dtype))
        out_colnames = fki__wppbj
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            rrvf__pgny = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[wzxif__doz]].dtype) for wzxif__doz in out_colnames
                ]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(rrvf__pgny, []))
    except NotImplementedError as fthel__sqrmu:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    ipr__hin = ''
    if func_name in ('sum', 'prod'):
        ipr__hin = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    poj__yrp = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, ipr__hin))
    if func_name == 'quantile':
        poj__yrp = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        poj__yrp = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        poj__yrp += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        poj__yrp += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        minem__dyhx)
    impl = minem__dyhx['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    hprr__dxzik = ''
    if func_name in ('min', 'max'):
        hprr__dxzik = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        hprr__dxzik = ', dtype=np.float32'
    accmc__pqkdb = f'bodo.libs.array_ops.array_op_{func_name}'
    psuqg__gakm = ''
    if func_name in ['sum', 'prod']:
        psuqg__gakm = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        psuqg__gakm = 'index'
    elif func_name == 'quantile':
        psuqg__gakm = 'q'
    elif func_name in ['std', 'var']:
        psuqg__gakm = 'True, ddof'
    elif func_name == 'median':
        psuqg__gakm = 'True'
    data_args = ', '.join(
        f'{accmc__pqkdb}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[wzxif__doz]}), {psuqg__gakm})'
         for wzxif__doz in out_colnames)
    poj__yrp = ''
    if func_name in ('idxmax', 'idxmin'):
        poj__yrp += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        poj__yrp += ('  data = bodo.utils.conversion.coerce_to_array(({},))\n'
            .format(data_args))
    else:
        poj__yrp += '  data = np.asarray(({},){})\n'.format(data_args,
            hprr__dxzik)
    poj__yrp += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return poj__yrp


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    nydzs__ttnhz = [df_type.column_index[wzxif__doz] for wzxif__doz in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in nydzs__ttnhz)
    loqx__wre = '\n        '.join(f'row[{i}] = arr_{nydzs__ttnhz[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    rps__zpg = f'len(arr_{nydzs__ttnhz[0]})'
    rtl__zki = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum': 'np.nansum',
        'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in rtl__zki:
        loxww__vibv = rtl__zki[func_name]
        wce__kkax = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        poj__yrp = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {rps__zpg}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{wce__kkax})
    for i in numba.parfors.parfor.internal_prange(n):
        {loqx__wre}
        A[i] = {loxww__vibv}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return poj__yrp
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    inu__venp = dict(fill_method=fill_method, limit=limit, freq=freq)
    tisnf__uro = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', inu__venp, tisnf__uro,
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
    inu__venp = dict(axis=axis, skipna=skipna)
    tisnf__uro = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', inu__venp, tisnf__uro,
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
    inu__venp = dict(skipna=skipna)
    tisnf__uro = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', inu__venp, tisnf__uro,
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
    inu__venp = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    tisnf__uro = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    fki__wppbj = [wzxif__doz for wzxif__doz, qbgwd__ccezu in zip(df.columns,
        df.data) if _is_describe_type(qbgwd__ccezu)]
    if len(fki__wppbj) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    dvukt__xaf = sum(df.data[df.column_index[wzxif__doz]].dtype == bodo.
        datetime64ns for wzxif__doz in fki__wppbj)

    def _get_describe(col_ind):
        locj__dsjr = df.data[col_ind].dtype == bodo.datetime64ns
        if dvukt__xaf and dvukt__xaf != len(fki__wppbj):
            if locj__dsjr:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for wzxif__doz in fki__wppbj:
        col_ind = df.column_index[wzxif__doz]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[wzxif__doz]) for
        wzxif__doz in fki__wppbj)
    juwod__oint = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if dvukt__xaf == len(fki__wppbj):
        juwod__oint = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif dvukt__xaf:
        juwod__oint = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({juwod__oint})'
    return _gen_init_df(header, fki__wppbj, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    inu__venp = dict(axis=axis, convert=convert, is_copy=is_copy)
    tisnf__uro = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', inu__venp, tisnf__uro,
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
    inu__venp = dict(freq=freq, axis=axis, fill_value=fill_value)
    tisnf__uro = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for tdsft__tsgs in df.data:
        if not is_supported_shift_array_type(tdsft__tsgs):
            raise BodoError(
                f'Dataframe.shift() column input type {tdsft__tsgs.dtype} not supported yet.'
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
    inu__venp = dict(axis=axis)
    tisnf__uro = dict(axis=0)
    check_unsupported_args('DataFrame.diff', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for tdsft__tsgs in df.data:
        if not (isinstance(tdsft__tsgs, types.Array) and (isinstance(
            tdsft__tsgs.dtype, types.Number) or tdsft__tsgs.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {tdsft__tsgs.dtype} not supported.'
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
    rwtq__qnhm = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(rwtq__qnhm)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        lrylu__ebcpj = get_overload_const_list(column)
    else:
        lrylu__ebcpj = [get_literal_value(column)]
    gaa__frdm = [df.column_index[wzxif__doz] for wzxif__doz in lrylu__ebcpj]
    for i in gaa__frdm:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{gaa__frdm[0]})\n'
        )
    for i in range(n):
        if i in gaa__frdm:
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
    tbzw__lqlan = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    dym__gpxcp = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', tbzw__lqlan, dym__gpxcp,
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
    columns = tuple(wzxif__doz for wzxif__doz in df.columns if wzxif__doz !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    tbzw__lqlan = {'inplace': inplace}
    dym__gpxcp = {'inplace': False}
    check_unsupported_args('query', tbzw__lqlan, dym__gpxcp, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        drb__quffa = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[drb__quffa]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    tbzw__lqlan = {'subset': subset, 'keep': keep}
    dym__gpxcp = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', tbzw__lqlan, dym__gpxcp,
        package_name='pandas', module_name='DataFrame')
    gru__scpyp = len(df.columns)
    poj__yrp = "def impl(df, subset=None, keep='first'):\n"
    for i in range(gru__scpyp):
        poj__yrp += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    fix__smg = ', '.join(f'data_{i}' for i in range(gru__scpyp))
    fix__smg += ',' if gru__scpyp == 1 else ''
    poj__yrp += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({fix__smg}))\n')
    poj__yrp += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    poj__yrp += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo}, minem__dyhx)
    impl = minem__dyhx['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    tbzw__lqlan = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    dym__gpxcp = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    giphx__ywaiu = []
    if is_overload_constant_list(subset):
        giphx__ywaiu = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        giphx__ywaiu = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        giphx__ywaiu = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    ectp__tma = []
    for col_name in giphx__ywaiu:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        ectp__tma.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', tbzw__lqlan,
        dym__gpxcp, package_name='pandas', module_name='DataFrame')
    nokmi__xqga = []
    if ectp__tma:
        for yhih__nuulp in ectp__tma:
            if isinstance(df.data[yhih__nuulp], bodo.MapArrayType):
                nokmi__xqga.append(df.columns[yhih__nuulp])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                nokmi__xqga.append(col_name)
    if nokmi__xqga:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {nokmi__xqga} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    gru__scpyp = len(df.columns)
    pfac__reo = ['data_{}'.format(i) for i in ectp__tma]
    vbp__ycoit = ['data_{}'.format(i) for i in range(gru__scpyp) if i not in
        ectp__tma]
    if pfac__reo:
        xcald__zflj = len(pfac__reo)
    else:
        xcald__zflj = gru__scpyp
    pgkc__raxy = ', '.join(pfac__reo + vbp__ycoit)
    data_args = ', '.join('data_{}'.format(i) for i in range(gru__scpyp))
    poj__yrp = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(gru__scpyp):
        poj__yrp += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    poj__yrp += (
        '  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})\n'
        .format(pgkc__raxy, index, xcald__zflj))
    poj__yrp += '  index = bodo.utils.conversion.index_from_array(index_arr)\n'
    return _gen_init_df(poj__yrp, df.columns, data_args, 'index')


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
            jrynw__bhpxq = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                jrynw__bhpxq = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                jrynw__bhpxq = lambda i: f'other[:,{i}]'
        gru__scpyp = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {jrynw__bhpxq(i)})'
             for i in range(gru__scpyp))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        ieti__plng = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(ieti__plng
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    inu__venp = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    tisnf__uro = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', inu__venp, tisnf__uro,
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
    gru__scpyp = len(df.columns)
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
        for i in range(gru__scpyp):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(gru__scpyp):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(gru__scpyp):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    bvl__lxx = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    poj__yrp = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    minem__dyhx = {}
    fcb__whf = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': bvl__lxx}
    fcb__whf.update(extra_globals)
    exec(poj__yrp, fcb__whf, minem__dyhx)
    impl = minem__dyhx['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        fbedo__cjgqn = pd.Index(lhs.columns)
        wpvlv__vfq = pd.Index(rhs.columns)
        bhyf__tfop, gtq__wslfe, ssfx__xrocj = fbedo__cjgqn.join(wpvlv__vfq,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(bhyf__tfop), gtq__wslfe, ssfx__xrocj
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        rzqbb__gcr = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        fvpm__hdcao = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, rzqbb__gcr)
        check_runtime_cols_unsupported(rhs, rzqbb__gcr)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                bhyf__tfop, gtq__wslfe, ssfx__xrocj = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {izudb__nwv}) {rzqbb__gcr}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {jxqs__dyzv})'
                     if izudb__nwv != -1 and jxqs__dyzv != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for izudb__nwv, jxqs__dyzv in zip(gtq__wslfe, ssfx__xrocj)
                    )
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, bhyf__tfop, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            euvqc__hdf = []
            spfpa__hbs = []
            if op in fvpm__hdcao:
                for i, tfegb__ffe in enumerate(lhs.data):
                    if is_common_scalar_dtype([tfegb__ffe.dtype, rhs]):
                        euvqc__hdf.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {rzqbb__gcr} rhs'
                            )
                    else:
                        gaee__iaq = f'arr{i}'
                        spfpa__hbs.append(gaee__iaq)
                        euvqc__hdf.append(gaee__iaq)
                data_args = ', '.join(euvqc__hdf)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {rzqbb__gcr} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(spfpa__hbs) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {gaee__iaq} = np.empty(n, dtype=np.bool_)\n' for
                    gaee__iaq in spfpa__hbs)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(gaee__iaq, op ==
                    operator.ne) for gaee__iaq in spfpa__hbs)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            euvqc__hdf = []
            spfpa__hbs = []
            if op in fvpm__hdcao:
                for i, tfegb__ffe in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, tfegb__ffe.dtype]):
                        euvqc__hdf.append(
                            f'lhs {rzqbb__gcr} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        gaee__iaq = f'arr{i}'
                        spfpa__hbs.append(gaee__iaq)
                        euvqc__hdf.append(gaee__iaq)
                data_args = ', '.join(euvqc__hdf)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, rzqbb__gcr) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(spfpa__hbs) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(gaee__iaq) for gaee__iaq in spfpa__hbs)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(gaee__iaq, op ==
                    operator.ne) for gaee__iaq in spfpa__hbs)
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
        ieti__plng = create_binary_op_overload(op)
        overload(op)(ieti__plng)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        rzqbb__gcr = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, rzqbb__gcr)
        check_runtime_cols_unsupported(right, rzqbb__gcr)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                bhyf__tfop, _, ssfx__xrocj = _get_binop_columns(left, right,
                    True)
                poj__yrp = 'def impl(left, right):\n'
                for i, jxqs__dyzv in enumerate(ssfx__xrocj):
                    if jxqs__dyzv == -1:
                        poj__yrp += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    poj__yrp += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    poj__yrp += f"""  df_arr{i} {rzqbb__gcr} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {jxqs__dyzv})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    bhyf__tfop)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(poj__yrp, bhyf__tfop, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            poj__yrp = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                poj__yrp += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                poj__yrp += '  df_arr{0} {1} right\n'.format(i, rzqbb__gcr)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(poj__yrp, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        ieti__plng = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(ieti__plng)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            rzqbb__gcr = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, rzqbb__gcr)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, rzqbb__gcr) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        ieti__plng = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(ieti__plng)


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
            eju__bmcvb = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                eju__bmcvb[i] = bodo.libs.array_kernels.isna(obj, i)
            return eju__bmcvb
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
            eju__bmcvb = np.empty(n, np.bool_)
            for i in range(n):
                eju__bmcvb[i] = pd.isna(obj[i])
            return eju__bmcvb
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
    tbzw__lqlan = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    dym__gpxcp = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', tbzw__lqlan, dym__gpxcp, package_name
        ='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    ogrql__auvhx = str(expr_node)
    return ogrql__auvhx.startswith('left.') or ogrql__auvhx.startswith('right.'
        )


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    trdc__rxvz = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (trdc__rxvz,))
    elpcs__nvl = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        wdwrx__afsm = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        uiwnf__focz = {('NOT_NA', elpcs__nvl(tfegb__ffe)): tfegb__ffe for
            tfegb__ffe in null_set}
        gxt__byw, _, _ = _parse_query_expr(wdwrx__afsm, env, [], [], None,
            join_cleaned_cols=uiwnf__focz)
        ajc__tvxgx = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            oydd__zkj = pd.core.computation.ops.BinOp('&', gxt__byw, expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = ajc__tvxgx
        return oydd__zkj

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                njpfn__aln = set()
                zqqyh__kon = set()
                itvxb__ipi = _insert_NA_cond_body(expr_node.lhs, njpfn__aln)
                qlhb__hhxp = _insert_NA_cond_body(expr_node.rhs, zqqyh__kon)
                hrz__nir = njpfn__aln.intersection(zqqyh__kon)
                njpfn__aln.difference_update(hrz__nir)
                zqqyh__kon.difference_update(hrz__nir)
                null_set.update(hrz__nir)
                expr_node.lhs = append_null_checks(itvxb__ipi, njpfn__aln)
                expr_node.rhs = append_null_checks(qlhb__hhxp, zqqyh__kon)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            lci__ckbbz = expr_node.name
            twd__cpf, col_name = lci__ckbbz.split('.')
            if twd__cpf == 'left':
                djl__ddnc = left_columns
                data = left_data
            else:
                djl__ddnc = right_columns
                data = right_data
            zex__mad = data[djl__ddnc.index(col_name)]
            if bodo.utils.typing.is_nullable(zex__mad):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    mgpzi__yzh = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        umbop__xord = str(expr_node.lhs)
        cgrqm__ubuen = str(expr_node.rhs)
        if umbop__xord.startswith('left.') and cgrqm__ubuen.startswith('left.'
            ) or umbop__xord.startswith('right.') and cgrqm__ubuen.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [umbop__xord.split('.')[1]]
        right_on = [cgrqm__ubuen.split('.')[1]]
        if umbop__xord.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        tesuh__uyjnt, syvjl__pgaw, aksf__ypgk = _extract_equal_conds(expr_node
            .lhs)
        wkd__tsch, pshz__iqakd, kqqqu__pxq = _extract_equal_conds(expr_node.rhs
            )
        left_on = tesuh__uyjnt + wkd__tsch
        right_on = syvjl__pgaw + pshz__iqakd
        if aksf__ypgk is None:
            return left_on, right_on, kqqqu__pxq
        if kqqqu__pxq is None:
            return left_on, right_on, aksf__ypgk
        expr_node.lhs = aksf__ypgk
        expr_node.rhs = kqqqu__pxq
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    trdc__rxvz = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (trdc__rxvz,))
    hqr__ziajl = dict()
    elpcs__nvl = pd.core.computation.parsing.clean_column_name
    for name, tajg__xag in (('left', left_columns), ('right', right_columns)):
        for tfegb__ffe in tajg__xag:
            qccn__mzf = elpcs__nvl(tfegb__ffe)
            zwtpp__hpj = name, qccn__mzf
            if zwtpp__hpj in hqr__ziajl:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{tfegb__ffe}' and '{hqr__ziajl[qccn__mzf]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            hqr__ziajl[zwtpp__hpj] = tfegb__ffe
    xdx__ofkfe, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=hqr__ziajl)
    left_on, right_on, zuy__orvdw = _extract_equal_conds(xdx__ofkfe.terms)
    return left_on, right_on, _insert_NA_cond(zuy__orvdw, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    inu__venp = dict(sort=sort, copy=copy, validate=validate)
    tisnf__uro = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    nbtwn__fpfkv = tuple(sorted(set(left.columns) & set(right.columns), key
        =lambda k: str(k)))
    pehvp__nss = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in nbtwn__fpfkv and ('left.' in on_str or 
                'right.' in on_str):
                left_on, right_on, mppxc__lao = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if mppxc__lao is None:
                    pehvp__nss = ''
                else:
                    pehvp__nss = str(mppxc__lao)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = nbtwn__fpfkv
        right_keys = nbtwn__fpfkv
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
    dut__gyy = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        feaps__dobp = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        feaps__dobp = list(get_overload_const_list(suffixes))
    suffix_x = feaps__dobp[0]
    suffix_y = feaps__dobp[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    poj__yrp = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    poj__yrp += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    poj__yrp += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    poj__yrp += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, dut__gyy, pehvp__nss))
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo}, minem__dyhx)
    _impl = minem__dyhx['_impl']
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
    wog__rccss = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    tojk__vachk = {get_overload_const_str(ydber__dbfz) for ydber__dbfz in (
        left_on, right_on, on) if is_overload_constant_str(ydber__dbfz)}
    for df in (left, right):
        for i, tfegb__ffe in enumerate(df.data):
            if not isinstance(tfegb__ffe, valid_dataframe_column_types
                ) and tfegb__ffe not in wog__rccss:
                raise BodoError(
                    f'{name_func}(): use of column with {type(tfegb__ffe)} in merge unsupported'
                    )
            if df.columns[i] in tojk__vachk and isinstance(tfegb__ffe,
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
        feaps__dobp = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        feaps__dobp = list(get_overload_const_list(suffixes))
    if len(feaps__dobp) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    nbtwn__fpfkv = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        sbcno__dpr = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            sbcno__dpr = on_str not in nbtwn__fpfkv and ('left.' in on_str or
                'right.' in on_str)
        if len(nbtwn__fpfkv) == 0 and not sbcno__dpr:
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
    kdngl__pwee = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            vhpj__dlkk = left.index
            ehr__bknpl = isinstance(vhpj__dlkk, StringIndexType)
            htu__ywvq = right.index
            xik__qce = isinstance(htu__ywvq, StringIndexType)
        elif is_overload_true(left_index):
            vhpj__dlkk = left.index
            ehr__bknpl = isinstance(vhpj__dlkk, StringIndexType)
            htu__ywvq = right.data[right.columns.index(right_keys[0])]
            xik__qce = htu__ywvq.dtype == string_type
        elif is_overload_true(right_index):
            vhpj__dlkk = left.data[left.columns.index(left_keys[0])]
            ehr__bknpl = vhpj__dlkk.dtype == string_type
            htu__ywvq = right.index
            xik__qce = isinstance(htu__ywvq, StringIndexType)
        if ehr__bknpl and xik__qce:
            return
        vhpj__dlkk = vhpj__dlkk.dtype
        htu__ywvq = htu__ywvq.dtype
        try:
            zezzm__woz = kdngl__pwee.resolve_function_type(operator.eq, (
                vhpj__dlkk, htu__ywvq), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=vhpj__dlkk, rk_dtype=htu__ywvq))
    else:
        for ijdx__icnn, jncj__pymon in zip(left_keys, right_keys):
            vhpj__dlkk = left.data[left.columns.index(ijdx__icnn)].dtype
            linb__fzpi = left.data[left.columns.index(ijdx__icnn)]
            htu__ywvq = right.data[right.columns.index(jncj__pymon)].dtype
            xlj__hjap = right.data[right.columns.index(jncj__pymon)]
            if linb__fzpi == xlj__hjap:
                continue
            brel__zait = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=ijdx__icnn, lk_dtype=vhpj__dlkk, rk=jncj__pymon,
                rk_dtype=htu__ywvq))
            noz__hxvav = vhpj__dlkk == string_type
            fxz__llkdn = htu__ywvq == string_type
            if noz__hxvav ^ fxz__llkdn:
                raise_bodo_error(brel__zait)
            try:
                zezzm__woz = kdngl__pwee.resolve_function_type(operator.eq,
                    (vhpj__dlkk, htu__ywvq), {})
            except:
                raise_bodo_error(brel__zait)


def validate_keys(keys, df):
    tqrqy__mtjvl = set(keys).difference(set(df.columns))
    if len(tqrqy__mtjvl) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in tqrqy__mtjvl:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {tqrqy__mtjvl} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    inu__venp = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    tisnf__uro = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', inu__venp, tisnf__uro,
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
    poj__yrp = "def _impl(left, other, on=None, how='left',\n"
    poj__yrp += "    lsuffix='', rsuffix='', sort=False):\n"
    poj__yrp += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo}, minem__dyhx)
    _impl = minem__dyhx['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        peaf__rzko = get_overload_const_list(on)
        validate_keys(peaf__rzko, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    nbtwn__fpfkv = tuple(set(left.columns) & set(other.columns))
    if len(nbtwn__fpfkv) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=nbtwn__fpfkv))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    bjpi__buw = set(left_keys) & set(right_keys)
    yhn__yns = set(left_columns) & set(right_columns)
    plaj__pxrv = yhn__yns - bjpi__buw
    dmrbl__jub = set(left_columns) - yhn__yns
    jegn__rlwz = set(right_columns) - yhn__yns
    ewo__laa = {}

    def insertOutColumn(col_name):
        if col_name in ewo__laa:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        ewo__laa[col_name] = 0
    for vpm__jeu in bjpi__buw:
        insertOutColumn(vpm__jeu)
    for vpm__jeu in plaj__pxrv:
        nuubu__jvvz = str(vpm__jeu) + suffix_x
        uqq__zhyb = str(vpm__jeu) + suffix_y
        insertOutColumn(nuubu__jvvz)
        insertOutColumn(uqq__zhyb)
    for vpm__jeu in dmrbl__jub:
        insertOutColumn(vpm__jeu)
    for vpm__jeu in jegn__rlwz:
        insertOutColumn(vpm__jeu)
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
    nbtwn__fpfkv = tuple(sorted(set(left.columns) & set(right.columns), key
        =lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = nbtwn__fpfkv
        right_keys = nbtwn__fpfkv
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
        feaps__dobp = suffixes
    if is_overload_constant_list(suffixes):
        feaps__dobp = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        feaps__dobp = suffixes.value
    suffix_x = feaps__dobp[0]
    suffix_y = feaps__dobp[1]
    poj__yrp = 'def _impl(left, right, on=None, left_on=None, right_on=None,\n'
    poj__yrp += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    poj__yrp += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    poj__yrp += "    allow_exact_matches=True, direction='backward'):\n"
    poj__yrp += '  suffix_x = suffixes[0]\n'
    poj__yrp += '  suffix_y = suffixes[1]\n'
    poj__yrp += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo}, minem__dyhx)
    _impl = minem__dyhx['_impl']
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
    inu__venp = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    xryw__rnab = dict(sort=False, group_keys=True, squeeze=False, observed=True
        )
    check_unsupported_args('Dataframe.groupby', inu__venp, xryw__rnab,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    pdzzb__dcnl = func_name == 'DataFrame.pivot_table'
    if pdzzb__dcnl:
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
    rnxp__iflvn = get_literal_value(columns)
    if isinstance(rnxp__iflvn, (list, tuple)):
        if len(rnxp__iflvn) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {rnxp__iflvn}"
                )
        rnxp__iflvn = rnxp__iflvn[0]
    if rnxp__iflvn not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {rnxp__iflvn} not found in DataFrame {df}."
            )
    trat__trl = df.column_index[rnxp__iflvn]
    if is_overload_none(index):
        seh__tvzd = []
        gqbp__lfrky = []
    else:
        gqbp__lfrky = get_literal_value(index)
        if not isinstance(gqbp__lfrky, (list, tuple)):
            gqbp__lfrky = [gqbp__lfrky]
        seh__tvzd = []
        for index in gqbp__lfrky:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            seh__tvzd.append(df.column_index[index])
    if not (all(isinstance(wzxif__doz, int) for wzxif__doz in gqbp__lfrky) or
        all(isinstance(wzxif__doz, str) for wzxif__doz in gqbp__lfrky)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        zkhwf__umer = []
        xfhew__gavz = []
        debte__vpzkt = seh__tvzd + [trat__trl]
        for i, wzxif__doz in enumerate(df.columns):
            if i not in debte__vpzkt:
                zkhwf__umer.append(i)
                xfhew__gavz.append(wzxif__doz)
    else:
        xfhew__gavz = get_literal_value(values)
        if not isinstance(xfhew__gavz, (list, tuple)):
            xfhew__gavz = [xfhew__gavz]
        zkhwf__umer = []
        for val in xfhew__gavz:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            zkhwf__umer.append(df.column_index[val])
    omhkt__dedak = set(zkhwf__umer) | set(seh__tvzd) | {trat__trl}
    if len(omhkt__dedak) != len(zkhwf__umer) + len(seh__tvzd) + 1:
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
    if len(seh__tvzd) == 0:
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
        for ibipg__dtti in seh__tvzd:
            index_column = df.data[ibipg__dtti]
            check_valid_index_typ(index_column)
    jbz__naz = df.data[trat__trl]
    if isinstance(jbz__naz, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(jbz__naz, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for enw__ipod in zkhwf__umer:
        akdv__xkz = df.data[enw__ipod]
        if isinstance(akdv__xkz, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or akdv__xkz == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (gqbp__lfrky, rnxp__iflvn, xfhew__gavz, seh__tvzd, trat__trl,
        zkhwf__umer)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (gqbp__lfrky, rnxp__iflvn, xfhew__gavz, ibipg__dtti, trat__trl,
        zdzrk__pnbhm) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot'))
    if len(gqbp__lfrky) == 0:
        if is_overload_none(data.index.name_typ):
            hwkf__nvtpg = None,
        else:
            hwkf__nvtpg = get_literal_value(data.index.name_typ),
    else:
        hwkf__nvtpg = tuple(gqbp__lfrky)
    gqbp__lfrky = ColNamesMetaType(hwkf__nvtpg)
    xfhew__gavz = ColNamesMetaType(tuple(xfhew__gavz))
    rnxp__iflvn = ColNamesMetaType((rnxp__iflvn,))
    poj__yrp = 'def impl(data, index=None, columns=None, values=None):\n'
    poj__yrp += "    ev = tracing.Event('df.pivot')\n"
    poj__yrp += f'    pivot_values = data.iloc[:, {trat__trl}].unique()\n'
    poj__yrp += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(ibipg__dtti) == 0:
        poj__yrp += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        poj__yrp += '        (\n'
        for gma__qlwi in ibipg__dtti:
            poj__yrp += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {gma__qlwi}),
"""
        poj__yrp += '        ),\n'
    poj__yrp += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {trat__trl}),),
"""
    poj__yrp += '        (\n'
    for enw__ipod in zdzrk__pnbhm:
        poj__yrp += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {enw__ipod}),
"""
    poj__yrp += '        ),\n'
    poj__yrp += '        pivot_values,\n'
    poj__yrp += '        index_lit,\n'
    poj__yrp += '        columns_lit,\n'
    poj__yrp += '        values_lit,\n'
    poj__yrp += '    )\n'
    poj__yrp += '    ev.finalize()\n'
    poj__yrp += '    return result\n'
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo, 'index_lit': gqbp__lfrky, 'columns_lit':
        rnxp__iflvn, 'values_lit': xfhew__gavz, 'tracing': tracing},
        minem__dyhx)
    impl = minem__dyhx['impl']
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
    inu__venp = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    tisnf__uro = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (gqbp__lfrky, rnxp__iflvn, xfhew__gavz, ibipg__dtti, trat__trl,
        zdzrk__pnbhm) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    veu__piuyp = gqbp__lfrky
    gqbp__lfrky = ColNamesMetaType(tuple(gqbp__lfrky))
    xfhew__gavz = ColNamesMetaType(tuple(xfhew__gavz))
    otzy__nnud = rnxp__iflvn
    rnxp__iflvn = ColNamesMetaType((rnxp__iflvn,))
    poj__yrp = 'def impl(\n'
    poj__yrp += '    data,\n'
    poj__yrp += '    values=None,\n'
    poj__yrp += '    index=None,\n'
    poj__yrp += '    columns=None,\n'
    poj__yrp += '    aggfunc="mean",\n'
    poj__yrp += '    fill_value=None,\n'
    poj__yrp += '    margins=False,\n'
    poj__yrp += '    dropna=True,\n'
    poj__yrp += '    margins_name="All",\n'
    poj__yrp += '    observed=False,\n'
    poj__yrp += '    sort=True,\n'
    poj__yrp += '    _pivot_values=None,\n'
    poj__yrp += '):\n'
    poj__yrp += "    ev = tracing.Event('df.pivot_table')\n"
    yght__yxb = ibipg__dtti + [trat__trl] + zdzrk__pnbhm
    poj__yrp += f'    data = data.iloc[:, {yght__yxb}]\n'
    ktged__nuy = veu__piuyp + [otzy__nnud]
    if not is_overload_none(_pivot_values):
        iph__sfqbb = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(iph__sfqbb)
        poj__yrp += '    pivot_values = _pivot_values_arr\n'
        poj__yrp += (
            f'    data = data[data.iloc[:, {len(ibipg__dtti)}].isin(pivot_values)]\n'
            )
        if all(isinstance(wzxif__doz, str) for wzxif__doz in iph__sfqbb):
            socv__nrqs = pd.array(iph__sfqbb, 'string')
        elif all(isinstance(wzxif__doz, int) for wzxif__doz in iph__sfqbb):
            socv__nrqs = np.array(iph__sfqbb, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        socv__nrqs = None
    ysp__tjj = is_overload_constant_str(aggfunc) and get_overload_const_str(
        aggfunc) == 'nunique'
    wsun__tqh = len(ktged__nuy) if ysp__tjj else len(veu__piuyp)
    poj__yrp += f"""    data = data.groupby({ktged__nuy!r}, as_index=False, _bodo_num_shuffle_keys={wsun__tqh}).agg(aggfunc)
"""
    if is_overload_none(_pivot_values):
        poj__yrp += (
            f'    pivot_values = data.iloc[:, {len(ibipg__dtti)}].unique()\n')
    poj__yrp += '    result = bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    poj__yrp += '        (\n'
    for i in range(0, len(ibipg__dtti)):
        poj__yrp += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    poj__yrp += '        ),\n'
    poj__yrp += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(ibipg__dtti)}),),
"""
    poj__yrp += '        (\n'
    for i in range(len(ibipg__dtti) + 1, len(zdzrk__pnbhm) + len(
        ibipg__dtti) + 1):
        poj__yrp += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    poj__yrp += '        ),\n'
    poj__yrp += '        pivot_values,\n'
    poj__yrp += '        index_lit,\n'
    poj__yrp += '        columns_lit,\n'
    poj__yrp += '        values_lit,\n'
    poj__yrp += '        check_duplicates=False,\n'
    poj__yrp += f'        is_already_shuffled={not ysp__tjj},\n'
    poj__yrp += '        _constant_pivot_values=_constant_pivot_values,\n'
    poj__yrp += '    )\n'
    poj__yrp += '    ev.finalize()\n'
    poj__yrp += '    return result\n'
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo, 'numba': numba, 'index_lit': gqbp__lfrky,
        'columns_lit': rnxp__iflvn, 'values_lit': xfhew__gavz,
        '_pivot_values_arr': socv__nrqs, '_constant_pivot_values':
        _pivot_values, 'tracing': tracing}, minem__dyhx)
    impl = minem__dyhx['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    inu__venp = dict(col_level=col_level, ignore_index=ignore_index)
    tisnf__uro = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', inu__venp, tisnf__uro,
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
    yyu__khidr = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(yyu__khidr, (list, tuple)):
        yyu__khidr = [yyu__khidr]
    for wzxif__doz in yyu__khidr:
        if wzxif__doz not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {wzxif__doz} not found in {frame}."
                )
    dqf__dfoz = [frame.column_index[i] for i in yyu__khidr]
    if is_overload_none(value_vars):
        unhdv__wnk = []
        giyjk__hxj = []
        for i, wzxif__doz in enumerate(frame.columns):
            if i not in dqf__dfoz:
                unhdv__wnk.append(i)
                giyjk__hxj.append(wzxif__doz)
    else:
        giyjk__hxj = get_literal_value(value_vars)
        if not isinstance(giyjk__hxj, (list, tuple)):
            giyjk__hxj = [giyjk__hxj]
        giyjk__hxj = [v for v in giyjk__hxj if v not in yyu__khidr]
        if not giyjk__hxj:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        unhdv__wnk = []
        for val in giyjk__hxj:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            unhdv__wnk.append(frame.column_index[val])
    for wzxif__doz in giyjk__hxj:
        if wzxif__doz not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {wzxif__doz} not found in {frame}."
                )
    if not (all(isinstance(wzxif__doz, int) for wzxif__doz in giyjk__hxj) or
        all(isinstance(wzxif__doz, str) for wzxif__doz in giyjk__hxj)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    jvcd__rlerp = frame.data[unhdv__wnk[0]]
    umfq__scugj = [frame.data[i].dtype for i in unhdv__wnk]
    unhdv__wnk = np.array(unhdv__wnk, dtype=np.int64)
    dqf__dfoz = np.array(dqf__dfoz, dtype=np.int64)
    _, cjmry__imoj = bodo.utils.typing.get_common_scalar_dtype(umfq__scugj)
    if not cjmry__imoj:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': giyjk__hxj, 'val_type': jvcd__rlerp
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
    if frame.is_table_format and all(v == jvcd__rlerp.dtype for v in
        umfq__scugj):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            unhdv__wnk))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(giyjk__hxj) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {unhdv__wnk[0]})
"""
    else:
        xan__onaq = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in unhdv__wnk)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({xan__onaq},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in dqf__dfoz:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(giyjk__hxj)})\n'
            )
    afogl__errn = ', '.join(f'out_id{i}' for i in dqf__dfoz) + (', ' if len
        (dqf__dfoz) > 0 else '')
    data_args = afogl__errn + 'var_col, val_col'
    columns = tuple(yyu__khidr + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(giyjk__hxj)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    inu__venp = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    tisnf__uro = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', inu__venp, tisnf__uro,
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
    inu__venp = dict(ignore_index=ignore_index, key=key)
    tisnf__uro = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', inu__venp, tisnf__uro,
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
    ikd__kjfaq = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        ikd__kjfaq.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        eocz__cop = [get_overload_const_tuple(by)]
    else:
        eocz__cop = get_overload_const_list(by)
    eocz__cop = set((k, '') if (k, '') in ikd__kjfaq else k for k in eocz__cop)
    if len(eocz__cop.difference(ikd__kjfaq)) > 0:
        xyka__qmxd = list(set(get_overload_const_list(by)).difference(
            ikd__kjfaq))
        raise_bodo_error(f'sort_values(): invalid keys {xyka__qmxd} for by.')
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
        mwxx__tyk = get_overload_const_list(na_position)
        for na_position in mwxx__tyk:
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
    inu__venp = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    tisnf__uro = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', inu__venp, tisnf__uro,
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
    poj__yrp = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    gru__scpyp = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(gru__scpyp))
    for i in range(gru__scpyp):
        poj__yrp += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(poj__yrp, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    inu__venp = dict(limit=limit, downcast=downcast)
    tisnf__uro = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', inu__venp, tisnf__uro,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    zlsp__ohocy = not is_overload_none(value)
    vgd__knilz = not is_overload_none(method)
    if zlsp__ohocy and vgd__knilz:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not zlsp__ohocy and not vgd__knilz:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if zlsp__ohocy:
        yqaxr__klr = 'value=value'
    else:
        yqaxr__klr = 'method=method'
    data_args = [(
        f"df['{wzxif__doz}'].fillna({yqaxr__klr}, inplace=inplace)" if
        isinstance(wzxif__doz, str) else
        f'df[{wzxif__doz}].fillna({yqaxr__klr}, inplace=inplace)') for
        wzxif__doz in df.columns]
    poj__yrp = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        poj__yrp += '  ' + '  \n'.join(data_args) + '\n'
        minem__dyhx = {}
        exec(poj__yrp, {}, minem__dyhx)
        impl = minem__dyhx['impl']
        return impl
    else:
        return _gen_init_df(poj__yrp, df.columns, ', '.join(qbgwd__ccezu +
            '.values' for qbgwd__ccezu in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    inu__venp = dict(col_level=col_level, col_fill=col_fill)
    tisnf__uro = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', inu__venp, tisnf__uro,
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
    poj__yrp = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    poj__yrp += (
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
        gujzn__suxw = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            gujzn__suxw)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            poj__yrp += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            rdrwt__tchw = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = rdrwt__tchw + data_args
        else:
            fotzq__fen = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [fotzq__fen] + data_args
    return _gen_init_df(poj__yrp, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    grr__jsblg = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and grr__jsblg == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(grr__jsblg))


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
        yvztc__imis = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        wvx__mzimv = get_overload_const_list(subset)
        yvztc__imis = []
        for tndln__cxjn in wvx__mzimv:
            if tndln__cxjn not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{tndln__cxjn}' not in data frame columns {df}"
                    )
            yvztc__imis.append(df.column_index[tndln__cxjn])
    gru__scpyp = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(gru__scpyp))
    poj__yrp = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(gru__scpyp):
        poj__yrp += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    poj__yrp += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in yvztc__imis)))
    poj__yrp += '  index = bodo.utils.conversion.index_from_array(index_arr)\n'
    return _gen_init_df(poj__yrp, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    inu__venp = dict(index=index, level=level, errors=errors)
    tisnf__uro = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', inu__venp, tisnf__uro,
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
            nzy__cxw = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            nzy__cxw = get_overload_const_list(labels)
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
            nzy__cxw = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            nzy__cxw = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for wzxif__doz in nzy__cxw:
        if wzxif__doz not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(wzxif__doz, df.columns))
    if len(set(nzy__cxw)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    nkrmp__aleic = tuple(wzxif__doz for wzxif__doz in df.columns if 
        wzxif__doz not in nzy__cxw)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[wzxif__doz], '.copy()' if not inplace else
        '') for wzxif__doz in nkrmp__aleic)
    poj__yrp = 'def impl(df, labels=None, axis=0, index=None, columns=None,\n'
    poj__yrp += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(poj__yrp, nkrmp__aleic, data_args, index)


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
    inu__venp = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    fud__vnmrv = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', inu__venp, fud__vnmrv,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    gru__scpyp = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(gru__scpyp))
    mqf__jifpp = ', '.join('rhs_data_{}'.format(i) for i in range(gru__scpyp))
    poj__yrp = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    poj__yrp += '  if (frac == 1 or n == len(df)) and not replace:\n'
    poj__yrp += '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n'
    for i in range(gru__scpyp):
        poj__yrp += (
            '  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    poj__yrp += '  if frac is None:\n'
    poj__yrp += '    frac_d = -1.0\n'
    poj__yrp += '  else:\n'
    poj__yrp += '    frac_d = frac\n'
    poj__yrp += '  if n is None:\n'
    poj__yrp += '    n_i = 0\n'
    poj__yrp += '  else:\n'
    poj__yrp += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    poj__yrp += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({mqf__jifpp},), {index}, n_i, frac_d, replace)
"""
    poj__yrp += '  index = bodo.utils.conversion.index_from_array(index_arr)\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(poj__yrp, df.columns,
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
    tbzw__lqlan = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    dym__gpxcp = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', tbzw__lqlan, dym__gpxcp,
        package_name='pandas', module_name='DataFrame')
    kboj__pqino = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            qfp__uas = kboj__pqino + '\n'
            qfp__uas += 'Index: 0 entries\n'
            qfp__uas += 'Empty DataFrame'
            print(qfp__uas)
        return _info_impl
    else:
        poj__yrp = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        poj__yrp += '    ncols = df.shape[1]\n'
        poj__yrp += f'    lines = "{kboj__pqino}\\n"\n'
        poj__yrp += f'    lines += "{df.index}: "\n'
        poj__yrp += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            poj__yrp += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            poj__yrp += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            poj__yrp += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        poj__yrp += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        poj__yrp += f'    space = {max(len(str(k)) for k in df.columns) + 1}\n'
        poj__yrp += '    column_width = max(space, 7)\n'
        poj__yrp += '    column= "Column"\n'
        poj__yrp += '    underl= "------"\n'
        poj__yrp += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        poj__yrp += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        poj__yrp += '    mem_size = 0\n'
        poj__yrp += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        poj__yrp += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        poj__yrp += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        wqm__ngzcc = dict()
        for i in range(len(df.columns)):
            poj__yrp += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            red__laues = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                red__laues = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                tphs__vhgn = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                red__laues = f'{tphs__vhgn[:-7]}'
            poj__yrp += f'    col_dtype[{i}] = "{red__laues}"\n'
            if red__laues in wqm__ngzcc:
                wqm__ngzcc[red__laues] += 1
            else:
                wqm__ngzcc[red__laues] = 1
            poj__yrp += f'    col_name[{i}] = "{df.columns[i]}"\n'
            poj__yrp += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        poj__yrp += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        poj__yrp += '    for i in column_info:\n'
        poj__yrp += "        lines += f'{i}\\n'\n"
        teu__xwf = ', '.join(f'{k}({wqm__ngzcc[k]})' for k in sorted(
            wqm__ngzcc))
        poj__yrp += f"    lines += 'dtypes: {teu__xwf}\\n'\n"
        poj__yrp += '    mem_size += df.index.nbytes\n'
        poj__yrp += '    total_size = _sizeof_fmt(mem_size)\n'
        poj__yrp += "    lines += f'memory usage: {total_size}'\n"
        poj__yrp += '    print(lines)\n'
        minem__dyhx = {}
        exec(poj__yrp, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo': bodo,
            'np': np}, minem__dyhx)
        _info_impl = minem__dyhx['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    poj__yrp = 'def impl(df, index=True, deep=False):\n'
    nuc__ftlm = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes'
    lvslc__nzudw = is_overload_true(index)
    columns = df.columns
    if lvslc__nzudw:
        columns = ('Index',) + columns
    if len(columns) == 0:
        cyws__hzn = ()
    elif all(isinstance(wzxif__doz, int) for wzxif__doz in columns):
        cyws__hzn = np.array(columns, 'int64')
    elif all(isinstance(wzxif__doz, str) for wzxif__doz in columns):
        cyws__hzn = pd.array(columns, 'string')
    else:
        cyws__hzn = columns
    if df.is_table_format and len(df.columns) > 0:
        ahjjb__xgqiy = int(lvslc__nzudw)
        dirh__ytyp = len(columns)
        poj__yrp += f'  nbytes_arr = np.empty({dirh__ytyp}, np.int64)\n'
        poj__yrp += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        poj__yrp += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {ahjjb__xgqiy})
"""
        if lvslc__nzudw:
            poj__yrp += f'  nbytes_arr[0] = {nuc__ftlm}\n'
        poj__yrp += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if lvslc__nzudw:
            data = f'{nuc__ftlm},{data}'
        else:
            jtu__efj = ',' if len(columns) == 1 else ''
            data = f'{data}{jtu__efj}'
        poj__yrp += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        cyws__hzn}, minem__dyhx)
    impl = minem__dyhx['impl']
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
    yryt__kilib = 'read_excel_df{}'.format(next_label())
    setattr(types, yryt__kilib, df_type)
    epzy__gxym = False
    if is_overload_constant_list(parse_dates):
        epzy__gxym = get_overload_const_list(parse_dates)
    zpezs__lqtah = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    poj__yrp = f"""
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
    with numba.objmode(df="{yryt__kilib}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{zpezs__lqtah}}},
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
            parse_dates={epzy__gxym},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    minem__dyhx = {}
    exec(poj__yrp, globals(), minem__dyhx)
    impl = minem__dyhx['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as fthel__sqrmu:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    poj__yrp = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    poj__yrp += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    poj__yrp += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        poj__yrp += '   fig, ax = plt.subplots()\n'
    else:
        poj__yrp += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        poj__yrp += '   fig.set_figwidth(figsize[0])\n'
        poj__yrp += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        poj__yrp += '   xlabel = x\n'
    poj__yrp += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        poj__yrp += '   ylabel = y\n'
    else:
        poj__yrp += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        poj__yrp += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        poj__yrp += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    poj__yrp += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            poj__yrp += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            jjkiu__dhpn = get_overload_const_str(x)
            yhe__yhysq = df.columns.index(jjkiu__dhpn)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if yhe__yhysq != i:
                        poj__yrp += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            poj__yrp += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        poj__yrp += '   ax.scatter(df[x], df[y], s=20)\n'
        poj__yrp += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        poj__yrp += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        poj__yrp += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        poj__yrp += '   ax.legend()\n'
    poj__yrp += '   return ax\n'
    minem__dyhx = {}
    exec(poj__yrp, {'bodo': bodo, 'plt': plt}, minem__dyhx)
    impl = minem__dyhx['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for wenf__sdlw in df_typ.data:
        if not (isinstance(wenf__sdlw, IntegerArrayType) or isinstance(
            wenf__sdlw.dtype, types.Number) or wenf__sdlw.dtype in (bodo.
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
        ltw__cne = args[0]
        bmf__tns = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        yhwu__pbqk = ltw__cne
        check_runtime_cols_unsupported(ltw__cne, 'set_df_col()')
        if isinstance(ltw__cne, DataFrameType):
            index = ltw__cne.index
            if len(ltw__cne.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(ltw__cne.columns) == 0:
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
            if bmf__tns in ltw__cne.columns:
                nkrmp__aleic = ltw__cne.columns
                ylhx__aimlx = ltw__cne.columns.index(bmf__tns)
                rqz__uyac = list(ltw__cne.data)
                rqz__uyac[ylhx__aimlx] = val
                rqz__uyac = tuple(rqz__uyac)
            else:
                nkrmp__aleic = ltw__cne.columns + (bmf__tns,)
                rqz__uyac = ltw__cne.data + (val,)
            yhwu__pbqk = DataFrameType(rqz__uyac, index, nkrmp__aleic,
                ltw__cne.dist, ltw__cne.is_table_format)
        return yhwu__pbqk(*args)


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
        ube__gfkn = args[0]
        assert isinstance(ube__gfkn, DataFrameType) and len(ube__gfkn.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        ovlrq__asge = args[2]
        assert len(col_names_to_replace) == len(ovlrq__asge
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(ube__gfkn.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in ube__gfkn.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(ube__gfkn,
            '__bodosql_replace_columns_dummy()')
        index = ube__gfkn.index
        nkrmp__aleic = ube__gfkn.columns
        rqz__uyac = list(ube__gfkn.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            ibdm__pbpxy = ovlrq__asge[i]
            assert isinstance(ibdm__pbpxy, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(ibdm__pbpxy, SeriesType):
                ibdm__pbpxy = ibdm__pbpxy.data
            yhih__nuulp = ube__gfkn.column_index[col_name]
            rqz__uyac[yhih__nuulp] = ibdm__pbpxy
        rqz__uyac = tuple(rqz__uyac)
        yhwu__pbqk = DataFrameType(rqz__uyac, index, nkrmp__aleic,
            ube__gfkn.dist, ube__gfkn.is_table_format)
        return yhwu__pbqk(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    dyrh__jzm = {}

    def _rewrite_membership_op(self, node, left, right):
        zqa__sst = node.op
        op = self.visit(zqa__sst)
        return op, zqa__sst, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    wjmvc__kuih = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in wjmvc__kuih:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in wjmvc__kuih:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        ogcy__dod = node.attr
        value = node.value
        ofa__adl = pd.core.computation.ops.LOCAL_TAG
        if ogcy__dod in ('str', 'dt'):
            try:
                mhdyn__fadi = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as bfgb__ata:
                col_name = bfgb__ata.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            mhdyn__fadi = str(self.visit(value))
        zwtpp__hpj = mhdyn__fadi, ogcy__dod
        if zwtpp__hpj in join_cleaned_cols:
            ogcy__dod = join_cleaned_cols[zwtpp__hpj]
        name = mhdyn__fadi + '.' + ogcy__dod
        if name.startswith(ofa__adl):
            name = name[len(ofa__adl):]
        if ogcy__dod in ('str', 'dt'):
            snee__qqw = columns[cleaned_columns.index(mhdyn__fadi)]
            dyrh__jzm[snee__qqw] = mhdyn__fadi
            self.env.scope[name] = 0
            return self.term_type(ofa__adl + name, self.env)
        wjmvc__kuih.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in wjmvc__kuih:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        qfd__bnv = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        bmf__tns = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(qfd__bnv), bmf__tns))

    def op__str__(self):
        ohps__usal = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            rzm__dydw)) for rzm__dydw in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(ohps__usal)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(ohps__usal)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(ohps__usal))
    ahxsw__hydou = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    tszmq__otz = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    lfcl__nxt = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    aediz__xzvc = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    txk__xos = pd.core.computation.ops.Term.__str__
    gcl__gik = pd.core.computation.ops.MathCall.__str__
    iohq__qxsud = pd.core.computation.ops.Op.__str__
    ajc__tvxgx = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        xdx__ofkfe = pd.core.computation.expr.Expr(expr, env=env)
        rqfe__pmz = str(xdx__ofkfe)
    except pd.core.computation.ops.UndefinedVariableError as bfgb__ata:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == bfgb__ata.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {bfgb__ata}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            ahxsw__hydou)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            tszmq__otz)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = lfcl__nxt
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = aediz__xzvc
        pd.core.computation.ops.Term.__str__ = txk__xos
        pd.core.computation.ops.MathCall.__str__ = gcl__gik
        pd.core.computation.ops.Op.__str__ = iohq__qxsud
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            ajc__tvxgx)
    pctj__nxkfp = pd.core.computation.parsing.clean_column_name
    dyrh__jzm.update({wzxif__doz: pctj__nxkfp(wzxif__doz) for wzxif__doz in
        columns if pctj__nxkfp(wzxif__doz) in xdx__ofkfe.names})
    return xdx__ofkfe, rqfe__pmz, dyrh__jzm


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        pix__maul = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(pix__maul))
        gzu__xpu = namedtuple('Pandas', col_names)
        peg__qibp = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], gzu__xpu)
        super(DataFrameTupleIterator, self).__init__(name, peg__qibp)

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
        xqyyn__arr = [if_series_to_array_type(a) for a in args[len(args) // 2:]
            ]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        xqyyn__arr = [types.Array(types.int64, 1, 'C')] + xqyyn__arr
        ifs__ztdh = DataFrameTupleIterator(col_names, xqyyn__arr)
        return ifs__ztdh(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fvio__fpvgb = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            fvio__fpvgb)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    kbawm__xjogi = args[len(args) // 2:]
    nrt__lylgq = sig.args[len(sig.args) // 2:]
    nhhbd__bxlh = context.make_helper(builder, sig.return_type)
    fdt__laofm = context.get_constant(types.intp, 0)
    loxd__iba = cgutils.alloca_once_value(builder, fdt__laofm)
    nhhbd__bxlh.index = loxd__iba
    for i, arr in enumerate(kbawm__xjogi):
        setattr(nhhbd__bxlh, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(kbawm__xjogi, nrt__lylgq):
        context.nrt.incref(builder, arr_typ, arr)
    res = nhhbd__bxlh._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    sthqd__waffe, = sig.args
    raw__sxqy, = args
    nhhbd__bxlh = context.make_helper(builder, sthqd__waffe, value=raw__sxqy)
    tmpf__cgxf = signature(types.intp, sthqd__waffe.array_types[1])
    zbpa__kgf = context.compile_internal(builder, lambda a: len(a),
        tmpf__cgxf, [nhhbd__bxlh.array0])
    index = builder.load(nhhbd__bxlh.index)
    aksm__pmh = builder.icmp_signed('<', index, zbpa__kgf)
    result.set_valid(aksm__pmh)
    with builder.if_then(aksm__pmh):
        values = [index]
        for i, arr_typ in enumerate(sthqd__waffe.array_types[1:]):
            stn__ohnn = getattr(nhhbd__bxlh, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                kbz__lmjpq = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    kbz__lmjpq, [stn__ohnn, index])
            else:
                kbz__lmjpq = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    kbz__lmjpq, [stn__ohnn, index])
            values.append(val)
        value = context.make_tuple(builder, sthqd__waffe.yield_type, values)
        result.yield_(value)
        srdl__slkz = cgutils.increment_index(builder, index)
        builder.store(srdl__slkz, nhhbd__bxlh.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    cmp__wygg = ir.Assign(rhs, lhs, expr.loc)
    olg__gqca = lhs
    uys__eszi = []
    igpb__zpkj = []
    man__yyz = typ.count
    for i in range(man__yyz):
        zrkix__dwonj = ir.Var(olg__gqca.scope, mk_unique_var('{}_size{}'.
            format(olg__gqca.name, i)), olg__gqca.loc)
        qnumj__qdyfd = ir.Expr.static_getitem(lhs, i, None, olg__gqca.loc)
        self.calltypes[qnumj__qdyfd] = None
        uys__eszi.append(ir.Assign(qnumj__qdyfd, zrkix__dwonj, olg__gqca.loc))
        self._define(equiv_set, zrkix__dwonj, types.intp, qnumj__qdyfd)
        igpb__zpkj.append(zrkix__dwonj)
    pcm__cfe = tuple(igpb__zpkj)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        pcm__cfe, pre=[cmp__wygg] + uys__eszi)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
