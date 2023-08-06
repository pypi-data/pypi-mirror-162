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
        regkx__igd = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = regkx__igd
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        regkx__igd = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = regkx__igd
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
            vljwj__krkh = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            vljwj__krkh[ind + 1] = vljwj__krkh[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            vljwj__krkh = bodo.libs.array_item_arr_ext.get_offsets(arr)
            vljwj__krkh[ind + 1] = vljwj__krkh[ind]
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
    vfpt__opfnp = arr_tup.count
    jlm__kodko = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(vfpt__opfnp):
        jlm__kodko += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    jlm__kodko += '  return\n'
    ayti__hlgh = {}
    exec(jlm__kodko, {'setna': setna}, ayti__hlgh)
    impl = ayti__hlgh['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        hpg__rthm = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(hpg__rthm.start, hpg__rthm.stop, hpg__rthm.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        ultic__fil = 'n'
        mqtxc__ghboi = 'n_pes'
        jvu__gelx = 'min_op'
    else:
        ultic__fil = 'n-1, -1, -1'
        mqtxc__ghboi = '-1'
        jvu__gelx = 'max_op'
    jlm__kodko = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {mqtxc__ghboi}
    for i in range({ultic__fil}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {jvu__gelx}))
        if possible_valid_rank != {mqtxc__ghboi}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    ayti__hlgh = {}
    exec(jlm__kodko, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, ayti__hlgh)
    impl = ayti__hlgh['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    mfd__wlbsn = array_to_info(arr)
    _median_series_computation(res, mfd__wlbsn, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(mfd__wlbsn)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    mfd__wlbsn = array_to_info(arr)
    _autocorr_series_computation(res, mfd__wlbsn, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(mfd__wlbsn)


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
    mfd__wlbsn = array_to_info(arr)
    _compute_series_monotonicity(res, mfd__wlbsn, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(mfd__wlbsn)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    hfw__fzrw = res[0] > 0.5
    return hfw__fzrw


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        sxls__wocro = '-'
        fbs__arhj = 'index_arr[0] > threshhold_date'
        ultic__fil = '1, n+1'
        dluow__xoxbl = 'index_arr[-i] <= threshhold_date'
        jrgzs__xwmx = 'i - 1'
    else:
        sxls__wocro = '+'
        fbs__arhj = 'index_arr[-1] < threshhold_date'
        ultic__fil = 'n'
        dluow__xoxbl = 'index_arr[i] >= threshhold_date'
        jrgzs__xwmx = 'i'
    jlm__kodko = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        jlm__kodko += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        jlm__kodko += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            jlm__kodko += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            jlm__kodko += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            jlm__kodko += '    else:\n'
            jlm__kodko += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            jlm__kodko += (
                f'    threshhold_date = initial_date {sxls__wocro} date_offset\n'
                )
    else:
        jlm__kodko += (
            f'  threshhold_date = initial_date {sxls__wocro} offset\n')
    jlm__kodko += '  local_valid = 0\n'
    jlm__kodko += f'  n = len(index_arr)\n'
    jlm__kodko += f'  if n:\n'
    jlm__kodko += f'    if {fbs__arhj}:\n'
    jlm__kodko += '      loc_valid = n\n'
    jlm__kodko += '    else:\n'
    jlm__kodko += f'      for i in range({ultic__fil}):\n'
    jlm__kodko += f'        if {dluow__xoxbl}:\n'
    jlm__kodko += f'          loc_valid = {jrgzs__xwmx}\n'
    jlm__kodko += '          break\n'
    jlm__kodko += '  if is_parallel:\n'
    jlm__kodko += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    jlm__kodko += '    return total_valid\n'
    jlm__kodko += '  else:\n'
    jlm__kodko += '    return loc_valid\n'
    ayti__hlgh = {}
    exec(jlm__kodko, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, ayti__hlgh)
    return ayti__hlgh['impl']


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
    bzgel__vbqo = numba_to_c_type(sig.args[0].dtype)
    jfwar__ekn = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), bzgel__vbqo))
    ctzk__taee = args[0]
    mone__xiyvl = sig.args[0]
    if isinstance(mone__xiyvl, (IntegerArrayType, BooleanArrayType)):
        ctzk__taee = cgutils.create_struct_proxy(mone__xiyvl)(context,
            builder, ctzk__taee).data
        mone__xiyvl = types.Array(mone__xiyvl.dtype, 1, 'C')
    assert mone__xiyvl.ndim == 1
    arr = make_array(mone__xiyvl)(context, builder, ctzk__taee)
    wpdw__kjzuj = builder.extract_value(arr.shape, 0)
    qjio__rhv = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        wpdw__kjzuj, args[1], builder.load(jfwar__ekn)]
    zydz__ziq = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    eqmvs__vuc = lir.FunctionType(lir.DoubleType(), zydz__ziq)
    dfa__nso = cgutils.get_or_insert_function(builder.module, eqmvs__vuc,
        name='quantile_sequential')
    tgdeg__bqvff = builder.call(dfa__nso, qjio__rhv)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return tgdeg__bqvff


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    bzgel__vbqo = numba_to_c_type(sig.args[0].dtype)
    jfwar__ekn = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), bzgel__vbqo))
    ctzk__taee = args[0]
    mone__xiyvl = sig.args[0]
    if isinstance(mone__xiyvl, (IntegerArrayType, BooleanArrayType)):
        ctzk__taee = cgutils.create_struct_proxy(mone__xiyvl)(context,
            builder, ctzk__taee).data
        mone__xiyvl = types.Array(mone__xiyvl.dtype, 1, 'C')
    assert mone__xiyvl.ndim == 1
    arr = make_array(mone__xiyvl)(context, builder, ctzk__taee)
    wpdw__kjzuj = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        knhzc__wotk = args[2]
    else:
        knhzc__wotk = wpdw__kjzuj
    qjio__rhv = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        wpdw__kjzuj, knhzc__wotk, args[1], builder.load(jfwar__ekn)]
    zydz__ziq = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType(
        64), lir.DoubleType(), lir.IntType(32)]
    eqmvs__vuc = lir.FunctionType(lir.DoubleType(), zydz__ziq)
    dfa__nso = cgutils.get_or_insert_function(builder.module, eqmvs__vuc,
        name='quantile_parallel')
    tgdeg__bqvff = builder.call(dfa__nso, qjio__rhv)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return tgdeg__bqvff


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        uop__xfdm = np.nonzero(pd.isna(arr))[0]
        iyl__siujq = arr[1:] != arr[:-1]
        iyl__siujq[pd.isna(iyl__siujq)] = False
        bvu__zixj = iyl__siujq.astype(np.bool_)
        bexe__ahokc = np.concatenate((np.array([True]), bvu__zixj))
        if uop__xfdm.size:
            vlhm__vbbv, cowfc__cex = uop__xfdm[0], uop__xfdm[1:]
            bexe__ahokc[vlhm__vbbv] = True
            if cowfc__cex.size:
                bexe__ahokc[cowfc__cex] = False
                if cowfc__cex[-1] + 1 < bexe__ahokc.size:
                    bexe__ahokc[cowfc__cex[-1] + 1] = True
            elif vlhm__vbbv + 1 < bexe__ahokc.size:
                bexe__ahokc[vlhm__vbbv + 1] = True
        return bexe__ahokc
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
    jlm__kodko = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    jlm__kodko += '  na_idxs = pd.isna(arr)\n'
    jlm__kodko += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    jlm__kodko += '  nas = sum(na_idxs)\n'
    if not ascending:
        jlm__kodko += '  if nas and nas < (sorter.size - 1):\n'
        jlm__kodko += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        jlm__kodko += '  else:\n'
        jlm__kodko += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        jlm__kodko += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    jlm__kodko += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    jlm__kodko += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        jlm__kodko += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        jlm__kodko += '    inv,\n'
        jlm__kodko += '    new_dtype=np.float64,\n'
        jlm__kodko += '    copy=True,\n'
        jlm__kodko += '    nan_to_str=False,\n'
        jlm__kodko += '    from_series=True,\n'
        jlm__kodko += '    ) + 1\n'
    else:
        jlm__kodko += '  arr = arr[sorter]\n'
        jlm__kodko += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        jlm__kodko += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            jlm__kodko += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            jlm__kodko += '    dense,\n'
            jlm__kodko += '    new_dtype=np.float64,\n'
            jlm__kodko += '    copy=True,\n'
            jlm__kodko += '    nan_to_str=False,\n'
            jlm__kodko += '    from_series=True,\n'
            jlm__kodko += '  )\n'
        else:
            jlm__kodko += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            jlm__kodko += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                jlm__kodko += '  ret = count_float[dense]\n'
            elif method == 'min':
                jlm__kodko += '  ret = count_float[dense - 1] + 1\n'
            else:
                jlm__kodko += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                jlm__kodko += '  ret[na_idxs] = -1\n'
            jlm__kodko += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            jlm__kodko += '  div_val = arr.size - nas\n'
        else:
            jlm__kodko += '  div_val = arr.size\n'
        jlm__kodko += '  for i in range(len(ret)):\n'
        jlm__kodko += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        jlm__kodko += '  ret[na_idxs] = np.nan\n'
    jlm__kodko += '  return ret\n'
    ayti__hlgh = {}
    exec(jlm__kodko, {'np': np, 'pd': pd, 'bodo': bodo}, ayti__hlgh)
    return ayti__hlgh['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    epcxt__ygv = start
    jsbb__ehu = 2 * start + 1
    dtfbn__euu = 2 * start + 2
    if jsbb__ehu < n and not cmp_f(arr[jsbb__ehu], arr[epcxt__ygv]):
        epcxt__ygv = jsbb__ehu
    if dtfbn__euu < n and not cmp_f(arr[dtfbn__euu], arr[epcxt__ygv]):
        epcxt__ygv = dtfbn__euu
    if epcxt__ygv != start:
        arr[start], arr[epcxt__ygv] = arr[epcxt__ygv], arr[start]
        ind_arr[start], ind_arr[epcxt__ygv] = ind_arr[epcxt__ygv], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, epcxt__ygv, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        wdlw__imtb = np.empty(k, A.dtype)
        kzwwo__mylpq = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                wdlw__imtb[ind] = A[i]
                kzwwo__mylpq[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            wdlw__imtb = wdlw__imtb[:ind]
            kzwwo__mylpq = kzwwo__mylpq[:ind]
        return wdlw__imtb, kzwwo__mylpq, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        smbwu__ntjpe = np.sort(A)
        bkjx__gqptr = index_arr[np.argsort(A)]
        zdtuc__wyjoz = pd.Series(smbwu__ntjpe).notna().values
        smbwu__ntjpe = smbwu__ntjpe[zdtuc__wyjoz]
        bkjx__gqptr = bkjx__gqptr[zdtuc__wyjoz]
        if is_largest:
            smbwu__ntjpe = smbwu__ntjpe[::-1]
            bkjx__gqptr = bkjx__gqptr[::-1]
        return np.ascontiguousarray(smbwu__ntjpe), np.ascontiguousarray(
            bkjx__gqptr)
    wdlw__imtb, kzwwo__mylpq, start = select_k_nonan(A, index_arr, m, k)
    kzwwo__mylpq = kzwwo__mylpq[wdlw__imtb.argsort()]
    wdlw__imtb.sort()
    if not is_largest:
        wdlw__imtb = np.ascontiguousarray(wdlw__imtb[::-1])
        kzwwo__mylpq = np.ascontiguousarray(kzwwo__mylpq[::-1])
    for i in range(start, m):
        if cmp_f(A[i], wdlw__imtb[0]):
            wdlw__imtb[0] = A[i]
            kzwwo__mylpq[0] = index_arr[i]
            min_heapify(wdlw__imtb, kzwwo__mylpq, k, 0, cmp_f)
    kzwwo__mylpq = kzwwo__mylpq[wdlw__imtb.argsort()]
    wdlw__imtb.sort()
    if is_largest:
        wdlw__imtb = wdlw__imtb[::-1]
        kzwwo__mylpq = kzwwo__mylpq[::-1]
    return np.ascontiguousarray(wdlw__imtb), np.ascontiguousarray(kzwwo__mylpq)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    iskqb__sry = bodo.libs.distributed_api.get_rank()
    xctz__khmh, xovq__tuejb = nlargest(A, I, k, is_largest, cmp_f)
    ktjzd__aew = bodo.libs.distributed_api.gatherv(xctz__khmh)
    odeoa__pfogm = bodo.libs.distributed_api.gatherv(xovq__tuejb)
    if iskqb__sry == MPI_ROOT:
        res, paqq__rbz = nlargest(ktjzd__aew, odeoa__pfogm, k, is_largest,
            cmp_f)
    else:
        res = np.empty(k, A.dtype)
        paqq__rbz = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(paqq__rbz)
    return res, paqq__rbz


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    brdfd__snh, xrda__qzhnv = mat.shape
    psyq__tzd = np.empty((xrda__qzhnv, xrda__qzhnv), dtype=np.float64)
    for whd__kygg in range(xrda__qzhnv):
        for fys__dixqd in range(whd__kygg + 1):
            osk__ngh = 0
            upf__wjnky = xdv__hkgy = hufvy__vsjkz = usr__uin = 0.0
            for i in range(brdfd__snh):
                if np.isfinite(mat[i, whd__kygg]) and np.isfinite(mat[i,
                    fys__dixqd]):
                    lms__rlo = mat[i, whd__kygg]
                    uif__bnk = mat[i, fys__dixqd]
                    osk__ngh += 1
                    hufvy__vsjkz += lms__rlo
                    usr__uin += uif__bnk
            if parallel:
                osk__ngh = bodo.libs.distributed_api.dist_reduce(osk__ngh,
                    sum_op)
                hufvy__vsjkz = bodo.libs.distributed_api.dist_reduce(
                    hufvy__vsjkz, sum_op)
                usr__uin = bodo.libs.distributed_api.dist_reduce(usr__uin,
                    sum_op)
            if osk__ngh < minpv:
                psyq__tzd[whd__kygg, fys__dixqd] = psyq__tzd[fys__dixqd,
                    whd__kygg] = np.nan
            else:
                ylc__aihi = hufvy__vsjkz / osk__ngh
                wbky__vrn = usr__uin / osk__ngh
                hufvy__vsjkz = 0.0
                for i in range(brdfd__snh):
                    if np.isfinite(mat[i, whd__kygg]) and np.isfinite(mat[i,
                        fys__dixqd]):
                        lms__rlo = mat[i, whd__kygg] - ylc__aihi
                        uif__bnk = mat[i, fys__dixqd] - wbky__vrn
                        hufvy__vsjkz += lms__rlo * uif__bnk
                        upf__wjnky += lms__rlo * lms__rlo
                        xdv__hkgy += uif__bnk * uif__bnk
                if parallel:
                    hufvy__vsjkz = bodo.libs.distributed_api.dist_reduce(
                        hufvy__vsjkz, sum_op)
                    upf__wjnky = bodo.libs.distributed_api.dist_reduce(
                        upf__wjnky, sum_op)
                    xdv__hkgy = bodo.libs.distributed_api.dist_reduce(xdv__hkgy
                        , sum_op)
                uurl__murnu = osk__ngh - 1.0 if cov else sqrt(upf__wjnky *
                    xdv__hkgy)
                if uurl__murnu != 0.0:
                    psyq__tzd[whd__kygg, fys__dixqd] = psyq__tzd[fys__dixqd,
                        whd__kygg] = hufvy__vsjkz / uurl__murnu
                else:
                    psyq__tzd[whd__kygg, fys__dixqd] = psyq__tzd[fys__dixqd,
                        whd__kygg] = np.nan
    return psyq__tzd


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    idj__ytuh = n != 1
    jlm__kodko = 'def impl(data, parallel=False):\n'
    jlm__kodko += '  if parallel:\n'
    mnob__ustg = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    jlm__kodko += f'    cpp_table = arr_info_list_to_table([{mnob__ustg}])\n'
    jlm__kodko += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    sakmd__cyl = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    jlm__kodko += f'    data = ({sakmd__cyl},)\n'
    jlm__kodko += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    jlm__kodko += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    jlm__kodko += '    bodo.libs.array.delete_table(cpp_table)\n'
    jlm__kodko += '  n = len(data[0])\n'
    jlm__kodko += '  out = np.empty(n, np.bool_)\n'
    jlm__kodko += '  uniqs = dict()\n'
    if idj__ytuh:
        jlm__kodko += '  for i in range(n):\n'
        bbzo__gyjz = ', '.join(f'data[{i}][i]' for i in range(n))
        rmeya__sszpj = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        jlm__kodko += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({bbzo__gyjz},), ({rmeya__sszpj},))
"""
        jlm__kodko += '    if val in uniqs:\n'
        jlm__kodko += '      out[i] = True\n'
        jlm__kodko += '    else:\n'
        jlm__kodko += '      out[i] = False\n'
        jlm__kodko += '      uniqs[val] = 0\n'
    else:
        jlm__kodko += '  data = data[0]\n'
        jlm__kodko += '  hasna = False\n'
        jlm__kodko += '  for i in range(n):\n'
        jlm__kodko += '    if bodo.libs.array_kernels.isna(data, i):\n'
        jlm__kodko += '      out[i] = hasna\n'
        jlm__kodko += '      hasna = True\n'
        jlm__kodko += '    else:\n'
        jlm__kodko += '      val = data[i]\n'
        jlm__kodko += '      if val in uniqs:\n'
        jlm__kodko += '        out[i] = True\n'
        jlm__kodko += '      else:\n'
        jlm__kodko += '        out[i] = False\n'
        jlm__kodko += '        uniqs[val] = 0\n'
    jlm__kodko += '  if parallel:\n'
    jlm__kodko += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    jlm__kodko += '  return out\n'
    ayti__hlgh = {}
    exec(jlm__kodko, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        ayti__hlgh)
    impl = ayti__hlgh['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    vfpt__opfnp = len(data)
    jlm__kodko = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    jlm__kodko += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        vfpt__opfnp)))
    jlm__kodko += '  table_total = arr_info_list_to_table(info_list_total)\n'
    jlm__kodko += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(vfpt__opfnp))
    for kws__sjpf in range(vfpt__opfnp):
        jlm__kodko += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(kws__sjpf, kws__sjpf, kws__sjpf))
    jlm__kodko += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(vfpt__opfnp))
    jlm__kodko += '  delete_table(out_table)\n'
    jlm__kodko += '  delete_table(table_total)\n'
    jlm__kodko += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(vfpt__opfnp)))
    ayti__hlgh = {}
    exec(jlm__kodko, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, ayti__hlgh)
    impl = ayti__hlgh['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    vfpt__opfnp = len(data)
    jlm__kodko = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    jlm__kodko += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        vfpt__opfnp)))
    jlm__kodko += '  table_total = arr_info_list_to_table(info_list_total)\n'
    jlm__kodko += '  keep_i = 0\n'
    jlm__kodko += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for kws__sjpf in range(vfpt__opfnp):
        jlm__kodko += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(kws__sjpf, kws__sjpf, kws__sjpf))
    jlm__kodko += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(vfpt__opfnp))
    jlm__kodko += '  delete_table(out_table)\n'
    jlm__kodko += '  delete_table(table_total)\n'
    jlm__kodko += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(vfpt__opfnp)))
    ayti__hlgh = {}
    exec(jlm__kodko, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, ayti__hlgh)
    impl = ayti__hlgh['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        ixm__obaj = [array_to_info(data_arr)]
        hiwcf__ajucj = arr_info_list_to_table(ixm__obaj)
        xjn__xoczs = 0
        vhb__tne = drop_duplicates_table(hiwcf__ajucj, parallel, 1,
            xjn__xoczs, False, True)
        kbapx__kbi = info_to_array(info_from_table(vhb__tne, 0), data_arr)
        delete_table(vhb__tne)
        delete_table(hiwcf__ajucj)
        return kbapx__kbi
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    bco__vayli = len(data.types)
    bxid__oyvbr = [('out' + str(i)) for i in range(bco__vayli)]
    wmm__ztd = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    nxhh__ilcp = ['isna(data[{}], i)'.format(i) for i in wmm__ztd]
    ajyub__qcg = 'not ({})'.format(' or '.join(nxhh__ilcp))
    if not is_overload_none(thresh):
        ajyub__qcg = '(({}) <= ({}) - thresh)'.format(' + '.join(nxhh__ilcp
            ), bco__vayli - 1)
    elif how == 'all':
        ajyub__qcg = 'not ({})'.format(' and '.join(nxhh__ilcp))
    jlm__kodko = 'def _dropna_imp(data, how, thresh, subset):\n'
    jlm__kodko += '  old_len = len(data[0])\n'
    jlm__kodko += '  new_len = 0\n'
    jlm__kodko += '  for i in range(old_len):\n'
    jlm__kodko += '    if {}:\n'.format(ajyub__qcg)
    jlm__kodko += '      new_len += 1\n'
    for i, out in enumerate(bxid__oyvbr):
        if isinstance(data[i], bodo.CategoricalArrayType):
            jlm__kodko += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            jlm__kodko += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    jlm__kodko += '  curr_ind = 0\n'
    jlm__kodko += '  for i in range(old_len):\n'
    jlm__kodko += '    if {}:\n'.format(ajyub__qcg)
    for i in range(bco__vayli):
        jlm__kodko += '      if isna(data[{}], i):\n'.format(i)
        jlm__kodko += '        setna({}, curr_ind)\n'.format(bxid__oyvbr[i])
        jlm__kodko += '      else:\n'
        jlm__kodko += '        {}[curr_ind] = data[{}][i]\n'.format(bxid__oyvbr
            [i], i)
    jlm__kodko += '      curr_ind += 1\n'
    jlm__kodko += '  return {}\n'.format(', '.join(bxid__oyvbr))
    ayti__hlgh = {}
    hvol__gpr = {'t{}'.format(i): voq__wzguq for i, voq__wzguq in enumerate
        (data.types)}
    hvol__gpr.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(jlm__kodko, hvol__gpr, ayti__hlgh)
    hukk__gtfs = ayti__hlgh['_dropna_imp']
    return hukk__gtfs


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        mone__xiyvl = arr.dtype
        udonq__gjk = mone__xiyvl.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            hthlg__nty = init_nested_counts(udonq__gjk)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                hthlg__nty = add_nested_counts(hthlg__nty, val[ind])
            kbapx__kbi = bodo.utils.utils.alloc_type(n, mone__xiyvl, hthlg__nty
                )
            for bwpp__hlobi in range(n):
                if bodo.libs.array_kernels.isna(arr, bwpp__hlobi):
                    setna(kbapx__kbi, bwpp__hlobi)
                    continue
                val = arr[bwpp__hlobi]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(kbapx__kbi, bwpp__hlobi)
                    continue
                kbapx__kbi[bwpp__hlobi] = val[ind]
            return kbapx__kbi
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    bwqcz__zqo = _to_readonly(arr_types.types[0])
    return all(isinstance(voq__wzguq, CategoricalArrayType) and 
        _to_readonly(voq__wzguq) == bwqcz__zqo for voq__wzguq in arr_types.
        types)


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
        pxlxp__ljt = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            gncc__jotq = 0
            ddmok__kttfm = []
            for A in arr_list:
                yaaho__yngz = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                ddmok__kttfm.append(bodo.libs.array_item_arr_ext.get_data(A))
                gncc__jotq += yaaho__yngz
            cyyk__opbc = np.empty(gncc__jotq + 1, offset_type)
            dpqoy__yinl = bodo.libs.array_kernels.concat(ddmok__kttfm)
            dup__rnab = np.empty(gncc__jotq + 7 >> 3, np.uint8)
            fzxra__kqjg = 0
            aadbg__ieggi = 0
            for A in arr_list:
                spn__tmx = bodo.libs.array_item_arr_ext.get_offsets(A)
                edpt__rmhzn = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                yaaho__yngz = len(A)
                supw__gkjp = spn__tmx[yaaho__yngz]
                for i in range(yaaho__yngz):
                    cyyk__opbc[i + fzxra__kqjg] = spn__tmx[i] + aadbg__ieggi
                    mtywd__tux = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        edpt__rmhzn, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(dup__rnab, i +
                        fzxra__kqjg, mtywd__tux)
                fzxra__kqjg += yaaho__yngz
                aadbg__ieggi += supw__gkjp
            cyyk__opbc[fzxra__kqjg] = aadbg__ieggi
            kbapx__kbi = bodo.libs.array_item_arr_ext.init_array_item_array(
                gncc__jotq, dpqoy__yinl, cyyk__opbc, dup__rnab)
            return kbapx__kbi
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        ccfvl__igc = arr_list.dtype.names
        jlm__kodko = 'def struct_array_concat_impl(arr_list):\n'
        jlm__kodko += f'    n_all = 0\n'
        for i in range(len(ccfvl__igc)):
            jlm__kodko += f'    concat_list{i} = []\n'
        jlm__kodko += '    for A in arr_list:\n'
        jlm__kodko += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(ccfvl__igc)):
            jlm__kodko += f'        concat_list{i}.append(data_tuple[{i}])\n'
        jlm__kodko += '        n_all += len(A)\n'
        jlm__kodko += '    n_bytes = (n_all + 7) >> 3\n'
        jlm__kodko += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        jlm__kodko += '    curr_bit = 0\n'
        jlm__kodko += '    for A in arr_list:\n'
        jlm__kodko += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        jlm__kodko += '        for j in range(len(A)):\n'
        jlm__kodko += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        jlm__kodko += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        jlm__kodko += '            curr_bit += 1\n'
        jlm__kodko += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        tmbs__xyvpy = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(ccfvl__igc))])
        jlm__kodko += f'        ({tmbs__xyvpy},),\n'
        jlm__kodko += '        new_mask,\n'
        jlm__kodko += f'        {ccfvl__igc},\n'
        jlm__kodko += '    )\n'
        ayti__hlgh = {}
        exec(jlm__kodko, {'bodo': bodo, 'np': np}, ayti__hlgh)
        return ayti__hlgh['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            qrks__okru = 0
            for A in arr_list:
                qrks__okru += len(A)
            ywfyg__mxfqs = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(qrks__okru))
            ytagd__spnzb = 0
            for A in arr_list:
                for i in range(len(A)):
                    ywfyg__mxfqs._data[i + ytagd__spnzb] = A._data[i]
                    mtywd__tux = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ywfyg__mxfqs.
                        _null_bitmap, i + ytagd__spnzb, mtywd__tux)
                ytagd__spnzb += len(A)
            return ywfyg__mxfqs
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            qrks__okru = 0
            for A in arr_list:
                qrks__okru += len(A)
            ywfyg__mxfqs = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(qrks__okru))
            ytagd__spnzb = 0
            for A in arr_list:
                for i in range(len(A)):
                    ywfyg__mxfqs._days_data[i + ytagd__spnzb] = A._days_data[i]
                    ywfyg__mxfqs._seconds_data[i + ytagd__spnzb
                        ] = A._seconds_data[i]
                    ywfyg__mxfqs._microseconds_data[i + ytagd__spnzb
                        ] = A._microseconds_data[i]
                    mtywd__tux = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ywfyg__mxfqs.
                        _null_bitmap, i + ytagd__spnzb, mtywd__tux)
                ytagd__spnzb += len(A)
            return ywfyg__mxfqs
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        gxrqd__qbz = arr_list.dtype.precision
        bzzb__dxad = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            qrks__okru = 0
            for A in arr_list:
                qrks__okru += len(A)
            ywfyg__mxfqs = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                qrks__okru, gxrqd__qbz, bzzb__dxad)
            ytagd__spnzb = 0
            for A in arr_list:
                for i in range(len(A)):
                    ywfyg__mxfqs._data[i + ytagd__spnzb] = A._data[i]
                    mtywd__tux = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ywfyg__mxfqs.
                        _null_bitmap, i + ytagd__spnzb, mtywd__tux)
                ytagd__spnzb += len(A)
            return ywfyg__mxfqs
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        voq__wzguq) for voq__wzguq in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            nsb__eqtc = arr_list.types[0]
        else:
            nsb__eqtc = arr_list.dtype
        nsb__eqtc = to_str_arr_if_dict_array(nsb__eqtc)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            kmqc__pptlb = 0
            eudfq__gbzj = 0
            for A in arr_list:
                arr = A
                kmqc__pptlb += len(arr)
                eudfq__gbzj += bodo.libs.str_arr_ext.num_total_chars(arr)
            kbapx__kbi = bodo.utils.utils.alloc_type(kmqc__pptlb, nsb__eqtc,
                (eudfq__gbzj,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(kbapx__kbi, -1)
            qon__qftsm = 0
            zowo__qde = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(kbapx__kbi,
                    arr, qon__qftsm, zowo__qde)
                qon__qftsm += len(arr)
                zowo__qde += bodo.libs.str_arr_ext.num_total_chars(arr)
            return kbapx__kbi
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(voq__wzguq.dtype, types.Integer) for
        voq__wzguq in arr_list.types) and any(isinstance(voq__wzguq,
        IntegerArrayType) for voq__wzguq in arr_list.types):

        def impl_int_arr_list(arr_list):
            dfybv__brh = convert_to_nullable_tup(arr_list)
            ivewv__wxdyw = []
            nuzf__pztf = 0
            for A in dfybv__brh:
                ivewv__wxdyw.append(A._data)
                nuzf__pztf += len(A)
            dpqoy__yinl = bodo.libs.array_kernels.concat(ivewv__wxdyw)
            bbcai__pgjnf = nuzf__pztf + 7 >> 3
            hutno__attr = np.empty(bbcai__pgjnf, np.uint8)
            nbda__yyj = 0
            for A in dfybv__brh:
                kkn__uchl = A._null_bitmap
                for bwpp__hlobi in range(len(A)):
                    mtywd__tux = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        kkn__uchl, bwpp__hlobi)
                    bodo.libs.int_arr_ext.set_bit_to_arr(hutno__attr,
                        nbda__yyj, mtywd__tux)
                    nbda__yyj += 1
            return bodo.libs.int_arr_ext.init_integer_array(dpqoy__yinl,
                hutno__attr)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(voq__wzguq.dtype == types.bool_ for voq__wzguq in
        arr_list.types) and any(voq__wzguq == boolean_array for voq__wzguq in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            dfybv__brh = convert_to_nullable_tup(arr_list)
            ivewv__wxdyw = []
            nuzf__pztf = 0
            for A in dfybv__brh:
                ivewv__wxdyw.append(A._data)
                nuzf__pztf += len(A)
            dpqoy__yinl = bodo.libs.array_kernels.concat(ivewv__wxdyw)
            bbcai__pgjnf = nuzf__pztf + 7 >> 3
            hutno__attr = np.empty(bbcai__pgjnf, np.uint8)
            nbda__yyj = 0
            for A in dfybv__brh:
                kkn__uchl = A._null_bitmap
                for bwpp__hlobi in range(len(A)):
                    mtywd__tux = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        kkn__uchl, bwpp__hlobi)
                    bodo.libs.int_arr_ext.set_bit_to_arr(hutno__attr,
                        nbda__yyj, mtywd__tux)
                    nbda__yyj += 1
            return bodo.libs.bool_arr_ext.init_bool_array(dpqoy__yinl,
                hutno__attr)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            nsemk__chi = []
            for A in arr_list:
                nsemk__chi.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                nsemk__chi), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        togb__wyxz = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        jlm__kodko = 'def impl(arr_list):\n'
        jlm__kodko += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({togb__wyxz},)), arr_list[0].dtype)
"""
        muxl__trr = {}
        exec(jlm__kodko, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, muxl__trr)
        return muxl__trr['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            nuzf__pztf = 0
            for A in arr_list:
                nuzf__pztf += len(A)
            kbapx__kbi = np.empty(nuzf__pztf, dtype)
            feq__ifar = 0
            for A in arr_list:
                n = len(A)
                kbapx__kbi[feq__ifar:feq__ifar + n] = A
                feq__ifar += n
            return kbapx__kbi
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(voq__wzguq,
        (types.Array, IntegerArrayType)) and isinstance(voq__wzguq.dtype,
        types.Integer) for voq__wzguq in arr_list.types) and any(isinstance
        (voq__wzguq, types.Array) and isinstance(voq__wzguq.dtype, types.
        Float) for voq__wzguq in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            itx__ymst = []
            for A in arr_list:
                itx__ymst.append(A._data)
            tgrps__kwvlc = bodo.libs.array_kernels.concat(itx__ymst)
            psyq__tzd = bodo.libs.map_arr_ext.init_map_arr(tgrps__kwvlc)
            return psyq__tzd
        return impl_map_arr_list
    for thr__mdsne in arr_list:
        if not isinstance(thr__mdsne, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(voq__wzguq.astype(np.float64) for voq__wzguq in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    vfpt__opfnp = len(arr_tup.types)
    jlm__kodko = 'def f(arr_tup):\n'
    jlm__kodko += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        vfpt__opfnp)), ',' if vfpt__opfnp == 1 else '')
    ayti__hlgh = {}
    exec(jlm__kodko, {'np': np}, ayti__hlgh)
    rztf__wnd = ayti__hlgh['f']
    return rztf__wnd


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    vfpt__opfnp = len(arr_tup.types)
    fmzp__zzc = find_common_np_dtype(arr_tup.types)
    udonq__gjk = None
    zqls__gyscv = ''
    if isinstance(fmzp__zzc, types.Integer):
        udonq__gjk = bodo.libs.int_arr_ext.IntDtype(fmzp__zzc)
        zqls__gyscv = '.astype(out_dtype, False)'
    jlm__kodko = 'def f(arr_tup):\n'
    jlm__kodko += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, zqls__gyscv) for i in range(vfpt__opfnp)), ',' if 
        vfpt__opfnp == 1 else '')
    ayti__hlgh = {}
    exec(jlm__kodko, {'bodo': bodo, 'out_dtype': udonq__gjk}, ayti__hlgh)
    zdhhf__zcxqr = ayti__hlgh['f']
    return zdhhf__zcxqr


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, yntgt__ozzsv = build_set_seen_na(A)
        return len(s) + int(not dropna and yntgt__ozzsv)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        gluvk__rltz = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        yzja__ivc = len(gluvk__rltz)
        return bodo.libs.distributed_api.dist_reduce(yzja__ivc, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([rlewj__sxyct for rlewj__sxyct in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        pcu__zjrb = np.finfo(A.dtype(1).dtype).max
    else:
        pcu__zjrb = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        kbapx__kbi = np.empty(n, A.dtype)
        rvy__xmxip = pcu__zjrb
        for i in range(n):
            rvy__xmxip = min(rvy__xmxip, A[i])
            kbapx__kbi[i] = rvy__xmxip
        return kbapx__kbi
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        pcu__zjrb = np.finfo(A.dtype(1).dtype).min
    else:
        pcu__zjrb = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        kbapx__kbi = np.empty(n, A.dtype)
        rvy__xmxip = pcu__zjrb
        for i in range(n):
            rvy__xmxip = max(rvy__xmxip, A[i])
            kbapx__kbi[i] = rvy__xmxip
        return kbapx__kbi
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        grvse__wvh = arr_info_list_to_table([array_to_info(A)])
        dxpl__fpxs = 1
        xjn__xoczs = 0
        vhb__tne = drop_duplicates_table(grvse__wvh, parallel, dxpl__fpxs,
            xjn__xoczs, dropna, True)
        kbapx__kbi = info_to_array(info_from_table(vhb__tne, 0), A)
        delete_table(grvse__wvh)
        delete_table(vhb__tne)
        return kbapx__kbi
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    pxlxp__ljt = bodo.utils.typing.to_nullable_type(arr.dtype)
    bwev__ffosk = index_arr
    cmsgx__ght = bwev__ffosk.dtype

    def impl(arr, index_arr):
        n = len(arr)
        hthlg__nty = init_nested_counts(pxlxp__ljt)
        momh__otb = init_nested_counts(cmsgx__ght)
        for i in range(n):
            jiv__kmeep = index_arr[i]
            if isna(arr, i):
                hthlg__nty = (hthlg__nty[0] + 1,) + hthlg__nty[1:]
                momh__otb = add_nested_counts(momh__otb, jiv__kmeep)
                continue
            kgd__odbyp = arr[i]
            if len(kgd__odbyp) == 0:
                hthlg__nty = (hthlg__nty[0] + 1,) + hthlg__nty[1:]
                momh__otb = add_nested_counts(momh__otb, jiv__kmeep)
                continue
            hthlg__nty = add_nested_counts(hthlg__nty, kgd__odbyp)
            for duu__qvhym in range(len(kgd__odbyp)):
                momh__otb = add_nested_counts(momh__otb, jiv__kmeep)
        kbapx__kbi = bodo.utils.utils.alloc_type(hthlg__nty[0], pxlxp__ljt,
            hthlg__nty[1:])
        wsua__pwzll = bodo.utils.utils.alloc_type(hthlg__nty[0],
            bwev__ffosk, momh__otb)
        aadbg__ieggi = 0
        for i in range(n):
            if isna(arr, i):
                setna(kbapx__kbi, aadbg__ieggi)
                wsua__pwzll[aadbg__ieggi] = index_arr[i]
                aadbg__ieggi += 1
                continue
            kgd__odbyp = arr[i]
            supw__gkjp = len(kgd__odbyp)
            if supw__gkjp == 0:
                setna(kbapx__kbi, aadbg__ieggi)
                wsua__pwzll[aadbg__ieggi] = index_arr[i]
                aadbg__ieggi += 1
                continue
            kbapx__kbi[aadbg__ieggi:aadbg__ieggi + supw__gkjp] = kgd__odbyp
            wsua__pwzll[aadbg__ieggi:aadbg__ieggi + supw__gkjp] = index_arr[i]
            aadbg__ieggi += supw__gkjp
        return kbapx__kbi, wsua__pwzll
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    pxlxp__ljt = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        hthlg__nty = init_nested_counts(pxlxp__ljt)
        for i in range(n):
            if isna(arr, i):
                hthlg__nty = (hthlg__nty[0] + 1,) + hthlg__nty[1:]
                sqcs__tkvt = 1
            else:
                kgd__odbyp = arr[i]
                knz__gvuz = len(kgd__odbyp)
                if knz__gvuz == 0:
                    hthlg__nty = (hthlg__nty[0] + 1,) + hthlg__nty[1:]
                    sqcs__tkvt = 1
                    continue
                else:
                    hthlg__nty = add_nested_counts(hthlg__nty, kgd__odbyp)
                    sqcs__tkvt = knz__gvuz
            if counts[i] != sqcs__tkvt:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        kbapx__kbi = bodo.utils.utils.alloc_type(hthlg__nty[0], pxlxp__ljt,
            hthlg__nty[1:])
        aadbg__ieggi = 0
        for i in range(n):
            if isna(arr, i):
                setna(kbapx__kbi, aadbg__ieggi)
                aadbg__ieggi += 1
                continue
            kgd__odbyp = arr[i]
            supw__gkjp = len(kgd__odbyp)
            if supw__gkjp == 0:
                setna(kbapx__kbi, aadbg__ieggi)
                aadbg__ieggi += 1
                continue
            kbapx__kbi[aadbg__ieggi:aadbg__ieggi + supw__gkjp] = kgd__odbyp
            aadbg__ieggi += supw__gkjp
        return kbapx__kbi
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(ebfuf__yqr) for ebfuf__yqr in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        ttcys__ctza = 'np.empty(n, np.int64)'
        irpz__tqmg = 'out_arr[i] = 1'
        jfiie__ayhjl = 'max(len(arr[i]), 1)'
    else:
        ttcys__ctza = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        irpz__tqmg = 'bodo.libs.array_kernels.setna(out_arr, i)'
        jfiie__ayhjl = 'len(arr[i])'
    jlm__kodko = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {ttcys__ctza}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {irpz__tqmg}
        else:
            out_arr[i] = {jfiie__ayhjl}
    return out_arr
    """
    ayti__hlgh = {}
    exec(jlm__kodko, {'bodo': bodo, 'numba': numba, 'np': np}, ayti__hlgh)
    impl = ayti__hlgh['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    bwev__ffosk = index_arr
    cmsgx__ght = bwev__ffosk.dtype

    def impl(arr, pat, n, index_arr):
        evad__vyr = pat is not None and len(pat) > 1
        if evad__vyr:
            ikixf__xctys = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        npatv__gca = len(arr)
        kmqc__pptlb = 0
        eudfq__gbzj = 0
        momh__otb = init_nested_counts(cmsgx__ght)
        for i in range(npatv__gca):
            jiv__kmeep = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                kmqc__pptlb += 1
                momh__otb = add_nested_counts(momh__otb, jiv__kmeep)
                continue
            if evad__vyr:
                tdqdx__orn = ikixf__xctys.split(arr[i], maxsplit=n)
            else:
                tdqdx__orn = arr[i].split(pat, n)
            kmqc__pptlb += len(tdqdx__orn)
            for s in tdqdx__orn:
                momh__otb = add_nested_counts(momh__otb, jiv__kmeep)
                eudfq__gbzj += bodo.libs.str_arr_ext.get_utf8_size(s)
        kbapx__kbi = bodo.libs.str_arr_ext.pre_alloc_string_array(kmqc__pptlb,
            eudfq__gbzj)
        wsua__pwzll = bodo.utils.utils.alloc_type(kmqc__pptlb, bwev__ffosk,
            momh__otb)
        waa__dzeyu = 0
        for bwpp__hlobi in range(npatv__gca):
            if isna(arr, bwpp__hlobi):
                kbapx__kbi[waa__dzeyu] = ''
                bodo.libs.array_kernels.setna(kbapx__kbi, waa__dzeyu)
                wsua__pwzll[waa__dzeyu] = index_arr[bwpp__hlobi]
                waa__dzeyu += 1
                continue
            if evad__vyr:
                tdqdx__orn = ikixf__xctys.split(arr[bwpp__hlobi], maxsplit=n)
            else:
                tdqdx__orn = arr[bwpp__hlobi].split(pat, n)
            octb__upq = len(tdqdx__orn)
            kbapx__kbi[waa__dzeyu:waa__dzeyu + octb__upq] = tdqdx__orn
            wsua__pwzll[waa__dzeyu:waa__dzeyu + octb__upq] = index_arr[
                bwpp__hlobi]
            waa__dzeyu += octb__upq
        return kbapx__kbi, wsua__pwzll
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
            kbapx__kbi = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                kbapx__kbi[i] = np.nan
            return kbapx__kbi
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            geyu__iuqv = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            mlqoe__rgqz = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(mlqoe__rgqz, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(geyu__iuqv,
                mlqoe__rgqz, True)
        return impl_dict
    rbf__ollz = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        kbapx__kbi = bodo.utils.utils.alloc_type(n, rbf__ollz, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(kbapx__kbi, i)
        return kbapx__kbi
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
    dns__lhnpe = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            kbapx__kbi = bodo.utils.utils.alloc_type(new_len, dns__lhnpe)
            bodo.libs.str_arr_ext.str_copy_ptr(kbapx__kbi.ctypes, 0, A.
                ctypes, old_size)
            return kbapx__kbi
        return impl_char

    def impl(A, old_size, new_len):
        kbapx__kbi = bodo.utils.utils.alloc_type(new_len, dns__lhnpe, (-1,))
        kbapx__kbi[:old_size] = A[:old_size]
        return kbapx__kbi
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    mjw__pnt = math.ceil((stop - start) / step)
    return int(max(mjw__pnt, 0))


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
    if any(isinstance(rlewj__sxyct, types.Complex) for rlewj__sxyct in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            oxw__fwe = (stop - start) / step
            mjw__pnt = math.ceil(oxw__fwe.real)
            zdhb__rdux = math.ceil(oxw__fwe.imag)
            abdxx__mtz = int(max(min(zdhb__rdux, mjw__pnt), 0))
            arr = np.empty(abdxx__mtz, dtype)
            for i in numba.parfors.parfor.internal_prange(abdxx__mtz):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            abdxx__mtz = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(abdxx__mtz, dtype)
            for i in numba.parfors.parfor.internal_prange(abdxx__mtz):
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
        omoje__lrrmb = arr,
        if not inplace:
            omoje__lrrmb = arr.copy(),
        asrbi__xhdsw = bodo.libs.str_arr_ext.to_list_if_immutable_arr(
            omoje__lrrmb)
        sye__vyync = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(asrbi__xhdsw, 0, n, sye__vyync)
        if not ascending:
            bodo.libs.timsort.reverseRange(asrbi__xhdsw, 0, n, sye__vyync)
        bodo.libs.str_arr_ext.cp_str_list_to_array(omoje__lrrmb, asrbi__xhdsw)
        return omoje__lrrmb[0]
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
        psyq__tzd = []
        for i in range(n):
            if A[i]:
                psyq__tzd.append(i + offset)
        return np.array(psyq__tzd, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    dns__lhnpe = element_type(A)
    if dns__lhnpe == types.unicode_type:
        null_value = '""'
    elif dns__lhnpe == types.bool_:
        null_value = 'False'
    elif dns__lhnpe == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif dns__lhnpe == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    waa__dzeyu = 'i'
    mqn__nlk = False
    qhvqd__exmw = get_overload_const_str(method)
    if qhvqd__exmw in ('ffill', 'pad'):
        lyz__yjy = 'n'
        send_right = True
    elif qhvqd__exmw in ('backfill', 'bfill'):
        lyz__yjy = 'n-1, -1, -1'
        send_right = False
        if dns__lhnpe == types.unicode_type:
            waa__dzeyu = '(n - 1) - i'
            mqn__nlk = True
    jlm__kodko = 'def impl(A, method, parallel=False):\n'
    jlm__kodko += '  A = decode_if_dict_array(A)\n'
    jlm__kodko += '  has_last_value = False\n'
    jlm__kodko += f'  last_value = {null_value}\n'
    jlm__kodko += '  if parallel:\n'
    jlm__kodko += '    rank = bodo.libs.distributed_api.get_rank()\n'
    jlm__kodko += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    jlm__kodko += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    jlm__kodko += '  n = len(A)\n'
    jlm__kodko += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    jlm__kodko += f'  for i in range({lyz__yjy}):\n'
    jlm__kodko += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    jlm__kodko += (
        f'      bodo.libs.array_kernels.setna(out_arr, {waa__dzeyu})\n')
    jlm__kodko += '      continue\n'
    jlm__kodko += '    s = A[i]\n'
    jlm__kodko += '    if bodo.libs.array_kernels.isna(A, i):\n'
    jlm__kodko += '      s = last_value\n'
    jlm__kodko += f'    out_arr[{waa__dzeyu}] = s\n'
    jlm__kodko += '    last_value = s\n'
    jlm__kodko += '    has_last_value = True\n'
    if mqn__nlk:
        jlm__kodko += '  return out_arr[::-1]\n'
    else:
        jlm__kodko += '  return out_arr\n'
    fkv__xpbnh = {}
    exec(jlm__kodko, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, fkv__xpbnh)
    impl = fkv__xpbnh['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        pdjpm__nclpl = 0
        ciqac__qqdjv = n_pes - 1
        ynome__peps = np.int32(rank + 1)
        mln__paj = np.int32(rank - 1)
        okccw__vswh = len(in_arr) - 1
        kkhjh__alj = -1
        apm__fzr = -1
    else:
        pdjpm__nclpl = n_pes - 1
        ciqac__qqdjv = 0
        ynome__peps = np.int32(rank - 1)
        mln__paj = np.int32(rank + 1)
        okccw__vswh = 0
        kkhjh__alj = len(in_arr)
        apm__fzr = 1
    dyu__pikqn = np.int32(bodo.hiframes.rolling.comm_border_tag)
    mhngo__gef = np.empty(1, dtype=np.bool_)
    iibv__zifg = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    cabtf__sfb = np.empty(1, dtype=np.bool_)
    ajzi__pen = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    bfrlj__hqomu = False
    dzn__lhaz = null_value
    for i in range(okccw__vswh, kkhjh__alj, apm__fzr):
        if not isna(in_arr, i):
            bfrlj__hqomu = True
            dzn__lhaz = in_arr[i]
            break
    if rank != pdjpm__nclpl:
        xfeky__jbt = bodo.libs.distributed_api.irecv(mhngo__gef, 1,
            mln__paj, dyu__pikqn, True)
        bodo.libs.distributed_api.wait(xfeky__jbt, True)
        hisg__htnvt = bodo.libs.distributed_api.irecv(iibv__zifg, 1,
            mln__paj, dyu__pikqn, True)
        bodo.libs.distributed_api.wait(hisg__htnvt, True)
        sxwrg__omw = mhngo__gef[0]
        oveyv__ymas = iibv__zifg[0]
    else:
        sxwrg__omw = False
        oveyv__ymas = null_value
    if bfrlj__hqomu:
        cabtf__sfb[0] = bfrlj__hqomu
        ajzi__pen[0] = dzn__lhaz
    else:
        cabtf__sfb[0] = sxwrg__omw
        ajzi__pen[0] = oveyv__ymas
    if rank != ciqac__qqdjv:
        xffhl__whly = bodo.libs.distributed_api.isend(cabtf__sfb, 1,
            ynome__peps, dyu__pikqn, True)
        gisd__frhx = bodo.libs.distributed_api.isend(ajzi__pen, 1,
            ynome__peps, dyu__pikqn, True)
    return sxwrg__omw, oveyv__ymas


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    bzh__tbu = {'axis': axis, 'kind': kind, 'order': order}
    trp__llwq = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', bzh__tbu, trp__llwq, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    dns__lhnpe = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            npatv__gca = len(A)
            kbapx__kbi = bodo.utils.utils.alloc_type(npatv__gca * repeats,
                dns__lhnpe, (-1,))
            for i in range(npatv__gca):
                waa__dzeyu = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for bwpp__hlobi in range(repeats):
                        bodo.libs.array_kernels.setna(kbapx__kbi, 
                            waa__dzeyu + bwpp__hlobi)
                else:
                    kbapx__kbi[waa__dzeyu:waa__dzeyu + repeats] = A[i]
            return kbapx__kbi
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        npatv__gca = len(A)
        kbapx__kbi = bodo.utils.utils.alloc_type(repeats.sum(), dns__lhnpe,
            (-1,))
        waa__dzeyu = 0
        for i in range(npatv__gca):
            ugcc__qzoe = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for bwpp__hlobi in range(ugcc__qzoe):
                    bodo.libs.array_kernels.setna(kbapx__kbi, waa__dzeyu +
                        bwpp__hlobi)
            else:
                kbapx__kbi[waa__dzeyu:waa__dzeyu + ugcc__qzoe] = A[i]
            waa__dzeyu += ugcc__qzoe
        return kbapx__kbi
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
        padql__dzmj = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(padql__dzmj, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        coi__bmoc = bodo.libs.array_kernels.concat([A1, A2])
        obyd__qsnj = bodo.libs.array_kernels.unique(coi__bmoc)
        return pd.Series(obyd__qsnj).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    bzh__tbu = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    trp__llwq = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', bzh__tbu, trp__llwq, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        vrnep__ogvts = bodo.libs.array_kernels.unique(A1)
        zsvd__bkn = bodo.libs.array_kernels.unique(A2)
        coi__bmoc = bodo.libs.array_kernels.concat([vrnep__ogvts, zsvd__bkn])
        rccv__tus = pd.Series(coi__bmoc).sort_values().values
        return slice_array_intersect1d(rccv__tus)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    zdtuc__wyjoz = arr[1:] == arr[:-1]
    return arr[:-1][zdtuc__wyjoz]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    dyu__pikqn = np.int32(bodo.hiframes.rolling.comm_border_tag)
    gboim__quinf = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        nvmx__mldr = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), dyu__pikqn, True)
        bodo.libs.distributed_api.wait(nvmx__mldr, True)
    if rank == n_pes - 1:
        return None
    else:
        scue__veeuj = bodo.libs.distributed_api.irecv(gboim__quinf, 1, np.
            int32(rank + 1), dyu__pikqn, True)
        bodo.libs.distributed_api.wait(scue__veeuj, True)
        return gboim__quinf[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    zdtuc__wyjoz = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            zdtuc__wyjoz[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        hfy__ahhj = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == hfy__ahhj:
            zdtuc__wyjoz[n - 1] = True
    return zdtuc__wyjoz


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    bzh__tbu = {'assume_unique': assume_unique}
    trp__llwq = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', bzh__tbu, trp__llwq, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        vrnep__ogvts = bodo.libs.array_kernels.unique(A1)
        zsvd__bkn = bodo.libs.array_kernels.unique(A2)
        zdtuc__wyjoz = calculate_mask_setdiff1d(vrnep__ogvts, zsvd__bkn)
        return pd.Series(vrnep__ogvts[zdtuc__wyjoz]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    zdtuc__wyjoz = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        zdtuc__wyjoz &= A1 != A2[i]
    return zdtuc__wyjoz


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    bzh__tbu = {'retstep': retstep, 'axis': axis}
    trp__llwq = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', bzh__tbu, trp__llwq, 'numpy')
    tsdio__jthg = False
    if is_overload_none(dtype):
        dns__lhnpe = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            tsdio__jthg = True
        dns__lhnpe = numba.np.numpy_support.as_dtype(dtype).type
    if tsdio__jthg:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            koel__goq = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            kbapx__kbi = np.empty(num, dns__lhnpe)
            for i in numba.parfors.parfor.internal_prange(num):
                kbapx__kbi[i] = dns__lhnpe(np.floor(start + i * koel__goq))
            return kbapx__kbi
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            koel__goq = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            kbapx__kbi = np.empty(num, dns__lhnpe)
            for i in numba.parfors.parfor.internal_prange(num):
                kbapx__kbi[i] = dns__lhnpe(start + i * koel__goq)
            return kbapx__kbi
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
        vfpt__opfnp = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                vfpt__opfnp += A[i] == val
        return vfpt__opfnp > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    bzh__tbu = {'axis': axis, 'out': out, 'keepdims': keepdims}
    trp__llwq = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', bzh__tbu, trp__llwq, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        vfpt__opfnp = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                vfpt__opfnp += int(bool(A[i]))
        return vfpt__opfnp > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    bzh__tbu = {'axis': axis, 'out': out, 'keepdims': keepdims}
    trp__llwq = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', bzh__tbu, trp__llwq, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        vfpt__opfnp = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                vfpt__opfnp += int(bool(A[i]))
        return vfpt__opfnp == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    bzh__tbu = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    trp__llwq = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', bzh__tbu, trp__llwq, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        btfw__akomf = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            kbapx__kbi = np.empty(n, btfw__akomf)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(kbapx__kbi, i)
                    continue
                kbapx__kbi[i] = np_cbrt_scalar(A[i], btfw__akomf)
            return kbapx__kbi
        return impl_arr
    btfw__akomf = np.promote_types(numba.np.numpy_support.as_dtype(A),
        numba.np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, btfw__akomf)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    betv__neg = x < 0
    if betv__neg:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if betv__neg:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    vqya__juzr = isinstance(tup, (types.BaseTuple, types.List))
    bjkt__zxp = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for thr__mdsne in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                thr__mdsne, 'numpy.hstack()')
            vqya__juzr = vqya__juzr and bodo.utils.utils.is_array_typ(
                thr__mdsne, False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        vqya__juzr = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif bjkt__zxp:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        jyn__uvnv = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for thr__mdsne in jyn__uvnv.types:
            bjkt__zxp = bjkt__zxp and bodo.utils.utils.is_array_typ(thr__mdsne,
                False)
    if not (vqya__juzr or bjkt__zxp):
        return
    if bjkt__zxp:

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
    bzh__tbu = {'check_valid': check_valid, 'tol': tol}
    trp__llwq = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', bzh__tbu,
        trp__llwq, 'numpy')
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
        brdfd__snh = mean.shape[0]
        zttih__yzyos = size, brdfd__snh
        ldew__kjm = np.random.standard_normal(zttih__yzyos)
        cov = cov.astype(np.float64)
        vrily__nwxlr, s, nzwek__adqaq = np.linalg.svd(cov)
        res = np.dot(ldew__kjm, np.sqrt(s).reshape(brdfd__snh, 1) *
            nzwek__adqaq)
        num__owtw = res + mean
        return num__owtw
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
            mqtxc__ghboi = bodo.hiframes.series_kernels._get_type_max_value(arr
                )
            nvds__ypk = typing.builtins.IndexValue(-1, mqtxc__ghboi)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                zkwy__izwl = typing.builtins.IndexValue(i, arr[i])
                nvds__ypk = min(nvds__ypk, zkwy__izwl)
            return nvds__ypk.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        tdtt__rra = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            jbhb__hbbh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            mqtxc__ghboi = tdtt__rra(len(arr.dtype.categories) + 1)
            nvds__ypk = typing.builtins.IndexValue(-1, mqtxc__ghboi)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                zkwy__izwl = typing.builtins.IndexValue(i, jbhb__hbbh[i])
                nvds__ypk = min(nvds__ypk, zkwy__izwl)
            return nvds__ypk.index
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
            mqtxc__ghboi = bodo.hiframes.series_kernels._get_type_min_value(arr
                )
            nvds__ypk = typing.builtins.IndexValue(-1, mqtxc__ghboi)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                zkwy__izwl = typing.builtins.IndexValue(i, arr[i])
                nvds__ypk = max(nvds__ypk, zkwy__izwl)
            return nvds__ypk.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        tdtt__rra = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            jbhb__hbbh = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            mqtxc__ghboi = tdtt__rra(-1)
            nvds__ypk = typing.builtins.IndexValue(-1, mqtxc__ghboi)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                zkwy__izwl = typing.builtins.IndexValue(i, jbhb__hbbh[i])
                nvds__ypk = max(nvds__ypk, zkwy__izwl)
            return nvds__ypk.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
