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
            mav__uhn = bodo.hiframes.pd_series_ext.get_series_data(s)
            uad__riftr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(mav__uhn
                )
            return uad__riftr
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
            jvw__itiq = list()
            for hae__tunm in range(len(S)):
                jvw__itiq.append(S.iat[hae__tunm])
            return jvw__itiq
        return impl_float

    def impl(S):
        jvw__itiq = list()
        for hae__tunm in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, hae__tunm):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            jvw__itiq.append(S.iat[hae__tunm])
        return jvw__itiq
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    xnpk__eai = dict(dtype=dtype, copy=copy, na_value=na_value)
    brra__gdhb = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    xnpk__eai = dict(name=name, inplace=inplace)
    brra__gdhb = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', xnpk__eai, brra__gdhb,
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
        yrhfr__vtk = ', '.join(['index_arrs[{}]'.format(hae__tunm) for
            hae__tunm in range(S.index.nlevels)])
    else:
        yrhfr__vtk = '    bodo.utils.conversion.index_to_array(index)\n'
    ntdga__zoke = 'index' if 'index' != series_name else 'level_0'
    gidkk__qvpcd = get_index_names(S.index, 'Series.reset_index()', ntdga__zoke
        )
    columns = [name for name in gidkk__qvpcd]
    columns.append(series_name)
    wpcg__isc = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    wpcg__isc += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    wpcg__isc += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        wpcg__isc += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    wpcg__isc += (
        '    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)\n'
        )
    wpcg__isc += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({yrhfr__vtk}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    mwpcc__dxsz = {}
    exec(wpcg__isc, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, mwpcc__dxsz)
    rwpso__mjw = mwpcc__dxsz['_impl']
    return rwpso__mjw


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zufp__ftjw = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
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
        zufp__ftjw = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for hae__tunm in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[hae__tunm]):
                bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
            else:
                zufp__ftjw[hae__tunm] = np.round(arr[hae__tunm], decimals)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    xnpk__eai = dict(level=level, numeric_only=numeric_only)
    brra__gdhb = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(level=level, numeric_only=numeric_only)
    brra__gdhb = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    brra__gdhb = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', xnpk__eai, brra__gdhb,
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
        mnqmr__lri = bodo.hiframes.pd_series_ext.get_series_data(S)
        anums__zlt = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        ulpo__ziwt = 0
        for hae__tunm in numba.parfors.parfor.internal_prange(len(mnqmr__lri)):
            dqbp__ince = 0
            yntw__bdif = bodo.libs.array_kernels.isna(mnqmr__lri, hae__tunm)
            vxmju__eetg = bodo.libs.array_kernels.isna(anums__zlt, hae__tunm)
            if (yntw__bdif and not vxmju__eetg or not yntw__bdif and
                vxmju__eetg):
                dqbp__ince = 1
            elif not yntw__bdif:
                if mnqmr__lri[hae__tunm] != anums__zlt[hae__tunm]:
                    dqbp__ince = 1
            ulpo__ziwt += dqbp__ince
        return ulpo__ziwt == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    xnpk__eai = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    brra__gdhb = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    xnpk__eai = dict(level=level)
    brra__gdhb = dict(level=None)
    check_unsupported_args('Series.mad', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    yixsk__iwvj = types.float64
    vgst__ouh = types.float64
    if S.dtype == types.float32:
        yixsk__iwvj = types.float32
        vgst__ouh = types.float32
    qxgym__xee = yixsk__iwvj(0)
    ulpl__ufl = vgst__ouh(0)
    snqd__yiuk = vgst__ouh(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        gasz__ewo = qxgym__xee
        ulpo__ziwt = ulpl__ufl
        for hae__tunm in numba.parfors.parfor.internal_prange(len(A)):
            dqbp__ince = qxgym__xee
            afwu__ognyp = ulpl__ufl
            if not bodo.libs.array_kernels.isna(A, hae__tunm) or not skipna:
                dqbp__ince = A[hae__tunm]
                afwu__ognyp = snqd__yiuk
            gasz__ewo += dqbp__ince
            ulpo__ziwt += afwu__ognyp
        tgqr__eiw = bodo.hiframes.series_kernels._mean_handle_nan(gasz__ewo,
            ulpo__ziwt)
        zig__ezyjh = qxgym__xee
        for hae__tunm in numba.parfors.parfor.internal_prange(len(A)):
            dqbp__ince = qxgym__xee
            if not bodo.libs.array_kernels.isna(A, hae__tunm) or not skipna:
                dqbp__ince = abs(A[hae__tunm] - tgqr__eiw)
            zig__ezyjh += dqbp__ince
        nkkh__uca = bodo.hiframes.series_kernels._mean_handle_nan(zig__ezyjh,
            ulpo__ziwt)
        return nkkh__uca
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    xnpk__eai = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    brra__gdhb = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(level=level, numeric_only=numeric_only)
    brra__gdhb = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', xnpk__eai, brra__gdhb,
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
        keou__bqdbz = 0
        oqj__etbv = 0
        ulpo__ziwt = 0
        for hae__tunm in numba.parfors.parfor.internal_prange(len(A)):
            dqbp__ince = 0
            afwu__ognyp = 0
            if not bodo.libs.array_kernels.isna(A, hae__tunm) or not skipna:
                dqbp__ince = A[hae__tunm]
                afwu__ognyp = 1
            keou__bqdbz += dqbp__ince
            oqj__etbv += dqbp__ince * dqbp__ince
            ulpo__ziwt += afwu__ognyp
        tksfc__zvi = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            keou__bqdbz, oqj__etbv, ulpo__ziwt, ddof)
        rjoy__npx = bodo.hiframes.series_kernels._sem_handle_nan(tksfc__zvi,
            ulpo__ziwt)
        return rjoy__npx
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    xnpk__eai = dict(level=level, numeric_only=numeric_only)
    brra__gdhb = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', xnpk__eai, brra__gdhb,
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
        keou__bqdbz = 0.0
        oqj__etbv = 0.0
        aifnp__wolif = 0.0
        ptf__gdj = 0.0
        ulpo__ziwt = 0
        for hae__tunm in numba.parfors.parfor.internal_prange(len(A)):
            dqbp__ince = 0.0
            afwu__ognyp = 0
            if not bodo.libs.array_kernels.isna(A, hae__tunm) or not skipna:
                dqbp__ince = np.float64(A[hae__tunm])
                afwu__ognyp = 1
            keou__bqdbz += dqbp__ince
            oqj__etbv += dqbp__ince ** 2
            aifnp__wolif += dqbp__ince ** 3
            ptf__gdj += dqbp__ince ** 4
            ulpo__ziwt += afwu__ognyp
        tksfc__zvi = bodo.hiframes.series_kernels.compute_kurt(keou__bqdbz,
            oqj__etbv, aifnp__wolif, ptf__gdj, ulpo__ziwt)
        return tksfc__zvi
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    xnpk__eai = dict(level=level, numeric_only=numeric_only)
    brra__gdhb = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', xnpk__eai, brra__gdhb,
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
        keou__bqdbz = 0.0
        oqj__etbv = 0.0
        aifnp__wolif = 0.0
        ulpo__ziwt = 0
        for hae__tunm in numba.parfors.parfor.internal_prange(len(A)):
            dqbp__ince = 0.0
            afwu__ognyp = 0
            if not bodo.libs.array_kernels.isna(A, hae__tunm) or not skipna:
                dqbp__ince = np.float64(A[hae__tunm])
                afwu__ognyp = 1
            keou__bqdbz += dqbp__ince
            oqj__etbv += dqbp__ince ** 2
            aifnp__wolif += dqbp__ince ** 3
            ulpo__ziwt += afwu__ognyp
        tksfc__zvi = bodo.hiframes.series_kernels.compute_skew(keou__bqdbz,
            oqj__etbv, aifnp__wolif, ulpo__ziwt)
        return tksfc__zvi
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    xnpk__eai = dict(level=level, numeric_only=numeric_only)
    brra__gdhb = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(level=level, numeric_only=numeric_only)
    brra__gdhb = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', xnpk__eai, brra__gdhb,
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
        mnqmr__lri = bodo.hiframes.pd_series_ext.get_series_data(S)
        anums__zlt = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        hbe__osmew = 0
        for hae__tunm in numba.parfors.parfor.internal_prange(len(mnqmr__lri)):
            gdkg__umvl = mnqmr__lri[hae__tunm]
            qmsk__ajqt = anums__zlt[hae__tunm]
            hbe__osmew += gdkg__umvl * qmsk__ajqt
        return hbe__osmew
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    xnpk__eai = dict(skipna=skipna)
    brra__gdhb = dict(skipna=True)
    check_unsupported_args('Series.cumsum', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(skipna=skipna)
    brra__gdhb = dict(skipna=True)
    check_unsupported_args('Series.cumprod', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(skipna=skipna)
    brra__gdhb = dict(skipna=True)
    check_unsupported_args('Series.cummin', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(skipna=skipna)
    brra__gdhb = dict(skipna=True)
    check_unsupported_args('Series.cummax', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    brra__gdhb = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        gotx__ybkz = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, gotx__ybkz, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    xnpk__eai = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    brra__gdhb = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(level=level)
    brra__gdhb = dict(level=None)
    check_unsupported_args('Series.count', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    xnpk__eai = dict(method=method, min_periods=min_periods)
    brra__gdhb = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        frlhq__ulan = S.sum()
        povg__ymjlu = other.sum()
        a = n * (S * other).sum() - frlhq__ulan * povg__ymjlu
        aqoql__oqzlj = n * (S ** 2).sum() - frlhq__ulan ** 2
        vsu__epl = n * (other ** 2).sum() - povg__ymjlu ** 2
        return a / np.sqrt(aqoql__oqzlj * vsu__epl)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    xnpk__eai = dict(min_periods=min_periods)
    brra__gdhb = dict(min_periods=None)
    check_unsupported_args('Series.cov', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        frlhq__ulan = S.mean()
        povg__ymjlu = other.mean()
        planf__wsejl = ((S - frlhq__ulan) * (other - povg__ymjlu)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(planf__wsejl, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            qulh__qgm = np.sign(sum_val)
            return np.inf * qulh__qgm
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    xnpk__eai = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    brra__gdhb = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    brra__gdhb = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(axis=axis, skipna=skipna)
    brra__gdhb = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(axis=axis, skipna=skipna)
    brra__gdhb = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', xnpk__eai, brra__gdhb,
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
    xnpk__eai = dict(level=level, numeric_only=numeric_only)
    brra__gdhb = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', xnpk__eai, brra__gdhb,
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
        qrcu__fpipm = arr[:n]
        lxtls__qrm = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(qrcu__fpipm,
            lxtls__qrm, name)
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
        rpc__hvmfg = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qrcu__fpipm = arr[rpc__hvmfg:]
        lxtls__qrm = index[rpc__hvmfg:]
        return bodo.hiframes.pd_series_ext.init_series(qrcu__fpipm,
            lxtls__qrm, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    mxlz__wlkz = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in mxlz__wlkz:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            lnqjl__hhum = index[0]
            hpzam__ufj = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                lnqjl__hhum, False))
        else:
            hpzam__ufj = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qrcu__fpipm = arr[:hpzam__ufj]
        lxtls__qrm = index[:hpzam__ufj]
        return bodo.hiframes.pd_series_ext.init_series(qrcu__fpipm,
            lxtls__qrm, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    mxlz__wlkz = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in mxlz__wlkz:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            nlnqi__tpj = index[-1]
            hpzam__ufj = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                nlnqi__tpj, True))
        else:
            hpzam__ufj = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qrcu__fpipm = arr[len(arr) - hpzam__ufj:]
        lxtls__qrm = index[len(arr) - hpzam__ufj:]
        return bodo.hiframes.pd_series_ext.init_series(qrcu__fpipm,
            lxtls__qrm, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        tkrlc__ijk = bodo.utils.conversion.index_to_array(index)
        gdr__hxv, fto__heq = bodo.libs.array_kernels.first_last_valid_index(arr
            , tkrlc__ijk)
        return fto__heq if gdr__hxv else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        tkrlc__ijk = bodo.utils.conversion.index_to_array(index)
        gdr__hxv, fto__heq = bodo.libs.array_kernels.first_last_valid_index(arr
            , tkrlc__ijk, False)
        return fto__heq if gdr__hxv else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    xnpk__eai = dict(keep=keep)
    brra__gdhb = dict(keep='first')
    check_unsupported_args('Series.nlargest', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        tkrlc__ijk = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zufp__ftjw, rnltq__jhqx = bodo.libs.array_kernels.nlargest(arr,
            tkrlc__ijk, n, True, bodo.hiframes.series_kernels.gt_f)
        pxv__tkv = bodo.utils.conversion.convert_to_index(rnltq__jhqx)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, pxv__tkv,
            name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    xnpk__eai = dict(keep=keep)
    brra__gdhb = dict(keep='first')
    check_unsupported_args('Series.nsmallest', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        tkrlc__ijk = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zufp__ftjw, rnltq__jhqx = bodo.libs.array_kernels.nlargest(arr,
            tkrlc__ijk, n, False, bodo.hiframes.series_kernels.lt_f)
        pxv__tkv = bodo.utils.conversion.convert_to_index(rnltq__jhqx)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, pxv__tkv,
            name)
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
    xnpk__eai = dict(errors=errors)
    brra__gdhb = dict(errors='raise')
    check_unsupported_args('Series.astype', xnpk__eai, brra__gdhb,
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
        zufp__ftjw = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    xnpk__eai = dict(axis=axis, is_copy=is_copy)
    brra__gdhb = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        xey__thfg = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[xey__thfg],
            index[xey__thfg], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    xnpk__eai = dict(axis=axis, kind=kind, order=order)
    brra__gdhb = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ugkbw__htu = S.notna().values
        if not ugkbw__htu.all():
            zufp__ftjw = np.full(n, -1, np.int64)
            zufp__ftjw[ugkbw__htu] = argsort(arr[ugkbw__htu])
        else:
            zufp__ftjw = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    xnpk__eai = dict(axis=axis, numeric_only=numeric_only)
    brra__gdhb = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', xnpk__eai, brra__gdhb,
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
        zufp__ftjw = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    xnpk__eai = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    brra__gdhb = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    xsu__ecxwb = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        xyr__ouxg = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, xsu__ecxwb)
        bph__hsj = xyr__ouxg.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        zufp__ftjw = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(bph__hsj
            , 0)
        pxv__tkv = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(bph__hsj)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, pxv__tkv,
            name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    xnpk__eai = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    brra__gdhb = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    dmxs__zym = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        xyr__ouxg = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, dmxs__zym)
        bph__hsj = xyr__ouxg.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        zufp__ftjw = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(bph__hsj
            , 0)
        pxv__tkv = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(bph__hsj)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, pxv__tkv,
            name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    uja__pwmo = is_overload_true(is_nullable)
    wpcg__isc = 'def impl(bins, arr, is_nullable=True, include_lowest=True):\n'
    wpcg__isc += '  numba.parfors.parfor.init_prange()\n'
    wpcg__isc += '  n = len(arr)\n'
    if uja__pwmo:
        wpcg__isc += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        wpcg__isc += '  out_arr = np.empty(n, np.int64)\n'
    wpcg__isc += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    wpcg__isc += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if uja__pwmo:
        wpcg__isc += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        wpcg__isc += '      out_arr[i] = -1\n'
    wpcg__isc += '      continue\n'
    wpcg__isc += '    val = arr[i]\n'
    wpcg__isc += '    if include_lowest and val == bins[0]:\n'
    wpcg__isc += '      ind = 1\n'
    wpcg__isc += '    else:\n'
    wpcg__isc += '      ind = np.searchsorted(bins, val)\n'
    wpcg__isc += '    if ind == 0 or ind == len(bins):\n'
    if uja__pwmo:
        wpcg__isc += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        wpcg__isc += '      out_arr[i] = -1\n'
    wpcg__isc += '    else:\n'
    wpcg__isc += '      out_arr[i] = ind - 1\n'
    wpcg__isc += '  return out_arr\n'
    mwpcc__dxsz = {}
    exec(wpcg__isc, {'bodo': bodo, 'np': np, 'numba': numba}, mwpcc__dxsz)
    impl = mwpcc__dxsz['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        lphp__dph, clil__hpffv = np.divmod(x, 1)
        if lphp__dph == 0:
            thul__bbhv = -int(np.floor(np.log10(abs(clil__hpffv)))
                ) - 1 + precision
        else:
            thul__bbhv = precision
        return np.around(x, thul__bbhv)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        iotiy__sys = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(iotiy__sys)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        mlekn__xorjv = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            nowzx__gmo = bins.copy()
            if right and include_lowest:
                nowzx__gmo[0] = nowzx__gmo[0] - mlekn__xorjv
            ecj__vdcen = bodo.libs.interval_arr_ext.init_interval_array(
                nowzx__gmo[:-1], nowzx__gmo[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(ecj__vdcen,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        nowzx__gmo = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            nowzx__gmo[0] = nowzx__gmo[0] - 10.0 ** -precision
        ecj__vdcen = bodo.libs.interval_arr_ext.init_interval_array(nowzx__gmo
            [:-1], nowzx__gmo[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(ecj__vdcen, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        gytn__wwdm = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        rslkh__yxlk = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        zufp__ftjw = np.zeros(nbins, np.int64)
        for hae__tunm in range(len(gytn__wwdm)):
            zufp__ftjw[rslkh__yxlk[hae__tunm]] = gytn__wwdm[hae__tunm]
        return zufp__ftjw
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
            poc__fufb = (max_val - min_val) * 0.001
            if right:
                bins[0] -= poc__fufb
            else:
                bins[-1] += poc__fufb
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    xnpk__eai = dict(dropna=dropna)
    brra__gdhb = dict(dropna=True)
    check_unsupported_args('Series.value_counts', xnpk__eai, brra__gdhb,
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
    uvp__dqy = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    wpcg__isc = 'def impl(\n'
    wpcg__isc += '    S,\n'
    wpcg__isc += '    normalize=False,\n'
    wpcg__isc += '    sort=True,\n'
    wpcg__isc += '    ascending=False,\n'
    wpcg__isc += '    bins=None,\n'
    wpcg__isc += '    dropna=True,\n'
    wpcg__isc += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    wpcg__isc += '):\n'
    wpcg__isc += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    wpcg__isc += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    wpcg__isc += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if uvp__dqy:
        wpcg__isc += '    right = True\n'
        wpcg__isc += _gen_bins_handling(bins, S.dtype)
        wpcg__isc += '    arr = get_bin_inds(bins, arr)\n'
    wpcg__isc += '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n'
    wpcg__isc += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    wpcg__isc += '    )\n'
    wpcg__isc += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if uvp__dqy:
        wpcg__isc += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        wpcg__isc += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        wpcg__isc += '    index = get_bin_labels(bins)\n'
    else:
        wpcg__isc += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        wpcg__isc += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        wpcg__isc += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        wpcg__isc += '    )\n'
        wpcg__isc += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    wpcg__isc += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        wpcg__isc += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        lpgp__pymwi = 'len(S)' if uvp__dqy else 'count_arr.sum()'
        wpcg__isc += f'    res = res / float({lpgp__pymwi})\n'
    wpcg__isc += '    return res\n'
    mwpcc__dxsz = {}
    exec(wpcg__isc, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, mwpcc__dxsz)
    impl = mwpcc__dxsz['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    wpcg__isc = ''
    if isinstance(bins, types.Integer):
        wpcg__isc += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        wpcg__isc += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            wpcg__isc += '    min_val = min_val.value\n'
            wpcg__isc += '    max_val = max_val.value\n'
        wpcg__isc += '    bins = compute_bins(bins, min_val, max_val, right)\n'
        if dtype == bodo.datetime64ns:
            wpcg__isc += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        wpcg__isc += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return wpcg__isc


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    xnpk__eai = dict(right=right, labels=labels, retbins=retbins, precision
        =precision, duplicates=duplicates, ordered=ordered)
    brra__gdhb = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    wpcg__isc = 'def impl(\n'
    wpcg__isc += '    x,\n'
    wpcg__isc += '    bins,\n'
    wpcg__isc += '    right=True,\n'
    wpcg__isc += '    labels=None,\n'
    wpcg__isc += '    retbins=False,\n'
    wpcg__isc += '    precision=3,\n'
    wpcg__isc += '    include_lowest=False,\n'
    wpcg__isc += "    duplicates='raise',\n"
    wpcg__isc += '    ordered=True\n'
    wpcg__isc += '):\n'
    if isinstance(x, SeriesType):
        wpcg__isc += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        wpcg__isc += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        wpcg__isc += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        wpcg__isc += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    wpcg__isc += _gen_bins_handling(bins, x.dtype)
    wpcg__isc += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    wpcg__isc += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    wpcg__isc += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    wpcg__isc += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        wpcg__isc += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        wpcg__isc += '    return res\n'
    else:
        wpcg__isc += '    return out_arr\n'
    mwpcc__dxsz = {}
    exec(wpcg__isc, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, mwpcc__dxsz)
    impl = mwpcc__dxsz['impl']
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
    xnpk__eai = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    brra__gdhb = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        tdfn__vdhwd = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, tdfn__vdhwd)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    xnpk__eai = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    brra__gdhb = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', xnpk__eai, brra__gdhb,
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
        ezno__had = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            jra__afsr = bodo.utils.conversion.coerce_to_array(index)
            xyr__ouxg = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                jra__afsr, arr), index, ezno__had)
            return xyr__ouxg.groupby(' ')['']
        return impl_index
    frnq__yzia = by
    if isinstance(by, SeriesType):
        frnq__yzia = by.data
    if isinstance(frnq__yzia, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    sxskg__fmsxq = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        jra__afsr = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        xyr__ouxg = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            jra__afsr, arr), index, sxskg__fmsxq)
        return xyr__ouxg.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    xnpk__eai = dict(verify_integrity=verify_integrity)
    brra__gdhb = dict(verify_integrity=False)
    check_unsupported_args('Series.append', xnpk__eai, brra__gdhb,
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
            ihjd__wghqj = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            zufp__ftjw = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(zufp__ftjw, A, ihjd__wghqj, False)
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zufp__ftjw = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    xnpk__eai = dict(interpolation=interpolation)
    brra__gdhb = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            zufp__ftjw = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
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
        qho__rmfzu = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(qho__rmfzu, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    xnpk__eai = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    brra__gdhb = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', xnpk__eai, brra__gdhb,
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
        ssaq__uaf = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ssaq__uaf = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    wpcg__isc = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {ssaq__uaf}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    ruaaz__lqwni = dict()
    exec(wpcg__isc, {'bodo': bodo, 'numba': numba}, ruaaz__lqwni)
    ovj__zekl = ruaaz__lqwni['impl']
    return ovj__zekl


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        ssaq__uaf = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ssaq__uaf = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    wpcg__isc = 'def impl(S,\n'
    wpcg__isc += '     value=None,\n'
    wpcg__isc += '    method=None,\n'
    wpcg__isc += '    axis=None,\n'
    wpcg__isc += '    inplace=False,\n'
    wpcg__isc += '    limit=None,\n'
    wpcg__isc += '   downcast=None,\n'
    wpcg__isc += '):\n'
    wpcg__isc += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    wpcg__isc += '    n = len(in_arr)\n'
    wpcg__isc += f'    out_arr = {ssaq__uaf}(n, -1)\n'
    wpcg__isc += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    wpcg__isc += '        s = in_arr[j]\n'
    wpcg__isc += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    wpcg__isc += '            s = value\n'
    wpcg__isc += '        out_arr[j] = s\n'
    wpcg__isc += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    ruaaz__lqwni = dict()
    exec(wpcg__isc, {'bodo': bodo, 'numba': numba}, ruaaz__lqwni)
    ovj__zekl = ruaaz__lqwni['impl']
    return ovj__zekl


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
    yauas__iod = bodo.hiframes.pd_series_ext.get_series_data(value)
    for hae__tunm in numba.parfors.parfor.internal_prange(len(zimgf__igm)):
        s = zimgf__igm[hae__tunm]
        if bodo.libs.array_kernels.isna(zimgf__igm, hae__tunm
            ) and not bodo.libs.array_kernels.isna(yauas__iod, hae__tunm):
            s = yauas__iod[hae__tunm]
        zimgf__igm[hae__tunm] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
    for hae__tunm in numba.parfors.parfor.internal_prange(len(zimgf__igm)):
        s = zimgf__igm[hae__tunm]
        if bodo.libs.array_kernels.isna(zimgf__igm, hae__tunm):
            s = value
        zimgf__igm[hae__tunm] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    yauas__iod = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(zimgf__igm)
    zufp__ftjw = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for ifb__vyvj in numba.parfors.parfor.internal_prange(n):
        s = zimgf__igm[ifb__vyvj]
        if bodo.libs.array_kernels.isna(zimgf__igm, ifb__vyvj
            ) and not bodo.libs.array_kernels.isna(yauas__iod, ifb__vyvj):
            s = yauas__iod[ifb__vyvj]
        zufp__ftjw[ifb__vyvj] = s
        if bodo.libs.array_kernels.isna(zimgf__igm, ifb__vyvj
            ) and bodo.libs.array_kernels.isna(yauas__iod, ifb__vyvj):
            bodo.libs.array_kernels.setna(zufp__ftjw, ifb__vyvj)
    return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    yauas__iod = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(zimgf__igm)
    zufp__ftjw = bodo.utils.utils.alloc_type(n, zimgf__igm.dtype, (-1,))
    for hae__tunm in numba.parfors.parfor.internal_prange(n):
        s = zimgf__igm[hae__tunm]
        if bodo.libs.array_kernels.isna(zimgf__igm, hae__tunm
            ) and not bodo.libs.array_kernels.isna(yauas__iod, hae__tunm):
            s = yauas__iod[hae__tunm]
        zufp__ftjw[hae__tunm] = s
    return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    xnpk__eai = dict(limit=limit, downcast=downcast)
    brra__gdhb = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')
    cytda__dnhl = not is_overload_none(value)
    pdoop__mvvlb = not is_overload_none(method)
    if cytda__dnhl and pdoop__mvvlb:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not cytda__dnhl and not pdoop__mvvlb:
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
    if pdoop__mvvlb:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        wwku__ava = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(wwku__ava)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(wwku__ava)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    xed__fiu = element_type(S.data)
    kzgpu__icg = None
    if cytda__dnhl:
        kzgpu__icg = element_type(types.unliteral(value))
    if kzgpu__icg and not can_replace(xed__fiu, kzgpu__icg):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {kzgpu__icg} with series type {xed__fiu}'
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
        njhma__lolfl = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                yauas__iod = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(zimgf__igm)
                zufp__ftjw = bodo.utils.utils.alloc_type(n, njhma__lolfl, (-1,)
                    )
                for hae__tunm in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(zimgf__igm, hae__tunm
                        ) and bodo.libs.array_kernels.isna(yauas__iod,
                        hae__tunm):
                        bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                        continue
                    if bodo.libs.array_kernels.isna(zimgf__igm, hae__tunm):
                        zufp__ftjw[hae__tunm
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            yauas__iod[hae__tunm])
                        continue
                    zufp__ftjw[hae__tunm
                        ] = bodo.utils.conversion.unbox_if_timestamp(zimgf__igm
                        [hae__tunm])
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                    index, name)
            return fillna_series_impl
        if pdoop__mvvlb:
            lcs__prel = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(xed__fiu, (types.Integer, types.Float)
                ) and xed__fiu not in lcs__prel:
                raise BodoError(
                    f"Series.fillna(): series of type {xed__fiu} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                zufp__ftjw = bodo.libs.array_kernels.ffill_bfill_arr(zimgf__igm
                    , method)
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(zimgf__igm)
            zufp__ftjw = bodo.utils.utils.alloc_type(n, njhma__lolfl, (-1,))
            for hae__tunm in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(zimgf__igm[
                    hae__tunm])
                if bodo.libs.array_kernels.isna(zimgf__igm, hae__tunm):
                    s = value
                zufp__ftjw[hae__tunm] = s
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        qduy__xxl = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        xnpk__eai = dict(limit=limit, downcast=downcast)
        brra__gdhb = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', xnpk__eai,
            brra__gdhb, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        xed__fiu = element_type(S.data)
        lcs__prel = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(xed__fiu, (types.Integer, types.Float)
            ) and xed__fiu not in lcs__prel:
            raise BodoError(
                f'Series.{overload_name}(): series of type {xed__fiu} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            zufp__ftjw = bodo.libs.array_kernels.ffill_bfill_arr(zimgf__igm,
                qduy__xxl)
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        qgfdc__fgrk = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            qgfdc__fgrk)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        aqpj__yzm = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(aqpj__yzm)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        aqpj__yzm = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(aqpj__yzm)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        aqpj__yzm = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(aqpj__yzm)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    xnpk__eai = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    dsuvf__ygcp = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', xnpk__eai, dsuvf__ygcp,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    xed__fiu = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        ynmy__lqw = element_type(to_replace.key_type)
        kzgpu__icg = element_type(to_replace.value_type)
    else:
        ynmy__lqw = element_type(to_replace)
        kzgpu__icg = element_type(value)
    dek__toehd = None
    if xed__fiu != types.unliteral(ynmy__lqw):
        if bodo.utils.typing.equality_always_false(xed__fiu, types.
            unliteral(ynmy__lqw)
            ) or not bodo.utils.typing.types_equality_exists(xed__fiu,
            ynmy__lqw):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(xed__fiu, (types.Float, types.Integer)
            ) or xed__fiu == np.bool_:
            dek__toehd = xed__fiu
    if not can_replace(xed__fiu, types.unliteral(kzgpu__icg)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    yrl__iem = to_str_arr_if_dict_array(S.data)
    if isinstance(yrl__iem, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(zimgf__igm.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(zimgf__igm)
        zufp__ftjw = bodo.utils.utils.alloc_type(n, yrl__iem, (-1,))
        pro__sgrc = build_replace_dict(to_replace, value, dek__toehd)
        for hae__tunm in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(zimgf__igm, hae__tunm):
                bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                continue
            s = zimgf__igm[hae__tunm]
            if s in pro__sgrc:
                s = pro__sgrc[s]
            zufp__ftjw[hae__tunm] = s
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    lesce__zcxp = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    odtg__kfo = is_iterable_type(to_replace)
    bxulo__sys = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    xty__dxhxx = is_iterable_type(value)
    if lesce__zcxp and bxulo__sys:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                pro__sgrc = {}
                pro__sgrc[key_dtype_conv(to_replace)] = value
                return pro__sgrc
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            pro__sgrc = {}
            pro__sgrc[to_replace] = value
            return pro__sgrc
        return impl
    if odtg__kfo and bxulo__sys:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                pro__sgrc = {}
                for iflh__mbuua in to_replace:
                    pro__sgrc[key_dtype_conv(iflh__mbuua)] = value
                return pro__sgrc
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            pro__sgrc = {}
            for iflh__mbuua in to_replace:
                pro__sgrc[iflh__mbuua] = value
            return pro__sgrc
        return impl
    if odtg__kfo and xty__dxhxx:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                pro__sgrc = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for hae__tunm in range(len(to_replace)):
                    pro__sgrc[key_dtype_conv(to_replace[hae__tunm])] = value[
                        hae__tunm]
                return pro__sgrc
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            pro__sgrc = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for hae__tunm in range(len(to_replace)):
                pro__sgrc[to_replace[hae__tunm]] = value[hae__tunm]
            return pro__sgrc
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
            zufp__ftjw = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zufp__ftjw = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    xnpk__eai = dict(ignore_index=ignore_index)
    kmo__ayviy = dict(ignore_index=False)
    check_unsupported_args('Series.explode', xnpk__eai, kmo__ayviy,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        tkrlc__ijk = bodo.utils.conversion.index_to_array(index)
        zufp__ftjw, sqa__ybpb = bodo.libs.array_kernels.explode(arr, tkrlc__ijk
            )
        pxv__tkv = bodo.utils.conversion.index_from_array(sqa__ybpb)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, pxv__tkv,
            name)
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
            kbuq__ygq = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for hae__tunm in numba.parfors.parfor.internal_prange(n):
                kbuq__ygq[hae__tunm] = np.argmax(a[hae__tunm])
            return kbuq__ygq
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            ddipn__iceip = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for hae__tunm in numba.parfors.parfor.internal_prange(n):
                ddipn__iceip[hae__tunm] = np.argmin(a[hae__tunm])
            return ddipn__iceip
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
    xnpk__eai = dict(axis=axis, inplace=inplace, how=how)
    bvtm__ijlxu = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', xnpk__eai, bvtm__ijlxu,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ugkbw__htu = S.notna().values
            tkrlc__ijk = bodo.utils.conversion.extract_index_array(S)
            pxv__tkv = bodo.utils.conversion.convert_to_index(tkrlc__ijk[
                ugkbw__htu])
            zufp__ftjw = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(zimgf__igm))
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                pxv__tkv, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            tkrlc__ijk = bodo.utils.conversion.extract_index_array(S)
            ugkbw__htu = S.notna().values
            pxv__tkv = bodo.utils.conversion.convert_to_index(tkrlc__ijk[
                ugkbw__htu])
            zufp__ftjw = zimgf__igm[ugkbw__htu]
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                pxv__tkv, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    xnpk__eai = dict(freq=freq, axis=axis, fill_value=fill_value)
    brra__gdhb = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', xnpk__eai, brra__gdhb,
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
        zufp__ftjw = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    xnpk__eai = dict(fill_method=fill_method, limit=limit, freq=freq)
    brra__gdhb = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', xnpk__eai, brra__gdhb,
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
        zufp__ftjw = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
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
            devic__qfzvb = 'None'
        else:
            devic__qfzvb = 'other'
        wpcg__isc = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            wpcg__isc += '  cond = ~cond\n'
        wpcg__isc += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        wpcg__isc += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        wpcg__isc += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        wpcg__isc += f"""  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {devic__qfzvb})
"""
        wpcg__isc += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        mwpcc__dxsz = {}
        exec(wpcg__isc, {'bodo': bodo, 'np': np}, mwpcc__dxsz)
        impl = mwpcc__dxsz['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        qgfdc__fgrk = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(qgfdc__fgrk)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    xnpk__eai = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    brra__gdhb = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', xnpk__eai, brra__gdhb,
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
    dgiqb__mtgoo = is_overload_constant_nan(other)
    if not (is_default or dgiqb__mtgoo or is_scalar_type(other) or 
        isinstance(other, types.Array) and other.ndim >= 1 and other.ndim <=
        max_ndim or isinstance(other, SeriesType) and (isinstance(arr,
        types.Array) or arr.dtype in [bodo.string_type, bodo.bytes_type]) or
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
            kqgbx__lrw = arr.dtype.elem_type
        else:
            kqgbx__lrw = arr.dtype
        if is_iterable_type(other):
            xjl__skqpu = other.dtype
        elif dgiqb__mtgoo:
            xjl__skqpu = types.float64
        else:
            xjl__skqpu = types.unliteral(other)
        if not dgiqb__mtgoo and not is_common_scalar_dtype([kqgbx__lrw,
            xjl__skqpu]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        xnpk__eai = dict(level=level, axis=axis)
        brra__gdhb = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), xnpk__eai,
            brra__gdhb, package_name='pandas', module_name='Series')
        wqjc__khumh = other == string_type or is_overload_constant_str(other)
        itc__wjvts = is_iterable_type(other) and other.dtype == string_type
        nwz__hzz = S.dtype == string_type and (op == operator.add and (
            wqjc__khumh or itc__wjvts) or op == operator.mul and isinstance
            (other, types.Integer))
        wur__cmzh = S.dtype == bodo.timedelta64ns
        fyyij__tcsk = S.dtype == bodo.datetime64ns
        rcst__jyhn = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        ibqqe__yykyb = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        brud__hzc = wur__cmzh and (rcst__jyhn or ibqqe__yykyb
            ) or fyyij__tcsk and rcst__jyhn
        brud__hzc = brud__hzc and op == operator.add
        if not (isinstance(S.dtype, types.Number) or nwz__hzz or brud__hzc):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        ndd__xcu = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            yrl__iem = ndd__xcu.resolve_function_type(op, args, {}).return_type
            if isinstance(S.data, IntegerArrayType
                ) and yrl__iem == types.Array(types.bool_, 1, 'C'):
                yrl__iem = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                zufp__ftjw = bodo.utils.utils.alloc_type(n, yrl__iem, (-1,))
                for hae__tunm in numba.parfors.parfor.internal_prange(n):
                    bvrd__iduvk = bodo.libs.array_kernels.isna(arr, hae__tunm)
                    if bvrd__iduvk:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm
                                )
                        else:
                            zufp__ftjw[hae__tunm] = op(fill_value, other)
                    else:
                        zufp__ftjw[hae__tunm] = op(arr[hae__tunm], other)
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        yrl__iem = ndd__xcu.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and yrl__iem == types.Array(
            types.bool_, 1, 'C'):
            yrl__iem = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            tejcm__esni = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            zufp__ftjw = bodo.utils.utils.alloc_type(n, yrl__iem, (-1,))
            for hae__tunm in numba.parfors.parfor.internal_prange(n):
                bvrd__iduvk = bodo.libs.array_kernels.isna(arr, hae__tunm)
                kxhx__xskz = bodo.libs.array_kernels.isna(tejcm__esni,
                    hae__tunm)
                if bvrd__iduvk and kxhx__xskz:
                    bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                elif bvrd__iduvk:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                    else:
                        zufp__ftjw[hae__tunm] = op(fill_value, tejcm__esni[
                            hae__tunm])
                elif kxhx__xskz:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                    else:
                        zufp__ftjw[hae__tunm] = op(arr[hae__tunm], fill_value)
                else:
                    zufp__ftjw[hae__tunm] = op(arr[hae__tunm], tejcm__esni[
                        hae__tunm])
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
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
        ndd__xcu = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            yrl__iem = ndd__xcu.resolve_function_type(op, args, {}).return_type
            if isinstance(S.data, IntegerArrayType
                ) and yrl__iem == types.Array(types.bool_, 1, 'C'):
                yrl__iem = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                zufp__ftjw = bodo.utils.utils.alloc_type(n, yrl__iem, None)
                for hae__tunm in numba.parfors.parfor.internal_prange(n):
                    bvrd__iduvk = bodo.libs.array_kernels.isna(arr, hae__tunm)
                    if bvrd__iduvk:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm
                                )
                        else:
                            zufp__ftjw[hae__tunm] = op(other, fill_value)
                    else:
                        zufp__ftjw[hae__tunm] = op(other, arr[hae__tunm])
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        yrl__iem = ndd__xcu.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and yrl__iem == types.Array(
            types.bool_, 1, 'C'):
            yrl__iem = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            tejcm__esni = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            zufp__ftjw = bodo.utils.utils.alloc_type(n, yrl__iem, None)
            for hae__tunm in numba.parfors.parfor.internal_prange(n):
                bvrd__iduvk = bodo.libs.array_kernels.isna(arr, hae__tunm)
                kxhx__xskz = bodo.libs.array_kernels.isna(tejcm__esni,
                    hae__tunm)
                zufp__ftjw[hae__tunm] = op(tejcm__esni[hae__tunm], arr[
                    hae__tunm])
                if bvrd__iduvk and kxhx__xskz:
                    bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                elif bvrd__iduvk:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                    else:
                        zufp__ftjw[hae__tunm] = op(tejcm__esni[hae__tunm],
                            fill_value)
                elif kxhx__xskz:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                    else:
                        zufp__ftjw[hae__tunm] = op(fill_value, arr[hae__tunm])
                else:
                    zufp__ftjw[hae__tunm] = op(tejcm__esni[hae__tunm], arr[
                        hae__tunm])
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
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
    for op, qhddi__gcb in explicit_binop_funcs_two_ways.items():
        for name in qhddi__gcb:
            qgfdc__fgrk = create_explicit_binary_op_overload(op)
            euvsh__qnoxj = create_explicit_binary_reverse_op_overload(op)
            tljm__ejfp = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(qgfdc__fgrk)
            overload_method(SeriesType, tljm__ejfp, no_unliteral=True)(
                euvsh__qnoxj)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        qgfdc__fgrk = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(qgfdc__fgrk)
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
                kecj__mhjjr = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                zufp__ftjw = dt64_arr_sub(arr, kecj__mhjjr)
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
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
                zufp__ftjw = np.empty(n, np.dtype('datetime64[ns]'))
                for hae__tunm in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, hae__tunm):
                        bodo.libs.array_kernels.setna(zufp__ftjw, hae__tunm)
                        continue
                    dzhcb__syvnw = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[hae__tunm]))
                    miabl__nfr = op(dzhcb__syvnw, rhs)
                    zufp__ftjw[hae__tunm
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        miabl__nfr.value)
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
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
                    kecj__mhjjr = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    zufp__ftjw = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(kecj__mhjjr))
                    return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kecj__mhjjr = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                zufp__ftjw = op(arr, kecj__mhjjr)
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    vbrt__nmc = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    zufp__ftjw = op(bodo.utils.conversion.
                        unbox_if_timestamp(vbrt__nmc), arr)
                    return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                vbrt__nmc = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                zufp__ftjw = op(vbrt__nmc, arr)
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        qgfdc__fgrk = create_binary_op_overload(op)
        overload(op)(qgfdc__fgrk)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    bfj__ukw = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, bfj__ukw)
        for hae__tunm in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, hae__tunm
                ) or bodo.libs.array_kernels.isna(arg2, hae__tunm):
                bodo.libs.array_kernels.setna(S, hae__tunm)
                continue
            S[hae__tunm
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                hae__tunm]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[hae__tunm]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                tejcm__esni = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, tejcm__esni)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        qgfdc__fgrk = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(qgfdc__fgrk)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                zufp__ftjw = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        qgfdc__fgrk = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(qgfdc__fgrk)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    zufp__ftjw = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                        index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    tejcm__esni = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    zufp__ftjw = ufunc(arr, tejcm__esni)
                    return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    tejcm__esni = bodo.hiframes.pd_series_ext.get_series_data(
                        S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    zufp__ftjw = ufunc(arr, tejcm__esni)
                    return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        qgfdc__fgrk = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(qgfdc__fgrk)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        cbfp__gsoet = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.
            copy(),))
        mav__uhn = np.arange(n),
        bodo.libs.timsort.sort(cbfp__gsoet, 0, n, mav__uhn)
        return mav__uhn[0]
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
        zzes__aswf = get_overload_const_str(downcast)
        if zzes__aswf in ('integer', 'signed'):
            out_dtype = types.int64
        elif zzes__aswf == 'unsigned':
            out_dtype = types.uint64
        else:
            assert zzes__aswf == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            zimgf__igm = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            zufp__ftjw = pd.to_numeric(zimgf__igm, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            ukr__rnode = np.empty(n, np.float64)
            for hae__tunm in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, hae__tunm):
                    bodo.libs.array_kernels.setna(ukr__rnode, hae__tunm)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(ukr__rnode,
                        hae__tunm, arg_a, hae__tunm)
            return ukr__rnode
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            ukr__rnode = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for hae__tunm in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, hae__tunm):
                    bodo.libs.array_kernels.setna(ukr__rnode, hae__tunm)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(ukr__rnode,
                        hae__tunm, arg_a, hae__tunm)
            return ukr__rnode
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        qsg__hger = if_series_to_array_type(args[0])
        if isinstance(qsg__hger, types.Array) and isinstance(qsg__hger.
            dtype, types.Integer):
            qsg__hger = types.Array(types.float64, 1, 'C')
        return qsg__hger(*args)


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
    xqhli__lxks = bodo.utils.utils.is_array_typ(x, True)
    tavvz__aqm = bodo.utils.utils.is_array_typ(y, True)
    wpcg__isc = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        wpcg__isc += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if xqhli__lxks and not bodo.utils.utils.is_array_typ(x, False):
        wpcg__isc += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if tavvz__aqm and not bodo.utils.utils.is_array_typ(y, False):
        wpcg__isc += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    wpcg__isc += '  n = len(condition)\n'
    onmxm__gqruf = x.dtype if xqhli__lxks else types.unliteral(x)
    yazwl__rdve = y.dtype if tavvz__aqm else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        onmxm__gqruf = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        yazwl__rdve = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    vpooj__fru = get_data(x)
    xpi__wzfub = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(mav__uhn) for mav__uhn in
        [vpooj__fru, xpi__wzfub])
    if xpi__wzfub == types.none:
        if isinstance(onmxm__gqruf, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif vpooj__fru == xpi__wzfub and not is_nullable:
        out_dtype = dtype_to_array_type(onmxm__gqruf)
    elif onmxm__gqruf == string_type or yazwl__rdve == string_type:
        out_dtype = bodo.string_array_type
    elif vpooj__fru == bytes_type or (xqhli__lxks and onmxm__gqruf ==
        bytes_type) and (xpi__wzfub == bytes_type or tavvz__aqm and 
        yazwl__rdve == bytes_type):
        out_dtype = binary_array_type
    elif isinstance(onmxm__gqruf, bodo.PDCategoricalDtype):
        out_dtype = None
    elif onmxm__gqruf in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(onmxm__gqruf, 1, 'C')
    elif yazwl__rdve in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(yazwl__rdve, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(onmxm__gqruf), numba.np.numpy_support.
            as_dtype(yazwl__rdve)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(onmxm__gqruf, bodo.PDCategoricalDtype):
        hcsm__nqlm = 'x'
    else:
        hcsm__nqlm = 'out_dtype'
    wpcg__isc += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {hcsm__nqlm}, (-1,))\n')
    if isinstance(onmxm__gqruf, bodo.PDCategoricalDtype):
        wpcg__isc += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        wpcg__isc += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    wpcg__isc += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    wpcg__isc += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if xqhli__lxks:
        wpcg__isc += '      if bodo.libs.array_kernels.isna(x, j):\n'
        wpcg__isc += '        setna(out_arr, j)\n'
        wpcg__isc += '        continue\n'
    if isinstance(onmxm__gqruf, bodo.PDCategoricalDtype):
        wpcg__isc += '      out_codes[j] = x_codes[j]\n'
    else:
        wpcg__isc += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if xqhli__lxks else 'x'))
    wpcg__isc += '    else:\n'
    if tavvz__aqm:
        wpcg__isc += '      if bodo.libs.array_kernels.isna(y, j):\n'
        wpcg__isc += '        setna(out_arr, j)\n'
        wpcg__isc += '        continue\n'
    if xpi__wzfub == types.none:
        if isinstance(onmxm__gqruf, bodo.PDCategoricalDtype):
            wpcg__isc += '      out_codes[j] = -1\n'
        else:
            wpcg__isc += '      setna(out_arr, j)\n'
    else:
        wpcg__isc += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if tavvz__aqm else 'y'))
    wpcg__isc += '  return out_arr\n'
    mwpcc__dxsz = {}
    exec(wpcg__isc, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, mwpcc__dxsz)
    rwpso__mjw = mwpcc__dxsz['_impl']
    return rwpso__mjw


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
        hzd__mnsj = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(hzd__mnsj, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(hzd__mnsj):
            zid__ptfvd = hzd__mnsj.data.dtype
        else:
            zid__ptfvd = hzd__mnsj.dtype
        if isinstance(zid__ptfvd, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        qhqqe__jxscv = hzd__mnsj
    else:
        nyw__yygc = []
        for hzd__mnsj in choicelist:
            if not bodo.utils.utils.is_array_typ(hzd__mnsj, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(hzd__mnsj):
                zid__ptfvd = hzd__mnsj.data.dtype
            else:
                zid__ptfvd = hzd__mnsj.dtype
            if isinstance(zid__ptfvd, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            nyw__yygc.append(zid__ptfvd)
        if not is_common_scalar_dtype(nyw__yygc):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        qhqqe__jxscv = choicelist[0]
    if is_series_type(qhqqe__jxscv):
        qhqqe__jxscv = qhqqe__jxscv.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, qhqqe__jxscv.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(qhqqe__jxscv, types.Array) or isinstance(
        qhqqe__jxscv, BooleanArrayType) or isinstance(qhqqe__jxscv,
        IntegerArrayType) or bodo.utils.utils.is_array_typ(qhqqe__jxscv, 
        False) and qhqqe__jxscv.dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {qhqqe__jxscv} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    uqddm__nak = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        fnuj__auxd = choicelist.dtype
    else:
        cuv__ynycs = False
        nyw__yygc = []
        for hzd__mnsj in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(hzd__mnsj
                , 'numpy.select()')
            if is_nullable_type(hzd__mnsj):
                cuv__ynycs = True
            if is_series_type(hzd__mnsj):
                zid__ptfvd = hzd__mnsj.data.dtype
            else:
                zid__ptfvd = hzd__mnsj.dtype
            if isinstance(zid__ptfvd, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            nyw__yygc.append(zid__ptfvd)
        sefy__ayvld, dwh__uxz = get_common_scalar_dtype(nyw__yygc)
        if not dwh__uxz:
            raise BodoError('Internal error in overload_np_select')
        zsafu__syrfw = dtype_to_array_type(sefy__ayvld)
        if cuv__ynycs:
            zsafu__syrfw = to_nullable_type(zsafu__syrfw)
        fnuj__auxd = zsafu__syrfw
    if isinstance(fnuj__auxd, SeriesType):
        fnuj__auxd = fnuj__auxd.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        xgbu__vzaq = True
    else:
        xgbu__vzaq = False
    uouwe__sbtyn = False
    roese__ncpnd = False
    if xgbu__vzaq:
        if isinstance(fnuj__auxd.dtype, types.Number):
            pass
        elif fnuj__auxd.dtype == types.bool_:
            roese__ncpnd = True
        else:
            uouwe__sbtyn = True
            fnuj__auxd = to_nullable_type(fnuj__auxd)
    elif default == types.none or is_overload_constant_nan(default):
        uouwe__sbtyn = True
        fnuj__auxd = to_nullable_type(fnuj__auxd)
    wpcg__isc = 'def np_select_impl(condlist, choicelist, default=0):\n'
    wpcg__isc += '  if len(condlist) != len(choicelist):\n'
    wpcg__isc += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    wpcg__isc += '  output_len = len(choicelist[0])\n'
    wpcg__isc += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    wpcg__isc += '  for i in range(output_len):\n'
    if uouwe__sbtyn:
        wpcg__isc += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif roese__ncpnd:
        wpcg__isc += '    out[i] = False\n'
    else:
        wpcg__isc += '    out[i] = default\n'
    if uqddm__nak:
        wpcg__isc += '  for i in range(len(condlist) - 1, -1, -1):\n'
        wpcg__isc += '    cond = condlist[i]\n'
        wpcg__isc += '    choice = choicelist[i]\n'
        wpcg__isc += '    out = np.where(cond, choice, out)\n'
    else:
        for hae__tunm in range(len(choicelist) - 1, -1, -1):
            wpcg__isc += f'  cond = condlist[{hae__tunm}]\n'
            wpcg__isc += f'  choice = choicelist[{hae__tunm}]\n'
            wpcg__isc += f'  out = np.where(cond, choice, out)\n'
    wpcg__isc += '  return out'
    mwpcc__dxsz = dict()
    exec(wpcg__isc, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': fnuj__auxd}, mwpcc__dxsz)
    impl = mwpcc__dxsz['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        zufp__ftjw = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    xnpk__eai = dict(subset=subset, keep=keep, inplace=inplace)
    brra__gdhb = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', xnpk__eai, brra__gdhb,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        vxnn__vbl = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (vxnn__vbl,), tkrlc__ijk = bodo.libs.array_kernels.drop_duplicates((
            vxnn__vbl,), index, 1)
        index = bodo.utils.conversion.index_from_array(tkrlc__ijk)
        return bodo.hiframes.pd_series_ext.init_series(vxnn__vbl, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    rzfif__skym = element_type(S.data)
    if not is_common_scalar_dtype([rzfif__skym, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([rzfif__skym, right]):
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
        zufp__ftjw = np.empty(n, np.bool_)
        for hae__tunm in numba.parfors.parfor.internal_prange(n):
            dqbp__ince = bodo.utils.conversion.box_if_dt64(arr[hae__tunm])
            if inclusive == 'both':
                zufp__ftjw[hae__tunm
                    ] = dqbp__ince <= right and dqbp__ince >= left
            else:
                zufp__ftjw[hae__tunm
                    ] = dqbp__ince < right and dqbp__ince > left
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    xnpk__eai = dict(axis=axis)
    brra__gdhb = dict(axis=None)
    check_unsupported_args('Series.repeat', xnpk__eai, brra__gdhb,
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
            tkrlc__ijk = bodo.utils.conversion.index_to_array(index)
            zufp__ftjw = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            sqa__ybpb = bodo.libs.array_kernels.repeat_kernel(tkrlc__ijk,
                repeats)
            pxv__tkv = bodo.utils.conversion.index_from_array(sqa__ybpb)
            return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw,
                pxv__tkv, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        tkrlc__ijk = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        zufp__ftjw = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        sqa__ybpb = bodo.libs.array_kernels.repeat_kernel(tkrlc__ijk, repeats)
        pxv__tkv = bodo.utils.conversion.index_from_array(sqa__ybpb)
        return bodo.hiframes.pd_series_ext.init_series(zufp__ftjw, pxv__tkv,
            name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        mav__uhn = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(mav__uhn)
        nfvzk__mxcy = {}
        for hae__tunm in range(n):
            dqbp__ince = bodo.utils.conversion.box_if_dt64(mav__uhn[hae__tunm])
            nfvzk__mxcy[index[hae__tunm]] = dqbp__ince
        return nfvzk__mxcy
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    wwku__ava = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            qoye__fuj = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(wwku__ava)
    elif is_literal_type(name):
        qoye__fuj = get_literal_value(name)
    else:
        raise_bodo_error(wwku__ava)
    qoye__fuj = 0 if qoye__fuj is None else qoye__fuj
    phoh__mwlbo = ColNamesMetaType((qoye__fuj,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            phoh__mwlbo)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
