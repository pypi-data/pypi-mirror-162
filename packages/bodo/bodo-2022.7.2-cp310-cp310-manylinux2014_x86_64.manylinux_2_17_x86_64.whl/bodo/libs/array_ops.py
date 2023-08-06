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
        iwk__dtzc = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        iwk__dtzc = False
    elif A == bodo.string_array_type:
        iwk__dtzc = ''
    elif A == bodo.binary_array_type:
        iwk__dtzc = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        fnu__eqwh = 0
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, xtxzk__kdx):
                if A[xtxzk__kdx] != iwk__dtzc:
                    fnu__eqwh += 1
        return fnu__eqwh != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        iwk__dtzc = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        iwk__dtzc = False
    elif A == bodo.string_array_type:
        iwk__dtzc = ''
    elif A == bodo.binary_array_type:
        iwk__dtzc = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        fnu__eqwh = 0
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, xtxzk__kdx):
                if A[xtxzk__kdx] == iwk__dtzc:
                    fnu__eqwh += 1
        return fnu__eqwh == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    hafyd__ebdq = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(hafyd__ebdq.ctypes,
        arr, parallel, skipna)
    return hafyd__ebdq[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        srp__zddhl = len(arr)
        gon__wac = np.empty(srp__zddhl, np.bool_)
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(srp__zddhl):
            gon__wac[xtxzk__kdx] = bodo.libs.array_kernels.isna(arr, xtxzk__kdx
                )
        return gon__wac
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        fnu__eqwh = 0
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
            ext__iwr = 0
            if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                ext__iwr = 1
            fnu__eqwh += ext__iwr
        hafyd__ebdq = fnu__eqwh
        return hafyd__ebdq
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    iokoe__ysfg = array_op_count(arr)
    dyaqm__odp = array_op_min(arr)
    rfv__ebvi = array_op_max(arr)
    ualw__ouxz = array_op_mean(arr)
    jbrlk__xyvi = array_op_std(arr)
    hvle__txa = array_op_quantile(arr, 0.25)
    aghki__fzenj = array_op_quantile(arr, 0.5)
    jbt__pxu = array_op_quantile(arr, 0.75)
    return (iokoe__ysfg, ualw__ouxz, jbrlk__xyvi, dyaqm__odp, hvle__txa,
        aghki__fzenj, jbt__pxu, rfv__ebvi)


def array_op_describe_dt_impl(arr):
    iokoe__ysfg = array_op_count(arr)
    dyaqm__odp = array_op_min(arr)
    rfv__ebvi = array_op_max(arr)
    ualw__ouxz = array_op_mean(arr)
    hvle__txa = array_op_quantile(arr, 0.25)
    aghki__fzenj = array_op_quantile(arr, 0.5)
    jbt__pxu = array_op_quantile(arr, 0.75)
    return (iokoe__ysfg, ualw__ouxz, dyaqm__odp, hvle__txa, aghki__fzenj,
        jbt__pxu, rfv__ebvi)


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
            wgxh__jykir = numba.cpython.builtins.get_type_max_value(np.int64)
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
                gwo__uja = wgxh__jykir
                ext__iwr = 0
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                    gwo__uja = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[xtxzk__kdx]))
                    ext__iwr = 1
                wgxh__jykir = min(wgxh__jykir, gwo__uja)
                fnu__eqwh += ext__iwr
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(wgxh__jykir,
                fnu__eqwh)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = numba.cpython.builtins.get_type_max_value(np.int64)
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
                gwo__uja = wgxh__jykir
                ext__iwr = 0
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                    gwo__uja = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[xtxzk__kdx])
                    ext__iwr = 1
                wgxh__jykir = min(wgxh__jykir, gwo__uja)
                fnu__eqwh += ext__iwr
            return bodo.hiframes.pd_index_ext._dti_val_finalize(wgxh__jykir,
                fnu__eqwh)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            vsqkt__wndlk = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            wgxh__jykir = numba.cpython.builtins.get_type_max_value(np.int64)
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(
                vsqkt__wndlk)):
                yix__ticv = vsqkt__wndlk[xtxzk__kdx]
                if yix__ticv == -1:
                    continue
                wgxh__jykir = min(wgxh__jykir, yix__ticv)
                fnu__eqwh += 1
            hafyd__ebdq = bodo.hiframes.series_kernels._box_cat_val(wgxh__jykir
                , arr.dtype, fnu__eqwh)
            return hafyd__ebdq
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = bodo.hiframes.series_kernels._get_date_max_value()
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
                gwo__uja = wgxh__jykir
                ext__iwr = 0
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                    gwo__uja = arr[xtxzk__kdx]
                    ext__iwr = 1
                wgxh__jykir = min(wgxh__jykir, gwo__uja)
                fnu__eqwh += ext__iwr
            hafyd__ebdq = bodo.hiframes.series_kernels._sum_handle_nan(
                wgxh__jykir, fnu__eqwh)
            return hafyd__ebdq
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        wgxh__jykir = bodo.hiframes.series_kernels._get_type_max_value(arr.
            dtype)
        fnu__eqwh = 0
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
            gwo__uja = wgxh__jykir
            ext__iwr = 0
            if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                gwo__uja = arr[xtxzk__kdx]
                ext__iwr = 1
            wgxh__jykir = min(wgxh__jykir, gwo__uja)
            fnu__eqwh += ext__iwr
        hafyd__ebdq = bodo.hiframes.series_kernels._sum_handle_nan(wgxh__jykir,
            fnu__eqwh)
        return hafyd__ebdq
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = numba.cpython.builtins.get_type_min_value(np.int64)
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
                gwo__uja = wgxh__jykir
                ext__iwr = 0
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                    gwo__uja = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[xtxzk__kdx]))
                    ext__iwr = 1
                wgxh__jykir = max(wgxh__jykir, gwo__uja)
                fnu__eqwh += ext__iwr
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(wgxh__jykir,
                fnu__eqwh)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = numba.cpython.builtins.get_type_min_value(np.int64)
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
                gwo__uja = wgxh__jykir
                ext__iwr = 0
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                    gwo__uja = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[xtxzk__kdx])
                    ext__iwr = 1
                wgxh__jykir = max(wgxh__jykir, gwo__uja)
                fnu__eqwh += ext__iwr
            return bodo.hiframes.pd_index_ext._dti_val_finalize(wgxh__jykir,
                fnu__eqwh)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            vsqkt__wndlk = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            wgxh__jykir = -1
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(
                vsqkt__wndlk)):
                wgxh__jykir = max(wgxh__jykir, vsqkt__wndlk[xtxzk__kdx])
            hafyd__ebdq = bodo.hiframes.series_kernels._box_cat_val(wgxh__jykir
                , arr.dtype, 1)
            return hafyd__ebdq
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = bodo.hiframes.series_kernels._get_date_min_value()
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
                gwo__uja = wgxh__jykir
                ext__iwr = 0
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                    gwo__uja = arr[xtxzk__kdx]
                    ext__iwr = 1
                wgxh__jykir = max(wgxh__jykir, gwo__uja)
                fnu__eqwh += ext__iwr
            hafyd__ebdq = bodo.hiframes.series_kernels._sum_handle_nan(
                wgxh__jykir, fnu__eqwh)
            return hafyd__ebdq
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        wgxh__jykir = bodo.hiframes.series_kernels._get_type_min_value(arr.
            dtype)
        fnu__eqwh = 0
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
            gwo__uja = wgxh__jykir
            ext__iwr = 0
            if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                gwo__uja = arr[xtxzk__kdx]
                ext__iwr = 1
            wgxh__jykir = max(wgxh__jykir, gwo__uja)
            fnu__eqwh += ext__iwr
        hafyd__ebdq = bodo.hiframes.series_kernels._sum_handle_nan(wgxh__jykir,
            fnu__eqwh)
        return hafyd__ebdq
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
    vhlfl__vnya = types.float64
    poyu__qhz = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        vhlfl__vnya = types.float32
        poyu__qhz = types.float32
    mzdb__tyq = vhlfl__vnya(0)
    oio__htyw = poyu__qhz(0)
    bsnk__yfqo = poyu__qhz(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        wgxh__jykir = mzdb__tyq
        fnu__eqwh = oio__htyw
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
            gwo__uja = mzdb__tyq
            ext__iwr = oio__htyw
            if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                gwo__uja = arr[xtxzk__kdx]
                ext__iwr = bsnk__yfqo
            wgxh__jykir += gwo__uja
            fnu__eqwh += ext__iwr
        hafyd__ebdq = bodo.hiframes.series_kernels._mean_handle_nan(wgxh__jykir
            , fnu__eqwh)
        return hafyd__ebdq
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        loq__krwry = 0.0
        hee__ewg = 0.0
        fnu__eqwh = 0
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
            gwo__uja = 0.0
            ext__iwr = 0
            if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx) or not skipna:
                gwo__uja = arr[xtxzk__kdx]
                ext__iwr = 1
            loq__krwry += gwo__uja
            hee__ewg += gwo__uja * gwo__uja
            fnu__eqwh += ext__iwr
        hafyd__ebdq = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            loq__krwry, hee__ewg, fnu__eqwh, ddof)
        return hafyd__ebdq
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
                gon__wac = np.empty(len(q), np.int64)
                for xtxzk__kdx in range(len(q)):
                    hdequ__blgp = np.float64(q[xtxzk__kdx])
                    gon__wac[xtxzk__kdx] = bodo.libs.array_kernels.quantile(arr
                        .view(np.int64), hdequ__blgp)
                return gon__wac.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            gon__wac = np.empty(len(q), np.float64)
            for xtxzk__kdx in range(len(q)):
                hdequ__blgp = np.float64(q[xtxzk__kdx])
                gon__wac[xtxzk__kdx] = bodo.libs.array_kernels.quantile(arr,
                    hdequ__blgp)
            return gon__wac
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
        smgr__wtkzm = types.intp
    elif arr.dtype == types.bool_:
        smgr__wtkzm = np.int64
    else:
        smgr__wtkzm = arr.dtype
    sje__tyag = smgr__wtkzm(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = sje__tyag
            srp__zddhl = len(arr)
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(srp__zddhl):
                gwo__uja = sje__tyag
                ext__iwr = 0
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx
                    ) or not skipna:
                    gwo__uja = arr[xtxzk__kdx]
                    ext__iwr = 1
                wgxh__jykir += gwo__uja
                fnu__eqwh += ext__iwr
            hafyd__ebdq = bodo.hiframes.series_kernels._var_handle_mincount(
                wgxh__jykir, fnu__eqwh, min_count)
            return hafyd__ebdq
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = sje__tyag
            srp__zddhl = len(arr)
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(srp__zddhl):
                gwo__uja = sje__tyag
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                    gwo__uja = arr[xtxzk__kdx]
                wgxh__jykir += gwo__uja
            return wgxh__jykir
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    ujcqn__qrkdz = arr.dtype(1)
    if arr.dtype == types.bool_:
        ujcqn__qrkdz = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = ujcqn__qrkdz
            fnu__eqwh = 0
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
                gwo__uja = ujcqn__qrkdz
                ext__iwr = 0
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx
                    ) or not skipna:
                    gwo__uja = arr[xtxzk__kdx]
                    ext__iwr = 1
                fnu__eqwh += ext__iwr
                wgxh__jykir *= gwo__uja
            hafyd__ebdq = bodo.hiframes.series_kernels._var_handle_mincount(
                wgxh__jykir, fnu__eqwh, min_count)
            return hafyd__ebdq
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            wgxh__jykir = ujcqn__qrkdz
            for xtxzk__kdx in numba.parfors.parfor.internal_prange(len(arr)):
                gwo__uja = ujcqn__qrkdz
                if not bodo.libs.array_kernels.isna(arr, xtxzk__kdx):
                    gwo__uja = arr[xtxzk__kdx]
                wgxh__jykir *= gwo__uja
            return wgxh__jykir
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        xtxzk__kdx = bodo.libs.array_kernels._nan_argmax(arr)
        return index[xtxzk__kdx]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        xtxzk__kdx = bodo.libs.array_kernels._nan_argmin(arr)
        return index[xtxzk__kdx]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            gbg__qcqx = {}
            for iin__rgeyr in values:
                gbg__qcqx[bodo.utils.conversion.box_if_dt64(iin__rgeyr)] = 0
            return gbg__qcqx
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
        srp__zddhl = len(arr)
        gon__wac = np.empty(srp__zddhl, np.bool_)
        for xtxzk__kdx in numba.parfors.parfor.internal_prange(srp__zddhl):
            gon__wac[xtxzk__kdx] = bodo.utils.conversion.box_if_dt64(arr[
                xtxzk__kdx]) in values
        return gon__wac
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    blntu__dcyyd = len(in_arr_tup) != 1
    ucx__eiith = list(in_arr_tup.types)
    iczry__bsoc = 'def impl(in_arr_tup):\n'
    iczry__bsoc += (
        "  ev = tracing.Event('array_unique_vector_map', is_parallel=False)\n")
    iczry__bsoc += '  n = len(in_arr_tup[0])\n'
    if blntu__dcyyd:
        ieywz__duxq = ', '.join([f'in_arr_tup[{xtxzk__kdx}][unused]' for
            xtxzk__kdx in range(len(in_arr_tup))])
        idt__rio = ', '.join(['False' for mpdvj__ycwt in range(len(
            in_arr_tup))])
        iczry__bsoc += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({ieywz__duxq},), ({idt__rio},)): 0 for unused in range(0)}}
"""
        iczry__bsoc += '  map_vector = np.empty(n, np.int64)\n'
        for xtxzk__kdx, fvnea__mvn in enumerate(ucx__eiith):
            iczry__bsoc += f'  in_lst_{xtxzk__kdx} = []\n'
            if is_str_arr_type(fvnea__mvn):
                iczry__bsoc += f'  total_len_{xtxzk__kdx} = 0\n'
            iczry__bsoc += f'  null_in_lst_{xtxzk__kdx} = []\n'
        iczry__bsoc += '  for i in range(n):\n'
        pwnb__tsrf = ', '.join([f'in_arr_tup[{xtxzk__kdx}][i]' for
            xtxzk__kdx in range(len(ucx__eiith))])
        oyeh__osg = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{xtxzk__kdx}], i)' for
            xtxzk__kdx in range(len(ucx__eiith))])
        iczry__bsoc += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({pwnb__tsrf},), ({oyeh__osg},))
"""
        iczry__bsoc += '    if data_val not in arr_map:\n'
        iczry__bsoc += '      set_val = len(arr_map)\n'
        iczry__bsoc += '      values_tup = data_val._data\n'
        iczry__bsoc += '      nulls_tup = data_val._null_values\n'
        for xtxzk__kdx, fvnea__mvn in enumerate(ucx__eiith):
            iczry__bsoc += (
                f'      in_lst_{xtxzk__kdx}.append(values_tup[{xtxzk__kdx}])\n'
                )
            iczry__bsoc += (
                f'      null_in_lst_{xtxzk__kdx}.append(nulls_tup[{xtxzk__kdx}])\n'
                )
            if is_str_arr_type(fvnea__mvn):
                iczry__bsoc += f"""      total_len_{xtxzk__kdx}  += nulls_tup[{xtxzk__kdx}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{xtxzk__kdx}], i)
"""
        iczry__bsoc += '      arr_map[data_val] = len(arr_map)\n'
        iczry__bsoc += '    else:\n'
        iczry__bsoc += '      set_val = arr_map[data_val]\n'
        iczry__bsoc += '    map_vector[i] = set_val\n'
        iczry__bsoc += '  n_rows = len(arr_map)\n'
        for xtxzk__kdx, fvnea__mvn in enumerate(ucx__eiith):
            if is_str_arr_type(fvnea__mvn):
                iczry__bsoc += f"""  out_arr_{xtxzk__kdx} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{xtxzk__kdx})
"""
            else:
                iczry__bsoc += f"""  out_arr_{xtxzk__kdx} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{xtxzk__kdx}], (-1,))
"""
        iczry__bsoc += '  for j in range(len(arr_map)):\n'
        for xtxzk__kdx in range(len(ucx__eiith)):
            iczry__bsoc += f'    if null_in_lst_{xtxzk__kdx}[j]:\n'
            iczry__bsoc += (
                f'      bodo.libs.array_kernels.setna(out_arr_{xtxzk__kdx}, j)\n'
                )
            iczry__bsoc += '    else:\n'
            iczry__bsoc += (
                f'      out_arr_{xtxzk__kdx}[j] = in_lst_{xtxzk__kdx}[j]\n')
        dhdz__iyhjh = ', '.join([f'out_arr_{xtxzk__kdx}' for xtxzk__kdx in
            range(len(ucx__eiith))])
        iczry__bsoc += "  ev.add_attribute('n_map_entries', n_rows)\n"
        iczry__bsoc += '  ev.finalize()\n'
        iczry__bsoc += f'  return ({dhdz__iyhjh},), map_vector\n'
    else:
        iczry__bsoc += '  in_arr = in_arr_tup[0]\n'
        iczry__bsoc += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        iczry__bsoc += '  map_vector = np.empty(n, np.int64)\n'
        iczry__bsoc += '  is_na = 0\n'
        iczry__bsoc += '  in_lst = []\n'
        iczry__bsoc += '  na_idxs = []\n'
        if is_str_arr_type(ucx__eiith[0]):
            iczry__bsoc += '  total_len = 0\n'
        iczry__bsoc += '  for i in range(n):\n'
        iczry__bsoc += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        iczry__bsoc += '      is_na = 1\n'
        iczry__bsoc += '      # Always put NA in the last location.\n'
        iczry__bsoc += '      # We use -1 as a placeholder\n'
        iczry__bsoc += '      set_val = -1\n'
        iczry__bsoc += '      na_idxs.append(i)\n'
        iczry__bsoc += '    else:\n'
        iczry__bsoc += '      data_val = in_arr[i]\n'
        iczry__bsoc += '      if data_val not in arr_map:\n'
        iczry__bsoc += '        set_val = len(arr_map)\n'
        iczry__bsoc += '        in_lst.append(data_val)\n'
        if is_str_arr_type(ucx__eiith[0]):
            iczry__bsoc += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        iczry__bsoc += '        arr_map[data_val] = len(arr_map)\n'
        iczry__bsoc += '      else:\n'
        iczry__bsoc += '        set_val = arr_map[data_val]\n'
        iczry__bsoc += '    map_vector[i] = set_val\n'
        iczry__bsoc += '  map_vector[na_idxs] = len(arr_map)\n'
        iczry__bsoc += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(ucx__eiith[0]):
            iczry__bsoc += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            iczry__bsoc += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        iczry__bsoc += '  for j in range(len(arr_map)):\n'
        iczry__bsoc += '    out_arr[j] = in_lst[j]\n'
        iczry__bsoc += '  if is_na:\n'
        iczry__bsoc += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        iczry__bsoc += "  ev.add_attribute('n_map_entries', n_rows)\n"
        iczry__bsoc += '  ev.finalize()\n'
        iczry__bsoc += f'  return (out_arr,), map_vector\n'
    adv__nkyi = {}
    exec(iczry__bsoc, {'bodo': bodo, 'np': np, 'tracing': tracing}, adv__nkyi)
    impl = adv__nkyi['impl']
    return impl
