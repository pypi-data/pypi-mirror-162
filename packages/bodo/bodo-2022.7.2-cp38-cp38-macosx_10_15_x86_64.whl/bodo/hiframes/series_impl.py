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
            bsmih__okh = bodo.hiframes.pd_series_ext.get_series_data(s)
            ggl__iqpm = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                bsmih__okh)
            return ggl__iqpm
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
            ajw__tntel = list()
            for mob__gooit in range(len(S)):
                ajw__tntel.append(S.iat[mob__gooit])
            return ajw__tntel
        return impl_float

    def impl(S):
        ajw__tntel = list()
        for mob__gooit in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, mob__gooit):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            ajw__tntel.append(S.iat[mob__gooit])
        return ajw__tntel
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    pnt__zbduy = dict(dtype=dtype, copy=copy, na_value=na_value)
    vqml__upv = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    pnt__zbduy = dict(name=name, inplace=inplace)
    vqml__upv = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', pnt__zbduy, vqml__upv,
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
        djnct__yhb = ', '.join(['index_arrs[{}]'.format(mob__gooit) for
            mob__gooit in range(S.index.nlevels)])
    else:
        djnct__yhb = '    bodo.utils.conversion.index_to_array(index)\n'
    mmb__ricq = 'index' if 'index' != series_name else 'level_0'
    itqpe__xzhhm = get_index_names(S.index, 'Series.reset_index()', mmb__ricq)
    columns = [name for name in itqpe__xzhhm]
    columns.append(series_name)
    gjl__nxker = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    gjl__nxker += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    gjl__nxker += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        gjl__nxker += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    gjl__nxker += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    gjl__nxker += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({djnct__yhb}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    sho__bgyuy = {}
    exec(gjl__nxker, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, sho__bgyuy)
    gsptf__dstia = sho__bgyuy['_impl']
    return gsptf__dstia


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        txso__rzwrw = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
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
        txso__rzwrw = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for mob__gooit in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[mob__gooit]):
                bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
            else:
                txso__rzwrw[mob__gooit] = np.round(arr[mob__gooit], decimals)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    pnt__zbduy = dict(level=level, numeric_only=numeric_only)
    vqml__upv = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(level=level, numeric_only=numeric_only)
    vqml__upv = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=
        level)
    vqml__upv = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', pnt__zbduy, vqml__upv,
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
        qxz__bzey = bodo.hiframes.pd_series_ext.get_series_data(S)
        inyp__pcreo = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        adsns__opuf = 0
        for mob__gooit in numba.parfors.parfor.internal_prange(len(qxz__bzey)):
            rbz__tnozn = 0
            zaueq__qyg = bodo.libs.array_kernels.isna(qxz__bzey, mob__gooit)
            kek__ady = bodo.libs.array_kernels.isna(inyp__pcreo, mob__gooit)
            if zaueq__qyg and not kek__ady or not zaueq__qyg and kek__ady:
                rbz__tnozn = 1
            elif not zaueq__qyg:
                if qxz__bzey[mob__gooit] != inyp__pcreo[mob__gooit]:
                    rbz__tnozn = 1
            adsns__opuf += rbz__tnozn
        return adsns__opuf == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    pnt__zbduy = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=
        level)
    vqml__upv = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    pnt__zbduy = dict(level=level)
    vqml__upv = dict(level=None)
    check_unsupported_args('Series.mad', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    eqt__qbkdd = types.float64
    hou__crpzt = types.float64
    if S.dtype == types.float32:
        eqt__qbkdd = types.float32
        hou__crpzt = types.float32
    mcm__kvm = eqt__qbkdd(0)
    tgy__mcf = hou__crpzt(0)
    klvi__huig = hou__crpzt(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        dvwb__wbhk = mcm__kvm
        adsns__opuf = tgy__mcf
        for mob__gooit in numba.parfors.parfor.internal_prange(len(A)):
            rbz__tnozn = mcm__kvm
            kneu__twm = tgy__mcf
            if not bodo.libs.array_kernels.isna(A, mob__gooit) or not skipna:
                rbz__tnozn = A[mob__gooit]
                kneu__twm = klvi__huig
            dvwb__wbhk += rbz__tnozn
            adsns__opuf += kneu__twm
        wrj__sbf = bodo.hiframes.series_kernels._mean_handle_nan(dvwb__wbhk,
            adsns__opuf)
        blubn__ibdjx = mcm__kvm
        for mob__gooit in numba.parfors.parfor.internal_prange(len(A)):
            rbz__tnozn = mcm__kvm
            if not bodo.libs.array_kernels.isna(A, mob__gooit) or not skipna:
                rbz__tnozn = abs(A[mob__gooit] - wrj__sbf)
            blubn__ibdjx += rbz__tnozn
        yvctf__cvlqi = bodo.hiframes.series_kernels._mean_handle_nan(
            blubn__ibdjx, adsns__opuf)
        return yvctf__cvlqi
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    pnt__zbduy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vqml__upv = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(level=level, numeric_only=numeric_only)
    vqml__upv = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', pnt__zbduy, vqml__upv,
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
        tmzhx__lkb = 0
        nrtln__ftmk = 0
        adsns__opuf = 0
        for mob__gooit in numba.parfors.parfor.internal_prange(len(A)):
            rbz__tnozn = 0
            kneu__twm = 0
            if not bodo.libs.array_kernels.isna(A, mob__gooit) or not skipna:
                rbz__tnozn = A[mob__gooit]
                kneu__twm = 1
            tmzhx__lkb += rbz__tnozn
            nrtln__ftmk += rbz__tnozn * rbz__tnozn
            adsns__opuf += kneu__twm
        oyg__huc = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            tmzhx__lkb, nrtln__ftmk, adsns__opuf, ddof)
        kecax__zwxfm = bodo.hiframes.series_kernels._sem_handle_nan(oyg__huc,
            adsns__opuf)
        return kecax__zwxfm
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    pnt__zbduy = dict(level=level, numeric_only=numeric_only)
    vqml__upv = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', pnt__zbduy, vqml__upv,
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
        tmzhx__lkb = 0.0
        nrtln__ftmk = 0.0
        djav__ahzgd = 0.0
        qktz__ncqt = 0.0
        adsns__opuf = 0
        for mob__gooit in numba.parfors.parfor.internal_prange(len(A)):
            rbz__tnozn = 0.0
            kneu__twm = 0
            if not bodo.libs.array_kernels.isna(A, mob__gooit) or not skipna:
                rbz__tnozn = np.float64(A[mob__gooit])
                kneu__twm = 1
            tmzhx__lkb += rbz__tnozn
            nrtln__ftmk += rbz__tnozn ** 2
            djav__ahzgd += rbz__tnozn ** 3
            qktz__ncqt += rbz__tnozn ** 4
            adsns__opuf += kneu__twm
        oyg__huc = bodo.hiframes.series_kernels.compute_kurt(tmzhx__lkb,
            nrtln__ftmk, djav__ahzgd, qktz__ncqt, adsns__opuf)
        return oyg__huc
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    pnt__zbduy = dict(level=level, numeric_only=numeric_only)
    vqml__upv = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', pnt__zbduy, vqml__upv,
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
        tmzhx__lkb = 0.0
        nrtln__ftmk = 0.0
        djav__ahzgd = 0.0
        adsns__opuf = 0
        for mob__gooit in numba.parfors.parfor.internal_prange(len(A)):
            rbz__tnozn = 0.0
            kneu__twm = 0
            if not bodo.libs.array_kernels.isna(A, mob__gooit) or not skipna:
                rbz__tnozn = np.float64(A[mob__gooit])
                kneu__twm = 1
            tmzhx__lkb += rbz__tnozn
            nrtln__ftmk += rbz__tnozn ** 2
            djav__ahzgd += rbz__tnozn ** 3
            adsns__opuf += kneu__twm
        oyg__huc = bodo.hiframes.series_kernels.compute_skew(tmzhx__lkb,
            nrtln__ftmk, djav__ahzgd, adsns__opuf)
        return oyg__huc
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    pnt__zbduy = dict(level=level, numeric_only=numeric_only)
    vqml__upv = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(level=level, numeric_only=numeric_only)
    vqml__upv = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', pnt__zbduy, vqml__upv,
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
        qxz__bzey = bodo.hiframes.pd_series_ext.get_series_data(S)
        inyp__pcreo = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        ydwb__lmoo = 0
        for mob__gooit in numba.parfors.parfor.internal_prange(len(qxz__bzey)):
            dtgr__msnci = qxz__bzey[mob__gooit]
            qfvw__mfwr = inyp__pcreo[mob__gooit]
            ydwb__lmoo += dtgr__msnci * qfvw__mfwr
        return ydwb__lmoo
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    pnt__zbduy = dict(skipna=skipna)
    vqml__upv = dict(skipna=True)
    check_unsupported_args('Series.cumsum', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(skipna=skipna)
    vqml__upv = dict(skipna=True)
    check_unsupported_args('Series.cumprod', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(skipna=skipna)
    vqml__upv = dict(skipna=True)
    check_unsupported_args('Series.cummin', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(skipna=skipna)
    vqml__upv = dict(skipna=True)
    check_unsupported_args('Series.cummax', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    vqml__upv = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        aid__exe = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, aid__exe, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    pnt__zbduy = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    vqml__upv = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(level=level)
    vqml__upv = dict(level=None)
    check_unsupported_args('Series.count', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    pnt__zbduy = dict(method=method, min_periods=min_periods)
    vqml__upv = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        jew__lhah = S.sum()
        gah__fvf = other.sum()
        a = n * (S * other).sum() - jew__lhah * gah__fvf
        qkl__nxuj = n * (S ** 2).sum() - jew__lhah ** 2
        otop__crdp = n * (other ** 2).sum() - gah__fvf ** 2
        return a / np.sqrt(qkl__nxuj * otop__crdp)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    pnt__zbduy = dict(min_periods=min_periods)
    vqml__upv = dict(min_periods=None)
    check_unsupported_args('Series.cov', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        jew__lhah = S.mean()
        gah__fvf = other.mean()
        dvfv__akig = ((S - jew__lhah) * (other - gah__fvf)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(dvfv__akig, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            corlz__ttk = np.sign(sum_val)
            return np.inf * corlz__ttk
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    pnt__zbduy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vqml__upv = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    vqml__upv = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(axis=axis, skipna=skipna)
    vqml__upv = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(axis=axis, skipna=skipna)
    vqml__upv = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', pnt__zbduy, vqml__upv,
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
    pnt__zbduy = dict(level=level, numeric_only=numeric_only)
    vqml__upv = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', pnt__zbduy, vqml__upv,
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
        uzvv__mrd = arr[:n]
        hjbsg__mosld = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(uzvv__mrd,
            hjbsg__mosld, name)
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
        vauoe__ovvo = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        uzvv__mrd = arr[vauoe__ovvo:]
        hjbsg__mosld = index[vauoe__ovvo:]
        return bodo.hiframes.pd_series_ext.init_series(uzvv__mrd,
            hjbsg__mosld, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    rtyu__iwtq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in rtyu__iwtq:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            loyk__udoly = index[0]
            fzp__ftrwa = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                loyk__udoly, False))
        else:
            fzp__ftrwa = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        uzvv__mrd = arr[:fzp__ftrwa]
        hjbsg__mosld = index[:fzp__ftrwa]
        return bodo.hiframes.pd_series_ext.init_series(uzvv__mrd,
            hjbsg__mosld, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    rtyu__iwtq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in rtyu__iwtq:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            pslhi__jahtn = index[-1]
            fzp__ftrwa = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                pslhi__jahtn, True))
        else:
            fzp__ftrwa = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        uzvv__mrd = arr[len(arr) - fzp__ftrwa:]
        hjbsg__mosld = index[len(arr) - fzp__ftrwa:]
        return bodo.hiframes.pd_series_ext.init_series(uzvv__mrd,
            hjbsg__mosld, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        esyo__aducp = bodo.utils.conversion.index_to_array(index)
        fyl__nst, jjmt__dxwz = bodo.libs.array_kernels.first_last_valid_index(
            arr, esyo__aducp)
        return jjmt__dxwz if fyl__nst else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        esyo__aducp = bodo.utils.conversion.index_to_array(index)
        fyl__nst, jjmt__dxwz = bodo.libs.array_kernels.first_last_valid_index(
            arr, esyo__aducp, False)
        return jjmt__dxwz if fyl__nst else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    pnt__zbduy = dict(keep=keep)
    vqml__upv = dict(keep='first')
    check_unsupported_args('Series.nlargest', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        esyo__aducp = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        txso__rzwrw, yto__drelo = bodo.libs.array_kernels.nlargest(arr,
            esyo__aducp, n, True, bodo.hiframes.series_kernels.gt_f)
        qadcf__fth = bodo.utils.conversion.convert_to_index(yto__drelo)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
            qadcf__fth, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    pnt__zbduy = dict(keep=keep)
    vqml__upv = dict(keep='first')
    check_unsupported_args('Series.nsmallest', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        esyo__aducp = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        txso__rzwrw, yto__drelo = bodo.libs.array_kernels.nlargest(arr,
            esyo__aducp, n, False, bodo.hiframes.series_kernels.lt_f)
        qadcf__fth = bodo.utils.conversion.convert_to_index(yto__drelo)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
            qadcf__fth, name)
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
    pnt__zbduy = dict(errors=errors)
    vqml__upv = dict(errors='raise')
    check_unsupported_args('Series.astype', pnt__zbduy, vqml__upv,
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
        txso__rzwrw = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    pnt__zbduy = dict(axis=axis, is_copy=is_copy)
    vqml__upv = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        wmfq__eihch = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[wmfq__eihch],
            index[wmfq__eihch], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    pnt__zbduy = dict(axis=axis, kind=kind, order=order)
    vqml__upv = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fclfx__tto = S.notna().values
        if not fclfx__tto.all():
            txso__rzwrw = np.full(n, -1, np.int64)
            txso__rzwrw[fclfx__tto] = argsort(arr[fclfx__tto])
        else:
            txso__rzwrw = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    pnt__zbduy = dict(axis=axis, numeric_only=numeric_only)
    vqml__upv = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', pnt__zbduy, vqml__upv,
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
        txso__rzwrw = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    pnt__zbduy = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    vqml__upv = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    ihey__hfq = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        srin__clfkh = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ihey__hfq)
        qynbb__zvv = srin__clfkh.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        txso__rzwrw = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            qynbb__zvv, 0)
        qadcf__fth = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            qynbb__zvv)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
            qadcf__fth, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    pnt__zbduy = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    vqml__upv = dict(axis=0, inplace=False, kind='quicksort', ignore_index=
        False, key=None)
    check_unsupported_args('Series.sort_values', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    qjdm__edsik = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        srin__clfkh = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, qjdm__edsik)
        qynbb__zvv = srin__clfkh.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        txso__rzwrw = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            qynbb__zvv, 0)
        qadcf__fth = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            qynbb__zvv)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
            qadcf__fth, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    ynl__kel = is_overload_true(is_nullable)
    gjl__nxker = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    gjl__nxker += '  numba.parfors.parfor.init_prange()\n'
    gjl__nxker += '  n = len(arr)\n'
    if ynl__kel:
        gjl__nxker += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        gjl__nxker += '  out_arr = np.empty(n, np.int64)\n'
    gjl__nxker += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    gjl__nxker += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if ynl__kel:
        gjl__nxker += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        gjl__nxker += '      out_arr[i] = -1\n'
    gjl__nxker += '      continue\n'
    gjl__nxker += '    val = arr[i]\n'
    gjl__nxker += '    if include_lowest and val == bins[0]:\n'
    gjl__nxker += '      ind = 1\n'
    gjl__nxker += '    else:\n'
    gjl__nxker += '      ind = np.searchsorted(bins, val)\n'
    gjl__nxker += '    if ind == 0 or ind == len(bins):\n'
    if ynl__kel:
        gjl__nxker += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        gjl__nxker += '      out_arr[i] = -1\n'
    gjl__nxker += '    else:\n'
    gjl__nxker += '      out_arr[i] = ind - 1\n'
    gjl__nxker += '  return out_arr\n'
    sho__bgyuy = {}
    exec(gjl__nxker, {'bodo': bodo, 'np': np, 'numba': numba}, sho__bgyuy)
    impl = sho__bgyuy['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        adnj__hkkcs, uaav__fevg = np.divmod(x, 1)
        if adnj__hkkcs == 0:
            bmipz__xpulu = -int(np.floor(np.log10(abs(uaav__fevg)))
                ) - 1 + precision
        else:
            bmipz__xpulu = precision
        return np.around(x, bmipz__xpulu)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        dfo__vqti = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(dfo__vqti)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        ipbw__urg = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            jmyz__wlwnu = bins.copy()
            if right and include_lowest:
                jmyz__wlwnu[0] = jmyz__wlwnu[0] - ipbw__urg
            yxm__ost = bodo.libs.interval_arr_ext.init_interval_array(
                jmyz__wlwnu[:-1], jmyz__wlwnu[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(yxm__ost,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        jmyz__wlwnu = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            jmyz__wlwnu[0] = jmyz__wlwnu[0] - 10.0 ** -precision
        yxm__ost = bodo.libs.interval_arr_ext.init_interval_array(jmyz__wlwnu
            [:-1], jmyz__wlwnu[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(yxm__ost, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        vct__nbt = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        ufv__atwsr = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        txso__rzwrw = np.zeros(nbins, np.int64)
        for mob__gooit in range(len(vct__nbt)):
            txso__rzwrw[ufv__atwsr[mob__gooit]] = vct__nbt[mob__gooit]
        return txso__rzwrw
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
            nkk__tujvp = (max_val - min_val) * 0.001
            if right:
                bins[0] -= nkk__tujvp
            else:
                bins[-1] += nkk__tujvp
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    pnt__zbduy = dict(dropna=dropna)
    vqml__upv = dict(dropna=True)
    check_unsupported_args('Series.value_counts', pnt__zbduy, vqml__upv,
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
    ervva__vem = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    gjl__nxker = 'def impl(\n'
    gjl__nxker += '    S,\n'
    gjl__nxker += '    normalize=False,\n'
    gjl__nxker += '    sort=True,\n'
    gjl__nxker += '    ascending=False,\n'
    gjl__nxker += '    bins=None,\n'
    gjl__nxker += '    dropna=True,\n'
    gjl__nxker += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    gjl__nxker += '):\n'
    gjl__nxker += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    gjl__nxker += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    gjl__nxker += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if ervva__vem:
        gjl__nxker += '    right = True\n'
        gjl__nxker += _gen_bins_handling(bins, S.dtype)
        gjl__nxker += '    arr = get_bin_inds(bins, arr)\n'
    gjl__nxker += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    gjl__nxker += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    gjl__nxker += '    )\n'
    gjl__nxker += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if ervva__vem:
        gjl__nxker += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        gjl__nxker += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        gjl__nxker += '    index = get_bin_labels(bins)\n'
    else:
        gjl__nxker += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        gjl__nxker += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        gjl__nxker += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        gjl__nxker += '    )\n'
        gjl__nxker += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    gjl__nxker += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        gjl__nxker += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        mitiw__avzo = 'len(S)' if ervva__vem else 'count_arr.sum()'
        gjl__nxker += f'    res = res / float({mitiw__avzo})\n'
    gjl__nxker += '    return res\n'
    sho__bgyuy = {}
    exec(gjl__nxker, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, sho__bgyuy)
    impl = sho__bgyuy['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    gjl__nxker = ''
    if isinstance(bins, types.Integer):
        gjl__nxker += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        gjl__nxker += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            gjl__nxker += '    min_val = min_val.value\n'
            gjl__nxker += '    max_val = max_val.value\n'
        gjl__nxker += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            gjl__nxker += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        gjl__nxker += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return gjl__nxker


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    pnt__zbduy = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    vqml__upv = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    gjl__nxker = 'def impl(\n'
    gjl__nxker += '    x,\n'
    gjl__nxker += '    bins,\n'
    gjl__nxker += '    right=True,\n'
    gjl__nxker += '    labels=None,\n'
    gjl__nxker += '    retbins=False,\n'
    gjl__nxker += '    precision=3,\n'
    gjl__nxker += '    include_lowest=False,\n'
    gjl__nxker += "    duplicates='raise',\n"
    gjl__nxker += '    ordered=True\n'
    gjl__nxker += '):\n'
    if isinstance(x, SeriesType):
        gjl__nxker += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        gjl__nxker += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        gjl__nxker += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        gjl__nxker += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    gjl__nxker += _gen_bins_handling(bins, x.dtype)
    gjl__nxker += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    gjl__nxker += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    gjl__nxker += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    gjl__nxker += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        gjl__nxker += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        gjl__nxker += '    return res\n'
    else:
        gjl__nxker += '    return out_arr\n'
    sho__bgyuy = {}
    exec(gjl__nxker, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, sho__bgyuy)
    impl = sho__bgyuy['impl']
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
    pnt__zbduy = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    vqml__upv = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        dlq__nzaty = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, dlq__nzaty)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    pnt__zbduy = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    vqml__upv = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', pnt__zbduy, vqml__upv,
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
        biroj__ofod = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            qmo__dsfno = bodo.utils.conversion.coerce_to_array(index)
            srin__clfkh = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                qmo__dsfno, arr), index, biroj__ofod)
            return srin__clfkh.groupby(' ')['']
        return impl_index
    llhg__zpyq = by
    if isinstance(by, SeriesType):
        llhg__zpyq = by.data
    if isinstance(llhg__zpyq, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    njjc__wvegw = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        qmo__dsfno = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        srin__clfkh = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            qmo__dsfno, arr), index, njjc__wvegw)
        return srin__clfkh.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    pnt__zbduy = dict(verify_integrity=verify_integrity)
    vqml__upv = dict(verify_integrity=False)
    check_unsupported_args('Series.append', pnt__zbduy, vqml__upv,
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
            nkk__bmr = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            txso__rzwrw = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(txso__rzwrw, A, nkk__bmr, False)
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        txso__rzwrw = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    pnt__zbduy = dict(interpolation=interpolation)
    vqml__upv = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            txso__rzwrw = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
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
        drb__weof = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(drb__weof, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    pnt__zbduy = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    vqml__upv = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', pnt__zbduy, vqml__upv,
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
        qmf__zxfg = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        qmf__zxfg = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    gjl__nxker = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {qmf__zxfg}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    uenc__bgcfk = dict()
    exec(gjl__nxker, {'bodo': bodo, 'numba': numba}, uenc__bgcfk)
    txd__hqhi = uenc__bgcfk['impl']
    return txd__hqhi


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        qmf__zxfg = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        qmf__zxfg = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    gjl__nxker = 'def impl(S,\n'
    gjl__nxker += '     value=None,\n'
    gjl__nxker += '    method=None,\n'
    gjl__nxker += '    axis=None,\n'
    gjl__nxker += '    inplace=False,\n'
    gjl__nxker += '    limit=None,\n'
    gjl__nxker += '   downcast=None,\n'
    gjl__nxker += '):\n'
    gjl__nxker += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    gjl__nxker += '    n = len(in_arr)\n'
    gjl__nxker += f'    out_arr = {qmf__zxfg}(n, -1)\n'
    gjl__nxker += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    gjl__nxker += '        s = in_arr[j]\n'
    gjl__nxker += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    gjl__nxker += '            s = value\n'
    gjl__nxker += '        out_arr[j] = s\n'
    gjl__nxker += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    uenc__bgcfk = dict()
    exec(gjl__nxker, {'bodo': bodo, 'numba': numba}, uenc__bgcfk)
    txd__hqhi = uenc__bgcfk['impl']
    return txd__hqhi


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
    sfpm__tdmf = bodo.hiframes.pd_series_ext.get_series_data(value)
    for mob__gooit in numba.parfors.parfor.internal_prange(len(lcbu__rgt)):
        s = lcbu__rgt[mob__gooit]
        if bodo.libs.array_kernels.isna(lcbu__rgt, mob__gooit
            ) and not bodo.libs.array_kernels.isna(sfpm__tdmf, mob__gooit):
            s = sfpm__tdmf[mob__gooit]
        lcbu__rgt[mob__gooit] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
    for mob__gooit in numba.parfors.parfor.internal_prange(len(lcbu__rgt)):
        s = lcbu__rgt[mob__gooit]
        if bodo.libs.array_kernels.isna(lcbu__rgt, mob__gooit):
            s = value
        lcbu__rgt[mob__gooit] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    sfpm__tdmf = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(lcbu__rgt)
    txso__rzwrw = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for hkba__qgm in numba.parfors.parfor.internal_prange(n):
        s = lcbu__rgt[hkba__qgm]
        if bodo.libs.array_kernels.isna(lcbu__rgt, hkba__qgm
            ) and not bodo.libs.array_kernels.isna(sfpm__tdmf, hkba__qgm):
            s = sfpm__tdmf[hkba__qgm]
        txso__rzwrw[hkba__qgm] = s
        if bodo.libs.array_kernels.isna(lcbu__rgt, hkba__qgm
            ) and bodo.libs.array_kernels.isna(sfpm__tdmf, hkba__qgm):
            bodo.libs.array_kernels.setna(txso__rzwrw, hkba__qgm)
    return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    sfpm__tdmf = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(lcbu__rgt)
    txso__rzwrw = bodo.utils.utils.alloc_type(n, lcbu__rgt.dtype, (-1,))
    for mob__gooit in numba.parfors.parfor.internal_prange(n):
        s = lcbu__rgt[mob__gooit]
        if bodo.libs.array_kernels.isna(lcbu__rgt, mob__gooit
            ) and not bodo.libs.array_kernels.isna(sfpm__tdmf, mob__gooit):
            s = sfpm__tdmf[mob__gooit]
        txso__rzwrw[mob__gooit] = s
    return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    pnt__zbduy = dict(limit=limit, downcast=downcast)
    vqml__upv = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')
    yqzxh__nna = not is_overload_none(value)
    pfxsi__xjy = not is_overload_none(method)
    if yqzxh__nna and pfxsi__xjy:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not yqzxh__nna and not pfxsi__xjy:
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
    if pfxsi__xjy:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        ywvob__heqd = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(ywvob__heqd)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(ywvob__heqd)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    dibm__alxxg = element_type(S.data)
    uiocz__ofk = None
    if yqzxh__nna:
        uiocz__ofk = element_type(types.unliteral(value))
    if uiocz__ofk and not can_replace(dibm__alxxg, uiocz__ofk):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {uiocz__ofk} with series type {dibm__alxxg}'
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
        suo__kaa = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                sfpm__tdmf = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(lcbu__rgt)
                txso__rzwrw = bodo.utils.utils.alloc_type(n, suo__kaa, (-1,))
                for mob__gooit in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lcbu__rgt, mob__gooit
                        ) and bodo.libs.array_kernels.isna(sfpm__tdmf,
                        mob__gooit):
                        bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                        continue
                    if bodo.libs.array_kernels.isna(lcbu__rgt, mob__gooit):
                        txso__rzwrw[mob__gooit
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            sfpm__tdmf[mob__gooit])
                        continue
                    txso__rzwrw[mob__gooit
                        ] = bodo.utils.conversion.unbox_if_timestamp(lcbu__rgt
                        [mob__gooit])
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                    index, name)
            return fillna_series_impl
        if pfxsi__xjy:
            wcej__yfbo = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(dibm__alxxg, (types.Integer, types.Float)
                ) and dibm__alxxg not in wcej__yfbo:
                raise BodoError(
                    f"Series.fillna(): series of type {dibm__alxxg} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                txso__rzwrw = bodo.libs.array_kernels.ffill_bfill_arr(lcbu__rgt
                    , method)
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(lcbu__rgt)
            txso__rzwrw = bodo.utils.utils.alloc_type(n, suo__kaa, (-1,))
            for mob__gooit in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(lcbu__rgt[
                    mob__gooit])
                if bodo.libs.array_kernels.isna(lcbu__rgt, mob__gooit):
                    s = value
                txso__rzwrw[mob__gooit] = s
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        uoc__xcs = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        pnt__zbduy = dict(limit=limit, downcast=downcast)
        vqml__upv = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', pnt__zbduy,
            vqml__upv, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        dibm__alxxg = element_type(S.data)
        wcej__yfbo = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(dibm__alxxg, (types.Integer, types.Float)
            ) and dibm__alxxg not in wcej__yfbo:
            raise BodoError(
                f'Series.{overload_name}(): series of type {dibm__alxxg} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            txso__rzwrw = bodo.libs.array_kernels.ffill_bfill_arr(lcbu__rgt,
                uoc__xcs)
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        qbb__utvup = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            qbb__utvup)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        gha__cgey = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(gha__cgey)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        gha__cgey = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(gha__cgey)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        gha__cgey = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(gha__cgey)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    pnt__zbduy = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    vmr__kbvz = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', pnt__zbduy, vmr__kbvz,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    dibm__alxxg = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        zxir__sdhp = element_type(to_replace.key_type)
        uiocz__ofk = element_type(to_replace.value_type)
    else:
        zxir__sdhp = element_type(to_replace)
        uiocz__ofk = element_type(value)
    apjd__fojv = None
    if dibm__alxxg != types.unliteral(zxir__sdhp):
        if bodo.utils.typing.equality_always_false(dibm__alxxg, types.
            unliteral(zxir__sdhp)
            ) or not bodo.utils.typing.types_equality_exists(dibm__alxxg,
            zxir__sdhp):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(dibm__alxxg, (types.Float, types.Integer)
            ) or dibm__alxxg == np.bool_:
            apjd__fojv = dibm__alxxg
    if not can_replace(dibm__alxxg, types.unliteral(uiocz__ofk)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    vqbc__aac = to_str_arr_if_dict_array(S.data)
    if isinstance(vqbc__aac, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(lcbu__rgt.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(lcbu__rgt)
        txso__rzwrw = bodo.utils.utils.alloc_type(n, vqbc__aac, (-1,))
        pjf__imo = build_replace_dict(to_replace, value, apjd__fojv)
        for mob__gooit in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(lcbu__rgt, mob__gooit):
                bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                continue
            s = lcbu__rgt[mob__gooit]
            if s in pjf__imo:
                s = pjf__imo[s]
            txso__rzwrw[mob__gooit] = s
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    mrc__wwsbm = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    dmy__nhf = is_iterable_type(to_replace)
    jcx__enpc = isinstance(value, (types.Number, Decimal128Type)) or value in [
        bodo.string_type, bodo.bytes_type, types.boolean]
    kjdqz__khcuv = is_iterable_type(value)
    if mrc__wwsbm and jcx__enpc:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                pjf__imo = {}
                pjf__imo[key_dtype_conv(to_replace)] = value
                return pjf__imo
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            pjf__imo = {}
            pjf__imo[to_replace] = value
            return pjf__imo
        return impl
    if dmy__nhf and jcx__enpc:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                pjf__imo = {}
                for uzw__xfv in to_replace:
                    pjf__imo[key_dtype_conv(uzw__xfv)] = value
                return pjf__imo
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            pjf__imo = {}
            for uzw__xfv in to_replace:
                pjf__imo[uzw__xfv] = value
            return pjf__imo
        return impl
    if dmy__nhf and kjdqz__khcuv:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                pjf__imo = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for mob__gooit in range(len(to_replace)):
                    pjf__imo[key_dtype_conv(to_replace[mob__gooit])] = value[
                        mob__gooit]
                return pjf__imo
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            pjf__imo = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for mob__gooit in range(len(to_replace)):
                pjf__imo[to_replace[mob__gooit]] = value[mob__gooit]
            return pjf__imo
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
            txso__rzwrw = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        txso__rzwrw = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    pnt__zbduy = dict(ignore_index=ignore_index)
    bboi__psja = dict(ignore_index=False)
    check_unsupported_args('Series.explode', pnt__zbduy, bboi__psja,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        esyo__aducp = bodo.utils.conversion.index_to_array(index)
        txso__rzwrw, njb__suc = bodo.libs.array_kernels.explode(arr,
            esyo__aducp)
        qadcf__fth = bodo.utils.conversion.index_from_array(njb__suc)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
            qadcf__fth, name)
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
            yeeu__iqd = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for mob__gooit in numba.parfors.parfor.internal_prange(n):
                yeeu__iqd[mob__gooit] = np.argmax(a[mob__gooit])
            return yeeu__iqd
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            yagkq__voydj = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for mob__gooit in numba.parfors.parfor.internal_prange(n):
                yagkq__voydj[mob__gooit] = np.argmin(a[mob__gooit])
            return yagkq__voydj
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
    pnt__zbduy = dict(axis=axis, inplace=inplace, how=how)
    lykc__vgzb = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', pnt__zbduy, lykc__vgzb,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            fclfx__tto = S.notna().values
            esyo__aducp = bodo.utils.conversion.extract_index_array(S)
            qadcf__fth = bodo.utils.conversion.convert_to_index(esyo__aducp
                [fclfx__tto])
            txso__rzwrw = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(lcbu__rgt))
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                qadcf__fth, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            esyo__aducp = bodo.utils.conversion.extract_index_array(S)
            fclfx__tto = S.notna().values
            qadcf__fth = bodo.utils.conversion.convert_to_index(esyo__aducp
                [fclfx__tto])
            txso__rzwrw = lcbu__rgt[fclfx__tto]
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                qadcf__fth, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    pnt__zbduy = dict(freq=freq, axis=axis, fill_value=fill_value)
    vqml__upv = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', pnt__zbduy, vqml__upv,
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
        txso__rzwrw = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    pnt__zbduy = dict(fill_method=fill_method, limit=limit, freq=freq)
    vqml__upv = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', pnt__zbduy, vqml__upv,
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
        txso__rzwrw = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
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
            ijlbl__bfgt = 'None'
        else:
            ijlbl__bfgt = 'other'
        gjl__nxker = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            gjl__nxker += '  cond = ~cond\n'
        gjl__nxker += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        gjl__nxker += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        gjl__nxker += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        gjl__nxker += f"""  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {ijlbl__bfgt})
"""
        gjl__nxker += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        sho__bgyuy = {}
        exec(gjl__nxker, {'bodo': bodo, 'np': np}, sho__bgyuy)
        impl = sho__bgyuy['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        qbb__utvup = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(qbb__utvup)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    pnt__zbduy = dict(inplace=inplace, level=level, errors=errors, try_cast
        =try_cast)
    vqml__upv = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', pnt__zbduy, vqml__upv,
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
    amlv__uxjmg = is_overload_constant_nan(other)
    if not (is_default or amlv__uxjmg or is_scalar_type(other) or 
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
            vprb__ime = arr.dtype.elem_type
        else:
            vprb__ime = arr.dtype
        if is_iterable_type(other):
            pdcyw__denuk = other.dtype
        elif amlv__uxjmg:
            pdcyw__denuk = types.float64
        else:
            pdcyw__denuk = types.unliteral(other)
        if not amlv__uxjmg and not is_common_scalar_dtype([vprb__ime,
            pdcyw__denuk]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        pnt__zbduy = dict(level=level, axis=axis)
        vqml__upv = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), pnt__zbduy,
            vqml__upv, package_name='pandas', module_name='Series')
        ydpd__fphw = other == string_type or is_overload_constant_str(other)
        oeg__kgyie = is_iterable_type(other) and other.dtype == string_type
        tkt__awg = S.dtype == string_type and (op == operator.add and (
            ydpd__fphw or oeg__kgyie) or op == operator.mul and isinstance(
            other, types.Integer))
        wsqeh__yxjvg = S.dtype == bodo.timedelta64ns
        eml__fod = S.dtype == bodo.datetime64ns
        ngt__svgrg = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        wld__hkoa = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        mvqi__rha = wsqeh__yxjvg and (ngt__svgrg or wld__hkoa
            ) or eml__fod and ngt__svgrg
        mvqi__rha = mvqi__rha and op == operator.add
        if not (isinstance(S.dtype, types.Number) or tkt__awg or mvqi__rha):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        rzvnq__vsh = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            vqbc__aac = rzvnq__vsh.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and vqbc__aac == types.Array(types.bool_, 1, 'C'):
                vqbc__aac = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                txso__rzwrw = bodo.utils.utils.alloc_type(n, vqbc__aac, (-1,))
                for mob__gooit in numba.parfors.parfor.internal_prange(n):
                    pbzxe__vgla = bodo.libs.array_kernels.isna(arr, mob__gooit)
                    if pbzxe__vgla:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(txso__rzwrw,
                                mob__gooit)
                        else:
                            txso__rzwrw[mob__gooit] = op(fill_value, other)
                    else:
                        txso__rzwrw[mob__gooit] = op(arr[mob__gooit], other)
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        vqbc__aac = rzvnq__vsh.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and vqbc__aac == types.Array(
            types.bool_, 1, 'C'):
            vqbc__aac = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xhxar__uxv = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            txso__rzwrw = bodo.utils.utils.alloc_type(n, vqbc__aac, (-1,))
            for mob__gooit in numba.parfors.parfor.internal_prange(n):
                pbzxe__vgla = bodo.libs.array_kernels.isna(arr, mob__gooit)
                jmqa__kqq = bodo.libs.array_kernels.isna(xhxar__uxv, mob__gooit
                    )
                if pbzxe__vgla and jmqa__kqq:
                    bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                elif pbzxe__vgla:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                    else:
                        txso__rzwrw[mob__gooit] = op(fill_value, xhxar__uxv
                            [mob__gooit])
                elif jmqa__kqq:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                    else:
                        txso__rzwrw[mob__gooit] = op(arr[mob__gooit],
                            fill_value)
                else:
                    txso__rzwrw[mob__gooit] = op(arr[mob__gooit],
                        xhxar__uxv[mob__gooit])
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
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
        rzvnq__vsh = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            vqbc__aac = rzvnq__vsh.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and vqbc__aac == types.Array(types.bool_, 1, 'C'):
                vqbc__aac = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                txso__rzwrw = bodo.utils.utils.alloc_type(n, vqbc__aac, None)
                for mob__gooit in numba.parfors.parfor.internal_prange(n):
                    pbzxe__vgla = bodo.libs.array_kernels.isna(arr, mob__gooit)
                    if pbzxe__vgla:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(txso__rzwrw,
                                mob__gooit)
                        else:
                            txso__rzwrw[mob__gooit] = op(other, fill_value)
                    else:
                        txso__rzwrw[mob__gooit] = op(other, arr[mob__gooit])
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        vqbc__aac = rzvnq__vsh.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and vqbc__aac == types.Array(
            types.bool_, 1, 'C'):
            vqbc__aac = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xhxar__uxv = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            txso__rzwrw = bodo.utils.utils.alloc_type(n, vqbc__aac, None)
            for mob__gooit in numba.parfors.parfor.internal_prange(n):
                pbzxe__vgla = bodo.libs.array_kernels.isna(arr, mob__gooit)
                jmqa__kqq = bodo.libs.array_kernels.isna(xhxar__uxv, mob__gooit
                    )
                txso__rzwrw[mob__gooit] = op(xhxar__uxv[mob__gooit], arr[
                    mob__gooit])
                if pbzxe__vgla and jmqa__kqq:
                    bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                elif pbzxe__vgla:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                    else:
                        txso__rzwrw[mob__gooit] = op(xhxar__uxv[mob__gooit],
                            fill_value)
                elif jmqa__kqq:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                    else:
                        txso__rzwrw[mob__gooit] = op(fill_value, arr[
                            mob__gooit])
                else:
                    txso__rzwrw[mob__gooit] = op(xhxar__uxv[mob__gooit],
                        arr[mob__gooit])
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
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
    for op, ijhyk__irg in explicit_binop_funcs_two_ways.items():
        for name in ijhyk__irg:
            qbb__utvup = create_explicit_binary_op_overload(op)
            stlg__hzh = create_explicit_binary_reverse_op_overload(op)
            otpnq__wqwq = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(qbb__utvup)
            overload_method(SeriesType, otpnq__wqwq, no_unliteral=True)(
                stlg__hzh)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        qbb__utvup = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(qbb__utvup)
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
                ubhl__lwv = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                txso__rzwrw = dt64_arr_sub(arr, ubhl__lwv)
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
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
                txso__rzwrw = np.empty(n, np.dtype('datetime64[ns]'))
                for mob__gooit in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, mob__gooit):
                        bodo.libs.array_kernels.setna(txso__rzwrw, mob__gooit)
                        continue
                    pmnk__cassg = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[mob__gooit]))
                    wmzcj__ymffb = op(pmnk__cassg, rhs)
                    txso__rzwrw[mob__gooit
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wmzcj__ymffb.value)
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
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
                    ubhl__lwv = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    txso__rzwrw = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(ubhl__lwv))
                    return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ubhl__lwv = bodo.utils.conversion.get_array_if_series_or_index(
                    rhs)
                txso__rzwrw = op(arr, ubhl__lwv)
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    unsn__wsy = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    txso__rzwrw = op(bodo.utils.conversion.
                        unbox_if_timestamp(unsn__wsy), arr)
                    return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                unsn__wsy = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                txso__rzwrw = op(unsn__wsy, arr)
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        qbb__utvup = create_binary_op_overload(op)
        overload(op)(qbb__utvup)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    mgaa__vli = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, mgaa__vli)
        for mob__gooit in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, mob__gooit
                ) or bodo.libs.array_kernels.isna(arg2, mob__gooit):
                bodo.libs.array_kernels.setna(S, mob__gooit)
                continue
            S[mob__gooit
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                mob__gooit]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[mob__gooit]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                xhxar__uxv = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, xhxar__uxv)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        qbb__utvup = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(qbb__utvup)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                txso__rzwrw = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        qbb__utvup = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(qbb__utvup)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    txso__rzwrw = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
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
                    xhxar__uxv = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    txso__rzwrw = ufunc(arr, xhxar__uxv)
                    return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    xhxar__uxv = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    txso__rzwrw = ufunc(arr, xhxar__uxv)
                    return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        qbb__utvup = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(qbb__utvup)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        kzixn__aasn = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.
            copy(),))
        bsmih__okh = np.arange(n),
        bodo.libs.timsort.sort(kzixn__aasn, 0, n, bsmih__okh)
        return bsmih__okh[0]
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
        ovrsl__dvej = get_overload_const_str(downcast)
        if ovrsl__dvej in ('integer', 'signed'):
            out_dtype = types.int64
        elif ovrsl__dvej == 'unsigned':
            out_dtype = types.uint64
        else:
            assert ovrsl__dvej == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            lcbu__rgt = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            txso__rzwrw = pd.to_numeric(lcbu__rgt, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            jysn__woh = np.empty(n, np.float64)
            for mob__gooit in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, mob__gooit):
                    bodo.libs.array_kernels.setna(jysn__woh, mob__gooit)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(jysn__woh,
                        mob__gooit, arg_a, mob__gooit)
            return jysn__woh
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            jysn__woh = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for mob__gooit in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, mob__gooit):
                    bodo.libs.array_kernels.setna(jysn__woh, mob__gooit)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(jysn__woh,
                        mob__gooit, arg_a, mob__gooit)
            return jysn__woh
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        gimkr__tobx = if_series_to_array_type(args[0])
        if isinstance(gimkr__tobx, types.Array) and isinstance(gimkr__tobx.
            dtype, types.Integer):
            gimkr__tobx = types.Array(types.float64, 1, 'C')
        return gimkr__tobx(*args)


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
    licw__vagah = bodo.utils.utils.is_array_typ(x, True)
    aaza__ixktt = bodo.utils.utils.is_array_typ(y, True)
    gjl__nxker = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        gjl__nxker += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if licw__vagah and not bodo.utils.utils.is_array_typ(x, False):
        gjl__nxker += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if aaza__ixktt and not bodo.utils.utils.is_array_typ(y, False):
        gjl__nxker += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    gjl__nxker += '  n = len(condition)\n'
    jtzfi__wub = x.dtype if licw__vagah else types.unliteral(x)
    kqaqk__ppv = y.dtype if aaza__ixktt else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        jtzfi__wub = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        kqaqk__ppv = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    giw__pvosg = get_data(x)
    kbcb__hylw = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(bsmih__okh) for
        bsmih__okh in [giw__pvosg, kbcb__hylw])
    if kbcb__hylw == types.none:
        if isinstance(jtzfi__wub, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif giw__pvosg == kbcb__hylw and not is_nullable:
        out_dtype = dtype_to_array_type(jtzfi__wub)
    elif jtzfi__wub == string_type or kqaqk__ppv == string_type:
        out_dtype = bodo.string_array_type
    elif giw__pvosg == bytes_type or (licw__vagah and jtzfi__wub == bytes_type
        ) and (kbcb__hylw == bytes_type or aaza__ixktt and kqaqk__ppv ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(jtzfi__wub, bodo.PDCategoricalDtype):
        out_dtype = None
    elif jtzfi__wub in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(jtzfi__wub, 1, 'C')
    elif kqaqk__ppv in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(kqaqk__ppv, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(jtzfi__wub), numba.np.numpy_support.
            as_dtype(kqaqk__ppv)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(jtzfi__wub, bodo.PDCategoricalDtype):
        lbomx__nzld = 'x'
    else:
        lbomx__nzld = 'out_dtype'
    gjl__nxker += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {lbomx__nzld}, (-1,))\n')
    if isinstance(jtzfi__wub, bodo.PDCategoricalDtype):
        gjl__nxker += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        gjl__nxker += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    gjl__nxker += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    gjl__nxker += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if licw__vagah:
        gjl__nxker += '      if bodo.libs.array_kernels.isna(x, j):\n'
        gjl__nxker += '        setna(out_arr, j)\n'
        gjl__nxker += '        continue\n'
    if isinstance(jtzfi__wub, bodo.PDCategoricalDtype):
        gjl__nxker += '      out_codes[j] = x_codes[j]\n'
    else:
        gjl__nxker += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if licw__vagah else 'x'))
    gjl__nxker += '    else:\n'
    if aaza__ixktt:
        gjl__nxker += '      if bodo.libs.array_kernels.isna(y, j):\n'
        gjl__nxker += '        setna(out_arr, j)\n'
        gjl__nxker += '        continue\n'
    if kbcb__hylw == types.none:
        if isinstance(jtzfi__wub, bodo.PDCategoricalDtype):
            gjl__nxker += '      out_codes[j] = -1\n'
        else:
            gjl__nxker += '      setna(out_arr, j)\n'
    else:
        gjl__nxker += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if aaza__ixktt else 'y'))
    gjl__nxker += '  return out_arr\n'
    sho__bgyuy = {}
    exec(gjl__nxker, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, sho__bgyuy)
    gsptf__dstia = sho__bgyuy['_impl']
    return gsptf__dstia


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
        jmu__fdy = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(jmu__fdy, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(jmu__fdy):
            dyy__phh = jmu__fdy.data.dtype
        else:
            dyy__phh = jmu__fdy.dtype
        if isinstance(dyy__phh, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        nqwuw__atk = jmu__fdy
    else:
        bimnr__ksfu = []
        for jmu__fdy in choicelist:
            if not bodo.utils.utils.is_array_typ(jmu__fdy, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(jmu__fdy):
                dyy__phh = jmu__fdy.data.dtype
            else:
                dyy__phh = jmu__fdy.dtype
            if isinstance(dyy__phh, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            bimnr__ksfu.append(dyy__phh)
        if not is_common_scalar_dtype(bimnr__ksfu):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        nqwuw__atk = choicelist[0]
    if is_series_type(nqwuw__atk):
        nqwuw__atk = nqwuw__atk.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, nqwuw__atk.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(nqwuw__atk, types.Array) or isinstance(nqwuw__atk,
        BooleanArrayType) or isinstance(nqwuw__atk, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(nqwuw__atk, False) and nqwuw__atk.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {nqwuw__atk} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    wmde__gml = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        bhofw__mtrg = choicelist.dtype
    else:
        dja__hjkx = False
        bimnr__ksfu = []
        for jmu__fdy in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(jmu__fdy,
                'numpy.select()')
            if is_nullable_type(jmu__fdy):
                dja__hjkx = True
            if is_series_type(jmu__fdy):
                dyy__phh = jmu__fdy.data.dtype
            else:
                dyy__phh = jmu__fdy.dtype
            if isinstance(dyy__phh, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            bimnr__ksfu.append(dyy__phh)
        oibhh__azgfj, wvuc__grekz = get_common_scalar_dtype(bimnr__ksfu)
        if not wvuc__grekz:
            raise BodoError('Internal error in overload_np_select')
        kfbux__oroj = dtype_to_array_type(oibhh__azgfj)
        if dja__hjkx:
            kfbux__oroj = to_nullable_type(kfbux__oroj)
        bhofw__mtrg = kfbux__oroj
    if isinstance(bhofw__mtrg, SeriesType):
        bhofw__mtrg = bhofw__mtrg.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        hxc__bluma = True
    else:
        hxc__bluma = False
    ussln__jsyw = False
    xwnxg__dyi = False
    if hxc__bluma:
        if isinstance(bhofw__mtrg.dtype, types.Number):
            pass
        elif bhofw__mtrg.dtype == types.bool_:
            xwnxg__dyi = True
        else:
            ussln__jsyw = True
            bhofw__mtrg = to_nullable_type(bhofw__mtrg)
    elif default == types.none or is_overload_constant_nan(default):
        ussln__jsyw = True
        bhofw__mtrg = to_nullable_type(bhofw__mtrg)
    gjl__nxker = 'def np_select_impl(condlist, choicelist, default=0):\n'
    gjl__nxker += '  if len(condlist) != len(choicelist):\n'
    gjl__nxker += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    gjl__nxker += '  output_len = len(choicelist[0])\n'
    gjl__nxker += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    gjl__nxker += '  for i in range(output_len):\n'
    if ussln__jsyw:
        gjl__nxker += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif xwnxg__dyi:
        gjl__nxker += '    out[i] = False\n'
    else:
        gjl__nxker += '    out[i] = default\n'
    if wmde__gml:
        gjl__nxker += '  for i in range(len(condlist) - 1, -1, -1):\n'
        gjl__nxker += '    cond = condlist[i]\n'
        gjl__nxker += '    choice = choicelist[i]\n'
        gjl__nxker += '    out = np.where(cond, choice, out)\n'
    else:
        for mob__gooit in range(len(choicelist) - 1, -1, -1):
            gjl__nxker += f'  cond = condlist[{mob__gooit}]\n'
            gjl__nxker += f'  choice = choicelist[{mob__gooit}]\n'
            gjl__nxker += f'  out = np.where(cond, choice, out)\n'
    gjl__nxker += '  return out'
    sho__bgyuy = dict()
    exec(gjl__nxker, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': bhofw__mtrg}, sho__bgyuy)
    impl = sho__bgyuy['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        txso__rzwrw = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    pnt__zbduy = dict(subset=subset, keep=keep, inplace=inplace)
    vqml__upv = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', pnt__zbduy, vqml__upv,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        djqo__gfrx = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (djqo__gfrx,), esyo__aducp = bodo.libs.array_kernels.drop_duplicates((
            djqo__gfrx,), index, 1)
        index = bodo.utils.conversion.index_from_array(esyo__aducp)
        return bodo.hiframes.pd_series_ext.init_series(djqo__gfrx, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    gknfy__sku = element_type(S.data)
    if not is_common_scalar_dtype([gknfy__sku, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([gknfy__sku, right]):
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
        txso__rzwrw = np.empty(n, np.bool_)
        for mob__gooit in numba.parfors.parfor.internal_prange(n):
            rbz__tnozn = bodo.utils.conversion.box_if_dt64(arr[mob__gooit])
            if inclusive == 'both':
                txso__rzwrw[mob__gooit
                    ] = rbz__tnozn <= right and rbz__tnozn >= left
            else:
                txso__rzwrw[mob__gooit
                    ] = rbz__tnozn < right and rbz__tnozn > left
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw, index, name
            )
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    pnt__zbduy = dict(axis=axis)
    vqml__upv = dict(axis=None)
    check_unsupported_args('Series.repeat', pnt__zbduy, vqml__upv,
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
            esyo__aducp = bodo.utils.conversion.index_to_array(index)
            txso__rzwrw = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            njb__suc = bodo.libs.array_kernels.repeat_kernel(esyo__aducp,
                repeats)
            qadcf__fth = bodo.utils.conversion.index_from_array(njb__suc)
            return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
                qadcf__fth, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        esyo__aducp = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        txso__rzwrw = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        njb__suc = bodo.libs.array_kernels.repeat_kernel(esyo__aducp, repeats)
        qadcf__fth = bodo.utils.conversion.index_from_array(njb__suc)
        return bodo.hiframes.pd_series_ext.init_series(txso__rzwrw,
            qadcf__fth, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        bsmih__okh = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(bsmih__okh)
        nkpp__alws = {}
        for mob__gooit in range(n):
            rbz__tnozn = bodo.utils.conversion.box_if_dt64(bsmih__okh[
                mob__gooit])
            nkpp__alws[index[mob__gooit]] = rbz__tnozn
        return nkpp__alws
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    ywvob__heqd = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            cngf__uffu = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(ywvob__heqd)
    elif is_literal_type(name):
        cngf__uffu = get_literal_value(name)
    else:
        raise_bodo_error(ywvob__heqd)
    cngf__uffu = 0 if cngf__uffu is None else cngf__uffu
    mmgiw__zlik = ColNamesMetaType((cngf__uffu,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            mmgiw__zlik)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
