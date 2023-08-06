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
    dnu__mffq = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, dnu__mffq, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    dnu__mffq = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, dnu__mffq, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            dnu__mffq = get_type_enum(arr)
            return _isend(arr.ctypes, size, dnu__mffq, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        dnu__mffq = np.int32(numba_to_c_type(arr.dtype))
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            ozh__ylyx = size + 7 >> 3
            whc__qfl = _isend(arr._data.ctypes, size, dnu__mffq, pe, tag, cond)
            mzg__udb = _isend(arr._null_bitmap.ctypes, ozh__ylyx,
                uyczd__egzl, pe, tag, cond)
            return whc__qfl, mzg__udb
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        mvt__yiha = np.int32(numba_to_c_type(offset_type))
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            bgs__wvacz = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(bgs__wvacz, pe, tag - 1)
            ozh__ylyx = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                mvt__yiha, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), bgs__wvacz,
                uyczd__egzl, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), ozh__ylyx,
                uyczd__egzl, pe, tag)
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
            dnu__mffq = get_type_enum(arr)
            return _irecv(arr.ctypes, size, dnu__mffq, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        dnu__mffq = np.int32(numba_to_c_type(arr.dtype))
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            ozh__ylyx = size + 7 >> 3
            whc__qfl = _irecv(arr._data.ctypes, size, dnu__mffq, pe, tag, cond)
            mzg__udb = _irecv(arr._null_bitmap.ctypes, ozh__ylyx,
                uyczd__egzl, pe, tag, cond)
            return whc__qfl, mzg__udb
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        mvt__yiha = np.int32(numba_to_c_type(offset_type))
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            dbtds__owfok = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            dbtds__owfok = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        otypr__vub = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {dbtds__owfok}(size, n_chars)
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
        mtf__nwqa = dict()
        exec(otypr__vub, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            mvt__yiha, 'char_typ_enum': uyczd__egzl}, mtf__nwqa)
        impl = mtf__nwqa['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    dnu__mffq = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), dnu__mffq)


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
        urhn__lxg = n_pes if rank == root or allgather else 0
        rpdr__lixqt = np.empty(urhn__lxg, dtype)
        c_gather_scalar(send.ctypes, rpdr__lixqt.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return rpdr__lixqt
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
        tvnn__mhgd = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], tvnn__mhgd)
        return builder.bitcast(tvnn__mhgd, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        tvnn__mhgd = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(tvnn__mhgd)
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
    ibb__bnrbj = types.unliteral(value)
    if isinstance(ibb__bnrbj, IndexValueType):
        ibb__bnrbj = ibb__bnrbj.val_typ
        piwa__aeb = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            piwa__aeb.append(types.int64)
            piwa__aeb.append(bodo.datetime64ns)
            piwa__aeb.append(bodo.timedelta64ns)
            piwa__aeb.append(bodo.datetime_date_type)
        if ibb__bnrbj not in piwa__aeb:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(ibb__bnrbj))
    typ_enum = np.int32(numba_to_c_type(ibb__bnrbj))

    def impl(value, reduce_op):
        gedab__lchi = value_to_ptr(value)
        iak__kibr = value_to_ptr(value)
        _dist_reduce(gedab__lchi, iak__kibr, reduce_op, typ_enum)
        return load_val_ptr(iak__kibr, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    ibb__bnrbj = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(ibb__bnrbj))
    zposc__lgun = ibb__bnrbj(0)

    def impl(value, reduce_op):
        gedab__lchi = value_to_ptr(value)
        iak__kibr = value_to_ptr(zposc__lgun)
        _dist_exscan(gedab__lchi, iak__kibr, reduce_op, typ_enum)
        return load_val_ptr(iak__kibr, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    pyx__grucr = 0
    ddu__uwcu = 0
    for i in range(len(recv_counts)):
        dbnp__adh = recv_counts[i]
        ozh__ylyx = recv_counts_nulls[i]
        yusi__rlbwr = tmp_null_bytes[pyx__grucr:pyx__grucr + ozh__ylyx]
        for tggtx__wcwc in range(dbnp__adh):
            set_bit_to(null_bitmap_ptr, ddu__uwcu, get_bit(yusi__rlbwr,
                tggtx__wcwc))
            ddu__uwcu += 1
        pyx__grucr += ozh__ylyx


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            ozl__pfos = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                ozl__pfos, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            hftmo__iund = data.size
            recv_counts = gather_scalar(np.int32(hftmo__iund), allgather,
                root=root)
            ebwc__kpa = recv_counts.sum()
            hsjx__lpote = empty_like_type(ebwc__kpa, data)
            soa__gwiky = np.empty(1, np.int32)
            if rank == root or allgather:
                soa__gwiky = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(hftmo__iund), hsjx__lpote.
                ctypes, recv_counts.ctypes, soa__gwiky.ctypes, np.int32(
                typ_val), allgather, np.int32(root))
            return hsjx__lpote.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            hsjx__lpote = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.str_arr_ext.init_str_arr(hsjx__lpote)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            hsjx__lpote = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.binary_arr_ext.init_binary_arr(hsjx__lpote)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            hftmo__iund = len(data)
            ozh__ylyx = hftmo__iund + 7 >> 3
            recv_counts = gather_scalar(np.int32(hftmo__iund), allgather,
                root=root)
            ebwc__kpa = recv_counts.sum()
            hsjx__lpote = empty_like_type(ebwc__kpa, data)
            soa__gwiky = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            ojij__qwgm = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                soa__gwiky = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                ojij__qwgm = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(hftmo__iund),
                hsjx__lpote._days_data.ctypes, recv_counts.ctypes,
                soa__gwiky.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._seconds_data.ctypes, np.int32(hftmo__iund),
                hsjx__lpote._seconds_data.ctypes, recv_counts.ctypes,
                soa__gwiky.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._microseconds_data.ctypes, np.int32(hftmo__iund),
                hsjx__lpote._microseconds_data.ctypes, recv_counts.ctypes,
                soa__gwiky.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._null_bitmap.ctypes, np.int32(ozh__ylyx),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, ojij__qwgm
                .ctypes, uyczd__egzl, allgather, np.int32(root))
            copy_gathered_null_bytes(hsjx__lpote._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return hsjx__lpote
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            hftmo__iund = len(data)
            ozh__ylyx = hftmo__iund + 7 >> 3
            recv_counts = gather_scalar(np.int32(hftmo__iund), allgather,
                root=root)
            ebwc__kpa = recv_counts.sum()
            hsjx__lpote = empty_like_type(ebwc__kpa, data)
            soa__gwiky = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            ojij__qwgm = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                soa__gwiky = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                ojij__qwgm = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(hftmo__iund), hsjx__lpote
                ._data.ctypes, recv_counts.ctypes, soa__gwiky.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(ozh__ylyx),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, ojij__qwgm
                .ctypes, uyczd__egzl, allgather, np.int32(root))
            copy_gathered_null_bytes(hsjx__lpote._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return hsjx__lpote
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        kkd__lni = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            ipqta__uatfq = bodo.gatherv(data._data, allgather, warn_if_rep,
                root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                ipqta__uatfq, kkd__lni)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            nnd__yile = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            vitjn__hyizw = bodo.gatherv(data._right, allgather, warn_if_rep,
                root)
            return bodo.libs.interval_arr_ext.init_interval_array(nnd__yile,
                vitjn__hyizw)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            npf__rpvk = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            cfkw__ekl = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cfkw__ekl, npf__rpvk)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        umu__bmrqc = np.iinfo(np.int64).max
        sahyo__orkd = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            rpo__frclr = data._start
            syv__jtcy = data._stop
            if len(data) == 0:
                rpo__frclr = umu__bmrqc
                syv__jtcy = sahyo__orkd
            rpo__frclr = bodo.libs.distributed_api.dist_reduce(rpo__frclr,
                np.int32(Reduce_Type.Min.value))
            syv__jtcy = bodo.libs.distributed_api.dist_reduce(syv__jtcy, np
                .int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if rpo__frclr == umu__bmrqc and syv__jtcy == sahyo__orkd:
                rpo__frclr = 0
                syv__jtcy = 0
            tmnu__hrtha = max(0, -(-(syv__jtcy - rpo__frclr) // data._step))
            if tmnu__hrtha < total_len:
                syv__jtcy = rpo__frclr + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                rpo__frclr = 0
                syv__jtcy = 0
            return bodo.hiframes.pd_index_ext.init_range_index(rpo__frclr,
                syv__jtcy, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            ivdo__miwk = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, ivdo__miwk)
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
            hsjx__lpote = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                hsjx__lpote, data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        kfx__dync = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        otypr__vub = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        otypr__vub += '  T = data\n'
        otypr__vub += '  T2 = init_table(T, True)\n'
        for fkj__efa in data.type_to_blk.values():
            kfx__dync[f'arr_inds_{fkj__efa}'] = np.array(data.
                block_to_arr_ind[fkj__efa], dtype=np.int64)
            otypr__vub += (
                f'  arr_list_{fkj__efa} = get_table_block(T, {fkj__efa})\n')
            otypr__vub += f"""  out_arr_list_{fkj__efa} = alloc_list_like(arr_list_{fkj__efa}, len(arr_list_{fkj__efa}), True)
"""
            otypr__vub += f'  for i in range(len(arr_list_{fkj__efa})):\n'
            otypr__vub += f'    arr_ind_{fkj__efa} = arr_inds_{fkj__efa}[i]\n'
            otypr__vub += f"""    ensure_column_unboxed(T, arr_list_{fkj__efa}, i, arr_ind_{fkj__efa})
"""
            otypr__vub += f"""    out_arr_{fkj__efa} = bodo.gatherv(arr_list_{fkj__efa}[i], allgather, warn_if_rep, root)
"""
            otypr__vub += (
                f'    out_arr_list_{fkj__efa}[i] = out_arr_{fkj__efa}\n')
            otypr__vub += (
                f'  T2 = set_table_block(T2, out_arr_list_{fkj__efa}, {fkj__efa})\n'
                )
        otypr__vub += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        otypr__vub += f'  T2 = set_table_len(T2, length)\n'
        otypr__vub += f'  return T2\n'
        mtf__nwqa = {}
        exec(otypr__vub, kfx__dync, mtf__nwqa)
        mlpc__slx = mtf__nwqa['impl_table']
        return mlpc__slx
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        vpezg__jabm = len(data.columns)
        if vpezg__jabm == 0:
            kkm__kxfty = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                qhul__hzqu = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    qhul__hzqu, kkm__kxfty)
            return impl
        ubuex__fjmf = ', '.join(f'g_data_{i}' for i in range(vpezg__jabm))
        otypr__vub = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            iboz__bepfn = bodo.hiframes.pd_dataframe_ext.DataFrameType(data
                .data, data.index, data.columns, Distribution.REP, True)
            ubuex__fjmf = 'T2'
            otypr__vub += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            otypr__vub += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(vpezg__jabm):
                otypr__vub += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                otypr__vub += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        otypr__vub += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        otypr__vub += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        otypr__vub += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(ubuex__fjmf))
        mtf__nwqa = {}
        kfx__dync = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(otypr__vub, kfx__dync, mtf__nwqa)
        rbegw__ayu = mtf__nwqa['impl_df']
        return rbegw__ayu
    if isinstance(data, ArrayItemArrayType):
        qnu__uays = np.int32(numba_to_c_type(types.int32))
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            mkgwz__insp = bodo.libs.array_item_arr_ext.get_offsets(data)
            hyjhe__tukf = bodo.libs.array_item_arr_ext.get_data(data)
            hyjhe__tukf = hyjhe__tukf[:mkgwz__insp[-1]]
            xmq__jrutc = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            hftmo__iund = len(data)
            mwl__eyvku = np.empty(hftmo__iund, np.uint32)
            ozh__ylyx = hftmo__iund + 7 >> 3
            for i in range(hftmo__iund):
                mwl__eyvku[i] = mkgwz__insp[i + 1] - mkgwz__insp[i]
            recv_counts = gather_scalar(np.int32(hftmo__iund), allgather,
                root=root)
            ebwc__kpa = recv_counts.sum()
            soa__gwiky = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            ojij__qwgm = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                soa__gwiky = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for eocy__gqqhi in range(len(recv_counts)):
                    recv_counts_nulls[eocy__gqqhi] = recv_counts[eocy__gqqhi
                        ] + 7 >> 3
                ojij__qwgm = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            tdzrb__jlh = np.empty(ebwc__kpa + 1, np.uint32)
            aprla__pcxkh = bodo.gatherv(hyjhe__tukf, allgather, warn_if_rep,
                root)
            sir__znw = np.empty(ebwc__kpa + 7 >> 3, np.uint8)
            c_gatherv(mwl__eyvku.ctypes, np.int32(hftmo__iund), tdzrb__jlh.
                ctypes, recv_counts.ctypes, soa__gwiky.ctypes, qnu__uays,
                allgather, np.int32(root))
            c_gatherv(xmq__jrutc.ctypes, np.int32(ozh__ylyx),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, ojij__qwgm
                .ctypes, uyczd__egzl, allgather, np.int32(root))
            dummy_use(data)
            gic__mbuhg = np.empty(ebwc__kpa + 1, np.uint64)
            convert_len_arr_to_offset(tdzrb__jlh.ctypes, gic__mbuhg.ctypes,
                ebwc__kpa)
            copy_gathered_null_bytes(sir__znw.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                ebwc__kpa, aprla__pcxkh, gic__mbuhg, sir__znw)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        xxzny__lhm = data.names
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            oocdh__gwzy = bodo.libs.struct_arr_ext.get_data(data)
            asamy__uzxfv = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            xbjsy__xqnr = bodo.gatherv(oocdh__gwzy, allgather=allgather,
                root=root)
            rank = bodo.libs.distributed_api.get_rank()
            hftmo__iund = len(data)
            ozh__ylyx = hftmo__iund + 7 >> 3
            recv_counts = gather_scalar(np.int32(hftmo__iund), allgather,
                root=root)
            ebwc__kpa = recv_counts.sum()
            bqs__pgfwl = np.empty(ebwc__kpa + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            ojij__qwgm = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                ojij__qwgm = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(asamy__uzxfv.ctypes, np.int32(ozh__ylyx),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, ojij__qwgm
                .ctypes, uyczd__egzl, allgather, np.int32(root))
            copy_gathered_null_bytes(bqs__pgfwl.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(xbjsy__xqnr,
                bqs__pgfwl, xxzny__lhm)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            hsjx__lpote = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.binary_arr_ext.init_binary_arr(hsjx__lpote)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            hsjx__lpote = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.tuple_arr_ext.init_tuple_arr(hsjx__lpote)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            hsjx__lpote = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.map_arr_ext.init_map_arr(hsjx__lpote)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            hsjx__lpote = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            eyby__dluo = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            wwsq__waegs = bodo.gatherv(data.indptr, allgather, warn_if_rep,
                root)
            gxqg__ymfdo = gather_scalar(data.shape[0], allgather, root=root)
            ffip__fzql = gxqg__ymfdo.sum()
            vpezg__jabm = bodo.libs.distributed_api.dist_reduce(data.shape[
                1], np.int32(Reduce_Type.Max.value))
            gcm__hdhkm = np.empty(ffip__fzql + 1, np.int64)
            eyby__dluo = eyby__dluo.astype(np.int64)
            gcm__hdhkm[0] = 0
            hdld__lenf = 1
            jtvpq__zcuof = 0
            for pdjw__smwq in gxqg__ymfdo:
                for spxff__ahd in range(pdjw__smwq):
                    dazvw__tdzd = wwsq__waegs[jtvpq__zcuof + 1] - wwsq__waegs[
                        jtvpq__zcuof]
                    gcm__hdhkm[hdld__lenf] = gcm__hdhkm[hdld__lenf - 1
                        ] + dazvw__tdzd
                    hdld__lenf += 1
                    jtvpq__zcuof += 1
                jtvpq__zcuof += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(hsjx__lpote,
                eyby__dluo, gcm__hdhkm, (ffip__fzql, vpezg__jabm))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        otypr__vub = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        otypr__vub += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        mtf__nwqa = {}
        exec(otypr__vub, {'bodo': bodo}, mtf__nwqa)
        eggva__zdiax = mtf__nwqa['impl_tuple']
        return eggva__zdiax
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    otypr__vub = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    otypr__vub += '    if random:\n'
    otypr__vub += '        if random_seed is None:\n'
    otypr__vub += '            random = 1\n'
    otypr__vub += '        else:\n'
    otypr__vub += '            random = 2\n'
    otypr__vub += '    if random_seed is None:\n'
    otypr__vub += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        hyyrz__qpdy = data
        vpezg__jabm = len(hyyrz__qpdy.columns)
        for i in range(vpezg__jabm):
            otypr__vub += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        otypr__vub += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        ubuex__fjmf = ', '.join(f'data_{i}' for i in range(vpezg__jabm))
        otypr__vub += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(hxtxi__bsxyr) for
            hxtxi__bsxyr in range(vpezg__jabm))))
        otypr__vub += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        otypr__vub += '    if dests is None:\n'
        otypr__vub += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        otypr__vub += '    else:\n'
        otypr__vub += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for pluyh__ozbvk in range(vpezg__jabm):
            otypr__vub += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(pluyh__ozbvk))
        otypr__vub += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(vpezg__jabm))
        otypr__vub += '    delete_table(out_table)\n'
        otypr__vub += '    if parallel:\n'
        otypr__vub += '        delete_table(table_total)\n'
        ubuex__fjmf = ', '.join('out_arr_{}'.format(i) for i in range(
            vpezg__jabm))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        otypr__vub += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(ubuex__fjmf, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        otypr__vub += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        otypr__vub += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        otypr__vub += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        otypr__vub += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        otypr__vub += '    if dests is None:\n'
        otypr__vub += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        otypr__vub += '    else:\n'
        otypr__vub += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        otypr__vub += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        otypr__vub += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        otypr__vub += '    delete_table(out_table)\n'
        otypr__vub += '    if parallel:\n'
        otypr__vub += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        otypr__vub += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        otypr__vub += '    if not parallel:\n'
        otypr__vub += '        return data\n'
        otypr__vub += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        otypr__vub += '    if dests is None:\n'
        otypr__vub += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        otypr__vub += '    elif bodo.get_rank() not in dests:\n'
        otypr__vub += '        dim0_local_size = 0\n'
        otypr__vub += '    else:\n'
        otypr__vub += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        otypr__vub += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        otypr__vub += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        otypr__vub += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        otypr__vub += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        otypr__vub += '    if dests is None:\n'
        otypr__vub += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        otypr__vub += '    else:\n'
        otypr__vub += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        otypr__vub += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        otypr__vub += '    delete_table(out_table)\n'
        otypr__vub += '    if parallel:\n'
        otypr__vub += '        delete_table(table_total)\n'
        otypr__vub += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    mtf__nwqa = {}
    kfx__dync = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        kfx__dync.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(hyyrz__qpdy.columns)})
    exec(otypr__vub, kfx__dync, mtf__nwqa)
    impl = mtf__nwqa['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    otypr__vub = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        otypr__vub += '    if seed is None:\n'
        otypr__vub += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        otypr__vub += '    np.random.seed(seed)\n'
        otypr__vub += '    if not parallel:\n'
        otypr__vub += '        data = data.copy()\n'
        otypr__vub += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            otypr__vub += '        data = data[:n_samples]\n'
        otypr__vub += '        return data\n'
        otypr__vub += '    else:\n'
        otypr__vub += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        otypr__vub += '        permutation = np.arange(dim0_global_size)\n'
        otypr__vub += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            otypr__vub += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            otypr__vub += '        n_samples = dim0_global_size\n'
        otypr__vub += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        otypr__vub += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        otypr__vub += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        otypr__vub += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        otypr__vub += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        otypr__vub += '        return output\n'
    else:
        otypr__vub += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            otypr__vub += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            otypr__vub += '    output = output[:local_n_samples]\n'
        otypr__vub += '    return output\n'
    mtf__nwqa = {}
    exec(otypr__vub, {'np': np, 'bodo': bodo}, mtf__nwqa)
    impl = mtf__nwqa['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    ovyz__vyck = np.empty(sendcounts_nulls.sum(), np.uint8)
    pyx__grucr = 0
    ddu__uwcu = 0
    for cdlno__kwg in range(len(sendcounts)):
        dbnp__adh = sendcounts[cdlno__kwg]
        ozh__ylyx = sendcounts_nulls[cdlno__kwg]
        yusi__rlbwr = ovyz__vyck[pyx__grucr:pyx__grucr + ozh__ylyx]
        for tggtx__wcwc in range(dbnp__adh):
            set_bit_to_arr(yusi__rlbwr, tggtx__wcwc, get_bit_bitmap(
                null_bitmap_ptr, ddu__uwcu))
            ddu__uwcu += 1
        pyx__grucr += ozh__ylyx
    return ovyz__vyck


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    awlzy__bjagw = MPI.COMM_WORLD
    data = awlzy__bjagw.bcast(data, root)
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
    nxudp__wtr = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    pde__jlft = (0,) * nxudp__wtr

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        wwn__ivi = np.ascontiguousarray(data)
        cfrx__kcxta = data.ctypes
        dor__kwyw = pde__jlft
        if rank == MPI_ROOT:
            dor__kwyw = wwn__ivi.shape
        dor__kwyw = bcast_tuple(dor__kwyw)
        vadc__uki = get_tuple_prod(dor__kwyw[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            dor__kwyw[0])
        send_counts *= vadc__uki
        hftmo__iund = send_counts[rank]
        mhz__goptp = np.empty(hftmo__iund, dtype)
        soa__gwiky = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(cfrx__kcxta, send_counts.ctypes, soa__gwiky.ctypes,
            mhz__goptp.ctypes, np.int32(hftmo__iund), np.int32(typ_val))
        return mhz__goptp.reshape((-1,) + dor__kwyw[1:])
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
        nccv__evfcw = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], nccv__evfcw)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        npf__rpvk = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=npf__rpvk)
        pjsz__kfif = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(pjsz__kfif)
        return pd.Index(arr, name=npf__rpvk)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        npf__rpvk = _get_name_value_for_type(dtype.name_typ)
        xxzny__lhm = tuple(_get_name_value_for_type(t) for t in dtype.names_typ
            )
        zquug__wlmgq = tuple(get_value_for_type(t) for t in dtype.array_types)
        zquug__wlmgq = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in zquug__wlmgq)
        val = pd.MultiIndex.from_arrays(zquug__wlmgq, names=xxzny__lhm)
        val.name = npf__rpvk
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        npf__rpvk = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=npf__rpvk)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        zquug__wlmgq = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({npf__rpvk: arr for npf__rpvk, arr in zip(dtype
            .columns, zquug__wlmgq)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        pjsz__kfif = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(pjsz__kfif[0],
            pjsz__kfif[0])])
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
        qnu__uays = np.int32(numba_to_c_type(types.int32))
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            dbtds__owfok = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            dbtds__owfok = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        otypr__vub = f"""def impl(
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
            recv_arr = {dbtds__owfok}(n_loc, n_loc_char)

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
        mtf__nwqa = dict()
        exec(otypr__vub, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            qnu__uays, 'char_typ_enum': uyczd__egzl, 'decode_if_dict_array':
            decode_if_dict_array}, mtf__nwqa)
        impl = mtf__nwqa['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        qnu__uays = np.int32(numba_to_c_type(types.int32))
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            fyr__iisb = bodo.libs.array_item_arr_ext.get_offsets(data)
            smjg__ekz = bodo.libs.array_item_arr_ext.get_data(data)
            smjg__ekz = smjg__ekz[:fyr__iisb[-1]]
            hpxjo__dehg = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            yjp__loweq = bcast_scalar(len(data))
            tjx__ijyo = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                tjx__ijyo[i] = fyr__iisb[i + 1] - fyr__iisb[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                yjp__loweq)
            soa__gwiky = bodo.ir.join.calc_disp(send_counts)
            vve__uxkww = np.empty(n_pes, np.int32)
            if rank == 0:
                psi__dfoz = 0
                for i in range(n_pes):
                    pubrh__bso = 0
                    for spxff__ahd in range(send_counts[i]):
                        pubrh__bso += tjx__ijyo[psi__dfoz]
                        psi__dfoz += 1
                    vve__uxkww[i] = pubrh__bso
            bcast(vve__uxkww)
            xdbh__smcwu = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                xdbh__smcwu[i] = send_counts[i] + 7 >> 3
            ojij__qwgm = bodo.ir.join.calc_disp(xdbh__smcwu)
            hftmo__iund = send_counts[rank]
            pqd__whk = np.empty(hftmo__iund + 1, np_offset_type)
            agygi__nbs = bodo.libs.distributed_api.scatterv_impl(smjg__ekz,
                vve__uxkww)
            arz__uoqv = hftmo__iund + 7 >> 3
            kawo__xrrp = np.empty(arz__uoqv, np.uint8)
            usd__uoyd = np.empty(hftmo__iund, np.uint32)
            c_scatterv(tjx__ijyo.ctypes, send_counts.ctypes, soa__gwiky.
                ctypes, usd__uoyd.ctypes, np.int32(hftmo__iund), qnu__uays)
            convert_len_arr_to_offset(usd__uoyd.ctypes, pqd__whk.ctypes,
                hftmo__iund)
            wcvw__ujww = get_scatter_null_bytes_buff(hpxjo__dehg.ctypes,
                send_counts, xdbh__smcwu)
            c_scatterv(wcvw__ujww.ctypes, xdbh__smcwu.ctypes, ojij__qwgm.
                ctypes, kawo__xrrp.ctypes, np.int32(arz__uoqv), uyczd__egzl)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                hftmo__iund, agygi__nbs, pqd__whk, kawo__xrrp)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            remhn__xeiw = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            remhn__xeiw = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            remhn__xeiw = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            remhn__xeiw = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            wwn__ivi = data._data
            asamy__uzxfv = data._null_bitmap
            jnk__gqt = len(wwn__ivi)
            cgwz__idqmz = _scatterv_np(wwn__ivi, send_counts)
            yjp__loweq = bcast_scalar(jnk__gqt)
            sgsee__tawco = len(cgwz__idqmz) + 7 >> 3
            pmfw__sjtu = np.empty(sgsee__tawco, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                yjp__loweq)
            xdbh__smcwu = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                xdbh__smcwu[i] = send_counts[i] + 7 >> 3
            ojij__qwgm = bodo.ir.join.calc_disp(xdbh__smcwu)
            wcvw__ujww = get_scatter_null_bytes_buff(asamy__uzxfv.ctypes,
                send_counts, xdbh__smcwu)
            c_scatterv(wcvw__ujww.ctypes, xdbh__smcwu.ctypes, ojij__qwgm.
                ctypes, pmfw__sjtu.ctypes, np.int32(sgsee__tawco), uyczd__egzl)
            return remhn__xeiw(cgwz__idqmz, pmfw__sjtu)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            tlex__aguy = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            fzk__wck = bodo.libs.distributed_api.scatterv_impl(data._right,
                send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(tlex__aguy,
                fzk__wck)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            rpo__frclr = data._start
            syv__jtcy = data._stop
            yedbg__fjqm = data._step
            npf__rpvk = data._name
            npf__rpvk = bcast_scalar(npf__rpvk)
            rpo__frclr = bcast_scalar(rpo__frclr)
            syv__jtcy = bcast_scalar(syv__jtcy)
            yedbg__fjqm = bcast_scalar(yedbg__fjqm)
            bnjh__pdceg = bodo.libs.array_kernels.calc_nitems(rpo__frclr,
                syv__jtcy, yedbg__fjqm)
            chunk_start = bodo.libs.distributed_api.get_start(bnjh__pdceg,
                n_pes, rank)
            epkv__tzxqr = bodo.libs.distributed_api.get_node_portion(
                bnjh__pdceg, n_pes, rank)
            toxr__ofy = rpo__frclr + yedbg__fjqm * chunk_start
            gmf__iqio = rpo__frclr + yedbg__fjqm * (chunk_start + epkv__tzxqr)
            gmf__iqio = min(gmf__iqio, syv__jtcy)
            return bodo.hiframes.pd_index_ext.init_range_index(toxr__ofy,
                gmf__iqio, yedbg__fjqm, npf__rpvk)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        ivdo__miwk = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            wwn__ivi = data._data
            npf__rpvk = data._name
            npf__rpvk = bcast_scalar(npf__rpvk)
            arr = bodo.libs.distributed_api.scatterv_impl(wwn__ivi, send_counts
                )
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                npf__rpvk, ivdo__miwk)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            wwn__ivi = data._data
            npf__rpvk = data._name
            npf__rpvk = bcast_scalar(npf__rpvk)
            arr = bodo.libs.distributed_api.scatterv_impl(wwn__ivi, send_counts
                )
            return bodo.utils.conversion.index_from_array(arr, npf__rpvk)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            hsjx__lpote = bodo.libs.distributed_api.scatterv_impl(data.
                _data, send_counts)
            npf__rpvk = bcast_scalar(data._name)
            xxzny__lhm = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                hsjx__lpote, xxzny__lhm, npf__rpvk)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            npf__rpvk = bodo.hiframes.pd_series_ext.get_series_name(data)
            onngn__muksl = bcast_scalar(npf__rpvk)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            cfkw__ekl = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cfkw__ekl, onngn__muksl)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        vpezg__jabm = len(data.columns)
        ubuex__fjmf = ', '.join('g_data_{}'.format(i) for i in range(
            vpezg__jabm))
        yxop__ngsh = ColNamesMetaType(data.columns)
        otypr__vub = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(vpezg__jabm):
            otypr__vub += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            otypr__vub += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        otypr__vub += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        otypr__vub += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        otypr__vub += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({ubuex__fjmf},), g_index, __col_name_meta_scaterv_impl)
"""
        mtf__nwqa = {}
        exec(otypr__vub, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            yxop__ngsh}, mtf__nwqa)
        rbegw__ayu = mtf__nwqa['impl_df']
        return rbegw__ayu
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            ozl__pfos = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                ozl__pfos, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        otypr__vub = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        otypr__vub += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        mtf__nwqa = {}
        exec(otypr__vub, {'bodo': bodo}, mtf__nwqa)
        eggva__zdiax = mtf__nwqa['impl_tuple']
        return eggva__zdiax
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
        mvt__yiha = np.int32(numba_to_c_type(offset_type))
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            hftmo__iund = len(data)
            epli__tqh = num_total_chars(data)
            assert hftmo__iund < INT_MAX
            assert epli__tqh < INT_MAX
            khu__pai = get_offset_ptr(data)
            cfrx__kcxta = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            ozh__ylyx = hftmo__iund + 7 >> 3
            c_bcast(khu__pai, np.int32(hftmo__iund + 1), mvt__yiha, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(cfrx__kcxta, np.int32(epli__tqh), uyczd__egzl, np.array
                ([-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(ozh__ylyx), uyczd__egzl, np.
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
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                vjre__bzji = 0
                wcy__ydmj = np.empty(0, np.uint8).ctypes
            else:
                wcy__ydmj, vjre__bzji = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            vjre__bzji = bodo.libs.distributed_api.bcast_scalar(vjre__bzji,
                root)
            if rank != root:
                pnie__plmhw = np.empty(vjre__bzji + 1, np.uint8)
                pnie__plmhw[vjre__bzji] = 0
                wcy__ydmj = pnie__plmhw.ctypes
            c_bcast(wcy__ydmj, np.int32(vjre__bzji), uyczd__egzl, np.array(
                [-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(wcy__ydmj, vjre__bzji)
        return impl_str
    typ_val = numba_to_c_type(val)
    otypr__vub = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    mtf__nwqa = {}
    exec(otypr__vub, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, mtf__nwqa)
    vnpep__mbxtq = mtf__nwqa['bcast_scalar_impl']
    return vnpep__mbxtq


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    mywci__cgbfd = len(val)
    otypr__vub = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    otypr__vub += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(mywci__cgbfd
        )), ',' if mywci__cgbfd else '')
    mtf__nwqa = {}
    exec(otypr__vub, {'bcast_scalar': bcast_scalar}, mtf__nwqa)
    bwkj__euhlq = mtf__nwqa['bcast_tuple_impl']
    return bwkj__euhlq


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            hftmo__iund = bcast_scalar(len(arr), root)
            eufnl__hpu = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(hftmo__iund, eufnl__hpu)
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
            toxr__ofy = max(arr_start, slice_index.start) - arr_start
            gmf__iqio = max(slice_index.stop - arr_start, 0)
            return slice(toxr__ofy, gmf__iqio)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            rpo__frclr = slice_index.start
            yedbg__fjqm = slice_index.step
            lgu__nvwsu = (0 if yedbg__fjqm == 1 or rpo__frclr > arr_start else
                abs(yedbg__fjqm - arr_start % yedbg__fjqm) % yedbg__fjqm)
            toxr__ofy = max(arr_start, slice_index.start
                ) - arr_start + lgu__nvwsu
            gmf__iqio = max(slice_index.stop - arr_start, 0)
            return slice(toxr__ofy, gmf__iqio, yedbg__fjqm)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        yigd__tjatj = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[yigd__tjatj])
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
        olx__ydy = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        uyczd__egzl = np.int32(numba_to_c_type(types.uint8))
        rma__dvuq = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            rzjy__fes = np.int32(10)
            tag = np.int32(11)
            nsf__rmwj = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                hyjhe__tukf = arr._data
                tpd__znnh = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    hyjhe__tukf, ind)
                fld__tsny = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    hyjhe__tukf, ind + 1)
                length = fld__tsny - tpd__znnh
                tvnn__mhgd = hyjhe__tukf[ind]
                nsf__rmwj[0] = length
                isend(nsf__rmwj, np.int32(1), root, rzjy__fes, True)
                isend(tvnn__mhgd, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(rma__dvuq,
                olx__ydy, 0, 1)
            tmnu__hrtha = 0
            if rank == root:
                tmnu__hrtha = recv(np.int64, ANY_SOURCE, rzjy__fes)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    rma__dvuq, olx__ydy, tmnu__hrtha, 1)
                cfrx__kcxta = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(cfrx__kcxta, np.int32(tmnu__hrtha), uyczd__egzl,
                    ANY_SOURCE, tag)
            dummy_use(nsf__rmwj)
            tmnu__hrtha = bcast_scalar(tmnu__hrtha)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    rma__dvuq, olx__ydy, tmnu__hrtha, 1)
            cfrx__kcxta = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(cfrx__kcxta, np.int32(tmnu__hrtha), uyczd__egzl, np.
                array([-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, tmnu__hrtha)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        rjk__syy = bodo.hiframes.pd_categorical_ext.get_categories_int_type(arr
            .dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, rjk__syy)
            if arr_start <= ind < arr_start + len(arr):
                ozl__pfos = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = ozl__pfos[ind - arr_start]
                send_arr = np.full(1, data, rjk__syy)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = rjk__syy(-1)
            if rank == root:
                val = recv(rjk__syy, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            iye__zlg = arr.dtype.categories[max(val, 0)]
            return iye__zlg
        return cat_getitem_impl
    mnoe__dqjqr = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, mnoe__dqjqr)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, mnoe__dqjqr)[0]
        if rank == root:
            val = recv(mnoe__dqjqr, ANY_SOURCE, tag)
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
    uynr__mpqtw = get_type_enum(out_data)
    assert typ_enum == uynr__mpqtw
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
    otypr__vub = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        otypr__vub += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    otypr__vub += '  return\n'
    mtf__nwqa = {}
    exec(otypr__vub, {'alltoallv': alltoallv}, mtf__nwqa)
    jjg__tdc = mtf__nwqa['f']
    return jjg__tdc


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    rpo__frclr = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return rpo__frclr, count


@numba.njit
def get_start(total_size, pes, rank):
    rpdr__lixqt = total_size % pes
    ojw__opdu = (total_size - rpdr__lixqt) // pes
    return rank * ojw__opdu + min(rank, rpdr__lixqt)


@numba.njit
def get_end(total_size, pes, rank):
    rpdr__lixqt = total_size % pes
    ojw__opdu = (total_size - rpdr__lixqt) // pes
    return (rank + 1) * ojw__opdu + min(rank + 1, rpdr__lixqt)


@numba.njit
def get_node_portion(total_size, pes, rank):
    rpdr__lixqt = total_size % pes
    ojw__opdu = (total_size - rpdr__lixqt) // pes
    if rank < rpdr__lixqt:
        return ojw__opdu + 1
    else:
        return ojw__opdu


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    zposc__lgun = in_arr.dtype(0)
    ptwwn__dugv = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        pubrh__bso = zposc__lgun
        for bioj__ryk in np.nditer(in_arr):
            pubrh__bso += bioj__ryk.item()
        pna__myv = dist_exscan(pubrh__bso, ptwwn__dugv)
        for i in range(in_arr.size):
            pna__myv += in_arr[i]
            out_arr[i] = pna__myv
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    yrtu__csvmt = in_arr.dtype(1)
    ptwwn__dugv = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        pubrh__bso = yrtu__csvmt
        for bioj__ryk in np.nditer(in_arr):
            pubrh__bso *= bioj__ryk.item()
        pna__myv = dist_exscan(pubrh__bso, ptwwn__dugv)
        if get_rank() == 0:
            pna__myv = yrtu__csvmt
        for i in range(in_arr.size):
            pna__myv *= in_arr[i]
            out_arr[i] = pna__myv
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        yrtu__csvmt = np.finfo(in_arr.dtype(1).dtype).max
    else:
        yrtu__csvmt = np.iinfo(in_arr.dtype(1).dtype).max
    ptwwn__dugv = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        pubrh__bso = yrtu__csvmt
        for bioj__ryk in np.nditer(in_arr):
            pubrh__bso = min(pubrh__bso, bioj__ryk.item())
        pna__myv = dist_exscan(pubrh__bso, ptwwn__dugv)
        if get_rank() == 0:
            pna__myv = yrtu__csvmt
        for i in range(in_arr.size):
            pna__myv = min(pna__myv, in_arr[i])
            out_arr[i] = pna__myv
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        yrtu__csvmt = np.finfo(in_arr.dtype(1).dtype).min
    else:
        yrtu__csvmt = np.iinfo(in_arr.dtype(1).dtype).min
    yrtu__csvmt = in_arr.dtype(1)
    ptwwn__dugv = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        pubrh__bso = yrtu__csvmt
        for bioj__ryk in np.nditer(in_arr):
            pubrh__bso = max(pubrh__bso, bioj__ryk.item())
        pna__myv = dist_exscan(pubrh__bso, ptwwn__dugv)
        if get_rank() == 0:
            pna__myv = yrtu__csvmt
        for i in range(in_arr.size):
            pna__myv = max(pna__myv, in_arr[i])
            out_arr[i] = pna__myv
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    dnu__mffq = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), dnu__mffq)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    jhd__qloa = args[0]
    if equiv_set.has_shape(jhd__qloa):
        return ArrayAnalysis.AnalyzeResult(shape=jhd__qloa, pre=[])
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
    tsaf__zect = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for 
        i, guqo__pdont in enumerate(args) if is_array_typ(guqo__pdont) or
        isinstance(guqo__pdont, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    otypr__vub = f"""def impl(*args):
    if {tsaf__zect} or bodo.get_rank() == 0:
        print(*args)"""
    mtf__nwqa = {}
    exec(otypr__vub, globals(), mtf__nwqa)
    impl = mtf__nwqa['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        zznvu__kufhs = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        otypr__vub = 'def f(req, cond=True):\n'
        otypr__vub += f'  return {zznvu__kufhs}\n'
        mtf__nwqa = {}
        exec(otypr__vub, {'_wait': _wait}, mtf__nwqa)
        impl = mtf__nwqa['f']
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
        rpdr__lixqt = 1
        for a in t:
            rpdr__lixqt *= a
        return rpdr__lixqt
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    wouv__hbw = np.ascontiguousarray(in_arr)
    yldcd__ieyyj = get_tuple_prod(wouv__hbw.shape[1:])
    yelx__inj = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        zvelh__mub = np.array(dest_ranks, dtype=np.int32)
    else:
        zvelh__mub = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, wouv__hbw.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * yelx__inj, dtype_size * yldcd__ieyyj, len
        (zvelh__mub), zvelh__mub.ctypes)
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
    jmmi__ktv = np.ascontiguousarray(rhs)
    idv__awozx = get_tuple_prod(jmmi__ktv.shape[1:])
    dplj__adjr = dtype_size * idv__awozx
    permutation_array_index(lhs.ctypes, lhs_len, dplj__adjr, jmmi__ktv.
        ctypes, jmmi__ktv.shape[0], p.ctypes, p_len, n_samples)
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
        otypr__vub = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        mtf__nwqa = {}
        exec(otypr__vub, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, mtf__nwqa)
        vnpep__mbxtq = mtf__nwqa['bcast_scalar_impl']
        return vnpep__mbxtq
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        vpezg__jabm = len(data.columns)
        ubuex__fjmf = ', '.join('g_data_{}'.format(i) for i in range(
            vpezg__jabm))
        zdl__jib = ColNamesMetaType(data.columns)
        otypr__vub = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(vpezg__jabm):
            otypr__vub += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            otypr__vub += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        otypr__vub += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        otypr__vub += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        otypr__vub += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(ubuex__fjmf))
        mtf__nwqa = {}
        exec(otypr__vub, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            zdl__jib}, mtf__nwqa)
        rbegw__ayu = mtf__nwqa['impl_df']
        return rbegw__ayu
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            rpo__frclr = data._start
            syv__jtcy = data._stop
            yedbg__fjqm = data._step
            npf__rpvk = data._name
            npf__rpvk = bcast_scalar(npf__rpvk, root)
            rpo__frclr = bcast_scalar(rpo__frclr, root)
            syv__jtcy = bcast_scalar(syv__jtcy, root)
            yedbg__fjqm = bcast_scalar(yedbg__fjqm, root)
            bnjh__pdceg = bodo.libs.array_kernels.calc_nitems(rpo__frclr,
                syv__jtcy, yedbg__fjqm)
            chunk_start = bodo.libs.distributed_api.get_start(bnjh__pdceg,
                n_pes, rank)
            epkv__tzxqr = bodo.libs.distributed_api.get_node_portion(
                bnjh__pdceg, n_pes, rank)
            toxr__ofy = rpo__frclr + yedbg__fjqm * chunk_start
            gmf__iqio = rpo__frclr + yedbg__fjqm * (chunk_start + epkv__tzxqr)
            gmf__iqio = min(gmf__iqio, syv__jtcy)
            return bodo.hiframes.pd_index_ext.init_range_index(toxr__ofy,
                gmf__iqio, yedbg__fjqm, npf__rpvk)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            wwn__ivi = data._data
            npf__rpvk = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(wwn__ivi,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, npf__rpvk)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            npf__rpvk = bodo.hiframes.pd_series_ext.get_series_name(data)
            onngn__muksl = bodo.libs.distributed_api.bcast_comm_impl(npf__rpvk,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            cfkw__ekl = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cfkw__ekl, onngn__muksl)
        return impl_series
    if isinstance(data, types.BaseTuple):
        otypr__vub = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        otypr__vub += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        mtf__nwqa = {}
        exec(otypr__vub, {'bcast_comm_impl': bcast_comm_impl}, mtf__nwqa)
        eggva__zdiax = mtf__nwqa['impl_tuple']
        return eggva__zdiax
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    nxudp__wtr = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    pde__jlft = (0,) * nxudp__wtr

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        wwn__ivi = np.ascontiguousarray(data)
        cfrx__kcxta = data.ctypes
        dor__kwyw = pde__jlft
        if rank == root:
            dor__kwyw = wwn__ivi.shape
        dor__kwyw = bcast_tuple(dor__kwyw, root)
        vadc__uki = get_tuple_prod(dor__kwyw[1:])
        send_counts = dor__kwyw[0] * vadc__uki
        mhz__goptp = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(cfrx__kcxta, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(mhz__goptp.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return mhz__goptp.reshape((-1,) + dor__kwyw[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        awlzy__bjagw = MPI.COMM_WORLD
        riy__zic = MPI.Get_processor_name()
        lra__axw = awlzy__bjagw.allgather(riy__zic)
        node_ranks = defaultdict(list)
        for i, aaxc__gkz in enumerate(lra__axw):
            node_ranks[aaxc__gkz].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    awlzy__bjagw = MPI.COMM_WORLD
    guie__nzepa = awlzy__bjagw.Get_group()
    olc__xqkl = guie__nzepa.Incl(comm_ranks)
    wbj__svcr = awlzy__bjagw.Create_group(olc__xqkl)
    return wbj__svcr


def get_nodes_first_ranks():
    lfa__mqj = get_host_ranks()
    return np.array([bmc__jlnp[0] for bmc__jlnp in lfa__mqj.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
