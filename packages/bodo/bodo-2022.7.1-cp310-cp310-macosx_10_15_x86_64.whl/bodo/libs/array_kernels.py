"""
Implements array kernels such as median and quantile.
"""
import hashlib
import inspect
import math
import operator
import re
import warnings
from math import sqrt
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types, typing
from numba.core.imputils import lower_builtin
from numba.core.ir_utils import find_const, guard
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload, overload_attribute, register_jitable
from numba.np.arrayobj import make_array
from numba.np.numpy_support import as_dtype
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, init_categorical_array
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import quantile_alg
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, drop_duplicates_table, info_from_table, info_to_array, sample_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, offset_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import DictionaryArrayType
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import str_arr_set_na, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, check_unsupported_args, decode_if_dict_array, element_type, find_common_np_dtype, get_overload_const_bool, get_overload_const_list, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error, to_str_arr_if_dict_array
from bodo.utils.utils import build_set_seen_na, check_and_propagate_cpp_exception, numba_to_c_type, unliteral_all
ll.add_symbol('quantile_sequential', quantile_alg.quantile_sequential)
ll.add_symbol('quantile_parallel', quantile_alg.quantile_parallel)
MPI_ROOT = 0
sum_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value)
max_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Max.value)
min_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Min.value)


def isna(arr, i):
    return False


@overload(isna)
def overload_isna(arr, i):
    i = types.unliteral(i)
    if arr == string_array_type:
        return lambda arr, i: bodo.libs.str_arr_ext.str_arr_is_na(arr, i)
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type,
        datetime_timedelta_array_type, string_array_split_view_type):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._null_bitmap, i)
    if isinstance(arr, ArrayItemArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, StructArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.struct_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, TupleArrayType):
        return lambda arr, i: bodo.libs.array_kernels.isna(arr._data, i)
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return lambda arr, i: arr.codes[i] == -1
    if arr == bodo.binary_array_type:
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr._data), i)
    if isinstance(arr, types.List):
        if arr.dtype == types.none:
            return lambda arr, i: True
        elif isinstance(arr.dtype, types.optional):
            return lambda arr, i: arr[i] is None
        else:
            return lambda arr, i: False
    if isinstance(arr, bodo.NullableTupleType):
        return lambda arr, i: arr._null_values[i]
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._indices._null_bitmap, i) or bodo.libs.array_kernels.isna(arr.
            _data, arr._indices[i])
    if isinstance(arr, DatetimeArrayType):
        return lambda arr, i: np.isnat(arr._data[i])
    assert isinstance(arr, types.Array), f'Invalid array type in isna(): {arr}'
    dtype = arr.dtype
    if isinstance(dtype, types.Float):
        return lambda arr, i: np.isnan(arr[i])
    if isinstance(dtype, (types.NPDatetime, types.NPTimedelta)):
        return lambda arr, i: np.isnat(arr[i])
    return lambda arr, i: False


def setna(arr, ind, int_nan_const=0):
    arr[ind] = np.nan


@overload(setna, no_unliteral=True)
def setna_overload(arr, ind, int_nan_const=0):
    if isinstance(arr.dtype, types.Float):
        return setna
    if isinstance(arr.dtype, (types.NPDatetime, types.NPTimedelta)):
        eqzco__uybo = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = eqzco__uybo
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        eqzco__uybo = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = eqzco__uybo
        return _setnan_impl
    if arr == string_array_type:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = ''
            str_arr_set_na(arr, ind)
        return impl
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, ind, int_nan_const=0: bodo.libs.array_kernels.setna(
            arr._indices, ind)
    if arr == boolean_array:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = False
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)):
        return (lambda arr, ind, int_nan_const=0: bodo.libs.int_arr_ext.
            set_bit_to_arr(arr._null_bitmap, ind, 0))
    if arr == bodo.binary_array_type:

        def impl_binary_arr(arr, ind, int_nan_const=0):
            otjay__uypq = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            otjay__uypq[ind + 1] = otjay__uypq[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            otjay__uypq = bodo.libs.array_item_arr_ext.get_offsets(arr)
            otjay__uypq[ind + 1] = otjay__uypq[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr), ind, 0)
        return impl_arr_item
    if isinstance(arr, bodo.libs.struct_arr_ext.StructArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.struct_arr_ext.
                get_null_bitmap(arr), ind, 0)
            data = bodo.libs.struct_arr_ext.get_data(arr)
            setna_tup(data, ind)
        return impl
    if isinstance(arr, TupleArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._data, ind)
        return impl
    if arr.dtype == types.bool_:

        def b_set(arr, ind, int_nan_const=0):
            arr[ind] = False
        return b_set
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):

        def setna_cat(arr, ind, int_nan_const=0):
            arr.codes[ind] = -1
        return setna_cat
    if isinstance(arr.dtype, types.Integer):

        def setna_int(arr, ind, int_nan_const=0):
            arr[ind] = int_nan_const
        return setna_int
    if arr == datetime_date_array_type:

        def setna_datetime_date(arr, ind, int_nan_const=0):
            arr._data[ind] = (1970 << 32) + (1 << 16) + 1
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_date
    if arr == datetime_timedelta_array_type:

        def setna_datetime_timedelta(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._days_data, ind)
            bodo.libs.array_kernels.setna(arr._seconds_data, ind)
            bodo.libs.array_kernels.setna(arr._microseconds_data, ind)
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_timedelta
    return lambda arr, ind, int_nan_const=0: None


def setna_tup(arr_tup, ind, int_nan_const=0):
    for arr in arr_tup:
        arr[ind] = np.nan


@overload(setna_tup, no_unliteral=True)
def overload_setna_tup(arr_tup, ind, int_nan_const=0):
    aotkp__znnqo = arr_tup.count
    yduo__xsdxa = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(aotkp__znnqo):
        yduo__xsdxa += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    yduo__xsdxa += '  return\n'
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'setna': setna}, zgrto__kjne)
    impl = zgrto__kjne['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        fkhlt__axucv = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(fkhlt__axucv.start, fkhlt__axucv.stop, fkhlt__axucv.step
            ):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        hru__exm = 'n'
        btz__ins = 'n_pes'
        xgdd__ocko = 'min_op'
    else:
        hru__exm = 'n-1, -1, -1'
        btz__ins = '-1'
        xgdd__ocko = 'max_op'
    yduo__xsdxa = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {btz__ins}
    for i in range({hru__exm}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {xgdd__ocko}))
        if possible_valid_rank != {btz__ins}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, zgrto__kjne)
    impl = zgrto__kjne['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    vvdh__tyeh = array_to_info(arr)
    _median_series_computation(res, vvdh__tyeh, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(vvdh__tyeh)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    vvdh__tyeh = array_to_info(arr)
    _autocorr_series_computation(res, vvdh__tyeh, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(vvdh__tyeh)


@numba.njit
def autocorr(arr, lag=1, parallel=False):
    res = np.empty(1, types.float64)
    autocorr_series_computation(res.ctypes, arr, lag, parallel)
    return res[0]


ll.add_symbol('compute_series_monotonicity', quantile_alg.
    compute_series_monotonicity)
_compute_series_monotonicity = types.ExternalFunction(
    'compute_series_monotonicity', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def series_monotonicity_call(res, arr, inc_dec, is_parallel):
    vvdh__tyeh = array_to_info(arr)
    _compute_series_monotonicity(res, vvdh__tyeh, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(vvdh__tyeh)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    pjxsx__gjtt = res[0] > 0.5
    return pjxsx__gjtt


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        grb__rts = '-'
        zqjx__fsyxd = 'index_arr[0] > threshhold_date'
        hru__exm = '1, n+1'
        lfhik__zjkt = 'index_arr[-i] <= threshhold_date'
        lpf__wjg = 'i - 1'
    else:
        grb__rts = '+'
        zqjx__fsyxd = 'index_arr[-1] < threshhold_date'
        hru__exm = 'n'
        lfhik__zjkt = 'index_arr[i] >= threshhold_date'
        lpf__wjg = 'i'
    yduo__xsdxa = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        yduo__xsdxa += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        yduo__xsdxa += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            yduo__xsdxa += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            yduo__xsdxa += """      threshhold_date = initial_date - date_offset.base + date_offset
"""
            yduo__xsdxa += '    else:\n'
            yduo__xsdxa += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            yduo__xsdxa += (
                f'    threshhold_date = initial_date {grb__rts} date_offset\n')
    else:
        yduo__xsdxa += f'  threshhold_date = initial_date {grb__rts} offset\n'
    yduo__xsdxa += '  local_valid = 0\n'
    yduo__xsdxa += f'  n = len(index_arr)\n'
    yduo__xsdxa += f'  if n:\n'
    yduo__xsdxa += f'    if {zqjx__fsyxd}:\n'
    yduo__xsdxa += '      loc_valid = n\n'
    yduo__xsdxa += '    else:\n'
    yduo__xsdxa += f'      for i in range({hru__exm}):\n'
    yduo__xsdxa += f'        if {lfhik__zjkt}:\n'
    yduo__xsdxa += f'          loc_valid = {lpf__wjg}\n'
    yduo__xsdxa += '          break\n'
    yduo__xsdxa += '  if is_parallel:\n'
    yduo__xsdxa += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    yduo__xsdxa += '    return total_valid\n'
    yduo__xsdxa += '  else:\n'
    yduo__xsdxa += '    return loc_valid\n'
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, zgrto__kjne)
    return zgrto__kjne['impl']


def quantile(A, q):
    return 0


def quantile_parallel(A, q):
    return 0


@infer_global(quantile)
@infer_global(quantile_parallel)
class QuantileType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) in [2, 3]
        return signature(types.float64, *unliteral_all(args))


@lower_builtin(quantile, types.Array, types.float64)
@lower_builtin(quantile, IntegerArrayType, types.float64)
@lower_builtin(quantile, BooleanArrayType, types.float64)
def lower_dist_quantile_seq(context, builder, sig, args):
    xmcu__kddtm = numba_to_c_type(sig.args[0].dtype)
    evvu__gecri = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), xmcu__kddtm))
    yvipy__fzcd = args[0]
    pmy__xcxhq = sig.args[0]
    if isinstance(pmy__xcxhq, (IntegerArrayType, BooleanArrayType)):
        yvipy__fzcd = cgutils.create_struct_proxy(pmy__xcxhq)(context,
            builder, yvipy__fzcd).data
        pmy__xcxhq = types.Array(pmy__xcxhq.dtype, 1, 'C')
    assert pmy__xcxhq.ndim == 1
    arr = make_array(pmy__xcxhq)(context, builder, yvipy__fzcd)
    gxsk__owi = builder.extract_value(arr.shape, 0)
    gzkap__ngiva = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        gxsk__owi, args[1], builder.load(evvu__gecri)]
    aegj__tkuw = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    skw__okrz = lir.FunctionType(lir.DoubleType(), aegj__tkuw)
    ksg__epow = cgutils.get_or_insert_function(builder.module, skw__okrz,
        name='quantile_sequential')
    vikl__jvdfd = builder.call(ksg__epow, gzkap__ngiva)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return vikl__jvdfd


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    xmcu__kddtm = numba_to_c_type(sig.args[0].dtype)
    evvu__gecri = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), xmcu__kddtm))
    yvipy__fzcd = args[0]
    pmy__xcxhq = sig.args[0]
    if isinstance(pmy__xcxhq, (IntegerArrayType, BooleanArrayType)):
        yvipy__fzcd = cgutils.create_struct_proxy(pmy__xcxhq)(context,
            builder, yvipy__fzcd).data
        pmy__xcxhq = types.Array(pmy__xcxhq.dtype, 1, 'C')
    assert pmy__xcxhq.ndim == 1
    arr = make_array(pmy__xcxhq)(context, builder, yvipy__fzcd)
    gxsk__owi = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        voja__vga = args[2]
    else:
        voja__vga = gxsk__owi
    gzkap__ngiva = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        gxsk__owi, voja__vga, args[1], builder.load(evvu__gecri)]
    aegj__tkuw = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType
        (64), lir.DoubleType(), lir.IntType(32)]
    skw__okrz = lir.FunctionType(lir.DoubleType(), aegj__tkuw)
    ksg__epow = cgutils.get_or_insert_function(builder.module, skw__okrz,
        name='quantile_parallel')
    vikl__jvdfd = builder.call(ksg__epow, gzkap__ngiva)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return vikl__jvdfd


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        pwt__aeznv = np.nonzero(pd.isna(arr))[0]
        whkvo__itp = arr[1:] != arr[:-1]
        whkvo__itp[pd.isna(whkvo__itp)] = False
        etnek__flfno = whkvo__itp.astype(np.bool_)
        fnpv__dut = np.concatenate((np.array([True]), etnek__flfno))
        if pwt__aeznv.size:
            ailc__kkk, rpqfy__jji = pwt__aeznv[0], pwt__aeznv[1:]
            fnpv__dut[ailc__kkk] = True
            if rpqfy__jji.size:
                fnpv__dut[rpqfy__jji] = False
                if rpqfy__jji[-1] + 1 < fnpv__dut.size:
                    fnpv__dut[rpqfy__jji[-1] + 1] = True
            elif ailc__kkk + 1 < fnpv__dut.size:
                fnpv__dut[ailc__kkk + 1] = True
        return fnpv__dut
    return impl


def rank(arr, method='average', na_option='keep', ascending=True, pct=False):
    return arr


@overload(rank, no_unliteral=True, inline='always')
def overload_rank(arr, method='average', na_option='keep', ascending=True,
    pct=False):
    if not is_overload_constant_str(method):
        raise_bodo_error(
            "Series.rank(): 'method' argument must be a constant string")
    method = get_overload_const_str(method)
    if not is_overload_constant_str(na_option):
        raise_bodo_error(
            "Series.rank(): 'na_option' argument must be a constant string")
    na_option = get_overload_const_str(na_option)
    if not is_overload_constant_bool(ascending):
        raise_bodo_error(
            "Series.rank(): 'ascending' argument must be a constant boolean")
    ascending = get_overload_const_bool(ascending)
    if not is_overload_constant_bool(pct):
        raise_bodo_error(
            "Series.rank(): 'pct' argument must be a constant boolean")
    pct = get_overload_const_bool(pct)
    if method == 'first' and not ascending:
        raise BodoError(
            "Series.rank(): method='first' with ascending=False is currently unsupported."
            )
    yduo__xsdxa = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    yduo__xsdxa += '  na_idxs = pd.isna(arr)\n'
    yduo__xsdxa += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    yduo__xsdxa += '  nas = sum(na_idxs)\n'
    if not ascending:
        yduo__xsdxa += '  if nas and nas < (sorter.size - 1):\n'
        yduo__xsdxa += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        yduo__xsdxa += '  else:\n'
        yduo__xsdxa += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        yduo__xsdxa += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    yduo__xsdxa += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    yduo__xsdxa += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        yduo__xsdxa += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        yduo__xsdxa += '    inv,\n'
        yduo__xsdxa += '    new_dtype=np.float64,\n'
        yduo__xsdxa += '    copy=True,\n'
        yduo__xsdxa += '    nan_to_str=False,\n'
        yduo__xsdxa += '    from_series=True,\n'
        yduo__xsdxa += '    ) + 1\n'
    else:
        yduo__xsdxa += '  arr = arr[sorter]\n'
        yduo__xsdxa += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        yduo__xsdxa += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            yduo__xsdxa += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            yduo__xsdxa += '    dense,\n'
            yduo__xsdxa += '    new_dtype=np.float64,\n'
            yduo__xsdxa += '    copy=True,\n'
            yduo__xsdxa += '    nan_to_str=False,\n'
            yduo__xsdxa += '    from_series=True,\n'
            yduo__xsdxa += '  )\n'
        else:
            yduo__xsdxa += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            yduo__xsdxa += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                yduo__xsdxa += '  ret = count_float[dense]\n'
            elif method == 'min':
                yduo__xsdxa += '  ret = count_float[dense - 1] + 1\n'
            else:
                yduo__xsdxa += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                yduo__xsdxa += '  ret[na_idxs] = -1\n'
            yduo__xsdxa += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            yduo__xsdxa += '  div_val = arr.size - nas\n'
        else:
            yduo__xsdxa += '  div_val = arr.size\n'
        yduo__xsdxa += '  for i in range(len(ret)):\n'
        yduo__xsdxa += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        yduo__xsdxa += '  ret[na_idxs] = np.nan\n'
    yduo__xsdxa += '  return ret\n'
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'np': np, 'pd': pd, 'bodo': bodo}, zgrto__kjne)
    return zgrto__kjne['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    jpg__usv = start
    mucz__gnwx = 2 * start + 1
    gsk__fcn = 2 * start + 2
    if mucz__gnwx < n and not cmp_f(arr[mucz__gnwx], arr[jpg__usv]):
        jpg__usv = mucz__gnwx
    if gsk__fcn < n and not cmp_f(arr[gsk__fcn], arr[jpg__usv]):
        jpg__usv = gsk__fcn
    if jpg__usv != start:
        arr[start], arr[jpg__usv] = arr[jpg__usv], arr[start]
        ind_arr[start], ind_arr[jpg__usv] = ind_arr[jpg__usv], ind_arr[start]
        min_heapify(arr, ind_arr, n, jpg__usv, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        ohmci__pbdc = np.empty(k, A.dtype)
        ftcd__tmazp = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                ohmci__pbdc[ind] = A[i]
                ftcd__tmazp[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            ohmci__pbdc = ohmci__pbdc[:ind]
            ftcd__tmazp = ftcd__tmazp[:ind]
        return ohmci__pbdc, ftcd__tmazp, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        yncx__fwutn = np.sort(A)
        pqka__nwmj = index_arr[np.argsort(A)]
        sax__zhh = pd.Series(yncx__fwutn).notna().values
        yncx__fwutn = yncx__fwutn[sax__zhh]
        pqka__nwmj = pqka__nwmj[sax__zhh]
        if is_largest:
            yncx__fwutn = yncx__fwutn[::-1]
            pqka__nwmj = pqka__nwmj[::-1]
        return np.ascontiguousarray(yncx__fwutn), np.ascontiguousarray(
            pqka__nwmj)
    ohmci__pbdc, ftcd__tmazp, start = select_k_nonan(A, index_arr, m, k)
    ftcd__tmazp = ftcd__tmazp[ohmci__pbdc.argsort()]
    ohmci__pbdc.sort()
    if not is_largest:
        ohmci__pbdc = np.ascontiguousarray(ohmci__pbdc[::-1])
        ftcd__tmazp = np.ascontiguousarray(ftcd__tmazp[::-1])
    for i in range(start, m):
        if cmp_f(A[i], ohmci__pbdc[0]):
            ohmci__pbdc[0] = A[i]
            ftcd__tmazp[0] = index_arr[i]
            min_heapify(ohmci__pbdc, ftcd__tmazp, k, 0, cmp_f)
    ftcd__tmazp = ftcd__tmazp[ohmci__pbdc.argsort()]
    ohmci__pbdc.sort()
    if is_largest:
        ohmci__pbdc = ohmci__pbdc[::-1]
        ftcd__tmazp = ftcd__tmazp[::-1]
    return np.ascontiguousarray(ohmci__pbdc), np.ascontiguousarray(ftcd__tmazp)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    jtnzo__jzni = bodo.libs.distributed_api.get_rank()
    ygjth__oqy, jctad__ovah = nlargest(A, I, k, is_largest, cmp_f)
    jpczz__omzfk = bodo.libs.distributed_api.gatherv(ygjth__oqy)
    fvak__ueb = bodo.libs.distributed_api.gatherv(jctad__ovah)
    if jtnzo__jzni == MPI_ROOT:
        res, slskl__xnqd = nlargest(jpczz__omzfk, fvak__ueb, k, is_largest,
            cmp_f)
    else:
        res = np.empty(k, A.dtype)
        slskl__xnqd = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(slskl__xnqd)
    return res, slskl__xnqd


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    zzkho__pznka, yms__tdw = mat.shape
    rdc__vmwe = np.empty((yms__tdw, yms__tdw), dtype=np.float64)
    for pzoz__gxfh in range(yms__tdw):
        for qjn__ceyoe in range(pzoz__gxfh + 1):
            nqrjg__kpx = 0
            avvs__mltd = jpu__fazll = djbk__knxz = wwxla__xum = 0.0
            for i in range(zzkho__pznka):
                if np.isfinite(mat[i, pzoz__gxfh]) and np.isfinite(mat[i,
                    qjn__ceyoe]):
                    ldka__jzcc = mat[i, pzoz__gxfh]
                    giilw__ecea = mat[i, qjn__ceyoe]
                    nqrjg__kpx += 1
                    djbk__knxz += ldka__jzcc
                    wwxla__xum += giilw__ecea
            if parallel:
                nqrjg__kpx = bodo.libs.distributed_api.dist_reduce(nqrjg__kpx,
                    sum_op)
                djbk__knxz = bodo.libs.distributed_api.dist_reduce(djbk__knxz,
                    sum_op)
                wwxla__xum = bodo.libs.distributed_api.dist_reduce(wwxla__xum,
                    sum_op)
            if nqrjg__kpx < minpv:
                rdc__vmwe[pzoz__gxfh, qjn__ceyoe] = rdc__vmwe[qjn__ceyoe,
                    pzoz__gxfh] = np.nan
            else:
                qfjb__lqwum = djbk__knxz / nqrjg__kpx
                lkee__ukrsg = wwxla__xum / nqrjg__kpx
                djbk__knxz = 0.0
                for i in range(zzkho__pznka):
                    if np.isfinite(mat[i, pzoz__gxfh]) and np.isfinite(mat[
                        i, qjn__ceyoe]):
                        ldka__jzcc = mat[i, pzoz__gxfh] - qfjb__lqwum
                        giilw__ecea = mat[i, qjn__ceyoe] - lkee__ukrsg
                        djbk__knxz += ldka__jzcc * giilw__ecea
                        avvs__mltd += ldka__jzcc * ldka__jzcc
                        jpu__fazll += giilw__ecea * giilw__ecea
                if parallel:
                    djbk__knxz = bodo.libs.distributed_api.dist_reduce(
                        djbk__knxz, sum_op)
                    avvs__mltd = bodo.libs.distributed_api.dist_reduce(
                        avvs__mltd, sum_op)
                    jpu__fazll = bodo.libs.distributed_api.dist_reduce(
                        jpu__fazll, sum_op)
                fya__qbp = nqrjg__kpx - 1.0 if cov else sqrt(avvs__mltd *
                    jpu__fazll)
                if fya__qbp != 0.0:
                    rdc__vmwe[pzoz__gxfh, qjn__ceyoe] = rdc__vmwe[
                        qjn__ceyoe, pzoz__gxfh] = djbk__knxz / fya__qbp
                else:
                    rdc__vmwe[pzoz__gxfh, qjn__ceyoe] = rdc__vmwe[
                        qjn__ceyoe, pzoz__gxfh] = np.nan
    return rdc__vmwe


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    lgf__ljmd = n != 1
    yduo__xsdxa = 'def impl(data, parallel=False):\n'
    yduo__xsdxa += '  if parallel:\n'
    ryaa__vqihl = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    yduo__xsdxa += f'    cpp_table = arr_info_list_to_table([{ryaa__vqihl}])\n'
    yduo__xsdxa += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    xkcf__tsxp = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    yduo__xsdxa += f'    data = ({xkcf__tsxp},)\n'
    yduo__xsdxa += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    yduo__xsdxa += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    yduo__xsdxa += '    bodo.libs.array.delete_table(cpp_table)\n'
    yduo__xsdxa += '  n = len(data[0])\n'
    yduo__xsdxa += '  out = np.empty(n, np.bool_)\n'
    yduo__xsdxa += '  uniqs = dict()\n'
    if lgf__ljmd:
        yduo__xsdxa += '  for i in range(n):\n'
        rae__oaxdy = ', '.join(f'data[{i}][i]' for i in range(n))
        ewh__oih = ',  '.join(f'bodo.libs.array_kernels.isna(data[{i}], i)' for
            i in range(n))
        yduo__xsdxa += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({rae__oaxdy},), ({ewh__oih},))
"""
        yduo__xsdxa += '    if val in uniqs:\n'
        yduo__xsdxa += '      out[i] = True\n'
        yduo__xsdxa += '    else:\n'
        yduo__xsdxa += '      out[i] = False\n'
        yduo__xsdxa += '      uniqs[val] = 0\n'
    else:
        yduo__xsdxa += '  data = data[0]\n'
        yduo__xsdxa += '  hasna = False\n'
        yduo__xsdxa += '  for i in range(n):\n'
        yduo__xsdxa += '    if bodo.libs.array_kernels.isna(data, i):\n'
        yduo__xsdxa += '      out[i] = hasna\n'
        yduo__xsdxa += '      hasna = True\n'
        yduo__xsdxa += '    else:\n'
        yduo__xsdxa += '      val = data[i]\n'
        yduo__xsdxa += '      if val in uniqs:\n'
        yduo__xsdxa += '        out[i] = True\n'
        yduo__xsdxa += '      else:\n'
        yduo__xsdxa += '        out[i] = False\n'
        yduo__xsdxa += '        uniqs[val] = 0\n'
    yduo__xsdxa += '  if parallel:\n'
    yduo__xsdxa += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    yduo__xsdxa += '  return out\n'
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        zgrto__kjne)
    impl = zgrto__kjne['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    aotkp__znnqo = len(data)
    yduo__xsdxa = (
        'def impl(data, ind_arr, n, frac, replace, parallel=False):\n')
    yduo__xsdxa += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        aotkp__znnqo)))
    yduo__xsdxa += '  table_total = arr_info_list_to_table(info_list_total)\n'
    yduo__xsdxa += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(aotkp__znnqo))
    for maty__rgph in range(aotkp__znnqo):
        yduo__xsdxa += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(maty__rgph, maty__rgph, maty__rgph))
    yduo__xsdxa += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(aotkp__znnqo))
    yduo__xsdxa += '  delete_table(out_table)\n'
    yduo__xsdxa += '  delete_table(table_total)\n'
    yduo__xsdxa += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(aotkp__znnqo)))
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, zgrto__kjne)
    impl = zgrto__kjne['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    aotkp__znnqo = len(data)
    yduo__xsdxa = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    yduo__xsdxa += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        aotkp__znnqo)))
    yduo__xsdxa += '  table_total = arr_info_list_to_table(info_list_total)\n'
    yduo__xsdxa += '  keep_i = 0\n'
    yduo__xsdxa += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for maty__rgph in range(aotkp__znnqo):
        yduo__xsdxa += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(maty__rgph, maty__rgph, maty__rgph))
    yduo__xsdxa += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(aotkp__znnqo))
    yduo__xsdxa += '  delete_table(out_table)\n'
    yduo__xsdxa += '  delete_table(table_total)\n'
    yduo__xsdxa += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(aotkp__znnqo)))
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, zgrto__kjne)
    impl = zgrto__kjne['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        pma__gbsaw = [array_to_info(data_arr)]
        uvgd__oajxq = arr_info_list_to_table(pma__gbsaw)
        yfetp__ossy = 0
        tfl__spt = drop_duplicates_table(uvgd__oajxq, parallel, 1,
            yfetp__ossy, False, True)
        cyh__jrv = info_to_array(info_from_table(tfl__spt, 0), data_arr)
        delete_table(tfl__spt)
        delete_table(uvgd__oajxq)
        return cyh__jrv
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    slfa__axo = len(data.types)
    ylczr__ekkt = [('out' + str(i)) for i in range(slfa__axo)]
    qhrtr__iyogt = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    kikjj__zyg = ['isna(data[{}], i)'.format(i) for i in qhrtr__iyogt]
    jmvw__wsm = 'not ({})'.format(' or '.join(kikjj__zyg))
    if not is_overload_none(thresh):
        jmvw__wsm = '(({}) <= ({}) - thresh)'.format(' + '.join(kikjj__zyg),
            slfa__axo - 1)
    elif how == 'all':
        jmvw__wsm = 'not ({})'.format(' and '.join(kikjj__zyg))
    yduo__xsdxa = 'def _dropna_imp(data, how, thresh, subset):\n'
    yduo__xsdxa += '  old_len = len(data[0])\n'
    yduo__xsdxa += '  new_len = 0\n'
    yduo__xsdxa += '  for i in range(old_len):\n'
    yduo__xsdxa += '    if {}:\n'.format(jmvw__wsm)
    yduo__xsdxa += '      new_len += 1\n'
    for i, out in enumerate(ylczr__ekkt):
        if isinstance(data[i], bodo.CategoricalArrayType):
            yduo__xsdxa += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            yduo__xsdxa += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    yduo__xsdxa += '  curr_ind = 0\n'
    yduo__xsdxa += '  for i in range(old_len):\n'
    yduo__xsdxa += '    if {}:\n'.format(jmvw__wsm)
    for i in range(slfa__axo):
        yduo__xsdxa += '      if isna(data[{}], i):\n'.format(i)
        yduo__xsdxa += '        setna({}, curr_ind)\n'.format(ylczr__ekkt[i])
        yduo__xsdxa += '      else:\n'
        yduo__xsdxa += '        {}[curr_ind] = data[{}][i]\n'.format(
            ylczr__ekkt[i], i)
    yduo__xsdxa += '      curr_ind += 1\n'
    yduo__xsdxa += '  return {}\n'.format(', '.join(ylczr__ekkt))
    zgrto__kjne = {}
    khsv__tyejk = {'t{}'.format(i): pevuz__lxcp for i, pevuz__lxcp in
        enumerate(data.types)}
    khsv__tyejk.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(yduo__xsdxa, khsv__tyejk, zgrto__kjne)
    boii__xxklz = zgrto__kjne['_dropna_imp']
    return boii__xxklz


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        pmy__xcxhq = arr.dtype
        pdmn__lqgjf = pmy__xcxhq.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            gum__llo = init_nested_counts(pdmn__lqgjf)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                gum__llo = add_nested_counts(gum__llo, val[ind])
            cyh__jrv = bodo.utils.utils.alloc_type(n, pmy__xcxhq, gum__llo)
            for ogudf__obi in range(n):
                if bodo.libs.array_kernels.isna(arr, ogudf__obi):
                    setna(cyh__jrv, ogudf__obi)
                    continue
                val = arr[ogudf__obi]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(cyh__jrv, ogudf__obi)
                    continue
                cyh__jrv[ogudf__obi] = val[ind]
            return cyh__jrv
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    lcqle__hxo = _to_readonly(arr_types.types[0])
    return all(isinstance(pevuz__lxcp, CategoricalArrayType) and 
        _to_readonly(pevuz__lxcp) == lcqle__hxo for pevuz__lxcp in
        arr_types.types)


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arr_list.
        dtype, 'bodo.concat()')
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        twpw__ygl = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            kfxut__faec = 0
            tvrsp__mgwx = []
            for A in arr_list:
                yswlr__ulc = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                tvrsp__mgwx.append(bodo.libs.array_item_arr_ext.get_data(A))
                kfxut__faec += yswlr__ulc
            kwwqp__ulep = np.empty(kfxut__faec + 1, offset_type)
            qvois__hsyec = bodo.libs.array_kernels.concat(tvrsp__mgwx)
            jod__ysmqf = np.empty(kfxut__faec + 7 >> 3, np.uint8)
            dbzed__tuwdn = 0
            rqvn__ntzvq = 0
            for A in arr_list:
                bgc__bopt = bodo.libs.array_item_arr_ext.get_offsets(A)
                tuwf__qwcik = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                yswlr__ulc = len(A)
                gipmj__yhwh = bgc__bopt[yswlr__ulc]
                for i in range(yswlr__ulc):
                    kwwqp__ulep[i + dbzed__tuwdn] = bgc__bopt[i] + rqvn__ntzvq
                    oormd__btwta = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        tuwf__qwcik, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jod__ysmqf, i +
                        dbzed__tuwdn, oormd__btwta)
                dbzed__tuwdn += yswlr__ulc
                rqvn__ntzvq += gipmj__yhwh
            kwwqp__ulep[dbzed__tuwdn] = rqvn__ntzvq
            cyh__jrv = bodo.libs.array_item_arr_ext.init_array_item_array(
                kfxut__faec, qvois__hsyec, kwwqp__ulep, jod__ysmqf)
            return cyh__jrv
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        bfzp__ewtxj = arr_list.dtype.names
        yduo__xsdxa = 'def struct_array_concat_impl(arr_list):\n'
        yduo__xsdxa += f'    n_all = 0\n'
        for i in range(len(bfzp__ewtxj)):
            yduo__xsdxa += f'    concat_list{i} = []\n'
        yduo__xsdxa += '    for A in arr_list:\n'
        yduo__xsdxa += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(bfzp__ewtxj)):
            yduo__xsdxa += f'        concat_list{i}.append(data_tuple[{i}])\n'
        yduo__xsdxa += '        n_all += len(A)\n'
        yduo__xsdxa += '    n_bytes = (n_all + 7) >> 3\n'
        yduo__xsdxa += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        yduo__xsdxa += '    curr_bit = 0\n'
        yduo__xsdxa += '    for A in arr_list:\n'
        yduo__xsdxa += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        yduo__xsdxa += '        for j in range(len(A)):\n'
        yduo__xsdxa += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        yduo__xsdxa += """            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)
"""
        yduo__xsdxa += '            curr_bit += 1\n'
        yduo__xsdxa += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        uxm__hdxkn = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(bfzp__ewtxj))])
        yduo__xsdxa += f'        ({uxm__hdxkn},),\n'
        yduo__xsdxa += '        new_mask,\n'
        yduo__xsdxa += f'        {bfzp__ewtxj},\n'
        yduo__xsdxa += '    )\n'
        zgrto__kjne = {}
        exec(yduo__xsdxa, {'bodo': bodo, 'np': np}, zgrto__kjne)
        return zgrto__kjne['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            gxn__hnw = 0
            for A in arr_list:
                gxn__hnw += len(A)
            cfcnk__yzd = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(gxn__hnw))
            zcoix__lfa = 0
            for A in arr_list:
                for i in range(len(A)):
                    cfcnk__yzd._data[i + zcoix__lfa] = A._data[i]
                    oormd__btwta = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(cfcnk__yzd.
                        _null_bitmap, i + zcoix__lfa, oormd__btwta)
                zcoix__lfa += len(A)
            return cfcnk__yzd
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            gxn__hnw = 0
            for A in arr_list:
                gxn__hnw += len(A)
            cfcnk__yzd = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(gxn__hnw))
            zcoix__lfa = 0
            for A in arr_list:
                for i in range(len(A)):
                    cfcnk__yzd._days_data[i + zcoix__lfa] = A._days_data[i]
                    cfcnk__yzd._seconds_data[i + zcoix__lfa] = A._seconds_data[
                        i]
                    cfcnk__yzd._microseconds_data[i + zcoix__lfa
                        ] = A._microseconds_data[i]
                    oormd__btwta = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(cfcnk__yzd.
                        _null_bitmap, i + zcoix__lfa, oormd__btwta)
                zcoix__lfa += len(A)
            return cfcnk__yzd
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        ywdy__ezx = arr_list.dtype.precision
        zex__xztts = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            gxn__hnw = 0
            for A in arr_list:
                gxn__hnw += len(A)
            cfcnk__yzd = bodo.libs.decimal_arr_ext.alloc_decimal_array(gxn__hnw
                , ywdy__ezx, zex__xztts)
            zcoix__lfa = 0
            for A in arr_list:
                for i in range(len(A)):
                    cfcnk__yzd._data[i + zcoix__lfa] = A._data[i]
                    oormd__btwta = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(cfcnk__yzd.
                        _null_bitmap, i + zcoix__lfa, oormd__btwta)
                zcoix__lfa += len(A)
            return cfcnk__yzd
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        pevuz__lxcp) for pevuz__lxcp in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            cvu__jguz = arr_list.types[0]
        else:
            cvu__jguz = arr_list.dtype
        cvu__jguz = to_str_arr_if_dict_array(cvu__jguz)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            wvfe__daeu = 0
            wqi__cxc = 0
            for A in arr_list:
                arr = A
                wvfe__daeu += len(arr)
                wqi__cxc += bodo.libs.str_arr_ext.num_total_chars(arr)
            cyh__jrv = bodo.utils.utils.alloc_type(wvfe__daeu, cvu__jguz, (
                wqi__cxc,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(cyh__jrv, -1)
            rwrz__cvo = 0
            mrto__tuvr = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(cyh__jrv, arr,
                    rwrz__cvo, mrto__tuvr)
                rwrz__cvo += len(arr)
                mrto__tuvr += bodo.libs.str_arr_ext.num_total_chars(arr)
            return cyh__jrv
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(pevuz__lxcp.dtype, types.Integer) for
        pevuz__lxcp in arr_list.types) and any(isinstance(pevuz__lxcp,
        IntegerArrayType) for pevuz__lxcp in arr_list.types):

        def impl_int_arr_list(arr_list):
            wck__qjqfg = convert_to_nullable_tup(arr_list)
            hnxk__qkf = []
            mvkxw__sakro = 0
            for A in wck__qjqfg:
                hnxk__qkf.append(A._data)
                mvkxw__sakro += len(A)
            qvois__hsyec = bodo.libs.array_kernels.concat(hnxk__qkf)
            zucsa__cvsrz = mvkxw__sakro + 7 >> 3
            zuxfh__dzba = np.empty(zucsa__cvsrz, np.uint8)
            cpwwd__pyfy = 0
            for A in wck__qjqfg:
                brnc__ndx = A._null_bitmap
                for ogudf__obi in range(len(A)):
                    oormd__btwta = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        brnc__ndx, ogudf__obi)
                    bodo.libs.int_arr_ext.set_bit_to_arr(zuxfh__dzba,
                        cpwwd__pyfy, oormd__btwta)
                    cpwwd__pyfy += 1
            return bodo.libs.int_arr_ext.init_integer_array(qvois__hsyec,
                zuxfh__dzba)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(pevuz__lxcp.dtype == types.bool_ for
        pevuz__lxcp in arr_list.types) and any(pevuz__lxcp == boolean_array for
        pevuz__lxcp in arr_list.types):

        def impl_bool_arr_list(arr_list):
            wck__qjqfg = convert_to_nullable_tup(arr_list)
            hnxk__qkf = []
            mvkxw__sakro = 0
            for A in wck__qjqfg:
                hnxk__qkf.append(A._data)
                mvkxw__sakro += len(A)
            qvois__hsyec = bodo.libs.array_kernels.concat(hnxk__qkf)
            zucsa__cvsrz = mvkxw__sakro + 7 >> 3
            zuxfh__dzba = np.empty(zucsa__cvsrz, np.uint8)
            cpwwd__pyfy = 0
            for A in wck__qjqfg:
                brnc__ndx = A._null_bitmap
                for ogudf__obi in range(len(A)):
                    oormd__btwta = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        brnc__ndx, ogudf__obi)
                    bodo.libs.int_arr_ext.set_bit_to_arr(zuxfh__dzba,
                        cpwwd__pyfy, oormd__btwta)
                    cpwwd__pyfy += 1
            return bodo.libs.bool_arr_ext.init_bool_array(qvois__hsyec,
                zuxfh__dzba)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            lnao__qmb = []
            for A in arr_list:
                lnao__qmb.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                lnao__qmb), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        mrme__nol = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        yduo__xsdxa = 'def impl(arr_list):\n'
        yduo__xsdxa += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({mrme__nol},)), arr_list[0].dtype)
"""
        dlg__uzkeg = {}
        exec(yduo__xsdxa, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, dlg__uzkeg)
        return dlg__uzkeg['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            mvkxw__sakro = 0
            for A in arr_list:
                mvkxw__sakro += len(A)
            cyh__jrv = np.empty(mvkxw__sakro, dtype)
            grmlw__iyir = 0
            for A in arr_list:
                n = len(A)
                cyh__jrv[grmlw__iyir:grmlw__iyir + n] = A
                grmlw__iyir += n
            return cyh__jrv
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(pevuz__lxcp,
        (types.Array, IntegerArrayType)) and isinstance(pevuz__lxcp.dtype,
        types.Integer) for pevuz__lxcp in arr_list.types) and any(
        isinstance(pevuz__lxcp, types.Array) and isinstance(pevuz__lxcp.
        dtype, types.Float) for pevuz__lxcp in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            tbtpy__iem = []
            for A in arr_list:
                tbtpy__iem.append(A._data)
            jlodr__npba = bodo.libs.array_kernels.concat(tbtpy__iem)
            rdc__vmwe = bodo.libs.map_arr_ext.init_map_arr(jlodr__npba)
            return rdc__vmwe
        return impl_map_arr_list
    for qiyn__xgnt in arr_list:
        if not isinstance(qiyn__xgnt, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(pevuz__lxcp.astype(np.float64) for pevuz__lxcp in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    aotkp__znnqo = len(arr_tup.types)
    yduo__xsdxa = 'def f(arr_tup):\n'
    yduo__xsdxa += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        aotkp__znnqo)), ',' if aotkp__znnqo == 1 else '')
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'np': np}, zgrto__kjne)
    qenca__pfl = zgrto__kjne['f']
    return qenca__pfl


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    aotkp__znnqo = len(arr_tup.types)
    xetic__yphf = find_common_np_dtype(arr_tup.types)
    pdmn__lqgjf = None
    owp__jxsvz = ''
    if isinstance(xetic__yphf, types.Integer):
        pdmn__lqgjf = bodo.libs.int_arr_ext.IntDtype(xetic__yphf)
        owp__jxsvz = '.astype(out_dtype, False)'
    yduo__xsdxa = 'def f(arr_tup):\n'
    yduo__xsdxa += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, owp__jxsvz) for i in range(aotkp__znnqo)), ',' if 
        aotkp__znnqo == 1 else '')
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'bodo': bodo, 'out_dtype': pdmn__lqgjf}, zgrto__kjne)
    peuh__zkhq = zgrto__kjne['f']
    return peuh__zkhq


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, nitns__jyhsg = build_set_seen_na(A)
        return len(s) + int(not dropna and nitns__jyhsg)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        vdrei__tvph = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        onovz__yyl = len(vdrei__tvph)
        return bodo.libs.distributed_api.dist_reduce(onovz__yyl, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([pebsc__siz for pebsc__siz in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        tnag__mpd = np.finfo(A.dtype(1).dtype).max
    else:
        tnag__mpd = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        cyh__jrv = np.empty(n, A.dtype)
        bdz__hpfst = tnag__mpd
        for i in range(n):
            bdz__hpfst = min(bdz__hpfst, A[i])
            cyh__jrv[i] = bdz__hpfst
        return cyh__jrv
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        tnag__mpd = np.finfo(A.dtype(1).dtype).min
    else:
        tnag__mpd = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        cyh__jrv = np.empty(n, A.dtype)
        bdz__hpfst = tnag__mpd
        for i in range(n):
            bdz__hpfst = max(bdz__hpfst, A[i])
            cyh__jrv[i] = bdz__hpfst
        return cyh__jrv
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        lfd__ivivr = arr_info_list_to_table([array_to_info(A)])
        elsk__xvpmi = 1
        yfetp__ossy = 0
        tfl__spt = drop_duplicates_table(lfd__ivivr, parallel, elsk__xvpmi,
            yfetp__ossy, dropna, True)
        cyh__jrv = info_to_array(info_from_table(tfl__spt, 0), A)
        delete_table(lfd__ivivr)
        delete_table(tfl__spt)
        return cyh__jrv
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    twpw__ygl = bodo.utils.typing.to_nullable_type(arr.dtype)
    rqyqp__yvazm = index_arr
    aai__nhctn = rqyqp__yvazm.dtype

    def impl(arr, index_arr):
        n = len(arr)
        gum__llo = init_nested_counts(twpw__ygl)
        nfyqr__vbvag = init_nested_counts(aai__nhctn)
        for i in range(n):
            fxtlx__lhis = index_arr[i]
            if isna(arr, i):
                gum__llo = (gum__llo[0] + 1,) + gum__llo[1:]
                nfyqr__vbvag = add_nested_counts(nfyqr__vbvag, fxtlx__lhis)
                continue
            ccln__nkyur = arr[i]
            if len(ccln__nkyur) == 0:
                gum__llo = (gum__llo[0] + 1,) + gum__llo[1:]
                nfyqr__vbvag = add_nested_counts(nfyqr__vbvag, fxtlx__lhis)
                continue
            gum__llo = add_nested_counts(gum__llo, ccln__nkyur)
            for lfq__yvl in range(len(ccln__nkyur)):
                nfyqr__vbvag = add_nested_counts(nfyqr__vbvag, fxtlx__lhis)
        cyh__jrv = bodo.utils.utils.alloc_type(gum__llo[0], twpw__ygl,
            gum__llo[1:])
        bwzlr__ffblr = bodo.utils.utils.alloc_type(gum__llo[0],
            rqyqp__yvazm, nfyqr__vbvag)
        rqvn__ntzvq = 0
        for i in range(n):
            if isna(arr, i):
                setna(cyh__jrv, rqvn__ntzvq)
                bwzlr__ffblr[rqvn__ntzvq] = index_arr[i]
                rqvn__ntzvq += 1
                continue
            ccln__nkyur = arr[i]
            gipmj__yhwh = len(ccln__nkyur)
            if gipmj__yhwh == 0:
                setna(cyh__jrv, rqvn__ntzvq)
                bwzlr__ffblr[rqvn__ntzvq] = index_arr[i]
                rqvn__ntzvq += 1
                continue
            cyh__jrv[rqvn__ntzvq:rqvn__ntzvq + gipmj__yhwh] = ccln__nkyur
            bwzlr__ffblr[rqvn__ntzvq:rqvn__ntzvq + gipmj__yhwh] = index_arr[i]
            rqvn__ntzvq += gipmj__yhwh
        return cyh__jrv, bwzlr__ffblr
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    twpw__ygl = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        gum__llo = init_nested_counts(twpw__ygl)
        for i in range(n):
            if isna(arr, i):
                gum__llo = (gum__llo[0] + 1,) + gum__llo[1:]
                xtia__lmet = 1
            else:
                ccln__nkyur = arr[i]
                ycoze__jfknb = len(ccln__nkyur)
                if ycoze__jfknb == 0:
                    gum__llo = (gum__llo[0] + 1,) + gum__llo[1:]
                    xtia__lmet = 1
                    continue
                else:
                    gum__llo = add_nested_counts(gum__llo, ccln__nkyur)
                    xtia__lmet = ycoze__jfknb
            if counts[i] != xtia__lmet:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        cyh__jrv = bodo.utils.utils.alloc_type(gum__llo[0], twpw__ygl,
            gum__llo[1:])
        rqvn__ntzvq = 0
        for i in range(n):
            if isna(arr, i):
                setna(cyh__jrv, rqvn__ntzvq)
                rqvn__ntzvq += 1
                continue
            ccln__nkyur = arr[i]
            gipmj__yhwh = len(ccln__nkyur)
            if gipmj__yhwh == 0:
                setna(cyh__jrv, rqvn__ntzvq)
                rqvn__ntzvq += 1
                continue
            cyh__jrv[rqvn__ntzvq:rqvn__ntzvq + gipmj__yhwh] = ccln__nkyur
            rqvn__ntzvq += gipmj__yhwh
        return cyh__jrv
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(elilf__jba) for elilf__jba in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        nxt__gdl = 'np.empty(n, np.int64)'
        qavv__owne = 'out_arr[i] = 1'
        iew__kwri = 'max(len(arr[i]), 1)'
    else:
        nxt__gdl = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        qavv__owne = 'bodo.libs.array_kernels.setna(out_arr, i)'
        iew__kwri = 'len(arr[i])'
    yduo__xsdxa = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {nxt__gdl}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {qavv__owne}
        else:
            out_arr[i] = {iew__kwri}
    return out_arr
    """
    zgrto__kjne = {}
    exec(yduo__xsdxa, {'bodo': bodo, 'numba': numba, 'np': np}, zgrto__kjne)
    impl = zgrto__kjne['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    rqyqp__yvazm = index_arr
    aai__nhctn = rqyqp__yvazm.dtype

    def impl(arr, pat, n, index_arr):
        ygftl__zlv = pat is not None and len(pat) > 1
        if ygftl__zlv:
            mush__okklp = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        ptgam__nlf = len(arr)
        wvfe__daeu = 0
        wqi__cxc = 0
        nfyqr__vbvag = init_nested_counts(aai__nhctn)
        for i in range(ptgam__nlf):
            fxtlx__lhis = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                wvfe__daeu += 1
                nfyqr__vbvag = add_nested_counts(nfyqr__vbvag, fxtlx__lhis)
                continue
            if ygftl__zlv:
                lbzs__ywf = mush__okklp.split(arr[i], maxsplit=n)
            else:
                lbzs__ywf = arr[i].split(pat, n)
            wvfe__daeu += len(lbzs__ywf)
            for s in lbzs__ywf:
                nfyqr__vbvag = add_nested_counts(nfyqr__vbvag, fxtlx__lhis)
                wqi__cxc += bodo.libs.str_arr_ext.get_utf8_size(s)
        cyh__jrv = bodo.libs.str_arr_ext.pre_alloc_string_array(wvfe__daeu,
            wqi__cxc)
        bwzlr__ffblr = bodo.utils.utils.alloc_type(wvfe__daeu, rqyqp__yvazm,
            nfyqr__vbvag)
        eus__ylmfp = 0
        for ogudf__obi in range(ptgam__nlf):
            if isna(arr, ogudf__obi):
                cyh__jrv[eus__ylmfp] = ''
                bodo.libs.array_kernels.setna(cyh__jrv, eus__ylmfp)
                bwzlr__ffblr[eus__ylmfp] = index_arr[ogudf__obi]
                eus__ylmfp += 1
                continue
            if ygftl__zlv:
                lbzs__ywf = mush__okklp.split(arr[ogudf__obi], maxsplit=n)
            else:
                lbzs__ywf = arr[ogudf__obi].split(pat, n)
            qffs__epgzq = len(lbzs__ywf)
            cyh__jrv[eus__ylmfp:eus__ylmfp + qffs__epgzq] = lbzs__ywf
            bwzlr__ffblr[eus__ylmfp:eus__ylmfp + qffs__epgzq] = index_arr[
                ogudf__obi]
            eus__ylmfp += qffs__epgzq
        return cyh__jrv, bwzlr__ffblr
    return impl


def gen_na_array(n, arr):
    return np.full(n, np.nan)


@overload(gen_na_array, no_unliteral=True)
def overload_gen_na_array(n, arr, use_dict_arr=False):
    if isinstance(arr, types.TypeRef):
        arr = arr.instance_type
    dtype = arr.dtype
    if not isinstance(arr, IntegerArrayType) and isinstance(dtype, (types.
        Integer, types.Float)):
        dtype = dtype if isinstance(dtype, types.Float) else types.float64

        def impl_float(n, arr, use_dict_arr=False):
            numba.parfors.parfor.init_prange()
            cyh__jrv = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                cyh__jrv[i] = np.nan
            return cyh__jrv
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            igji__fhze = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            cewyd__phe = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(cewyd__phe, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(igji__fhze,
                cewyd__phe, True)
        return impl_dict
    vvhy__oxh = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        cyh__jrv = bodo.utils.utils.alloc_type(n, vvhy__oxh, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(cyh__jrv, i)
        return cyh__jrv
    return impl


def gen_na_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_gen_na_array = (
    gen_na_array_equiv)


def resize_and_copy(A, new_len):
    return A


@overload(resize_and_copy, no_unliteral=True)
def overload_resize_and_copy(A, old_size, new_len):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.resize_and_copy()')
    wiwtg__gthg = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            cyh__jrv = bodo.utils.utils.alloc_type(new_len, wiwtg__gthg)
            bodo.libs.str_arr_ext.str_copy_ptr(cyh__jrv.ctypes, 0, A.ctypes,
                old_size)
            return cyh__jrv
        return impl_char

    def impl(A, old_size, new_len):
        cyh__jrv = bodo.utils.utils.alloc_type(new_len, wiwtg__gthg, (-1,))
        cyh__jrv[:old_size] = A[:old_size]
        return cyh__jrv
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    curq__rgew = math.ceil((stop - start) / step)
    return int(max(curq__rgew, 0))


def calc_nitems_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    if guard(find_const, self.func_ir, args[0]) == 0 and guard(find_const,
        self.func_ir, args[2]) == 1:
        return ArrayAnalysis.AnalyzeResult(shape=args[1], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_calc_nitems = (
    calc_nitems_equiv)


def arange_parallel_impl(return_type, *args):
    dtype = as_dtype(return_type.dtype)

    def arange_1(stop):
        return np.arange(0, stop, 1, dtype)

    def arange_2(start, stop):
        return np.arange(start, stop, 1, dtype)

    def arange_3(start, stop, step):
        return np.arange(start, stop, step, dtype)
    if any(isinstance(pebsc__siz, types.Complex) for pebsc__siz in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            pic__vvu = (stop - start) / step
            curq__rgew = math.ceil(pic__vvu.real)
            khdti__gsm = math.ceil(pic__vvu.imag)
            ufm__knudr = int(max(min(khdti__gsm, curq__rgew), 0))
            arr = np.empty(ufm__knudr, dtype)
            for i in numba.parfors.parfor.internal_prange(ufm__knudr):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            ufm__knudr = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(ufm__knudr, dtype)
            for i in numba.parfors.parfor.internal_prange(ufm__knudr):
                arr[i] = start + i * step
            return arr
    if len(args) == 1:
        return arange_1
    elif len(args) == 2:
        return arange_2
    elif len(args) == 3:
        return arange_3
    elif len(args) == 4:
        return arange_4
    else:
        raise BodoError('parallel arange with types {}'.format(args))


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.arange_parallel_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c72b0390b4f3e52dcc5426bd42c6b55ff96bae5a425381900985d36e7527a4bd':
        warnings.warn('numba.parfors.parfor.arange_parallel_impl has changed')
numba.parfors.parfor.swap_functions_map['arange', 'numpy'
    ] = arange_parallel_impl


def sort(arr, ascending, inplace):
    return np.sort(arr)


@overload(sort, no_unliteral=True)
def overload_sort(arr, ascending, inplace):

    def impl(arr, ascending, inplace):
        n = len(arr)
        data = np.arange(n),
        lva__ftsu = arr,
        if not inplace:
            lva__ftsu = arr.copy(),
        uawb__brxiq = bodo.libs.str_arr_ext.to_list_if_immutable_arr(lva__ftsu)
        hkuz__dcq = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(uawb__brxiq, 0, n, hkuz__dcq)
        if not ascending:
            bodo.libs.timsort.reverseRange(uawb__brxiq, 0, n, hkuz__dcq)
        bodo.libs.str_arr_ext.cp_str_list_to_array(lva__ftsu, uawb__brxiq)
        return lva__ftsu[0]
    return impl


def overload_array_max(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).max()
        return impl


overload(np.max, inline='always', no_unliteral=True)(overload_array_max)
overload(max, inline='always', no_unliteral=True)(overload_array_max)


def overload_array_min(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).min()
        return impl


overload(np.min, inline='always', no_unliteral=True)(overload_array_min)
overload(min, inline='always', no_unliteral=True)(overload_array_min)


def overload_array_sum(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).sum()
    return impl


overload(np.sum, inline='always', no_unliteral=True)(overload_array_sum)
overload(sum, inline='always', no_unliteral=True)(overload_array_sum)


@overload(np.prod, inline='always', no_unliteral=True)
def overload_array_prod(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).prod()
    return impl


def nonzero(arr):
    return arr,


@overload(nonzero, no_unliteral=True)
def nonzero_overload(A, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.nonzero()')
    if not bodo.utils.utils.is_array_typ(A, False):
        return

    def impl(A, parallel=False):
        n = len(A)
        if parallel:
            offset = bodo.libs.distributed_api.dist_exscan(n, Reduce_Type.
                Sum.value)
        else:
            offset = 0
        rdc__vmwe = []
        for i in range(n):
            if A[i]:
                rdc__vmwe.append(i + offset)
        return np.array(rdc__vmwe, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    wiwtg__gthg = element_type(A)
    if wiwtg__gthg == types.unicode_type:
        null_value = '""'
    elif wiwtg__gthg == types.bool_:
        null_value = 'False'
    elif wiwtg__gthg == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif wiwtg__gthg == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    eus__ylmfp = 'i'
    wjhui__bov = False
    zzq__slkj = get_overload_const_str(method)
    if zzq__slkj in ('ffill', 'pad'):
        lvdwy__ruj = 'n'
        send_right = True
    elif zzq__slkj in ('backfill', 'bfill'):
        lvdwy__ruj = 'n-1, -1, -1'
        send_right = False
        if wiwtg__gthg == types.unicode_type:
            eus__ylmfp = '(n - 1) - i'
            wjhui__bov = True
    yduo__xsdxa = 'def impl(A, method, parallel=False):\n'
    yduo__xsdxa += '  A = decode_if_dict_array(A)\n'
    yduo__xsdxa += '  has_last_value = False\n'
    yduo__xsdxa += f'  last_value = {null_value}\n'
    yduo__xsdxa += '  if parallel:\n'
    yduo__xsdxa += '    rank = bodo.libs.distributed_api.get_rank()\n'
    yduo__xsdxa += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    yduo__xsdxa += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    yduo__xsdxa += '  n = len(A)\n'
    yduo__xsdxa += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    yduo__xsdxa += f'  for i in range({lvdwy__ruj}):\n'
    yduo__xsdxa += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    yduo__xsdxa += (
        f'      bodo.libs.array_kernels.setna(out_arr, {eus__ylmfp})\n')
    yduo__xsdxa += '      continue\n'
    yduo__xsdxa += '    s = A[i]\n'
    yduo__xsdxa += '    if bodo.libs.array_kernels.isna(A, i):\n'
    yduo__xsdxa += '      s = last_value\n'
    yduo__xsdxa += f'    out_arr[{eus__ylmfp}] = s\n'
    yduo__xsdxa += '    last_value = s\n'
    yduo__xsdxa += '    has_last_value = True\n'
    if wjhui__bov:
        yduo__xsdxa += '  return out_arr[::-1]\n'
    else:
        yduo__xsdxa += '  return out_arr\n'
    szd__yeepr = {}
    exec(yduo__xsdxa, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, szd__yeepr)
    impl = szd__yeepr['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        yxl__imw = 0
        pcl__mga = n_pes - 1
        wbrcn__onlv = np.int32(rank + 1)
        mhl__blm = np.int32(rank - 1)
        rdwrs__jfty = len(in_arr) - 1
        dic__dkyn = -1
        zdau__zove = -1
    else:
        yxl__imw = n_pes - 1
        pcl__mga = 0
        wbrcn__onlv = np.int32(rank - 1)
        mhl__blm = np.int32(rank + 1)
        rdwrs__jfty = 0
        dic__dkyn = len(in_arr)
        zdau__zove = 1
    jav__cebzj = np.int32(bodo.hiframes.rolling.comm_border_tag)
    ltqlb__efkvs = np.empty(1, dtype=np.bool_)
    jws__nysg = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    lzqw__gqxnh = np.empty(1, dtype=np.bool_)
    ycf__ptovn = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    lln__oajcj = False
    uhhvo__iyk = null_value
    for i in range(rdwrs__jfty, dic__dkyn, zdau__zove):
        if not isna(in_arr, i):
            lln__oajcj = True
            uhhvo__iyk = in_arr[i]
            break
    if rank != yxl__imw:
        ndtc__sbn = bodo.libs.distributed_api.irecv(ltqlb__efkvs, 1,
            mhl__blm, jav__cebzj, True)
        bodo.libs.distributed_api.wait(ndtc__sbn, True)
        pjols__qkb = bodo.libs.distributed_api.irecv(jws__nysg, 1, mhl__blm,
            jav__cebzj, True)
        bodo.libs.distributed_api.wait(pjols__qkb, True)
        hks__eyjur = ltqlb__efkvs[0]
        ljiy__ztcos = jws__nysg[0]
    else:
        hks__eyjur = False
        ljiy__ztcos = null_value
    if lln__oajcj:
        lzqw__gqxnh[0] = lln__oajcj
        ycf__ptovn[0] = uhhvo__iyk
    else:
        lzqw__gqxnh[0] = hks__eyjur
        ycf__ptovn[0] = ljiy__ztcos
    if rank != pcl__mga:
        jdu__fdf = bodo.libs.distributed_api.isend(lzqw__gqxnh, 1,
            wbrcn__onlv, jav__cebzj, True)
        ang__gkp = bodo.libs.distributed_api.isend(ycf__ptovn, 1,
            wbrcn__onlv, jav__cebzj, True)
    return hks__eyjur, ljiy__ztcos


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    nbdgb__vijs = {'axis': axis, 'kind': kind, 'order': order}
    wmqi__mom = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', nbdgb__vijs, wmqi__mom, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    wiwtg__gthg = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            ptgam__nlf = len(A)
            cyh__jrv = bodo.utils.utils.alloc_type(ptgam__nlf * repeats,
                wiwtg__gthg, (-1,))
            for i in range(ptgam__nlf):
                eus__ylmfp = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for ogudf__obi in range(repeats):
                        bodo.libs.array_kernels.setna(cyh__jrv, eus__ylmfp +
                            ogudf__obi)
                else:
                    cyh__jrv[eus__ylmfp:eus__ylmfp + repeats] = A[i]
            return cyh__jrv
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        ptgam__nlf = len(A)
        cyh__jrv = bodo.utils.utils.alloc_type(repeats.sum(), wiwtg__gthg,
            (-1,))
        eus__ylmfp = 0
        for i in range(ptgam__nlf):
            ackhw__vxnvk = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for ogudf__obi in range(ackhw__vxnvk):
                    bodo.libs.array_kernels.setna(cyh__jrv, eus__ylmfp +
                        ogudf__obi)
            else:
                cyh__jrv[eus__ylmfp:eus__ylmfp + ackhw__vxnvk] = A[i]
            eus__ylmfp += ackhw__vxnvk
        return cyh__jrv
    return impl_arr


@overload(np.repeat, inline='always', no_unliteral=True)
def np_repeat(A, repeats):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    if not isinstance(repeats, types.Integer):
        raise BodoError(
            'Only integer type supported for repeats in np.repeat()')

    def impl(A, repeats):
        return bodo.libs.array_kernels.repeat_kernel(A, repeats)
    return impl


@numba.generated_jit
def repeat_like(A, dist_like_arr):
    if not bodo.utils.utils.is_array_typ(A, False
        ) or not bodo.utils.utils.is_array_typ(dist_like_arr, False):
        raise BodoError('Both A and dist_like_arr must be array-like.')

    def impl(A, dist_like_arr):
        return bodo.libs.array_kernels.repeat_kernel(A, len(dist_like_arr))
    return impl


@overload(np.unique, inline='always', no_unliteral=True)
def np_unique(A):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return

    def impl(A):
        rru__unoy = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(rru__unoy, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        hxdpg__vbg = bodo.libs.array_kernels.concat([A1, A2])
        ucwbu__sqqxk = bodo.libs.array_kernels.unique(hxdpg__vbg)
        return pd.Series(ucwbu__sqqxk).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    nbdgb__vijs = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    wmqi__mom = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', nbdgb__vijs, wmqi__mom, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        tftyx__vdoix = bodo.libs.array_kernels.unique(A1)
        iso__zvag = bodo.libs.array_kernels.unique(A2)
        hxdpg__vbg = bodo.libs.array_kernels.concat([tftyx__vdoix, iso__zvag])
        zwx__zcdho = pd.Series(hxdpg__vbg).sort_values().values
        return slice_array_intersect1d(zwx__zcdho)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    sax__zhh = arr[1:] == arr[:-1]
    return arr[:-1][sax__zhh]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    jav__cebzj = np.int32(bodo.hiframes.rolling.comm_border_tag)
    mxurt__zlgv = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        qhal__mnny = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), jav__cebzj, True)
        bodo.libs.distributed_api.wait(qhal__mnny, True)
    if rank == n_pes - 1:
        return None
    else:
        kpnau__djyy = bodo.libs.distributed_api.irecv(mxurt__zlgv, 1, np.
            int32(rank + 1), jav__cebzj, True)
        bodo.libs.distributed_api.wait(kpnau__djyy, True)
        return mxurt__zlgv[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    sax__zhh = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            sax__zhh[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        ehpyw__klme = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == ehpyw__klme:
            sax__zhh[n - 1] = True
    return sax__zhh


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    nbdgb__vijs = {'assume_unique': assume_unique}
    wmqi__mom = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', nbdgb__vijs, wmqi__mom, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        tftyx__vdoix = bodo.libs.array_kernels.unique(A1)
        iso__zvag = bodo.libs.array_kernels.unique(A2)
        sax__zhh = calculate_mask_setdiff1d(tftyx__vdoix, iso__zvag)
        return pd.Series(tftyx__vdoix[sax__zhh]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    sax__zhh = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        sax__zhh &= A1 != A2[i]
    return sax__zhh


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    nbdgb__vijs = {'retstep': retstep, 'axis': axis}
    wmqi__mom = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', nbdgb__vijs, wmqi__mom, 'numpy')
    lzbaa__nwt = False
    if is_overload_none(dtype):
        wiwtg__gthg = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            lzbaa__nwt = True
        wiwtg__gthg = numba.np.numpy_support.as_dtype(dtype).type
    if lzbaa__nwt:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            ojem__vpxdi = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            cyh__jrv = np.empty(num, wiwtg__gthg)
            for i in numba.parfors.parfor.internal_prange(num):
                cyh__jrv[i] = wiwtg__gthg(np.floor(start + i * ojem__vpxdi))
            return cyh__jrv
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            ojem__vpxdi = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            cyh__jrv = np.empty(num, wiwtg__gthg)
            for i in numba.parfors.parfor.internal_prange(num):
                cyh__jrv[i] = wiwtg__gthg(start + i * ojem__vpxdi)
            return cyh__jrv
        return impl


def np_linspace_get_stepsize(start, stop, num, endpoint):
    return 0


@overload(np_linspace_get_stepsize, no_unliteral=True)
def overload_np_linspace_get_stepsize(start, stop, num, endpoint):

    def impl(start, stop, num, endpoint):
        if num < 0:
            raise ValueError('np.linspace() Num must be >= 0')
        if endpoint:
            num -= 1
        if num > 1:
            return (stop - start) / num
        return 0
    return impl


@overload(operator.contains, no_unliteral=True)
def arr_contains(A, val):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'np.contains()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.dtype == types.
        unliteral(val)):
        return

    def impl(A, val):
        numba.parfors.parfor.init_prange()
        aotkp__znnqo = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                aotkp__znnqo += A[i] == val
        return aotkp__znnqo > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    nbdgb__vijs = {'axis': axis, 'out': out, 'keepdims': keepdims}
    wmqi__mom = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', nbdgb__vijs, wmqi__mom, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        aotkp__znnqo = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                aotkp__znnqo += int(bool(A[i]))
        return aotkp__znnqo > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    nbdgb__vijs = {'axis': axis, 'out': out, 'keepdims': keepdims}
    wmqi__mom = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', nbdgb__vijs, wmqi__mom, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        aotkp__znnqo = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                aotkp__znnqo += int(bool(A[i]))
        return aotkp__znnqo == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    nbdgb__vijs = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    wmqi__mom = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', nbdgb__vijs, wmqi__mom, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        uqulj__wfay = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            cyh__jrv = np.empty(n, uqulj__wfay)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(cyh__jrv, i)
                    continue
                cyh__jrv[i] = np_cbrt_scalar(A[i], uqulj__wfay)
            return cyh__jrv
        return impl_arr
    uqulj__wfay = np.promote_types(numba.np.numpy_support.as_dtype(A),
        numba.np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, uqulj__wfay)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    yua__boso = x < 0
    if yua__boso:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if yua__boso:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    fah__bma = isinstance(tup, (types.BaseTuple, types.List))
    mcmm__zftc = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for qiyn__xgnt in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                qiyn__xgnt, 'numpy.hstack()')
            fah__bma = fah__bma and bodo.utils.utils.is_array_typ(qiyn__xgnt,
                False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        fah__bma = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif mcmm__zftc:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        dqvgn__wqic = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for qiyn__xgnt in dqvgn__wqic.types:
            mcmm__zftc = mcmm__zftc and bodo.utils.utils.is_array_typ(
                qiyn__xgnt, False)
    if not (fah__bma or mcmm__zftc):
        return
    if mcmm__zftc:

        def impl_series(tup):
            arr_tup = bodo.hiframes.pd_series_ext.get_series_data(tup)
            return bodo.libs.array_kernels.concat(arr_tup)
        return impl_series

    def impl(tup):
        return bodo.libs.array_kernels.concat(tup)
    return impl


@overload(np.random.multivariate_normal, inline='always', no_unliteral=True)
def np_random_multivariate_normal(mean, cov, size=None, check_valid='warn',
    tol=1e-08):
    nbdgb__vijs = {'check_valid': check_valid, 'tol': tol}
    wmqi__mom = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', nbdgb__vijs,
        wmqi__mom, 'numpy')
    if not isinstance(size, types.Integer):
        raise BodoError(
            'np.random.multivariate_normal() size argument is required and must be an integer'
            )
    if not (bodo.utils.utils.is_array_typ(mean, False) and mean.ndim == 1):
        raise BodoError(
            'np.random.multivariate_normal() mean must be a 1 dimensional numpy array'
            )
    if not (bodo.utils.utils.is_array_typ(cov, False) and cov.ndim == 2):
        raise BodoError(
            'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
            )

    def impl(mean, cov, size=None, check_valid='warn', tol=1e-08):
        _validate_multivar_norm(cov)
        zzkho__pznka = mean.shape[0]
        skx__szkax = size, zzkho__pznka
        jiqb__fduls = np.random.standard_normal(skx__szkax)
        cov = cov.astype(np.float64)
        hnh__bjycu, s, noizj__eshx = np.linalg.svd(cov)
        res = np.dot(jiqb__fduls, np.sqrt(s).reshape(zzkho__pznka, 1) *
            noizj__eshx)
        prvwt__miro = res + mean
        return prvwt__miro
    return impl


def _validate_multivar_norm(cov):
    return


@overload(_validate_multivar_norm, no_unliteral=True)
def _overload_validate_multivar_norm(cov):

    def impl(cov):
        if cov.shape[0] != cov.shape[1]:
            raise ValueError(
                'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
                )
    return impl


def _nan_argmin(arr):
    return


@overload(_nan_argmin, no_unliteral=True)
def _overload_nan_argmin(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            numba.parfors.parfor.init_prange()
            btz__ins = bodo.hiframes.series_kernels._get_type_max_value(arr)
            obicw__tuhte = typing.builtins.IndexValue(-1, btz__ins)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                yly__ntz = typing.builtins.IndexValue(i, arr[i])
                obicw__tuhte = min(obicw__tuhte, yly__ntz)
            return obicw__tuhte.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        fnblg__gop = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            lzz__qsxw = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            btz__ins = fnblg__gop(len(arr.dtype.categories) + 1)
            obicw__tuhte = typing.builtins.IndexValue(-1, btz__ins)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                yly__ntz = typing.builtins.IndexValue(i, lzz__qsxw[i])
                obicw__tuhte = min(obicw__tuhte, yly__ntz)
            return obicw__tuhte.index
        return impl_cat_arr
    return lambda arr: arr.argmin()


def _nan_argmax(arr):
    return


@overload(_nan_argmax, no_unliteral=True)
def _overload_nan_argmax(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            n = len(arr)
            numba.parfors.parfor.init_prange()
            btz__ins = bodo.hiframes.series_kernels._get_type_min_value(arr)
            obicw__tuhte = typing.builtins.IndexValue(-1, btz__ins)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                yly__ntz = typing.builtins.IndexValue(i, arr[i])
                obicw__tuhte = max(obicw__tuhte, yly__ntz)
            return obicw__tuhte.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        fnblg__gop = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            lzz__qsxw = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            btz__ins = fnblg__gop(-1)
            obicw__tuhte = typing.builtins.IndexValue(-1, btz__ins)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                yly__ntz = typing.builtins.IndexValue(i, lzz__qsxw[i])
                obicw__tuhte = max(obicw__tuhte, yly__ntz)
            return obicw__tuhte.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
