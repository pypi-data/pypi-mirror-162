import atexit
import datetime
import sys
import time
import warnings
from collections import defaultdict
from decimal import Decimal
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir_utils, types
from numba.core.typing import signature
from numba.core.typing.builtins import IndexValueType
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload, register_jitable
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdist
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType, set_bit_to_arr
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, num_total_chars, pre_alloc_string_array, set_bit_to, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, decode_if_dict_array, is_overload_false, is_overload_none, is_str_arr_type
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, empty_like_type, is_array_typ, numba_to_c_type
ll.add_symbol('dist_get_time', hdist.dist_get_time)
ll.add_symbol('get_time', hdist.get_time)
ll.add_symbol('dist_reduce', hdist.dist_reduce)
ll.add_symbol('dist_arr_reduce', hdist.dist_arr_reduce)
ll.add_symbol('dist_exscan', hdist.dist_exscan)
ll.add_symbol('dist_irecv', hdist.dist_irecv)
ll.add_symbol('dist_isend', hdist.dist_isend)
ll.add_symbol('dist_wait', hdist.dist_wait)
ll.add_symbol('dist_get_item_pointer', hdist.dist_get_item_pointer)
ll.add_symbol('get_dummy_ptr', hdist.get_dummy_ptr)
ll.add_symbol('allgather', hdist.allgather)
ll.add_symbol('oneD_reshape_shuffle', hdist.oneD_reshape_shuffle)
ll.add_symbol('permutation_int', hdist.permutation_int)
ll.add_symbol('permutation_array_index', hdist.permutation_array_index)
ll.add_symbol('c_get_rank', hdist.dist_get_rank)
ll.add_symbol('c_get_size', hdist.dist_get_size)
ll.add_symbol('c_barrier', hdist.barrier)
ll.add_symbol('c_alltoall', hdist.c_alltoall)
ll.add_symbol('c_gather_scalar', hdist.c_gather_scalar)
ll.add_symbol('c_gatherv', hdist.c_gatherv)
ll.add_symbol('c_scatterv', hdist.c_scatterv)
ll.add_symbol('c_allgatherv', hdist.c_allgatherv)
ll.add_symbol('c_bcast', hdist.c_bcast)
ll.add_symbol('c_recv', hdist.dist_recv)
ll.add_symbol('c_send', hdist.dist_send)
mpi_req_numba_type = getattr(types, 'int' + str(8 * hdist.mpi_req_num_bytes))
MPI_ROOT = 0
ANY_SOURCE = np.int32(hdist.ANY_SOURCE)


class Reduce_Type(Enum):
    Sum = 0
    Prod = 1
    Min = 2
    Max = 3
    Argmin = 4
    Argmax = 5
    Or = 6
    Concat = 7
    No_Op = 8


_get_rank = types.ExternalFunction('c_get_rank', types.int32())
_get_size = types.ExternalFunction('c_get_size', types.int32())
_barrier = types.ExternalFunction('c_barrier', types.int32())


@numba.njit
def get_rank():
    return _get_rank()


@numba.njit
def get_size():
    return _get_size()


@numba.njit
def barrier():
    _barrier()


_get_time = types.ExternalFunction('get_time', types.float64())
dist_time = types.ExternalFunction('dist_get_time', types.float64())


@overload(time.time, no_unliteral=True)
def overload_time_time():
    return lambda : _get_time()


@numba.generated_jit(nopython=True)
def get_type_enum(arr):
    arr = arr.instance_type if isinstance(arr, types.TypeRef) else arr
    dtype = arr.dtype
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = bodo.hiframes.pd_categorical_ext.get_categories_int_type(dtype)
    typ_val = numba_to_c_type(dtype)
    return lambda arr: np.int32(typ_val)


INT_MAX = np.iinfo(np.int32).max
_send = types.ExternalFunction('c_send', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def send(val, rank, tag):
    send_arr = np.full(1, val)
    pidzz__bir = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, pidzz__bir, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    pidzz__bir = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, pidzz__bir, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            pidzz__bir = get_type_enum(arr)
            return _isend(arr.ctypes, size, pidzz__bir, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        pidzz__bir = np.int32(numba_to_c_type(arr.dtype))
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            twn__ydx = size + 7 >> 3
            ftsum__ccv = _isend(arr._data.ctypes, size, pidzz__bir, pe, tag,
                cond)
            emzeg__zolvf = _isend(arr._null_bitmap.ctypes, twn__ydx,
                jtzd__tnxa, pe, tag, cond)
            return ftsum__ccv, emzeg__zolvf
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        zde__qop = np.int32(numba_to_c_type(offset_type))
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            kwbbe__mhb = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(kwbbe__mhb, pe, tag - 1)
            twn__ydx = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                zde__qop, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), kwbbe__mhb,
                jtzd__tnxa, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), twn__ydx,
                jtzd__tnxa, pe, tag)
            return None
        return impl_str_arr
    typ_enum = numba_to_c_type(types.uint8)

    def impl_voidptr(arr, size, pe, tag, cond=True):
        return _isend(arr, size, typ_enum, pe, tag, cond)
    return impl_voidptr


_irecv = types.ExternalFunction('dist_irecv', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def irecv(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            pidzz__bir = get_type_enum(arr)
            return _irecv(arr.ctypes, size, pidzz__bir, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        pidzz__bir = np.int32(numba_to_c_type(arr.dtype))
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            twn__ydx = size + 7 >> 3
            ftsum__ccv = _irecv(arr._data.ctypes, size, pidzz__bir, pe, tag,
                cond)
            emzeg__zolvf = _irecv(arr._null_bitmap.ctypes, twn__ydx,
                jtzd__tnxa, pe, tag, cond)
            return ftsum__ccv, emzeg__zolvf
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        zde__qop = np.int32(numba_to_c_type(offset_type))
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            wqhtt__qdg = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            wqhtt__qdg = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        zjp__cca = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {wqhtt__qdg}(size, n_chars)
            bodo.libs.str_arr_ext.move_str_binary_arr_payload(arr, new_arr)

            n_bytes = (size + 7) >> 3
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_offset_ptr(arr),
                size + 1,
                offset_typ_enum,
                pe,
                tag,
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_data_ptr(arr), n_chars, char_typ_enum, pe, tag
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                n_bytes,
                char_typ_enum,
                pe,
                tag,
            )
            return None"""
        vkl__vhvwz = dict()
        exec(zjp__cca, {'bodo': bodo, 'np': np, 'offset_typ_enum': zde__qop,
            'char_typ_enum': jtzd__tnxa}, vkl__vhvwz)
        impl = vkl__vhvwz['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    pidzz__bir = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), pidzz__bir)


@numba.generated_jit(nopython=True)
def gather_scalar(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    data = types.unliteral(data)
    typ_val = numba_to_c_type(data)
    dtype = data

    def gather_scalar_impl(data, allgather=False, warn_if_rep=True, root=
        MPI_ROOT):
        n_pes = bodo.libs.distributed_api.get_size()
        rank = bodo.libs.distributed_api.get_rank()
        send = np.full(1, data, dtype)
        rjsa__olmp = n_pes if rank == root or allgather else 0
        hif__qsf = np.empty(rjsa__olmp, dtype)
        c_gather_scalar(send.ctypes, hif__qsf.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return hif__qsf
    return gather_scalar_impl


c_gather_scalar = types.ExternalFunction('c_gather_scalar', types.void(
    types.voidptr, types.voidptr, types.int32, types.bool_, types.int32))
c_gatherv = types.ExternalFunction('c_gatherv', types.void(types.voidptr,
    types.int32, types.voidptr, types.voidptr, types.voidptr, types.int32,
    types.bool_, types.int32))
c_scatterv = types.ExternalFunction('c_scatterv', types.void(types.voidptr,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.int32))


@intrinsic
def value_to_ptr(typingctx, val_tp=None):

    def codegen(context, builder, sig, args):
        apw__igbj = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], apw__igbj)
        return builder.bitcast(apw__igbj, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        apw__igbj = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(apw__igbj)
    return val_tp(ptr_tp, val_tp), codegen


_dist_reduce = types.ExternalFunction('dist_reduce', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))
_dist_arr_reduce = types.ExternalFunction('dist_arr_reduce', types.void(
    types.voidptr, types.int64, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_reduce(value, reduce_op):
    if isinstance(value, types.Array):
        typ_enum = np.int32(numba_to_c_type(value.dtype))

        def impl_arr(value, reduce_op):
            A = np.ascontiguousarray(value)
            _dist_arr_reduce(A.ctypes, A.size, reduce_op, typ_enum)
            return A
        return impl_arr
    jeh__xwarm = types.unliteral(value)
    if isinstance(jeh__xwarm, IndexValueType):
        jeh__xwarm = jeh__xwarm.val_typ
        asq__wnwx = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            asq__wnwx.append(types.int64)
            asq__wnwx.append(bodo.datetime64ns)
            asq__wnwx.append(bodo.timedelta64ns)
            asq__wnwx.append(bodo.datetime_date_type)
        if jeh__xwarm not in asq__wnwx:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(jeh__xwarm))
    typ_enum = np.int32(numba_to_c_type(jeh__xwarm))

    def impl(value, reduce_op):
        gpju__kwxc = value_to_ptr(value)
        qzn__thwsc = value_to_ptr(value)
        _dist_reduce(gpju__kwxc, qzn__thwsc, reduce_op, typ_enum)
        return load_val_ptr(qzn__thwsc, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    jeh__xwarm = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(jeh__xwarm))
    uzk__ntjtk = jeh__xwarm(0)

    def impl(value, reduce_op):
        gpju__kwxc = value_to_ptr(value)
        qzn__thwsc = value_to_ptr(uzk__ntjtk)
        _dist_exscan(gpju__kwxc, qzn__thwsc, reduce_op, typ_enum)
        return load_val_ptr(qzn__thwsc, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    ztbqa__znk = 0
    iovp__frxhx = 0
    for i in range(len(recv_counts)):
        xiivw__jzfbe = recv_counts[i]
        twn__ydx = recv_counts_nulls[i]
        xlp__uymt = tmp_null_bytes[ztbqa__znk:ztbqa__znk + twn__ydx]
        for pkenv__cel in range(xiivw__jzfbe):
            set_bit_to(null_bitmap_ptr, iovp__frxhx, get_bit(xlp__uymt,
                pkenv__cel))
            iovp__frxhx += 1
        ztbqa__znk += twn__ydx


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            xza__zurap = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                xza__zurap, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            osvt__tmps = data.size
            recv_counts = gather_scalar(np.int32(osvt__tmps), allgather,
                root=root)
            qfa__mxq = recv_counts.sum()
            bgdnz__exssu = empty_like_type(qfa__mxq, data)
            wxw__jlnfd = np.empty(1, np.int32)
            if rank == root or allgather:
                wxw__jlnfd = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(osvt__tmps), bgdnz__exssu.
                ctypes, recv_counts.ctypes, wxw__jlnfd.ctypes, np.int32(
                typ_val), allgather, np.int32(root))
            return bgdnz__exssu.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            bgdnz__exssu = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.str_arr_ext.init_str_arr(bgdnz__exssu)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            bgdnz__exssu = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.binary_arr_ext.init_binary_arr(bgdnz__exssu)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            osvt__tmps = len(data)
            twn__ydx = osvt__tmps + 7 >> 3
            recv_counts = gather_scalar(np.int32(osvt__tmps), allgather,
                root=root)
            qfa__mxq = recv_counts.sum()
            bgdnz__exssu = empty_like_type(qfa__mxq, data)
            wxw__jlnfd = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            adqqi__dvgj = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                wxw__jlnfd = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                adqqi__dvgj = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(osvt__tmps),
                bgdnz__exssu._days_data.ctypes, recv_counts.ctypes,
                wxw__jlnfd.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._seconds_data.ctypes, np.int32(osvt__tmps),
                bgdnz__exssu._seconds_data.ctypes, recv_counts.ctypes,
                wxw__jlnfd.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._microseconds_data.ctypes, np.int32(osvt__tmps),
                bgdnz__exssu._microseconds_data.ctypes, recv_counts.ctypes,
                wxw__jlnfd.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._null_bitmap.ctypes, np.int32(twn__ydx),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                adqqi__dvgj.ctypes, jtzd__tnxa, allgather, np.int32(root))
            copy_gathered_null_bytes(bgdnz__exssu._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return bgdnz__exssu
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            osvt__tmps = len(data)
            twn__ydx = osvt__tmps + 7 >> 3
            recv_counts = gather_scalar(np.int32(osvt__tmps), allgather,
                root=root)
            qfa__mxq = recv_counts.sum()
            bgdnz__exssu = empty_like_type(qfa__mxq, data)
            wxw__jlnfd = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            adqqi__dvgj = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                wxw__jlnfd = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                adqqi__dvgj = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(osvt__tmps), bgdnz__exssu
                ._data.ctypes, recv_counts.ctypes, wxw__jlnfd.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(twn__ydx),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                adqqi__dvgj.ctypes, jtzd__tnxa, allgather, np.int32(root))
            copy_gathered_null_bytes(bgdnz__exssu._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return bgdnz__exssu
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        pderp__tnr = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            ujgp__qgqz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                ujgp__qgqz, pderp__tnr)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            rjfmi__ithef = bodo.gatherv(data._left, allgather, warn_if_rep,
                root)
            znf__cidph = bodo.gatherv(data._right, allgather, warn_if_rep, root
                )
            return bodo.libs.interval_arr_ext.init_interval_array(rjfmi__ithef,
                znf__cidph)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            mmefs__eplij = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            mtaix__ipl = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                mtaix__ipl, mmefs__eplij)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        ozqu__ezk = np.iinfo(np.int64).max
        bduzw__ltq = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ixnmn__tfzzb = data._start
            npjm__wosux = data._stop
            if len(data) == 0:
                ixnmn__tfzzb = ozqu__ezk
                npjm__wosux = bduzw__ltq
            ixnmn__tfzzb = bodo.libs.distributed_api.dist_reduce(ixnmn__tfzzb,
                np.int32(Reduce_Type.Min.value))
            npjm__wosux = bodo.libs.distributed_api.dist_reduce(npjm__wosux,
                np.int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if ixnmn__tfzzb == ozqu__ezk and npjm__wosux == bduzw__ltq:
                ixnmn__tfzzb = 0
                npjm__wosux = 0
            cdgv__jkw = max(0, -(-(npjm__wosux - ixnmn__tfzzb) // data._step))
            if cdgv__jkw < total_len:
                npjm__wosux = ixnmn__tfzzb + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                ixnmn__tfzzb = 0
                npjm__wosux = 0
            return bodo.hiframes.pd_index_ext.init_range_index(ixnmn__tfzzb,
                npjm__wosux, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            ymju__sen = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, ymju__sen)
        else:

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.utils.conversion.index_from_array(arr, data._name)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            bgdnz__exssu = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                bgdnz__exssu, data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        ajrq__ifx = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        zjp__cca = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        zjp__cca += '  T = data\n'
        zjp__cca += '  T2 = init_table(T, True)\n'
        for rmxt__qansr in data.type_to_blk.values():
            ajrq__ifx[f'arr_inds_{rmxt__qansr}'] = np.array(data.
                block_to_arr_ind[rmxt__qansr], dtype=np.int64)
            zjp__cca += (
                f'  arr_list_{rmxt__qansr} = get_table_block(T, {rmxt__qansr})\n'
                )
            zjp__cca += f"""  out_arr_list_{rmxt__qansr} = alloc_list_like(arr_list_{rmxt__qansr}, len(arr_list_{rmxt__qansr}), True)
"""
            zjp__cca += f'  for i in range(len(arr_list_{rmxt__qansr})):\n'
            zjp__cca += (
                f'    arr_ind_{rmxt__qansr} = arr_inds_{rmxt__qansr}[i]\n')
            zjp__cca += f"""    ensure_column_unboxed(T, arr_list_{rmxt__qansr}, i, arr_ind_{rmxt__qansr})
"""
            zjp__cca += f"""    out_arr_{rmxt__qansr} = bodo.gatherv(arr_list_{rmxt__qansr}[i], allgather, warn_if_rep, root)
"""
            zjp__cca += (
                f'    out_arr_list_{rmxt__qansr}[i] = out_arr_{rmxt__qansr}\n')
            zjp__cca += (
                f'  T2 = set_table_block(T2, out_arr_list_{rmxt__qansr}, {rmxt__qansr})\n'
                )
        zjp__cca += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        zjp__cca += f'  T2 = set_table_len(T2, length)\n'
        zjp__cca += f'  return T2\n'
        vkl__vhvwz = {}
        exec(zjp__cca, ajrq__ifx, vkl__vhvwz)
        uci__qoz = vkl__vhvwz['impl_table']
        return uci__qoz
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hng__uytb = len(data.columns)
        if hng__uytb == 0:
            lir__vxj = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                orod__ccjqo = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    orod__ccjqo, lir__vxj)
            return impl
        ezhjf__mnle = ', '.join(f'g_data_{i}' for i in range(hng__uytb))
        zjp__cca = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            mfygm__dym = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            ezhjf__mnle = 'T2'
            zjp__cca += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            zjp__cca += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(hng__uytb):
                zjp__cca += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                zjp__cca += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        zjp__cca += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zjp__cca += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        zjp__cca += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(ezhjf__mnle))
        vkl__vhvwz = {}
        ajrq__ifx = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(zjp__cca, ajrq__ifx, vkl__vhvwz)
        uuej__tmck = vkl__vhvwz['impl_df']
        return uuej__tmck
    if isinstance(data, ArrayItemArrayType):
        owj__kup = np.int32(numba_to_c_type(types.int32))
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            wxnf__tma = bodo.libs.array_item_arr_ext.get_offsets(data)
            fpxd__vhx = bodo.libs.array_item_arr_ext.get_data(data)
            fpxd__vhx = fpxd__vhx[:wxnf__tma[-1]]
            vlpgv__pwjp = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            osvt__tmps = len(data)
            btu__ifu = np.empty(osvt__tmps, np.uint32)
            twn__ydx = osvt__tmps + 7 >> 3
            for i in range(osvt__tmps):
                btu__ifu[i] = wxnf__tma[i + 1] - wxnf__tma[i]
            recv_counts = gather_scalar(np.int32(osvt__tmps), allgather,
                root=root)
            qfa__mxq = recv_counts.sum()
            wxw__jlnfd = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            adqqi__dvgj = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                wxw__jlnfd = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for ymn__fsm in range(len(recv_counts)):
                    recv_counts_nulls[ymn__fsm] = recv_counts[ymn__fsm
                        ] + 7 >> 3
                adqqi__dvgj = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            yylj__cug = np.empty(qfa__mxq + 1, np.uint32)
            alxu__jcfkt = bodo.gatherv(fpxd__vhx, allgather, warn_if_rep, root)
            woe__dbhkq = np.empty(qfa__mxq + 7 >> 3, np.uint8)
            c_gatherv(btu__ifu.ctypes, np.int32(osvt__tmps), yylj__cug.
                ctypes, recv_counts.ctypes, wxw__jlnfd.ctypes, owj__kup,
                allgather, np.int32(root))
            c_gatherv(vlpgv__pwjp.ctypes, np.int32(twn__ydx),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                adqqi__dvgj.ctypes, jtzd__tnxa, allgather, np.int32(root))
            dummy_use(data)
            gqv__twcxl = np.empty(qfa__mxq + 1, np.uint64)
            convert_len_arr_to_offset(yylj__cug.ctypes, gqv__twcxl.ctypes,
                qfa__mxq)
            copy_gathered_null_bytes(woe__dbhkq.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                qfa__mxq, alxu__jcfkt, gqv__twcxl, woe__dbhkq)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        ozwts__ecx = data.names
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ibsgu__cfwi = bodo.libs.struct_arr_ext.get_data(data)
            xnwdq__fgn = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            yhuvu__ydyhj = bodo.gatherv(ibsgu__cfwi, allgather=allgather,
                root=root)
            rank = bodo.libs.distributed_api.get_rank()
            osvt__tmps = len(data)
            twn__ydx = osvt__tmps + 7 >> 3
            recv_counts = gather_scalar(np.int32(osvt__tmps), allgather,
                root=root)
            qfa__mxq = recv_counts.sum()
            cxd__arvha = np.empty(qfa__mxq + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            adqqi__dvgj = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                adqqi__dvgj = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(xnwdq__fgn.ctypes, np.int32(twn__ydx), tmp_null_bytes
                .ctypes, recv_counts_nulls.ctypes, adqqi__dvgj.ctypes,
                jtzd__tnxa, allgather, np.int32(root))
            copy_gathered_null_bytes(cxd__arvha.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(yhuvu__ydyhj,
                cxd__arvha, ozwts__ecx)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            bgdnz__exssu = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.binary_arr_ext.init_binary_arr(bgdnz__exssu)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            bgdnz__exssu = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(bgdnz__exssu)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            bgdnz__exssu = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.map_arr_ext.init_map_arr(bgdnz__exssu)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            bgdnz__exssu = bodo.gatherv(data.data, allgather, warn_if_rep, root
                )
            svvg__mfeam = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            mgoo__zrcxy = bodo.gatherv(data.indptr, allgather, warn_if_rep,
                root)
            car__ekbpw = gather_scalar(data.shape[0], allgather, root=root)
            bhdr__ywgje = car__ekbpw.sum()
            hng__uytb = bodo.libs.distributed_api.dist_reduce(data.shape[1],
                np.int32(Reduce_Type.Max.value))
            azai__vcscs = np.empty(bhdr__ywgje + 1, np.int64)
            svvg__mfeam = svvg__mfeam.astype(np.int64)
            azai__vcscs[0] = 0
            ylmrt__atio = 1
            zur__ahc = 0
            for huahi__ewnlo in car__ekbpw:
                for yxh__szn in range(huahi__ewnlo):
                    qcmee__cwm = mgoo__zrcxy[zur__ahc + 1] - mgoo__zrcxy[
                        zur__ahc]
                    azai__vcscs[ylmrt__atio] = azai__vcscs[ylmrt__atio - 1
                        ] + qcmee__cwm
                    ylmrt__atio += 1
                    zur__ahc += 1
                zur__ahc += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(bgdnz__exssu,
                svvg__mfeam, azai__vcscs, (bhdr__ywgje, hng__uytb))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        zjp__cca = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        zjp__cca += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        vkl__vhvwz = {}
        exec(zjp__cca, {'bodo': bodo}, vkl__vhvwz)
        ufuc__dffla = vkl__vhvwz['impl_tuple']
        return ufuc__dffla
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    zjp__cca = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    zjp__cca += '    if random:\n'
    zjp__cca += '        if random_seed is None:\n'
    zjp__cca += '            random = 1\n'
    zjp__cca += '        else:\n'
    zjp__cca += '            random = 2\n'
    zjp__cca += '    if random_seed is None:\n'
    zjp__cca += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        tejuo__tsnnp = data
        hng__uytb = len(tejuo__tsnnp.columns)
        for i in range(hng__uytb):
            zjp__cca += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        zjp__cca += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        ezhjf__mnle = ', '.join(f'data_{i}' for i in range(hng__uytb))
        zjp__cca += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(pnsp__zaf) for
            pnsp__zaf in range(hng__uytb))))
        zjp__cca += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        zjp__cca += '    if dests is None:\n'
        zjp__cca += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zjp__cca += '    else:\n'
        zjp__cca += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for sjogu__qcg in range(hng__uytb):
            zjp__cca += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(sjogu__qcg))
        zjp__cca += (
            '    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
            .format(hng__uytb))
        zjp__cca += '    delete_table(out_table)\n'
        zjp__cca += '    if parallel:\n'
        zjp__cca += '        delete_table(table_total)\n'
        ezhjf__mnle = ', '.join('out_arr_{}'.format(i) for i in range(
            hng__uytb))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        zjp__cca += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(ezhjf__mnle, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        zjp__cca += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        zjp__cca += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        zjp__cca += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        zjp__cca += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        zjp__cca += '    if dests is None:\n'
        zjp__cca += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zjp__cca += '    else:\n'
        zjp__cca += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        zjp__cca += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        zjp__cca += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        zjp__cca += '    delete_table(out_table)\n'
        zjp__cca += '    if parallel:\n'
        zjp__cca += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        zjp__cca += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        zjp__cca += '    if not parallel:\n'
        zjp__cca += '        return data\n'
        zjp__cca += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        zjp__cca += '    if dests is None:\n'
        zjp__cca += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        zjp__cca += '    elif bodo.get_rank() not in dests:\n'
        zjp__cca += '        dim0_local_size = 0\n'
        zjp__cca += '    else:\n'
        zjp__cca += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        zjp__cca += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        zjp__cca += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        zjp__cca += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        zjp__cca += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        zjp__cca += '    if dests is None:\n'
        zjp__cca += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        zjp__cca += '    else:\n'
        zjp__cca += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        zjp__cca += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        zjp__cca += '    delete_table(out_table)\n'
        zjp__cca += '    if parallel:\n'
        zjp__cca += '        delete_table(table_total)\n'
        zjp__cca += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    vkl__vhvwz = {}
    ajrq__ifx = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ajrq__ifx.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(tejuo__tsnnp.columns)})
    exec(zjp__cca, ajrq__ifx, vkl__vhvwz)
    impl = vkl__vhvwz['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    zjp__cca = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        zjp__cca += '    if seed is None:\n'
        zjp__cca += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        zjp__cca += '    np.random.seed(seed)\n'
        zjp__cca += '    if not parallel:\n'
        zjp__cca += '        data = data.copy()\n'
        zjp__cca += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            zjp__cca += '        data = data[:n_samples]\n'
        zjp__cca += '        return data\n'
        zjp__cca += '    else:\n'
        zjp__cca += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        zjp__cca += '        permutation = np.arange(dim0_global_size)\n'
        zjp__cca += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            zjp__cca += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            zjp__cca += '        n_samples = dim0_global_size\n'
        zjp__cca += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        zjp__cca += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        zjp__cca += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        zjp__cca += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        zjp__cca += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        zjp__cca += '        return output\n'
    else:
        zjp__cca += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            zjp__cca += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            zjp__cca += '    output = output[:local_n_samples]\n'
        zjp__cca += '    return output\n'
    vkl__vhvwz = {}
    exec(zjp__cca, {'np': np, 'bodo': bodo}, vkl__vhvwz)
    impl = vkl__vhvwz['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    lpayw__xgem = np.empty(sendcounts_nulls.sum(), np.uint8)
    ztbqa__znk = 0
    iovp__frxhx = 0
    for trpo__trf in range(len(sendcounts)):
        xiivw__jzfbe = sendcounts[trpo__trf]
        twn__ydx = sendcounts_nulls[trpo__trf]
        xlp__uymt = lpayw__xgem[ztbqa__znk:ztbqa__znk + twn__ydx]
        for pkenv__cel in range(xiivw__jzfbe):
            set_bit_to_arr(xlp__uymt, pkenv__cel, get_bit_bitmap(
                null_bitmap_ptr, iovp__frxhx))
            iovp__frxhx += 1
        ztbqa__znk += twn__ydx
    return lpayw__xgem


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    ijpen__laxy = MPI.COMM_WORLD
    data = ijpen__laxy.bcast(data, root)
    return data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_scatterv_send_counts(send_counts, n_pes, n):
    if not is_overload_none(send_counts):
        return lambda send_counts, n_pes, n: send_counts

    def impl(send_counts, n_pes, n):
        send_counts = np.empty(n_pes, np.int32)
        for i in range(n_pes):
            send_counts[i] = get_node_portion(n, n_pes, i)
        return send_counts
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _scatterv_np(data, send_counts=None, warn_if_dist=True):
    typ_val = numba_to_c_type(data.dtype)
    rpv__mjo = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    gmf__gywj = (0,) * rpv__mjo

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        thk__nsu = np.ascontiguousarray(data)
        mjxf__urva = data.ctypes
        vehuh__djdwo = gmf__gywj
        if rank == MPI_ROOT:
            vehuh__djdwo = thk__nsu.shape
        vehuh__djdwo = bcast_tuple(vehuh__djdwo)
        nsy__suhci = get_tuple_prod(vehuh__djdwo[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            vehuh__djdwo[0])
        send_counts *= nsy__suhci
        osvt__tmps = send_counts[rank]
        xyy__puz = np.empty(osvt__tmps, dtype)
        wxw__jlnfd = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(mjxf__urva, send_counts.ctypes, wxw__jlnfd.ctypes,
            xyy__puz.ctypes, np.int32(osvt__tmps), np.int32(typ_val))
        return xyy__puz.reshape((-1,) + vehuh__djdwo[1:])
    return scatterv_arr_impl


def _get_name_value_for_type(name_typ):
    assert isinstance(name_typ, (types.UnicodeType, types.StringLiteral)
        ) or name_typ == types.none
    return None if name_typ == types.none else '_' + str(ir_utils.next_label())


def get_value_for_type(dtype):
    if isinstance(dtype, types.Array):
        return np.zeros((1,) * dtype.ndim, numba.np.numpy_support.as_dtype(
            dtype.dtype))
    if dtype == string_array_type:
        return pd.array(['A'], 'string')
    if dtype == bodo.dict_str_arr_type:
        import pyarrow as pa
        return pa.array(['a'], type=pa.dictionary(pa.int32(), pa.string()))
    if dtype == binary_array_type:
        return np.array([b'A'], dtype=object)
    if isinstance(dtype, IntegerArrayType):
        kfwed__xsui = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], kfwed__xsui)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        mmefs__eplij = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=mmefs__eplij)
        mxp__nolx = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(mxp__nolx)
        return pd.Index(arr, name=mmefs__eplij)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        mmefs__eplij = _get_name_value_for_type(dtype.name_typ)
        ozwts__ecx = tuple(_get_name_value_for_type(t) for t in dtype.names_typ
            )
        rcew__nmk = tuple(get_value_for_type(t) for t in dtype.array_types)
        rcew__nmk = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in rcew__nmk)
        val = pd.MultiIndex.from_arrays(rcew__nmk, names=ozwts__ecx)
        val.name = mmefs__eplij
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        mmefs__eplij = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=mmefs__eplij)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        rcew__nmk = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({mmefs__eplij: arr for mmefs__eplij, arr in zip
            (dtype.columns, rcew__nmk)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        mxp__nolx = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(mxp__nolx[0], mxp__nolx
            [0])])
    raise BodoError(f'get_value_for_type(dtype): Missing data type {dtype}')


def scatterv(data, send_counts=None, warn_if_dist=True):
    rank = bodo.libs.distributed_api.get_rank()
    if rank != MPI_ROOT and data is not None:
        warnings.warn(BodoWarning(
            "bodo.scatterv(): A non-None value for 'data' was found on a rank other than the root. This data won't be sent to any other ranks and will be overwritten with data from rank 0."
            ))
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return scatterv_impl(data, send_counts)


@overload(scatterv)
def scatterv_overload(data, send_counts=None, warn_if_dist=True):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.scatterv()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.scatterv()')
    return lambda data, send_counts=None, warn_if_dist=True: scatterv_impl(data
        , send_counts)


@numba.generated_jit(nopython=True)
def scatterv_impl(data, send_counts=None, warn_if_dist=True):
    if isinstance(data, types.Array):
        return lambda data, send_counts=None, warn_if_dist=True: _scatterv_np(
            data, send_counts)
    if is_str_arr_type(data) or data == binary_array_type:
        owj__kup = np.int32(numba_to_c_type(types.int32))
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            wqhtt__qdg = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            wqhtt__qdg = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        zjp__cca = f"""def impl(
            data, send_counts=None, warn_if_dist=True
        ):  # pragma: no cover
            data = decode_if_dict_array(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            n_all = bodo.libs.distributed_api.bcast_scalar(len(data))

            # convert offsets to lengths of strings
            send_arr_lens = np.empty(
                len(data), np.uint32
            )  # XXX offset type is offset_type, lengths for comm are uint32
            for i in range(len(data)):
                send_arr_lens[i] = bodo.libs.str_arr_ext.get_str_arr_item_length(
                    data, i
                )

            # ------- calculate buffer counts -------

            send_counts = bodo.libs.distributed_api._get_scatterv_send_counts(send_counts, n_pes, n_all)

            # displacements
            displs = bodo.ir.join.calc_disp(send_counts)

            # compute send counts for characters
            send_counts_char = np.empty(n_pes, np.int32)
            if rank == 0:
                curr_str = 0
                for i in range(n_pes):
                    c = 0
                    for _ in range(send_counts[i]):
                        c += send_arr_lens[curr_str]
                        curr_str += 1
                    send_counts_char[i] = c

            bodo.libs.distributed_api.bcast(send_counts_char)

            # displacements for characters
            displs_char = bodo.ir.join.calc_disp(send_counts_char)

            # compute send counts for nulls
            send_counts_nulls = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                send_counts_nulls[i] = (send_counts[i] + 7) >> 3

            # displacements for nulls
            displs_nulls = bodo.ir.join.calc_disp(send_counts_nulls)

            # alloc output array
            n_loc = send_counts[rank]  # total number of elements on this PE
            n_loc_char = send_counts_char[rank]
            recv_arr = {wqhtt__qdg}(n_loc, n_loc_char)

            # ----- string lengths -----------

            recv_lens = np.empty(n_loc, np.uint32)
            bodo.libs.distributed_api.c_scatterv(
                send_arr_lens.ctypes,
                send_counts.ctypes,
                displs.ctypes,
                recv_lens.ctypes,
                np.int32(n_loc),
                int32_typ_enum,
            )

            # TODO: don't hardcode offset type. Also, if offset is 32 bit we can
            # use the same buffer
            bodo.libs.str_arr_ext.convert_len_arr_to_offset(recv_lens.ctypes, bodo.libs.str_arr_ext.get_offset_ptr(recv_arr), n_loc)

            # ----- string characters -----------

            bodo.libs.distributed_api.c_scatterv(
                bodo.libs.str_arr_ext.get_data_ptr(data),
                send_counts_char.ctypes,
                displs_char.ctypes,
                bodo.libs.str_arr_ext.get_data_ptr(recv_arr),
                np.int32(n_loc_char),
                char_typ_enum,
            )

            # ----------- null bitmap -------------

            n_recv_bytes = (n_loc + 7) >> 3

            send_null_bitmap = bodo.libs.distributed_api.get_scatter_null_bytes_buff(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(data), send_counts, send_counts_nulls
            )

            bodo.libs.distributed_api.c_scatterv(
                send_null_bitmap.ctypes,
                send_counts_nulls.ctypes,
                displs_nulls.ctypes,
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(recv_arr),
                np.int32(n_recv_bytes),
                char_typ_enum,
            )

            return recv_arr"""
        vkl__vhvwz = dict()
        exec(zjp__cca, {'bodo': bodo, 'np': np, 'int32_typ_enum': owj__kup,
            'char_typ_enum': jtzd__tnxa, 'decode_if_dict_array':
            decode_if_dict_array}, vkl__vhvwz)
        impl = vkl__vhvwz['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        owj__kup = np.int32(numba_to_c_type(types.int32))
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            vzosz__fof = bodo.libs.array_item_arr_ext.get_offsets(data)
            lgg__kjbh = bodo.libs.array_item_arr_ext.get_data(data)
            lgg__kjbh = lgg__kjbh[:vzosz__fof[-1]]
            kdc__zaqxi = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            axl__fdw = bcast_scalar(len(data))
            endl__htzaz = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                endl__htzaz[i] = vzosz__fof[i + 1] - vzosz__fof[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                axl__fdw)
            wxw__jlnfd = bodo.ir.join.calc_disp(send_counts)
            ulh__tmdd = np.empty(n_pes, np.int32)
            if rank == 0:
                lxcf__abc = 0
                for i in range(n_pes):
                    cmhk__fei = 0
                    for yxh__szn in range(send_counts[i]):
                        cmhk__fei += endl__htzaz[lxcf__abc]
                        lxcf__abc += 1
                    ulh__tmdd[i] = cmhk__fei
            bcast(ulh__tmdd)
            rbwdg__eiyaa = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                rbwdg__eiyaa[i] = send_counts[i] + 7 >> 3
            adqqi__dvgj = bodo.ir.join.calc_disp(rbwdg__eiyaa)
            osvt__tmps = send_counts[rank]
            zgnix__gmmv = np.empty(osvt__tmps + 1, np_offset_type)
            oske__vrojf = bodo.libs.distributed_api.scatterv_impl(lgg__kjbh,
                ulh__tmdd)
            vdnhz__ihxwi = osvt__tmps + 7 >> 3
            krea__lle = np.empty(vdnhz__ihxwi, np.uint8)
            uotkr__eeqb = np.empty(osvt__tmps, np.uint32)
            c_scatterv(endl__htzaz.ctypes, send_counts.ctypes, wxw__jlnfd.
                ctypes, uotkr__eeqb.ctypes, np.int32(osvt__tmps), owj__kup)
            convert_len_arr_to_offset(uotkr__eeqb.ctypes, zgnix__gmmv.
                ctypes, osvt__tmps)
            qkxi__hgi = get_scatter_null_bytes_buff(kdc__zaqxi.ctypes,
                send_counts, rbwdg__eiyaa)
            c_scatterv(qkxi__hgi.ctypes, rbwdg__eiyaa.ctypes, adqqi__dvgj.
                ctypes, krea__lle.ctypes, np.int32(vdnhz__ihxwi), jtzd__tnxa)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                osvt__tmps, oske__vrojf, zgnix__gmmv, krea__lle)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            ksh__axekl = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            ksh__axekl = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            ksh__axekl = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            ksh__axekl = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            thk__nsu = data._data
            xnwdq__fgn = data._null_bitmap
            msvay__nvw = len(thk__nsu)
            ruglm__two = _scatterv_np(thk__nsu, send_counts)
            axl__fdw = bcast_scalar(msvay__nvw)
            ncmj__ach = len(ruglm__two) + 7 >> 3
            lroo__voiec = np.empty(ncmj__ach, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                axl__fdw)
            rbwdg__eiyaa = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                rbwdg__eiyaa[i] = send_counts[i] + 7 >> 3
            adqqi__dvgj = bodo.ir.join.calc_disp(rbwdg__eiyaa)
            qkxi__hgi = get_scatter_null_bytes_buff(xnwdq__fgn.ctypes,
                send_counts, rbwdg__eiyaa)
            c_scatterv(qkxi__hgi.ctypes, rbwdg__eiyaa.ctypes, adqqi__dvgj.
                ctypes, lroo__voiec.ctypes, np.int32(ncmj__ach), jtzd__tnxa)
            return ksh__axekl(ruglm__two, lroo__voiec)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            tnyn__zcae = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            tof__obduv = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(tnyn__zcae,
                tof__obduv)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            ixnmn__tfzzb = data._start
            npjm__wosux = data._stop
            vhz__raywj = data._step
            mmefs__eplij = data._name
            mmefs__eplij = bcast_scalar(mmefs__eplij)
            ixnmn__tfzzb = bcast_scalar(ixnmn__tfzzb)
            npjm__wosux = bcast_scalar(npjm__wosux)
            vhz__raywj = bcast_scalar(vhz__raywj)
            xmksd__vqzm = bodo.libs.array_kernels.calc_nitems(ixnmn__tfzzb,
                npjm__wosux, vhz__raywj)
            chunk_start = bodo.libs.distributed_api.get_start(xmksd__vqzm,
                n_pes, rank)
            drxu__lkygp = bodo.libs.distributed_api.get_node_portion(
                xmksd__vqzm, n_pes, rank)
            lkcyy__cwmh = ixnmn__tfzzb + vhz__raywj * chunk_start
            cgdl__wslus = ixnmn__tfzzb + vhz__raywj * (chunk_start +
                drxu__lkygp)
            cgdl__wslus = min(cgdl__wslus, npjm__wosux)
            return bodo.hiframes.pd_index_ext.init_range_index(lkcyy__cwmh,
                cgdl__wslus, vhz__raywj, mmefs__eplij)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        ymju__sen = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            thk__nsu = data._data
            mmefs__eplij = data._name
            mmefs__eplij = bcast_scalar(mmefs__eplij)
            arr = bodo.libs.distributed_api.scatterv_impl(thk__nsu, send_counts
                )
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                mmefs__eplij, ymju__sen)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            thk__nsu = data._data
            mmefs__eplij = data._name
            mmefs__eplij = bcast_scalar(mmefs__eplij)
            arr = bodo.libs.distributed_api.scatterv_impl(thk__nsu, send_counts
                )
            return bodo.utils.conversion.index_from_array(arr, mmefs__eplij)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            bgdnz__exssu = bodo.libs.distributed_api.scatterv_impl(data.
                _data, send_counts)
            mmefs__eplij = bcast_scalar(data._name)
            ozwts__ecx = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                bgdnz__exssu, ozwts__ecx, mmefs__eplij)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            mmefs__eplij = bodo.hiframes.pd_series_ext.get_series_name(data)
            wqnf__abc = bcast_scalar(mmefs__eplij)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            mtaix__ipl = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                mtaix__ipl, wqnf__abc)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hng__uytb = len(data.columns)
        ezhjf__mnle = ', '.join('g_data_{}'.format(i) for i in range(hng__uytb)
            )
        xncz__vludu = ColNamesMetaType(data.columns)
        zjp__cca = 'def impl_df(data, send_counts=None, warn_if_dist=True):\n'
        for i in range(hng__uytb):
            zjp__cca += (
                '  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})\n'
                .format(i, i))
            zjp__cca += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        zjp__cca += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zjp__cca += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        zjp__cca += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({ezhjf__mnle},), g_index, __col_name_meta_scaterv_impl)
"""
        vkl__vhvwz = {}
        exec(zjp__cca, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            xncz__vludu}, vkl__vhvwz)
        uuej__tmck = vkl__vhvwz['impl_df']
        return uuej__tmck
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            xza__zurap = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                xza__zurap, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        zjp__cca = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        zjp__cca += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        vkl__vhvwz = {}
        exec(zjp__cca, {'bodo': bodo}, vkl__vhvwz)
        ufuc__dffla = vkl__vhvwz['impl_tuple']
        return ufuc__dffla
    if data is types.none:
        return lambda data, send_counts=None, warn_if_dist=True: None
    raise BodoError('scatterv() not available for {}'.format(data))


@intrinsic
def cptr_to_voidptr(typingctx, cptr_tp=None):

    def codegen(context, builder, sig, args):
        return builder.bitcast(args[0], lir.IntType(8).as_pointer())
    return types.voidptr(cptr_tp), codegen


def bcast(data, root=MPI_ROOT):
    return


@overload(bcast, no_unliteral=True)
def bcast_overload(data, root=MPI_ROOT):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.bcast()')
    if isinstance(data, types.Array):

        def bcast_impl(data, root=MPI_ROOT):
            typ_enum = get_type_enum(data)
            count = data.size
            assert count < INT_MAX
            c_bcast(data.ctypes, np.int32(count), typ_enum, np.array([-1]).
                ctypes, 0, np.int32(root))
            return
        return bcast_impl
    if isinstance(data, DecimalArrayType):

        def bcast_decimal_arr(data, root=MPI_ROOT):
            count = data._data.size
            assert count < INT_MAX
            c_bcast(data._data.ctypes, np.int32(count), CTypeEnum.Int128.
                value, np.array([-1]).ctypes, 0, np.int32(root))
            bcast(data._null_bitmap, root)
            return
        return bcast_decimal_arr
    if isinstance(data, IntegerArrayType) or data in (boolean_array,
        datetime_date_array_type):

        def bcast_impl_int_arr(data, root=MPI_ROOT):
            bcast(data._data, root)
            bcast(data._null_bitmap, root)
            return
        return bcast_impl_int_arr
    if is_str_arr_type(data) or data == binary_array_type:
        zde__qop = np.int32(numba_to_c_type(offset_type))
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            osvt__tmps = len(data)
            zbw__hqjys = num_total_chars(data)
            assert osvt__tmps < INT_MAX
            assert zbw__hqjys < INT_MAX
            mgc__lxwxw = get_offset_ptr(data)
            mjxf__urva = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            twn__ydx = osvt__tmps + 7 >> 3
            c_bcast(mgc__lxwxw, np.int32(osvt__tmps + 1), zde__qop, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(mjxf__urva, np.int32(zbw__hqjys), jtzd__tnxa, np.array(
                [-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(twn__ydx), jtzd__tnxa, np.
                array([-1]).ctypes, 0, np.int32(root))
        return bcast_str_impl


c_bcast = types.ExternalFunction('c_bcast', types.void(types.voidptr, types
    .int32, types.int32, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def bcast_scalar(val, root=MPI_ROOT):
    val = types.unliteral(val)
    if not (isinstance(val, (types.Integer, types.Float)) or val in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.string_type, types.none,
        types.bool_]):
        raise BodoError(
            f'bcast_scalar requires an argument of type Integer, Float, datetime64ns, timedelta64ns, string, None, or Bool. Found type {val}'
            )
    if val == types.none:
        return lambda val, root=MPI_ROOT: None
    if val == bodo.string_type:
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                xfdt__oom = 0
                eyetv__xzwuf = np.empty(0, np.uint8).ctypes
            else:
                eyetv__xzwuf, xfdt__oom = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            xfdt__oom = bodo.libs.distributed_api.bcast_scalar(xfdt__oom, root)
            if rank != root:
                qlo__cogow = np.empty(xfdt__oom + 1, np.uint8)
                qlo__cogow[xfdt__oom] = 0
                eyetv__xzwuf = qlo__cogow.ctypes
            c_bcast(eyetv__xzwuf, np.int32(xfdt__oom), jtzd__tnxa, np.array
                ([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(eyetv__xzwuf, xfdt__oom)
        return impl_str
    typ_val = numba_to_c_type(val)
    zjp__cca = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    vkl__vhvwz = {}
    exec(zjp__cca, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, vkl__vhvwz)
    vpda__tqoc = vkl__vhvwz['bcast_scalar_impl']
    return vpda__tqoc


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    oszn__mmnej = len(val)
    zjp__cca = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    zjp__cca += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(oszn__mmnej)
        ), ',' if oszn__mmnej else '')
    vkl__vhvwz = {}
    exec(zjp__cca, {'bcast_scalar': bcast_scalar}, vkl__vhvwz)
    acdwg__axc = vkl__vhvwz['bcast_tuple_impl']
    return acdwg__axc


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            osvt__tmps = bcast_scalar(len(arr), root)
            phg__mcf = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(osvt__tmps, phg__mcf)
            return arr
        return prealloc_impl
    return lambda arr, root=MPI_ROOT: arr


def get_local_slice(idx, arr_start, total_len):
    return idx


@overload(get_local_slice, no_unliteral=True, jit_options={'cache': True,
    'no_cpython_wrapper': True})
def get_local_slice_overload(idx, arr_start, total_len):
    if not idx.has_step:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            lkcyy__cwmh = max(arr_start, slice_index.start) - arr_start
            cgdl__wslus = max(slice_index.stop - arr_start, 0)
            return slice(lkcyy__cwmh, cgdl__wslus)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            ixnmn__tfzzb = slice_index.start
            vhz__raywj = slice_index.step
            zwyrv__dau = (0 if vhz__raywj == 1 or ixnmn__tfzzb > arr_start else
                abs(vhz__raywj - arr_start % vhz__raywj) % vhz__raywj)
            lkcyy__cwmh = max(arr_start, slice_index.start
                ) - arr_start + zwyrv__dau
            cgdl__wslus = max(slice_index.stop - arr_start, 0)
            return slice(lkcyy__cwmh, cgdl__wslus, vhz__raywj)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        lqcx__kffcw = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[lqcx__kffcw])
    return getitem_impl


dummy_use = numba.njit(lambda a: None)


def int_getitem(arr, ind, arr_start, total_len, is_1D):
    return arr[ind]


def transform_str_getitem_output(data, length):
    pass


@overload(transform_str_getitem_output)
def overload_transform_str_getitem_output(data, length):
    if data == bodo.string_type:
        return lambda data, length: bodo.libs.str_arr_ext.decode_utf8(data.
            _data, length)
    if data == types.Array(types.uint8, 1, 'C'):
        return lambda data, length: bodo.libs.binary_arr_ext.init_bytes_type(
            data, length)
    raise BodoError(
        f'Internal Error: Expected String or Uint8 Array, found {data}')


@overload(int_getitem, no_unliteral=True)
def int_getitem_overload(arr, ind, arr_start, total_len, is_1D):
    if is_str_arr_type(arr) or arr == bodo.binary_array_type:
        kikke__ccosy = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        jtzd__tnxa = np.int32(numba_to_c_type(types.uint8))
        xjrex__xyw = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            vfm__vau = np.int32(10)
            tag = np.int32(11)
            epe__cwbuh = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                fpxd__vhx = arr._data
                rre__otnd = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    fpxd__vhx, ind)
                jjyi__ymbzc = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    fpxd__vhx, ind + 1)
                length = jjyi__ymbzc - rre__otnd
                apw__igbj = fpxd__vhx[ind]
                epe__cwbuh[0] = length
                isend(epe__cwbuh, np.int32(1), root, vfm__vau, True)
                isend(apw__igbj, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(xjrex__xyw
                , kikke__ccosy, 0, 1)
            cdgv__jkw = 0
            if rank == root:
                cdgv__jkw = recv(np.int64, ANY_SOURCE, vfm__vau)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    xjrex__xyw, kikke__ccosy, cdgv__jkw, 1)
                mjxf__urva = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(mjxf__urva, np.int32(cdgv__jkw), jtzd__tnxa,
                    ANY_SOURCE, tag)
            dummy_use(epe__cwbuh)
            cdgv__jkw = bcast_scalar(cdgv__jkw)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    xjrex__xyw, kikke__ccosy, cdgv__jkw, 1)
            mjxf__urva = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(mjxf__urva, np.int32(cdgv__jkw), jtzd__tnxa, np.array([
                -1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, cdgv__jkw)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        jpeao__daoer = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, jpeao__daoer)
            if arr_start <= ind < arr_start + len(arr):
                xza__zurap = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = xza__zurap[ind - arr_start]
                send_arr = np.full(1, data, jpeao__daoer)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = jpeao__daoer(-1)
            if rank == root:
                val = recv(jpeao__daoer, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            xjk__jqk = arr.dtype.categories[max(val, 0)]
            return xjk__jqk
        return cat_getitem_impl
    wnp__mnmo = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, wnp__mnmo)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, wnp__mnmo)[0]
        if rank == root:
            val = recv(wnp__mnmo, ANY_SOURCE, tag)
        dummy_use(send_arr)
        val = bcast_scalar(val)
        return val
    return getitem_impl


c_alltoallv = types.ExternalFunction('c_alltoallv', types.void(types.
    voidptr, types.voidptr, types.voidptr, types.voidptr, types.voidptr,
    types.voidptr, types.int32))


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def alltoallv(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    typ_enum = get_type_enum(send_data)
    qfnxp__ctw = get_type_enum(out_data)
    assert typ_enum == qfnxp__ctw
    if isinstance(send_data, (IntegerArrayType, DecimalArrayType)
        ) or send_data in (boolean_array, datetime_date_array_type):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data._data.ctypes,
            out_data._data.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    if isinstance(send_data, bodo.CategoricalArrayType):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data.codes.ctypes,
            out_data.codes.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    return (lambda send_data, out_data, send_counts, recv_counts, send_disp,
        recv_disp: c_alltoallv(send_data.ctypes, out_data.ctypes,
        send_counts.ctypes, recv_counts.ctypes, send_disp.ctypes, recv_disp
        .ctypes, typ_enum))


def alltoallv_tup(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    return


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(send_data, out_data, send_counts, recv_counts,
    send_disp, recv_disp):
    count = send_data.count
    assert out_data.count == count
    zjp__cca = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        zjp__cca += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    zjp__cca += '  return\n'
    vkl__vhvwz = {}
    exec(zjp__cca, {'alltoallv': alltoallv}, vkl__vhvwz)
    fhjh__yvak = vkl__vhvwz['f']
    return fhjh__yvak


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    ixnmn__tfzzb = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return ixnmn__tfzzb, count


@numba.njit
def get_start(total_size, pes, rank):
    hif__qsf = total_size % pes
    cgi__kfz = (total_size - hif__qsf) // pes
    return rank * cgi__kfz + min(rank, hif__qsf)


@numba.njit
def get_end(total_size, pes, rank):
    hif__qsf = total_size % pes
    cgi__kfz = (total_size - hif__qsf) // pes
    return (rank + 1) * cgi__kfz + min(rank + 1, hif__qsf)


@numba.njit
def get_node_portion(total_size, pes, rank):
    hif__qsf = total_size % pes
    cgi__kfz = (total_size - hif__qsf) // pes
    if rank < hif__qsf:
        return cgi__kfz + 1
    else:
        return cgi__kfz


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    uzk__ntjtk = in_arr.dtype(0)
    atb__tpl = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        cmhk__fei = uzk__ntjtk
        for lgme__dvk in np.nditer(in_arr):
            cmhk__fei += lgme__dvk.item()
        aad__joomh = dist_exscan(cmhk__fei, atb__tpl)
        for i in range(in_arr.size):
            aad__joomh += in_arr[i]
            out_arr[i] = aad__joomh
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    fjplf__twx = in_arr.dtype(1)
    atb__tpl = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        cmhk__fei = fjplf__twx
        for lgme__dvk in np.nditer(in_arr):
            cmhk__fei *= lgme__dvk.item()
        aad__joomh = dist_exscan(cmhk__fei, atb__tpl)
        if get_rank() == 0:
            aad__joomh = fjplf__twx
        for i in range(in_arr.size):
            aad__joomh *= in_arr[i]
            out_arr[i] = aad__joomh
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        fjplf__twx = np.finfo(in_arr.dtype(1).dtype).max
    else:
        fjplf__twx = np.iinfo(in_arr.dtype(1).dtype).max
    atb__tpl = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        cmhk__fei = fjplf__twx
        for lgme__dvk in np.nditer(in_arr):
            cmhk__fei = min(cmhk__fei, lgme__dvk.item())
        aad__joomh = dist_exscan(cmhk__fei, atb__tpl)
        if get_rank() == 0:
            aad__joomh = fjplf__twx
        for i in range(in_arr.size):
            aad__joomh = min(aad__joomh, in_arr[i])
            out_arr[i] = aad__joomh
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        fjplf__twx = np.finfo(in_arr.dtype(1).dtype).min
    else:
        fjplf__twx = np.iinfo(in_arr.dtype(1).dtype).min
    fjplf__twx = in_arr.dtype(1)
    atb__tpl = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        cmhk__fei = fjplf__twx
        for lgme__dvk in np.nditer(in_arr):
            cmhk__fei = max(cmhk__fei, lgme__dvk.item())
        aad__joomh = dist_exscan(cmhk__fei, atb__tpl)
        if get_rank() == 0:
            aad__joomh = fjplf__twx
        for i in range(in_arr.size):
            aad__joomh = max(aad__joomh, in_arr[i])
            out_arr[i] = aad__joomh
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    pidzz__bir = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), pidzz__bir)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ijr__aar = args[0]
    if equiv_set.has_shape(ijr__aar):
        return ArrayAnalysis.AnalyzeResult(shape=ijr__aar, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_dist_return = (
    dist_return_equiv)
ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_rep_return = (
    dist_return_equiv)


def threaded_return(A):
    return A


@numba.njit
def set_arr_local(arr, ind, val):
    arr[ind] = val


@numba.njit
def local_alloc_size(n, in_arr):
    return n


@infer_global(threaded_return)
@infer_global(dist_return)
@infer_global(rep_return)
class ThreadedRetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        return signature(args[0], *args)


@numba.njit
def parallel_print(*args):
    print(*args)


@numba.njit
def single_print(*args):
    if bodo.libs.distributed_api.get_rank() == 0:
        print(*args)


def print_if_not_empty(args):
    pass


@overload(print_if_not_empty)
def overload_print_if_not_empty(*args):
    fnxkh__nixdg = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for
        i, vilz__bkta in enumerate(args) if is_array_typ(vilz__bkta) or
        isinstance(vilz__bkta, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    zjp__cca = f"""def impl(*args):
    if {fnxkh__nixdg} or bodo.get_rank() == 0:
        print(*args)"""
    vkl__vhvwz = {}
    exec(zjp__cca, globals(), vkl__vhvwz)
    impl = vkl__vhvwz['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        znfmc__ojnk = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        zjp__cca = 'def f(req, cond=True):\n'
        zjp__cca += f'  return {znfmc__ojnk}\n'
        vkl__vhvwz = {}
        exec(zjp__cca, {'_wait': _wait}, vkl__vhvwz)
        impl = vkl__vhvwz['f']
        return impl
    if is_overload_none(req):
        return lambda req, cond=True: None
    return lambda req, cond=True: _wait(req, cond)


@register_jitable
def _set_if_in_range(A, val, index, chunk_start):
    if index >= chunk_start and index < chunk_start + len(A):
        A[index - chunk_start] = val


@register_jitable
def _root_rank_select(old_val, new_val):
    if get_rank() == 0:
        return old_val
    return new_val


def get_tuple_prod(t):
    return np.prod(t)


@overload(get_tuple_prod, no_unliteral=True)
def get_tuple_prod_overload(t):
    if t == numba.core.types.containers.Tuple(()):
        return lambda t: 1

    def get_tuple_prod_impl(t):
        hif__qsf = 1
        for a in t:
            hif__qsf *= a
        return hif__qsf
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    abewq__uqp = np.ascontiguousarray(in_arr)
    azbg__zestw = get_tuple_prod(abewq__uqp.shape[1:])
    qbe__wto = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        goy__obgr = np.array(dest_ranks, dtype=np.int32)
    else:
        goy__obgr = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, abewq__uqp.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * qbe__wto, dtype_size * azbg__zestw, len(
        goy__obgr), goy__obgr.ctypes)
    check_and_propagate_cpp_exception()


permutation_int = types.ExternalFunction('permutation_int', types.void(
    types.voidptr, types.intp))


@numba.njit
def dist_permutation_int(lhs, n):
    permutation_int(lhs.ctypes, n)


permutation_array_index = types.ExternalFunction('permutation_array_index',
    types.void(types.voidptr, types.intp, types.intp, types.voidptr, types.
    int64, types.voidptr, types.intp, types.int64))


@numba.njit
def dist_permutation_array_index(lhs, lhs_len, dtype_size, rhs, p, p_len,
    n_samples):
    cxp__meeda = np.ascontiguousarray(rhs)
    rab__mivtm = get_tuple_prod(cxp__meeda.shape[1:])
    ytw__njsv = dtype_size * rab__mivtm
    permutation_array_index(lhs.ctypes, lhs_len, ytw__njsv, cxp__meeda.
        ctypes, cxp__meeda.shape[0], p.ctypes, p_len, n_samples)
    check_and_propagate_cpp_exception()


from bodo.io import fsspec_reader, hdfs_reader, s3_reader
ll.add_symbol('finalize', hdist.finalize)
finalize = types.ExternalFunction('finalize', types.int32())
ll.add_symbol('finalize_s3', s3_reader.finalize_s3)
finalize_s3 = types.ExternalFunction('finalize_s3', types.int32())
ll.add_symbol('finalize_fsspec', fsspec_reader.finalize_fsspec)
finalize_fsspec = types.ExternalFunction('finalize_fsspec', types.int32())
ll.add_symbol('disconnect_hdfs', hdfs_reader.disconnect_hdfs)
disconnect_hdfs = types.ExternalFunction('disconnect_hdfs', types.int32())


def _check_for_cpp_errors():
    pass


@overload(_check_for_cpp_errors)
def overload_check_for_cpp_errors():
    return lambda : check_and_propagate_cpp_exception()


@numba.njit
def call_finalize():
    finalize()
    finalize_s3()
    finalize_fsspec()
    _check_for_cpp_errors()
    disconnect_hdfs()


def flush_stdout():
    if not sys.stdout.closed:
        sys.stdout.flush()


atexit.register(call_finalize)
atexit.register(flush_stdout)


def bcast_comm(data, comm_ranks, nranks, root=MPI_ROOT):
    rank = bodo.libs.distributed_api.get_rank()
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype, root)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return bcast_comm_impl(data, comm_ranks, nranks, root)


@overload(bcast_comm)
def bcast_comm_overload(data, comm_ranks, nranks, root=MPI_ROOT):
    return lambda data, comm_ranks, nranks, root=MPI_ROOT: bcast_comm_impl(data
        , comm_ranks, nranks, root)


@numba.generated_jit(nopython=True)
def bcast_comm_impl(data, comm_ranks, nranks, root=MPI_ROOT):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.bcast_comm()')
    if isinstance(data, (types.Integer, types.Float)):
        typ_val = numba_to_c_type(data)
        zjp__cca = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        vkl__vhvwz = {}
        exec(zjp__cca, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
            dtype}, vkl__vhvwz)
        vpda__tqoc = vkl__vhvwz['bcast_scalar_impl']
        return vpda__tqoc
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hng__uytb = len(data.columns)
        ezhjf__mnle = ', '.join('g_data_{}'.format(i) for i in range(hng__uytb)
            )
        uhhjt__uxkhp = ColNamesMetaType(data.columns)
        zjp__cca = f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n'
        for i in range(hng__uytb):
            zjp__cca += (
                '  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})\n'
                .format(i, i))
            zjp__cca += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        zjp__cca += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        zjp__cca += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        zjp__cca += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(ezhjf__mnle))
        vkl__vhvwz = {}
        exec(zjp__cca, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            uhhjt__uxkhp}, vkl__vhvwz)
        uuej__tmck = vkl__vhvwz['impl_df']
        return uuej__tmck
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            ixnmn__tfzzb = data._start
            npjm__wosux = data._stop
            vhz__raywj = data._step
            mmefs__eplij = data._name
            mmefs__eplij = bcast_scalar(mmefs__eplij, root)
            ixnmn__tfzzb = bcast_scalar(ixnmn__tfzzb, root)
            npjm__wosux = bcast_scalar(npjm__wosux, root)
            vhz__raywj = bcast_scalar(vhz__raywj, root)
            xmksd__vqzm = bodo.libs.array_kernels.calc_nitems(ixnmn__tfzzb,
                npjm__wosux, vhz__raywj)
            chunk_start = bodo.libs.distributed_api.get_start(xmksd__vqzm,
                n_pes, rank)
            drxu__lkygp = bodo.libs.distributed_api.get_node_portion(
                xmksd__vqzm, n_pes, rank)
            lkcyy__cwmh = ixnmn__tfzzb + vhz__raywj * chunk_start
            cgdl__wslus = ixnmn__tfzzb + vhz__raywj * (chunk_start +
                drxu__lkygp)
            cgdl__wslus = min(cgdl__wslus, npjm__wosux)
            return bodo.hiframes.pd_index_ext.init_range_index(lkcyy__cwmh,
                cgdl__wslus, vhz__raywj, mmefs__eplij)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            thk__nsu = data._data
            mmefs__eplij = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(thk__nsu,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, mmefs__eplij)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            mmefs__eplij = bodo.hiframes.pd_series_ext.get_series_name(data)
            wqnf__abc = bodo.libs.distributed_api.bcast_comm_impl(mmefs__eplij,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            mtaix__ipl = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                mtaix__ipl, wqnf__abc)
        return impl_series
    if isinstance(data, types.BaseTuple):
        zjp__cca = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        zjp__cca += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        vkl__vhvwz = {}
        exec(zjp__cca, {'bcast_comm_impl': bcast_comm_impl}, vkl__vhvwz)
        ufuc__dffla = vkl__vhvwz['impl_tuple']
        return ufuc__dffla
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    rpv__mjo = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    gmf__gywj = (0,) * rpv__mjo

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        thk__nsu = np.ascontiguousarray(data)
        mjxf__urva = data.ctypes
        vehuh__djdwo = gmf__gywj
        if rank == root:
            vehuh__djdwo = thk__nsu.shape
        vehuh__djdwo = bcast_tuple(vehuh__djdwo, root)
        nsy__suhci = get_tuple_prod(vehuh__djdwo[1:])
        send_counts = vehuh__djdwo[0] * nsy__suhci
        xyy__puz = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(mjxf__urva, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(xyy__puz.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return xyy__puz.reshape((-1,) + vehuh__djdwo[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        ijpen__laxy = MPI.COMM_WORLD
        tez__lwl = MPI.Get_processor_name()
        kepw__fmy = ijpen__laxy.allgather(tez__lwl)
        node_ranks = defaultdict(list)
        for i, hlozt__ifqwe in enumerate(kepw__fmy):
            node_ranks[hlozt__ifqwe].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    ijpen__laxy = MPI.COMM_WORLD
    mxk__dow = ijpen__laxy.Get_group()
    kjcx__gieu = mxk__dow.Incl(comm_ranks)
    uvv__jpvj = ijpen__laxy.Create_group(kjcx__gieu)
    return uvv__jpvj


def get_nodes_first_ranks():
    vrofu__euzs = get_host_ranks()
    return np.array([ctquc__bvi[0] for ctquc__bvi in vrofu__euzs.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
