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
    fjjy__lcf = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, fjjy__lcf, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    fjjy__lcf = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, fjjy__lcf, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            fjjy__lcf = get_type_enum(arr)
            return _isend(arr.ctypes, size, fjjy__lcf, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        fjjy__lcf = np.int32(numba_to_c_type(arr.dtype))
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            oepa__ahwm = size + 7 >> 3
            qlia__hejvk = _isend(arr._data.ctypes, size, fjjy__lcf, pe, tag,
                cond)
            loebq__yxn = _isend(arr._null_bitmap.ctypes, oepa__ahwm,
                jcwro__bzq, pe, tag, cond)
            return qlia__hejvk, loebq__yxn
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        eic__vwrsi = np.int32(numba_to_c_type(offset_type))
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            gem__nwug = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(gem__nwug, pe, tag - 1)
            oepa__ahwm = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                eic__vwrsi, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), gem__nwug,
                jcwro__bzq, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                oepa__ahwm, jcwro__bzq, pe, tag)
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
            fjjy__lcf = get_type_enum(arr)
            return _irecv(arr.ctypes, size, fjjy__lcf, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        fjjy__lcf = np.int32(numba_to_c_type(arr.dtype))
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            oepa__ahwm = size + 7 >> 3
            qlia__hejvk = _irecv(arr._data.ctypes, size, fjjy__lcf, pe, tag,
                cond)
            loebq__yxn = _irecv(arr._null_bitmap.ctypes, oepa__ahwm,
                jcwro__bzq, pe, tag, cond)
            return qlia__hejvk, loebq__yxn
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        eic__vwrsi = np.int32(numba_to_c_type(offset_type))
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            rbkao__xuw = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            rbkao__xuw = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        fcqcj__gbf = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {rbkao__xuw}(size, n_chars)
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
        ogqd__xzv = dict()
        exec(fcqcj__gbf, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            eic__vwrsi, 'char_typ_enum': jcwro__bzq}, ogqd__xzv)
        impl = ogqd__xzv['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    fjjy__lcf = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), fjjy__lcf)


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
        cpdez__bzae = n_pes if rank == root or allgather else 0
        mzayz__bmdvl = np.empty(cpdez__bzae, dtype)
        c_gather_scalar(send.ctypes, mzayz__bmdvl.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return mzayz__bmdvl
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
        vxvqe__jcpzx = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], vxvqe__jcpzx)
        return builder.bitcast(vxvqe__jcpzx, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        vxvqe__jcpzx = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(vxvqe__jcpzx)
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
    dxyb__rhu = types.unliteral(value)
    if isinstance(dxyb__rhu, IndexValueType):
        dxyb__rhu = dxyb__rhu.val_typ
        jzb__dvteu = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            jzb__dvteu.append(types.int64)
            jzb__dvteu.append(bodo.datetime64ns)
            jzb__dvteu.append(bodo.timedelta64ns)
            jzb__dvteu.append(bodo.datetime_date_type)
        if dxyb__rhu not in jzb__dvteu:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(dxyb__rhu))
    typ_enum = np.int32(numba_to_c_type(dxyb__rhu))

    def impl(value, reduce_op):
        vbo__hvx = value_to_ptr(value)
        ubsg__ptwal = value_to_ptr(value)
        _dist_reduce(vbo__hvx, ubsg__ptwal, reduce_op, typ_enum)
        return load_val_ptr(ubsg__ptwal, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    dxyb__rhu = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(dxyb__rhu))
    aodxs__ueb = dxyb__rhu(0)

    def impl(value, reduce_op):
        vbo__hvx = value_to_ptr(value)
        ubsg__ptwal = value_to_ptr(aodxs__ueb)
        _dist_exscan(vbo__hvx, ubsg__ptwal, reduce_op, typ_enum)
        return load_val_ptr(ubsg__ptwal, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    hrfc__kuqm = 0
    tain__wiiro = 0
    for i in range(len(recv_counts)):
        hyf__iun = recv_counts[i]
        oepa__ahwm = recv_counts_nulls[i]
        jpovi__vcgbx = tmp_null_bytes[hrfc__kuqm:hrfc__kuqm + oepa__ahwm]
        for zhld__mnipc in range(hyf__iun):
            set_bit_to(null_bitmap_ptr, tain__wiiro, get_bit(jpovi__vcgbx,
                zhld__mnipc))
            tain__wiiro += 1
        hrfc__kuqm += oepa__ahwm


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            fcq__kkxfs = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                fcq__kkxfs, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            yjrlo__dpri = data.size
            recv_counts = gather_scalar(np.int32(yjrlo__dpri), allgather,
                root=root)
            rgb__esnhc = recv_counts.sum()
            uewcy__uvi = empty_like_type(rgb__esnhc, data)
            mlbq__atenl = np.empty(1, np.int32)
            if rank == root or allgather:
                mlbq__atenl = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(yjrlo__dpri), uewcy__uvi.ctypes,
                recv_counts.ctypes, mlbq__atenl.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return uewcy__uvi.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            uewcy__uvi = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(uewcy__uvi)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            uewcy__uvi = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(uewcy__uvi)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            yjrlo__dpri = len(data)
            oepa__ahwm = yjrlo__dpri + 7 >> 3
            recv_counts = gather_scalar(np.int32(yjrlo__dpri), allgather,
                root=root)
            rgb__esnhc = recv_counts.sum()
            uewcy__uvi = empty_like_type(rgb__esnhc, data)
            mlbq__atenl = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            pplis__dvcc = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mlbq__atenl = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                pplis__dvcc = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(yjrlo__dpri),
                uewcy__uvi._days_data.ctypes, recv_counts.ctypes,
                mlbq__atenl.ctypes, np.int32(typ_val), allgather, np.int32(
                root))
            c_gatherv(data._seconds_data.ctypes, np.int32(yjrlo__dpri),
                uewcy__uvi._seconds_data.ctypes, recv_counts.ctypes,
                mlbq__atenl.ctypes, np.int32(typ_val), allgather, np.int32(
                root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(yjrlo__dpri),
                uewcy__uvi._microseconds_data.ctypes, recv_counts.ctypes,
                mlbq__atenl.ctypes, np.int32(typ_val), allgather, np.int32(
                root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(oepa__ahwm),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                pplis__dvcc.ctypes, jcwro__bzq, allgather, np.int32(root))
            copy_gathered_null_bytes(uewcy__uvi._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return uewcy__uvi
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            yjrlo__dpri = len(data)
            oepa__ahwm = yjrlo__dpri + 7 >> 3
            recv_counts = gather_scalar(np.int32(yjrlo__dpri), allgather,
                root=root)
            rgb__esnhc = recv_counts.sum()
            uewcy__uvi = empty_like_type(rgb__esnhc, data)
            mlbq__atenl = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            pplis__dvcc = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mlbq__atenl = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                pplis__dvcc = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(yjrlo__dpri), uewcy__uvi.
                _data.ctypes, recv_counts.ctypes, mlbq__atenl.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(oepa__ahwm),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                pplis__dvcc.ctypes, jcwro__bzq, allgather, np.int32(root))
            copy_gathered_null_bytes(uewcy__uvi._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return uewcy__uvi
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        pduw__ksf = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rxcld__ofv = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                rxcld__ofv, pduw__ksf)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            vgc__itsq = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            gjk__hwgi = bodo.gatherv(data._right, allgather, warn_if_rep, root)
            return bodo.libs.interval_arr_ext.init_interval_array(vgc__itsq,
                gjk__hwgi)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            kxrui__pyn = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            rqs__nzfga = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rqs__nzfga, kxrui__pyn)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        dtx__xwaii = np.iinfo(np.int64).max
        xchae__qtwxa = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            dpvxa__jwezp = data._start
            gdbqu__gvfzn = data._stop
            if len(data) == 0:
                dpvxa__jwezp = dtx__xwaii
                gdbqu__gvfzn = xchae__qtwxa
            dpvxa__jwezp = bodo.libs.distributed_api.dist_reduce(dpvxa__jwezp,
                np.int32(Reduce_Type.Min.value))
            gdbqu__gvfzn = bodo.libs.distributed_api.dist_reduce(gdbqu__gvfzn,
                np.int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if dpvxa__jwezp == dtx__xwaii and gdbqu__gvfzn == xchae__qtwxa:
                dpvxa__jwezp = 0
                gdbqu__gvfzn = 0
            imtlp__vjcil = max(0, -(-(gdbqu__gvfzn - dpvxa__jwezp) // data.
                _step))
            if imtlp__vjcil < total_len:
                gdbqu__gvfzn = dpvxa__jwezp + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                dpvxa__jwezp = 0
                gdbqu__gvfzn = 0
            return bodo.hiframes.pd_index_ext.init_range_index(dpvxa__jwezp,
                gdbqu__gvfzn, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            xzv__hmwg = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, xzv__hmwg)
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
            uewcy__uvi = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(uewcy__uvi
                , data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        dobjj__ehuyr = {'bodo': bodo, 'get_table_block': bodo.hiframes.
            table.get_table_block, 'ensure_column_unboxed': bodo.hiframes.
            table.ensure_column_unboxed, 'set_table_block': bodo.hiframes.
            table.set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        fcqcj__gbf = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        fcqcj__gbf += '  T = data\n'
        fcqcj__gbf += '  T2 = init_table(T, True)\n'
        for tznb__abzf in data.type_to_blk.values():
            dobjj__ehuyr[f'arr_inds_{tznb__abzf}'] = np.array(data.
                block_to_arr_ind[tznb__abzf], dtype=np.int64)
            fcqcj__gbf += (
                f'  arr_list_{tznb__abzf} = get_table_block(T, {tznb__abzf})\n'
                )
            fcqcj__gbf += f"""  out_arr_list_{tznb__abzf} = alloc_list_like(arr_list_{tznb__abzf}, len(arr_list_{tznb__abzf}), True)
"""
            fcqcj__gbf += f'  for i in range(len(arr_list_{tznb__abzf})):\n'
            fcqcj__gbf += (
                f'    arr_ind_{tznb__abzf} = arr_inds_{tznb__abzf}[i]\n')
            fcqcj__gbf += f"""    ensure_column_unboxed(T, arr_list_{tznb__abzf}, i, arr_ind_{tznb__abzf})
"""
            fcqcj__gbf += f"""    out_arr_{tznb__abzf} = bodo.gatherv(arr_list_{tznb__abzf}[i], allgather, warn_if_rep, root)
"""
            fcqcj__gbf += (
                f'    out_arr_list_{tznb__abzf}[i] = out_arr_{tznb__abzf}\n')
            fcqcj__gbf += (
                f'  T2 = set_table_block(T2, out_arr_list_{tznb__abzf}, {tznb__abzf})\n'
                )
        fcqcj__gbf += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        fcqcj__gbf += f'  T2 = set_table_len(T2, length)\n'
        fcqcj__gbf += f'  return T2\n'
        ogqd__xzv = {}
        exec(fcqcj__gbf, dobjj__ehuyr, ogqd__xzv)
        hnkh__jml = ogqd__xzv['impl_table']
        return hnkh__jml
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        kwen__ixlb = len(data.columns)
        if kwen__ixlb == 0:
            jyn__zzwk = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                irbwp__huwa = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    irbwp__huwa, jyn__zzwk)
            return impl
        tfo__pdfhj = ', '.join(f'g_data_{i}' for i in range(kwen__ixlb))
        fcqcj__gbf = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            kbvvh__xoy = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            tfo__pdfhj = 'T2'
            fcqcj__gbf += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            fcqcj__gbf += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(kwen__ixlb):
                fcqcj__gbf += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                fcqcj__gbf += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        fcqcj__gbf += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        fcqcj__gbf += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        fcqcj__gbf += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(tfo__pdfhj))
        ogqd__xzv = {}
        dobjj__ehuyr = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(fcqcj__gbf, dobjj__ehuyr, ogqd__xzv)
        mlbcl__dbiz = ogqd__xzv['impl_df']
        return mlbcl__dbiz
    if isinstance(data, ArrayItemArrayType):
        wdp__yuakp = np.int32(numba_to_c_type(types.int32))
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            mwiz__vtp = bodo.libs.array_item_arr_ext.get_offsets(data)
            pid__ixqs = bodo.libs.array_item_arr_ext.get_data(data)
            pid__ixqs = pid__ixqs[:mwiz__vtp[-1]]
            eyxqb__vgksl = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            yjrlo__dpri = len(data)
            svblu__tbyy = np.empty(yjrlo__dpri, np.uint32)
            oepa__ahwm = yjrlo__dpri + 7 >> 3
            for i in range(yjrlo__dpri):
                svblu__tbyy[i] = mwiz__vtp[i + 1] - mwiz__vtp[i]
            recv_counts = gather_scalar(np.int32(yjrlo__dpri), allgather,
                root=root)
            rgb__esnhc = recv_counts.sum()
            mlbq__atenl = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            pplis__dvcc = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mlbq__atenl = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for pdpc__aiju in range(len(recv_counts)):
                    recv_counts_nulls[pdpc__aiju] = recv_counts[pdpc__aiju
                        ] + 7 >> 3
                pplis__dvcc = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            sdzkn__mlpb = np.empty(rgb__esnhc + 1, np.uint32)
            kkddk__bcoce = bodo.gatherv(pid__ixqs, allgather, warn_if_rep, root
                )
            mlgx__nhq = np.empty(rgb__esnhc + 7 >> 3, np.uint8)
            c_gatherv(svblu__tbyy.ctypes, np.int32(yjrlo__dpri),
                sdzkn__mlpb.ctypes, recv_counts.ctypes, mlbq__atenl.ctypes,
                wdp__yuakp, allgather, np.int32(root))
            c_gatherv(eyxqb__vgksl.ctypes, np.int32(oepa__ahwm),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                pplis__dvcc.ctypes, jcwro__bzq, allgather, np.int32(root))
            dummy_use(data)
            mfmbp__eou = np.empty(rgb__esnhc + 1, np.uint64)
            convert_len_arr_to_offset(sdzkn__mlpb.ctypes, mfmbp__eou.ctypes,
                rgb__esnhc)
            copy_gathered_null_bytes(mlgx__nhq.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                rgb__esnhc, kkddk__bcoce, mfmbp__eou, mlgx__nhq)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        dsa__gsptp = data.names
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vyel__uvoh = bodo.libs.struct_arr_ext.get_data(data)
            kehc__iwhqb = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            ioy__maya = bodo.gatherv(vyel__uvoh, allgather=allgather, root=root
                )
            rank = bodo.libs.distributed_api.get_rank()
            yjrlo__dpri = len(data)
            oepa__ahwm = yjrlo__dpri + 7 >> 3
            recv_counts = gather_scalar(np.int32(yjrlo__dpri), allgather,
                root=root)
            rgb__esnhc = recv_counts.sum()
            rma__nerkn = np.empty(rgb__esnhc + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            pplis__dvcc = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                pplis__dvcc = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(kehc__iwhqb.ctypes, np.int32(oepa__ahwm),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                pplis__dvcc.ctypes, jcwro__bzq, allgather, np.int32(root))
            copy_gathered_null_bytes(rma__nerkn.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(ioy__maya,
                rma__nerkn, dsa__gsptp)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            uewcy__uvi = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(uewcy__uvi)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            uewcy__uvi = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(uewcy__uvi)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            uewcy__uvi = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(uewcy__uvi)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            uewcy__uvi = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            jflm__olzo = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            nesr__tzmn = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            tfrh__gly = gather_scalar(data.shape[0], allgather, root=root)
            vfx__jizqh = tfrh__gly.sum()
            kwen__ixlb = bodo.libs.distributed_api.dist_reduce(data.shape[1
                ], np.int32(Reduce_Type.Max.value))
            yvar__twz = np.empty(vfx__jizqh + 1, np.int64)
            jflm__olzo = jflm__olzo.astype(np.int64)
            yvar__twz[0] = 0
            mizpz__oli = 1
            fmlp__bees = 0
            for lbtk__nzpfb in tfrh__gly:
                for grrkf__wcswb in range(lbtk__nzpfb):
                    vfzkl__eaax = nesr__tzmn[fmlp__bees + 1] - nesr__tzmn[
                        fmlp__bees]
                    yvar__twz[mizpz__oli] = yvar__twz[mizpz__oli - 1
                        ] + vfzkl__eaax
                    mizpz__oli += 1
                    fmlp__bees += 1
                fmlp__bees += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(uewcy__uvi,
                jflm__olzo, yvar__twz, (vfx__jizqh, kwen__ixlb))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        fcqcj__gbf = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        fcqcj__gbf += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        ogqd__xzv = {}
        exec(fcqcj__gbf, {'bodo': bodo}, ogqd__xzv)
        vizoi__nucph = ogqd__xzv['impl_tuple']
        return vizoi__nucph
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    fcqcj__gbf = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    fcqcj__gbf += '    if random:\n'
    fcqcj__gbf += '        if random_seed is None:\n'
    fcqcj__gbf += '            random = 1\n'
    fcqcj__gbf += '        else:\n'
    fcqcj__gbf += '            random = 2\n'
    fcqcj__gbf += '    if random_seed is None:\n'
    fcqcj__gbf += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        rbhw__coh = data
        kwen__ixlb = len(rbhw__coh.columns)
        for i in range(kwen__ixlb):
            fcqcj__gbf += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        fcqcj__gbf += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        tfo__pdfhj = ', '.join(f'data_{i}' for i in range(kwen__ixlb))
        fcqcj__gbf += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(tkxbr__kjrgb) for
            tkxbr__kjrgb in range(kwen__ixlb))))
        fcqcj__gbf += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        fcqcj__gbf += '    if dests is None:\n'
        fcqcj__gbf += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        fcqcj__gbf += '    else:\n'
        fcqcj__gbf += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for byz__jzyz in range(kwen__ixlb):
            fcqcj__gbf += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(byz__jzyz))
        fcqcj__gbf += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(kwen__ixlb))
        fcqcj__gbf += '    delete_table(out_table)\n'
        fcqcj__gbf += '    if parallel:\n'
        fcqcj__gbf += '        delete_table(table_total)\n'
        tfo__pdfhj = ', '.join('out_arr_{}'.format(i) for i in range(
            kwen__ixlb))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        fcqcj__gbf += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(tfo__pdfhj, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        fcqcj__gbf += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        fcqcj__gbf += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        fcqcj__gbf += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        fcqcj__gbf += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        fcqcj__gbf += '    if dests is None:\n'
        fcqcj__gbf += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        fcqcj__gbf += '    else:\n'
        fcqcj__gbf += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        fcqcj__gbf += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        fcqcj__gbf += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        fcqcj__gbf += '    delete_table(out_table)\n'
        fcqcj__gbf += '    if parallel:\n'
        fcqcj__gbf += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        fcqcj__gbf += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        fcqcj__gbf += '    if not parallel:\n'
        fcqcj__gbf += '        return data\n'
        fcqcj__gbf += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        fcqcj__gbf += '    if dests is None:\n'
        fcqcj__gbf += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        fcqcj__gbf += '    elif bodo.get_rank() not in dests:\n'
        fcqcj__gbf += '        dim0_local_size = 0\n'
        fcqcj__gbf += '    else:\n'
        fcqcj__gbf += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        fcqcj__gbf += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        fcqcj__gbf += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        fcqcj__gbf += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        fcqcj__gbf += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        fcqcj__gbf += '    if dests is None:\n'
        fcqcj__gbf += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        fcqcj__gbf += '    else:\n'
        fcqcj__gbf += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        fcqcj__gbf += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        fcqcj__gbf += '    delete_table(out_table)\n'
        fcqcj__gbf += '    if parallel:\n'
        fcqcj__gbf += '        delete_table(table_total)\n'
        fcqcj__gbf += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    ogqd__xzv = {}
    dobjj__ehuyr = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.
        array.array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        dobjj__ehuyr.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(rbhw__coh.columns)})
    exec(fcqcj__gbf, dobjj__ehuyr, ogqd__xzv)
    impl = ogqd__xzv['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    fcqcj__gbf = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        fcqcj__gbf += '    if seed is None:\n'
        fcqcj__gbf += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        fcqcj__gbf += '    np.random.seed(seed)\n'
        fcqcj__gbf += '    if not parallel:\n'
        fcqcj__gbf += '        data = data.copy()\n'
        fcqcj__gbf += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            fcqcj__gbf += '        data = data[:n_samples]\n'
        fcqcj__gbf += '        return data\n'
        fcqcj__gbf += '    else:\n'
        fcqcj__gbf += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        fcqcj__gbf += '        permutation = np.arange(dim0_global_size)\n'
        fcqcj__gbf += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            fcqcj__gbf += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            fcqcj__gbf += '        n_samples = dim0_global_size\n'
        fcqcj__gbf += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        fcqcj__gbf += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        fcqcj__gbf += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        fcqcj__gbf += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        fcqcj__gbf += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        fcqcj__gbf += '        return output\n'
    else:
        fcqcj__gbf += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            fcqcj__gbf += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            fcqcj__gbf += '    output = output[:local_n_samples]\n'
        fcqcj__gbf += '    return output\n'
    ogqd__xzv = {}
    exec(fcqcj__gbf, {'np': np, 'bodo': bodo}, ogqd__xzv)
    impl = ogqd__xzv['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    sjsih__skoh = np.empty(sendcounts_nulls.sum(), np.uint8)
    hrfc__kuqm = 0
    tain__wiiro = 0
    for rrnff__smi in range(len(sendcounts)):
        hyf__iun = sendcounts[rrnff__smi]
        oepa__ahwm = sendcounts_nulls[rrnff__smi]
        jpovi__vcgbx = sjsih__skoh[hrfc__kuqm:hrfc__kuqm + oepa__ahwm]
        for zhld__mnipc in range(hyf__iun):
            set_bit_to_arr(jpovi__vcgbx, zhld__mnipc, get_bit_bitmap(
                null_bitmap_ptr, tain__wiiro))
            tain__wiiro += 1
        hrfc__kuqm += oepa__ahwm
    return sjsih__skoh


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    ghlcz__gizr = MPI.COMM_WORLD
    data = ghlcz__gizr.bcast(data, root)
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
    sanbn__uspf = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    ldut__vufx = (0,) * sanbn__uspf

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        uzsfh__hbv = np.ascontiguousarray(data)
        upgay__oao = data.ctypes
        jse__dwgvz = ldut__vufx
        if rank == MPI_ROOT:
            jse__dwgvz = uzsfh__hbv.shape
        jse__dwgvz = bcast_tuple(jse__dwgvz)
        wvlex__twe = get_tuple_prod(jse__dwgvz[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            jse__dwgvz[0])
        send_counts *= wvlex__twe
        yjrlo__dpri = send_counts[rank]
        zvtfp__cplt = np.empty(yjrlo__dpri, dtype)
        mlbq__atenl = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(upgay__oao, send_counts.ctypes, mlbq__atenl.ctypes,
            zvtfp__cplt.ctypes, np.int32(yjrlo__dpri), np.int32(typ_val))
        return zvtfp__cplt.reshape((-1,) + jse__dwgvz[1:])
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
        kell__qnac = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], kell__qnac)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        kxrui__pyn = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=kxrui__pyn)
        uhsd__lvy = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(uhsd__lvy)
        return pd.Index(arr, name=kxrui__pyn)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        kxrui__pyn = _get_name_value_for_type(dtype.name_typ)
        dsa__gsptp = tuple(_get_name_value_for_type(t) for t in dtype.names_typ
            )
        kvd__scr = tuple(get_value_for_type(t) for t in dtype.array_types)
        kvd__scr = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in kvd__scr)
        val = pd.MultiIndex.from_arrays(kvd__scr, names=dsa__gsptp)
        val.name = kxrui__pyn
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        kxrui__pyn = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=kxrui__pyn)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        kvd__scr = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({kxrui__pyn: arr for kxrui__pyn, arr in zip(
            dtype.columns, kvd__scr)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        uhsd__lvy = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(uhsd__lvy[0], uhsd__lvy
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
        wdp__yuakp = np.int32(numba_to_c_type(types.int32))
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            rbkao__xuw = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            rbkao__xuw = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        fcqcj__gbf = f"""def impl(
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
            recv_arr = {rbkao__xuw}(n_loc, n_loc_char)

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
        ogqd__xzv = dict()
        exec(fcqcj__gbf, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            wdp__yuakp, 'char_typ_enum': jcwro__bzq, 'decode_if_dict_array':
            decode_if_dict_array}, ogqd__xzv)
        impl = ogqd__xzv['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        wdp__yuakp = np.int32(numba_to_c_type(types.int32))
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            anbtx__cxz = bodo.libs.array_item_arr_ext.get_offsets(data)
            nelse__oslev = bodo.libs.array_item_arr_ext.get_data(data)
            nelse__oslev = nelse__oslev[:anbtx__cxz[-1]]
            mchw__ocg = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            ymro__jtwhs = bcast_scalar(len(data))
            mnbov__zvv = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                mnbov__zvv[i] = anbtx__cxz[i + 1] - anbtx__cxz[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                ymro__jtwhs)
            mlbq__atenl = bodo.ir.join.calc_disp(send_counts)
            ytiiq__rhf = np.empty(n_pes, np.int32)
            if rank == 0:
                pvzen__eekq = 0
                for i in range(n_pes):
                    ftom__ohvw = 0
                    for grrkf__wcswb in range(send_counts[i]):
                        ftom__ohvw += mnbov__zvv[pvzen__eekq]
                        pvzen__eekq += 1
                    ytiiq__rhf[i] = ftom__ohvw
            bcast(ytiiq__rhf)
            tpxu__qyb = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                tpxu__qyb[i] = send_counts[i] + 7 >> 3
            pplis__dvcc = bodo.ir.join.calc_disp(tpxu__qyb)
            yjrlo__dpri = send_counts[rank]
            vlgh__muwrd = np.empty(yjrlo__dpri + 1, np_offset_type)
            ckzfy__csoco = bodo.libs.distributed_api.scatterv_impl(nelse__oslev
                , ytiiq__rhf)
            suwbf__zowy = yjrlo__dpri + 7 >> 3
            pmzxu__yegf = np.empty(suwbf__zowy, np.uint8)
            ylx__ytqe = np.empty(yjrlo__dpri, np.uint32)
            c_scatterv(mnbov__zvv.ctypes, send_counts.ctypes, mlbq__atenl.
                ctypes, ylx__ytqe.ctypes, np.int32(yjrlo__dpri), wdp__yuakp)
            convert_len_arr_to_offset(ylx__ytqe.ctypes, vlgh__muwrd.ctypes,
                yjrlo__dpri)
            uju__obep = get_scatter_null_bytes_buff(mchw__ocg.ctypes,
                send_counts, tpxu__qyb)
            c_scatterv(uju__obep.ctypes, tpxu__qyb.ctypes, pplis__dvcc.
                ctypes, pmzxu__yegf.ctypes, np.int32(suwbf__zowy), jcwro__bzq)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                yjrlo__dpri, ckzfy__csoco, vlgh__muwrd, pmzxu__yegf)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            rmdb__nilzy = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            rmdb__nilzy = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            rmdb__nilzy = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            rmdb__nilzy = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            uzsfh__hbv = data._data
            kehc__iwhqb = data._null_bitmap
            ytqzz__yjpx = len(uzsfh__hbv)
            huldv__exv = _scatterv_np(uzsfh__hbv, send_counts)
            ymro__jtwhs = bcast_scalar(ytqzz__yjpx)
            fcov__lqbu = len(huldv__exv) + 7 >> 3
            wujrv__zpe = np.empty(fcov__lqbu, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                ymro__jtwhs)
            tpxu__qyb = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                tpxu__qyb[i] = send_counts[i] + 7 >> 3
            pplis__dvcc = bodo.ir.join.calc_disp(tpxu__qyb)
            uju__obep = get_scatter_null_bytes_buff(kehc__iwhqb.ctypes,
                send_counts, tpxu__qyb)
            c_scatterv(uju__obep.ctypes, tpxu__qyb.ctypes, pplis__dvcc.
                ctypes, wujrv__zpe.ctypes, np.int32(fcov__lqbu), jcwro__bzq)
            return rmdb__nilzy(huldv__exv, wujrv__zpe)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            fjkf__oouq = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            rtb__vry = bodo.libs.distributed_api.scatterv_impl(data._right,
                send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(fjkf__oouq,
                rtb__vry)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            dpvxa__jwezp = data._start
            gdbqu__gvfzn = data._stop
            ijk__egzm = data._step
            kxrui__pyn = data._name
            kxrui__pyn = bcast_scalar(kxrui__pyn)
            dpvxa__jwezp = bcast_scalar(dpvxa__jwezp)
            gdbqu__gvfzn = bcast_scalar(gdbqu__gvfzn)
            ijk__egzm = bcast_scalar(ijk__egzm)
            cge__tbsd = bodo.libs.array_kernels.calc_nitems(dpvxa__jwezp,
                gdbqu__gvfzn, ijk__egzm)
            chunk_start = bodo.libs.distributed_api.get_start(cge__tbsd,
                n_pes, rank)
            moees__fczk = bodo.libs.distributed_api.get_node_portion(cge__tbsd,
                n_pes, rank)
            pvj__jth = dpvxa__jwezp + ijk__egzm * chunk_start
            vynz__yapd = dpvxa__jwezp + ijk__egzm * (chunk_start + moees__fczk)
            vynz__yapd = min(vynz__yapd, gdbqu__gvfzn)
            return bodo.hiframes.pd_index_ext.init_range_index(pvj__jth,
                vynz__yapd, ijk__egzm, kxrui__pyn)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        xzv__hmwg = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            uzsfh__hbv = data._data
            kxrui__pyn = data._name
            kxrui__pyn = bcast_scalar(kxrui__pyn)
            arr = bodo.libs.distributed_api.scatterv_impl(uzsfh__hbv,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                kxrui__pyn, xzv__hmwg)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            uzsfh__hbv = data._data
            kxrui__pyn = data._name
            kxrui__pyn = bcast_scalar(kxrui__pyn)
            arr = bodo.libs.distributed_api.scatterv_impl(uzsfh__hbv,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, kxrui__pyn)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            uewcy__uvi = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            kxrui__pyn = bcast_scalar(data._name)
            dsa__gsptp = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(uewcy__uvi
                , dsa__gsptp, kxrui__pyn)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            kxrui__pyn = bodo.hiframes.pd_series_ext.get_series_name(data)
            aekc__yuoqt = bcast_scalar(kxrui__pyn)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            rqs__nzfga = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rqs__nzfga, aekc__yuoqt)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        kwen__ixlb = len(data.columns)
        tfo__pdfhj = ', '.join('g_data_{}'.format(i) for i in range(kwen__ixlb)
            )
        ltl__zsrs = ColNamesMetaType(data.columns)
        fcqcj__gbf = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(kwen__ixlb):
            fcqcj__gbf += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            fcqcj__gbf += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        fcqcj__gbf += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        fcqcj__gbf += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        fcqcj__gbf += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({tfo__pdfhj},), g_index, __col_name_meta_scaterv_impl)
"""
        ogqd__xzv = {}
        exec(fcqcj__gbf, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            ltl__zsrs}, ogqd__xzv)
        mlbcl__dbiz = ogqd__xzv['impl_df']
        return mlbcl__dbiz
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            fcq__kkxfs = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                fcq__kkxfs, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        fcqcj__gbf = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        fcqcj__gbf += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        ogqd__xzv = {}
        exec(fcqcj__gbf, {'bodo': bodo}, ogqd__xzv)
        vizoi__nucph = ogqd__xzv['impl_tuple']
        return vizoi__nucph
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
        eic__vwrsi = np.int32(numba_to_c_type(offset_type))
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            yjrlo__dpri = len(data)
            zpqy__xly = num_total_chars(data)
            assert yjrlo__dpri < INT_MAX
            assert zpqy__xly < INT_MAX
            yhud__idqc = get_offset_ptr(data)
            upgay__oao = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            oepa__ahwm = yjrlo__dpri + 7 >> 3
            c_bcast(yhud__idqc, np.int32(yjrlo__dpri + 1), eic__vwrsi, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(upgay__oao, np.int32(zpqy__xly), jcwro__bzq, np.array([
                -1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(oepa__ahwm), jcwro__bzq, np.
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
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                aldb__idg = 0
                uszeu__qfdq = np.empty(0, np.uint8).ctypes
            else:
                uszeu__qfdq, aldb__idg = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            aldb__idg = bodo.libs.distributed_api.bcast_scalar(aldb__idg, root)
            if rank != root:
                lanb__rgc = np.empty(aldb__idg + 1, np.uint8)
                lanb__rgc[aldb__idg] = 0
                uszeu__qfdq = lanb__rgc.ctypes
            c_bcast(uszeu__qfdq, np.int32(aldb__idg), jcwro__bzq, np.array(
                [-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(uszeu__qfdq, aldb__idg)
        return impl_str
    typ_val = numba_to_c_type(val)
    fcqcj__gbf = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    ogqd__xzv = {}
    exec(fcqcj__gbf, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, ogqd__xzv)
    sgy__buerc = ogqd__xzv['bcast_scalar_impl']
    return sgy__buerc


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    swgjn__mne = len(val)
    fcqcj__gbf = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    fcqcj__gbf += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(swgjn__mne)),
        ',' if swgjn__mne else '')
    ogqd__xzv = {}
    exec(fcqcj__gbf, {'bcast_scalar': bcast_scalar}, ogqd__xzv)
    rpkt__fpc = ogqd__xzv['bcast_tuple_impl']
    return rpkt__fpc


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            yjrlo__dpri = bcast_scalar(len(arr), root)
            zmfw__bjurl = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(yjrlo__dpri, zmfw__bjurl)
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
            pvj__jth = max(arr_start, slice_index.start) - arr_start
            vynz__yapd = max(slice_index.stop - arr_start, 0)
            return slice(pvj__jth, vynz__yapd)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            dpvxa__jwezp = slice_index.start
            ijk__egzm = slice_index.step
            vjes__pyw = (0 if ijk__egzm == 1 or dpvxa__jwezp > arr_start else
                abs(ijk__egzm - arr_start % ijk__egzm) % ijk__egzm)
            pvj__jth = max(arr_start, slice_index.start
                ) - arr_start + vjes__pyw
            vynz__yapd = max(slice_index.stop - arr_start, 0)
            return slice(pvj__jth, vynz__yapd, ijk__egzm)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        fep__jegm = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[fep__jegm])
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
        wkfnv__gbk = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        jcwro__bzq = np.int32(numba_to_c_type(types.uint8))
        nbdd__zvth = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            jpmqs__jil = np.int32(10)
            tag = np.int32(11)
            nca__cxdq = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                pid__ixqs = arr._data
                emg__krbr = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    pid__ixqs, ind)
                lukkb__tdpq = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    pid__ixqs, ind + 1)
                length = lukkb__tdpq - emg__krbr
                vxvqe__jcpzx = pid__ixqs[ind]
                nca__cxdq[0] = length
                isend(nca__cxdq, np.int32(1), root, jpmqs__jil, True)
                isend(vxvqe__jcpzx, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(nbdd__zvth
                , wkfnv__gbk, 0, 1)
            imtlp__vjcil = 0
            if rank == root:
                imtlp__vjcil = recv(np.int64, ANY_SOURCE, jpmqs__jil)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    nbdd__zvth, wkfnv__gbk, imtlp__vjcil, 1)
                upgay__oao = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(upgay__oao, np.int32(imtlp__vjcil), jcwro__bzq,
                    ANY_SOURCE, tag)
            dummy_use(nca__cxdq)
            imtlp__vjcil = bcast_scalar(imtlp__vjcil)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    nbdd__zvth, wkfnv__gbk, imtlp__vjcil, 1)
            upgay__oao = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(upgay__oao, np.int32(imtlp__vjcil), jcwro__bzq, np.
                array([-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, imtlp__vjcil)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        vdgo__lvdl = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, vdgo__lvdl)
            if arr_start <= ind < arr_start + len(arr):
                fcq__kkxfs = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = fcq__kkxfs[ind - arr_start]
                send_arr = np.full(1, data, vdgo__lvdl)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = vdgo__lvdl(-1)
            if rank == root:
                val = recv(vdgo__lvdl, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            bpvs__gmedg = arr.dtype.categories[max(val, 0)]
            return bpvs__gmedg
        return cat_getitem_impl
    zjr__odua = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, zjr__odua)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, zjr__odua)[0]
        if rank == root:
            val = recv(zjr__odua, ANY_SOURCE, tag)
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
    ygs__ntgpo = get_type_enum(out_data)
    assert typ_enum == ygs__ntgpo
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
    fcqcj__gbf = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        fcqcj__gbf += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    fcqcj__gbf += '  return\n'
    ogqd__xzv = {}
    exec(fcqcj__gbf, {'alltoallv': alltoallv}, ogqd__xzv)
    vwd__bqek = ogqd__xzv['f']
    return vwd__bqek


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    dpvxa__jwezp = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return dpvxa__jwezp, count


@numba.njit
def get_start(total_size, pes, rank):
    mzayz__bmdvl = total_size % pes
    sdi__zyfe = (total_size - mzayz__bmdvl) // pes
    return rank * sdi__zyfe + min(rank, mzayz__bmdvl)


@numba.njit
def get_end(total_size, pes, rank):
    mzayz__bmdvl = total_size % pes
    sdi__zyfe = (total_size - mzayz__bmdvl) // pes
    return (rank + 1) * sdi__zyfe + min(rank + 1, mzayz__bmdvl)


@numba.njit
def get_node_portion(total_size, pes, rank):
    mzayz__bmdvl = total_size % pes
    sdi__zyfe = (total_size - mzayz__bmdvl) // pes
    if rank < mzayz__bmdvl:
        return sdi__zyfe + 1
    else:
        return sdi__zyfe


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    aodxs__ueb = in_arr.dtype(0)
    mxhrf__zxpo = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        ftom__ohvw = aodxs__ueb
        for lbxuo__yfroz in np.nditer(in_arr):
            ftom__ohvw += lbxuo__yfroz.item()
        jenl__wzkhr = dist_exscan(ftom__ohvw, mxhrf__zxpo)
        for i in range(in_arr.size):
            jenl__wzkhr += in_arr[i]
            out_arr[i] = jenl__wzkhr
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    vmdn__imvuf = in_arr.dtype(1)
    mxhrf__zxpo = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        ftom__ohvw = vmdn__imvuf
        for lbxuo__yfroz in np.nditer(in_arr):
            ftom__ohvw *= lbxuo__yfroz.item()
        jenl__wzkhr = dist_exscan(ftom__ohvw, mxhrf__zxpo)
        if get_rank() == 0:
            jenl__wzkhr = vmdn__imvuf
        for i in range(in_arr.size):
            jenl__wzkhr *= in_arr[i]
            out_arr[i] = jenl__wzkhr
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        vmdn__imvuf = np.finfo(in_arr.dtype(1).dtype).max
    else:
        vmdn__imvuf = np.iinfo(in_arr.dtype(1).dtype).max
    mxhrf__zxpo = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        ftom__ohvw = vmdn__imvuf
        for lbxuo__yfroz in np.nditer(in_arr):
            ftom__ohvw = min(ftom__ohvw, lbxuo__yfroz.item())
        jenl__wzkhr = dist_exscan(ftom__ohvw, mxhrf__zxpo)
        if get_rank() == 0:
            jenl__wzkhr = vmdn__imvuf
        for i in range(in_arr.size):
            jenl__wzkhr = min(jenl__wzkhr, in_arr[i])
            out_arr[i] = jenl__wzkhr
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        vmdn__imvuf = np.finfo(in_arr.dtype(1).dtype).min
    else:
        vmdn__imvuf = np.iinfo(in_arr.dtype(1).dtype).min
    vmdn__imvuf = in_arr.dtype(1)
    mxhrf__zxpo = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        ftom__ohvw = vmdn__imvuf
        for lbxuo__yfroz in np.nditer(in_arr):
            ftom__ohvw = max(ftom__ohvw, lbxuo__yfroz.item())
        jenl__wzkhr = dist_exscan(ftom__ohvw, mxhrf__zxpo)
        if get_rank() == 0:
            jenl__wzkhr = vmdn__imvuf
        for i in range(in_arr.size):
            jenl__wzkhr = max(jenl__wzkhr, in_arr[i])
            out_arr[i] = jenl__wzkhr
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    fjjy__lcf = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), fjjy__lcf)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    xelsc__vepv = args[0]
    if equiv_set.has_shape(xelsc__vepv):
        return ArrayAnalysis.AnalyzeResult(shape=xelsc__vepv, pre=[])
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
    ymd__bsvjy = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for 
        i, olcx__hfv in enumerate(args) if is_array_typ(olcx__hfv) or
        isinstance(olcx__hfv, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    fcqcj__gbf = f"""def impl(*args):
    if {ymd__bsvjy} or bodo.get_rank() == 0:
        print(*args)"""
    ogqd__xzv = {}
    exec(fcqcj__gbf, globals(), ogqd__xzv)
    impl = ogqd__xzv['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        cihn__tjrhd = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        fcqcj__gbf = 'def f(req, cond=True):\n'
        fcqcj__gbf += f'  return {cihn__tjrhd}\n'
        ogqd__xzv = {}
        exec(fcqcj__gbf, {'_wait': _wait}, ogqd__xzv)
        impl = ogqd__xzv['f']
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
        mzayz__bmdvl = 1
        for a in t:
            mzayz__bmdvl *= a
        return mzayz__bmdvl
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    tnd__fyjh = np.ascontiguousarray(in_arr)
    parf__avtm = get_tuple_prod(tnd__fyjh.shape[1:])
    vkvtk__ovhoc = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        pdh__tcvev = np.array(dest_ranks, dtype=np.int32)
    else:
        pdh__tcvev = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, tnd__fyjh.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * vkvtk__ovhoc, dtype_size * parf__avtm,
        len(pdh__tcvev), pdh__tcvev.ctypes)
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
    sra__kwg = np.ascontiguousarray(rhs)
    pcay__bkm = get_tuple_prod(sra__kwg.shape[1:])
    hdt__mgxu = dtype_size * pcay__bkm
    permutation_array_index(lhs.ctypes, lhs_len, hdt__mgxu, sra__kwg.ctypes,
        sra__kwg.shape[0], p.ctypes, p_len, n_samples)
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
        fcqcj__gbf = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        ogqd__xzv = {}
        exec(fcqcj__gbf, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, ogqd__xzv)
        sgy__buerc = ogqd__xzv['bcast_scalar_impl']
        return sgy__buerc
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        kwen__ixlb = len(data.columns)
        tfo__pdfhj = ', '.join('g_data_{}'.format(i) for i in range(kwen__ixlb)
            )
        wdo__ijpjk = ColNamesMetaType(data.columns)
        fcqcj__gbf = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(kwen__ixlb):
            fcqcj__gbf += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            fcqcj__gbf += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        fcqcj__gbf += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        fcqcj__gbf += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        fcqcj__gbf += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(tfo__pdfhj))
        ogqd__xzv = {}
        exec(fcqcj__gbf, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            wdo__ijpjk}, ogqd__xzv)
        mlbcl__dbiz = ogqd__xzv['impl_df']
        return mlbcl__dbiz
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            dpvxa__jwezp = data._start
            gdbqu__gvfzn = data._stop
            ijk__egzm = data._step
            kxrui__pyn = data._name
            kxrui__pyn = bcast_scalar(kxrui__pyn, root)
            dpvxa__jwezp = bcast_scalar(dpvxa__jwezp, root)
            gdbqu__gvfzn = bcast_scalar(gdbqu__gvfzn, root)
            ijk__egzm = bcast_scalar(ijk__egzm, root)
            cge__tbsd = bodo.libs.array_kernels.calc_nitems(dpvxa__jwezp,
                gdbqu__gvfzn, ijk__egzm)
            chunk_start = bodo.libs.distributed_api.get_start(cge__tbsd,
                n_pes, rank)
            moees__fczk = bodo.libs.distributed_api.get_node_portion(cge__tbsd,
                n_pes, rank)
            pvj__jth = dpvxa__jwezp + ijk__egzm * chunk_start
            vynz__yapd = dpvxa__jwezp + ijk__egzm * (chunk_start + moees__fczk)
            vynz__yapd = min(vynz__yapd, gdbqu__gvfzn)
            return bodo.hiframes.pd_index_ext.init_range_index(pvj__jth,
                vynz__yapd, ijk__egzm, kxrui__pyn)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            uzsfh__hbv = data._data
            kxrui__pyn = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(uzsfh__hbv,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, kxrui__pyn)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            kxrui__pyn = bodo.hiframes.pd_series_ext.get_series_name(data)
            aekc__yuoqt = bodo.libs.distributed_api.bcast_comm_impl(kxrui__pyn,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            rqs__nzfga = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                rqs__nzfga, aekc__yuoqt)
        return impl_series
    if isinstance(data, types.BaseTuple):
        fcqcj__gbf = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        fcqcj__gbf += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        ogqd__xzv = {}
        exec(fcqcj__gbf, {'bcast_comm_impl': bcast_comm_impl}, ogqd__xzv)
        vizoi__nucph = ogqd__xzv['impl_tuple']
        return vizoi__nucph
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    sanbn__uspf = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    ldut__vufx = (0,) * sanbn__uspf

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        uzsfh__hbv = np.ascontiguousarray(data)
        upgay__oao = data.ctypes
        jse__dwgvz = ldut__vufx
        if rank == root:
            jse__dwgvz = uzsfh__hbv.shape
        jse__dwgvz = bcast_tuple(jse__dwgvz, root)
        wvlex__twe = get_tuple_prod(jse__dwgvz[1:])
        send_counts = jse__dwgvz[0] * wvlex__twe
        zvtfp__cplt = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(upgay__oao, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(zvtfp__cplt.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return zvtfp__cplt.reshape((-1,) + jse__dwgvz[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        ghlcz__gizr = MPI.COMM_WORLD
        jkma__gsvie = MPI.Get_processor_name()
        yvo__yobtb = ghlcz__gizr.allgather(jkma__gsvie)
        node_ranks = defaultdict(list)
        for i, txc__rkt in enumerate(yvo__yobtb):
            node_ranks[txc__rkt].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    ghlcz__gizr = MPI.COMM_WORLD
    oweug__ive = ghlcz__gizr.Get_group()
    odmnl__qosk = oweug__ive.Incl(comm_ranks)
    vds__eoul = ghlcz__gizr.Create_group(odmnl__qosk)
    return vds__eoul


def get_nodes_first_ranks():
    yzba__egob = get_host_ranks()
    return np.array([kcbpp__rmbrc[0] for kcbpp__rmbrc in yzba__egob.values(
        )], dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
