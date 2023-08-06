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
        fpeeb__hlbg = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        fpeeb__hlbg = False
    elif A == bodo.string_array_type:
        fpeeb__hlbg = ''
    elif A == bodo.binary_array_type:
        fpeeb__hlbg = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        xxsea__zer = 0
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, vgncy__yjhwd):
                if A[vgncy__yjhwd] != fpeeb__hlbg:
                    xxsea__zer += 1
        return xxsea__zer != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        fpeeb__hlbg = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        fpeeb__hlbg = False
    elif A == bodo.string_array_type:
        fpeeb__hlbg = ''
    elif A == bodo.binary_array_type:
        fpeeb__hlbg = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        xxsea__zer = 0
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, vgncy__yjhwd):
                if A[vgncy__yjhwd] == fpeeb__hlbg:
                    xxsea__zer += 1
        return xxsea__zer == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    xmhm__dxst = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(xmhm__dxst.ctypes,
        arr, parallel, skipna)
    return xmhm__dxst[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        bffm__ghkco = len(arr)
        jypvh__uilp = np.empty(bffm__ghkco, np.bool_)
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(bffm__ghkco):
            jypvh__uilp[vgncy__yjhwd] = bodo.libs.array_kernels.isna(arr,
                vgncy__yjhwd)
        return jypvh__uilp
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xxsea__zer = 0
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
            gjbo__nysz = 0
            if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                gjbo__nysz = 1
            xxsea__zer += gjbo__nysz
        xmhm__dxst = xxsea__zer
        return xmhm__dxst
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    hezw__goue = array_op_count(arr)
    cocxe__vinz = array_op_min(arr)
    aylj__kcih = array_op_max(arr)
    egscc__hagca = array_op_mean(arr)
    fzzgo__spl = array_op_std(arr)
    fuan__jree = array_op_quantile(arr, 0.25)
    lje__eifqs = array_op_quantile(arr, 0.5)
    qci__mxdtk = array_op_quantile(arr, 0.75)
    return (hezw__goue, egscc__hagca, fzzgo__spl, cocxe__vinz, fuan__jree,
        lje__eifqs, qci__mxdtk, aylj__kcih)


def array_op_describe_dt_impl(arr):
    hezw__goue = array_op_count(arr)
    cocxe__vinz = array_op_min(arr)
    aylj__kcih = array_op_max(arr)
    egscc__hagca = array_op_mean(arr)
    fuan__jree = array_op_quantile(arr, 0.25)
    lje__eifqs = array_op_quantile(arr, 0.5)
    qci__mxdtk = array_op_quantile(arr, 0.75)
    return (hezw__goue, egscc__hagca, cocxe__vinz, fuan__jree, lje__eifqs,
        qci__mxdtk, aylj__kcih)


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
            yijd__vllt = numba.cpython.builtins.get_type_max_value(np.int64)
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
                uhx__ipgu = yijd__vllt
                gjbo__nysz = 0
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                    uhx__ipgu = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[vgncy__yjhwd]))
                    gjbo__nysz = 1
                yijd__vllt = min(yijd__vllt, uhx__ipgu)
                xxsea__zer += gjbo__nysz
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(yijd__vllt,
                xxsea__zer)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            yijd__vllt = numba.cpython.builtins.get_type_max_value(np.int64)
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
                uhx__ipgu = yijd__vllt
                gjbo__nysz = 0
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                    uhx__ipgu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[vgncy__yjhwd])
                    gjbo__nysz = 1
                yijd__vllt = min(yijd__vllt, uhx__ipgu)
                xxsea__zer += gjbo__nysz
            return bodo.hiframes.pd_index_ext._dti_val_finalize(yijd__vllt,
                xxsea__zer)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            xhzbz__quqj = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            yijd__vllt = numba.cpython.builtins.get_type_max_value(np.int64)
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(
                xhzbz__quqj)):
                drxnc__ajxd = xhzbz__quqj[vgncy__yjhwd]
                if drxnc__ajxd == -1:
                    continue
                yijd__vllt = min(yijd__vllt, drxnc__ajxd)
                xxsea__zer += 1
            xmhm__dxst = bodo.hiframes.series_kernels._box_cat_val(yijd__vllt,
                arr.dtype, xxsea__zer)
            return xmhm__dxst
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            yijd__vllt = bodo.hiframes.series_kernels._get_date_max_value()
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
                uhx__ipgu = yijd__vllt
                gjbo__nysz = 0
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                    uhx__ipgu = arr[vgncy__yjhwd]
                    gjbo__nysz = 1
                yijd__vllt = min(yijd__vllt, uhx__ipgu)
                xxsea__zer += gjbo__nysz
            xmhm__dxst = bodo.hiframes.series_kernels._sum_handle_nan(
                yijd__vllt, xxsea__zer)
            return xmhm__dxst
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        yijd__vllt = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype
            )
        xxsea__zer = 0
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
            uhx__ipgu = yijd__vllt
            gjbo__nysz = 0
            if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                uhx__ipgu = arr[vgncy__yjhwd]
                gjbo__nysz = 1
            yijd__vllt = min(yijd__vllt, uhx__ipgu)
            xxsea__zer += gjbo__nysz
        xmhm__dxst = bodo.hiframes.series_kernels._sum_handle_nan(yijd__vllt,
            xxsea__zer)
        return xmhm__dxst
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            yijd__vllt = numba.cpython.builtins.get_type_min_value(np.int64)
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
                uhx__ipgu = yijd__vllt
                gjbo__nysz = 0
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                    uhx__ipgu = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[vgncy__yjhwd]))
                    gjbo__nysz = 1
                yijd__vllt = max(yijd__vllt, uhx__ipgu)
                xxsea__zer += gjbo__nysz
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(yijd__vllt,
                xxsea__zer)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            yijd__vllt = numba.cpython.builtins.get_type_min_value(np.int64)
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
                uhx__ipgu = yijd__vllt
                gjbo__nysz = 0
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                    uhx__ipgu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[vgncy__yjhwd])
                    gjbo__nysz = 1
                yijd__vllt = max(yijd__vllt, uhx__ipgu)
                xxsea__zer += gjbo__nysz
            return bodo.hiframes.pd_index_ext._dti_val_finalize(yijd__vllt,
                xxsea__zer)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            xhzbz__quqj = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            yijd__vllt = -1
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(
                xhzbz__quqj)):
                yijd__vllt = max(yijd__vllt, xhzbz__quqj[vgncy__yjhwd])
            xmhm__dxst = bodo.hiframes.series_kernels._box_cat_val(yijd__vllt,
                arr.dtype, 1)
            return xmhm__dxst
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            yijd__vllt = bodo.hiframes.series_kernels._get_date_min_value()
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
                uhx__ipgu = yijd__vllt
                gjbo__nysz = 0
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                    uhx__ipgu = arr[vgncy__yjhwd]
                    gjbo__nysz = 1
                yijd__vllt = max(yijd__vllt, uhx__ipgu)
                xxsea__zer += gjbo__nysz
            xmhm__dxst = bodo.hiframes.series_kernels._sum_handle_nan(
                yijd__vllt, xxsea__zer)
            return xmhm__dxst
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        yijd__vllt = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype
            )
        xxsea__zer = 0
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
            uhx__ipgu = yijd__vllt
            gjbo__nysz = 0
            if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                uhx__ipgu = arr[vgncy__yjhwd]
                gjbo__nysz = 1
            yijd__vllt = max(yijd__vllt, uhx__ipgu)
            xxsea__zer += gjbo__nysz
        xmhm__dxst = bodo.hiframes.series_kernels._sum_handle_nan(yijd__vllt,
            xxsea__zer)
        return xmhm__dxst
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
    ozgx__qacee = types.float64
    sduc__zzhjq = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        ozgx__qacee = types.float32
        sduc__zzhjq = types.float32
    baebw__qcm = ozgx__qacee(0)
    smi__cwsb = sduc__zzhjq(0)
    qdmi__cuhbt = sduc__zzhjq(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        yijd__vllt = baebw__qcm
        xxsea__zer = smi__cwsb
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
            uhx__ipgu = baebw__qcm
            gjbo__nysz = smi__cwsb
            if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                uhx__ipgu = arr[vgncy__yjhwd]
                gjbo__nysz = qdmi__cuhbt
            yijd__vllt += uhx__ipgu
            xxsea__zer += gjbo__nysz
        xmhm__dxst = bodo.hiframes.series_kernels._mean_handle_nan(yijd__vllt,
            xxsea__zer)
        return xmhm__dxst
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        eruni__nbgoq = 0.0
        ips__dxrh = 0.0
        xxsea__zer = 0
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
            uhx__ipgu = 0.0
            gjbo__nysz = 0
            if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd
                ) or not skipna:
                uhx__ipgu = arr[vgncy__yjhwd]
                gjbo__nysz = 1
            eruni__nbgoq += uhx__ipgu
            ips__dxrh += uhx__ipgu * uhx__ipgu
            xxsea__zer += gjbo__nysz
        xmhm__dxst = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            eruni__nbgoq, ips__dxrh, xxsea__zer, ddof)
        return xmhm__dxst
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
                jypvh__uilp = np.empty(len(q), np.int64)
                for vgncy__yjhwd in range(len(q)):
                    jqhm__lpco = np.float64(q[vgncy__yjhwd])
                    jypvh__uilp[vgncy__yjhwd
                        ] = bodo.libs.array_kernels.quantile(arr.view(np.
                        int64), jqhm__lpco)
                return jypvh__uilp.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            jypvh__uilp = np.empty(len(q), np.float64)
            for vgncy__yjhwd in range(len(q)):
                jqhm__lpco = np.float64(q[vgncy__yjhwd])
                jypvh__uilp[vgncy__yjhwd] = bodo.libs.array_kernels.quantile(
                    arr, jqhm__lpco)
            return jypvh__uilp
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
        wykj__eoaz = types.intp
    elif arr.dtype == types.bool_:
        wykj__eoaz = np.int64
    else:
        wykj__eoaz = arr.dtype
    ngc__xgev = wykj__eoaz(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            yijd__vllt = ngc__xgev
            bffm__ghkco = len(arr)
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(
                bffm__ghkco):
                uhx__ipgu = ngc__xgev
                gjbo__nysz = 0
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd
                    ) or not skipna:
                    uhx__ipgu = arr[vgncy__yjhwd]
                    gjbo__nysz = 1
                yijd__vllt += uhx__ipgu
                xxsea__zer += gjbo__nysz
            xmhm__dxst = bodo.hiframes.series_kernels._var_handle_mincount(
                yijd__vllt, xxsea__zer, min_count)
            return xmhm__dxst
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            yijd__vllt = ngc__xgev
            bffm__ghkco = len(arr)
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(
                bffm__ghkco):
                uhx__ipgu = ngc__xgev
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                    uhx__ipgu = arr[vgncy__yjhwd]
                yijd__vllt += uhx__ipgu
            return yijd__vllt
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    aepdj__ysgei = arr.dtype(1)
    if arr.dtype == types.bool_:
        aepdj__ysgei = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            yijd__vllt = aepdj__ysgei
            xxsea__zer = 0
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
                uhx__ipgu = aepdj__ysgei
                gjbo__nysz = 0
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd
                    ) or not skipna:
                    uhx__ipgu = arr[vgncy__yjhwd]
                    gjbo__nysz = 1
                xxsea__zer += gjbo__nysz
                yijd__vllt *= uhx__ipgu
            xmhm__dxst = bodo.hiframes.series_kernels._var_handle_mincount(
                yijd__vllt, xxsea__zer, min_count)
            return xmhm__dxst
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            yijd__vllt = aepdj__ysgei
            for vgncy__yjhwd in numba.parfors.parfor.internal_prange(len(arr)):
                uhx__ipgu = aepdj__ysgei
                if not bodo.libs.array_kernels.isna(arr, vgncy__yjhwd):
                    uhx__ipgu = arr[vgncy__yjhwd]
                yijd__vllt *= uhx__ipgu
            return yijd__vllt
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        vgncy__yjhwd = bodo.libs.array_kernels._nan_argmax(arr)
        return index[vgncy__yjhwd]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        vgncy__yjhwd = bodo.libs.array_kernels._nan_argmin(arr)
        return index[vgncy__yjhwd]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            orzlo__dmmd = {}
            for zgek__rpppm in values:
                orzlo__dmmd[bodo.utils.conversion.box_if_dt64(zgek__rpppm)] = 0
            return orzlo__dmmd
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
        bffm__ghkco = len(arr)
        jypvh__uilp = np.empty(bffm__ghkco, np.bool_)
        for vgncy__yjhwd in numba.parfors.parfor.internal_prange(bffm__ghkco):
            jypvh__uilp[vgncy__yjhwd] = bodo.utils.conversion.box_if_dt64(arr
                [vgncy__yjhwd]) in values
        return jypvh__uilp
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    trg__fbxad = len(in_arr_tup) != 1
    nmv__fhoc = list(in_arr_tup.types)
    lzdd__ofdj = 'def impl(in_arr_tup):\n'
    lzdd__ofdj += (
        "  ev = tracing.Event('array_unique_vector_map', is_parallel=False)\n")
    lzdd__ofdj += '  n = len(in_arr_tup[0])\n'
    if trg__fbxad:
        fumh__qmxpp = ', '.join([f'in_arr_tup[{vgncy__yjhwd}][unused]' for
            vgncy__yjhwd in range(len(in_arr_tup))])
        aog__xkc = ', '.join(['False' for wrnfp__ojza in range(len(
            in_arr_tup))])
        lzdd__ofdj += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({fumh__qmxpp},), ({aog__xkc},)): 0 for unused in range(0)}}
"""
        lzdd__ofdj += '  map_vector = np.empty(n, np.int64)\n'
        for vgncy__yjhwd, etzml__bcz in enumerate(nmv__fhoc):
            lzdd__ofdj += f'  in_lst_{vgncy__yjhwd} = []\n'
            if is_str_arr_type(etzml__bcz):
                lzdd__ofdj += f'  total_len_{vgncy__yjhwd} = 0\n'
            lzdd__ofdj += f'  null_in_lst_{vgncy__yjhwd} = []\n'
        lzdd__ofdj += '  for i in range(n):\n'
        bkulp__qqpq = ', '.join([f'in_arr_tup[{vgncy__yjhwd}][i]' for
            vgncy__yjhwd in range(len(nmv__fhoc))])
        zlsi__cjo = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{vgncy__yjhwd}], i)' for
            vgncy__yjhwd in range(len(nmv__fhoc))])
        lzdd__ofdj += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({bkulp__qqpq},), ({zlsi__cjo},))
"""
        lzdd__ofdj += '    if data_val not in arr_map:\n'
        lzdd__ofdj += '      set_val = len(arr_map)\n'
        lzdd__ofdj += '      values_tup = data_val._data\n'
        lzdd__ofdj += '      nulls_tup = data_val._null_values\n'
        for vgncy__yjhwd, etzml__bcz in enumerate(nmv__fhoc):
            lzdd__ofdj += (
                f'      in_lst_{vgncy__yjhwd}.append(values_tup[{vgncy__yjhwd}])\n'
                )
            lzdd__ofdj += (
                f'      null_in_lst_{vgncy__yjhwd}.append(nulls_tup[{vgncy__yjhwd}])\n'
                )
            if is_str_arr_type(etzml__bcz):
                lzdd__ofdj += f"""      total_len_{vgncy__yjhwd}  += nulls_tup[{vgncy__yjhwd}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{vgncy__yjhwd}], i)
"""
        lzdd__ofdj += '      arr_map[data_val] = len(arr_map)\n'
        lzdd__ofdj += '    else:\n'
        lzdd__ofdj += '      set_val = arr_map[data_val]\n'
        lzdd__ofdj += '    map_vector[i] = set_val\n'
        lzdd__ofdj += '  n_rows = len(arr_map)\n'
        for vgncy__yjhwd, etzml__bcz in enumerate(nmv__fhoc):
            if is_str_arr_type(etzml__bcz):
                lzdd__ofdj += f"""  out_arr_{vgncy__yjhwd} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{vgncy__yjhwd})
"""
            else:
                lzdd__ofdj += f"""  out_arr_{vgncy__yjhwd} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{vgncy__yjhwd}], (-1,))
"""
        lzdd__ofdj += '  for j in range(len(arr_map)):\n'
        for vgncy__yjhwd in range(len(nmv__fhoc)):
            lzdd__ofdj += f'    if null_in_lst_{vgncy__yjhwd}[j]:\n'
            lzdd__ofdj += (
                f'      bodo.libs.array_kernels.setna(out_arr_{vgncy__yjhwd}, j)\n'
                )
            lzdd__ofdj += '    else:\n'
            lzdd__ofdj += (
                f'      out_arr_{vgncy__yjhwd}[j] = in_lst_{vgncy__yjhwd}[j]\n'
                )
        dqn__ekl = ', '.join([f'out_arr_{vgncy__yjhwd}' for vgncy__yjhwd in
            range(len(nmv__fhoc))])
        lzdd__ofdj += "  ev.add_attribute('n_map_entries', n_rows)\n"
        lzdd__ofdj += '  ev.finalize()\n'
        lzdd__ofdj += f'  return ({dqn__ekl},), map_vector\n'
    else:
        lzdd__ofdj += '  in_arr = in_arr_tup[0]\n'
        lzdd__ofdj += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        lzdd__ofdj += '  map_vector = np.empty(n, np.int64)\n'
        lzdd__ofdj += '  is_na = 0\n'
        lzdd__ofdj += '  in_lst = []\n'
        lzdd__ofdj += '  na_idxs = []\n'
        if is_str_arr_type(nmv__fhoc[0]):
            lzdd__ofdj += '  total_len = 0\n'
        lzdd__ofdj += '  for i in range(n):\n'
        lzdd__ofdj += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        lzdd__ofdj += '      is_na = 1\n'
        lzdd__ofdj += '      # Always put NA in the last location.\n'
        lzdd__ofdj += '      # We use -1 as a placeholder\n'
        lzdd__ofdj += '      set_val = -1\n'
        lzdd__ofdj += '      na_idxs.append(i)\n'
        lzdd__ofdj += '    else:\n'
        lzdd__ofdj += '      data_val = in_arr[i]\n'
        lzdd__ofdj += '      if data_val not in arr_map:\n'
        lzdd__ofdj += '        set_val = len(arr_map)\n'
        lzdd__ofdj += '        in_lst.append(data_val)\n'
        if is_str_arr_type(nmv__fhoc[0]):
            lzdd__ofdj += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        lzdd__ofdj += '        arr_map[data_val] = len(arr_map)\n'
        lzdd__ofdj += '      else:\n'
        lzdd__ofdj += '        set_val = arr_map[data_val]\n'
        lzdd__ofdj += '    map_vector[i] = set_val\n'
        lzdd__ofdj += '  map_vector[na_idxs] = len(arr_map)\n'
        lzdd__ofdj += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(nmv__fhoc[0]):
            lzdd__ofdj += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            lzdd__ofdj += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        lzdd__ofdj += '  for j in range(len(arr_map)):\n'
        lzdd__ofdj += '    out_arr[j] = in_lst[j]\n'
        lzdd__ofdj += '  if is_na:\n'
        lzdd__ofdj += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        lzdd__ofdj += "  ev.add_attribute('n_map_entries', n_rows)\n"
        lzdd__ofdj += '  ev.finalize()\n'
        lzdd__ofdj += f'  return (out_arr,), map_vector\n'
    qge__kczf = {}
    exec(lzdd__ofdj, {'bodo': bodo, 'np': np, 'tracing': tracing}, qge__kczf)
    impl = qge__kczf['impl']
    return impl
