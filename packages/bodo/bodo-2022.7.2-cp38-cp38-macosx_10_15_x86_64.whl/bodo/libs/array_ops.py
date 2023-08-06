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
        hpo__uofzw = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        hpo__uofzw = False
    elif A == bodo.string_array_type:
        hpo__uofzw = ''
    elif A == bodo.binary_array_type:
        hpo__uofzw = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        wgtcz__xfelp = 0
        for ful__ckpno in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, ful__ckpno):
                if A[ful__ckpno] != hpo__uofzw:
                    wgtcz__xfelp += 1
        return wgtcz__xfelp != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        hpo__uofzw = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        hpo__uofzw = False
    elif A == bodo.string_array_type:
        hpo__uofzw = ''
    elif A == bodo.binary_array_type:
        hpo__uofzw = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        wgtcz__xfelp = 0
        for ful__ckpno in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, ful__ckpno):
                if A[ful__ckpno] == hpo__uofzw:
                    wgtcz__xfelp += 1
        return wgtcz__xfelp == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    wdrv__jeo = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(wdrv__jeo.ctypes, arr,
        parallel, skipna)
    return wdrv__jeo[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        cfx__mzwqr = len(arr)
        sre__ppi = np.empty(cfx__mzwqr, np.bool_)
        for ful__ckpno in numba.parfors.parfor.internal_prange(cfx__mzwqr):
            sre__ppi[ful__ckpno] = bodo.libs.array_kernels.isna(arr, ful__ckpno
                )
        return sre__ppi
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        wgtcz__xfelp = 0
        for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
            xzak__nzr = 0
            if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                xzak__nzr = 1
            wgtcz__xfelp += xzak__nzr
        wdrv__jeo = wgtcz__xfelp
        return wdrv__jeo
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    qoj__cfp = array_op_count(arr)
    amss__islom = array_op_min(arr)
    hziqv__ymox = array_op_max(arr)
    chnod__mxgg = array_op_mean(arr)
    dbg__pdysf = array_op_std(arr)
    rkjtj__tsuyk = array_op_quantile(arr, 0.25)
    bwj__ybzn = array_op_quantile(arr, 0.5)
    hqhqi__jsgld = array_op_quantile(arr, 0.75)
    return (qoj__cfp, chnod__mxgg, dbg__pdysf, amss__islom, rkjtj__tsuyk,
        bwj__ybzn, hqhqi__jsgld, hziqv__ymox)


def array_op_describe_dt_impl(arr):
    qoj__cfp = array_op_count(arr)
    amss__islom = array_op_min(arr)
    hziqv__ymox = array_op_max(arr)
    chnod__mxgg = array_op_mean(arr)
    rkjtj__tsuyk = array_op_quantile(arr, 0.25)
    bwj__ybzn = array_op_quantile(arr, 0.5)
    hqhqi__jsgld = array_op_quantile(arr, 0.75)
    return (qoj__cfp, chnod__mxgg, amss__islom, rkjtj__tsuyk, bwj__ybzn,
        hqhqi__jsgld, hziqv__ymox)


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
            mfqx__fpr = numba.cpython.builtins.get_type_max_value(np.int64)
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
                dqdup__wnof = mfqx__fpr
                xzak__nzr = 0
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                    dqdup__wnof = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[ful__ckpno]))
                    xzak__nzr = 1
                mfqx__fpr = min(mfqx__fpr, dqdup__wnof)
                wgtcz__xfelp += xzak__nzr
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(mfqx__fpr,
                wgtcz__xfelp)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = numba.cpython.builtins.get_type_max_value(np.int64)
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
                dqdup__wnof = mfqx__fpr
                xzak__nzr = 0
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                    dqdup__wnof = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[ful__ckpno]))
                    xzak__nzr = 1
                mfqx__fpr = min(mfqx__fpr, dqdup__wnof)
                wgtcz__xfelp += xzak__nzr
            return bodo.hiframes.pd_index_ext._dti_val_finalize(mfqx__fpr,
                wgtcz__xfelp)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            zym__nlugx = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            mfqx__fpr = numba.cpython.builtins.get_type_max_value(np.int64)
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(
                zym__nlugx)):
                aay__tujz = zym__nlugx[ful__ckpno]
                if aay__tujz == -1:
                    continue
                mfqx__fpr = min(mfqx__fpr, aay__tujz)
                wgtcz__xfelp += 1
            wdrv__jeo = bodo.hiframes.series_kernels._box_cat_val(mfqx__fpr,
                arr.dtype, wgtcz__xfelp)
            return wdrv__jeo
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = bodo.hiframes.series_kernels._get_date_max_value()
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
                dqdup__wnof = mfqx__fpr
                xzak__nzr = 0
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                    dqdup__wnof = arr[ful__ckpno]
                    xzak__nzr = 1
                mfqx__fpr = min(mfqx__fpr, dqdup__wnof)
                wgtcz__xfelp += xzak__nzr
            wdrv__jeo = bodo.hiframes.series_kernels._sum_handle_nan(mfqx__fpr,
                wgtcz__xfelp)
            return wdrv__jeo
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        mfqx__fpr = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype)
        wgtcz__xfelp = 0
        for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
            dqdup__wnof = mfqx__fpr
            xzak__nzr = 0
            if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                dqdup__wnof = arr[ful__ckpno]
                xzak__nzr = 1
            mfqx__fpr = min(mfqx__fpr, dqdup__wnof)
            wgtcz__xfelp += xzak__nzr
        wdrv__jeo = bodo.hiframes.series_kernels._sum_handle_nan(mfqx__fpr,
            wgtcz__xfelp)
        return wdrv__jeo
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = numba.cpython.builtins.get_type_min_value(np.int64)
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
                dqdup__wnof = mfqx__fpr
                xzak__nzr = 0
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                    dqdup__wnof = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[ful__ckpno]))
                    xzak__nzr = 1
                mfqx__fpr = max(mfqx__fpr, dqdup__wnof)
                wgtcz__xfelp += xzak__nzr
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(mfqx__fpr,
                wgtcz__xfelp)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = numba.cpython.builtins.get_type_min_value(np.int64)
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
                dqdup__wnof = mfqx__fpr
                xzak__nzr = 0
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                    dqdup__wnof = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[ful__ckpno]))
                    xzak__nzr = 1
                mfqx__fpr = max(mfqx__fpr, dqdup__wnof)
                wgtcz__xfelp += xzak__nzr
            return bodo.hiframes.pd_index_ext._dti_val_finalize(mfqx__fpr,
                wgtcz__xfelp)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            zym__nlugx = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            mfqx__fpr = -1
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(
                zym__nlugx)):
                mfqx__fpr = max(mfqx__fpr, zym__nlugx[ful__ckpno])
            wdrv__jeo = bodo.hiframes.series_kernels._box_cat_val(mfqx__fpr,
                arr.dtype, 1)
            return wdrv__jeo
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = bodo.hiframes.series_kernels._get_date_min_value()
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
                dqdup__wnof = mfqx__fpr
                xzak__nzr = 0
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                    dqdup__wnof = arr[ful__ckpno]
                    xzak__nzr = 1
                mfqx__fpr = max(mfqx__fpr, dqdup__wnof)
                wgtcz__xfelp += xzak__nzr
            wdrv__jeo = bodo.hiframes.series_kernels._sum_handle_nan(mfqx__fpr,
                wgtcz__xfelp)
            return wdrv__jeo
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        mfqx__fpr = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype)
        wgtcz__xfelp = 0
        for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
            dqdup__wnof = mfqx__fpr
            xzak__nzr = 0
            if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                dqdup__wnof = arr[ful__ckpno]
                xzak__nzr = 1
            mfqx__fpr = max(mfqx__fpr, dqdup__wnof)
            wgtcz__xfelp += xzak__nzr
        wdrv__jeo = bodo.hiframes.series_kernels._sum_handle_nan(mfqx__fpr,
            wgtcz__xfelp)
        return wdrv__jeo
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
    tqsio__jgd = types.float64
    esah__xqm = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        tqsio__jgd = types.float32
        esah__xqm = types.float32
    rgbxs__xrj = tqsio__jgd(0)
    pox__mqwl = esah__xqm(0)
    xgdd__hmjj = esah__xqm(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        mfqx__fpr = rgbxs__xrj
        wgtcz__xfelp = pox__mqwl
        for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
            dqdup__wnof = rgbxs__xrj
            xzak__nzr = pox__mqwl
            if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                dqdup__wnof = arr[ful__ckpno]
                xzak__nzr = xgdd__hmjj
            mfqx__fpr += dqdup__wnof
            wgtcz__xfelp += xzak__nzr
        wdrv__jeo = bodo.hiframes.series_kernels._mean_handle_nan(mfqx__fpr,
            wgtcz__xfelp)
        return wdrv__jeo
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        bfq__vmha = 0.0
        vsbpa__onl = 0.0
        wgtcz__xfelp = 0
        for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
            dqdup__wnof = 0.0
            xzak__nzr = 0
            if not bodo.libs.array_kernels.isna(arr, ful__ckpno) or not skipna:
                dqdup__wnof = arr[ful__ckpno]
                xzak__nzr = 1
            bfq__vmha += dqdup__wnof
            vsbpa__onl += dqdup__wnof * dqdup__wnof
            wgtcz__xfelp += xzak__nzr
        wdrv__jeo = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            bfq__vmha, vsbpa__onl, wgtcz__xfelp, ddof)
        return wdrv__jeo
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
                sre__ppi = np.empty(len(q), np.int64)
                for ful__ckpno in range(len(q)):
                    hzf__wlm = np.float64(q[ful__ckpno])
                    sre__ppi[ful__ckpno] = bodo.libs.array_kernels.quantile(arr
                        .view(np.int64), hzf__wlm)
                return sre__ppi.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            sre__ppi = np.empty(len(q), np.float64)
            for ful__ckpno in range(len(q)):
                hzf__wlm = np.float64(q[ful__ckpno])
                sre__ppi[ful__ckpno] = bodo.libs.array_kernels.quantile(arr,
                    hzf__wlm)
            return sre__ppi
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
        zng__jlk = types.intp
    elif arr.dtype == types.bool_:
        zng__jlk = np.int64
    else:
        zng__jlk = arr.dtype
    kwz__xgqqn = zng__jlk(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = kwz__xgqqn
            cfx__mzwqr = len(arr)
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(cfx__mzwqr):
                dqdup__wnof = kwz__xgqqn
                xzak__nzr = 0
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno
                    ) or not skipna:
                    dqdup__wnof = arr[ful__ckpno]
                    xzak__nzr = 1
                mfqx__fpr += dqdup__wnof
                wgtcz__xfelp += xzak__nzr
            wdrv__jeo = bodo.hiframes.series_kernels._var_handle_mincount(
                mfqx__fpr, wgtcz__xfelp, min_count)
            return wdrv__jeo
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = kwz__xgqqn
            cfx__mzwqr = len(arr)
            for ful__ckpno in numba.parfors.parfor.internal_prange(cfx__mzwqr):
                dqdup__wnof = kwz__xgqqn
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                    dqdup__wnof = arr[ful__ckpno]
                mfqx__fpr += dqdup__wnof
            return mfqx__fpr
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    iri__okh = arr.dtype(1)
    if arr.dtype == types.bool_:
        iri__okh = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = iri__okh
            wgtcz__xfelp = 0
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
                dqdup__wnof = iri__okh
                xzak__nzr = 0
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno
                    ) or not skipna:
                    dqdup__wnof = arr[ful__ckpno]
                    xzak__nzr = 1
                wgtcz__xfelp += xzak__nzr
                mfqx__fpr *= dqdup__wnof
            wdrv__jeo = bodo.hiframes.series_kernels._var_handle_mincount(
                mfqx__fpr, wgtcz__xfelp, min_count)
            return wdrv__jeo
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            mfqx__fpr = iri__okh
            for ful__ckpno in numba.parfors.parfor.internal_prange(len(arr)):
                dqdup__wnof = iri__okh
                if not bodo.libs.array_kernels.isna(arr, ful__ckpno):
                    dqdup__wnof = arr[ful__ckpno]
                mfqx__fpr *= dqdup__wnof
            return mfqx__fpr
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        ful__ckpno = bodo.libs.array_kernels._nan_argmax(arr)
        return index[ful__ckpno]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        ful__ckpno = bodo.libs.array_kernels._nan_argmin(arr)
        return index[ful__ckpno]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            hhs__hjuk = {}
            for mcshu__avfn in values:
                hhs__hjuk[bodo.utils.conversion.box_if_dt64(mcshu__avfn)] = 0
            return hhs__hjuk
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
        cfx__mzwqr = len(arr)
        sre__ppi = np.empty(cfx__mzwqr, np.bool_)
        for ful__ckpno in numba.parfors.parfor.internal_prange(cfx__mzwqr):
            sre__ppi[ful__ckpno] = bodo.utils.conversion.box_if_dt64(arr[
                ful__ckpno]) in values
        return sre__ppi
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    fnjr__atc = len(in_arr_tup) != 1
    reok__ibir = list(in_arr_tup.types)
    ckb__ylq = 'def impl(in_arr_tup):\n'
    ckb__ylq += (
        "  ev = tracing.Event('array_unique_vector_map', is_parallel=False)\n")
    ckb__ylq += '  n = len(in_arr_tup[0])\n'
    if fnjr__atc:
        bwp__kgsy = ', '.join([f'in_arr_tup[{ful__ckpno}][unused]' for
            ful__ckpno in range(len(in_arr_tup))])
        vfklk__bbsdf = ', '.join(['False' for tppfq__xyd in range(len(
            in_arr_tup))])
        ckb__ylq += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({bwp__kgsy},), ({vfklk__bbsdf},)): 0 for unused in range(0)}}
"""
        ckb__ylq += '  map_vector = np.empty(n, np.int64)\n'
        for ful__ckpno, udiso__hgfe in enumerate(reok__ibir):
            ckb__ylq += f'  in_lst_{ful__ckpno} = []\n'
            if is_str_arr_type(udiso__hgfe):
                ckb__ylq += f'  total_len_{ful__ckpno} = 0\n'
            ckb__ylq += f'  null_in_lst_{ful__ckpno} = []\n'
        ckb__ylq += '  for i in range(n):\n'
        jae__qkwlk = ', '.join([f'in_arr_tup[{ful__ckpno}][i]' for
            ful__ckpno in range(len(reok__ibir))])
        fgu__opif = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{ful__ckpno}], i)' for
            ful__ckpno in range(len(reok__ibir))])
        ckb__ylq += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({jae__qkwlk},), ({fgu__opif},))
"""
        ckb__ylq += '    if data_val not in arr_map:\n'
        ckb__ylq += '      set_val = len(arr_map)\n'
        ckb__ylq += '      values_tup = data_val._data\n'
        ckb__ylq += '      nulls_tup = data_val._null_values\n'
        for ful__ckpno, udiso__hgfe in enumerate(reok__ibir):
            ckb__ylq += (
                f'      in_lst_{ful__ckpno}.append(values_tup[{ful__ckpno}])\n'
                )
            ckb__ylq += (
                f'      null_in_lst_{ful__ckpno}.append(nulls_tup[{ful__ckpno}])\n'
                )
            if is_str_arr_type(udiso__hgfe):
                ckb__ylq += f"""      total_len_{ful__ckpno}  += nulls_tup[{ful__ckpno}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{ful__ckpno}], i)
"""
        ckb__ylq += '      arr_map[data_val] = len(arr_map)\n'
        ckb__ylq += '    else:\n'
        ckb__ylq += '      set_val = arr_map[data_val]\n'
        ckb__ylq += '    map_vector[i] = set_val\n'
        ckb__ylq += '  n_rows = len(arr_map)\n'
        for ful__ckpno, udiso__hgfe in enumerate(reok__ibir):
            if is_str_arr_type(udiso__hgfe):
                ckb__ylq += f"""  out_arr_{ful__ckpno} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{ful__ckpno})
"""
            else:
                ckb__ylq += f"""  out_arr_{ful__ckpno} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{ful__ckpno}], (-1,))
"""
        ckb__ylq += '  for j in range(len(arr_map)):\n'
        for ful__ckpno in range(len(reok__ibir)):
            ckb__ylq += f'    if null_in_lst_{ful__ckpno}[j]:\n'
            ckb__ylq += (
                f'      bodo.libs.array_kernels.setna(out_arr_{ful__ckpno}, j)\n'
                )
            ckb__ylq += '    else:\n'
            ckb__ylq += (
                f'      out_arr_{ful__ckpno}[j] = in_lst_{ful__ckpno}[j]\n')
        nhhpb__ypca = ', '.join([f'out_arr_{ful__ckpno}' for ful__ckpno in
            range(len(reok__ibir))])
        ckb__ylq += "  ev.add_attribute('n_map_entries', n_rows)\n"
        ckb__ylq += '  ev.finalize()\n'
        ckb__ylq += f'  return ({nhhpb__ypca},), map_vector\n'
    else:
        ckb__ylq += '  in_arr = in_arr_tup[0]\n'
        ckb__ylq += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        ckb__ylq += '  map_vector = np.empty(n, np.int64)\n'
        ckb__ylq += '  is_na = 0\n'
        ckb__ylq += '  in_lst = []\n'
        ckb__ylq += '  na_idxs = []\n'
        if is_str_arr_type(reok__ibir[0]):
            ckb__ylq += '  total_len = 0\n'
        ckb__ylq += '  for i in range(n):\n'
        ckb__ylq += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        ckb__ylq += '      is_na = 1\n'
        ckb__ylq += '      # Always put NA in the last location.\n'
        ckb__ylq += '      # We use -1 as a placeholder\n'
        ckb__ylq += '      set_val = -1\n'
        ckb__ylq += '      na_idxs.append(i)\n'
        ckb__ylq += '    else:\n'
        ckb__ylq += '      data_val = in_arr[i]\n'
        ckb__ylq += '      if data_val not in arr_map:\n'
        ckb__ylq += '        set_val = len(arr_map)\n'
        ckb__ylq += '        in_lst.append(data_val)\n'
        if is_str_arr_type(reok__ibir[0]):
            ckb__ylq += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        ckb__ylq += '        arr_map[data_val] = len(arr_map)\n'
        ckb__ylq += '      else:\n'
        ckb__ylq += '        set_val = arr_map[data_val]\n'
        ckb__ylq += '    map_vector[i] = set_val\n'
        ckb__ylq += '  map_vector[na_idxs] = len(arr_map)\n'
        ckb__ylq += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(reok__ibir[0]):
            ckb__ylq += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            ckb__ylq += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        ckb__ylq += '  for j in range(len(arr_map)):\n'
        ckb__ylq += '    out_arr[j] = in_lst[j]\n'
        ckb__ylq += '  if is_na:\n'
        ckb__ylq += '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n'
        ckb__ylq += "  ev.add_attribute('n_map_entries', n_rows)\n"
        ckb__ylq += '  ev.finalize()\n'
        ckb__ylq += f'  return (out_arr,), map_vector\n'
    skmz__bjv = {}
    exec(ckb__ylq, {'bodo': bodo, 'np': np, 'tracing': tracing}, skmz__bjv)
    impl = skmz__bjv['impl']
    return impl
