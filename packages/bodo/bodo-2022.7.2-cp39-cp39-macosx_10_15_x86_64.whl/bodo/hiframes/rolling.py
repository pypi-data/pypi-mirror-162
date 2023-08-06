"""implementations of rolling window functions (sequential and parallel)
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, register_jitable
import bodo
from bodo.libs.distributed_api import Reduce_Type
from bodo.utils.typing import BodoError, decode_if_dict_array, get_overload_const_func, get_overload_const_str, is_const_func_type, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_overload_true
from bodo.utils.utils import unliteral_all
supported_rolling_funcs = ('sum', 'mean', 'var', 'std', 'count', 'median',
    'min', 'max', 'cov', 'corr', 'apply')
unsupported_rolling_methods = ['skew', 'kurt', 'aggregate', 'quantile', 'sem']


def rolling_fixed(arr, win):
    return arr


def rolling_variable(arr, on_arr, win):
    return arr


def rolling_cov(arr, arr2, win):
    return arr


def rolling_corr(arr, arr2, win):
    return arr


@infer_global(rolling_cov)
@infer_global(rolling_corr)
class RollingCovType(AbstractTemplate):

    def generic(self, args, kws):
        arr = args[0]
        denh__kgr = arr.copy(dtype=types.float64)
        return signature(denh__kgr, *unliteral_all(args))


@lower_builtin(rolling_corr, types.VarArg(types.Any))
@lower_builtin(rolling_cov, types.VarArg(types.Any))
def lower_rolling_corr_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@overload(rolling_fixed, no_unliteral=True)
def overload_rolling_fixed(arr, index_arr, win, minp, center, fname, raw=
    True, parallel=False):
    assert is_overload_constant_bool(raw
        ), 'raw argument should be constant bool'
    if is_const_func_type(fname):
        func = _get_apply_func(fname)
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, func, raw))
    assert is_overload_constant_str(fname)
    pcwsw__jlqo = get_overload_const_str(fname)
    if pcwsw__jlqo not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (fixed window) function {}'.format
            (pcwsw__jlqo))
    if pcwsw__jlqo in ('median', 'min', 'max'):
        iygol__fasi = 'def kernel_func(A):\n'
        iygol__fasi += '  if np.isnan(A).sum() != 0: return np.nan\n'
        iygol__fasi += '  return np.{}(A)\n'.format(pcwsw__jlqo)
        sak__mifn = {}
        exec(iygol__fasi, {'np': np}, sak__mifn)
        kernel_func = register_jitable(sak__mifn['kernel_func'])
        return (lambda arr, index_arr, win, minp, center, fname, raw=True,
            parallel=False: roll_fixed_apply(arr, index_arr, win, minp,
            center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        pcwsw__jlqo]
    return (lambda arr, index_arr, win, minp, center, fname, raw=True,
        parallel=False: roll_fixed_linear_generic(arr, win, minp, center,
        parallel, init_kernel, add_kernel, remove_kernel, calc_kernel))


@overload(rolling_variable, no_unliteral=True)
def overload_rolling_variable(arr, on_arr, index_arr, win, minp, center,
    fname, raw=True, parallel=False):
    assert is_overload_constant_bool(raw)
    if is_const_func_type(fname):
        func = _get_apply_func(fname)
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, func, raw))
    assert is_overload_constant_str(fname)
    pcwsw__jlqo = get_overload_const_str(fname)
    if pcwsw__jlqo not in ('sum', 'mean', 'var', 'std', 'count', 'median',
        'min', 'max'):
        raise BodoError('invalid rolling (variable window) function {}'.
            format(pcwsw__jlqo))
    if pcwsw__jlqo in ('median', 'min', 'max'):
        iygol__fasi = 'def kernel_func(A):\n'
        iygol__fasi += '  arr  = dropna(A)\n'
        iygol__fasi += '  if len(arr) == 0: return np.nan\n'
        iygol__fasi += '  return np.{}(arr)\n'.format(pcwsw__jlqo)
        sak__mifn = {}
        exec(iygol__fasi, {'np': np, 'dropna': _dropna}, sak__mifn)
        kernel_func = register_jitable(sak__mifn['kernel_func'])
        return (lambda arr, on_arr, index_arr, win, minp, center, fname,
            raw=True, parallel=False: roll_variable_apply(arr, on_arr,
            index_arr, win, minp, center, parallel, kernel_func))
    init_kernel, add_kernel, remove_kernel, calc_kernel = linear_kernels[
        pcwsw__jlqo]
    return (lambda arr, on_arr, index_arr, win, minp, center, fname, raw=
        True, parallel=False: roll_var_linear_generic(arr, on_arr, win,
        minp, center, parallel, init_kernel, add_kernel, remove_kernel,
        calc_kernel))


def _get_apply_func(f_type):
    func = get_overload_const_func(f_type, None)
    return bodo.compiler.udf_jit(func)


comm_border_tag = 22


@register_jitable
def roll_fixed_linear_generic(in_arr, win, minp, center, parallel,
    init_data, add_obs, remove_obs, calc_out):
    _validate_roll_fixed_args(win, minp)
    in_arr = prep_values(in_arr)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    if parallel:
        halo_size = np.int32(win // 2) if center else np.int32(win - 1)
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data(in_arr, win, minp, center, rank,
                n_pes, init_data, add_obs, remove_obs, calc_out)
        wwbaq__mbjhn = _border_icomm(in_arr, rank, n_pes, halo_size, True,
            center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            blqh__udhv) = wwbaq__mbjhn
    output, data = roll_fixed_linear_generic_seq(in_arr, win, minp, center,
        init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(blqh__udhv, True)
            for czy__xkl in range(0, halo_size):
                data = add_obs(r_recv_buff[czy__xkl], *data)
                vct__dzf = in_arr[N + czy__xkl - win]
                data = remove_obs(vct__dzf, *data)
                output[N + czy__xkl - offset] = calc_out(minp, *data)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            data = init_data()
            for czy__xkl in range(0, halo_size):
                data = add_obs(l_recv_buff[czy__xkl], *data)
            for czy__xkl in range(0, win - 1):
                data = add_obs(in_arr[czy__xkl], *data)
                if czy__xkl > offset:
                    vct__dzf = l_recv_buff[czy__xkl - offset - 1]
                    data = remove_obs(vct__dzf, *data)
                if czy__xkl >= offset:
                    output[czy__xkl - offset] = calc_out(minp, *data)
    return output


@register_jitable
def roll_fixed_linear_generic_seq(in_arr, win, minp, center, init_data,
    add_obs, remove_obs, calc_out):
    data = init_data()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    output = np.empty(N, dtype=np.float64)
    fmvk__xcu = max(minp, 1) - 1
    fmvk__xcu = min(fmvk__xcu, N)
    for czy__xkl in range(0, fmvk__xcu):
        data = add_obs(in_arr[czy__xkl], *data)
        if czy__xkl >= offset:
            output[czy__xkl - offset] = calc_out(minp, *data)
    for czy__xkl in range(fmvk__xcu, N):
        val = in_arr[czy__xkl]
        data = add_obs(val, *data)
        if czy__xkl > win - 1:
            vct__dzf = in_arr[czy__xkl - win]
            data = remove_obs(vct__dzf, *data)
        output[czy__xkl - offset] = calc_out(minp, *data)
    bnt__xrsye = data
    for czy__xkl in range(N, N + offset):
        if czy__xkl > win - 1:
            vct__dzf = in_arr[czy__xkl - win]
            data = remove_obs(vct__dzf, *data)
        output[czy__xkl - offset] = calc_out(minp, *data)
    return output, bnt__xrsye


def roll_fixed_apply(in_arr, index_arr, win, minp, center, parallel,
    kernel_func, raw=True):
    pass


@overload(roll_fixed_apply, no_unliteral=True)
def overload_roll_fixed_apply(in_arr, index_arr, win, minp, center,
    parallel, kernel_func, raw=True):
    assert is_overload_constant_bool(raw)
    return roll_fixed_apply_impl


def roll_fixed_apply_impl(in_arr, index_arr, win, minp, center, parallel,
    kernel_func, raw=True):
    _validate_roll_fixed_args(win, minp)
    in_arr = prep_values(in_arr)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    N = len(in_arr)
    offset = (win - 1) // 2 if center else 0
    index_arr = fix_index_arr(index_arr)
    if parallel:
        halo_size = np.int32(win // 2) if center else np.int32(win - 1)
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_apply(in_arr, index_arr, win, minp,
                center, rank, n_pes, kernel_func, raw)
        wwbaq__mbjhn = _border_icomm(in_arr, rank, n_pes, halo_size, True,
            center)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            blqh__udhv) = wwbaq__mbjhn
        if raw == False:
            vvswc__cek = _border_icomm(index_arr, rank, n_pes, halo_size, 
                True, center)
            (l_recv_buff_idx, r_recv_buff_idx, eyply__kspeo, yfwdv__eml,
                kal__rrter, tcv__isp) = vvswc__cek
    output = roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
        kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, center)
        if raw == False:
            _border_send_wait(yfwdv__eml, eyply__kspeo, rank, n_pes, True,
                center)
        if center and rank != n_pes - 1:
            bodo.libs.distributed_api.wait(blqh__udhv, True)
            if raw == False:
                bodo.libs.distributed_api.wait(tcv__isp, True)
            recv_right_compute(output, in_arr, index_arr, N, win, minp,
                offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            if raw == False:
                bodo.libs.distributed_api.wait(kal__rrter, True)
            recv_left_compute(output, in_arr, index_arr, win, minp, offset,
                l_recv_buff, l_recv_buff_idx, kernel_func, raw)
    return output


def recv_right_compute(output, in_arr, index_arr, N, win, minp, offset,
    r_recv_buff, r_recv_buff_idx, kernel_func, raw):
    pass


@overload(recv_right_compute, no_unliteral=True)
def overload_recv_right_compute(output, in_arr, index_arr, N, win, minp,
    offset, r_recv_buff, r_recv_buff_idx, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, N, win, minp, offset,
            r_recv_buff, r_recv_buff_idx, kernel_func, raw):
            bnt__xrsye = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
            cabic__ghs = 0
            for czy__xkl in range(max(N - offset, 0), N):
                data = bnt__xrsye[cabic__ghs:cabic__ghs + win]
                if win - np.isnan(data).sum() < minp:
                    output[czy__xkl] = np.nan
                else:
                    output[czy__xkl] = kernel_func(data)
                cabic__ghs += 1
        return impl

    def impl_series(output, in_arr, index_arr, N, win, minp, offset,
        r_recv_buff, r_recv_buff_idx, kernel_func, raw):
        bnt__xrsye = np.concatenate((in_arr[N - win + 1:], r_recv_buff))
        dgr__wwum = np.concatenate((index_arr[N - win + 1:], r_recv_buff_idx))
        cabic__ghs = 0
        for czy__xkl in range(max(N - offset, 0), N):
            data = bnt__xrsye[cabic__ghs:cabic__ghs + win]
            if win - np.isnan(data).sum() < minp:
                output[czy__xkl] = np.nan
            else:
                output[czy__xkl] = kernel_func(pd.Series(data, dgr__wwum[
                    cabic__ghs:cabic__ghs + win]))
            cabic__ghs += 1
    return impl_series


def recv_left_compute(output, in_arr, index_arr, win, minp, offset,
    l_recv_buff, l_recv_buff_idx, kernel_func, raw):
    pass


@overload(recv_left_compute, no_unliteral=True)
def overload_recv_left_compute(output, in_arr, index_arr, win, minp, offset,
    l_recv_buff, l_recv_buff_idx, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, win, minp, offset, l_recv_buff,
            l_recv_buff_idx, kernel_func, raw):
            bnt__xrsye = np.concatenate((l_recv_buff, in_arr[:win - 1]))
            for czy__xkl in range(0, win - offset - 1):
                data = bnt__xrsye[czy__xkl:czy__xkl + win]
                if win - np.isnan(data).sum() < minp:
                    output[czy__xkl] = np.nan
                else:
                    output[czy__xkl] = kernel_func(data)
        return impl

    def impl_series(output, in_arr, index_arr, win, minp, offset,
        l_recv_buff, l_recv_buff_idx, kernel_func, raw):
        bnt__xrsye = np.concatenate((l_recv_buff, in_arr[:win - 1]))
        dgr__wwum = np.concatenate((l_recv_buff_idx, index_arr[:win - 1]))
        for czy__xkl in range(0, win - offset - 1):
            data = bnt__xrsye[czy__xkl:czy__xkl + win]
            if win - np.isnan(data).sum() < minp:
                output[czy__xkl] = np.nan
            else:
                output[czy__xkl] = kernel_func(pd.Series(data, dgr__wwum[
                    czy__xkl:czy__xkl + win]))
    return impl_series


def roll_fixed_apply_seq(in_arr, index_arr, win, minp, center, kernel_func,
    raw=True):
    pass


@overload(roll_fixed_apply_seq, no_unliteral=True)
def overload_roll_fixed_apply_seq(in_arr, index_arr, win, minp, center,
    kernel_func, raw=True):
    assert is_overload_constant_bool(raw), "'raw' should be constant bool"

    def roll_fixed_apply_seq_impl(in_arr, index_arr, win, minp, center,
        kernel_func, raw=True):
        N = len(in_arr)
        output = np.empty(N, dtype=np.float64)
        offset = (win - 1) // 2 if center else 0
        for czy__xkl in range(0, N):
            start = max(czy__xkl - win + 1 + offset, 0)
            end = min(czy__xkl + 1 + offset, N)
            data = in_arr[start:end]
            if end - start - np.isnan(data).sum() < minp:
                output[czy__xkl] = np.nan
            else:
                output[czy__xkl] = apply_func(kernel_func, data, index_arr,
                    start, end, raw)
        return output
    return roll_fixed_apply_seq_impl


def apply_func(kernel_func, data, index_arr, start, end, raw):
    return kernel_func(data)


@overload(apply_func, no_unliteral=True)
def overload_apply_func(kernel_func, data, index_arr, start, end, raw):
    assert is_overload_constant_bool(raw), "'raw' should be constant bool"
    if is_overload_true(raw):
        return (lambda kernel_func, data, index_arr, start, end, raw:
            kernel_func(data))
    return lambda kernel_func, data, index_arr, start, end, raw: kernel_func(pd
        .Series(data, index_arr[start:end]))


def fix_index_arr(A):
    return A


@overload(fix_index_arr)
def overload_fix_index_arr(A):
    if is_overload_none(A):
        return lambda A: np.zeros(3)
    return lambda A: A


def get_offset_nanos(w):
    out = status = 0
    try:
        out = pd.tseries.frequencies.to_offset(w).nanos
    except:
        status = 1
    return out, status


def offset_to_nanos(w):
    return w


@overload(offset_to_nanos)
def overload_offset_to_nanos(w):
    if isinstance(w, types.Integer):
        return lambda w: w

    def impl(w):
        with numba.objmode(out='int64', status='int64'):
            out, status = get_offset_nanos(w)
        if status != 0:
            raise ValueError('Invalid offset value')
        return out
    return impl


@register_jitable
def roll_var_linear_generic(in_arr, on_arr_dt, win, minp, center, parallel,
    init_data, add_obs, remove_obs, calc_out):
    _validate_roll_var_args(minp, center)
    in_arr = prep_values(in_arr)
    win = offset_to_nanos(win)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    on_arr = cast_dt64_arr_to_int(on_arr_dt)
    N = len(in_arr)
    left_closed = False
    right_closed = True
    if parallel:
        if _is_small_for_parallel_variable(on_arr, win):
            return _handle_small_data_variable(in_arr, on_arr, win, minp,
                rank, n_pes, init_data, add_obs, remove_obs, calc_out)
        wwbaq__mbjhn = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, ceia__yvmng, l_recv_req,
            numg__xuif) = wwbaq__mbjhn
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start,
        end, init_data, add_obs, remove_obs, calc_out)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(ceia__yvmng, ceia__yvmng, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(numg__xuif, True)
            num_zero_starts = 0
            for czy__xkl in range(0, N):
                if start[czy__xkl] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            data = init_data()
            for cjyb__bcpqz in range(recv_starts[0], len(l_recv_t_buff)):
                data = add_obs(l_recv_buff[cjyb__bcpqz], *data)
            if right_closed:
                data = add_obs(in_arr[0], *data)
            output[0] = calc_out(minp, *data)
            for czy__xkl in range(1, num_zero_starts):
                s = recv_starts[czy__xkl]
                vjmn__snnvf = end[czy__xkl]
                for cjyb__bcpqz in range(recv_starts[czy__xkl - 1], s):
                    data = remove_obs(l_recv_buff[cjyb__bcpqz], *data)
                for cjyb__bcpqz in range(end[czy__xkl - 1], vjmn__snnvf):
                    data = add_obs(in_arr[cjyb__bcpqz], *data)
                output[czy__xkl] = calc_out(minp, *data)
    return output


@register_jitable(cache=True)
def _get_var_recv_starts(on_arr, l_recv_t_buff, num_zero_starts, win):
    recv_starts = np.zeros(num_zero_starts, np.int64)
    halo_size = len(l_recv_t_buff)
    meqzt__zvjjn = cast_dt64_arr_to_int(on_arr)
    left_closed = False
    opqo__qwtfm = meqzt__zvjjn[0] - win
    if left_closed:
        opqo__qwtfm -= 1
    recv_starts[0] = halo_size
    for cjyb__bcpqz in range(0, halo_size):
        if l_recv_t_buff[cjyb__bcpqz] > opqo__qwtfm:
            recv_starts[0] = cjyb__bcpqz
            break
    for czy__xkl in range(1, num_zero_starts):
        opqo__qwtfm = meqzt__zvjjn[czy__xkl] - win
        if left_closed:
            opqo__qwtfm -= 1
        recv_starts[czy__xkl] = halo_size
        for cjyb__bcpqz in range(recv_starts[czy__xkl - 1], halo_size):
            if l_recv_t_buff[cjyb__bcpqz] > opqo__qwtfm:
                recv_starts[czy__xkl] = cjyb__bcpqz
                break
    return recv_starts


@register_jitable
def roll_var_linear_generic_seq(in_arr, on_arr, win, minp, start, end,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    output = np.empty(N, np.float64)
    data = init_data()
    for cjyb__bcpqz in range(start[0], end[0]):
        data = add_obs(in_arr[cjyb__bcpqz], *data)
    output[0] = calc_out(minp, *data)
    for czy__xkl in range(1, N):
        s = start[czy__xkl]
        vjmn__snnvf = end[czy__xkl]
        for cjyb__bcpqz in range(start[czy__xkl - 1], s):
            data = remove_obs(in_arr[cjyb__bcpqz], *data)
        for cjyb__bcpqz in range(end[czy__xkl - 1], vjmn__snnvf):
            data = add_obs(in_arr[cjyb__bcpqz], *data)
        output[czy__xkl] = calc_out(minp, *data)
    return output


def roll_variable_apply(in_arr, on_arr_dt, index_arr, win, minp, center,
    parallel, kernel_func, raw=True):
    pass


@overload(roll_variable_apply, no_unliteral=True)
def overload_roll_variable_apply(in_arr, on_arr_dt, index_arr, win, minp,
    center, parallel, kernel_func, raw=True):
    assert is_overload_constant_bool(raw)
    return roll_variable_apply_impl


def roll_variable_apply_impl(in_arr, on_arr_dt, index_arr, win, minp,
    center, parallel, kernel_func, raw=True):
    _validate_roll_var_args(minp, center)
    in_arr = prep_values(in_arr)
    win = offset_to_nanos(win)
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    on_arr = cast_dt64_arr_to_int(on_arr_dt)
    index_arr = fix_index_arr(index_arr)
    N = len(in_arr)
    left_closed = False
    right_closed = True
    if parallel:
        if _is_small_for_parallel_variable(on_arr, win):
            return _handle_small_data_variable_apply(in_arr, on_arr,
                index_arr, win, minp, rank, n_pes, kernel_func, raw)
        wwbaq__mbjhn = _border_icomm_var(in_arr, on_arr, rank, n_pes, win)
        (l_recv_buff, l_recv_t_buff, r_send_req, ceia__yvmng, l_recv_req,
            numg__xuif) = wwbaq__mbjhn
        if raw == False:
            vvswc__cek = _border_icomm_var(index_arr, on_arr, rank, n_pes, win)
            (l_recv_buff_idx, wfgf__xhum, yfwdv__eml, sslu__opc, kal__rrter,
                dehni__eybm) = vvswc__cek
    start, end = _build_indexer(on_arr, N, win, left_closed, right_closed)
    output = roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
        start, end, kernel_func, raw)
    if parallel:
        _border_send_wait(r_send_req, r_send_req, rank, n_pes, True, False)
        _border_send_wait(ceia__yvmng, ceia__yvmng, rank, n_pes, True, False)
        if raw == False:
            _border_send_wait(yfwdv__eml, yfwdv__eml, rank, n_pes, True, False)
            _border_send_wait(sslu__opc, sslu__opc, rank, n_pes, True, False)
        if rank != 0:
            bodo.libs.distributed_api.wait(l_recv_req, True)
            bodo.libs.distributed_api.wait(numg__xuif, True)
            if raw == False:
                bodo.libs.distributed_api.wait(kal__rrter, True)
                bodo.libs.distributed_api.wait(dehni__eybm, True)
            num_zero_starts = 0
            for czy__xkl in range(0, N):
                if start[czy__xkl] != 0:
                    break
                num_zero_starts += 1
            if num_zero_starts == 0:
                return output
            recv_starts = _get_var_recv_starts(on_arr, l_recv_t_buff,
                num_zero_starts, win)
            recv_left_var_compute(output, in_arr, index_arr,
                num_zero_starts, recv_starts, l_recv_buff, l_recv_buff_idx,
                minp, kernel_func, raw)
    return output


def recv_left_var_compute(output, in_arr, index_arr, num_zero_starts,
    recv_starts, l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
    pass


@overload(recv_left_var_compute)
def overload_recv_left_var_compute(output, in_arr, index_arr,
    num_zero_starts, recv_starts, l_recv_buff, l_recv_buff_idx, minp,
    kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):

        def impl(output, in_arr, index_arr, num_zero_starts, recv_starts,
            l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
            for czy__xkl in range(0, num_zero_starts):
                pgtnd__qau = recv_starts[czy__xkl]
                xmo__qjri = np.concatenate((l_recv_buff[pgtnd__qau:],
                    in_arr[:czy__xkl + 1]))
                if len(xmo__qjri) - np.isnan(xmo__qjri).sum() >= minp:
                    output[czy__xkl] = kernel_func(xmo__qjri)
                else:
                    output[czy__xkl] = np.nan
        return impl

    def impl_series(output, in_arr, index_arr, num_zero_starts, recv_starts,
        l_recv_buff, l_recv_buff_idx, minp, kernel_func, raw):
        for czy__xkl in range(0, num_zero_starts):
            pgtnd__qau = recv_starts[czy__xkl]
            xmo__qjri = np.concatenate((l_recv_buff[pgtnd__qau:], in_arr[:
                czy__xkl + 1]))
            xgsde__nfy = np.concatenate((l_recv_buff_idx[pgtnd__qau:],
                index_arr[:czy__xkl + 1]))
            if len(xmo__qjri) - np.isnan(xmo__qjri).sum() >= minp:
                output[czy__xkl] = kernel_func(pd.Series(xmo__qjri, xgsde__nfy)
                    )
            else:
                output[czy__xkl] = np.nan
    return impl_series


def roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp, start,
    end, kernel_func, raw):
    pass


@overload(roll_variable_apply_seq)
def overload_roll_variable_apply_seq(in_arr, on_arr, index_arr, win, minp,
    start, end, kernel_func, raw):
    assert is_overload_constant_bool(raw)
    if is_overload_true(raw):
        return roll_variable_apply_seq_impl
    return roll_variable_apply_seq_impl_series


def roll_variable_apply_seq_impl(in_arr, on_arr, index_arr, win, minp,
    start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for czy__xkl in range(0, N):
        s = start[czy__xkl]
        vjmn__snnvf = end[czy__xkl]
        data = in_arr[s:vjmn__snnvf]
        if vjmn__snnvf - s - np.isnan(data).sum() >= minp:
            output[czy__xkl] = kernel_func(data)
        else:
            output[czy__xkl] = np.nan
    return output


def roll_variable_apply_seq_impl_series(in_arr, on_arr, index_arr, win,
    minp, start, end, kernel_func, raw):
    N = len(in_arr)
    output = np.empty(N, dtype=np.float64)
    for czy__xkl in range(0, N):
        s = start[czy__xkl]
        vjmn__snnvf = end[czy__xkl]
        data = in_arr[s:vjmn__snnvf]
        if vjmn__snnvf - s - np.isnan(data).sum() >= minp:
            output[czy__xkl] = kernel_func(pd.Series(data, index_arr[s:
                vjmn__snnvf]))
        else:
            output[czy__xkl] = np.nan
    return output


@register_jitable(cache=True)
def _build_indexer(on_arr, N, win, left_closed, right_closed):
    meqzt__zvjjn = cast_dt64_arr_to_int(on_arr)
    start = np.empty(N, np.int64)
    end = np.empty(N, np.int64)
    start[0] = 0
    if right_closed:
        end[0] = 1
    else:
        end[0] = 0
    for czy__xkl in range(1, N):
        xgwr__shv = meqzt__zvjjn[czy__xkl]
        opqo__qwtfm = meqzt__zvjjn[czy__xkl] - win
        if left_closed:
            opqo__qwtfm -= 1
        start[czy__xkl] = czy__xkl
        for cjyb__bcpqz in range(start[czy__xkl - 1], czy__xkl):
            if meqzt__zvjjn[cjyb__bcpqz] > opqo__qwtfm:
                start[czy__xkl] = cjyb__bcpqz
                break
        if meqzt__zvjjn[end[czy__xkl - 1]] <= xgwr__shv:
            end[czy__xkl] = czy__xkl + 1
        else:
            end[czy__xkl] = end[czy__xkl - 1]
        if not right_closed:
            end[czy__xkl] -= 1
    return start, end


@register_jitable
def init_data_sum():
    return 0, 0.0


@register_jitable
def add_sum(val, nobs, sum_x):
    if not np.isnan(val):
        nobs += 1
        sum_x += val
    return nobs, sum_x


@register_jitable
def remove_sum(val, nobs, sum_x):
    if not np.isnan(val):
        nobs -= 1
        sum_x -= val
    return nobs, sum_x


@register_jitable
def calc_sum(minp, nobs, sum_x):
    return sum_x if nobs >= minp else np.nan


@register_jitable
def init_data_mean():
    return 0, 0.0, 0


@register_jitable
def add_mean(val, nobs, sum_x, neg_ct):
    if not np.isnan(val):
        nobs += 1
        sum_x += val
        if val < 0:
            neg_ct += 1
    return nobs, sum_x, neg_ct


@register_jitable
def remove_mean(val, nobs, sum_x, neg_ct):
    if not np.isnan(val):
        nobs -= 1
        sum_x -= val
        if val < 0:
            neg_ct -= 1
    return nobs, sum_x, neg_ct


@register_jitable
def calc_mean(minp, nobs, sum_x, neg_ct):
    if nobs >= minp:
        ylv__rsq = sum_x / nobs
        if neg_ct == 0 and ylv__rsq < 0.0:
            ylv__rsq = 0
        elif neg_ct == nobs and ylv__rsq > 0.0:
            ylv__rsq = 0
    else:
        ylv__rsq = np.nan
    return ylv__rsq


@register_jitable
def init_data_var():
    return 0, 0.0, 0.0


@register_jitable
def add_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs += 1
        heo__zmax = val - mean_x
        mean_x += heo__zmax / nobs
        ssqdm_x += (nobs - 1) * heo__zmax ** 2 / nobs
    return nobs, mean_x, ssqdm_x


@register_jitable
def remove_var(val, nobs, mean_x, ssqdm_x):
    if not np.isnan(val):
        nobs -= 1
        if nobs != 0:
            heo__zmax = val - mean_x
            mean_x -= heo__zmax / nobs
            ssqdm_x -= (nobs + 1) * heo__zmax ** 2 / nobs
        else:
            mean_x = 0.0
            ssqdm_x = 0.0
    return nobs, mean_x, ssqdm_x


@register_jitable
def calc_var(minp, nobs, mean_x, ssqdm_x):
    gdzbv__eys = 1.0
    ylv__rsq = np.nan
    if nobs >= minp and nobs > gdzbv__eys:
        if nobs == 1:
            ylv__rsq = 0.0
        else:
            ylv__rsq = ssqdm_x / (nobs - gdzbv__eys)
            if ylv__rsq < 0.0:
                ylv__rsq = 0.0
    return ylv__rsq


@register_jitable
def calc_std(minp, nobs, mean_x, ssqdm_x):
    kizor__sbuqt = calc_var(minp, nobs, mean_x, ssqdm_x)
    return np.sqrt(kizor__sbuqt)


@register_jitable
def init_data_count():
    return 0.0,


@register_jitable
def add_count(val, count_x):
    if not np.isnan(val):
        count_x += 1.0
    return count_x,


@register_jitable
def remove_count(val, count_x):
    if not np.isnan(val):
        count_x -= 1.0
    return count_x,


@register_jitable
def calc_count(minp, count_x):
    return count_x


@register_jitable
def calc_count_var(minp, count_x):
    return count_x if count_x >= minp else np.nan


linear_kernels = {'sum': (init_data_sum, add_sum, remove_sum, calc_sum),
    'mean': (init_data_mean, add_mean, remove_mean, calc_mean), 'var': (
    init_data_var, add_var, remove_var, calc_var), 'std': (init_data_var,
    add_var, remove_var, calc_std), 'count': (init_data_count, add_count,
    remove_count, calc_count)}


def shift():
    return


@overload(shift, jit_options={'cache': True})
def shift_overload(in_arr, shift, parallel):
    if not isinstance(parallel, types.Literal):
        return shift_impl


def shift_impl(in_arr, shift, parallel):
    N = len(in_arr)
    in_arr = decode_if_dict_array(in_arr)
    output = alloc_shift(N, in_arr, (-1,))
    send_right = shift > 0
    send_left = shift <= 0
    is_parallel_str = False
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        halo_size = np.int32(abs(shift))
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_shift(in_arr, shift, rank, n_pes)
        wwbaq__mbjhn = _border_icomm(in_arr, rank, n_pes, halo_size,
            send_right, send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            blqh__udhv) = wwbaq__mbjhn
        if send_right and is_str_binary_array(in_arr):
            is_parallel_str = True
            shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
                l_recv_req, l_recv_buff, output)
    shift_seq(in_arr, shift, output, is_parallel_str)
    if parallel:
        if send_right:
            if not is_str_binary_array(in_arr):
                shift_left_recv(r_send_req, l_send_req, rank, n_pes,
                    halo_size, l_recv_req, l_recv_buff, output)
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(blqh__udhv, True)
                for czy__xkl in range(0, halo_size):
                    if bodo.libs.array_kernels.isna(r_recv_buff, czy__xkl):
                        bodo.libs.array_kernels.setna(output, N - halo_size +
                            czy__xkl)
                        continue
                    output[N - halo_size + czy__xkl] = r_recv_buff[czy__xkl]
    return output


@register_jitable(cache=True)
def shift_seq(in_arr, shift, output, is_parallel_str=False):
    N = len(in_arr)
    ukrq__zuj = 1 if shift > 0 else -1
    shift = ukrq__zuj * min(abs(shift), N)
    if shift > 0 and (not is_parallel_str or bodo.get_rank() == 0):
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    start = max(shift, 0)
    end = min(N, N + shift)
    for czy__xkl in range(start, end):
        if bodo.libs.array_kernels.isna(in_arr, czy__xkl - shift):
            bodo.libs.array_kernels.setna(output, czy__xkl)
            continue
        output[czy__xkl] = in_arr[czy__xkl - shift]
    if shift < 0:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    return output


@register_jitable
def shift_left_recv(r_send_req, l_send_req, rank, n_pes, halo_size,
    l_recv_req, l_recv_buff, output):
    _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
    if rank != 0:
        bodo.libs.distributed_api.wait(l_recv_req, True)
        for czy__xkl in range(0, halo_size):
            if bodo.libs.array_kernels.isna(l_recv_buff, czy__xkl):
                bodo.libs.array_kernels.setna(output, czy__xkl)
                continue
            output[czy__xkl] = l_recv_buff[czy__xkl]


def is_str_binary_array(arr):
    return False


@overload(is_str_binary_array)
def overload_is_str_binary_array(arr):
    if arr in [bodo.string_array_type, bodo.binary_array_type]:
        return lambda arr: True
    return lambda arr: False


def is_supported_shift_array_type(arr_type):
    return isinstance(arr_type, types.Array) and (isinstance(arr_type.dtype,
        types.Number) or arr_type.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]) or isinstance(arr_type, (bodo.IntegerArrayType,
        bodo.DecimalArrayType)) or arr_type in (bodo.boolean_array, bodo.
        datetime_date_array_type, bodo.string_array_type, bodo.
        binary_array_type, bodo.dict_str_arr_type)


def pct_change():
    return


@overload(pct_change, jit_options={'cache': True})
def pct_change_overload(in_arr, shift, parallel):
    if not isinstance(parallel, types.Literal):
        return pct_change_impl


def pct_change_impl(in_arr, shift, parallel):
    N = len(in_arr)
    send_right = shift > 0
    send_left = shift <= 0
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        halo_size = np.int32(abs(shift))
        if _is_small_for_parallel(N, halo_size):
            return _handle_small_data_pct_change(in_arr, shift, rank, n_pes)
        wwbaq__mbjhn = _border_icomm(in_arr, rank, n_pes, halo_size,
            send_right, send_left)
        (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
            blqh__udhv) = wwbaq__mbjhn
    output = pct_change_seq(in_arr, shift)
    if parallel:
        if send_right:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, True, False)
            if rank != 0:
                bodo.libs.distributed_api.wait(l_recv_req, True)
                for czy__xkl in range(0, halo_size):
                    rzx__utch = l_recv_buff[czy__xkl]
                    output[czy__xkl] = (in_arr[czy__xkl] - rzx__utch
                        ) / rzx__utch
        else:
            _border_send_wait(r_send_req, l_send_req, rank, n_pes, False, True)
            if rank != n_pes - 1:
                bodo.libs.distributed_api.wait(blqh__udhv, True)
                for czy__xkl in range(0, halo_size):
                    rzx__utch = r_recv_buff[czy__xkl]
                    output[N - halo_size + czy__xkl] = (in_arr[N -
                        halo_size + czy__xkl] - rzx__utch) / rzx__utch
    return output


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_first_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[0]
    assert isinstance(arr.dtype, types.Float)
    gtgh__qkrg = np.nan
    if arr.dtype == types.float32:
        gtgh__qkrg = np.float32('nan')

    def impl(arr):
        for czy__xkl in range(len(arr)):
            if not bodo.libs.array_kernels.isna(arr, czy__xkl):
                return arr[czy__xkl]
        return gtgh__qkrg
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_last_non_na(arr):
    if isinstance(arr.dtype, (types.Integer, types.Boolean)):
        zero = arr.dtype(0)
        return lambda arr: zero if len(arr) == 0 else arr[-1]
    assert isinstance(arr.dtype, types.Float)
    gtgh__qkrg = np.nan
    if arr.dtype == types.float32:
        gtgh__qkrg = np.float32('nan')

    def impl(arr):
        xwit__gazd = len(arr)
        for czy__xkl in range(len(arr)):
            cabic__ghs = xwit__gazd - czy__xkl - 1
            if not bodo.libs.array_kernels.isna(arr, cabic__ghs):
                return arr[cabic__ghs]
        return gtgh__qkrg
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_one_from_arr_dtype(arr):
    one = arr.dtype(1)
    return lambda arr: one


@register_jitable(cache=True)
def pct_change_seq(in_arr, shift):
    N = len(in_arr)
    output = alloc_pct_change(N, in_arr)
    ukrq__zuj = 1 if shift > 0 else -1
    shift = ukrq__zuj * min(abs(shift), N)
    if shift > 0:
        bodo.libs.array_kernels.setna_slice(output, slice(None, shift))
    else:
        bodo.libs.array_kernels.setna_slice(output, slice(shift, None))
    if shift > 0:
        agimx__fna = get_first_non_na(in_arr[:shift])
        scwnf__slrs = get_last_non_na(in_arr[:shift])
    else:
        agimx__fna = get_last_non_na(in_arr[:-shift])
        scwnf__slrs = get_first_non_na(in_arr[:-shift])
    one = get_one_from_arr_dtype(output)
    start = max(shift, 0)
    end = min(N, N + shift)
    for czy__xkl in range(start, end):
        rzx__utch = in_arr[czy__xkl - shift]
        if np.isnan(rzx__utch):
            rzx__utch = agimx__fna
        else:
            agimx__fna = rzx__utch
        val = in_arr[czy__xkl]
        if np.isnan(val):
            val = scwnf__slrs
        else:
            scwnf__slrs = val
        output[czy__xkl] = val / rzx__utch - one
    return output


@register_jitable(cache=True)
def _border_icomm(in_arr, rank, n_pes, halo_size, send_right=True,
    send_left=False):
    cevtb__saag = np.int32(comm_border_tag)
    l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    r_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr, (-1,))
    if send_right and rank != n_pes - 1:
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            halo_size, np.int32(rank + 1), cevtb__saag, True)
    if send_right and rank != 0:
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, halo_size,
            np.int32(rank - 1), cevtb__saag, True)
    if send_left and rank != 0:
        l_send_req = bodo.libs.distributed_api.isend(in_arr[:halo_size],
            halo_size, np.int32(rank - 1), cevtb__saag, True)
    if send_left and rank != n_pes - 1:
        blqh__udhv = bodo.libs.distributed_api.irecv(r_recv_buff, halo_size,
            np.int32(rank + 1), cevtb__saag, True)
    return (l_recv_buff, r_recv_buff, l_send_req, r_send_req, l_recv_req,
        blqh__udhv)


@register_jitable(cache=True)
def _border_icomm_var(in_arr, on_arr, rank, n_pes, win_size):
    cevtb__saag = np.int32(comm_border_tag)
    N = len(on_arr)
    halo_size = N
    end = on_arr[-1]
    for cjyb__bcpqz in range(-2, -N, -1):
        ucgw__rsw = on_arr[cjyb__bcpqz]
        if end - ucgw__rsw >= win_size:
            halo_size = -cjyb__bcpqz
            break
    if rank != n_pes - 1:
        bodo.libs.distributed_api.send(halo_size, np.int32(rank + 1),
            cevtb__saag)
        r_send_req = bodo.libs.distributed_api.isend(in_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), cevtb__saag, True)
        ceia__yvmng = bodo.libs.distributed_api.isend(on_arr[-halo_size:],
            np.int32(halo_size), np.int32(rank + 1), cevtb__saag, True)
    if rank != 0:
        halo_size = bodo.libs.distributed_api.recv(np.int64, np.int32(rank -
            1), cevtb__saag)
        l_recv_buff = bodo.utils.utils.alloc_type(halo_size, in_arr)
        l_recv_req = bodo.libs.distributed_api.irecv(l_recv_buff, np.int32(
            halo_size), np.int32(rank - 1), cevtb__saag, True)
        l_recv_t_buff = np.empty(halo_size, np.int64)
        numg__xuif = bodo.libs.distributed_api.irecv(l_recv_t_buff, np.
            int32(halo_size), np.int32(rank - 1), cevtb__saag, True)
    return (l_recv_buff, l_recv_t_buff, r_send_req, ceia__yvmng, l_recv_req,
        numg__xuif)


@register_jitable
def _border_send_wait(r_send_req, l_send_req, rank, n_pes, right, left):
    if right and rank != n_pes - 1:
        bodo.libs.distributed_api.wait(r_send_req, True)
    if left and rank != 0:
        bodo.libs.distributed_api.wait(l_send_req, True)


@register_jitable
def _is_small_for_parallel(N, halo_size):
    xdtx__nfb = bodo.libs.distributed_api.dist_reduce(int(N <= 2 *
        halo_size + 1), np.int32(Reduce_Type.Sum.value))
    return xdtx__nfb != 0


@register_jitable
def _handle_small_data(in_arr, win, minp, center, rank, n_pes, init_data,
    add_obs, remove_obs, calc_out):
    N = len(in_arr)
    wtwe__rwdu = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.
        int32(Reduce_Type.Sum.value))
    jdhy__fbhxz = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        dlc__cwclz, pbii__bqas = roll_fixed_linear_generic_seq(jdhy__fbhxz,
            win, minp, center, init_data, add_obs, remove_obs, calc_out)
    else:
        dlc__cwclz = np.empty(wtwe__rwdu, np.float64)
    bodo.libs.distributed_api.bcast(dlc__cwclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return dlc__cwclz[start:end]


@register_jitable
def _handle_small_data_apply(in_arr, index_arr, win, minp, center, rank,
    n_pes, kernel_func, raw=True):
    N = len(in_arr)
    wtwe__rwdu = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.
        int32(Reduce_Type.Sum.value))
    jdhy__fbhxz = bodo.libs.distributed_api.gatherv(in_arr)
    aza__mch = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        dlc__cwclz = roll_fixed_apply_seq(jdhy__fbhxz, aza__mch, win, minp,
            center, kernel_func, raw)
    else:
        dlc__cwclz = np.empty(wtwe__rwdu, np.float64)
    bodo.libs.distributed_api.bcast(dlc__cwclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return dlc__cwclz[start:end]


def bcast_n_chars_if_str_binary_arr(arr):
    pass


@overload(bcast_n_chars_if_str_binary_arr)
def overload_bcast_n_chars_if_str_binary_arr(arr):
    if arr in [bodo.binary_array_type, bodo.string_array_type]:

        def impl(arr):
            return bodo.libs.distributed_api.bcast_scalar(np.int64(bodo.
                libs.str_arr_ext.num_total_chars(arr)))
        return impl
    return lambda arr: -1


@register_jitable
def _handle_small_data_shift(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    wtwe__rwdu = bodo.libs.distributed_api.dist_reduce(len(in_arr), np.
        int32(Reduce_Type.Sum.value))
    jdhy__fbhxz = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        dlc__cwclz = alloc_shift(len(jdhy__fbhxz), jdhy__fbhxz, (-1,))
        shift_seq(jdhy__fbhxz, shift, dlc__cwclz)
        ikyr__esmni = bcast_n_chars_if_str_binary_arr(dlc__cwclz)
    else:
        ikyr__esmni = bcast_n_chars_if_str_binary_arr(in_arr)
        dlc__cwclz = alloc_shift(wtwe__rwdu, in_arr, (ikyr__esmni,))
    bodo.libs.distributed_api.bcast(dlc__cwclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return dlc__cwclz[start:end]


@register_jitable
def _handle_small_data_pct_change(in_arr, shift, rank, n_pes):
    N = len(in_arr)
    wtwe__rwdu = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    jdhy__fbhxz = bodo.libs.distributed_api.gatherv(in_arr)
    if rank == 0:
        dlc__cwclz = pct_change_seq(jdhy__fbhxz, shift)
    else:
        dlc__cwclz = alloc_pct_change(wtwe__rwdu, in_arr)
    bodo.libs.distributed_api.bcast(dlc__cwclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return dlc__cwclz[start:end]


def cast_dt64_arr_to_int(arr):
    return arr


@infer_global(cast_dt64_arr_to_int)
class DtArrToIntType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        assert args[0] == types.Array(types.NPDatetime('ns'), 1, 'C') or args[0
            ] == types.Array(types.int64, 1, 'C')
        return signature(types.Array(types.int64, 1, 'C'), *args)


@lower_builtin(cast_dt64_arr_to_int, types.Array(types.NPDatetime('ns'), 1,
    'C'))
@lower_builtin(cast_dt64_arr_to_int, types.Array(types.int64, 1, 'C'))
def lower_cast_dt64_arr_to_int(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@register_jitable
def _is_small_for_parallel_variable(on_arr, win_size):
    if len(on_arr) < 2:
        gwp__wcy = 1
    else:
        start = on_arr[0]
        end = on_arr[-1]
        vunmm__iozh = end - start
        gwp__wcy = int(vunmm__iozh <= win_size)
    xdtx__nfb = bodo.libs.distributed_api.dist_reduce(gwp__wcy, np.int32(
        Reduce_Type.Sum.value))
    return xdtx__nfb != 0


@register_jitable
def _handle_small_data_variable(in_arr, on_arr, win, minp, rank, n_pes,
    init_data, add_obs, remove_obs, calc_out):
    N = len(in_arr)
    wtwe__rwdu = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    jdhy__fbhxz = bodo.libs.distributed_api.gatherv(in_arr)
    facth__rukai = bodo.libs.distributed_api.gatherv(on_arr)
    if rank == 0:
        start, end = _build_indexer(facth__rukai, wtwe__rwdu, win, False, True)
        dlc__cwclz = roll_var_linear_generic_seq(jdhy__fbhxz, facth__rukai,
            win, minp, start, end, init_data, add_obs, remove_obs, calc_out)
    else:
        dlc__cwclz = np.empty(wtwe__rwdu, np.float64)
    bodo.libs.distributed_api.bcast(dlc__cwclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return dlc__cwclz[start:end]


@register_jitable
def _handle_small_data_variable_apply(in_arr, on_arr, index_arr, win, minp,
    rank, n_pes, kernel_func, raw):
    N = len(in_arr)
    wtwe__rwdu = bodo.libs.distributed_api.dist_reduce(N, np.int32(
        Reduce_Type.Sum.value))
    jdhy__fbhxz = bodo.libs.distributed_api.gatherv(in_arr)
    facth__rukai = bodo.libs.distributed_api.gatherv(on_arr)
    aza__mch = bodo.libs.distributed_api.gatherv(index_arr)
    if rank == 0:
        start, end = _build_indexer(facth__rukai, wtwe__rwdu, win, False, True)
        dlc__cwclz = roll_variable_apply_seq(jdhy__fbhxz, facth__rukai,
            aza__mch, win, minp, start, end, kernel_func, raw)
    else:
        dlc__cwclz = np.empty(wtwe__rwdu, np.float64)
    bodo.libs.distributed_api.bcast(dlc__cwclz)
    start = bodo.libs.distributed_api.dist_exscan(N, np.int32(Reduce_Type.
        Sum.value))
    end = start + N
    return dlc__cwclz[start:end]


@register_jitable(cache=True)
def _dropna(arr):
    oviw__uneqk = len(arr)
    gleij__qebyz = oviw__uneqk - np.isnan(arr).sum()
    A = np.empty(gleij__qebyz, arr.dtype)
    zzgbo__ezv = 0
    for czy__xkl in range(oviw__uneqk):
        val = arr[czy__xkl]
        if not np.isnan(val):
            A[zzgbo__ezv] = val
            zzgbo__ezv += 1
    return A


def alloc_shift(n, A, s=None):
    return np.empty(n, A.dtype)


@overload(alloc_shift, no_unliteral=True)
def alloc_shift_overload(n, A, s=None):
    if not isinstance(A, types.Array):
        return lambda n, A, s=None: bodo.utils.utils.alloc_type(n, A, s)
    if isinstance(A.dtype, types.Integer):
        return lambda n, A, s=None: np.empty(n, np.float64)
    return lambda n, A, s=None: np.empty(n, A.dtype)


def alloc_pct_change(n, A):
    return np.empty(n, A.dtype)


@overload(alloc_pct_change, no_unliteral=True)
def alloc_pct_change_overload(n, A):
    if isinstance(A.dtype, types.Integer):
        return lambda n, A: np.empty(n, np.float64)
    return lambda n, A: np.empty(n, A.dtype)


def prep_values(A):
    return A.astype('float64')


@overload(prep_values, no_unliteral=True)
def prep_values_overload(A):
    if A == types.Array(types.float64, 1, 'C'):
        return lambda A: A
    return lambda A: A.astype(np.float64)


@register_jitable
def _validate_roll_fixed_args(win, minp):
    if win < 0:
        raise ValueError('window must be non-negative')
    if minp < 0:
        raise ValueError('min_periods must be >= 0')
    if minp > win:
        raise ValueError('min_periods must be <= window')


@register_jitable
def _validate_roll_var_args(minp, center):
    if minp < 0:
        raise ValueError('min_periods must be >= 0')
    if center:
        raise NotImplementedError(
            'rolling: center is not implemented for datetimelike and offset based windows'
            )
