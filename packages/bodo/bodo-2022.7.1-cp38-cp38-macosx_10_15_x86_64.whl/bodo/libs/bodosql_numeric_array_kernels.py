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
    for uoehz__iif in range(3):
        if isinstance(args[uoehz__iif], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.conv', [
                'arr', 'old_base', 'new_base'], uoehz__iif)

    def impl(arr, old_base, new_base):
        return conv_util(arr, old_base, new_base)
    return impl


@numba.generated_jit(nopython=True)
def div0(arr, divisor):
    args = [arr, divisor]
    for uoehz__iif in range(2):
        if isinstance(args[uoehz__iif], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.div0', [
                'arr', 'divisor'], uoehz__iif)

    def impl(arr, divisor):
        return div0_util(arr, divisor)
    return impl


@numba.generated_jit(nopython=True)
def log(arr, base):
    args = [arr, base]
    for uoehz__iif in range(2):
        if isinstance(args[uoehz__iif], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.log', [
                'arr', 'base'], uoehz__iif)

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
    yfabq__dqde = ['arr', 'old_base', 'new_base']
    zvyz__gyj = [arr, old_base, new_base]
    mjlm__spkq = [True] * 3
    codii__jaz = 'old_val = int(arg0, arg1)\n'
    codii__jaz += 'if arg2 == 2:\n'
    codii__jaz += "   res[i] = format(old_val, 'b')\n"
    codii__jaz += 'elif arg2 == 8:\n'
    codii__jaz += "   res[i] = format(old_val, 'o')\n"
    codii__jaz += 'elif arg2 == 10:\n'
    codii__jaz += "   res[i] = format(old_val, 'd')\n"
    codii__jaz += 'elif arg2 == 16:\n'
    codii__jaz += "   res[i] = format(old_val, 'x')\n"
    codii__jaz += 'else:\n'
    codii__jaz += '   bodo.libs.array_kernels.setna(res, i)\n'
    hag__ufmlm = bodo.string_array_type
    return gen_vectorized(yfabq__dqde, zvyz__gyj, mjlm__spkq, codii__jaz,
        hag__ufmlm)


@numba.generated_jit(nopython=True)
def div0_util(arr, divisor):
    verify_int_float_arg(arr, 'DIV0', 'arr')
    verify_int_float_arg(divisor, 'DIV0', 'divisor')
    yfabq__dqde = ['arr', 'divisor']
    zvyz__gyj = [arr, divisor]
    dni__xeki = [True] * 2
    codii__jaz = 'res[i] = arg0 / arg1 if arg1 else 0\n'
    hag__ufmlm = types.float64
    return gen_vectorized(yfabq__dqde, zvyz__gyj, dni__xeki, codii__jaz,
        hag__ufmlm)


@numba.generated_jit(nopython=True)
def log_util(arr, base):
    verify_int_float_arg(arr, 'log', 'arr')
    verify_int_float_arg(base, 'log', 'base')
    yfabq__dqde = ['arr', 'base']
    zvyz__gyj = [arr, base]
    mjlm__spkq = [True] * 2
    codii__jaz = 'res[i] = np.log(arg0) / np.log(arg1)'
    hag__ufmlm = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(yfabq__dqde, zvyz__gyj, mjlm__spkq, codii__jaz,
        hag__ufmlm)


@numba.generated_jit(nopython=True)
def negate_util(arr):
    verify_int_float_arg(arr, 'negate', 'arr')
    yfabq__dqde = ['arr']
    zvyz__gyj = [arr]
    mjlm__spkq = [True]
    if arr == bodo.none:
        cmxa__kqc = types.int32
    elif bodo.utils.utils.is_array_typ(arr, False):
        cmxa__kqc = arr.dtype
    elif bodo.utils.utils.is_array_typ(arr, True):
        cmxa__kqc = arr.data.dtype
    else:
        cmxa__kqc = arr
    codii__jaz = {types.uint8: 'res[i] = -np.int16(arg0)', types.uint16:
        'res[i] = -np.int32(arg0)', types.uint32: 'res[i] = -np.int64(arg0)'
        }.get(cmxa__kqc, 'res[i] = -arg0')
    cmxa__kqc = {types.uint8: types.int16, types.uint16: types.int32, types
        .uint32: types.int64, types.uint64: types.int64}.get(cmxa__kqc,
        cmxa__kqc)
    hag__ufmlm = bodo.utils.typing.to_nullable_type(bodo.utils.typing.
        dtype_to_array_type(cmxa__kqc))
    return gen_vectorized(yfabq__dqde, zvyz__gyj, mjlm__spkq, codii__jaz,
        hag__ufmlm)


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
    fpp__dyhw = 'def impl(arr_tup, method="average", pct=False):\n'
    if method == 'first':
        fpp__dyhw += '  ret = np.arange(1, n + 1, 1, np.float64)\n'
    else:
        fpp__dyhw += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr_tup[0])\n')
        fpp__dyhw += '  for arr in arr_tup:\n'
        fpp__dyhw += (
            '    next_obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        fpp__dyhw += '    obs = obs | next_obs \n'
        fpp__dyhw += '  dense = obs.cumsum()\n'
        if method == 'dense':
            fpp__dyhw += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            fpp__dyhw += '    dense,\n'
            fpp__dyhw += '    new_dtype=np.float64,\n'
            fpp__dyhw += '    copy=True,\n'
            fpp__dyhw += '    nan_to_str=False,\n'
            fpp__dyhw += '    from_series=True,\n'
            fpp__dyhw += '  )\n'
        else:
            fpp__dyhw += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            fpp__dyhw += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                fpp__dyhw += '  ret = count_float[dense]\n'
            elif method == 'min':
                fpp__dyhw += '  ret = count_float[dense - 1] + 1\n'
            else:
                fpp__dyhw += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            fpp__dyhw += '  div_val = np.max(ret)\n'
        else:
            fpp__dyhw += '  div_val = arr.size\n'
        fpp__dyhw += '  for i in range(len(ret)):\n'
        fpp__dyhw += '    ret[i] = ret[i] / div_val\n'
    fpp__dyhw += '  return ret\n'
    cbsk__vwag = {}
    exec(fpp__dyhw, {'np': np, 'pd': pd, 'bodo': bodo}, cbsk__vwag)
    return cbsk__vwag['impl']
