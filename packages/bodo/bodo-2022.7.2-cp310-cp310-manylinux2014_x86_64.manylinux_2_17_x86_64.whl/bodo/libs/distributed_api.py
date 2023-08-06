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
    ybzme__ostts = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, ybzme__ostts, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    ybzme__ostts = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, ybzme__ostts, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            ybzme__ostts = get_type_enum(arr)
            return _isend(arr.ctypes, size, ybzme__ostts, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        ybzme__ostts = np.int32(numba_to_c_type(arr.dtype))
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            hkx__zhg = size + 7 >> 3
            zjdlf__nud = _isend(arr._data.ctypes, size, ybzme__ostts, pe,
                tag, cond)
            qspp__oet = _isend(arr._null_bitmap.ctypes, hkx__zhg,
                ceaqy__ooiib, pe, tag, cond)
            return zjdlf__nud, qspp__oet
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        pqt__itjhu = np.int32(numba_to_c_type(offset_type))
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            ujs__tpwj = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(ujs__tpwj, pe, tag - 1)
            hkx__zhg = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                pqt__itjhu, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), ujs__tpwj,
                ceaqy__ooiib, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), hkx__zhg,
                ceaqy__ooiib, pe, tag)
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
            ybzme__ostts = get_type_enum(arr)
            return _irecv(arr.ctypes, size, ybzme__ostts, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        ybzme__ostts = np.int32(numba_to_c_type(arr.dtype))
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            hkx__zhg = size + 7 >> 3
            zjdlf__nud = _irecv(arr._data.ctypes, size, ybzme__ostts, pe,
                tag, cond)
            qspp__oet = _irecv(arr._null_bitmap.ctypes, hkx__zhg,
                ceaqy__ooiib, pe, tag, cond)
            return zjdlf__nud, qspp__oet
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        pqt__itjhu = np.int32(numba_to_c_type(offset_type))
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            amwm__yeh = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            amwm__yeh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        bhe__gzij = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {amwm__yeh}(size, n_chars)
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
        qcdj__rml = dict()
        exec(bhe__gzij, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            pqt__itjhu, 'char_typ_enum': ceaqy__ooiib}, qcdj__rml)
        impl = qcdj__rml['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    ybzme__ostts = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), ybzme__ostts)


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
        bbfu__yuk = n_pes if rank == root or allgather else 0
        qrh__tnw = np.empty(bbfu__yuk, dtype)
        c_gather_scalar(send.ctypes, qrh__tnw.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return qrh__tnw
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
        btyv__yosw = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], btyv__yosw)
        return builder.bitcast(btyv__yosw, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        btyv__yosw = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(btyv__yosw)
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
    jll__btkvq = types.unliteral(value)
    if isinstance(jll__btkvq, IndexValueType):
        jll__btkvq = jll__btkvq.val_typ
        avhj__vavix = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            avhj__vavix.append(types.int64)
            avhj__vavix.append(bodo.datetime64ns)
            avhj__vavix.append(bodo.timedelta64ns)
            avhj__vavix.append(bodo.datetime_date_type)
        if jll__btkvq not in avhj__vavix:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(jll__btkvq))
    typ_enum = np.int32(numba_to_c_type(jll__btkvq))

    def impl(value, reduce_op):
        wyede__iikju = value_to_ptr(value)
        dtjj__fmsp = value_to_ptr(value)
        _dist_reduce(wyede__iikju, dtjj__fmsp, reduce_op, typ_enum)
        return load_val_ptr(dtjj__fmsp, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    jll__btkvq = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(jll__btkvq))
    snouc__qeuy = jll__btkvq(0)

    def impl(value, reduce_op):
        wyede__iikju = value_to_ptr(value)
        dtjj__fmsp = value_to_ptr(snouc__qeuy)
        _dist_exscan(wyede__iikju, dtjj__fmsp, reduce_op, typ_enum)
        return load_val_ptr(dtjj__fmsp, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    hlstc__vkeu = 0
    ezc__kgxlu = 0
    for i in range(len(recv_counts)):
        qcxu__aauwf = recv_counts[i]
        hkx__zhg = recv_counts_nulls[i]
        cfje__elt = tmp_null_bytes[hlstc__vkeu:hlstc__vkeu + hkx__zhg]
        for fimjl__doudq in range(qcxu__aauwf):
            set_bit_to(null_bitmap_ptr, ezc__kgxlu, get_bit(cfje__elt,
                fimjl__doudq))
            ezc__kgxlu += 1
        hlstc__vkeu += hkx__zhg


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            tuzd__mkjhs = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                tuzd__mkjhs, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            frx__xiqe = data.size
            recv_counts = gather_scalar(np.int32(frx__xiqe), allgather,
                root=root)
            qarmp__zine = recv_counts.sum()
            roym__ldiv = empty_like_type(qarmp__zine, data)
            mhmg__edm = np.empty(1, np.int32)
            if rank == root or allgather:
                mhmg__edm = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(frx__xiqe), roym__ldiv.ctypes,
                recv_counts.ctypes, mhmg__edm.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return roym__ldiv.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            roym__ldiv = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(roym__ldiv)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            roym__ldiv = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(roym__ldiv)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            frx__xiqe = len(data)
            hkx__zhg = frx__xiqe + 7 >> 3
            recv_counts = gather_scalar(np.int32(frx__xiqe), allgather,
                root=root)
            qarmp__zine = recv_counts.sum()
            roym__ldiv = empty_like_type(qarmp__zine, data)
            mhmg__edm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            rnuwq__vhxge = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mhmg__edm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                rnuwq__vhxge = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(frx__xiqe),
                roym__ldiv._days_data.ctypes, recv_counts.ctypes, mhmg__edm
                .ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(frx__xiqe),
                roym__ldiv._seconds_data.ctypes, recv_counts.ctypes,
                mhmg__edm.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(frx__xiqe),
                roym__ldiv._microseconds_data.ctypes, recv_counts.ctypes,
                mhmg__edm.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(hkx__zhg),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                rnuwq__vhxge.ctypes, ceaqy__ooiib, allgather, np.int32(root))
            copy_gathered_null_bytes(roym__ldiv._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return roym__ldiv
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            frx__xiqe = len(data)
            hkx__zhg = frx__xiqe + 7 >> 3
            recv_counts = gather_scalar(np.int32(frx__xiqe), allgather,
                root=root)
            qarmp__zine = recv_counts.sum()
            roym__ldiv = empty_like_type(qarmp__zine, data)
            mhmg__edm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            rnuwq__vhxge = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mhmg__edm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                rnuwq__vhxge = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(frx__xiqe), roym__ldiv.
                _data.ctypes, recv_counts.ctypes, mhmg__edm.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(hkx__zhg),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                rnuwq__vhxge.ctypes, ceaqy__ooiib, allgather, np.int32(root))
            copy_gathered_null_bytes(roym__ldiv._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return roym__ldiv
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        xtyro__abcu = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            jta__lwyjb = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                jta__lwyjb, xtyro__abcu)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            ubrzq__aeqr = bodo.gatherv(data._left, allgather, warn_if_rep, root
                )
            ndf__qkmi = bodo.gatherv(data._right, allgather, warn_if_rep, root)
            return bodo.libs.interval_arr_ext.init_interval_array(ubrzq__aeqr,
                ndf__qkmi)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            iskii__bub = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            cijmz__mqfs = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cijmz__mqfs, iskii__bub)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        mfrl__fzqev = np.iinfo(np.int64).max
        pcwo__spen = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            yowse__gsld = data._start
            prloq__ipdg = data._stop
            if len(data) == 0:
                yowse__gsld = mfrl__fzqev
                prloq__ipdg = pcwo__spen
            yowse__gsld = bodo.libs.distributed_api.dist_reduce(yowse__gsld,
                np.int32(Reduce_Type.Min.value))
            prloq__ipdg = bodo.libs.distributed_api.dist_reduce(prloq__ipdg,
                np.int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if yowse__gsld == mfrl__fzqev and prloq__ipdg == pcwo__spen:
                yowse__gsld = 0
                prloq__ipdg = 0
            aadx__ffe = max(0, -(-(prloq__ipdg - yowse__gsld) // data._step))
            if aadx__ffe < total_len:
                prloq__ipdg = yowse__gsld + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                yowse__gsld = 0
                prloq__ipdg = 0
            return bodo.hiframes.pd_index_ext.init_range_index(yowse__gsld,
                prloq__ipdg, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            aldir__edlae = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, aldir__edlae)
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
            roym__ldiv = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(roym__ldiv
                , data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        tonqx__rokl = {'bodo': bodo, 'get_table_block': bodo.hiframes.table
            .get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        bhe__gzij = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        bhe__gzij += '  T = data\n'
        bhe__gzij += '  T2 = init_table(T, True)\n'
        for olai__fsl in data.type_to_blk.values():
            tonqx__rokl[f'arr_inds_{olai__fsl}'] = np.array(data.
                block_to_arr_ind[olai__fsl], dtype=np.int64)
            bhe__gzij += (
                f'  arr_list_{olai__fsl} = get_table_block(T, {olai__fsl})\n')
            bhe__gzij += f"""  out_arr_list_{olai__fsl} = alloc_list_like(arr_list_{olai__fsl}, len(arr_list_{olai__fsl}), True)
"""
            bhe__gzij += f'  for i in range(len(arr_list_{olai__fsl})):\n'
            bhe__gzij += f'    arr_ind_{olai__fsl} = arr_inds_{olai__fsl}[i]\n'
            bhe__gzij += f"""    ensure_column_unboxed(T, arr_list_{olai__fsl}, i, arr_ind_{olai__fsl})
"""
            bhe__gzij += f"""    out_arr_{olai__fsl} = bodo.gatherv(arr_list_{olai__fsl}[i], allgather, warn_if_rep, root)
"""
            bhe__gzij += (
                f'    out_arr_list_{olai__fsl}[i] = out_arr_{olai__fsl}\n')
            bhe__gzij += (
                f'  T2 = set_table_block(T2, out_arr_list_{olai__fsl}, {olai__fsl})\n'
                )
        bhe__gzij += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        bhe__gzij += f'  T2 = set_table_len(T2, length)\n'
        bhe__gzij += f'  return T2\n'
        qcdj__rml = {}
        exec(bhe__gzij, tonqx__rokl, qcdj__rml)
        lpxbs__pnwya = qcdj__rml['impl_table']
        return lpxbs__pnwya
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        bwzk__lirth = len(data.columns)
        if bwzk__lirth == 0:
            wnbf__osynl = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                xvq__cfbft = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    xvq__cfbft, wnbf__osynl)
            return impl
        fmbu__beafl = ', '.join(f'g_data_{i}' for i in range(bwzk__lirth))
        bhe__gzij = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            duhz__hei = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            fmbu__beafl = 'T2'
            bhe__gzij += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            bhe__gzij += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(bwzk__lirth):
                bhe__gzij += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                bhe__gzij += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        bhe__gzij += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        bhe__gzij += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        bhe__gzij += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(fmbu__beafl))
        qcdj__rml = {}
        tonqx__rokl = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(bhe__gzij, tonqx__rokl, qcdj__rml)
        oee__rnfa = qcdj__rml['impl_df']
        return oee__rnfa
    if isinstance(data, ArrayItemArrayType):
        nyfoh__fkk = np.int32(numba_to_c_type(types.int32))
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            ruta__aff = bodo.libs.array_item_arr_ext.get_offsets(data)
            wac__top = bodo.libs.array_item_arr_ext.get_data(data)
            wac__top = wac__top[:ruta__aff[-1]]
            udo__uyj = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            frx__xiqe = len(data)
            glkv__bdz = np.empty(frx__xiqe, np.uint32)
            hkx__zhg = frx__xiqe + 7 >> 3
            for i in range(frx__xiqe):
                glkv__bdz[i] = ruta__aff[i + 1] - ruta__aff[i]
            recv_counts = gather_scalar(np.int32(frx__xiqe), allgather,
                root=root)
            qarmp__zine = recv_counts.sum()
            mhmg__edm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            rnuwq__vhxge = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                mhmg__edm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for agnq__rdel in range(len(recv_counts)):
                    recv_counts_nulls[agnq__rdel] = recv_counts[agnq__rdel
                        ] + 7 >> 3
                rnuwq__vhxge = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            htkd__txuoc = np.empty(qarmp__zine + 1, np.uint32)
            nsr__vslm = bodo.gatherv(wac__top, allgather, warn_if_rep, root)
            igebu__igpxu = np.empty(qarmp__zine + 7 >> 3, np.uint8)
            c_gatherv(glkv__bdz.ctypes, np.int32(frx__xiqe), htkd__txuoc.
                ctypes, recv_counts.ctypes, mhmg__edm.ctypes, nyfoh__fkk,
                allgather, np.int32(root))
            c_gatherv(udo__uyj.ctypes, np.int32(hkx__zhg), tmp_null_bytes.
                ctypes, recv_counts_nulls.ctypes, rnuwq__vhxge.ctypes,
                ceaqy__ooiib, allgather, np.int32(root))
            dummy_use(data)
            ykgc__fuaca = np.empty(qarmp__zine + 1, np.uint64)
            convert_len_arr_to_offset(htkd__txuoc.ctypes, ykgc__fuaca.
                ctypes, qarmp__zine)
            copy_gathered_null_bytes(igebu__igpxu.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                qarmp__zine, nsr__vslm, ykgc__fuaca, igebu__igpxu)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        ckfc__dbw = data.names
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vwfkq__fzm = bodo.libs.struct_arr_ext.get_data(data)
            qhm__wngki = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            pvq__nccm = bodo.gatherv(vwfkq__fzm, allgather=allgather, root=root
                )
            rank = bodo.libs.distributed_api.get_rank()
            frx__xiqe = len(data)
            hkx__zhg = frx__xiqe + 7 >> 3
            recv_counts = gather_scalar(np.int32(frx__xiqe), allgather,
                root=root)
            qarmp__zine = recv_counts.sum()
            coee__yhlxj = np.empty(qarmp__zine + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            rnuwq__vhxge = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                rnuwq__vhxge = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(qhm__wngki.ctypes, np.int32(hkx__zhg), tmp_null_bytes
                .ctypes, recv_counts_nulls.ctypes, rnuwq__vhxge.ctypes,
                ceaqy__ooiib, allgather, np.int32(root))
            copy_gathered_null_bytes(coee__yhlxj.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(pvq__nccm,
                coee__yhlxj, ckfc__dbw)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            roym__ldiv = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(roym__ldiv)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            roym__ldiv = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(roym__ldiv)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            roym__ldiv = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(roym__ldiv)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            roym__ldiv = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            mjix__xpnl = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            iel__rocnq = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            pzus__cvs = gather_scalar(data.shape[0], allgather, root=root)
            cbpo__hejg = pzus__cvs.sum()
            bwzk__lirth = bodo.libs.distributed_api.dist_reduce(data.shape[
                1], np.int32(Reduce_Type.Max.value))
            lrjc__sfqya = np.empty(cbpo__hejg + 1, np.int64)
            mjix__xpnl = mjix__xpnl.astype(np.int64)
            lrjc__sfqya[0] = 0
            xbe__uegh = 1
            ixv__zbmhv = 0
            for waso__fksd in pzus__cvs:
                for psc__xwuut in range(waso__fksd):
                    ufry__ghrr = iel__rocnq[ixv__zbmhv + 1] - iel__rocnq[
                        ixv__zbmhv]
                    lrjc__sfqya[xbe__uegh] = lrjc__sfqya[xbe__uegh - 1
                        ] + ufry__ghrr
                    xbe__uegh += 1
                    ixv__zbmhv += 1
                ixv__zbmhv += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(roym__ldiv,
                mjix__xpnl, lrjc__sfqya, (cbpo__hejg, bwzk__lirth))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        bhe__gzij = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        bhe__gzij += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        qcdj__rml = {}
        exec(bhe__gzij, {'bodo': bodo}, qcdj__rml)
        ipbmz__sykur = qcdj__rml['impl_tuple']
        return ipbmz__sykur
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    bhe__gzij = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    bhe__gzij += '    if random:\n'
    bhe__gzij += '        if random_seed is None:\n'
    bhe__gzij += '            random = 1\n'
    bhe__gzij += '        else:\n'
    bhe__gzij += '            random = 2\n'
    bhe__gzij += '    if random_seed is None:\n'
    bhe__gzij += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        aut__cin = data
        bwzk__lirth = len(aut__cin.columns)
        for i in range(bwzk__lirth):
            bhe__gzij += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        bhe__gzij += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        fmbu__beafl = ', '.join(f'data_{i}' for i in range(bwzk__lirth))
        bhe__gzij += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(wfx__jix) for
            wfx__jix in range(bwzk__lirth))))
        bhe__gzij += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        bhe__gzij += '    if dests is None:\n'
        bhe__gzij += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        bhe__gzij += '    else:\n'
        bhe__gzij += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for fvnf__bwreu in range(bwzk__lirth):
            bhe__gzij += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(fvnf__bwreu))
        bhe__gzij += (
            '    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
            .format(bwzk__lirth))
        bhe__gzij += '    delete_table(out_table)\n'
        bhe__gzij += '    if parallel:\n'
        bhe__gzij += '        delete_table(table_total)\n'
        fmbu__beafl = ', '.join('out_arr_{}'.format(i) for i in range(
            bwzk__lirth))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        bhe__gzij += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(fmbu__beafl, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        bhe__gzij += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        bhe__gzij += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        bhe__gzij += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        bhe__gzij += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        bhe__gzij += '    if dests is None:\n'
        bhe__gzij += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        bhe__gzij += '    else:\n'
        bhe__gzij += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        bhe__gzij += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        bhe__gzij += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        bhe__gzij += '    delete_table(out_table)\n'
        bhe__gzij += '    if parallel:\n'
        bhe__gzij += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        bhe__gzij += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        bhe__gzij += '    if not parallel:\n'
        bhe__gzij += '        return data\n'
        bhe__gzij += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        bhe__gzij += '    if dests is None:\n'
        bhe__gzij += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        bhe__gzij += '    elif bodo.get_rank() not in dests:\n'
        bhe__gzij += '        dim0_local_size = 0\n'
        bhe__gzij += '    else:\n'
        bhe__gzij += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        bhe__gzij += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        bhe__gzij += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        bhe__gzij += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        bhe__gzij += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        bhe__gzij += '    if dests is None:\n'
        bhe__gzij += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        bhe__gzij += '    else:\n'
        bhe__gzij += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        bhe__gzij += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        bhe__gzij += '    delete_table(out_table)\n'
        bhe__gzij += '    if parallel:\n'
        bhe__gzij += '        delete_table(table_total)\n'
        bhe__gzij += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    qcdj__rml = {}
    tonqx__rokl = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array
        .array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        tonqx__rokl.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(aut__cin.columns)})
    exec(bhe__gzij, tonqx__rokl, qcdj__rml)
    impl = qcdj__rml['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    bhe__gzij = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        bhe__gzij += '    if seed is None:\n'
        bhe__gzij += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        bhe__gzij += '    np.random.seed(seed)\n'
        bhe__gzij += '    if not parallel:\n'
        bhe__gzij += '        data = data.copy()\n'
        bhe__gzij += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            bhe__gzij += '        data = data[:n_samples]\n'
        bhe__gzij += '        return data\n'
        bhe__gzij += '    else:\n'
        bhe__gzij += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        bhe__gzij += '        permutation = np.arange(dim0_global_size)\n'
        bhe__gzij += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            bhe__gzij += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            bhe__gzij += '        n_samples = dim0_global_size\n'
        bhe__gzij += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        bhe__gzij += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        bhe__gzij += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        bhe__gzij += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        bhe__gzij += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        bhe__gzij += '        return output\n'
    else:
        bhe__gzij += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            bhe__gzij += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            bhe__gzij += '    output = output[:local_n_samples]\n'
        bhe__gzij += '    return output\n'
    qcdj__rml = {}
    exec(bhe__gzij, {'np': np, 'bodo': bodo}, qcdj__rml)
    impl = qcdj__rml['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    qgxzi__soe = np.empty(sendcounts_nulls.sum(), np.uint8)
    hlstc__vkeu = 0
    ezc__kgxlu = 0
    for qmeqk__ubk in range(len(sendcounts)):
        qcxu__aauwf = sendcounts[qmeqk__ubk]
        hkx__zhg = sendcounts_nulls[qmeqk__ubk]
        cfje__elt = qgxzi__soe[hlstc__vkeu:hlstc__vkeu + hkx__zhg]
        for fimjl__doudq in range(qcxu__aauwf):
            set_bit_to_arr(cfje__elt, fimjl__doudq, get_bit_bitmap(
                null_bitmap_ptr, ezc__kgxlu))
            ezc__kgxlu += 1
        hlstc__vkeu += hkx__zhg
    return qgxzi__soe


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    zblnp__eomp = MPI.COMM_WORLD
    data = zblnp__eomp.bcast(data, root)
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
    tgw__mlsy = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    kte__gex = (0,) * tgw__mlsy

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        ggbiy__qcjel = np.ascontiguousarray(data)
        yvvif__svx = data.ctypes
        qlvil__xigcb = kte__gex
        if rank == MPI_ROOT:
            qlvil__xigcb = ggbiy__qcjel.shape
        qlvil__xigcb = bcast_tuple(qlvil__xigcb)
        mwo__wwz = get_tuple_prod(qlvil__xigcb[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            qlvil__xigcb[0])
        send_counts *= mwo__wwz
        frx__xiqe = send_counts[rank]
        uqosx__fggda = np.empty(frx__xiqe, dtype)
        mhmg__edm = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(yvvif__svx, send_counts.ctypes, mhmg__edm.ctypes,
            uqosx__fggda.ctypes, np.int32(frx__xiqe), np.int32(typ_val))
        return uqosx__fggda.reshape((-1,) + qlvil__xigcb[1:])
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
        nscv__ast = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], nscv__ast)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        iskii__bub = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=iskii__bub)
        isj__dfkb = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(isj__dfkb)
        return pd.Index(arr, name=iskii__bub)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        iskii__bub = _get_name_value_for_type(dtype.name_typ)
        ckfc__dbw = tuple(_get_name_value_for_type(t) for t in dtype.names_typ)
        fhzzx__ssvzg = tuple(get_value_for_type(t) for t in dtype.array_types)
        fhzzx__ssvzg = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in fhzzx__ssvzg)
        val = pd.MultiIndex.from_arrays(fhzzx__ssvzg, names=ckfc__dbw)
        val.name = iskii__bub
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        iskii__bub = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=iskii__bub)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        fhzzx__ssvzg = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({iskii__bub: arr for iskii__bub, arr in zip(
            dtype.columns, fhzzx__ssvzg)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        isj__dfkb = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(isj__dfkb[0], isj__dfkb
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
        nyfoh__fkk = np.int32(numba_to_c_type(types.int32))
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            amwm__yeh = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            amwm__yeh = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        bhe__gzij = f"""def impl(
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
            recv_arr = {amwm__yeh}(n_loc, n_loc_char)

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
        qcdj__rml = dict()
        exec(bhe__gzij, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            nyfoh__fkk, 'char_typ_enum': ceaqy__ooiib,
            'decode_if_dict_array': decode_if_dict_array}, qcdj__rml)
        impl = qcdj__rml['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        nyfoh__fkk = np.int32(numba_to_c_type(types.int32))
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            olhl__dlad = bodo.libs.array_item_arr_ext.get_offsets(data)
            xivv__klqvi = bodo.libs.array_item_arr_ext.get_data(data)
            xivv__klqvi = xivv__klqvi[:olhl__dlad[-1]]
            vou__zfwhg = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            kzj__gyxf = bcast_scalar(len(data))
            tvm__qdlbh = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                tvm__qdlbh[i] = olhl__dlad[i + 1] - olhl__dlad[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                kzj__gyxf)
            mhmg__edm = bodo.ir.join.calc_disp(send_counts)
            tgywe__lhnw = np.empty(n_pes, np.int32)
            if rank == 0:
                wfgmh__xaqx = 0
                for i in range(n_pes):
                    qqr__qwyyo = 0
                    for psc__xwuut in range(send_counts[i]):
                        qqr__qwyyo += tvm__qdlbh[wfgmh__xaqx]
                        wfgmh__xaqx += 1
                    tgywe__lhnw[i] = qqr__qwyyo
            bcast(tgywe__lhnw)
            hkwlz__pwph = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                hkwlz__pwph[i] = send_counts[i] + 7 >> 3
            rnuwq__vhxge = bodo.ir.join.calc_disp(hkwlz__pwph)
            frx__xiqe = send_counts[rank]
            wykrm__hrw = np.empty(frx__xiqe + 1, np_offset_type)
            mqiz__ototw = bodo.libs.distributed_api.scatterv_impl(xivv__klqvi,
                tgywe__lhnw)
            bzkfu__fbz = frx__xiqe + 7 >> 3
            oxz__hsf = np.empty(bzkfu__fbz, np.uint8)
            rpld__hwe = np.empty(frx__xiqe, np.uint32)
            c_scatterv(tvm__qdlbh.ctypes, send_counts.ctypes, mhmg__edm.
                ctypes, rpld__hwe.ctypes, np.int32(frx__xiqe), nyfoh__fkk)
            convert_len_arr_to_offset(rpld__hwe.ctypes, wykrm__hrw.ctypes,
                frx__xiqe)
            rjj__vwii = get_scatter_null_bytes_buff(vou__zfwhg.ctypes,
                send_counts, hkwlz__pwph)
            c_scatterv(rjj__vwii.ctypes, hkwlz__pwph.ctypes, rnuwq__vhxge.
                ctypes, oxz__hsf.ctypes, np.int32(bzkfu__fbz), ceaqy__ooiib)
            return bodo.libs.array_item_arr_ext.init_array_item_array(frx__xiqe
                , mqiz__ototw, wykrm__hrw, oxz__hsf)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            qkvgk__tgyj = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            qkvgk__tgyj = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            qkvgk__tgyj = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            qkvgk__tgyj = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            ggbiy__qcjel = data._data
            qhm__wngki = data._null_bitmap
            uoiz__cepj = len(ggbiy__qcjel)
            xylu__fqee = _scatterv_np(ggbiy__qcjel, send_counts)
            kzj__gyxf = bcast_scalar(uoiz__cepj)
            pcbt__japdu = len(xylu__fqee) + 7 >> 3
            dzeou__heat = np.empty(pcbt__japdu, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                kzj__gyxf)
            hkwlz__pwph = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                hkwlz__pwph[i] = send_counts[i] + 7 >> 3
            rnuwq__vhxge = bodo.ir.join.calc_disp(hkwlz__pwph)
            rjj__vwii = get_scatter_null_bytes_buff(qhm__wngki.ctypes,
                send_counts, hkwlz__pwph)
            c_scatterv(rjj__vwii.ctypes, hkwlz__pwph.ctypes, rnuwq__vhxge.
                ctypes, dzeou__heat.ctypes, np.int32(pcbt__japdu), ceaqy__ooiib
                )
            return qkvgk__tgyj(xylu__fqee, dzeou__heat)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            kqp__ulzys = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            iuphr__ctizo = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(kqp__ulzys,
                iuphr__ctizo)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            yowse__gsld = data._start
            prloq__ipdg = data._stop
            toy__xok = data._step
            iskii__bub = data._name
            iskii__bub = bcast_scalar(iskii__bub)
            yowse__gsld = bcast_scalar(yowse__gsld)
            prloq__ipdg = bcast_scalar(prloq__ipdg)
            toy__xok = bcast_scalar(toy__xok)
            lvtd__iyuhv = bodo.libs.array_kernels.calc_nitems(yowse__gsld,
                prloq__ipdg, toy__xok)
            chunk_start = bodo.libs.distributed_api.get_start(lvtd__iyuhv,
                n_pes, rank)
            ytd__nfi = bodo.libs.distributed_api.get_node_portion(lvtd__iyuhv,
                n_pes, rank)
            crh__zumb = yowse__gsld + toy__xok * chunk_start
            xzc__wkk = yowse__gsld + toy__xok * (chunk_start + ytd__nfi)
            xzc__wkk = min(xzc__wkk, prloq__ipdg)
            return bodo.hiframes.pd_index_ext.init_range_index(crh__zumb,
                xzc__wkk, toy__xok, iskii__bub)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        aldir__edlae = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            ggbiy__qcjel = data._data
            iskii__bub = data._name
            iskii__bub = bcast_scalar(iskii__bub)
            arr = bodo.libs.distributed_api.scatterv_impl(ggbiy__qcjel,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                iskii__bub, aldir__edlae)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            ggbiy__qcjel = data._data
            iskii__bub = data._name
            iskii__bub = bcast_scalar(iskii__bub)
            arr = bodo.libs.distributed_api.scatterv_impl(ggbiy__qcjel,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, iskii__bub)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            roym__ldiv = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            iskii__bub = bcast_scalar(data._name)
            ckfc__dbw = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(roym__ldiv
                , ckfc__dbw, iskii__bub)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            iskii__bub = bodo.hiframes.pd_series_ext.get_series_name(data)
            acu__ymcnz = bcast_scalar(iskii__bub)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            cijmz__mqfs = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cijmz__mqfs, acu__ymcnz)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        bwzk__lirth = len(data.columns)
        fmbu__beafl = ', '.join('g_data_{}'.format(i) for i in range(
            bwzk__lirth))
        yptum__jsa = ColNamesMetaType(data.columns)
        bhe__gzij = 'def impl_df(data, send_counts=None, warn_if_dist=True):\n'
        for i in range(bwzk__lirth):
            bhe__gzij += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            bhe__gzij += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        bhe__gzij += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        bhe__gzij += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        bhe__gzij += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({fmbu__beafl},), g_index, __col_name_meta_scaterv_impl)
"""
        qcdj__rml = {}
        exec(bhe__gzij, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            yptum__jsa}, qcdj__rml)
        oee__rnfa = qcdj__rml['impl_df']
        return oee__rnfa
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            tuzd__mkjhs = bodo.libs.distributed_api.scatterv_impl(data.
                codes, send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                tuzd__mkjhs, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        bhe__gzij = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        bhe__gzij += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        qcdj__rml = {}
        exec(bhe__gzij, {'bodo': bodo}, qcdj__rml)
        ipbmz__sykur = qcdj__rml['impl_tuple']
        return ipbmz__sykur
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
        pqt__itjhu = np.int32(numba_to_c_type(offset_type))
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            frx__xiqe = len(data)
            uecab__ois = num_total_chars(data)
            assert frx__xiqe < INT_MAX
            assert uecab__ois < INT_MAX
            snjia__vzhcq = get_offset_ptr(data)
            yvvif__svx = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            hkx__zhg = frx__xiqe + 7 >> 3
            c_bcast(snjia__vzhcq, np.int32(frx__xiqe + 1), pqt__itjhu, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(yvvif__svx, np.int32(uecab__ois), ceaqy__ooiib, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(hkx__zhg), ceaqy__ooiib, np.
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
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                edli__hmjg = 0
                czqox__jogt = np.empty(0, np.uint8).ctypes
            else:
                czqox__jogt, edli__hmjg = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            edli__hmjg = bodo.libs.distributed_api.bcast_scalar(edli__hmjg,
                root)
            if rank != root:
                yiij__zncb = np.empty(edli__hmjg + 1, np.uint8)
                yiij__zncb[edli__hmjg] = 0
                czqox__jogt = yiij__zncb.ctypes
            c_bcast(czqox__jogt, np.int32(edli__hmjg), ceaqy__ooiib, np.
                array([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(czqox__jogt, edli__hmjg)
        return impl_str
    typ_val = numba_to_c_type(val)
    bhe__gzij = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    qcdj__rml = {}
    exec(bhe__gzij, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, qcdj__rml)
    byx__toyrj = qcdj__rml['bcast_scalar_impl']
    return byx__toyrj


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    vogfl__jzc = len(val)
    bhe__gzij = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    bhe__gzij += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(vogfl__jzc)),
        ',' if vogfl__jzc else '')
    qcdj__rml = {}
    exec(bhe__gzij, {'bcast_scalar': bcast_scalar}, qcdj__rml)
    oojl__ttiv = qcdj__rml['bcast_tuple_impl']
    return oojl__ttiv


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            frx__xiqe = bcast_scalar(len(arr), root)
            litf__not = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(frx__xiqe, litf__not)
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
            crh__zumb = max(arr_start, slice_index.start) - arr_start
            xzc__wkk = max(slice_index.stop - arr_start, 0)
            return slice(crh__zumb, xzc__wkk)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            yowse__gsld = slice_index.start
            toy__xok = slice_index.step
            fqssi__vasri = (0 if toy__xok == 1 or yowse__gsld > arr_start else
                abs(toy__xok - arr_start % toy__xok) % toy__xok)
            crh__zumb = max(arr_start, slice_index.start
                ) - arr_start + fqssi__vasri
            xzc__wkk = max(slice_index.stop - arr_start, 0)
            return slice(crh__zumb, xzc__wkk, toy__xok)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        fmql__may = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[fmql__may])
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
        watph__sso = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        ceaqy__ooiib = np.int32(numba_to_c_type(types.uint8))
        gvm__npqgi = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            xxf__pedfo = np.int32(10)
            tag = np.int32(11)
            zinpp__eodrk = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                wac__top = arr._data
                jhyv__ukqu = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    wac__top, ind)
                sgpu__jqsfe = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    wac__top, ind + 1)
                length = sgpu__jqsfe - jhyv__ukqu
                btyv__yosw = wac__top[ind]
                zinpp__eodrk[0] = length
                isend(zinpp__eodrk, np.int32(1), root, xxf__pedfo, True)
                isend(btyv__yosw, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(gvm__npqgi
                , watph__sso, 0, 1)
            aadx__ffe = 0
            if rank == root:
                aadx__ffe = recv(np.int64, ANY_SOURCE, xxf__pedfo)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    gvm__npqgi, watph__sso, aadx__ffe, 1)
                yvvif__svx = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(yvvif__svx, np.int32(aadx__ffe), ceaqy__ooiib,
                    ANY_SOURCE, tag)
            dummy_use(zinpp__eodrk)
            aadx__ffe = bcast_scalar(aadx__ffe)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    gvm__npqgi, watph__sso, aadx__ffe, 1)
            yvvif__svx = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(yvvif__svx, np.int32(aadx__ffe), ceaqy__ooiib, np.array
                ([-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, aadx__ffe)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        xyvc__wak = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, xyvc__wak)
            if arr_start <= ind < arr_start + len(arr):
                tuzd__mkjhs = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = tuzd__mkjhs[ind - arr_start]
                send_arr = np.full(1, data, xyvc__wak)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = xyvc__wak(-1)
            if rank == root:
                val = recv(xyvc__wak, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            xytst__udaw = arr.dtype.categories[max(val, 0)]
            return xytst__udaw
        return cat_getitem_impl
    deh__cpxv = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, deh__cpxv)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, deh__cpxv)[0]
        if rank == root:
            val = recv(deh__cpxv, ANY_SOURCE, tag)
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
    idza__vla = get_type_enum(out_data)
    assert typ_enum == idza__vla
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
    bhe__gzij = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        bhe__gzij += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    bhe__gzij += '  return\n'
    qcdj__rml = {}
    exec(bhe__gzij, {'alltoallv': alltoallv}, qcdj__rml)
    jgzs__mrjyb = qcdj__rml['f']
    return jgzs__mrjyb


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    yowse__gsld = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return yowse__gsld, count


@numba.njit
def get_start(total_size, pes, rank):
    qrh__tnw = total_size % pes
    gvcms__jso = (total_size - qrh__tnw) // pes
    return rank * gvcms__jso + min(rank, qrh__tnw)


@numba.njit
def get_end(total_size, pes, rank):
    qrh__tnw = total_size % pes
    gvcms__jso = (total_size - qrh__tnw) // pes
    return (rank + 1) * gvcms__jso + min(rank + 1, qrh__tnw)


@numba.njit
def get_node_portion(total_size, pes, rank):
    qrh__tnw = total_size % pes
    gvcms__jso = (total_size - qrh__tnw) // pes
    if rank < qrh__tnw:
        return gvcms__jso + 1
    else:
        return gvcms__jso


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    snouc__qeuy = in_arr.dtype(0)
    zhik__rezu = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        qqr__qwyyo = snouc__qeuy
        for twd__xpw in np.nditer(in_arr):
            qqr__qwyyo += twd__xpw.item()
        vst__wcdb = dist_exscan(qqr__qwyyo, zhik__rezu)
        for i in range(in_arr.size):
            vst__wcdb += in_arr[i]
            out_arr[i] = vst__wcdb
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    tve__lrg = in_arr.dtype(1)
    zhik__rezu = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        qqr__qwyyo = tve__lrg
        for twd__xpw in np.nditer(in_arr):
            qqr__qwyyo *= twd__xpw.item()
        vst__wcdb = dist_exscan(qqr__qwyyo, zhik__rezu)
        if get_rank() == 0:
            vst__wcdb = tve__lrg
        for i in range(in_arr.size):
            vst__wcdb *= in_arr[i]
            out_arr[i] = vst__wcdb
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        tve__lrg = np.finfo(in_arr.dtype(1).dtype).max
    else:
        tve__lrg = np.iinfo(in_arr.dtype(1).dtype).max
    zhik__rezu = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        qqr__qwyyo = tve__lrg
        for twd__xpw in np.nditer(in_arr):
            qqr__qwyyo = min(qqr__qwyyo, twd__xpw.item())
        vst__wcdb = dist_exscan(qqr__qwyyo, zhik__rezu)
        if get_rank() == 0:
            vst__wcdb = tve__lrg
        for i in range(in_arr.size):
            vst__wcdb = min(vst__wcdb, in_arr[i])
            out_arr[i] = vst__wcdb
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        tve__lrg = np.finfo(in_arr.dtype(1).dtype).min
    else:
        tve__lrg = np.iinfo(in_arr.dtype(1).dtype).min
    tve__lrg = in_arr.dtype(1)
    zhik__rezu = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        qqr__qwyyo = tve__lrg
        for twd__xpw in np.nditer(in_arr):
            qqr__qwyyo = max(qqr__qwyyo, twd__xpw.item())
        vst__wcdb = dist_exscan(qqr__qwyyo, zhik__rezu)
        if get_rank() == 0:
            vst__wcdb = tve__lrg
        for i in range(in_arr.size):
            vst__wcdb = max(vst__wcdb, in_arr[i])
            out_arr[i] = vst__wcdb
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    ybzme__ostts = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), ybzme__ostts)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ksis__buetd = args[0]
    if equiv_set.has_shape(ksis__buetd):
        return ArrayAnalysis.AnalyzeResult(shape=ksis__buetd, pre=[])
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
    bsbkc__kfhve = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for
        i, syfv__hvqar in enumerate(args) if is_array_typ(syfv__hvqar) or
        isinstance(syfv__hvqar, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    bhe__gzij = f"""def impl(*args):
    if {bsbkc__kfhve} or bodo.get_rank() == 0:
        print(*args)"""
    qcdj__rml = {}
    exec(bhe__gzij, globals(), qcdj__rml)
    impl = qcdj__rml['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        pbvq__kum = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        bhe__gzij = 'def f(req, cond=True):\n'
        bhe__gzij += f'  return {pbvq__kum}\n'
        qcdj__rml = {}
        exec(bhe__gzij, {'_wait': _wait}, qcdj__rml)
        impl = qcdj__rml['f']
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
        qrh__tnw = 1
        for a in t:
            qrh__tnw *= a
        return qrh__tnw
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    pmo__tnz = np.ascontiguousarray(in_arr)
    gfkk__foej = get_tuple_prod(pmo__tnz.shape[1:])
    ekkj__sfe = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        dssd__nhc = np.array(dest_ranks, dtype=np.int32)
    else:
        dssd__nhc = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, pmo__tnz.ctypes, new_dim0_global_len,
        len(in_arr), dtype_size * ekkj__sfe, dtype_size * gfkk__foej, len(
        dssd__nhc), dssd__nhc.ctypes)
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
    wplg__erpxa = np.ascontiguousarray(rhs)
    odnw__uop = get_tuple_prod(wplg__erpxa.shape[1:])
    fqxn__xkvnc = dtype_size * odnw__uop
    permutation_array_index(lhs.ctypes, lhs_len, fqxn__xkvnc, wplg__erpxa.
        ctypes, wplg__erpxa.shape[0], p.ctypes, p_len, n_samples)
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
        bhe__gzij = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        qcdj__rml = {}
        exec(bhe__gzij, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, qcdj__rml)
        byx__toyrj = qcdj__rml['bcast_scalar_impl']
        return byx__toyrj
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        bwzk__lirth = len(data.columns)
        fmbu__beafl = ', '.join('g_data_{}'.format(i) for i in range(
            bwzk__lirth))
        khct__irdx = ColNamesMetaType(data.columns)
        bhe__gzij = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(bwzk__lirth):
            bhe__gzij += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            bhe__gzij += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        bhe__gzij += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        bhe__gzij += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        bhe__gzij += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(fmbu__beafl))
        qcdj__rml = {}
        exec(bhe__gzij, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            khct__irdx}, qcdj__rml)
        oee__rnfa = qcdj__rml['impl_df']
        return oee__rnfa
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            yowse__gsld = data._start
            prloq__ipdg = data._stop
            toy__xok = data._step
            iskii__bub = data._name
            iskii__bub = bcast_scalar(iskii__bub, root)
            yowse__gsld = bcast_scalar(yowse__gsld, root)
            prloq__ipdg = bcast_scalar(prloq__ipdg, root)
            toy__xok = bcast_scalar(toy__xok, root)
            lvtd__iyuhv = bodo.libs.array_kernels.calc_nitems(yowse__gsld,
                prloq__ipdg, toy__xok)
            chunk_start = bodo.libs.distributed_api.get_start(lvtd__iyuhv,
                n_pes, rank)
            ytd__nfi = bodo.libs.distributed_api.get_node_portion(lvtd__iyuhv,
                n_pes, rank)
            crh__zumb = yowse__gsld + toy__xok * chunk_start
            xzc__wkk = yowse__gsld + toy__xok * (chunk_start + ytd__nfi)
            xzc__wkk = min(xzc__wkk, prloq__ipdg)
            return bodo.hiframes.pd_index_ext.init_range_index(crh__zumb,
                xzc__wkk, toy__xok, iskii__bub)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            ggbiy__qcjel = data._data
            iskii__bub = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(ggbiy__qcjel,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, iskii__bub)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            iskii__bub = bodo.hiframes.pd_series_ext.get_series_name(data)
            acu__ymcnz = bodo.libs.distributed_api.bcast_comm_impl(iskii__bub,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            cijmz__mqfs = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                cijmz__mqfs, acu__ymcnz)
        return impl_series
    if isinstance(data, types.BaseTuple):
        bhe__gzij = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        bhe__gzij += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        qcdj__rml = {}
        exec(bhe__gzij, {'bcast_comm_impl': bcast_comm_impl}, qcdj__rml)
        ipbmz__sykur = qcdj__rml['impl_tuple']
        return ipbmz__sykur
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    tgw__mlsy = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    kte__gex = (0,) * tgw__mlsy

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        ggbiy__qcjel = np.ascontiguousarray(data)
        yvvif__svx = data.ctypes
        qlvil__xigcb = kte__gex
        if rank == root:
            qlvil__xigcb = ggbiy__qcjel.shape
        qlvil__xigcb = bcast_tuple(qlvil__xigcb, root)
        mwo__wwz = get_tuple_prod(qlvil__xigcb[1:])
        send_counts = qlvil__xigcb[0] * mwo__wwz
        uqosx__fggda = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(yvvif__svx, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(uqosx__fggda.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return uqosx__fggda.reshape((-1,) + qlvil__xigcb[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        zblnp__eomp = MPI.COMM_WORLD
        gymp__gtagl = MPI.Get_processor_name()
        awb__jpeg = zblnp__eomp.allgather(gymp__gtagl)
        node_ranks = defaultdict(list)
        for i, pbbl__mpctd in enumerate(awb__jpeg):
            node_ranks[pbbl__mpctd].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    zblnp__eomp = MPI.COMM_WORLD
    ussmg__btvwd = zblnp__eomp.Get_group()
    hjlu__mlh = ussmg__btvwd.Incl(comm_ranks)
    hihod__rcq = zblnp__eomp.Create_group(hjlu__mlh)
    return hihod__rcq


def get_nodes_first_ranks():
    emlze__abq = get_host_ranks()
    return np.array([ylxgg__bfepv[0] for ylxgg__bfepv in emlze__abq.values(
        )], dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
