"""
Implements array operations for usage by DataFrames and Series
such as count and max.
"""
import numba
import numpy as np
import pandas as pd
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.utils import tracing
from bodo.utils.typing import element_type, is_hashable_type, is_iterable_type, is_overload_true, is_overload_zero, is_str_arr_type


def array_op_any(arr, skipna=True):
    pass


@overload(array_op_any)
def overload_array_op_any(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        oov__foche = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        oov__foche = False
    elif A == bodo.string_array_type:
        oov__foche = ''
    elif A == bodo.binary_array_type:
        oov__foche = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        jae__kfrny = 0
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, uxpcu__mhiyh):
                if A[uxpcu__mhiyh] != oov__foche:
                    jae__kfrny += 1
        return jae__kfrny != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        oov__foche = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        oov__foche = False
    elif A == bodo.string_array_type:
        oov__foche = ''
    elif A == bodo.binary_array_type:
        oov__foche = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        jae__kfrny = 0
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, uxpcu__mhiyh):
                if A[uxpcu__mhiyh] == oov__foche:
                    jae__kfrny += 1
        return jae__kfrny == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    ykav__cry = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(ykav__cry.ctypes, arr,
        parallel, skipna)
    return ykav__cry[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        awto__bawhq = len(arr)
        cbjbg__boe = np.empty(awto__bawhq, np.bool_)
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(awto__bawhq):
            cbjbg__boe[uxpcu__mhiyh] = bodo.libs.array_kernels.isna(arr,
                uxpcu__mhiyh)
        return cbjbg__boe
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        jae__kfrny = 0
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
            alzef__qzolg = 0
            if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                alzef__qzolg = 1
            jae__kfrny += alzef__qzolg
        ykav__cry = jae__kfrny
        return ykav__cry
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    qbuxm__ldh = array_op_count(arr)
    tli__hpswa = array_op_min(arr)
    vqkl__maiv = array_op_max(arr)
    gbv__qssg = array_op_mean(arr)
    yitvg__hudh = array_op_std(arr)
    myxri__akcj = array_op_quantile(arr, 0.25)
    tgw__ocrh = array_op_quantile(arr, 0.5)
    hmcr__hlx = array_op_quantile(arr, 0.75)
    return (qbuxm__ldh, gbv__qssg, yitvg__hudh, tli__hpswa, myxri__akcj,
        tgw__ocrh, hmcr__hlx, vqkl__maiv)


def array_op_describe_dt_impl(arr):
    qbuxm__ldh = array_op_count(arr)
    tli__hpswa = array_op_min(arr)
    vqkl__maiv = array_op_max(arr)
    gbv__qssg = array_op_mean(arr)
    myxri__akcj = array_op_quantile(arr, 0.25)
    tgw__ocrh = array_op_quantile(arr, 0.5)
    hmcr__hlx = array_op_quantile(arr, 0.75)
    return (qbuxm__ldh, gbv__qssg, tli__hpswa, myxri__akcj, tgw__ocrh,
        hmcr__hlx, vqkl__maiv)


@overload(array_op_describe)
def overload_array_op_describe(arr):
    if arr.dtype == bodo.datetime64ns:
        return array_op_describe_dt_impl
    return array_op_describe_impl


@generated_jit(nopython=True)
def array_op_nbytes(arr):
    return array_op_nbytes_impl


def array_op_nbytes_impl(arr):
    return arr.nbytes


def array_op_min(arr):
    pass


@overload(array_op_min)
def overload_array_op_min(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            nej__zov = numba.cpython.builtins.get_type_max_value(np.int64)
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
                tetm__zzcq = nej__zov
                alzef__qzolg = 0
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                    tetm__zzcq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[uxpcu__mhiyh]))
                    alzef__qzolg = 1
                nej__zov = min(nej__zov, tetm__zzcq)
                jae__kfrny += alzef__qzolg
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(nej__zov,
                jae__kfrny)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            nej__zov = numba.cpython.builtins.get_type_max_value(np.int64)
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
                tetm__zzcq = nej__zov
                alzef__qzolg = 0
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                    tetm__zzcq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[uxpcu__mhiyh]))
                    alzef__qzolg = 1
                nej__zov = min(nej__zov, tetm__zzcq)
                jae__kfrny += alzef__qzolg
            return bodo.hiframes.pd_index_ext._dti_val_finalize(nej__zov,
                jae__kfrny)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            ckx__nwz = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            nej__zov = numba.cpython.builtins.get_type_max_value(np.int64)
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(
                ckx__nwz)):
                jgpec__pzp = ckx__nwz[uxpcu__mhiyh]
                if jgpec__pzp == -1:
                    continue
                nej__zov = min(nej__zov, jgpec__pzp)
                jae__kfrny += 1
            ykav__cry = bodo.hiframes.series_kernels._box_cat_val(nej__zov,
                arr.dtype, jae__kfrny)
            return ykav__cry
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            nej__zov = bodo.hiframes.series_kernels._get_date_max_value()
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
                tetm__zzcq = nej__zov
                alzef__qzolg = 0
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                    tetm__zzcq = arr[uxpcu__mhiyh]
                    alzef__qzolg = 1
                nej__zov = min(nej__zov, tetm__zzcq)
                jae__kfrny += alzef__qzolg
            ykav__cry = bodo.hiframes.series_kernels._sum_handle_nan(nej__zov,
                jae__kfrny)
            return ykav__cry
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        nej__zov = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype)
        jae__kfrny = 0
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
            tetm__zzcq = nej__zov
            alzef__qzolg = 0
            if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                tetm__zzcq = arr[uxpcu__mhiyh]
                alzef__qzolg = 1
            nej__zov = min(nej__zov, tetm__zzcq)
            jae__kfrny += alzef__qzolg
        ykav__cry = bodo.hiframes.series_kernels._sum_handle_nan(nej__zov,
            jae__kfrny)
        return ykav__cry
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            nej__zov = numba.cpython.builtins.get_type_min_value(np.int64)
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
                tetm__zzcq = nej__zov
                alzef__qzolg = 0
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                    tetm__zzcq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[uxpcu__mhiyh]))
                    alzef__qzolg = 1
                nej__zov = max(nej__zov, tetm__zzcq)
                jae__kfrny += alzef__qzolg
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(nej__zov,
                jae__kfrny)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            nej__zov = numba.cpython.builtins.get_type_min_value(np.int64)
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
                tetm__zzcq = nej__zov
                alzef__qzolg = 0
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                    tetm__zzcq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[uxpcu__mhiyh]))
                    alzef__qzolg = 1
                nej__zov = max(nej__zov, tetm__zzcq)
                jae__kfrny += alzef__qzolg
            return bodo.hiframes.pd_index_ext._dti_val_finalize(nej__zov,
                jae__kfrny)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            ckx__nwz = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            nej__zov = -1
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(
                ckx__nwz)):
                nej__zov = max(nej__zov, ckx__nwz[uxpcu__mhiyh])
            ykav__cry = bodo.hiframes.series_kernels._box_cat_val(nej__zov,
                arr.dtype, 1)
            return ykav__cry
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            nej__zov = bodo.hiframes.series_kernels._get_date_min_value()
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
                tetm__zzcq = nej__zov
                alzef__qzolg = 0
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                    tetm__zzcq = arr[uxpcu__mhiyh]
                    alzef__qzolg = 1
                nej__zov = max(nej__zov, tetm__zzcq)
                jae__kfrny += alzef__qzolg
            ykav__cry = bodo.hiframes.series_kernels._sum_handle_nan(nej__zov,
                jae__kfrny)
            return ykav__cry
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        nej__zov = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype)
        jae__kfrny = 0
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
            tetm__zzcq = nej__zov
            alzef__qzolg = 0
            if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                tetm__zzcq = arr[uxpcu__mhiyh]
                alzef__qzolg = 1
            nej__zov = max(nej__zov, tetm__zzcq)
            jae__kfrny += alzef__qzolg
        ykav__cry = bodo.hiframes.series_kernels._sum_handle_nan(nej__zov,
            jae__kfrny)
        return ykav__cry
    return impl


def array_op_mean(arr):
    pass


@overload(array_op_mean)
def overload_array_op_mean(arr):
    if arr.dtype == bodo.datetime64ns:

        def impl(arr):
            return pd.Timestamp(types.int64(bodo.libs.array_ops.
                array_op_mean(arr.view(np.int64))))
        return impl
    tmwi__xxucl = types.float64
    wipov__crcwe = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        tmwi__xxucl = types.float32
        wipov__crcwe = types.float32
    kiso__pqo = tmwi__xxucl(0)
    owca__yzmu = wipov__crcwe(0)
    cps__tbk = wipov__crcwe(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        nej__zov = kiso__pqo
        jae__kfrny = owca__yzmu
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
            tetm__zzcq = kiso__pqo
            alzef__qzolg = owca__yzmu
            if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                tetm__zzcq = arr[uxpcu__mhiyh]
                alzef__qzolg = cps__tbk
            nej__zov += tetm__zzcq
            jae__kfrny += alzef__qzolg
        ykav__cry = bodo.hiframes.series_kernels._mean_handle_nan(nej__zov,
            jae__kfrny)
        return ykav__cry
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        sff__dsjk = 0.0
        wiha__ytdk = 0.0
        jae__kfrny = 0
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
            tetm__zzcq = 0.0
            alzef__qzolg = 0
            if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh
                ) or not skipna:
                tetm__zzcq = arr[uxpcu__mhiyh]
                alzef__qzolg = 1
            sff__dsjk += tetm__zzcq
            wiha__ytdk += tetm__zzcq * tetm__zzcq
            jae__kfrny += alzef__qzolg
        ykav__cry = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            sff__dsjk, wiha__ytdk, jae__kfrny, ddof)
        return ykav__cry
    return impl


def array_op_std(arr, skipna=True, ddof=1):
    pass


@overload(array_op_std)
def overload_array_op_std(arr, skipna=True, ddof=1):
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr, skipna=True, ddof=1):
            return pd.Timedelta(types.int64(array_op_var(arr.view(np.int64),
                skipna, ddof) ** 0.5))
        return impl_dt64
    return lambda arr, skipna=True, ddof=1: array_op_var(arr, skipna, ddof
        ) ** 0.5


def array_op_quantile(arr, q):
    pass


@overload(array_op_quantile)
def overload_array_op_quantile(arr, q):
    if is_iterable_type(q):
        if arr.dtype == bodo.datetime64ns:

            def _impl_list_dt(arr, q):
                cbjbg__boe = np.empty(len(q), np.int64)
                for uxpcu__mhiyh in range(len(q)):
                    gabxm__lviff = np.float64(q[uxpcu__mhiyh])
                    cbjbg__boe[uxpcu__mhiyh
                        ] = bodo.libs.array_kernels.quantile(arr.view(np.
                        int64), gabxm__lviff)
                return cbjbg__boe.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            cbjbg__boe = np.empty(len(q), np.float64)
            for uxpcu__mhiyh in range(len(q)):
                gabxm__lviff = np.float64(q[uxpcu__mhiyh])
                cbjbg__boe[uxpcu__mhiyh] = bodo.libs.array_kernels.quantile(arr
                    , gabxm__lviff)
            return cbjbg__boe
        return impl_list
    if arr.dtype == bodo.datetime64ns:

        def _impl_dt(arr, q):
            return pd.Timestamp(bodo.libs.array_kernels.quantile(arr.view(
                np.int64), np.float64(q)))
        return _impl_dt

    def impl(arr, q):
        return bodo.libs.array_kernels.quantile(arr, np.float64(q))
    return impl


def array_op_sum(arr, skipna, min_count):
    pass


@overload(array_op_sum, no_unliteral=True)
def overload_array_op_sum(arr, skipna, min_count):
    if isinstance(arr.dtype, types.Integer):
        fdxzd__qbw = types.intp
    elif arr.dtype == types.bool_:
        fdxzd__qbw = np.int64
    else:
        fdxzd__qbw = arr.dtype
    vmaqf__asae = fdxzd__qbw(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            nej__zov = vmaqf__asae
            awto__bawhq = len(arr)
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(
                awto__bawhq):
                tetm__zzcq = vmaqf__asae
                alzef__qzolg = 0
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh
                    ) or not skipna:
                    tetm__zzcq = arr[uxpcu__mhiyh]
                    alzef__qzolg = 1
                nej__zov += tetm__zzcq
                jae__kfrny += alzef__qzolg
            ykav__cry = bodo.hiframes.series_kernels._var_handle_mincount(
                nej__zov, jae__kfrny, min_count)
            return ykav__cry
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            nej__zov = vmaqf__asae
            awto__bawhq = len(arr)
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(
                awto__bawhq):
                tetm__zzcq = vmaqf__asae
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                    tetm__zzcq = arr[uxpcu__mhiyh]
                nej__zov += tetm__zzcq
            return nej__zov
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    gdu__oxff = arr.dtype(1)
    if arr.dtype == types.bool_:
        gdu__oxff = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            nej__zov = gdu__oxff
            jae__kfrny = 0
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
                tetm__zzcq = gdu__oxff
                alzef__qzolg = 0
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh
                    ) or not skipna:
                    tetm__zzcq = arr[uxpcu__mhiyh]
                    alzef__qzolg = 1
                jae__kfrny += alzef__qzolg
                nej__zov *= tetm__zzcq
            ykav__cry = bodo.hiframes.series_kernels._var_handle_mincount(
                nej__zov, jae__kfrny, min_count)
            return ykav__cry
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            nej__zov = gdu__oxff
            for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(len(arr)):
                tetm__zzcq = gdu__oxff
                if not bodo.libs.array_kernels.isna(arr, uxpcu__mhiyh):
                    tetm__zzcq = arr[uxpcu__mhiyh]
                nej__zov *= tetm__zzcq
            return nej__zov
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        uxpcu__mhiyh = bodo.libs.array_kernels._nan_argmax(arr)
        return index[uxpcu__mhiyh]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        uxpcu__mhiyh = bodo.libs.array_kernels._nan_argmin(arr)
        return index[uxpcu__mhiyh]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            optx__vikf = {}
            for ixxk__ejg in values:
                optx__vikf[bodo.utils.conversion.box_if_dt64(ixxk__ejg)] = 0
            return optx__vikf
        return impl
    else:

        def impl(values, use_hash_impl):
            return values
        return impl


def array_op_isin(arr, values):
    pass


@overload(array_op_isin, inline='always')
def overload_array_op_isin(arr, values):
    use_hash_impl = element_type(values) == element_type(arr
        ) and is_hashable_type(element_type(values))

    def impl(arr, values):
        values = bodo.libs.array_ops._convert_isin_values(values, use_hash_impl
            )
        numba.parfors.parfor.init_prange()
        awto__bawhq = len(arr)
        cbjbg__boe = np.empty(awto__bawhq, np.bool_)
        for uxpcu__mhiyh in numba.parfors.parfor.internal_prange(awto__bawhq):
            cbjbg__boe[uxpcu__mhiyh] = bodo.utils.conversion.box_if_dt64(arr
                [uxpcu__mhiyh]) in values
        return cbjbg__boe
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    pldg__qcf = len(in_arr_tup) != 1
    jzxot__egv = list(in_arr_tup.types)
    afkvw__gmf = 'def impl(in_arr_tup):\n'
    afkvw__gmf += (
        "  ev = tracing.Event('array_unique_vector_map', is_parallel=False)\n")
    afkvw__gmf += '  n = len(in_arr_tup[0])\n'
    if pldg__qcf:
        infy__ibnjq = ', '.join([f'in_arr_tup[{uxpcu__mhiyh}][unused]' for
            uxpcu__mhiyh in range(len(in_arr_tup))])
        iyp__tnf = ', '.join(['False' for szg__gufg in range(len(in_arr_tup))])
        afkvw__gmf += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({infy__ibnjq},), ({iyp__tnf},)): 0 for unused in range(0)}}
"""
        afkvw__gmf += '  map_vector = np.empty(n, np.int64)\n'
        for uxpcu__mhiyh, sfrrj__kvq in enumerate(jzxot__egv):
            afkvw__gmf += f'  in_lst_{uxpcu__mhiyh} = []\n'
            if is_str_arr_type(sfrrj__kvq):
                afkvw__gmf += f'  total_len_{uxpcu__mhiyh} = 0\n'
            afkvw__gmf += f'  null_in_lst_{uxpcu__mhiyh} = []\n'
        afkvw__gmf += '  for i in range(n):\n'
        xhtk__nvbn = ', '.join([f'in_arr_tup[{uxpcu__mhiyh}][i]' for
            uxpcu__mhiyh in range(len(jzxot__egv))])
        ooksy__ndbkw = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{uxpcu__mhiyh}], i)' for
            uxpcu__mhiyh in range(len(jzxot__egv))])
        afkvw__gmf += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({xhtk__nvbn},), ({ooksy__ndbkw},))
"""
        afkvw__gmf += '    if data_val not in arr_map:\n'
        afkvw__gmf += '      set_val = len(arr_map)\n'
        afkvw__gmf += '      values_tup = data_val._data\n'
        afkvw__gmf += '      nulls_tup = data_val._null_values\n'
        for uxpcu__mhiyh, sfrrj__kvq in enumerate(jzxot__egv):
            afkvw__gmf += (
                f'      in_lst_{uxpcu__mhiyh}.append(values_tup[{uxpcu__mhiyh}])\n'
                )
            afkvw__gmf += (
                f'      null_in_lst_{uxpcu__mhiyh}.append(nulls_tup[{uxpcu__mhiyh}])\n'
                )
            if is_str_arr_type(sfrrj__kvq):
                afkvw__gmf += f"""      total_len_{uxpcu__mhiyh}  += nulls_tup[{uxpcu__mhiyh}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{uxpcu__mhiyh}], i)
"""
        afkvw__gmf += '      arr_map[data_val] = len(arr_map)\n'
        afkvw__gmf += '    else:\n'
        afkvw__gmf += '      set_val = arr_map[data_val]\n'
        afkvw__gmf += '    map_vector[i] = set_val\n'
        afkvw__gmf += '  n_rows = len(arr_map)\n'
        for uxpcu__mhiyh, sfrrj__kvq in enumerate(jzxot__egv):
            if is_str_arr_type(sfrrj__kvq):
                afkvw__gmf += f"""  out_arr_{uxpcu__mhiyh} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{uxpcu__mhiyh})
"""
            else:
                afkvw__gmf += f"""  out_arr_{uxpcu__mhiyh} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{uxpcu__mhiyh}], (-1,))
"""
        afkvw__gmf += '  for j in range(len(arr_map)):\n'
        for uxpcu__mhiyh in range(len(jzxot__egv)):
            afkvw__gmf += f'    if null_in_lst_{uxpcu__mhiyh}[j]:\n'
            afkvw__gmf += (
                f'      bodo.libs.array_kernels.setna(out_arr_{uxpcu__mhiyh}, j)\n'
                )
            afkvw__gmf += '    else:\n'
            afkvw__gmf += (
                f'      out_arr_{uxpcu__mhiyh}[j] = in_lst_{uxpcu__mhiyh}[j]\n'
                )
        mlpy__hbbfw = ', '.join([f'out_arr_{uxpcu__mhiyh}' for uxpcu__mhiyh in
            range(len(jzxot__egv))])
        afkvw__gmf += "  ev.add_attribute('n_map_entries', n_rows)\n"
        afkvw__gmf += '  ev.finalize()\n'
        afkvw__gmf += f'  return ({mlpy__hbbfw},), map_vector\n'
    else:
        afkvw__gmf += '  in_arr = in_arr_tup[0]\n'
        afkvw__gmf += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        afkvw__gmf += '  map_vector = np.empty(n, np.int64)\n'
        afkvw__gmf += '  is_na = 0\n'
        afkvw__gmf += '  in_lst = []\n'
        afkvw__gmf += '  na_idxs = []\n'
        if is_str_arr_type(jzxot__egv[0]):
            afkvw__gmf += '  total_len = 0\n'
        afkvw__gmf += '  for i in range(n):\n'
        afkvw__gmf += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        afkvw__gmf += '      is_na = 1\n'
        afkvw__gmf += '      # Always put NA in the last location.\n'
        afkvw__gmf += '      # We use -1 as a placeholder\n'
        afkvw__gmf += '      set_val = -1\n'
        afkvw__gmf += '      na_idxs.append(i)\n'
        afkvw__gmf += '    else:\n'
        afkvw__gmf += '      data_val = in_arr[i]\n'
        afkvw__gmf += '      if data_val not in arr_map:\n'
        afkvw__gmf += '        set_val = len(arr_map)\n'
        afkvw__gmf += '        in_lst.append(data_val)\n'
        if is_str_arr_type(jzxot__egv[0]):
            afkvw__gmf += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        afkvw__gmf += '        arr_map[data_val] = len(arr_map)\n'
        afkvw__gmf += '      else:\n'
        afkvw__gmf += '        set_val = arr_map[data_val]\n'
        afkvw__gmf += '    map_vector[i] = set_val\n'
        afkvw__gmf += '  map_vector[na_idxs] = len(arr_map)\n'
        afkvw__gmf += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(jzxot__egv[0]):
            afkvw__gmf += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            afkvw__gmf += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        afkvw__gmf += '  for j in range(len(arr_map)):\n'
        afkvw__gmf += '    out_arr[j] = in_lst[j]\n'
        afkvw__gmf += '  if is_na:\n'
        afkvw__gmf += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        afkvw__gmf += "  ev.add_attribute('n_map_entries', n_rows)\n"
        afkvw__gmf += '  ev.finalize()\n'
        afkvw__gmf += f'  return (out_arr,), map_vector\n'
    ewbi__gws = {}
    exec(afkvw__gmf, {'bodo': bodo, 'np': np, 'tracing': tracing}, ewbi__gws)
    impl = ewbi__gws['impl']
    return impl
