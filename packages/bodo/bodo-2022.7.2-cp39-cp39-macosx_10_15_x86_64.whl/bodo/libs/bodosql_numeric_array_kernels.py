"""
Implements numerical array kernels that are specific to BodoSQL
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.bodosql_array_kernel_utils import *
from bodo.utils.typing import get_overload_const_bool, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, raise_bodo_error


@numba.generated_jit(nopython=True)
def bitand(A, B):
    args = [A, B]
    for xqd__gusd in range(2):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitand',
                ['A', 'B'], xqd__gusd)

    def impl(A, B):
        return bitand_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitleftshift(A, B):
    args = [A, B]
    for xqd__gusd in range(2):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitleftshift', ['A', 'B'],
                xqd__gusd)

    def impl(A, B):
        return bitleftshift_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitnot(A):
    if isinstance(A, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.bitnot_util',
            ['A'], 0)

    def impl(A):
        return bitnot_util(A)
    return impl


@numba.generated_jit(nopython=True)
def bitor(A, B):
    args = [A, B]
    for xqd__gusd in range(2):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitor',
                ['A', 'B'], xqd__gusd)

    def impl(A, B):
        return bitor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitrightshift(A, B):
    args = [A, B]
    for xqd__gusd in range(2):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitrightshift', ['A', 'B'],
                xqd__gusd)

    def impl(A, B):
        return bitrightshift_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitxor(A, B):
    args = [A, B]
    for xqd__gusd in range(2):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitxor',
                ['A', 'B'], xqd__gusd)

    def impl(A, B):
        return bitxor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def conv(arr, old_base, new_base):
    args = [arr, old_base, new_base]
    for xqd__gusd in range(3):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.conv', [
                'arr', 'old_base', 'new_base'], xqd__gusd)

    def impl(arr, old_base, new_base):
        return conv_util(arr, old_base, new_base)
    return impl


@numba.generated_jit(nopython=True)
def getbit(A, B):
    args = [A, B]
    for xqd__gusd in range(2):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.getbit',
                ['A', 'B'], xqd__gusd)

    def impl(A, B):
        return getbit_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def haversine(lat1, lon1, lat2, lon2):
    args = [lat1, lon1, lat2, lon2]
    for xqd__gusd in range(4):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.haversine',
                ['lat1', 'lon1', 'lat2', 'lon2'], xqd__gusd)

    def impl(lat1, lon1, lat2, lon2):
        return haversine_util(lat1, lon1, lat2, lon2)
    return impl


@numba.generated_jit(nopython=True)
def div0(arr, divisor):
    args = [arr, divisor]
    for xqd__gusd in range(2):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.div0', [
                'arr', 'divisor'], xqd__gusd)

    def impl(arr, divisor):
        return div0_util(arr, divisor)
    return impl


@numba.generated_jit(nopython=True)
def log(arr, base):
    args = [arr, base]
    for xqd__gusd in range(2):
        if isinstance(args[xqd__gusd], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.log', [
                'arr', 'base'], xqd__gusd)

    def impl(arr, base):
        return log_util(arr, base)
    return impl


@numba.generated_jit(nopython=True)
def negate(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.negate_util',
            ['arr'], 0)

    def impl(arr):
        return negate_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def bitand_util(A, B):
    verify_int_arg(A, 'bitand', 'A')
    verify_int_arg(B, 'bitand', 'B')
    zfq__renbl = ['A', 'B']
    qpjfp__omb = [A, B]
    fok__hcgam = [True] * 2
    uctdw__jub = 'res[i] = arg0 & arg1'
    geau__elide = get_common_broadcasted_type([A, B], 'bitand')
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def bitleftshift_util(A, B):
    verify_int_arg(A, 'bitleftshift', 'A')
    verify_int_arg(B, 'bitleftshift', 'B')
    zfq__renbl = ['A', 'B']
    qpjfp__omb = [A, B]
    fok__hcgam = [True] * 2
    uctdw__jub = 'res[i] = arg0 << arg1'
    geau__elide = bodo.libs.int_arr_ext.IntegerArrayType(types.int64)
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def bitnot_util(A):
    verify_int_arg(A, 'bitnot', 'A')
    zfq__renbl = ['A']
    qpjfp__omb = [A]
    fok__hcgam = [True]
    uctdw__jub = 'res[i] = ~arg0'
    if A == bodo.none:
        geau__elide = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            lqgm__zeoo = A.dtype
        else:
            lqgm__zeoo = A
        geau__elide = bodo.libs.int_arr_ext.IntegerArrayType(lqgm__zeoo)
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def bitor_util(A, B):
    verify_int_arg(A, 'bitor', 'A')
    verify_int_arg(B, 'bitor', 'B')
    zfq__renbl = ['A', 'B']
    qpjfp__omb = [A, B]
    fok__hcgam = [True] * 2
    uctdw__jub = 'res[i] = arg0 | arg1'
    geau__elide = get_common_broadcasted_type([A, B], 'bitor')
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def bitrightshift_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    zfq__renbl = ['A', 'B']
    qpjfp__omb = [A, B]
    fok__hcgam = [True] * 2
    if A == bodo.none:
        lqgm__zeoo = geau__elide = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            lqgm__zeoo = A.dtype
        else:
            lqgm__zeoo = A
        geau__elide = bodo.libs.int_arr_ext.IntegerArrayType(lqgm__zeoo)
    uctdw__jub = f'res[i] = arg0 >> arg1\n'
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def bitxor_util(A, B):
    verify_int_arg(A, 'bitxor', 'A')
    verify_int_arg(B, 'bitxor', 'B')
    zfq__renbl = ['A', 'B']
    qpjfp__omb = [A, B]
    fok__hcgam = [True] * 2
    uctdw__jub = 'res[i] = arg0 ^ arg1'
    geau__elide = get_common_broadcasted_type([A, B], 'bitxor')
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def conv_util(arr, old_base, new_base):
    verify_string_arg(arr, 'CONV', 'arr')
    verify_int_arg(old_base, 'CONV', 'old_base')
    verify_int_arg(new_base, 'CONV', 'new_base')
    zfq__renbl = ['arr', 'old_base', 'new_base']
    qpjfp__omb = [arr, old_base, new_base]
    fok__hcgam = [True] * 3
    uctdw__jub = 'old_val = int(arg0, arg1)\n'
    uctdw__jub += 'if arg2 == 2:\n'
    uctdw__jub += "   res[i] = format(old_val, 'b')\n"
    uctdw__jub += 'elif arg2 == 8:\n'
    uctdw__jub += "   res[i] = format(old_val, 'o')\n"
    uctdw__jub += 'elif arg2 == 10:\n'
    uctdw__jub += "   res[i] = format(old_val, 'd')\n"
    uctdw__jub += 'elif arg2 == 16:\n'
    uctdw__jub += "   res[i] = format(old_val, 'x')\n"
    uctdw__jub += 'else:\n'
    uctdw__jub += '   bodo.libs.array_kernels.setna(res, i)\n'
    geau__elide = bodo.string_array_type
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def getbit_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    zfq__renbl = ['A', 'B']
    qpjfp__omb = [A, B]
    fok__hcgam = [True] * 2
    uctdw__jub = 'res[i] = (arg0 >> arg1) & 1'
    geau__elide = bodo.libs.int_arr_ext.IntegerArrayType(types.uint8)
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def haversine_util(lat1, lon1, lat2, lon2):
    verify_int_float_arg(lat1, 'HAVERSINE', 'lat1')
    verify_int_float_arg(lon1, 'HAVERSINE', 'lon1')
    verify_int_float_arg(lat2, 'HAVERSINE', 'lat2')
    verify_int_float_arg(lon2, 'HAVERSINE', 'lon2')
    zfq__renbl = ['lat1', 'lon1', 'lat2', 'lon2']
    qpjfp__omb = [lat1, lon1, lat2, lon2]
    rgdfw__ajyzr = [True] * 4
    uctdw__jub = (
        'arg0, arg1, arg2, arg3 = map(np.radians, (arg0, arg1, arg2, arg3))\n')
    imdt__qqcf = '(arg2 - arg0) * 0.5'
    bgcq__sswhh = '(arg3 - arg1) * 0.5'
    mfgcs__hozmx = (
        f'np.square(np.sin({imdt__qqcf})) + (np.cos(arg0) * np.cos(arg2) * np.square(np.sin({bgcq__sswhh})))'
        )
    uctdw__jub += f'res[i] = 12742.0 * np.arcsin(np.sqrt({mfgcs__hozmx}))\n'
    geau__elide = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(zfq__renbl, qpjfp__omb, rgdfw__ajyzr, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def div0_util(arr, divisor):
    verify_int_float_arg(arr, 'DIV0', 'arr')
    verify_int_float_arg(divisor, 'DIV0', 'divisor')
    zfq__renbl = ['arr', 'divisor']
    qpjfp__omb = [arr, divisor]
    rgdfw__ajyzr = [True] * 2
    uctdw__jub = 'res[i] = arg0 / arg1 if arg1 else 0\n'
    geau__elide = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(zfq__renbl, qpjfp__omb, rgdfw__ajyzr, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def log_util(arr, base):
    verify_int_float_arg(arr, 'log', 'arr')
    verify_int_float_arg(base, 'log', 'base')
    zfq__renbl = ['arr', 'base']
    qpjfp__omb = [arr, base]
    fok__hcgam = [True] * 2
    uctdw__jub = 'res[i] = np.log(arg0) / np.log(arg1)'
    geau__elide = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


@numba.generated_jit(nopython=True)
def negate_util(arr):
    verify_int_float_arg(arr, 'negate', 'arr')
    zfq__renbl = ['arr']
    qpjfp__omb = [arr]
    fok__hcgam = [True]
    if arr == bodo.none:
        lqgm__zeoo = types.int32
    elif bodo.utils.utils.is_array_typ(arr, False):
        lqgm__zeoo = arr.dtype
    elif bodo.utils.utils.is_array_typ(arr, True):
        lqgm__zeoo = arr.data.dtype
    else:
        lqgm__zeoo = arr
    uctdw__jub = {types.uint8: 'res[i] = -np.int16(arg0)', types.uint16:
        'res[i] = -np.int32(arg0)', types.uint32: 'res[i] = -np.int64(arg0)'
        }.get(lqgm__zeoo, 'res[i] = -arg0')
    lqgm__zeoo = {types.uint8: types.int16, types.uint16: types.int32,
        types.uint32: types.int64, types.uint64: types.int64}.get(lqgm__zeoo,
        lqgm__zeoo)
    geau__elide = bodo.utils.typing.to_nullable_type(bodo.utils.typing.
        dtype_to_array_type(lqgm__zeoo))
    return gen_vectorized(zfq__renbl, qpjfp__omb, fok__hcgam, uctdw__jub,
        geau__elide)


def rank_sql(arr_tup, method='average', pct=False):
    return


@overload(rank_sql, no_unliteral=True)
def overload_rank_sql(arr_tup, method='average', pct=False):
    if not is_overload_constant_str(method):
        raise_bodo_error(
            "Series.rank(): 'method' argument must be a constant string")
    method = get_overload_const_str(method)
    if not is_overload_constant_bool(pct):
        raise_bodo_error(
            "Series.rank(): 'pct' argument must be a constant boolean")
    pct = get_overload_const_bool(pct)
    tcmyv__mnmfn = 'def impl(arr_tup, method="average", pct=False):\n'
    if method == 'first':
        tcmyv__mnmfn += '  ret = np.arange(1, n + 1, 1, np.float64)\n'
    else:
        tcmyv__mnmfn += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr_tup[0])\n')
        tcmyv__mnmfn += '  for arr in arr_tup:\n'
        tcmyv__mnmfn += (
            '    next_obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        tcmyv__mnmfn += '    obs = obs | next_obs \n'
        tcmyv__mnmfn += '  dense = obs.cumsum()\n'
        if method == 'dense':
            tcmyv__mnmfn += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            tcmyv__mnmfn += '    dense,\n'
            tcmyv__mnmfn += '    new_dtype=np.float64,\n'
            tcmyv__mnmfn += '    copy=True,\n'
            tcmyv__mnmfn += '    nan_to_str=False,\n'
            tcmyv__mnmfn += '    from_series=True,\n'
            tcmyv__mnmfn += '  )\n'
        else:
            tcmyv__mnmfn += """  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))
"""
            tcmyv__mnmfn += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                tcmyv__mnmfn += '  ret = count_float[dense]\n'
            elif method == 'min':
                tcmyv__mnmfn += '  ret = count_float[dense - 1] + 1\n'
            else:
                tcmyv__mnmfn += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            tcmyv__mnmfn += '  div_val = np.max(ret)\n'
        else:
            tcmyv__mnmfn += '  div_val = arr.size\n'
        tcmyv__mnmfn += '  for i in range(len(ret)):\n'
        tcmyv__mnmfn += '    ret[i] = ret[i] / div_val\n'
    tcmyv__mnmfn += '  return ret\n'
    bhkme__hrhno = {}
    exec(tcmyv__mnmfn, {'np': np, 'pd': pd, 'bodo': bodo}, bhkme__hrhno)
    return bhkme__hrhno['impl']
