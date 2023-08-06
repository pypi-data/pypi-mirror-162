"""
Implementation of Series attributes and methods using overload.
"""
import operator
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, overload_attribute, overload_method, register_jitable
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, datetime_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_offsets_ext import is_offsets_type
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType, if_series_to_array_type, is_series_type
from bodo.hiframes.pd_timestamp_ext import PandasTimestampType, pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.transform import is_var_size_item_array_type
from bodo.utils.typing import BodoError, ColNamesMetaType, can_replace, check_unsupported_args, dtype_to_array_type, element_type, get_common_scalar_dtype, get_index_names, get_literal_value, get_overload_const_bytes, get_overload_const_int, get_overload_const_str, is_common_scalar_dtype, is_iterable_type, is_literal_type, is_nullable_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_bytes, is_overload_constant_int, is_overload_constant_nan, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, is_str_arr_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array


@overload_attribute(HeterogeneousSeriesType, 'index', inline='always')
@overload_attribute(SeriesType, 'index', inline='always')
def overload_series_index(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_index(s)


@overload_attribute(HeterogeneousSeriesType, 'values', inline='always')
@overload_attribute(SeriesType, 'values', inline='always')
def overload_series_values(s):
    if isinstance(s.data, bodo.DatetimeArrayType):

        def impl(s):
            lqv__wjceq = bodo.hiframes.pd_series_ext.get_series_data(s)
            bln__crlsa = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                lqv__wjceq)
            return bln__crlsa
        return impl
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s)


@overload_attribute(SeriesType, 'dtype', inline='always')
def overload_series_dtype(s):
    if s.dtype == bodo.string_type:
        raise BodoError('Series.dtype not supported for string Series yet')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s, 'Series.dtype'
        )
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s).dtype


@overload_attribute(HeterogeneousSeriesType, 'shape')
@overload_attribute(SeriesType, 'shape')
def overload_series_shape(s):
    return lambda s: (len(bodo.hiframes.pd_series_ext.get_series_data(s)),)


@overload_attribute(HeterogeneousSeriesType, 'ndim', inline='always')
@overload_attribute(SeriesType, 'ndim', inline='always')
def overload_series_ndim(s):
    return lambda s: 1


@overload_attribute(HeterogeneousSeriesType, 'size')
@overload_attribute(SeriesType, 'size')
def overload_series_size(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s))


@overload_attribute(HeterogeneousSeriesType, 'T', inline='always')
@overload_attribute(SeriesType, 'T', inline='always')
def overload_series_T(s):
    return lambda s: s


@overload_attribute(SeriesType, 'hasnans', inline='always')
def overload_series_hasnans(s):
    return lambda s: s.isna().sum() != 0


@overload_attribute(HeterogeneousSeriesType, 'empty')
@overload_attribute(SeriesType, 'empty')
def overload_series_empty(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s)) == 0


@overload_attribute(SeriesType, 'dtypes', inline='always')
def overload_series_dtypes(s):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s,
        'Series.dtypes')
    return lambda s: s.dtype


@overload_attribute(HeterogeneousSeriesType, 'name', inline='always')
@overload_attribute(SeriesType, 'name', inline='always')
def overload_series_name(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_name(s)


@overload(len, no_unliteral=True)
def overload_series_len(S):
    if isinstance(S, (SeriesType, HeterogeneousSeriesType)):
        return lambda S: len(bodo.hiframes.pd_series_ext.get_series_data(S))


@overload_method(SeriesType, 'copy', inline='always', no_unliteral=True)
def overload_series_copy(S, deep=True):
    if is_overload_true(deep):

        def impl1(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr.copy(),
                index, name)
        return impl1
    if is_overload_false(deep):

        def impl2(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl2

    def impl(S, deep=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        if deep:
            arr = arr.copy()
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'to_list', no_unliteral=True)
@overload_method(SeriesType, 'tolist', no_unliteral=True)
def overload_series_to_list(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.tolist()')
    if isinstance(S.dtype, types.Float):

        def impl_float(S):
            sjywx__nars = list()
            for orq__botb in range(len(S)):
                sjywx__nars.append(S.iat[orq__botb])
            return sjywx__nars
        return impl_float

    def impl(S):
        sjywx__nars = list()
        for orq__botb in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, orq__botb):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            sjywx__nars.append(S.iat[orq__botb])
        return sjywx__nars
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    iphg__sqqz = dict(dtype=dtype, copy=copy, na_value=na_value)
    qzu__yrnkk = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    iphg__sqqz = dict(name=name, inplace=inplace)
    qzu__yrnkk = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not bodo.hiframes.dataframe_impl._is_all_levels(S, level):
        raise_bodo_error(
            'Series.reset_index(): only dropping all index levels supported')
    if not is_overload_constant_bool(drop):
        raise_bodo_error(
            "Series.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if is_overload_true(drop):

        def impl_drop(S, level=None, drop=False, name=None, inplace=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_index_ext.init_range_index(0, len(arr),
                1, None)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl_drop

    def get_name_literal(name_typ, is_index=False, series_name=None):
        if is_overload_none(name_typ):
            if is_index:
                return 'index' if series_name != 'index' else 'level_0'
            return 0
        if is_literal_type(name_typ):
            return get_literal_value(name_typ)
        else:
            raise BodoError(
                'Series.reset_index() not supported for non-literal series names'
                )
    series_name = get_name_literal(S.name_typ)
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        gdb__jnoe = ', '.join(['index_arrs[{}]'.format(orq__botb) for
            orq__botb in range(S.index.nlevels)])
    else:
        gdb__jnoe = '    bodo.utils.conversion.index_to_array(index)\n'
    ushps__jzjy = 'index' if 'index' != series_name else 'level_0'
    oybf__vbyxa = get_index_names(S.index, 'Series.reset_index()', ushps__jzjy)
    columns = [name for name in oybf__vbyxa]
    columns.append(series_name)
    omi__znhy = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    omi__znhy += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    omi__znhy += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        omi__znhy += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    omi__znhy += (
        '    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)\n'
        )
    omi__znhy += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({gdb__jnoe}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    tjqu__jao = {}
    exec(omi__znhy, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, tjqu__jao)
    dkay__bqdgo = tjqu__jao['_impl']
    return dkay__bqdgo


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.round()')

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        utcwa__nixkv = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for orq__botb in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[orq__botb]):
                bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
            else:
                utcwa__nixkv[orq__botb] = np.round(arr[orq__botb], decimals)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    iphg__sqqz = dict(level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sum(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sum(): skipna argument must be a boolean')
    if not is_overload_int(min_count):
        raise BodoError('Series.sum(): min_count argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sum()'
        )

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_sum(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'prod', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'product', inline='always', no_unliteral=True)
def overload_series_prod(S, axis=None, skipna=True, level=None,
    numeric_only=None, min_count=0):
    iphg__sqqz = dict(level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.product(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.product(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.product()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_prod(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'any', inline='always', no_unliteral=True)
def overload_series_any(S, axis=0, bool_only=None, skipna=True, level=None):
    iphg__sqqz = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=
        level)
    qzu__yrnkk = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.any()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(SeriesType, 'equals', inline='always', no_unliteral=True)
def overload_series_equals(S, other):
    if not isinstance(other, SeriesType):
        raise BodoError("Series.equals() 'other' must be a Series")
    if isinstance(S.data, bodo.ArrayItemArrayType):
        raise BodoError(
            'Series.equals() not supported for Series where each element is an array or list'
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.equals()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.equals()')
    if S.data != other.data:
        return lambda S, other: False

    def impl(S, other):
        jtdg__lfl = bodo.hiframes.pd_series_ext.get_series_data(S)
        ragbc__jxrg = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        yfa__son = 0
        for orq__botb in numba.parfors.parfor.internal_prange(len(jtdg__lfl)):
            qat__sjjny = 0
            exg__uhapl = bodo.libs.array_kernels.isna(jtdg__lfl, orq__botb)
            nrdxv__bink = bodo.libs.array_kernels.isna(ragbc__jxrg, orq__botb)
            if (exg__uhapl and not nrdxv__bink or not exg__uhapl and
                nrdxv__bink):
                qat__sjjny = 1
            elif not exg__uhapl:
                if jtdg__lfl[orq__botb] != ragbc__jxrg[orq__botb]:
                    qat__sjjny = 1
            yfa__son += qat__sjjny
        return yfa__son == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    iphg__sqqz = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=
        level)
    qzu__yrnkk = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    iphg__sqqz = dict(level=level)
    qzu__yrnkk = dict(level=None)
    check_unsupported_args('Series.mad', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    vqh__epu = types.float64
    ezei__epsce = types.float64
    if S.dtype == types.float32:
        vqh__epu = types.float32
        ezei__epsce = types.float32
    wwpcn__ryy = vqh__epu(0)
    ithkq__fxqnd = ezei__epsce(0)
    lqtm__rpfvf = ezei__epsce(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        yez__csog = wwpcn__ryy
        yfa__son = ithkq__fxqnd
        for orq__botb in numba.parfors.parfor.internal_prange(len(A)):
            qat__sjjny = wwpcn__ryy
            sxf__alzyy = ithkq__fxqnd
            if not bodo.libs.array_kernels.isna(A, orq__botb) or not skipna:
                qat__sjjny = A[orq__botb]
                sxf__alzyy = lqtm__rpfvf
            yez__csog += qat__sjjny
            yfa__son += sxf__alzyy
        djtj__nsask = bodo.hiframes.series_kernels._mean_handle_nan(yez__csog,
            yfa__son)
        joo__adjw = wwpcn__ryy
        for orq__botb in numba.parfors.parfor.internal_prange(len(A)):
            qat__sjjny = wwpcn__ryy
            if not bodo.libs.array_kernels.isna(A, orq__botb) or not skipna:
                qat__sjjny = abs(A[orq__botb] - djtj__nsask)
            joo__adjw += qat__sjjny
        entq__dxa = bodo.hiframes.series_kernels._mean_handle_nan(joo__adjw,
            yfa__son)
        return entq__dxa
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    iphg__sqqz = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mean(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.mean()')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_mean(arr)
    return impl


@overload_method(SeriesType, 'sem', inline='always', no_unliteral=True)
def overload_series_sem(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    iphg__sqqz = dict(level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sem(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sem(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.sem(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sem()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        ccou__ocz = 0
        gldk__iev = 0
        yfa__son = 0
        for orq__botb in numba.parfors.parfor.internal_prange(len(A)):
            qat__sjjny = 0
            sxf__alzyy = 0
            if not bodo.libs.array_kernels.isna(A, orq__botb) or not skipna:
                qat__sjjny = A[orq__botb]
                sxf__alzyy = 1
            ccou__ocz += qat__sjjny
            gldk__iev += qat__sjjny * qat__sjjny
            yfa__son += sxf__alzyy
        pdoak__rki = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            ccou__ocz, gldk__iev, yfa__son, ddof)
        riho__bkb = bodo.hiframes.series_kernels._sem_handle_nan(pdoak__rki,
            yfa__son)
        return riho__bkb
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    iphg__sqqz = dict(level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.kurtosis()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        ccou__ocz = 0.0
        gldk__iev = 0.0
        mlfz__qzdt = 0.0
        uer__sxjb = 0.0
        yfa__son = 0
        for orq__botb in numba.parfors.parfor.internal_prange(len(A)):
            qat__sjjny = 0.0
            sxf__alzyy = 0
            if not bodo.libs.array_kernels.isna(A, orq__botb) or not skipna:
                qat__sjjny = np.float64(A[orq__botb])
                sxf__alzyy = 1
            ccou__ocz += qat__sjjny
            gldk__iev += qat__sjjny ** 2
            mlfz__qzdt += qat__sjjny ** 3
            uer__sxjb += qat__sjjny ** 4
            yfa__son += sxf__alzyy
        pdoak__rki = bodo.hiframes.series_kernels.compute_kurt(ccou__ocz,
            gldk__iev, mlfz__qzdt, uer__sxjb, yfa__son)
        return pdoak__rki
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    iphg__sqqz = dict(level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.skew()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        ccou__ocz = 0.0
        gldk__iev = 0.0
        mlfz__qzdt = 0.0
        yfa__son = 0
        for orq__botb in numba.parfors.parfor.internal_prange(len(A)):
            qat__sjjny = 0.0
            sxf__alzyy = 0
            if not bodo.libs.array_kernels.isna(A, orq__botb) or not skipna:
                qat__sjjny = np.float64(A[orq__botb])
                sxf__alzyy = 1
            ccou__ocz += qat__sjjny
            gldk__iev += qat__sjjny ** 2
            mlfz__qzdt += qat__sjjny ** 3
            yfa__son += sxf__alzyy
        pdoak__rki = bodo.hiframes.series_kernels.compute_skew(ccou__ocz,
            gldk__iev, mlfz__qzdt, yfa__son)
        return pdoak__rki
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    iphg__sqqz = dict(level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.var(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.var(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.var(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.var()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_var(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'std', inline='always', no_unliteral=True)
def overload_series_std(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    iphg__sqqz = dict(level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.std(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.std(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.std(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.std()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_std(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'dot', inline='always', no_unliteral=True)
def overload_series_dot(S, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.dot()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.dot()')

    def impl(S, other):
        jtdg__lfl = bodo.hiframes.pd_series_ext.get_series_data(S)
        ragbc__jxrg = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        pdb__pojg = 0
        for orq__botb in numba.parfors.parfor.internal_prange(len(jtdg__lfl)):
            hqqhg__xlri = jtdg__lfl[orq__botb]
            ioumb__ezzy = ragbc__jxrg[orq__botb]
            pdb__pojg += hqqhg__xlri * ioumb__ezzy
        return pdb__pojg
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    iphg__sqqz = dict(skipna=skipna)
    qzu__yrnkk = dict(skipna=True)
    check_unsupported_args('Series.cumsum', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumsum(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumsum()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumsum(), index, name)
    return impl


@overload_method(SeriesType, 'cumprod', inline='always', no_unliteral=True)
def overload_series_cumprod(S, axis=None, skipna=True):
    iphg__sqqz = dict(skipna=skipna)
    qzu__yrnkk = dict(skipna=True)
    check_unsupported_args('Series.cumprod', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumprod(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumprod()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumprod(), index, name
            )
    return impl


@overload_method(SeriesType, 'cummin', inline='always', no_unliteral=True)
def overload_series_cummin(S, axis=None, skipna=True):
    iphg__sqqz = dict(skipna=skipna)
    qzu__yrnkk = dict(skipna=True)
    check_unsupported_args('Series.cummin', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummin(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummin()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummin(arr), index, name)
    return impl


@overload_method(SeriesType, 'cummax', inline='always', no_unliteral=True)
def overload_series_cummax(S, axis=None, skipna=True):
    iphg__sqqz = dict(skipna=skipna)
    qzu__yrnkk = dict(skipna=True)
    check_unsupported_args('Series.cummax', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummax(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummax()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummax(arr), index, name)
    return impl


@overload_method(SeriesType, 'rename', inline='always', no_unliteral=True)
def overload_series_rename(S, index=None, axis=None, copy=True, inplace=
    False, level=None, errors='ignore'):
    if not (index == bodo.string_type or isinstance(index, types.StringLiteral)
        ):
        raise BodoError("Series.rename() 'index' can only be a string")
    iphg__sqqz = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    qzu__yrnkk = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        dwm__dckks = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, dwm__dckks, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    iphg__sqqz = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    qzu__yrnkk = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if is_overload_none(mapper) or not is_scalar_type(mapper):
        raise BodoError(
            "Series.rename_axis(): 'mapper' is required and must be a scalar type."
            )

    def impl(S, mapper=None, index=None, columns=None, axis=None, copy=True,
        inplace=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        index = index.rename(mapper)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'abs', inline='always', no_unliteral=True)
def overload_series_abs(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.abs()'
        )

    def impl(S):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(np.abs(A), index, name)
    return impl


@overload_method(SeriesType, 'count', no_unliteral=True)
def overload_series_count(S, level=None):
    iphg__sqqz = dict(level=level)
    qzu__yrnkk = dict(level=None)
    check_unsupported_args('Series.count', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    iphg__sqqz = dict(method=method, min_periods=min_periods)
    qzu__yrnkk = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        kdn__jxujo = S.sum()
        sknri__xkgel = other.sum()
        a = n * (S * other).sum() - kdn__jxujo * sknri__xkgel
        egg__evysg = n * (S ** 2).sum() - kdn__jxujo ** 2
        brb__fmdoa = n * (other ** 2).sum() - sknri__xkgel ** 2
        return a / np.sqrt(egg__evysg * brb__fmdoa)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    iphg__sqqz = dict(min_periods=min_periods)
    qzu__yrnkk = dict(min_periods=None)
    check_unsupported_args('Series.cov', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        kdn__jxujo = S.mean()
        sknri__xkgel = other.mean()
        dtgug__odzv = ((S - kdn__jxujo) * (other - sknri__xkgel)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(dtgug__odzv, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            strtw__rcmjm = np.sign(sum_val)
            return np.inf * strtw__rcmjm
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    iphg__sqqz = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.min(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.min(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.min()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_min(arr)
    return impl


@overload(max, no_unliteral=True)
def overload_series_builtins_max(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.max()
        return impl


@overload(min, no_unliteral=True)
def overload_series_builtins_min(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.min()
        return impl


@overload(sum, no_unliteral=True)
def overload_series_builtins_sum(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.sum()
        return impl


@overload(np.prod, inline='always', no_unliteral=True)
def overload_series_np_prod(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.prod()
        return impl


@overload_method(SeriesType, 'max', inline='always', no_unliteral=True)
def overload_series_max(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    iphg__sqqz = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.max(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.max(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.max()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_max(arr)
    return impl


@overload_method(SeriesType, 'idxmin', inline='always', no_unliteral=True)
def overload_series_idxmin(S, axis=0, skipna=True):
    iphg__sqqz = dict(axis=axis, skipna=skipna)
    qzu__yrnkk = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmin()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmin() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmin(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmin(arr, index)
    return impl


@overload_method(SeriesType, 'idxmax', inline='always', no_unliteral=True)
def overload_series_idxmax(S, axis=0, skipna=True):
    iphg__sqqz = dict(axis=axis, skipna=skipna)
    qzu__yrnkk = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmax()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmax() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmax(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmax(arr, index)
    return impl


@overload_method(SeriesType, 'infer_objects', inline='always')
def overload_series_infer_objects(S):
    return lambda S: S.copy()


@overload_attribute(SeriesType, 'is_monotonic', inline='always')
@overload_attribute(SeriesType, 'is_monotonic_increasing', inline='always')
def overload_series_is_monotonic_increasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_increasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 1)


@overload_attribute(SeriesType, 'is_monotonic_decreasing', inline='always')
def overload_series_is_monotonic_decreasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_decreasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 2)


@overload_attribute(SeriesType, 'nbytes', inline='always')
def overload_series_nbytes(S):
    return lambda S: bodo.hiframes.pd_series_ext.get_series_data(S).nbytes


@overload_method(SeriesType, 'autocorr', inline='always', no_unliteral=True)
def overload_series_autocorr(S, lag=1):
    return lambda S, lag=1: bodo.libs.array_kernels.autocorr(bodo.hiframes.
        pd_series_ext.get_series_data(S), lag)


@overload_method(SeriesType, 'median', inline='always', no_unliteral=True)
def overload_series_median(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    iphg__sqqz = dict(level=level, numeric_only=numeric_only)
    qzu__yrnkk = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.median(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.median(): skipna argument must be a boolean')
    return (lambda S, axis=None, skipna=True, level=None, numeric_only=None:
        bodo.libs.array_ops.array_op_median(bodo.hiframes.pd_series_ext.
        get_series_data(S), skipna))


def overload_series_head(S, n=5):

    def impl(S, n=5):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        watoe__tfm = arr[:n]
        dud__taoog = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(watoe__tfm,
            dud__taoog, name)
    return impl


@lower_builtin('series.head', SeriesType, types.Integer)
@lower_builtin('series.head', SeriesType, types.Omitted)
def series_head_lower(context, builder, sig, args):
    impl = overload_series_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@numba.extending.register_jitable
def tail_slice(k, n):
    if n == 0:
        return k
    return -n


@overload_method(SeriesType, 'tail', inline='always', no_unliteral=True)
def overload_series_tail(S, n=5):
    if not is_overload_int(n):
        raise BodoError("Series.tail(): 'n' must be an Integer")

    def impl(S, n=5):
        bsi__dok = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        watoe__tfm = arr[bsi__dok:]
        dud__taoog = index[bsi__dok:]
        return bodo.hiframes.pd_series_ext.init_series(watoe__tfm,
            dud__taoog, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    ozpx__rygzn = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ozpx__rygzn:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            yryrt__oxdqy = index[0]
            ycdn__tvwb = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                yryrt__oxdqy, False))
        else:
            ycdn__tvwb = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        watoe__tfm = arr[:ycdn__tvwb]
        dud__taoog = index[:ycdn__tvwb]
        return bodo.hiframes.pd_series_ext.init_series(watoe__tfm,
            dud__taoog, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    ozpx__rygzn = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ozpx__rygzn:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            kiq__gzr = index[-1]
            ycdn__tvwb = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, kiq__gzr,
                True))
        else:
            ycdn__tvwb = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        watoe__tfm = arr[len(arr) - ycdn__tvwb:]
        dud__taoog = index[len(arr) - ycdn__tvwb:]
        return bodo.hiframes.pd_series_ext.init_series(watoe__tfm,
            dud__taoog, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        czkrq__jty = bodo.utils.conversion.index_to_array(index)
        ptxjd__fdhuj, uxknc__sll = (bodo.libs.array_kernels.
            first_last_valid_index(arr, czkrq__jty))
        return uxknc__sll if ptxjd__fdhuj else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        czkrq__jty = bodo.utils.conversion.index_to_array(index)
        ptxjd__fdhuj, uxknc__sll = (bodo.libs.array_kernels.
            first_last_valid_index(arr, czkrq__jty, False))
        return uxknc__sll if ptxjd__fdhuj else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    iphg__sqqz = dict(keep=keep)
    qzu__yrnkk = dict(keep='first')
    check_unsupported_args('Series.nlargest', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        czkrq__jty = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv, frq__wbuht = bodo.libs.array_kernels.nlargest(arr,
            czkrq__jty, n, True, bodo.hiframes.series_kernels.gt_f)
        bvq__frko = bodo.utils.conversion.convert_to_index(frq__wbuht)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
            bvq__frko, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    iphg__sqqz = dict(keep=keep)
    qzu__yrnkk = dict(keep='first')
    check_unsupported_args('Series.nsmallest', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        czkrq__jty = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv, frq__wbuht = bodo.libs.array_kernels.nlargest(arr,
            czkrq__jty, n, False, bodo.hiframes.series_kernels.lt_f)
        bvq__frko = bodo.utils.conversion.convert_to_index(frq__wbuht)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
            bvq__frko, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
@overload_method(HeterogeneousSeriesType, 'astype', inline='always',
    no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    iphg__sqqz = dict(errors=errors)
    qzu__yrnkk = dict(errors='raise')
    check_unsupported_args('Series.astype', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.astype()')

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    iphg__sqqz = dict(axis=axis, is_copy=is_copy)
    qzu__yrnkk = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        iwt__rfw = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[iwt__rfw], index
            [iwt__rfw], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    iphg__sqqz = dict(axis=axis, kind=kind, order=order)
    qzu__yrnkk = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ioslh__lpe = S.notna().values
        if not ioslh__lpe.all():
            utcwa__nixkv = np.full(n, -1, np.int64)
            utcwa__nixkv[ioslh__lpe] = argsort(arr[ioslh__lpe])
        else:
            utcwa__nixkv = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    iphg__sqqz = dict(axis=axis, numeric_only=numeric_only)
    qzu__yrnkk = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_str(method):
        raise BodoError(
            "Series.rank(): 'method' argument must be a constant string")
    if not is_overload_constant_str(na_option):
        raise BodoError(
            "Series.rank(): 'na_option' argument must be a constant string")

    def impl(S, axis=0, method='average', numeric_only=None, na_option=
        'keep', ascending=True, pct=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    iphg__sqqz = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    qzu__yrnkk = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    cxrv__woyjj = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qmk__ndy = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, cxrv__woyjj)
        otb__rcztm = qmk__ndy.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        utcwa__nixkv = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            otb__rcztm, 0)
        bvq__frko = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            otb__rcztm)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
            bvq__frko, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    iphg__sqqz = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    qzu__yrnkk = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    fjn__kywgg = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qmk__ndy = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, fjn__kywgg)
        otb__rcztm = qmk__ndy.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        utcwa__nixkv = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            otb__rcztm, 0)
        bvq__frko = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            otb__rcztm)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
            bvq__frko, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    uqsv__gpeyf = is_overload_true(is_nullable)
    omi__znhy = 'def impl(bins, arr, is_nullable=True, include_lowest=True):\n'
    omi__znhy += '  numba.parfors.parfor.init_prange()\n'
    omi__znhy += '  n = len(arr)\n'
    if uqsv__gpeyf:
        omi__znhy += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        omi__znhy += '  out_arr = np.empty(n, np.int64)\n'
    omi__znhy += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    omi__znhy += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if uqsv__gpeyf:
        omi__znhy += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        omi__znhy += '      out_arr[i] = -1\n'
    omi__znhy += '      continue\n'
    omi__znhy += '    val = arr[i]\n'
    omi__znhy += '    if include_lowest and val == bins[0]:\n'
    omi__znhy += '      ind = 1\n'
    omi__znhy += '    else:\n'
    omi__znhy += '      ind = np.searchsorted(bins, val)\n'
    omi__znhy += '    if ind == 0 or ind == len(bins):\n'
    if uqsv__gpeyf:
        omi__znhy += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        omi__znhy += '      out_arr[i] = -1\n'
    omi__znhy += '    else:\n'
    omi__znhy += '      out_arr[i] = ind - 1\n'
    omi__znhy += '  return out_arr\n'
    tjqu__jao = {}
    exec(omi__znhy, {'bodo': bodo, 'np': np, 'numba': numba}, tjqu__jao)
    impl = tjqu__jao['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        lel__ybc, gwqec__ojneu = np.divmod(x, 1)
        if lel__ybc == 0:
            lnes__gzbov = -int(np.floor(np.log10(abs(gwqec__ojneu)))
                ) - 1 + precision
        else:
            lnes__gzbov = precision
        return np.around(x, lnes__gzbov)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        ebg__zyef = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(ebg__zyef)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        avru__saovz = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            efsi__pgjjc = bins.copy()
            if right and include_lowest:
                efsi__pgjjc[0] = efsi__pgjjc[0] - avru__saovz
            qky__fpxo = bodo.libs.interval_arr_ext.init_interval_array(
                efsi__pgjjc[:-1], efsi__pgjjc[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(qky__fpxo,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        efsi__pgjjc = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            efsi__pgjjc[0] = efsi__pgjjc[0] - 10.0 ** -precision
        qky__fpxo = bodo.libs.interval_arr_ext.init_interval_array(efsi__pgjjc
            [:-1], efsi__pgjjc[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(qky__fpxo, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        ucxs__pupop = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        jdx__xsks = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        utcwa__nixkv = np.zeros(nbins, np.int64)
        for orq__botb in range(len(ucxs__pupop)):
            utcwa__nixkv[jdx__xsks[orq__botb]] = ucxs__pupop[orq__botb]
        return utcwa__nixkv
    return impl


def compute_bins(nbins, min_val, max_val):
    pass


@overload(compute_bins, no_unliteral=True)
def overload_compute_bins(nbins, min_val, max_val, right=True):

    def impl(nbins, min_val, max_val, right=True):
        if nbins < 1:
            raise ValueError('`bins` should be a positive integer.')
        min_val = min_val + 0.0
        max_val = max_val + 0.0
        if np.isinf(min_val) or np.isinf(max_val):
            raise ValueError(
                'cannot specify integer `bins` when input data contains infinity'
                )
        elif min_val == max_val:
            min_val -= 0.001 * abs(min_val) if min_val != 0 else 0.001
            max_val += 0.001 * abs(max_val) if max_val != 0 else 0.001
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
        else:
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
            uug__ihoq = (max_val - min_val) * 0.001
            if right:
                bins[0] -= uug__ihoq
            else:
                bins[-1] += uug__ihoq
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    iphg__sqqz = dict(dropna=dropna)
    qzu__yrnkk = dict(dropna=True)
    check_unsupported_args('Series.value_counts', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_bool(normalize):
        raise_bodo_error(
            'Series.value_counts(): normalize argument must be a constant boolean'
            )
    if not is_overload_constant_bool(sort):
        raise_bodo_error(
            'Series.value_counts(): sort argument must be a constant boolean')
    if not is_overload_bool(ascending):
        raise_bodo_error(
            'Series.value_counts(): ascending argument must be a constant boolean'
            )
    smd__sqmdi = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    omi__znhy = 'def impl(\n'
    omi__znhy += '    S,\n'
    omi__znhy += '    normalize=False,\n'
    omi__znhy += '    sort=True,\n'
    omi__znhy += '    ascending=False,\n'
    omi__znhy += '    bins=None,\n'
    omi__znhy += '    dropna=True,\n'
    omi__znhy += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    omi__znhy += '):\n'
    omi__znhy += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    omi__znhy += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    omi__znhy += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if smd__sqmdi:
        omi__znhy += '    right = True\n'
        omi__znhy += _gen_bins_handling(bins, S.dtype)
        omi__znhy += '    arr = get_bin_inds(bins, arr)\n'
    omi__znhy += '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n'
    omi__znhy += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    omi__znhy += '    )\n'
    omi__znhy += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if smd__sqmdi:
        omi__znhy += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        omi__znhy += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        omi__znhy += '    index = get_bin_labels(bins)\n'
    else:
        omi__znhy += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        omi__znhy += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        omi__znhy += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        omi__znhy += '    )\n'
        omi__znhy += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    omi__znhy += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        omi__znhy += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        ytvk__pmxyh = 'len(S)' if smd__sqmdi else 'count_arr.sum()'
        omi__znhy += f'    res = res / float({ytvk__pmxyh})\n'
    omi__znhy += '    return res\n'
    tjqu__jao = {}
    exec(omi__znhy, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, tjqu__jao)
    impl = tjqu__jao['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    omi__znhy = ''
    if isinstance(bins, types.Integer):
        omi__znhy += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        omi__znhy += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            omi__znhy += '    min_val = min_val.value\n'
            omi__znhy += '    max_val = max_val.value\n'
        omi__znhy += '    bins = compute_bins(bins, min_val, max_val, right)\n'
        if dtype == bodo.datetime64ns:
            omi__znhy += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        omi__znhy += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return omi__znhy


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    iphg__sqqz = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    qzu__yrnkk = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    omi__znhy = 'def impl(\n'
    omi__znhy += '    x,\n'
    omi__znhy += '    bins,\n'
    omi__znhy += '    right=True,\n'
    omi__znhy += '    labels=None,\n'
    omi__znhy += '    retbins=False,\n'
    omi__znhy += '    precision=3,\n'
    omi__znhy += '    include_lowest=False,\n'
    omi__znhy += "    duplicates='raise',\n"
    omi__znhy += '    ordered=True\n'
    omi__znhy += '):\n'
    if isinstance(x, SeriesType):
        omi__znhy += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        omi__znhy += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        omi__znhy += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        omi__znhy += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    omi__znhy += _gen_bins_handling(bins, x.dtype)
    omi__znhy += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    omi__znhy += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    omi__znhy += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    omi__znhy += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        omi__znhy += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        omi__znhy += '    return res\n'
    else:
        omi__znhy += '    return out_arr\n'
    tjqu__jao = {}
    exec(omi__znhy, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, tjqu__jao)
    impl = tjqu__jao['impl']
    return impl


def _get_q_list(q):
    return q


@overload(_get_q_list, no_unliteral=True)
def get_q_list_overload(q):
    if is_overload_int(q):
        return lambda q: np.linspace(0, 1, q + 1)
    return lambda q: q


@overload(pd.unique, inline='always', no_unliteral=True)
def overload_unique(values):
    if not is_series_type(values) and not (bodo.utils.utils.is_array_typ(
        values, False) and values.ndim == 1):
        raise BodoError(
            "pd.unique(): 'values' must be either a Series or a 1-d array")
    if is_series_type(values):

        def impl(values):
            arr = bodo.hiframes.pd_series_ext.get_series_data(values)
            return bodo.allgatherv(bodo.libs.array_kernels.unique(arr), False)
        return impl
    else:
        return lambda values: bodo.allgatherv(bodo.libs.array_kernels.
            unique(values), False)


@overload(pd.qcut, inline='always', no_unliteral=True)
def overload_qcut(x, q, labels=None, retbins=False, precision=3, duplicates
    ='raise'):
    iphg__sqqz = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    qzu__yrnkk = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        zbho__pobyj = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, zbho__pobyj)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    iphg__sqqz = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    qzu__yrnkk = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='GroupBy')
    if not is_overload_true(as_index):
        raise BodoError('as_index=False only valid with DataFrame')
    if is_overload_none(by) and is_overload_none(level):
        raise BodoError("You have to supply one of 'by' and 'level'")
    if not is_overload_none(by) and not is_overload_none(level):
        raise BodoError(
            "Series.groupby(): 'level' argument should be None if 'by' is not None"
            )
    if not is_overload_none(level):
        if not (is_overload_constant_int(level) and get_overload_const_int(
            level) == 0) or isinstance(S.index, bodo.hiframes.
            pd_multi_index_ext.MultiIndexType):
            raise BodoError(
                "Series.groupby(): MultiIndex case or 'level' other than 0 not supported yet"
                )
        ivjbp__zvc = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            hlws__sttgr = bodo.utils.conversion.coerce_to_array(index)
            qmk__ndy = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                hlws__sttgr, arr), index, ivjbp__zvc)
            return qmk__ndy.groupby(' ')['']
        return impl_index
    iohvz__npjct = by
    if isinstance(by, SeriesType):
        iohvz__npjct = by.data
    if isinstance(iohvz__npjct, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    amhf__qib = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        hlws__sttgr = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        qmk__ndy = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            hlws__sttgr, arr), index, amhf__qib)
        return qmk__ndy.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    iphg__sqqz = dict(verify_integrity=verify_integrity)
    qzu__yrnkk = dict(verify_integrity=False)
    check_unsupported_args('Series.append', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_append,
        'Series.append()')
    if isinstance(to_append, SeriesType):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S, to_append), ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    if isinstance(to_append, types.BaseTuple):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S,) + to_append, ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    return (lambda S, to_append, ignore_index=False, verify_integrity=False:
        pd.concat([S] + to_append, ignore_index=ignore_index,
        verify_integrity=verify_integrity))


@overload_method(SeriesType, 'isin', inline='always', no_unliteral=True)
def overload_series_isin(S, values):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.isin()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(values,
        'Series.isin()')
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(S, values):
            zrad__shzed = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            utcwa__nixkv = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(utcwa__nixkv, A, zrad__shzed, False)
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    iphg__sqqz = dict(interpolation=interpolation)
    qzu__yrnkk = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            utcwa__nixkv = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                index, name)
        return impl_list
    elif isinstance(q, (float, types.Number)) or is_overload_constant_int(q):

        def impl(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return bodo.libs.array_ops.array_op_quantile(arr, q)
        return impl
    else:
        raise BodoError(
            f'Series.quantile() q type must be float or iterable of floats only.'
            )


@overload_method(SeriesType, 'nunique', inline='always', no_unliteral=True)
def overload_series_nunique(S, dropna=True):
    if not is_overload_bool(dropna):
        raise BodoError('Series.nunique: dropna must be a boolean value')

    def impl(S, dropna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_kernels.nunique(arr, dropna)
    return impl


@overload_method(SeriesType, 'unique', inline='always', no_unliteral=True)
def overload_series_unique(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        osifb__ymj = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(osifb__ymj, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    iphg__sqqz = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    qzu__yrnkk = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.describe()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)
        ) and not isinstance(S.data, IntegerArrayType):
        raise BodoError(f'describe() column input type {S.data} not supported.'
            )
    if S.data.dtype == bodo.datetime64ns:

        def impl_dt(S, percentiles=None, include=None, exclude=None,
            datetime_is_numeric=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
                array_ops.array_op_describe(arr), bodo.utils.conversion.
                convert_to_index(['count', 'mean', 'min', '25%', '50%',
                '75%', 'max']), name)
        return impl_dt

    def impl(S, percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.array_ops.
            array_op_describe(arr), bodo.utils.conversion.convert_to_index(
            ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']), name)
    return impl


@overload_method(SeriesType, 'memory_usage', inline='always', no_unliteral=True
    )
def overload_series_memory_usage(S, index=True, deep=False):
    if is_overload_true(index):

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            return arr.nbytes + index.nbytes
        return impl
    else:

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return arr.nbytes
        return impl


def binary_str_fillna_inplace_series_impl(is_binary=False):
    if is_binary:
        mmuxl__jnsga = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        mmuxl__jnsga = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    omi__znhy = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {mmuxl__jnsga}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    axz__sshe = dict()
    exec(omi__znhy, {'bodo': bodo, 'numba': numba}, axz__sshe)
    stsm__bloo = axz__sshe['impl']
    return stsm__bloo


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        mmuxl__jnsga = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        mmuxl__jnsga = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    omi__znhy = 'def impl(S,\n'
    omi__znhy += '     value=None,\n'
    omi__znhy += '    method=None,\n'
    omi__znhy += '    axis=None,\n'
    omi__znhy += '    inplace=False,\n'
    omi__znhy += '    limit=None,\n'
    omi__znhy += '   downcast=None,\n'
    omi__znhy += '):\n'
    omi__znhy += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    omi__znhy += '    n = len(in_arr)\n'
    omi__znhy += f'    out_arr = {mmuxl__jnsga}(n, -1)\n'
    omi__znhy += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    omi__znhy += '        s = in_arr[j]\n'
    omi__znhy += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    omi__znhy += '            s = value\n'
    omi__znhy += '        out_arr[j] = s\n'
    omi__znhy += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    axz__sshe = dict()
    exec(omi__znhy, {'bodo': bodo, 'numba': numba}, axz__sshe)
    stsm__bloo = axz__sshe['impl']
    return stsm__bloo


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
    hlg__rxnlj = bodo.hiframes.pd_series_ext.get_series_data(value)
    for orq__botb in numba.parfors.parfor.internal_prange(len(ljs__iadge)):
        s = ljs__iadge[orq__botb]
        if bodo.libs.array_kernels.isna(ljs__iadge, orq__botb
            ) and not bodo.libs.array_kernels.isna(hlg__rxnlj, orq__botb):
            s = hlg__rxnlj[orq__botb]
        ljs__iadge[orq__botb] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
    for orq__botb in numba.parfors.parfor.internal_prange(len(ljs__iadge)):
        s = ljs__iadge[orq__botb]
        if bodo.libs.array_kernels.isna(ljs__iadge, orq__botb):
            s = value
        ljs__iadge[orq__botb] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    hlg__rxnlj = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(ljs__iadge)
    utcwa__nixkv = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for zer__mhmnn in numba.parfors.parfor.internal_prange(n):
        s = ljs__iadge[zer__mhmnn]
        if bodo.libs.array_kernels.isna(ljs__iadge, zer__mhmnn
            ) and not bodo.libs.array_kernels.isna(hlg__rxnlj, zer__mhmnn):
            s = hlg__rxnlj[zer__mhmnn]
        utcwa__nixkv[zer__mhmnn] = s
        if bodo.libs.array_kernels.isna(ljs__iadge, zer__mhmnn
            ) and bodo.libs.array_kernels.isna(hlg__rxnlj, zer__mhmnn):
            bodo.libs.array_kernels.setna(utcwa__nixkv, zer__mhmnn)
    return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    hlg__rxnlj = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(ljs__iadge)
    utcwa__nixkv = bodo.utils.utils.alloc_type(n, ljs__iadge.dtype, (-1,))
    for orq__botb in numba.parfors.parfor.internal_prange(n):
        s = ljs__iadge[orq__botb]
        if bodo.libs.array_kernels.isna(ljs__iadge, orq__botb
            ) and not bodo.libs.array_kernels.isna(hlg__rxnlj, orq__botb):
            s = hlg__rxnlj[orq__botb]
        utcwa__nixkv[orq__botb] = s
    return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    iphg__sqqz = dict(limit=limit, downcast=downcast)
    qzu__yrnkk = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    xegee__das = not is_overload_none(value)
    ufemn__lbn = not is_overload_none(method)
    if xegee__das and ufemn__lbn:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not xegee__das and not ufemn__lbn:
        raise BodoError(
            "Series.fillna(): Must specify one of 'value' and 'method'.")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.fillna(): axis argument not supported')
    elif is_iterable_type(value) and not isinstance(value, SeriesType):
        raise BodoError('Series.fillna(): "value" parameter cannot be a list')
    elif is_var_size_item_array_type(S.data
        ) and not S.dtype == bodo.string_type:
        raise BodoError(
            f'Series.fillna() with inplace=True not supported for {S.dtype} values yet.'
            )
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "Series.fillna(): 'inplace' argument must be a constant boolean")
    if ufemn__lbn:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        jksiy__cxr = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(jksiy__cxr)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(jksiy__cxr)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    yyn__lfvtt = element_type(S.data)
    tpvw__jtq = None
    if xegee__das:
        tpvw__jtq = element_type(types.unliteral(value))
    if tpvw__jtq and not can_replace(yyn__lfvtt, tpvw__jtq):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {tpvw__jtq} with series type {yyn__lfvtt}'
            )
    if is_overload_true(inplace):
        if S.dtype == bodo.string_type:
            if S.data == bodo.dict_str_arr_type:
                raise_bodo_error(
                    "Series.fillna(): 'inplace' not supported for dictionary-encoded string arrays yet."
                    )
            if is_overload_constant_str(value) and get_overload_const_str(value
                ) == '':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=False)
            return binary_str_fillna_inplace_impl(is_binary=False)
        if S.dtype == bodo.bytes_type:
            if is_overload_constant_bytes(value) and get_overload_const_bytes(
                value) == b'':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=True)
            return binary_str_fillna_inplace_impl(is_binary=True)
        else:
            if isinstance(value, SeriesType):
                return fillna_inplace_series_impl
            return fillna_inplace_impl
    else:
        wgug__ikut = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                hlg__rxnlj = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(ljs__iadge)
                utcwa__nixkv = bodo.utils.utils.alloc_type(n, wgug__ikut, (-1,)
                    )
                for orq__botb in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(ljs__iadge, orq__botb
                        ) and bodo.libs.array_kernels.isna(hlg__rxnlj,
                        orq__botb):
                        bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                        continue
                    if bodo.libs.array_kernels.isna(ljs__iadge, orq__botb):
                        utcwa__nixkv[orq__botb
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            hlg__rxnlj[orq__botb])
                        continue
                    utcwa__nixkv[orq__botb
                        ] = bodo.utils.conversion.unbox_if_timestamp(ljs__iadge
                        [orq__botb])
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return fillna_series_impl
        if ufemn__lbn:
            rwew__qda = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(yyn__lfvtt, (types.Integer, types.Float)
                ) and yyn__lfvtt not in rwew__qda:
                raise BodoError(
                    f"Series.fillna(): series of type {yyn__lfvtt} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                utcwa__nixkv = bodo.libs.array_kernels.ffill_bfill_arr(
                    ljs__iadge, method)
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(ljs__iadge)
            utcwa__nixkv = bodo.utils.utils.alloc_type(n, wgug__ikut, (-1,))
            for orq__botb in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(ljs__iadge[
                    orq__botb])
                if bodo.libs.array_kernels.isna(ljs__iadge, orq__botb):
                    s = value
                utcwa__nixkv[orq__botb] = s
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        lnxf__shtgt = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        iphg__sqqz = dict(limit=limit, downcast=downcast)
        qzu__yrnkk = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', iphg__sqqz,
            qzu__yrnkk, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        yyn__lfvtt = element_type(S.data)
        rwew__qda = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(yyn__lfvtt, (types.Integer, types.Float)
            ) and yyn__lfvtt not in rwew__qda:
            raise BodoError(
                f'Series.{overload_name}(): series of type {yyn__lfvtt} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            utcwa__nixkv = bodo.libs.array_kernels.ffill_bfill_arr(ljs__iadge,
                lnxf__shtgt)
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        gfmk__wbxsg = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            gfmk__wbxsg)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        jkver__qal = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(jkver__qal)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        jkver__qal = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(jkver__qal)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        jkver__qal = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(jkver__qal)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    iphg__sqqz = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    cstl__ssw = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', iphg__sqqz, cstl__ssw,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    yyn__lfvtt = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        dhr__ijdb = element_type(to_replace.key_type)
        tpvw__jtq = element_type(to_replace.value_type)
    else:
        dhr__ijdb = element_type(to_replace)
        tpvw__jtq = element_type(value)
    pso__mzwc = None
    if yyn__lfvtt != types.unliteral(dhr__ijdb):
        if bodo.utils.typing.equality_always_false(yyn__lfvtt, types.
            unliteral(dhr__ijdb)
            ) or not bodo.utils.typing.types_equality_exists(yyn__lfvtt,
            dhr__ijdb):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(yyn__lfvtt, (types.Float, types.Integer)
            ) or yyn__lfvtt == np.bool_:
            pso__mzwc = yyn__lfvtt
    if not can_replace(yyn__lfvtt, types.unliteral(tpvw__jtq)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    kqud__rrxis = to_str_arr_if_dict_array(S.data)
    if isinstance(kqud__rrxis, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(ljs__iadge.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(ljs__iadge)
        utcwa__nixkv = bodo.utils.utils.alloc_type(n, kqud__rrxis, (-1,))
        flijz__kxjhq = build_replace_dict(to_replace, value, pso__mzwc)
        for orq__botb in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(ljs__iadge, orq__botb):
                bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                continue
            s = ljs__iadge[orq__botb]
            if s in flijz__kxjhq:
                s = flijz__kxjhq[s]
            utcwa__nixkv[orq__botb] = s
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    qdxd__luhuo = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    efai__hdojl = is_iterable_type(to_replace)
    ynfn__aekin = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    dpzqt__umkwg = is_iterable_type(value)
    if qdxd__luhuo and ynfn__aekin:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                flijz__kxjhq = {}
                flijz__kxjhq[key_dtype_conv(to_replace)] = value
                return flijz__kxjhq
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            flijz__kxjhq = {}
            flijz__kxjhq[to_replace] = value
            return flijz__kxjhq
        return impl
    if efai__hdojl and ynfn__aekin:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                flijz__kxjhq = {}
                for ddkcv__ezds in to_replace:
                    flijz__kxjhq[key_dtype_conv(ddkcv__ezds)] = value
                return flijz__kxjhq
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            flijz__kxjhq = {}
            for ddkcv__ezds in to_replace:
                flijz__kxjhq[ddkcv__ezds] = value
            return flijz__kxjhq
        return impl
    if efai__hdojl and dpzqt__umkwg:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                flijz__kxjhq = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for orq__botb in range(len(to_replace)):
                    flijz__kxjhq[key_dtype_conv(to_replace[orq__botb])
                        ] = value[orq__botb]
                return flijz__kxjhq
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            flijz__kxjhq = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for orq__botb in range(len(to_replace)):
                flijz__kxjhq[to_replace[orq__botb]] = value[orq__botb]
            return flijz__kxjhq
        return impl
    if isinstance(to_replace, numba.types.DictType) and is_overload_none(value
        ):
        return lambda to_replace, value, key_dtype_conv: to_replace
    raise BodoError(
        'Series.replace(): Not supported for types to_replace={} and value={}'
        .format(to_replace, value))


@overload_method(SeriesType, 'diff', inline='always', no_unliteral=True)
def overload_series_diff(S, periods=1):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.diff()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)):
        raise BodoError(
            f'Series.diff() column input type {S.data} not supported.')
    if not is_overload_int(periods):
        raise BodoError("Series.diff(): 'periods' input must be an integer.")
    if S.data == types.Array(bodo.datetime64ns, 1, 'C'):

        def impl_datetime(S, periods=1):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            utcwa__nixkv = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo
                .hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    iphg__sqqz = dict(ignore_index=ignore_index)
    gny__jlou = dict(ignore_index=False)
    check_unsupported_args('Series.explode', iphg__sqqz, gny__jlou,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        czkrq__jty = bodo.utils.conversion.index_to_array(index)
        utcwa__nixkv, ddnmm__qyb = bodo.libs.array_kernels.explode(arr,
            czkrq__jty)
        bvq__frko = bodo.utils.conversion.index_from_array(ddnmm__qyb)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
            bvq__frko, name)
    return impl


@overload(np.digitize, inline='always', no_unliteral=True)
def overload_series_np_digitize(x, bins, right=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.digitize()')
    if isinstance(x, SeriesType):

        def impl(x, bins, right=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(x)
            return np.digitize(arr, bins, right)
        return impl


@overload(np.argmax, inline='always', no_unliteral=True)
def argmax_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            aoe__iqhkl = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for orq__botb in numba.parfors.parfor.internal_prange(n):
                aoe__iqhkl[orq__botb] = np.argmax(a[orq__botb])
            return aoe__iqhkl
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            ubrkz__jxbpd = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for orq__botb in numba.parfors.parfor.internal_prange(n):
                ubrkz__jxbpd[orq__botb] = np.argmin(a[orq__botb])
            return ubrkz__jxbpd
        return impl


def overload_series_np_dot(a, b, out=None):
    if (isinstance(a, SeriesType) or isinstance(b, SeriesType)
        ) and not is_overload_none(out):
        raise BodoError("np.dot(): 'out' parameter not supported yet")
    if isinstance(a, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(a)
            return np.dot(arr, b)
        return impl
    if isinstance(b, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(b)
            return np.dot(a, arr)
        return impl


overload(np.dot, inline='always', no_unliteral=True)(overload_series_np_dot)
overload(operator.matmul, inline='always', no_unliteral=True)(
    overload_series_np_dot)


@overload_method(SeriesType, 'dropna', inline='always', no_unliteral=True)
def overload_series_dropna(S, axis=0, inplace=False, how=None):
    iphg__sqqz = dict(axis=axis, inplace=inplace, how=how)
    wmcs__kxxoy = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', iphg__sqqz, wmcs__kxxoy,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ioslh__lpe = S.notna().values
            czkrq__jty = bodo.utils.conversion.extract_index_array(S)
            bvq__frko = bodo.utils.conversion.convert_to_index(czkrq__jty[
                ioslh__lpe])
            utcwa__nixkv = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(ljs__iadge))
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                bvq__frko, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            czkrq__jty = bodo.utils.conversion.extract_index_array(S)
            ioslh__lpe = S.notna().values
            bvq__frko = bodo.utils.conversion.convert_to_index(czkrq__jty[
                ioslh__lpe])
            utcwa__nixkv = ljs__iadge[ioslh__lpe]
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                bvq__frko, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    iphg__sqqz = dict(freq=freq, axis=axis, fill_value=fill_value)
    qzu__yrnkk = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.shift()')
    if not is_supported_shift_array_type(S.data):
        raise BodoError(
            f"Series.shift(): Series input type '{S.data.dtype}' not supported yet."
            )
    if not is_overload_int(periods):
        raise BodoError("Series.shift(): 'periods' input must be an integer.")

    def impl(S, periods=1, freq=None, axis=0, fill_value=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    iphg__sqqz = dict(fill_method=fill_method, limit=limit, freq=freq)
    qzu__yrnkk = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.pct_change()')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


def create_series_mask_where_overload(func_name):

    def overload_series_mask_where(S, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
            f'Series.{func_name}()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
            f'Series.{func_name}()')
        _validate_arguments_mask_where(f'Series.{func_name}', 'Series', S,
            cond, other, inplace, axis, level, errors, try_cast)
        if is_overload_constant_nan(other):
            wkzi__avi = 'None'
        else:
            wkzi__avi = 'other'
        omi__znhy = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            omi__znhy += '  cond = ~cond\n'
        omi__znhy += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        omi__znhy += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        omi__znhy += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        omi__znhy += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {wkzi__avi})\n'
            )
        omi__znhy += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        tjqu__jao = {}
        exec(omi__znhy, {'bodo': bodo, 'np': np}, tjqu__jao)
        impl = tjqu__jao['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        gfmk__wbxsg = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(gfmk__wbxsg)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    iphg__sqqz = dict(inplace=inplace, level=level, errors=errors, try_cast
        =try_cast)
    qzu__yrnkk = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name=module_name)
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if isinstance(S, bodo.hiframes.pd_index_ext.RangeIndexType):
        arr = types.Array(types.int64, 1, 'C')
    else:
        arr = S.data
    if isinstance(other, SeriesType):
        _validate_self_other_mask_where(func_name, module_name, arr, other.data
            )
    else:
        _validate_self_other_mask_where(func_name, module_name, arr, other)
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        cond.ndim == 1 and cond.dtype == types.bool_):
        raise BodoError(
            f"{func_name}() 'cond' argument must be a Series or 1-dim array of booleans"
            )


def _validate_self_other_mask_where(func_name, module_name, arr, other,
    max_ndim=1, is_default=False):
    if not (isinstance(arr, types.Array) or isinstance(arr,
        BooleanArrayType) or isinstance(arr, IntegerArrayType) or bodo.
        utils.utils.is_array_typ(arr, False) and arr.dtype in [bodo.
        string_type, bodo.bytes_type] or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type not in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.pd_timestamp_type, bodo.
        pd_timedelta_type]):
        raise BodoError(
            f'{func_name}() {module_name} data with type {arr} not yet supported'
            )
    utvwi__ewt = is_overload_constant_nan(other)
    if not (is_default or utvwi__ewt or is_scalar_type(other) or isinstance
        (other, types.Array) and other.ndim >= 1 and other.ndim <= max_ndim or
        isinstance(other, SeriesType) and (isinstance(arr, types.Array) or 
        arr.dtype in [bodo.string_type, bodo.bytes_type]) or 
        is_str_arr_type(other) and (arr.dtype == bodo.string_type or 
        isinstance(arr, bodo.CategoricalArrayType) and arr.dtype.elem_type ==
        bodo.string_type) or isinstance(other, BinaryArrayType) and (arr.
        dtype == bodo.bytes_type or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type == bodo.bytes_type) or
        (not (isinstance(other, (StringArrayType, BinaryArrayType)) or 
        other == bodo.dict_str_arr_type) and (isinstance(arr.dtype, types.
        Integer) and (bodo.utils.utils.is_array_typ(other) and isinstance(
        other.dtype, types.Integer) or is_series_type(other) and isinstance
        (other.dtype, types.Integer))) or (bodo.utils.utils.is_array_typ(
        other) and arr.dtype == other.dtype or is_series_type(other) and 
        arr.dtype == other.dtype)) and (isinstance(arr, BooleanArrayType) or
        isinstance(arr, IntegerArrayType))):
        raise BodoError(
            f"{func_name}() 'other' must be a scalar, non-categorical series, 1-dim numpy array or StringArray with a matching type for {module_name}."
            )
    if not is_default:
        if isinstance(arr.dtype, bodo.PDCategoricalDtype):
            tbucv__tplr = arr.dtype.elem_type
        else:
            tbucv__tplr = arr.dtype
        if is_iterable_type(other):
            yogab__tkj = other.dtype
        elif utvwi__ewt:
            yogab__tkj = types.float64
        else:
            yogab__tkj = types.unliteral(other)
        if not utvwi__ewt and not is_common_scalar_dtype([tbucv__tplr,
            yogab__tkj]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        iphg__sqqz = dict(level=level, axis=axis)
        qzu__yrnkk = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), iphg__sqqz,
            qzu__yrnkk, package_name='pandas', module_name='Series')
        cbuer__irpez = other == string_type or is_overload_constant_str(other)
        kvkx__kplq = is_iterable_type(other) and other.dtype == string_type
        vela__iln = S.dtype == string_type and (op == operator.add and (
            cbuer__irpez or kvkx__kplq) or op == operator.mul and
            isinstance(other, types.Integer))
        jxdun__pywo = S.dtype == bodo.timedelta64ns
        bfvkh__jegq = S.dtype == bodo.datetime64ns
        afwc__nndn = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        qzo__jid = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        yoxz__xfriw = jxdun__pywo and (afwc__nndn or qzo__jid
            ) or bfvkh__jegq and afwc__nndn
        yoxz__xfriw = yoxz__xfriw and op == operator.add
        if not (isinstance(S.dtype, types.Number) or vela__iln or yoxz__xfriw):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        hlr__jzkvb = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            kqud__rrxis = hlr__jzkvb.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and kqud__rrxis == types.Array(types.bool_, 1, 'C'):
                kqud__rrxis = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                utcwa__nixkv = bodo.utils.utils.alloc_type(n, kqud__rrxis,
                    (-1,))
                for orq__botb in numba.parfors.parfor.internal_prange(n):
                    pwkvt__muto = bodo.libs.array_kernels.isna(arr, orq__botb)
                    if pwkvt__muto:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(utcwa__nixkv,
                                orq__botb)
                        else:
                            utcwa__nixkv[orq__botb] = op(fill_value, other)
                    else:
                        utcwa__nixkv[orq__botb] = op(arr[orq__botb], other)
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        kqud__rrxis = hlr__jzkvb.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType) and kqud__rrxis == types.Array(
            types.bool_, 1, 'C'):
            kqud__rrxis = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            kdegu__ngs = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            utcwa__nixkv = bodo.utils.utils.alloc_type(n, kqud__rrxis, (-1,))
            for orq__botb in numba.parfors.parfor.internal_prange(n):
                pwkvt__muto = bodo.libs.array_kernels.isna(arr, orq__botb)
                kbsvn__klf = bodo.libs.array_kernels.isna(kdegu__ngs, orq__botb
                    )
                if pwkvt__muto and kbsvn__klf:
                    bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                elif pwkvt__muto:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                    else:
                        utcwa__nixkv[orq__botb] = op(fill_value, kdegu__ngs
                            [orq__botb])
                elif kbsvn__klf:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                    else:
                        utcwa__nixkv[orq__botb] = op(arr[orq__botb], fill_value
                            )
                else:
                    utcwa__nixkv[orq__botb] = op(arr[orq__botb], kdegu__ngs
                        [orq__botb])
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                index, name)
        return impl
    return overload_series_explicit_binary_op


def create_explicit_binary_reverse_op_overload(op):

    def overload_series_explicit_binary_reverse_op(S, other, level=None,
        fill_value=None, axis=0):
        if not is_overload_none(level):
            raise BodoError('level argument not supported')
        if not is_overload_zero(axis):
            raise BodoError('axis argument not supported')
        if not isinstance(S.dtype, types.Number):
            raise BodoError('only numeric values supported')
        hlr__jzkvb = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            kqud__rrxis = hlr__jzkvb.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and kqud__rrxis == types.Array(types.bool_, 1, 'C'):
                kqud__rrxis = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                utcwa__nixkv = bodo.utils.utils.alloc_type(n, kqud__rrxis, None
                    )
                for orq__botb in numba.parfors.parfor.internal_prange(n):
                    pwkvt__muto = bodo.libs.array_kernels.isna(arr, orq__botb)
                    if pwkvt__muto:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(utcwa__nixkv,
                                orq__botb)
                        else:
                            utcwa__nixkv[orq__botb] = op(other, fill_value)
                    else:
                        utcwa__nixkv[orq__botb] = op(other, arr[orq__botb])
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        kqud__rrxis = hlr__jzkvb.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType) and kqud__rrxis == types.Array(
            types.bool_, 1, 'C'):
            kqud__rrxis = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            kdegu__ngs = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            utcwa__nixkv = bodo.utils.utils.alloc_type(n, kqud__rrxis, None)
            for orq__botb in numba.parfors.parfor.internal_prange(n):
                pwkvt__muto = bodo.libs.array_kernels.isna(arr, orq__botb)
                kbsvn__klf = bodo.libs.array_kernels.isna(kdegu__ngs, orq__botb
                    )
                utcwa__nixkv[orq__botb] = op(kdegu__ngs[orq__botb], arr[
                    orq__botb])
                if pwkvt__muto and kbsvn__klf:
                    bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                elif pwkvt__muto:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                    else:
                        utcwa__nixkv[orq__botb] = op(kdegu__ngs[orq__botb],
                            fill_value)
                elif kbsvn__klf:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                    else:
                        utcwa__nixkv[orq__botb] = op(fill_value, arr[orq__botb]
                            )
                else:
                    utcwa__nixkv[orq__botb] = op(kdegu__ngs[orq__botb], arr
                        [orq__botb])
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                index, name)
        return impl
    return overload_series_explicit_binary_reverse_op


explicit_binop_funcs_two_ways = {operator.add: {'add'}, operator.sub: {
    'sub'}, operator.mul: {'mul'}, operator.truediv: {'div', 'truediv'},
    operator.floordiv: {'floordiv'}, operator.mod: {'mod'}, operator.pow: {
    'pow'}}
explicit_binop_funcs_single = {operator.lt: 'lt', operator.gt: 'gt',
    operator.le: 'le', operator.ge: 'ge', operator.ne: 'ne', operator.eq: 'eq'}
explicit_binop_funcs = set()
split_logical_binops_funcs = [operator.or_, operator.and_]


def _install_explicit_binary_ops():
    for op, cyfj__wfxty in explicit_binop_funcs_two_ways.items():
        for name in cyfj__wfxty:
            gfmk__wbxsg = create_explicit_binary_op_overload(op)
            jfzv__omrp = create_explicit_binary_reverse_op_overload(op)
            vmvu__mxzh = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(gfmk__wbxsg)
            overload_method(SeriesType, vmvu__mxzh, no_unliteral=True)(
                jfzv__omrp)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        gfmk__wbxsg = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(gfmk__wbxsg)
        explicit_binop_funcs.add(name)


_install_explicit_binary_ops()


def create_binary_op_overload(op):

    def overload_series_binary_op(lhs, rhs):
        if (isinstance(lhs, SeriesType) and isinstance(rhs, SeriesType) and
            lhs.dtype == bodo.datetime64ns and rhs.dtype == bodo.
            datetime64ns and op == operator.sub):

            def impl_dt64(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                sdge__gun = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                utcwa__nixkv = dt64_arr_sub(arr, sdge__gun)
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return impl_dt64
        if op in [operator.add, operator.sub] and isinstance(lhs, SeriesType
            ) and lhs.dtype == bodo.datetime64ns and is_offsets_type(rhs):

            def impl_offsets(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                utcwa__nixkv = np.empty(n, np.dtype('datetime64[ns]'))
                for orq__botb in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, orq__botb):
                        bodo.libs.array_kernels.setna(utcwa__nixkv, orq__botb)
                        continue
                    lee__mgyuz = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[orq__botb]))
                    lczv__sijhc = op(lee__mgyuz, rhs)
                    utcwa__nixkv[orq__botb
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        lczv__sijhc.value)
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return impl_offsets
        if op == operator.add and is_offsets_type(lhs) and isinstance(rhs,
            SeriesType) and rhs.dtype == bodo.datetime64ns:

            def impl(lhs, rhs):
                return op(rhs, lhs)
            return impl
        if isinstance(lhs, SeriesType):
            if lhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                    sdge__gun = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    utcwa__nixkv = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(sdge__gun))
                    return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv
                        , index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                sdge__gun = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                utcwa__nixkv = op(arr, sdge__gun)
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    bxcd__aru = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    utcwa__nixkv = op(bodo.utils.conversion.
                        unbox_if_timestamp(bxcd__aru), arr)
                    return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv
                        , index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                bxcd__aru = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                utcwa__nixkv = op(bxcd__aru, arr)
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        gfmk__wbxsg = create_binary_op_overload(op)
        overload(op)(gfmk__wbxsg)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    ssux__poxao = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, ssux__poxao)
        for orq__botb in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, orq__botb
                ) or bodo.libs.array_kernels.isna(arg2, orq__botb):
                bodo.libs.array_kernels.setna(S, orq__botb)
                continue
            S[orq__botb
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                orq__botb]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[orq__botb]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                kdegu__ngs = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, kdegu__ngs)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        gfmk__wbxsg = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(gfmk__wbxsg)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                utcwa__nixkv = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        gfmk__wbxsg = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(gfmk__wbxsg)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    utcwa__nixkv = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv
                        , index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    kdegu__ngs = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    utcwa__nixkv = ufunc(arr, kdegu__ngs)
                    return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv
                        , index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    kdegu__ngs = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    utcwa__nixkv = ufunc(arr, kdegu__ngs)
                    return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv
                        , index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        gfmk__wbxsg = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(gfmk__wbxsg)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        sukl__qklm = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        lqv__wjceq = np.arange(n),
        bodo.libs.timsort.sort(sukl__qklm, 0, n, lqv__wjceq)
        return lqv__wjceq[0]
    return impl


@overload(pd.to_numeric, inline='always', no_unliteral=True)
def overload_to_numeric(arg_a, errors='raise', downcast=None):
    if not is_overload_none(downcast) and not (is_overload_constant_str(
        downcast) and get_overload_const_str(downcast) in ('integer',
        'signed', 'unsigned', 'float')):
        raise BodoError(
            'pd.to_numeric(): invalid downcasting method provided {}'.
            format(downcast))
    out_dtype = types.float64
    if not is_overload_none(downcast):
        ugfy__jhrgy = get_overload_const_str(downcast)
        if ugfy__jhrgy in ('integer', 'signed'):
            out_dtype = types.int64
        elif ugfy__jhrgy == 'unsigned':
            out_dtype = types.uint64
        else:
            assert ugfy__jhrgy == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            ljs__iadge = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            utcwa__nixkv = pd.to_numeric(ljs__iadge, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            ohiom__rjeuv = np.empty(n, np.float64)
            for orq__botb in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, orq__botb):
                    bodo.libs.array_kernels.setna(ohiom__rjeuv, orq__botb)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(ohiom__rjeuv,
                        orq__botb, arg_a, orq__botb)
            return ohiom__rjeuv
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            ohiom__rjeuv = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for orq__botb in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, orq__botb):
                    bodo.libs.array_kernels.setna(ohiom__rjeuv, orq__botb)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(ohiom__rjeuv,
                        orq__botb, arg_a, orq__botb)
            return ohiom__rjeuv
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        umdzg__uqwbl = if_series_to_array_type(args[0])
        if isinstance(umdzg__uqwbl, types.Array) and isinstance(umdzg__uqwbl
            .dtype, types.Integer):
            umdzg__uqwbl = types.Array(types.float64, 1, 'C')
        return umdzg__uqwbl(*args)


def where_impl_one_arg(c):
    return np.where(c)


@overload(where_impl_one_arg, no_unliteral=True)
def overload_where_unsupported_one_arg(condition):
    if isinstance(condition, SeriesType) or bodo.utils.utils.is_array_typ(
        condition, False):
        return lambda condition: np.where(condition)


def overload_np_where_one_arg(condition):
    if isinstance(condition, SeriesType):

        def impl_series(condition):
            condition = bodo.hiframes.pd_series_ext.get_series_data(condition)
            return bodo.libs.array_kernels.nonzero(condition)
        return impl_series
    elif bodo.utils.utils.is_array_typ(condition, False):

        def impl(condition):
            return bodo.libs.array_kernels.nonzero(condition)
        return impl


overload(np.where, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)
overload(where_impl_one_arg, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)


def where_impl(c, x, y):
    return np.where(c, x, y)


@overload(where_impl, no_unliteral=True)
def overload_where_unsupported(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return lambda condition, x, y: np.where(condition, x, y)


@overload(where_impl, no_unliteral=True)
@overload(np.where, no_unliteral=True)
def overload_np_where(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return
    assert condition.dtype == types.bool_, 'invalid condition dtype'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(y,
        'numpy.where()')
    pzu__kyhuh = bodo.utils.utils.is_array_typ(x, True)
    ooiaw__gbz = bodo.utils.utils.is_array_typ(y, True)
    omi__znhy = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        omi__znhy += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if pzu__kyhuh and not bodo.utils.utils.is_array_typ(x, False):
        omi__znhy += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if ooiaw__gbz and not bodo.utils.utils.is_array_typ(y, False):
        omi__znhy += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    omi__znhy += '  n = len(condition)\n'
    bqc__sqoh = x.dtype if pzu__kyhuh else types.unliteral(x)
    kgtcm__mjs = y.dtype if ooiaw__gbz else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        bqc__sqoh = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        kgtcm__mjs = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    lhckb__rrw = get_data(x)
    haoik__jwmvl = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(lqv__wjceq) for
        lqv__wjceq in [lhckb__rrw, haoik__jwmvl])
    if haoik__jwmvl == types.none:
        if isinstance(bqc__sqoh, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif lhckb__rrw == haoik__jwmvl and not is_nullable:
        out_dtype = dtype_to_array_type(bqc__sqoh)
    elif bqc__sqoh == string_type or kgtcm__mjs == string_type:
        out_dtype = bodo.string_array_type
    elif lhckb__rrw == bytes_type or (pzu__kyhuh and bqc__sqoh == bytes_type
        ) and (haoik__jwmvl == bytes_type or ooiaw__gbz and kgtcm__mjs ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(bqc__sqoh, bodo.PDCategoricalDtype):
        out_dtype = None
    elif bqc__sqoh in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(bqc__sqoh, 1, 'C')
    elif kgtcm__mjs in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(kgtcm__mjs, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(bqc__sqoh), numba.np.numpy_support.
            as_dtype(kgtcm__mjs)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(bqc__sqoh, bodo.PDCategoricalDtype):
        htuml__yqol = 'x'
    else:
        htuml__yqol = 'out_dtype'
    omi__znhy += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {htuml__yqol}, (-1,))\n')
    if isinstance(bqc__sqoh, bodo.PDCategoricalDtype):
        omi__znhy += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        omi__znhy += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    omi__znhy += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    omi__znhy += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if pzu__kyhuh:
        omi__znhy += '      if bodo.libs.array_kernels.isna(x, j):\n'
        omi__znhy += '        setna(out_arr, j)\n'
        omi__znhy += '        continue\n'
    if isinstance(bqc__sqoh, bodo.PDCategoricalDtype):
        omi__znhy += '      out_codes[j] = x_codes[j]\n'
    else:
        omi__znhy += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if pzu__kyhuh else 'x'))
    omi__znhy += '    else:\n'
    if ooiaw__gbz:
        omi__znhy += '      if bodo.libs.array_kernels.isna(y, j):\n'
        omi__znhy += '        setna(out_arr, j)\n'
        omi__znhy += '        continue\n'
    if haoik__jwmvl == types.none:
        if isinstance(bqc__sqoh, bodo.PDCategoricalDtype):
            omi__znhy += '      out_codes[j] = -1\n'
        else:
            omi__znhy += '      setna(out_arr, j)\n'
    else:
        omi__znhy += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if ooiaw__gbz else 'y'))
    omi__znhy += '  return out_arr\n'
    tjqu__jao = {}
    exec(omi__znhy, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, tjqu__jao)
    dkay__bqdgo = tjqu__jao['_impl']
    return dkay__bqdgo


def _verify_np_select_arg_typs(condlist, choicelist, default):
    if isinstance(condlist, (types.List, types.UniTuple)):
        if not (bodo.utils.utils.is_np_array_typ(condlist.dtype) and 
            condlist.dtype.dtype == types.bool_):
            raise BodoError(
                "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
                )
    else:
        raise BodoError(
            "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
            )
    if not isinstance(choicelist, (types.List, types.UniTuple, types.BaseTuple)
        ):
        raise BodoError(
            "np.select(): 'choicelist' argument must be list or tuple type")
    if isinstance(choicelist, (types.List, types.UniTuple)):
        ikzgn__bxdrx = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(ikzgn__bxdrx, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(ikzgn__bxdrx):
            vuqb__pphc = ikzgn__bxdrx.data.dtype
        else:
            vuqb__pphc = ikzgn__bxdrx.dtype
        if isinstance(vuqb__pphc, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        ewhon__hwwn = ikzgn__bxdrx
    else:
        dtnih__oft = []
        for ikzgn__bxdrx in choicelist:
            if not bodo.utils.utils.is_array_typ(ikzgn__bxdrx, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(ikzgn__bxdrx):
                vuqb__pphc = ikzgn__bxdrx.data.dtype
            else:
                vuqb__pphc = ikzgn__bxdrx.dtype
            if isinstance(vuqb__pphc, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            dtnih__oft.append(vuqb__pphc)
        if not is_common_scalar_dtype(dtnih__oft):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        ewhon__hwwn = choicelist[0]
    if is_series_type(ewhon__hwwn):
        ewhon__hwwn = ewhon__hwwn.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, ewhon__hwwn.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(ewhon__hwwn, types.Array) or isinstance(ewhon__hwwn,
        BooleanArrayType) or isinstance(ewhon__hwwn, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(ewhon__hwwn, False) and ewhon__hwwn.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {ewhon__hwwn} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    iulv__ypi = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        zmh__bxpxd = choicelist.dtype
    else:
        rlfz__txzt = False
        dtnih__oft = []
        for ikzgn__bxdrx in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                ikzgn__bxdrx, 'numpy.select()')
            if is_nullable_type(ikzgn__bxdrx):
                rlfz__txzt = True
            if is_series_type(ikzgn__bxdrx):
                vuqb__pphc = ikzgn__bxdrx.data.dtype
            else:
                vuqb__pphc = ikzgn__bxdrx.dtype
            if isinstance(vuqb__pphc, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            dtnih__oft.append(vuqb__pphc)
        lawot__whd, ujafn__foje = get_common_scalar_dtype(dtnih__oft)
        if not ujafn__foje:
            raise BodoError('Internal error in overload_np_select')
        chlzb__cowxk = dtype_to_array_type(lawot__whd)
        if rlfz__txzt:
            chlzb__cowxk = to_nullable_type(chlzb__cowxk)
        zmh__bxpxd = chlzb__cowxk
    if isinstance(zmh__bxpxd, SeriesType):
        zmh__bxpxd = zmh__bxpxd.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pjdq__fuyf = True
    else:
        pjdq__fuyf = False
    vcun__cwsti = False
    vnoha__nkn = False
    if pjdq__fuyf:
        if isinstance(zmh__bxpxd.dtype, types.Number):
            pass
        elif zmh__bxpxd.dtype == types.bool_:
            vnoha__nkn = True
        else:
            vcun__cwsti = True
            zmh__bxpxd = to_nullable_type(zmh__bxpxd)
    elif default == types.none or is_overload_constant_nan(default):
        vcun__cwsti = True
        zmh__bxpxd = to_nullable_type(zmh__bxpxd)
    omi__znhy = 'def np_select_impl(condlist, choicelist, default=0):\n'
    omi__znhy += '  if len(condlist) != len(choicelist):\n'
    omi__znhy += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    omi__znhy += '  output_len = len(choicelist[0])\n'
    omi__znhy += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    omi__znhy += '  for i in range(output_len):\n'
    if vcun__cwsti:
        omi__znhy += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif vnoha__nkn:
        omi__znhy += '    out[i] = False\n'
    else:
        omi__znhy += '    out[i] = default\n'
    if iulv__ypi:
        omi__znhy += '  for i in range(len(condlist) - 1, -1, -1):\n'
        omi__znhy += '    cond = condlist[i]\n'
        omi__znhy += '    choice = choicelist[i]\n'
        omi__znhy += '    out = np.where(cond, choice, out)\n'
    else:
        for orq__botb in range(len(choicelist) - 1, -1, -1):
            omi__znhy += f'  cond = condlist[{orq__botb}]\n'
            omi__znhy += f'  choice = choicelist[{orq__botb}]\n'
            omi__znhy += f'  out = np.where(cond, choice, out)\n'
    omi__znhy += '  return out'
    tjqu__jao = dict()
    exec(omi__znhy, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': zmh__bxpxd}, tjqu__jao)
    impl = tjqu__jao['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        utcwa__nixkv = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    iphg__sqqz = dict(subset=subset, keep=keep, inplace=inplace)
    qzu__yrnkk = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        uee__rzrx = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (uee__rzrx,), czkrq__jty = bodo.libs.array_kernels.drop_duplicates((
            uee__rzrx,), index, 1)
        index = bodo.utils.conversion.index_from_array(czkrq__jty)
        return bodo.hiframes.pd_series_ext.init_series(uee__rzrx, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    lbd__rgln = element_type(S.data)
    if not is_common_scalar_dtype([lbd__rgln, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([lbd__rgln, right]):
        raise_bodo_error(
            "Series.between(): 'right' must be compariable with the Series data"
            )
    if not is_overload_constant_str(inclusive) or get_overload_const_str(
        inclusive) not in ('both', 'neither'):
        raise_bodo_error(
            "Series.between(): 'inclusive' must be a constant string and one of ('both', 'neither')"
            )

    def impl(S, left, right, inclusive='both'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        utcwa__nixkv = np.empty(n, np.bool_)
        for orq__botb in numba.parfors.parfor.internal_prange(n):
            qat__sjjny = bodo.utils.conversion.box_if_dt64(arr[orq__botb])
            if inclusive == 'both':
                utcwa__nixkv[orq__botb
                    ] = qat__sjjny <= right and qat__sjjny >= left
            else:
                utcwa__nixkv[orq__botb
                    ] = qat__sjjny < right and qat__sjjny > left
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv, index,
            name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    iphg__sqqz = dict(axis=axis)
    qzu__yrnkk = dict(axis=None)
    check_unsupported_args('Series.repeat', iphg__sqqz, qzu__yrnkk,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Series.repeat(): 'repeats' should be an integer or array of integers"
            )
    if isinstance(repeats, types.Integer):

        def impl_int(S, repeats, axis=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            czkrq__jty = bodo.utils.conversion.index_to_array(index)
            utcwa__nixkv = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            ddnmm__qyb = bodo.libs.array_kernels.repeat_kernel(czkrq__jty,
                repeats)
            bvq__frko = bodo.utils.conversion.index_from_array(ddnmm__qyb)
            return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
                bvq__frko, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        czkrq__jty = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        utcwa__nixkv = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        ddnmm__qyb = bodo.libs.array_kernels.repeat_kernel(czkrq__jty, repeats)
        bvq__frko = bodo.utils.conversion.index_from_array(ddnmm__qyb)
        return bodo.hiframes.pd_series_ext.init_series(utcwa__nixkv,
            bvq__frko, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        lqv__wjceq = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(lqv__wjceq)
        yras__wfgtk = {}
        for orq__botb in range(n):
            qat__sjjny = bodo.utils.conversion.box_if_dt64(lqv__wjceq[
                orq__botb])
            yras__wfgtk[index[orq__botb]] = qat__sjjny
        return yras__wfgtk
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    jksiy__cxr = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            dorx__kcjro = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(jksiy__cxr)
    elif is_literal_type(name):
        dorx__kcjro = get_literal_value(name)
    else:
        raise_bodo_error(jksiy__cxr)
    dorx__kcjro = 0 if dorx__kcjro is None else dorx__kcjro
    kblkt__esy = ColNamesMetaType((dorx__kcjro,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            kblkt__esy)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
