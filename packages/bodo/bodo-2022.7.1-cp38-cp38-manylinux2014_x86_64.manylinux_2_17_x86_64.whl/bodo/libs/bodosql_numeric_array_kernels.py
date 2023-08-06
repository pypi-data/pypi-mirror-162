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
def conv(arr, old_base, new_base):
    args = [arr, old_base, new_base]
    for fihqr__ugdj in range(3):
        if isinstance(args[fihqr__ugdj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.conv', [
                'arr', 'old_base', 'new_base'], fihqr__ugdj)

    def impl(arr, old_base, new_base):
        return conv_util(arr, old_base, new_base)
    return impl


@numba.generated_jit(nopython=True)
def div0(arr, divisor):
    args = [arr, divisor]
    for fihqr__ugdj in range(2):
        if isinstance(args[fihqr__ugdj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.div0', [
                'arr', 'divisor'], fihqr__ugdj)

    def impl(arr, divisor):
        return div0_util(arr, divisor)
    return impl


@numba.generated_jit(nopython=True)
def log(arr, base):
    args = [arr, base]
    for fihqr__ugdj in range(2):
        if isinstance(args[fihqr__ugdj], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.log', [
                'arr', 'base'], fihqr__ugdj)

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
def conv_util(arr, old_base, new_base):
    verify_string_arg(arr, 'CONV', 'arr')
    verify_int_arg(old_base, 'CONV', 'old_base')
    verify_int_arg(new_base, 'CONV', 'new_base')
    aziug__wfjrf = ['arr', 'old_base', 'new_base']
    vys__mnm = [arr, old_base, new_base]
    trg__gywrp = [True] * 3
    axscv__bqaf = 'old_val = int(arg0, arg1)\n'
    axscv__bqaf += 'if arg2 == 2:\n'
    axscv__bqaf += "   res[i] = format(old_val, 'b')\n"
    axscv__bqaf += 'elif arg2 == 8:\n'
    axscv__bqaf += "   res[i] = format(old_val, 'o')\n"
    axscv__bqaf += 'elif arg2 == 10:\n'
    axscv__bqaf += "   res[i] = format(old_val, 'd')\n"
    axscv__bqaf += 'elif arg2 == 16:\n'
    axscv__bqaf += "   res[i] = format(old_val, 'x')\n"
    axscv__bqaf += 'else:\n'
    axscv__bqaf += '   bodo.libs.array_kernels.setna(res, i)\n'
    dgm__vzhf = bodo.string_array_type
    return gen_vectorized(aziug__wfjrf, vys__mnm, trg__gywrp, axscv__bqaf,
        dgm__vzhf)


@numba.generated_jit(nopython=True)
def div0_util(arr, divisor):
    verify_int_float_arg(arr, 'DIV0', 'arr')
    verify_int_float_arg(divisor, 'DIV0', 'divisor')
    aziug__wfjrf = ['arr', 'divisor']
    vys__mnm = [arr, divisor]
    zcwm__kdec = [True] * 2
    axscv__bqaf = 'res[i] = arg0 / arg1 if arg1 else 0\n'
    dgm__vzhf = types.float64
    return gen_vectorized(aziug__wfjrf, vys__mnm, zcwm__kdec, axscv__bqaf,
        dgm__vzhf)


@numba.generated_jit(nopython=True)
def log_util(arr, base):
    verify_int_float_arg(arr, 'log', 'arr')
    verify_int_float_arg(base, 'log', 'base')
    aziug__wfjrf = ['arr', 'base']
    vys__mnm = [arr, base]
    trg__gywrp = [True] * 2
    axscv__bqaf = 'res[i] = np.log(arg0) / np.log(arg1)'
    dgm__vzhf = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(aziug__wfjrf, vys__mnm, trg__gywrp, axscv__bqaf,
        dgm__vzhf)


@numba.generated_jit(nopython=True)
def negate_util(arr):
    verify_int_float_arg(arr, 'negate', 'arr')
    aziug__wfjrf = ['arr']
    vys__mnm = [arr]
    trg__gywrp = [True]
    if arr == bodo.none:
        ormyq__sbkfx = types.int32
    elif bodo.utils.utils.is_array_typ(arr, False):
        ormyq__sbkfx = arr.dtype
    elif bodo.utils.utils.is_array_typ(arr, True):
        ormyq__sbkfx = arr.data.dtype
    else:
        ormyq__sbkfx = arr
    axscv__bqaf = {types.uint8: 'res[i] = -np.int16(arg0)', types.uint16:
        'res[i] = -np.int32(arg0)', types.uint32: 'res[i] = -np.int64(arg0)'
        }.get(ormyq__sbkfx, 'res[i] = -arg0')
    ormyq__sbkfx = {types.uint8: types.int16, types.uint16: types.int32,
        types.uint32: types.int64, types.uint64: types.int64}.get(ormyq__sbkfx,
        ormyq__sbkfx)
    dgm__vzhf = bodo.utils.typing.to_nullable_type(bodo.utils.typing.
        dtype_to_array_type(ormyq__sbkfx))
    return gen_vectorized(aziug__wfjrf, vys__mnm, trg__gywrp, axscv__bqaf,
        dgm__vzhf)


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
    ada__cbm = 'def impl(arr_tup, method="average", pct=False):\n'
    if method == 'first':
        ada__cbm += '  ret = np.arange(1, n + 1, 1, np.float64)\n'
    else:
        ada__cbm += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr_tup[0])\n')
        ada__cbm += '  for arr in arr_tup:\n'
        ada__cbm += (
            '    next_obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        ada__cbm += '    obs = obs | next_obs \n'
        ada__cbm += '  dense = obs.cumsum()\n'
        if method == 'dense':
            ada__cbm += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            ada__cbm += '    dense,\n'
            ada__cbm += '    new_dtype=np.float64,\n'
            ada__cbm += '    copy=True,\n'
            ada__cbm += '    nan_to_str=False,\n'
            ada__cbm += '    from_series=True,\n'
            ada__cbm += '  )\n'
        else:
            ada__cbm += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            ada__cbm += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                ada__cbm += '  ret = count_float[dense]\n'
            elif method == 'min':
                ada__cbm += '  ret = count_float[dense - 1] + 1\n'
            else:
                ada__cbm += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            ada__cbm += '  div_val = np.max(ret)\n'
        else:
            ada__cbm += '  div_val = arr.size\n'
        ada__cbm += '  for i in range(len(ret)):\n'
        ada__cbm += '    ret[i] = ret[i] / div_val\n'
    ada__cbm += '  return ret\n'
    fcyi__iozva = {}
    exec(ada__cbm, {'np': np, 'pd': pd, 'bodo': bodo}, fcyi__iozva)
    return fcyi__iozva['impl']
