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
    for acqqr__qwqcc in range(2):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitand',
                ['A', 'B'], acqqr__qwqcc)

    def impl(A, B):
        return bitand_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitleftshift(A, B):
    args = [A, B]
    for acqqr__qwqcc in range(2):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitleftshift', ['A', 'B'],
                acqqr__qwqcc)

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
    for acqqr__qwqcc in range(2):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitor',
                ['A', 'B'], acqqr__qwqcc)

    def impl(A, B):
        return bitor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitrightshift(A, B):
    args = [A, B]
    for acqqr__qwqcc in range(2):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.bitrightshift', ['A', 'B'],
                acqqr__qwqcc)

    def impl(A, B):
        return bitrightshift_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def bitxor(A, B):
    args = [A, B]
    for acqqr__qwqcc in range(2):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.bitxor',
                ['A', 'B'], acqqr__qwqcc)

    def impl(A, B):
        return bitxor_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def conv(arr, old_base, new_base):
    args = [arr, old_base, new_base]
    for acqqr__qwqcc in range(3):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.conv', [
                'arr', 'old_base', 'new_base'], acqqr__qwqcc)

    def impl(arr, old_base, new_base):
        return conv_util(arr, old_base, new_base)
    return impl


@numba.generated_jit(nopython=True)
def getbit(A, B):
    args = [A, B]
    for acqqr__qwqcc in range(2):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.getbit',
                ['A', 'B'], acqqr__qwqcc)

    def impl(A, B):
        return getbit_util(A, B)
    return impl


@numba.generated_jit(nopython=True)
def haversine(lat1, lon1, lat2, lon2):
    args = [lat1, lon1, lat2, lon2]
    for acqqr__qwqcc in range(4):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.haversine',
                ['lat1', 'lon1', 'lat2', 'lon2'], acqqr__qwqcc)

    def impl(lat1, lon1, lat2, lon2):
        return haversine_util(lat1, lon1, lat2, lon2)
    return impl


@numba.generated_jit(nopython=True)
def div0(arr, divisor):
    args = [arr, divisor]
    for acqqr__qwqcc in range(2):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.div0', [
                'arr', 'divisor'], acqqr__qwqcc)

    def impl(arr, divisor):
        return div0_util(arr, divisor)
    return impl


@numba.generated_jit(nopython=True)
def log(arr, base):
    args = [arr, base]
    for acqqr__qwqcc in range(2):
        if isinstance(args[acqqr__qwqcc], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.log', [
                'arr', 'base'], acqqr__qwqcc)

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
    vlpkd__vkyg = ['A', 'B']
    nroz__gbyq = [A, B]
    jnd__pgd = [True] * 2
    zaifi__ivgi = 'res[i] = arg0 & arg1'
    uugf__lvykg = get_common_broadcasted_type([A, B], 'bitand')
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def bitleftshift_util(A, B):
    verify_int_arg(A, 'bitleftshift', 'A')
    verify_int_arg(B, 'bitleftshift', 'B')
    vlpkd__vkyg = ['A', 'B']
    nroz__gbyq = [A, B]
    jnd__pgd = [True] * 2
    zaifi__ivgi = 'res[i] = arg0 << arg1'
    uugf__lvykg = bodo.libs.int_arr_ext.IntegerArrayType(types.int64)
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def bitnot_util(A):
    verify_int_arg(A, 'bitnot', 'A')
    vlpkd__vkyg = ['A']
    nroz__gbyq = [A]
    jnd__pgd = [True]
    zaifi__ivgi = 'res[i] = ~arg0'
    if A == bodo.none:
        uugf__lvykg = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            xuy__egeav = A.dtype
        else:
            xuy__egeav = A
        uugf__lvykg = bodo.libs.int_arr_ext.IntegerArrayType(xuy__egeav)
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def bitor_util(A, B):
    verify_int_arg(A, 'bitor', 'A')
    verify_int_arg(B, 'bitor', 'B')
    vlpkd__vkyg = ['A', 'B']
    nroz__gbyq = [A, B]
    jnd__pgd = [True] * 2
    zaifi__ivgi = 'res[i] = arg0 | arg1'
    uugf__lvykg = get_common_broadcasted_type([A, B], 'bitor')
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def bitrightshift_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    vlpkd__vkyg = ['A', 'B']
    nroz__gbyq = [A, B]
    jnd__pgd = [True] * 2
    if A == bodo.none:
        xuy__egeav = uugf__lvykg = bodo.none
    else:
        if bodo.utils.utils.is_array_typ(A, True):
            xuy__egeav = A.dtype
        else:
            xuy__egeav = A
        uugf__lvykg = bodo.libs.int_arr_ext.IntegerArrayType(xuy__egeav)
    zaifi__ivgi = f'res[i] = arg0 >> arg1\n'
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def bitxor_util(A, B):
    verify_int_arg(A, 'bitxor', 'A')
    verify_int_arg(B, 'bitxor', 'B')
    vlpkd__vkyg = ['A', 'B']
    nroz__gbyq = [A, B]
    jnd__pgd = [True] * 2
    zaifi__ivgi = 'res[i] = arg0 ^ arg1'
    uugf__lvykg = get_common_broadcasted_type([A, B], 'bitxor')
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def conv_util(arr, old_base, new_base):
    verify_string_arg(arr, 'CONV', 'arr')
    verify_int_arg(old_base, 'CONV', 'old_base')
    verify_int_arg(new_base, 'CONV', 'new_base')
    vlpkd__vkyg = ['arr', 'old_base', 'new_base']
    nroz__gbyq = [arr, old_base, new_base]
    jnd__pgd = [True] * 3
    zaifi__ivgi = 'old_val = int(arg0, arg1)\n'
    zaifi__ivgi += 'if arg2 == 2:\n'
    zaifi__ivgi += "   res[i] = format(old_val, 'b')\n"
    zaifi__ivgi += 'elif arg2 == 8:\n'
    zaifi__ivgi += "   res[i] = format(old_val, 'o')\n"
    zaifi__ivgi += 'elif arg2 == 10:\n'
    zaifi__ivgi += "   res[i] = format(old_val, 'd')\n"
    zaifi__ivgi += 'elif arg2 == 16:\n'
    zaifi__ivgi += "   res[i] = format(old_val, 'x')\n"
    zaifi__ivgi += 'else:\n'
    zaifi__ivgi += '   bodo.libs.array_kernels.setna(res, i)\n'
    uugf__lvykg = bodo.string_array_type
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def getbit_util(A, B):
    verify_int_arg(A, 'bitrightshift', 'A')
    verify_int_arg(B, 'bitrightshift', 'B')
    vlpkd__vkyg = ['A', 'B']
    nroz__gbyq = [A, B]
    jnd__pgd = [True] * 2
    zaifi__ivgi = 'res[i] = (arg0 >> arg1) & 1'
    uugf__lvykg = bodo.libs.int_arr_ext.IntegerArrayType(types.uint8)
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def haversine_util(lat1, lon1, lat2, lon2):
    verify_int_float_arg(lat1, 'HAVERSINE', 'lat1')
    verify_int_float_arg(lon1, 'HAVERSINE', 'lon1')
    verify_int_float_arg(lat2, 'HAVERSINE', 'lat2')
    verify_int_float_arg(lon2, 'HAVERSINE', 'lon2')
    vlpkd__vkyg = ['lat1', 'lon1', 'lat2', 'lon2']
    nroz__gbyq = [lat1, lon1, lat2, lon2]
    mvl__pox = [True] * 4
    zaifi__ivgi = (
        'arg0, arg1, arg2, arg3 = map(np.radians, (arg0, arg1, arg2, arg3))\n')
    aon__mfdy = '(arg2 - arg0) * 0.5'
    iih__qhve = '(arg3 - arg1) * 0.5'
    qfqi__gjea = (
        f'np.square(np.sin({aon__mfdy})) + (np.cos(arg0) * np.cos(arg2) * np.square(np.sin({iih__qhve})))'
        )
    zaifi__ivgi += f'res[i] = 12742.0 * np.arcsin(np.sqrt({qfqi__gjea}))\n'
    uugf__lvykg = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, mvl__pox, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def div0_util(arr, divisor):
    verify_int_float_arg(arr, 'DIV0', 'arr')
    verify_int_float_arg(divisor, 'DIV0', 'divisor')
    vlpkd__vkyg = ['arr', 'divisor']
    nroz__gbyq = [arr, divisor]
    mvl__pox = [True] * 2
    zaifi__ivgi = 'res[i] = arg0 / arg1 if arg1 else 0\n'
    uugf__lvykg = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, mvl__pox, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def log_util(arr, base):
    verify_int_float_arg(arr, 'log', 'arr')
    verify_int_float_arg(base, 'log', 'base')
    vlpkd__vkyg = ['arr', 'base']
    nroz__gbyq = [arr, base]
    jnd__pgd = [True] * 2
    zaifi__ivgi = 'res[i] = np.log(arg0) / np.log(arg1)'
    uugf__lvykg = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


@numba.generated_jit(nopython=True)
def negate_util(arr):
    verify_int_float_arg(arr, 'negate', 'arr')
    vlpkd__vkyg = ['arr']
    nroz__gbyq = [arr]
    jnd__pgd = [True]
    if arr == bodo.none:
        xuy__egeav = types.int32
    elif bodo.utils.utils.is_array_typ(arr, False):
        xuy__egeav = arr.dtype
    elif bodo.utils.utils.is_array_typ(arr, True):
        xuy__egeav = arr.data.dtype
    else:
        xuy__egeav = arr
    zaifi__ivgi = {types.uint8: 'res[i] = -np.int16(arg0)', types.uint16:
        'res[i] = -np.int32(arg0)', types.uint32: 'res[i] = -np.int64(arg0)'
        }.get(xuy__egeav, 'res[i] = -arg0')
    xuy__egeav = {types.uint8: types.int16, types.uint16: types.int32,
        types.uint32: types.int64, types.uint64: types.int64}.get(xuy__egeav,
        xuy__egeav)
    uugf__lvykg = bodo.utils.typing.to_nullable_type(bodo.utils.typing.
        dtype_to_array_type(xuy__egeav))
    return gen_vectorized(vlpkd__vkyg, nroz__gbyq, jnd__pgd, zaifi__ivgi,
        uugf__lvykg)


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
    rnm__epchs = 'def impl(arr_tup, method="average", pct=False):\n'
    if method == 'first':
        rnm__epchs += '  ret = np.arange(1, n + 1, 1, np.float64)\n'
    else:
        rnm__epchs += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr_tup[0])\n')
        rnm__epchs += '  for arr in arr_tup:\n'
        rnm__epchs += (
            '    next_obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        rnm__epchs += '    obs = obs | next_obs \n'
        rnm__epchs += '  dense = obs.cumsum()\n'
        if method == 'dense':
            rnm__epchs += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            rnm__epchs += '    dense,\n'
            rnm__epchs += '    new_dtype=np.float64,\n'
            rnm__epchs += '    copy=True,\n'
            rnm__epchs += '    nan_to_str=False,\n'
            rnm__epchs += '    from_series=True,\n'
            rnm__epchs += '  )\n'
        else:
            rnm__epchs += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            rnm__epchs += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                rnm__epchs += '  ret = count_float[dense]\n'
            elif method == 'min':
                rnm__epchs += '  ret = count_float[dense - 1] + 1\n'
            else:
                rnm__epchs += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            rnm__epchs += '  div_val = np.max(ret)\n'
        else:
            rnm__epchs += '  div_val = arr.size\n'
        rnm__epchs += '  for i in range(len(ret)):\n'
        rnm__epchs += '    ret[i] = ret[i] / div_val\n'
    rnm__epchs += '  return ret\n'
    eock__xnrr = {}
    exec(rnm__epchs, {'np': np, 'pd': pd, 'bodo': bodo}, eock__xnrr)
    return eock__xnrr['impl']
