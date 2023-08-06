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
            exif__kfp = bodo.hiframes.pd_series_ext.get_series_data(s)
            rotw__tme = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(exif__kfp
                )
            return rotw__tme
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
            jyabe__uun = list()
            for jnv__mrd in range(len(S)):
                jyabe__uun.append(S.iat[jnv__mrd])
            return jyabe__uun
        return impl_float

    def impl(S):
        jyabe__uun = list()
        for jnv__mrd in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, jnv__mrd):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            jyabe__uun.append(S.iat[jnv__mrd])
        return jyabe__uun
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    ikte__xfhaj = dict(dtype=dtype, copy=copy, na_value=na_value)
    uwcoc__ngbox = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    ikte__xfhaj = dict(name=name, inplace=inplace)
    uwcoc__ngbox = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', ikte__xfhaj, uwcoc__ngbox,
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
        hjmjf__dia = ', '.join(['index_arrs[{}]'.format(jnv__mrd) for
            jnv__mrd in range(S.index.nlevels)])
    else:
        hjmjf__dia = '    bodo.utils.conversion.index_to_array(index)\n'
    ghxbv__tbhv = 'index' if 'index' != series_name else 'level_0'
    ngttn__hhj = get_index_names(S.index, 'Series.reset_index()', ghxbv__tbhv)
    columns = [name for name in ngttn__hhj]
    columns.append(series_name)
    agsm__cgwh = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    agsm__cgwh += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    agsm__cgwh += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        agsm__cgwh += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    agsm__cgwh += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    agsm__cgwh += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({hjmjf__dia}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    fgysj__qevej = {}
    exec(agsm__cgwh, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, fgysj__qevej)
    lpwu__kkqkg = fgysj__qevej['_impl']
    return lpwu__kkqkg


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nvwoc__jpn = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
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
        nvwoc__jpn = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for jnv__mrd in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[jnv__mrd]):
                bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
            else:
                nvwoc__jpn[jnv__mrd] = np.round(arr[jnv__mrd], decimals)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    ikte__xfhaj = dict(level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    uwcoc__ngbox = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', ikte__xfhaj, uwcoc__ngbox,
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
        kzg__asssx = bodo.hiframes.pd_series_ext.get_series_data(S)
        omr__cdhwm = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        lfmk__rsgqn = 0
        for jnv__mrd in numba.parfors.parfor.internal_prange(len(kzg__asssx)):
            wyj__acse = 0
            bmgvp__conem = bodo.libs.array_kernels.isna(kzg__asssx, jnv__mrd)
            rng__ltnz = bodo.libs.array_kernels.isna(omr__cdhwm, jnv__mrd)
            if (bmgvp__conem and not rng__ltnz or not bmgvp__conem and
                rng__ltnz):
                wyj__acse = 1
            elif not bmgvp__conem:
                if kzg__asssx[jnv__mrd] != omr__cdhwm[jnv__mrd]:
                    wyj__acse = 1
            lfmk__rsgqn += wyj__acse
        return lfmk__rsgqn == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    ikte__xfhaj = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    uwcoc__ngbox = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    ikte__xfhaj = dict(level=level)
    uwcoc__ngbox = dict(level=None)
    check_unsupported_args('Series.mad', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    tqfk__poqfj = types.float64
    vfv__scxe = types.float64
    if S.dtype == types.float32:
        tqfk__poqfj = types.float32
        vfv__scxe = types.float32
    lnrpv__suuj = tqfk__poqfj(0)
    fmf__frh = vfv__scxe(0)
    nikvj__jsaq = vfv__scxe(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        oeg__pda = lnrpv__suuj
        lfmk__rsgqn = fmf__frh
        for jnv__mrd in numba.parfors.parfor.internal_prange(len(A)):
            wyj__acse = lnrpv__suuj
            tkie__azfev = fmf__frh
            if not bodo.libs.array_kernels.isna(A, jnv__mrd) or not skipna:
                wyj__acse = A[jnv__mrd]
                tkie__azfev = nikvj__jsaq
            oeg__pda += wyj__acse
            lfmk__rsgqn += tkie__azfev
        gqsut__zwvvp = bodo.hiframes.series_kernels._mean_handle_nan(oeg__pda,
            lfmk__rsgqn)
        bfn__lzucz = lnrpv__suuj
        for jnv__mrd in numba.parfors.parfor.internal_prange(len(A)):
            wyj__acse = lnrpv__suuj
            if not bodo.libs.array_kernels.isna(A, jnv__mrd) or not skipna:
                wyj__acse = abs(A[jnv__mrd] - gqsut__zwvvp)
            bfn__lzucz += wyj__acse
        atd__rhjop = bodo.hiframes.series_kernels._mean_handle_nan(bfn__lzucz,
            lfmk__rsgqn)
        return atd__rhjop
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    ikte__xfhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', ikte__xfhaj, uwcoc__ngbox,
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
        tzwl__bkpj = 0
        oihtw__dlwo = 0
        lfmk__rsgqn = 0
        for jnv__mrd in numba.parfors.parfor.internal_prange(len(A)):
            wyj__acse = 0
            tkie__azfev = 0
            if not bodo.libs.array_kernels.isna(A, jnv__mrd) or not skipna:
                wyj__acse = A[jnv__mrd]
                tkie__azfev = 1
            tzwl__bkpj += wyj__acse
            oihtw__dlwo += wyj__acse * wyj__acse
            lfmk__rsgqn += tkie__azfev
        ezmk__oyalb = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            tzwl__bkpj, oihtw__dlwo, lfmk__rsgqn, ddof)
        xlwy__dwkwq = bodo.hiframes.series_kernels._sem_handle_nan(ezmk__oyalb,
            lfmk__rsgqn)
        return xlwy__dwkwq
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    ikte__xfhaj = dict(level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', ikte__xfhaj, uwcoc__ngbox,
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
        tzwl__bkpj = 0.0
        oihtw__dlwo = 0.0
        grz__hzzlx = 0.0
        xnug__tgzko = 0.0
        lfmk__rsgqn = 0
        for jnv__mrd in numba.parfors.parfor.internal_prange(len(A)):
            wyj__acse = 0.0
            tkie__azfev = 0
            if not bodo.libs.array_kernels.isna(A, jnv__mrd) or not skipna:
                wyj__acse = np.float64(A[jnv__mrd])
                tkie__azfev = 1
            tzwl__bkpj += wyj__acse
            oihtw__dlwo += wyj__acse ** 2
            grz__hzzlx += wyj__acse ** 3
            xnug__tgzko += wyj__acse ** 4
            lfmk__rsgqn += tkie__azfev
        ezmk__oyalb = bodo.hiframes.series_kernels.compute_kurt(tzwl__bkpj,
            oihtw__dlwo, grz__hzzlx, xnug__tgzko, lfmk__rsgqn)
        return ezmk__oyalb
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    ikte__xfhaj = dict(level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', ikte__xfhaj, uwcoc__ngbox,
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
        tzwl__bkpj = 0.0
        oihtw__dlwo = 0.0
        grz__hzzlx = 0.0
        lfmk__rsgqn = 0
        for jnv__mrd in numba.parfors.parfor.internal_prange(len(A)):
            wyj__acse = 0.0
            tkie__azfev = 0
            if not bodo.libs.array_kernels.isna(A, jnv__mrd) or not skipna:
                wyj__acse = np.float64(A[jnv__mrd])
                tkie__azfev = 1
            tzwl__bkpj += wyj__acse
            oihtw__dlwo += wyj__acse ** 2
            grz__hzzlx += wyj__acse ** 3
            lfmk__rsgqn += tkie__azfev
        ezmk__oyalb = bodo.hiframes.series_kernels.compute_skew(tzwl__bkpj,
            oihtw__dlwo, grz__hzzlx, lfmk__rsgqn)
        return ezmk__oyalb
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    ikte__xfhaj = dict(level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', ikte__xfhaj, uwcoc__ngbox,
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
        kzg__asssx = bodo.hiframes.pd_series_ext.get_series_data(S)
        omr__cdhwm = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        bmj__umaol = 0
        for jnv__mrd in numba.parfors.parfor.internal_prange(len(kzg__asssx)):
            yfr__mvqp = kzg__asssx[jnv__mrd]
            teafo__ffyo = omr__cdhwm[jnv__mrd]
            bmj__umaol += yfr__mvqp * teafo__ffyo
        return bmj__umaol
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    ikte__xfhaj = dict(skipna=skipna)
    uwcoc__ngbox = dict(skipna=True)
    check_unsupported_args('Series.cumsum', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(skipna=skipna)
    uwcoc__ngbox = dict(skipna=True)
    check_unsupported_args('Series.cumprod', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(skipna=skipna)
    uwcoc__ngbox = dict(skipna=True)
    check_unsupported_args('Series.cummin', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(skipna=skipna)
    uwcoc__ngbox = dict(skipna=True)
    check_unsupported_args('Series.cummax', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    uwcoc__ngbox = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        bdmdg__sxq = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, bdmdg__sxq, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    ikte__xfhaj = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    uwcoc__ngbox = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(level=level)
    uwcoc__ngbox = dict(level=None)
    check_unsupported_args('Series.count', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    ikte__xfhaj = dict(method=method, min_periods=min_periods)
    uwcoc__ngbox = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        vry__euvfr = S.sum()
        cxiz__nsy = other.sum()
        a = n * (S * other).sum() - vry__euvfr * cxiz__nsy
        zhvl__kes = n * (S ** 2).sum() - vry__euvfr ** 2
        loa__avr = n * (other ** 2).sum() - cxiz__nsy ** 2
        return a / np.sqrt(zhvl__kes * loa__avr)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    ikte__xfhaj = dict(min_periods=min_periods)
    uwcoc__ngbox = dict(min_periods=None)
    check_unsupported_args('Series.cov', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        vry__euvfr = S.mean()
        cxiz__nsy = other.mean()
        pbnn__fbhba = ((S - vry__euvfr) * (other - cxiz__nsy)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(pbnn__fbhba, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            qho__lyrk = np.sign(sum_val)
            return np.inf * qho__lyrk
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    ikte__xfhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(axis=axis, skipna=skipna)
    uwcoc__ngbox = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(axis=axis, skipna=skipna)
    uwcoc__ngbox = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', ikte__xfhaj, uwcoc__ngbox,
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
    ikte__xfhaj = dict(level=level, numeric_only=numeric_only)
    uwcoc__ngbox = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', ikte__xfhaj, uwcoc__ngbox,
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
        ipefw__qlfy = arr[:n]
        jzso__gsv = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(ipefw__qlfy,
            jzso__gsv, name)
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
        zxwda__mhbg = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ipefw__qlfy = arr[zxwda__mhbg:]
        jzso__gsv = index[zxwda__mhbg:]
        return bodo.hiframes.pd_series_ext.init_series(ipefw__qlfy,
            jzso__gsv, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    gltu__ifla = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in gltu__ifla:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            mrxid__xqh = index[0]
            worjl__ouc = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                mrxid__xqh, False))
        else:
            worjl__ouc = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ipefw__qlfy = arr[:worjl__ouc]
        jzso__gsv = index[:worjl__ouc]
        return bodo.hiframes.pd_series_ext.init_series(ipefw__qlfy,
            jzso__gsv, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    gltu__ifla = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in gltu__ifla:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            uzjqy__xllqw = index[-1]
            worjl__ouc = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                uzjqy__xllqw, True))
        else:
            worjl__ouc = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ipefw__qlfy = arr[len(arr) - worjl__ouc:]
        jzso__gsv = index[len(arr) - worjl__ouc:]
        return bodo.hiframes.pd_series_ext.init_series(ipefw__qlfy,
            jzso__gsv, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        ftg__jvxet = bodo.utils.conversion.index_to_array(index)
        hmdbl__gqb, fhast__btmtf = (bodo.libs.array_kernels.
            first_last_valid_index(arr, ftg__jvxet))
        return fhast__btmtf if hmdbl__gqb else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        ftg__jvxet = bodo.utils.conversion.index_to_array(index)
        hmdbl__gqb, fhast__btmtf = (bodo.libs.array_kernels.
            first_last_valid_index(arr, ftg__jvxet, False))
        return fhast__btmtf if hmdbl__gqb else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    ikte__xfhaj = dict(keep=keep)
    uwcoc__ngbox = dict(keep='first')
    check_unsupported_args('Series.nlargest', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        ftg__jvxet = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nvwoc__jpn, owmlf__fuwl = bodo.libs.array_kernels.nlargest(arr,
            ftg__jvxet, n, True, bodo.hiframes.series_kernels.gt_f)
        fwm__rvki = bodo.utils.conversion.convert_to_index(owmlf__fuwl)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
            fwm__rvki, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    ikte__xfhaj = dict(keep=keep)
    uwcoc__ngbox = dict(keep='first')
    check_unsupported_args('Series.nsmallest', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        ftg__jvxet = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nvwoc__jpn, owmlf__fuwl = bodo.libs.array_kernels.nlargest(arr,
            ftg__jvxet, n, False, bodo.hiframes.series_kernels.lt_f)
        fwm__rvki = bodo.utils.conversion.convert_to_index(owmlf__fuwl)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
            fwm__rvki, name)
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
    ikte__xfhaj = dict(errors=errors)
    uwcoc__ngbox = dict(errors='raise')
    check_unsupported_args('Series.astype', ikte__xfhaj, uwcoc__ngbox,
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
        nvwoc__jpn = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    ikte__xfhaj = dict(axis=axis, is_copy=is_copy)
    uwcoc__ngbox = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        jrfg__ugvdk = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[jrfg__ugvdk],
            index[jrfg__ugvdk], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    ikte__xfhaj = dict(axis=axis, kind=kind, order=order)
    uwcoc__ngbox = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        szzif__fdogf = S.notna().values
        if not szzif__fdogf.all():
            nvwoc__jpn = np.full(n, -1, np.int64)
            nvwoc__jpn[szzif__fdogf] = argsort(arr[szzif__fdogf])
        else:
            nvwoc__jpn = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    ikte__xfhaj = dict(axis=axis, numeric_only=numeric_only)
    uwcoc__ngbox = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', ikte__xfhaj, uwcoc__ngbox,
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
        nvwoc__jpn = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    ikte__xfhaj = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    uwcoc__ngbox = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    reuzu__grccc = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        reofk__fgw = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, reuzu__grccc)
        rib__ebdp = reofk__fgw.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        nvwoc__jpn = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            rib__ebdp, 0)
        fwm__rvki = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            rib__ebdp)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
            fwm__rvki, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    ikte__xfhaj = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    uwcoc__ngbox = dict(axis=0, inplace=False, kind='quicksort',
        ignore_index=False, key=None)
    check_unsupported_args('Series.sort_values', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    kpmsf__tzh = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        reofk__fgw = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, kpmsf__tzh)
        rib__ebdp = reofk__fgw.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        nvwoc__jpn = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            rib__ebdp, 0)
        fwm__rvki = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            rib__ebdp)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
            fwm__rvki, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    vqlgk__zxy = is_overload_true(is_nullable)
    agsm__cgwh = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    agsm__cgwh += '  numba.parfors.parfor.init_prange()\n'
    agsm__cgwh += '  n = len(arr)\n'
    if vqlgk__zxy:
        agsm__cgwh += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        agsm__cgwh += '  out_arr = np.empty(n, np.int64)\n'
    agsm__cgwh += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    agsm__cgwh += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if vqlgk__zxy:
        agsm__cgwh += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        agsm__cgwh += '      out_arr[i] = -1\n'
    agsm__cgwh += '      continue\n'
    agsm__cgwh += '    val = arr[i]\n'
    agsm__cgwh += '    if include_lowest and val == bins[0]:\n'
    agsm__cgwh += '      ind = 1\n'
    agsm__cgwh += '    else:\n'
    agsm__cgwh += '      ind = np.searchsorted(bins, val)\n'
    agsm__cgwh += '    if ind == 0 or ind == len(bins):\n'
    if vqlgk__zxy:
        agsm__cgwh += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        agsm__cgwh += '      out_arr[i] = -1\n'
    agsm__cgwh += '    else:\n'
    agsm__cgwh += '      out_arr[i] = ind - 1\n'
    agsm__cgwh += '  return out_arr\n'
    fgysj__qevej = {}
    exec(agsm__cgwh, {'bodo': bodo, 'np': np, 'numba': numba}, fgysj__qevej)
    impl = fgysj__qevej['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        wowdy__ziy, qshbx__majq = np.divmod(x, 1)
        if wowdy__ziy == 0:
            rwu__qyl = -int(np.floor(np.log10(abs(qshbx__majq)))
                ) - 1 + precision
        else:
            rwu__qyl = precision
        return np.around(x, rwu__qyl)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        vco__mfmu = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(vco__mfmu)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        buz__sqt = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            ugg__nta = bins.copy()
            if right and include_lowest:
                ugg__nta[0] = ugg__nta[0] - buz__sqt
            icm__rbp = bodo.libs.interval_arr_ext.init_interval_array(ugg__nta
                [:-1], ugg__nta[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(icm__rbp,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        ugg__nta = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            ugg__nta[0] = ugg__nta[0] - 10.0 ** -precision
        icm__rbp = bodo.libs.interval_arr_ext.init_interval_array(ugg__nta[
            :-1], ugg__nta[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(icm__rbp, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        vjl__jfz = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        xzl__ixa = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        nvwoc__jpn = np.zeros(nbins, np.int64)
        for jnv__mrd in range(len(vjl__jfz)):
            nvwoc__jpn[xzl__ixa[jnv__mrd]] = vjl__jfz[jnv__mrd]
        return nvwoc__jpn
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
            nmgu__kegdw = (max_val - min_val) * 0.001
            if right:
                bins[0] -= nmgu__kegdw
            else:
                bins[-1] += nmgu__kegdw
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    ikte__xfhaj = dict(dropna=dropna)
    uwcoc__ngbox = dict(dropna=True)
    check_unsupported_args('Series.value_counts', ikte__xfhaj, uwcoc__ngbox,
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
    bzz__xjvpw = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    agsm__cgwh = 'def impl(\n'
    agsm__cgwh += '    S,\n'
    agsm__cgwh += '    normalize=False,\n'
    agsm__cgwh += '    sort=True,\n'
    agsm__cgwh += '    ascending=False,\n'
    agsm__cgwh += '    bins=None,\n'
    agsm__cgwh += '    dropna=True,\n'
    agsm__cgwh += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    agsm__cgwh += '):\n'
    agsm__cgwh += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    agsm__cgwh += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    agsm__cgwh += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if bzz__xjvpw:
        agsm__cgwh += '    right = True\n'
        agsm__cgwh += _gen_bins_handling(bins, S.dtype)
        agsm__cgwh += '    arr = get_bin_inds(bins, arr)\n'
    agsm__cgwh += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    agsm__cgwh += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    agsm__cgwh += '    )\n'
    agsm__cgwh += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if bzz__xjvpw:
        agsm__cgwh += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        agsm__cgwh += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        agsm__cgwh += '    index = get_bin_labels(bins)\n'
    else:
        agsm__cgwh += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        agsm__cgwh += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        agsm__cgwh += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        agsm__cgwh += '    )\n'
        agsm__cgwh += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    agsm__cgwh += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        agsm__cgwh += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        vyoq__gux = 'len(S)' if bzz__xjvpw else 'count_arr.sum()'
        agsm__cgwh += f'    res = res / float({vyoq__gux})\n'
    agsm__cgwh += '    return res\n'
    fgysj__qevej = {}
    exec(agsm__cgwh, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, fgysj__qevej)
    impl = fgysj__qevej['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    agsm__cgwh = ''
    if isinstance(bins, types.Integer):
        agsm__cgwh += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        agsm__cgwh += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            agsm__cgwh += '    min_val = min_val.value\n'
            agsm__cgwh += '    max_val = max_val.value\n'
        agsm__cgwh += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            agsm__cgwh += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        agsm__cgwh += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return agsm__cgwh


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    ikte__xfhaj = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    uwcoc__ngbox = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    agsm__cgwh = 'def impl(\n'
    agsm__cgwh += '    x,\n'
    agsm__cgwh += '    bins,\n'
    agsm__cgwh += '    right=True,\n'
    agsm__cgwh += '    labels=None,\n'
    agsm__cgwh += '    retbins=False,\n'
    agsm__cgwh += '    precision=3,\n'
    agsm__cgwh += '    include_lowest=False,\n'
    agsm__cgwh += "    duplicates='raise',\n"
    agsm__cgwh += '    ordered=True\n'
    agsm__cgwh += '):\n'
    if isinstance(x, SeriesType):
        agsm__cgwh += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        agsm__cgwh += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        agsm__cgwh += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        agsm__cgwh += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    agsm__cgwh += _gen_bins_handling(bins, x.dtype)
    agsm__cgwh += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    agsm__cgwh += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    agsm__cgwh += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    agsm__cgwh += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        agsm__cgwh += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        agsm__cgwh += '    return res\n'
    else:
        agsm__cgwh += '    return out_arr\n'
    fgysj__qevej = {}
    exec(agsm__cgwh, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, fgysj__qevej)
    impl = fgysj__qevej['impl']
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
    ikte__xfhaj = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    uwcoc__ngbox = dict(labels=None, retbins=False, precision=3, duplicates
        ='raise')
    check_unsupported_args('pandas.qcut', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        pcxdh__awm = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, pcxdh__awm)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    ikte__xfhaj = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze
        =squeeze, observed=observed, dropna=dropna)
    uwcoc__ngbox = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', ikte__xfhaj, uwcoc__ngbox,
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
        bcarr__bbx = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            ittrp__lxfkv = bodo.utils.conversion.coerce_to_array(index)
            reofk__fgw = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                ittrp__lxfkv, arr), index, bcarr__bbx)
            return reofk__fgw.groupby(' ')['']
        return impl_index
    ciiv__ahqje = by
    if isinstance(by, SeriesType):
        ciiv__ahqje = by.data
    if isinstance(ciiv__ahqje, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    vjab__fexe = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        ittrp__lxfkv = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        reofk__fgw = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            ittrp__lxfkv, arr), index, vjab__fexe)
        return reofk__fgw.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    ikte__xfhaj = dict(verify_integrity=verify_integrity)
    uwcoc__ngbox = dict(verify_integrity=False)
    check_unsupported_args('Series.append', ikte__xfhaj, uwcoc__ngbox,
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
            oyvyg__xsl = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            nvwoc__jpn = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(nvwoc__jpn, A, oyvyg__xsl, False)
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nvwoc__jpn = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    ikte__xfhaj = dict(interpolation=interpolation)
    uwcoc__ngbox = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            nvwoc__jpn = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
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
        huxux__zicx = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(huxux__zicx, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    ikte__xfhaj = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    uwcoc__ngbox = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', ikte__xfhaj, uwcoc__ngbox,
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
        iswu__tug = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        iswu__tug = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    agsm__cgwh = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {iswu__tug}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    nces__ryfwa = dict()
    exec(agsm__cgwh, {'bodo': bodo, 'numba': numba}, nces__ryfwa)
    dvxzb__fucu = nces__ryfwa['impl']
    return dvxzb__fucu


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        iswu__tug = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        iswu__tug = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    agsm__cgwh = 'def impl(S,\n'
    agsm__cgwh += '     value=None,\n'
    agsm__cgwh += '    method=None,\n'
    agsm__cgwh += '    axis=None,\n'
    agsm__cgwh += '    inplace=False,\n'
    agsm__cgwh += '    limit=None,\n'
    agsm__cgwh += '   downcast=None,\n'
    agsm__cgwh += '):\n'
    agsm__cgwh += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    agsm__cgwh += '    n = len(in_arr)\n'
    agsm__cgwh += f'    out_arr = {iswu__tug}(n, -1)\n'
    agsm__cgwh += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    agsm__cgwh += '        s = in_arr[j]\n'
    agsm__cgwh += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    agsm__cgwh += '            s = value\n'
    agsm__cgwh += '        out_arr[j] = s\n'
    agsm__cgwh += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    nces__ryfwa = dict()
    exec(agsm__cgwh, {'bodo': bodo, 'numba': numba}, nces__ryfwa)
    dvxzb__fucu = nces__ryfwa['impl']
    return dvxzb__fucu


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
    ifexc__xlcek = bodo.hiframes.pd_series_ext.get_series_data(value)
    for jnv__mrd in numba.parfors.parfor.internal_prange(len(fymlv__kpaae)):
        s = fymlv__kpaae[jnv__mrd]
        if bodo.libs.array_kernels.isna(fymlv__kpaae, jnv__mrd
            ) and not bodo.libs.array_kernels.isna(ifexc__xlcek, jnv__mrd):
            s = ifexc__xlcek[jnv__mrd]
        fymlv__kpaae[jnv__mrd] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
    for jnv__mrd in numba.parfors.parfor.internal_prange(len(fymlv__kpaae)):
        s = fymlv__kpaae[jnv__mrd]
        if bodo.libs.array_kernels.isna(fymlv__kpaae, jnv__mrd):
            s = value
        fymlv__kpaae[jnv__mrd] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    ifexc__xlcek = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(fymlv__kpaae)
    nvwoc__jpn = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for oof__thqv in numba.parfors.parfor.internal_prange(n):
        s = fymlv__kpaae[oof__thqv]
        if bodo.libs.array_kernels.isna(fymlv__kpaae, oof__thqv
            ) and not bodo.libs.array_kernels.isna(ifexc__xlcek, oof__thqv):
            s = ifexc__xlcek[oof__thqv]
        nvwoc__jpn[oof__thqv] = s
        if bodo.libs.array_kernels.isna(fymlv__kpaae, oof__thqv
            ) and bodo.libs.array_kernels.isna(ifexc__xlcek, oof__thqv):
            bodo.libs.array_kernels.setna(nvwoc__jpn, oof__thqv)
    return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    ifexc__xlcek = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(fymlv__kpaae)
    nvwoc__jpn = bodo.utils.utils.alloc_type(n, fymlv__kpaae.dtype, (-1,))
    for jnv__mrd in numba.parfors.parfor.internal_prange(n):
        s = fymlv__kpaae[jnv__mrd]
        if bodo.libs.array_kernels.isna(fymlv__kpaae, jnv__mrd
            ) and not bodo.libs.array_kernels.isna(ifexc__xlcek, jnv__mrd):
            s = ifexc__xlcek[jnv__mrd]
        nvwoc__jpn[jnv__mrd] = s
    return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    ikte__xfhaj = dict(limit=limit, downcast=downcast)
    uwcoc__ngbox = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', ikte__xfhaj, uwcoc__ngbox,
        package_name='pandas', module_name='Series')
    prkwk__yekzh = not is_overload_none(value)
    zjhc__hegu = not is_overload_none(method)
    if prkwk__yekzh and zjhc__hegu:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not prkwk__yekzh and not zjhc__hegu:
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
    if zjhc__hegu:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        dluw__uowg = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(dluw__uowg)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(dluw__uowg)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    rubit__khlgz = element_type(S.data)
    bldy__yjkkh = None
    if prkwk__yekzh:
        bldy__yjkkh = element_type(types.unliteral(value))
    if bldy__yjkkh and not can_replace(rubit__khlgz, bldy__yjkkh):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {bldy__yjkkh} with series type {rubit__khlgz}'
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
        ggu__mzv = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                ifexc__xlcek = bodo.hiframes.pd_series_ext.get_series_data(
                    value)
                n = len(fymlv__kpaae)
                nvwoc__jpn = bodo.utils.utils.alloc_type(n, ggu__mzv, (-1,))
                for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(fymlv__kpaae, jnv__mrd
                        ) and bodo.libs.array_kernels.isna(ifexc__xlcek,
                        jnv__mrd):
                        bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                        continue
                    if bodo.libs.array_kernels.isna(fymlv__kpaae, jnv__mrd):
                        nvwoc__jpn[jnv__mrd
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            ifexc__xlcek[jnv__mrd])
                        continue
                    nvwoc__jpn[jnv__mrd
                        ] = bodo.utils.conversion.unbox_if_timestamp(
                        fymlv__kpaae[jnv__mrd])
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                    index, name)
            return fillna_series_impl
        if zjhc__hegu:
            yay__phg = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(rubit__khlgz, (types.Integer, types.Float)
                ) and rubit__khlgz not in yay__phg:
                raise BodoError(
                    f"Series.fillna(): series of type {rubit__khlgz} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                nvwoc__jpn = bodo.libs.array_kernels.ffill_bfill_arr(
                    fymlv__kpaae, method)
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(fymlv__kpaae)
            nvwoc__jpn = bodo.utils.utils.alloc_type(n, ggu__mzv, (-1,))
            for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(fymlv__kpaae[
                    jnv__mrd])
                if bodo.libs.array_kernels.isna(fymlv__kpaae, jnv__mrd):
                    s = value
                nvwoc__jpn[jnv__mrd] = s
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        xctx__lirkh = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        ikte__xfhaj = dict(limit=limit, downcast=downcast)
        uwcoc__ngbox = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', ikte__xfhaj,
            uwcoc__ngbox, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        rubit__khlgz = element_type(S.data)
        yay__phg = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(rubit__khlgz, (types.Integer, types.Float)
            ) and rubit__khlgz not in yay__phg:
            raise BodoError(
                f'Series.{overload_name}(): series of type {rubit__khlgz} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            nvwoc__jpn = bodo.libs.array_kernels.ffill_bfill_arr(fymlv__kpaae,
                xctx__lirkh)
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        zntoz__stxet = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            zntoz__stxet)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        ghzrx__eboop = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(ghzrx__eboop)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        ghzrx__eboop = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(ghzrx__eboop)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        ghzrx__eboop = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(ghzrx__eboop)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    ikte__xfhaj = dict(inplace=inplace, limit=limit, regex=regex, method=method
        )
    qbd__hqscz = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', ikte__xfhaj, qbd__hqscz,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    rubit__khlgz = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        tve__wrzp = element_type(to_replace.key_type)
        bldy__yjkkh = element_type(to_replace.value_type)
    else:
        tve__wrzp = element_type(to_replace)
        bldy__yjkkh = element_type(value)
    pjvfw__juk = None
    if rubit__khlgz != types.unliteral(tve__wrzp):
        if bodo.utils.typing.equality_always_false(rubit__khlgz, types.
            unliteral(tve__wrzp)
            ) or not bodo.utils.typing.types_equality_exists(rubit__khlgz,
            tve__wrzp):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(rubit__khlgz, (types.Float, types.Integer)
            ) or rubit__khlgz == np.bool_:
            pjvfw__juk = rubit__khlgz
    if not can_replace(rubit__khlgz, types.unliteral(bldy__yjkkh)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    pps__nucck = to_str_arr_if_dict_array(S.data)
    if isinstance(pps__nucck, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(fymlv__kpaae.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(fymlv__kpaae)
        nvwoc__jpn = bodo.utils.utils.alloc_type(n, pps__nucck, (-1,))
        vux__adpi = build_replace_dict(to_replace, value, pjvfw__juk)
        for jnv__mrd in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(fymlv__kpaae, jnv__mrd):
                bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                continue
            s = fymlv__kpaae[jnv__mrd]
            if s in vux__adpi:
                s = vux__adpi[s]
            nvwoc__jpn[jnv__mrd] = s
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    sow__gksd = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    kmnh__yrt = is_iterable_type(to_replace)
    uvts__fdvs = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    azpv__qplg = is_iterable_type(value)
    if sow__gksd and uvts__fdvs:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                vux__adpi = {}
                vux__adpi[key_dtype_conv(to_replace)] = value
                return vux__adpi
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            vux__adpi = {}
            vux__adpi[to_replace] = value
            return vux__adpi
        return impl
    if kmnh__yrt and uvts__fdvs:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                vux__adpi = {}
                for bplgw__vfa in to_replace:
                    vux__adpi[key_dtype_conv(bplgw__vfa)] = value
                return vux__adpi
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            vux__adpi = {}
            for bplgw__vfa in to_replace:
                vux__adpi[bplgw__vfa] = value
            return vux__adpi
        return impl
    if kmnh__yrt and azpv__qplg:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                vux__adpi = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for jnv__mrd in range(len(to_replace)):
                    vux__adpi[key_dtype_conv(to_replace[jnv__mrd])] = value[
                        jnv__mrd]
                return vux__adpi
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            vux__adpi = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for jnv__mrd in range(len(to_replace)):
                vux__adpi[to_replace[jnv__mrd]] = value[jnv__mrd]
            return vux__adpi
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
            nvwoc__jpn = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nvwoc__jpn = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    ikte__xfhaj = dict(ignore_index=ignore_index)
    qzb__evtah = dict(ignore_index=False)
    check_unsupported_args('Series.explode', ikte__xfhaj, qzb__evtah,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ftg__jvxet = bodo.utils.conversion.index_to_array(index)
        nvwoc__jpn, csdsh__lny = bodo.libs.array_kernels.explode(arr,
            ftg__jvxet)
        fwm__rvki = bodo.utils.conversion.index_from_array(csdsh__lny)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
            fwm__rvki, name)
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
            aen__kakhm = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                aen__kakhm[jnv__mrd] = np.argmax(a[jnv__mrd])
            return aen__kakhm
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            ycm__xoln = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                ycm__xoln[jnv__mrd] = np.argmin(a[jnv__mrd])
            return ycm__xoln
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
    ikte__xfhaj = dict(axis=axis, inplace=inplace, how=how)
    wyfzg__cjy = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', ikte__xfhaj, wyfzg__cjy,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            szzif__fdogf = S.notna().values
            ftg__jvxet = bodo.utils.conversion.extract_index_array(S)
            fwm__rvki = bodo.utils.conversion.convert_to_index(ftg__jvxet[
                szzif__fdogf])
            nvwoc__jpn = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(fymlv__kpaae))
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                fwm__rvki, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ftg__jvxet = bodo.utils.conversion.extract_index_array(S)
            szzif__fdogf = S.notna().values
            fwm__rvki = bodo.utils.conversion.convert_to_index(ftg__jvxet[
                szzif__fdogf])
            nvwoc__jpn = fymlv__kpaae[szzif__fdogf]
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                fwm__rvki, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    ikte__xfhaj = dict(freq=freq, axis=axis, fill_value=fill_value)
    uwcoc__ngbox = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', ikte__xfhaj, uwcoc__ngbox,
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
        nvwoc__jpn = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    ikte__xfhaj = dict(fill_method=fill_method, limit=limit, freq=freq)
    uwcoc__ngbox = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', ikte__xfhaj, uwcoc__ngbox,
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
        nvwoc__jpn = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
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
            ubmp__hai = 'None'
        else:
            ubmp__hai = 'other'
        agsm__cgwh = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            agsm__cgwh += '  cond = ~cond\n'
        agsm__cgwh += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        agsm__cgwh += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        agsm__cgwh += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        agsm__cgwh += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {ubmp__hai})\n'
            )
        agsm__cgwh += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        fgysj__qevej = {}
        exec(agsm__cgwh, {'bodo': bodo, 'np': np}, fgysj__qevej)
        impl = fgysj__qevej['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        zntoz__stxet = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(zntoz__stxet)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    ikte__xfhaj = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    uwcoc__ngbox = dict(inplace=False, level=None, errors='raise', try_cast
        =False)
    check_unsupported_args(f'{func_name}', ikte__xfhaj, uwcoc__ngbox,
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
    mtbz__bdm = is_overload_constant_nan(other)
    if not (is_default or mtbz__bdm or is_scalar_type(other) or isinstance(
        other, types.Array) and other.ndim >= 1 and other.ndim <= max_ndim or
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
            scf__caw = arr.dtype.elem_type
        else:
            scf__caw = arr.dtype
        if is_iterable_type(other):
            ijazp__uajv = other.dtype
        elif mtbz__bdm:
            ijazp__uajv = types.float64
        else:
            ijazp__uajv = types.unliteral(other)
        if not mtbz__bdm and not is_common_scalar_dtype([scf__caw, ijazp__uajv]
            ):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        ikte__xfhaj = dict(level=level, axis=axis)
        uwcoc__ngbox = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), ikte__xfhaj,
            uwcoc__ngbox, package_name='pandas', module_name='Series')
        bkrnk__oeiqh = other == string_type or is_overload_constant_str(other)
        vpsw__leifz = is_iterable_type(other) and other.dtype == string_type
        ydy__uozr = S.dtype == string_type and (op == operator.add and (
            bkrnk__oeiqh or vpsw__leifz) or op == operator.mul and
            isinstance(other, types.Integer))
        iwqyg__mgqq = S.dtype == bodo.timedelta64ns
        rgq__pmlxv = S.dtype == bodo.datetime64ns
        uhy__ufdn = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        npf__dxa = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        bmwy__dcti = iwqyg__mgqq and (uhy__ufdn or npf__dxa
            ) or rgq__pmlxv and uhy__ufdn
        bmwy__dcti = bmwy__dcti and op == operator.add
        if not (isinstance(S.dtype, types.Number) or ydy__uozr or bmwy__dcti):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        otnei__eai = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            pps__nucck = otnei__eai.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and pps__nucck == types.Array(types.bool_, 1, 'C'):
                pps__nucck = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                nvwoc__jpn = bodo.utils.utils.alloc_type(n, pps__nucck, (-1,))
                for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                    mmi__pgtuy = bodo.libs.array_kernels.isna(arr, jnv__mrd)
                    if mmi__pgtuy:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                        else:
                            nvwoc__jpn[jnv__mrd] = op(fill_value, other)
                    else:
                        nvwoc__jpn[jnv__mrd] = op(arr[jnv__mrd], other)
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        pps__nucck = otnei__eai.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and pps__nucck == types.Array(
            types.bool_, 1, 'C'):
            pps__nucck = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ubtlh__wdv = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            nvwoc__jpn = bodo.utils.utils.alloc_type(n, pps__nucck, (-1,))
            for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                mmi__pgtuy = bodo.libs.array_kernels.isna(arr, jnv__mrd)
                uhom__xgk = bodo.libs.array_kernels.isna(ubtlh__wdv, jnv__mrd)
                if mmi__pgtuy and uhom__xgk:
                    bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                elif mmi__pgtuy:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                    else:
                        nvwoc__jpn[jnv__mrd] = op(fill_value, ubtlh__wdv[
                            jnv__mrd])
                elif uhom__xgk:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                    else:
                        nvwoc__jpn[jnv__mrd] = op(arr[jnv__mrd], fill_value)
                else:
                    nvwoc__jpn[jnv__mrd] = op(arr[jnv__mrd], ubtlh__wdv[
                        jnv__mrd])
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
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
        otnei__eai = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            pps__nucck = otnei__eai.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and pps__nucck == types.Array(types.bool_, 1, 'C'):
                pps__nucck = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                nvwoc__jpn = bodo.utils.utils.alloc_type(n, pps__nucck, None)
                for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                    mmi__pgtuy = bodo.libs.array_kernels.isna(arr, jnv__mrd)
                    if mmi__pgtuy:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                        else:
                            nvwoc__jpn[jnv__mrd] = op(other, fill_value)
                    else:
                        nvwoc__jpn[jnv__mrd] = op(other, arr[jnv__mrd])
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        pps__nucck = otnei__eai.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and pps__nucck == types.Array(
            types.bool_, 1, 'C'):
            pps__nucck = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            ubtlh__wdv = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            nvwoc__jpn = bodo.utils.utils.alloc_type(n, pps__nucck, None)
            for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                mmi__pgtuy = bodo.libs.array_kernels.isna(arr, jnv__mrd)
                uhom__xgk = bodo.libs.array_kernels.isna(ubtlh__wdv, jnv__mrd)
                nvwoc__jpn[jnv__mrd] = op(ubtlh__wdv[jnv__mrd], arr[jnv__mrd])
                if mmi__pgtuy and uhom__xgk:
                    bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                elif mmi__pgtuy:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                    else:
                        nvwoc__jpn[jnv__mrd] = op(ubtlh__wdv[jnv__mrd],
                            fill_value)
                elif uhom__xgk:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                    else:
                        nvwoc__jpn[jnv__mrd] = op(fill_value, arr[jnv__mrd])
                else:
                    nvwoc__jpn[jnv__mrd] = op(ubtlh__wdv[jnv__mrd], arr[
                        jnv__mrd])
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
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
    for op, jkzp__egj in explicit_binop_funcs_two_ways.items():
        for name in jkzp__egj:
            zntoz__stxet = create_explicit_binary_op_overload(op)
            vuq__xfq = create_explicit_binary_reverse_op_overload(op)
            kooz__jflto = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(zntoz__stxet)
            overload_method(SeriesType, kooz__jflto, no_unliteral=True)(
                vuq__xfq)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        zntoz__stxet = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(zntoz__stxet)
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
                utzp__dbbc = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                nvwoc__jpn = dt64_arr_sub(arr, utzp__dbbc)
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
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
                nvwoc__jpn = np.empty(n, np.dtype('datetime64[ns]'))
                for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, jnv__mrd):
                        bodo.libs.array_kernels.setna(nvwoc__jpn, jnv__mrd)
                        continue
                    igjv__mtrvu = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[jnv__mrd]))
                    jrtjy__eftjf = op(igjv__mtrvu, rhs)
                    nvwoc__jpn[jnv__mrd
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        jrtjy__eftjf.value)
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
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
                    utzp__dbbc = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    nvwoc__jpn = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(utzp__dbbc))
                    return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                utzp__dbbc = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                nvwoc__jpn = op(arr, utzp__dbbc)
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    zic__ksx = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    nvwoc__jpn = op(bodo.utils.conversion.
                        unbox_if_timestamp(zic__ksx), arr)
                    return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                zic__ksx = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                nvwoc__jpn = op(zic__ksx, arr)
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        zntoz__stxet = create_binary_op_overload(op)
        overload(op)(zntoz__stxet)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    jngpn__fgni = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, jngpn__fgni)
        for jnv__mrd in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, jnv__mrd
                ) or bodo.libs.array_kernels.isna(arg2, jnv__mrd):
                bodo.libs.array_kernels.setna(S, jnv__mrd)
                continue
            S[jnv__mrd
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                jnv__mrd]) - bodo.hiframes.pd_timestamp_ext.dt64_to_integer
                (arg2[jnv__mrd]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                ubtlh__wdv = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, ubtlh__wdv)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        zntoz__stxet = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(zntoz__stxet)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                nvwoc__jpn = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        zntoz__stxet = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(zntoz__stxet)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    nvwoc__jpn = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
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
                    ubtlh__wdv = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    nvwoc__jpn = ufunc(arr, ubtlh__wdv)
                    return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    ubtlh__wdv = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    nvwoc__jpn = ufunc(arr, ubtlh__wdv)
                    return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        zntoz__stxet = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(zntoz__stxet)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        xlplt__wfy = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        exif__kfp = np.arange(n),
        bodo.libs.timsort.sort(xlplt__wfy, 0, n, exif__kfp)
        return exif__kfp[0]
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
        fdq__xjgy = get_overload_const_str(downcast)
        if fdq__xjgy in ('integer', 'signed'):
            out_dtype = types.int64
        elif fdq__xjgy == 'unsigned':
            out_dtype = types.uint64
        else:
            assert fdq__xjgy == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            fymlv__kpaae = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            nvwoc__jpn = pd.to_numeric(fymlv__kpaae, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            byle__irnt = np.empty(n, np.float64)
            for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, jnv__mrd):
                    bodo.libs.array_kernels.setna(byle__irnt, jnv__mrd)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(byle__irnt,
                        jnv__mrd, arg_a, jnv__mrd)
            return byle__irnt
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            byle__irnt = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for jnv__mrd in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, jnv__mrd):
                    bodo.libs.array_kernels.setna(byle__irnt, jnv__mrd)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(byle__irnt,
                        jnv__mrd, arg_a, jnv__mrd)
            return byle__irnt
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        wsd__nknp = if_series_to_array_type(args[0])
        if isinstance(wsd__nknp, types.Array) and isinstance(wsd__nknp.
            dtype, types.Integer):
            wsd__nknp = types.Array(types.float64, 1, 'C')
        return wsd__nknp(*args)


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
    rlkx__eom = bodo.utils.utils.is_array_typ(x, True)
    zzxo__rkg = bodo.utils.utils.is_array_typ(y, True)
    agsm__cgwh = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        agsm__cgwh += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if rlkx__eom and not bodo.utils.utils.is_array_typ(x, False):
        agsm__cgwh += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if zzxo__rkg and not bodo.utils.utils.is_array_typ(y, False):
        agsm__cgwh += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    agsm__cgwh += '  n = len(condition)\n'
    bqlu__rye = x.dtype if rlkx__eom else types.unliteral(x)
    tzi__xrg = y.dtype if zzxo__rkg else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        bqlu__rye = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        tzi__xrg = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    rkqm__rupfp = get_data(x)
    vxklm__ihqyf = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(exif__kfp) for
        exif__kfp in [rkqm__rupfp, vxklm__ihqyf])
    if vxklm__ihqyf == types.none:
        if isinstance(bqlu__rye, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif rkqm__rupfp == vxklm__ihqyf and not is_nullable:
        out_dtype = dtype_to_array_type(bqlu__rye)
    elif bqlu__rye == string_type or tzi__xrg == string_type:
        out_dtype = bodo.string_array_type
    elif rkqm__rupfp == bytes_type or (rlkx__eom and bqlu__rye == bytes_type
        ) and (vxklm__ihqyf == bytes_type or zzxo__rkg and tzi__xrg ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(bqlu__rye, bodo.PDCategoricalDtype):
        out_dtype = None
    elif bqlu__rye in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(bqlu__rye, 1, 'C')
    elif tzi__xrg in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(tzi__xrg, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(bqlu__rye), numba.np.numpy_support.
            as_dtype(tzi__xrg)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(bqlu__rye, bodo.PDCategoricalDtype):
        fbekc__jxa = 'x'
    else:
        fbekc__jxa = 'out_dtype'
    agsm__cgwh += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {fbekc__jxa}, (-1,))\n')
    if isinstance(bqlu__rye, bodo.PDCategoricalDtype):
        agsm__cgwh += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        agsm__cgwh += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    agsm__cgwh += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    agsm__cgwh += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if rlkx__eom:
        agsm__cgwh += '      if bodo.libs.array_kernels.isna(x, j):\n'
        agsm__cgwh += '        setna(out_arr, j)\n'
        agsm__cgwh += '        continue\n'
    if isinstance(bqlu__rye, bodo.PDCategoricalDtype):
        agsm__cgwh += '      out_codes[j] = x_codes[j]\n'
    else:
        agsm__cgwh += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if rlkx__eom else 'x'))
    agsm__cgwh += '    else:\n'
    if zzxo__rkg:
        agsm__cgwh += '      if bodo.libs.array_kernels.isna(y, j):\n'
        agsm__cgwh += '        setna(out_arr, j)\n'
        agsm__cgwh += '        continue\n'
    if vxklm__ihqyf == types.none:
        if isinstance(bqlu__rye, bodo.PDCategoricalDtype):
            agsm__cgwh += '      out_codes[j] = -1\n'
        else:
            agsm__cgwh += '      setna(out_arr, j)\n'
    else:
        agsm__cgwh += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if zzxo__rkg else 'y'))
    agsm__cgwh += '  return out_arr\n'
    fgysj__qevej = {}
    exec(agsm__cgwh, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, fgysj__qevej)
    lpwu__kkqkg = fgysj__qevej['_impl']
    return lpwu__kkqkg


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
        zdux__tutu = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(zdux__tutu, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(zdux__tutu):
            swsai__izxvz = zdux__tutu.data.dtype
        else:
            swsai__izxvz = zdux__tutu.dtype
        if isinstance(swsai__izxvz, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        txahp__ssxki = zdux__tutu
    else:
        mjf__pyl = []
        for zdux__tutu in choicelist:
            if not bodo.utils.utils.is_array_typ(zdux__tutu, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(zdux__tutu):
                swsai__izxvz = zdux__tutu.data.dtype
            else:
                swsai__izxvz = zdux__tutu.dtype
            if isinstance(swsai__izxvz, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            mjf__pyl.append(swsai__izxvz)
        if not is_common_scalar_dtype(mjf__pyl):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        txahp__ssxki = choicelist[0]
    if is_series_type(txahp__ssxki):
        txahp__ssxki = txahp__ssxki.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, txahp__ssxki.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(txahp__ssxki, types.Array) or isinstance(
        txahp__ssxki, BooleanArrayType) or isinstance(txahp__ssxki,
        IntegerArrayType) or bodo.utils.utils.is_array_typ(txahp__ssxki, 
        False) and txahp__ssxki.dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {txahp__ssxki} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    sjh__gpmhl = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        sgk__sfqr = choicelist.dtype
    else:
        lff__kqpt = False
        mjf__pyl = []
        for zdux__tutu in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                zdux__tutu, 'numpy.select()')
            if is_nullable_type(zdux__tutu):
                lff__kqpt = True
            if is_series_type(zdux__tutu):
                swsai__izxvz = zdux__tutu.data.dtype
            else:
                swsai__izxvz = zdux__tutu.dtype
            if isinstance(swsai__izxvz, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            mjf__pyl.append(swsai__izxvz)
        qjkey__czcx, vwmcm__uro = get_common_scalar_dtype(mjf__pyl)
        if not vwmcm__uro:
            raise BodoError('Internal error in overload_np_select')
        ezw__awf = dtype_to_array_type(qjkey__czcx)
        if lff__kqpt:
            ezw__awf = to_nullable_type(ezw__awf)
        sgk__sfqr = ezw__awf
    if isinstance(sgk__sfqr, SeriesType):
        sgk__sfqr = sgk__sfqr.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        kvv__dizbe = True
    else:
        kvv__dizbe = False
    talsx__gwsh = False
    eumry__tcpd = False
    if kvv__dizbe:
        if isinstance(sgk__sfqr.dtype, types.Number):
            pass
        elif sgk__sfqr.dtype == types.bool_:
            eumry__tcpd = True
        else:
            talsx__gwsh = True
            sgk__sfqr = to_nullable_type(sgk__sfqr)
    elif default == types.none or is_overload_constant_nan(default):
        talsx__gwsh = True
        sgk__sfqr = to_nullable_type(sgk__sfqr)
    agsm__cgwh = 'def np_select_impl(condlist, choicelist, default=0):\n'
    agsm__cgwh += '  if len(condlist) != len(choicelist):\n'
    agsm__cgwh += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    agsm__cgwh += '  output_len = len(choicelist[0])\n'
    agsm__cgwh += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    agsm__cgwh += '  for i in range(output_len):\n'
    if talsx__gwsh:
        agsm__cgwh += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif eumry__tcpd:
        agsm__cgwh += '    out[i] = False\n'
    else:
        agsm__cgwh += '    out[i] = default\n'
    if sjh__gpmhl:
        agsm__cgwh += '  for i in range(len(condlist) - 1, -1, -1):\n'
        agsm__cgwh += '    cond = condlist[i]\n'
        agsm__cgwh += '    choice = choicelist[i]\n'
        agsm__cgwh += '    out = np.where(cond, choice, out)\n'
    else:
        for jnv__mrd in range(len(choicelist) - 1, -1, -1):
            agsm__cgwh += f'  cond = condlist[{jnv__mrd}]\n'
            agsm__cgwh += f'  choice = choicelist[{jnv__mrd}]\n'
            agsm__cgwh += f'  out = np.where(cond, choice, out)\n'
    agsm__cgwh += '  return out'
    fgysj__qevej = dict()
    exec(agsm__cgwh, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': sgk__sfqr}, fgysj__qevej)
    impl = fgysj__qevej['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nvwoc__jpn = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    ikte__xfhaj = dict(subset=subset, keep=keep, inplace=inplace)
    uwcoc__ngbox = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', ikte__xfhaj,
        uwcoc__ngbox, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        jis__fxoq = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (jis__fxoq,), ftg__jvxet = bodo.libs.array_kernels.drop_duplicates((
            jis__fxoq,), index, 1)
        index = bodo.utils.conversion.index_from_array(ftg__jvxet)
        return bodo.hiframes.pd_series_ext.init_series(jis__fxoq, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    bdj__whsr = element_type(S.data)
    if not is_common_scalar_dtype([bdj__whsr, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([bdj__whsr, right]):
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
        nvwoc__jpn = np.empty(n, np.bool_)
        for jnv__mrd in numba.parfors.parfor.internal_prange(n):
            wyj__acse = bodo.utils.conversion.box_if_dt64(arr[jnv__mrd])
            if inclusive == 'both':
                nvwoc__jpn[jnv__mrd] = wyj__acse <= right and wyj__acse >= left
            else:
                nvwoc__jpn[jnv__mrd] = wyj__acse < right and wyj__acse > left
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    ikte__xfhaj = dict(axis=axis)
    uwcoc__ngbox = dict(axis=None)
    check_unsupported_args('Series.repeat', ikte__xfhaj, uwcoc__ngbox,
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
            ftg__jvxet = bodo.utils.conversion.index_to_array(index)
            nvwoc__jpn = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            csdsh__lny = bodo.libs.array_kernels.repeat_kernel(ftg__jvxet,
                repeats)
            fwm__rvki = bodo.utils.conversion.index_from_array(csdsh__lny)
            return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
                fwm__rvki, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ftg__jvxet = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        nvwoc__jpn = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        csdsh__lny = bodo.libs.array_kernels.repeat_kernel(ftg__jvxet, repeats)
        fwm__rvki = bodo.utils.conversion.index_from_array(csdsh__lny)
        return bodo.hiframes.pd_series_ext.init_series(nvwoc__jpn,
            fwm__rvki, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        exif__kfp = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(exif__kfp)
        dbuko__vchxm = {}
        for jnv__mrd in range(n):
            wyj__acse = bodo.utils.conversion.box_if_dt64(exif__kfp[jnv__mrd])
            dbuko__vchxm[index[jnv__mrd]] = wyj__acse
        return dbuko__vchxm
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    dluw__uowg = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            xfbl__upqg = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(dluw__uowg)
    elif is_literal_type(name):
        xfbl__upqg = get_literal_value(name)
    else:
        raise_bodo_error(dluw__uowg)
    xfbl__upqg = 0 if xfbl__upqg is None else xfbl__upqg
    xlpbs__azhh = ColNamesMetaType((xfbl__upqg,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            xlpbs__azhh)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
