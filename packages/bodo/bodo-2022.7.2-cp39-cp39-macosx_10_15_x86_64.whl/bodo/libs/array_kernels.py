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
        bbwq__dog = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = bbwq__dog
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        bbwq__dog = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = bbwq__dog
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
            gjqz__nmp = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            gjqz__nmp[ind + 1] = gjqz__nmp[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            gjqz__nmp = bodo.libs.array_item_arr_ext.get_offsets(arr)
            gjqz__nmp[ind + 1] = gjqz__nmp[ind]
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
    xri__oybgy = arr_tup.count
    eaaft__spe = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(xri__oybgy):
        eaaft__spe += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    eaaft__spe += '  return\n'
    frfwx__uvc = {}
    exec(eaaft__spe, {'setna': setna}, frfwx__uvc)
    impl = frfwx__uvc['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        eej__ihork = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(eej__ihork.start, eej__ihork.stop, eej__ihork.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        aaw__qjiiw = 'n'
        gqq__ktds = 'n_pes'
        vpec__oabeh = 'min_op'
    else:
        aaw__qjiiw = 'n-1, -1, -1'
        gqq__ktds = '-1'
        vpec__oabeh = 'max_op'
    eaaft__spe = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {gqq__ktds}
    for i in range({aaw__qjiiw}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {vpec__oabeh}))
        if possible_valid_rank != {gqq__ktds}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    frfwx__uvc = {}
    exec(eaaft__spe, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, frfwx__uvc)
    impl = frfwx__uvc['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    knujw__uow = array_to_info(arr)
    _median_series_computation(res, knujw__uow, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(knujw__uow)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    knujw__uow = array_to_info(arr)
    _autocorr_series_computation(res, knujw__uow, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(knujw__uow)


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
    knujw__uow = array_to_info(arr)
    _compute_series_monotonicity(res, knujw__uow, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(knujw__uow)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    vaqnp__kddzo = res[0] > 0.5
    return vaqnp__kddzo


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        fmc__onl = '-'
        ivv__tzdnl = 'index_arr[0] > threshhold_date'
        aaw__qjiiw = '1, n+1'
        wmpx__kbu = 'index_arr[-i] <= threshhold_date'
        ozpg__pgd = 'i - 1'
    else:
        fmc__onl = '+'
        ivv__tzdnl = 'index_arr[-1] < threshhold_date'
        aaw__qjiiw = 'n'
        wmpx__kbu = 'index_arr[i] >= threshhold_date'
        ozpg__pgd = 'i'
    eaaft__spe = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        eaaft__spe += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        eaaft__spe += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            eaaft__spe += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            eaaft__spe += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            eaaft__spe += '    else:\n'
            eaaft__spe += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            eaaft__spe += (
                f'    threshhold_date = initial_date {fmc__onl} date_offset\n')
    else:
        eaaft__spe += f'  threshhold_date = initial_date {fmc__onl} offset\n'
    eaaft__spe += '  local_valid = 0\n'
    eaaft__spe += f'  n = len(index_arr)\n'
    eaaft__spe += f'  if n:\n'
    eaaft__spe += f'    if {ivv__tzdnl}:\n'
    eaaft__spe += '      loc_valid = n\n'
    eaaft__spe += '    else:\n'
    eaaft__spe += f'      for i in range({aaw__qjiiw}):\n'
    eaaft__spe += f'        if {wmpx__kbu}:\n'
    eaaft__spe += f'          loc_valid = {ozpg__pgd}\n'
    eaaft__spe += '          break\n'
    eaaft__spe += '  if is_parallel:\n'
    eaaft__spe += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    eaaft__spe += '    return total_valid\n'
    eaaft__spe += '  else:\n'
    eaaft__spe += '    return loc_valid\n'
    frfwx__uvc = {}
    exec(eaaft__spe, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, frfwx__uvc)
    return frfwx__uvc['impl']


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
    pnq__klcyq = numba_to_c_type(sig.args[0].dtype)
    iiuj__cecr = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), pnq__klcyq))
    htjv__aocj = args[0]
    xnwu__tpbfp = sig.args[0]
    if isinstance(xnwu__tpbfp, (IntegerArrayType, BooleanArrayType)):
        htjv__aocj = cgutils.create_struct_proxy(xnwu__tpbfp)(context,
            builder, htjv__aocj).data
        xnwu__tpbfp = types.Array(xnwu__tpbfp.dtype, 1, 'C')
    assert xnwu__tpbfp.ndim == 1
    arr = make_array(xnwu__tpbfp)(context, builder, htjv__aocj)
    qfm__qqj = builder.extract_value(arr.shape, 0)
    shd__hkek = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        qfm__qqj, args[1], builder.load(iiuj__cecr)]
    dafq__mpepg = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    obi__dizui = lir.FunctionType(lir.DoubleType(), dafq__mpepg)
    gwr__fwejn = cgutils.get_or_insert_function(builder.module, obi__dizui,
        name='quantile_sequential')
    dwnzy__wuqlx = builder.call(gwr__fwejn, shd__hkek)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return dwnzy__wuqlx


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    pnq__klcyq = numba_to_c_type(sig.args[0].dtype)
    iiuj__cecr = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), pnq__klcyq))
    htjv__aocj = args[0]
    xnwu__tpbfp = sig.args[0]
    if isinstance(xnwu__tpbfp, (IntegerArrayType, BooleanArrayType)):
        htjv__aocj = cgutils.create_struct_proxy(xnwu__tpbfp)(context,
            builder, htjv__aocj).data
        xnwu__tpbfp = types.Array(xnwu__tpbfp.dtype, 1, 'C')
    assert xnwu__tpbfp.ndim == 1
    arr = make_array(xnwu__tpbfp)(context, builder, htjv__aocj)
    qfm__qqj = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        okn__awgg = args[2]
    else:
        okn__awgg = qfm__qqj
    shd__hkek = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        qfm__qqj, okn__awgg, args[1], builder.load(iiuj__cecr)]
    dafq__mpepg = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        IntType(64), lir.DoubleType(), lir.IntType(32)]
    obi__dizui = lir.FunctionType(lir.DoubleType(), dafq__mpepg)
    gwr__fwejn = cgutils.get_or_insert_function(builder.module, obi__dizui,
        name='quantile_parallel')
    dwnzy__wuqlx = builder.call(gwr__fwejn, shd__hkek)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return dwnzy__wuqlx


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        kwfl__gai = np.nonzero(pd.isna(arr))[0]
        uha__bbmkm = arr[1:] != arr[:-1]
        uha__bbmkm[pd.isna(uha__bbmkm)] = False
        fjaa__zxgob = uha__bbmkm.astype(np.bool_)
        lyrg__peuy = np.concatenate((np.array([True]), fjaa__zxgob))
        if kwfl__gai.size:
            nvj__zqgl, nft__frx = kwfl__gai[0], kwfl__gai[1:]
            lyrg__peuy[nvj__zqgl] = True
            if nft__frx.size:
                lyrg__peuy[nft__frx] = False
                if nft__frx[-1] + 1 < lyrg__peuy.size:
                    lyrg__peuy[nft__frx[-1] + 1] = True
            elif nvj__zqgl + 1 < lyrg__peuy.size:
                lyrg__peuy[nvj__zqgl + 1] = True
        return lyrg__peuy
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
    eaaft__spe = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    eaaft__spe += '  na_idxs = pd.isna(arr)\n'
    eaaft__spe += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    eaaft__spe += '  nas = sum(na_idxs)\n'
    if not ascending:
        eaaft__spe += '  if nas and nas < (sorter.size - 1):\n'
        eaaft__spe += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        eaaft__spe += '  else:\n'
        eaaft__spe += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        eaaft__spe += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    eaaft__spe += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    eaaft__spe += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        eaaft__spe += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        eaaft__spe += '    inv,\n'
        eaaft__spe += '    new_dtype=np.float64,\n'
        eaaft__spe += '    copy=True,\n'
        eaaft__spe += '    nan_to_str=False,\n'
        eaaft__spe += '    from_series=True,\n'
        eaaft__spe += '    ) + 1\n'
    else:
        eaaft__spe += '  arr = arr[sorter]\n'
        eaaft__spe += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        eaaft__spe += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            eaaft__spe += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            eaaft__spe += '    dense,\n'
            eaaft__spe += '    new_dtype=np.float64,\n'
            eaaft__spe += '    copy=True,\n'
            eaaft__spe += '    nan_to_str=False,\n'
            eaaft__spe += '    from_series=True,\n'
            eaaft__spe += '  )\n'
        else:
            eaaft__spe += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            eaaft__spe += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                eaaft__spe += '  ret = count_float[dense]\n'
            elif method == 'min':
                eaaft__spe += '  ret = count_float[dense - 1] + 1\n'
            else:
                eaaft__spe += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                eaaft__spe += '  ret[na_idxs] = -1\n'
            eaaft__spe += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            eaaft__spe += '  div_val = arr.size - nas\n'
        else:
            eaaft__spe += '  div_val = arr.size\n'
        eaaft__spe += '  for i in range(len(ret)):\n'
        eaaft__spe += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        eaaft__spe += '  ret[na_idxs] = np.nan\n'
    eaaft__spe += '  return ret\n'
    frfwx__uvc = {}
    exec(eaaft__spe, {'np': np, 'pd': pd, 'bodo': bodo}, frfwx__uvc)
    return frfwx__uvc['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    bqzk__bex = start
    fsg__wlab = 2 * start + 1
    cdtky__ttitb = 2 * start + 2
    if fsg__wlab < n and not cmp_f(arr[fsg__wlab], arr[bqzk__bex]):
        bqzk__bex = fsg__wlab
    if cdtky__ttitb < n and not cmp_f(arr[cdtky__ttitb], arr[bqzk__bex]):
        bqzk__bex = cdtky__ttitb
    if bqzk__bex != start:
        arr[start], arr[bqzk__bex] = arr[bqzk__bex], arr[start]
        ind_arr[start], ind_arr[bqzk__bex] = ind_arr[bqzk__bex], ind_arr[start]
        min_heapify(arr, ind_arr, n, bqzk__bex, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        pdk__tbqm = np.empty(k, A.dtype)
        mjnqc__fahn = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                pdk__tbqm[ind] = A[i]
                mjnqc__fahn[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            pdk__tbqm = pdk__tbqm[:ind]
            mjnqc__fahn = mjnqc__fahn[:ind]
        return pdk__tbqm, mjnqc__fahn, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        loplh__jgn = np.sort(A)
        bhc__grun = index_arr[np.argsort(A)]
        voi__dzy = pd.Series(loplh__jgn).notna().values
        loplh__jgn = loplh__jgn[voi__dzy]
        bhc__grun = bhc__grun[voi__dzy]
        if is_largest:
            loplh__jgn = loplh__jgn[::-1]
            bhc__grun = bhc__grun[::-1]
        return np.ascontiguousarray(loplh__jgn), np.ascontiguousarray(bhc__grun
            )
    pdk__tbqm, mjnqc__fahn, start = select_k_nonan(A, index_arr, m, k)
    mjnqc__fahn = mjnqc__fahn[pdk__tbqm.argsort()]
    pdk__tbqm.sort()
    if not is_largest:
        pdk__tbqm = np.ascontiguousarray(pdk__tbqm[::-1])
        mjnqc__fahn = np.ascontiguousarray(mjnqc__fahn[::-1])
    for i in range(start, m):
        if cmp_f(A[i], pdk__tbqm[0]):
            pdk__tbqm[0] = A[i]
            mjnqc__fahn[0] = index_arr[i]
            min_heapify(pdk__tbqm, mjnqc__fahn, k, 0, cmp_f)
    mjnqc__fahn = mjnqc__fahn[pdk__tbqm.argsort()]
    pdk__tbqm.sort()
    if is_largest:
        pdk__tbqm = pdk__tbqm[::-1]
        mjnqc__fahn = mjnqc__fahn[::-1]
    return np.ascontiguousarray(pdk__tbqm), np.ascontiguousarray(mjnqc__fahn)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    lpwu__yqzd = bodo.libs.distributed_api.get_rank()
    dkw__wfyo, wza__vje = nlargest(A, I, k, is_largest, cmp_f)
    mkpdy__gqpqa = bodo.libs.distributed_api.gatherv(dkw__wfyo)
    fivta__fyv = bodo.libs.distributed_api.gatherv(wza__vje)
    if lpwu__yqzd == MPI_ROOT:
        res, yxor__imbg = nlargest(mkpdy__gqpqa, fivta__fyv, k, is_largest,
            cmp_f)
    else:
        res = np.empty(k, A.dtype)
        yxor__imbg = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(yxor__imbg)
    return res, yxor__imbg


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    gwh__lrsrl, eltwf__fdyvy = mat.shape
    ege__onqi = np.empty((eltwf__fdyvy, eltwf__fdyvy), dtype=np.float64)
    for yzb__ycxiq in range(eltwf__fdyvy):
        for cwtba__zsg in range(yzb__ycxiq + 1):
            smmn__vkeqh = 0
            iamzp__vme = fbfh__evc = bhwof__oge = vlc__kan = 0.0
            for i in range(gwh__lrsrl):
                if np.isfinite(mat[i, yzb__ycxiq]) and np.isfinite(mat[i,
                    cwtba__zsg]):
                    gyqw__qxq = mat[i, yzb__ycxiq]
                    zgh__sphsa = mat[i, cwtba__zsg]
                    smmn__vkeqh += 1
                    bhwof__oge += gyqw__qxq
                    vlc__kan += zgh__sphsa
            if parallel:
                smmn__vkeqh = bodo.libs.distributed_api.dist_reduce(smmn__vkeqh
                    , sum_op)
                bhwof__oge = bodo.libs.distributed_api.dist_reduce(bhwof__oge,
                    sum_op)
                vlc__kan = bodo.libs.distributed_api.dist_reduce(vlc__kan,
                    sum_op)
            if smmn__vkeqh < minpv:
                ege__onqi[yzb__ycxiq, cwtba__zsg] = ege__onqi[cwtba__zsg,
                    yzb__ycxiq] = np.nan
            else:
                fcg__zlg = bhwof__oge / smmn__vkeqh
                jar__fab = vlc__kan / smmn__vkeqh
                bhwof__oge = 0.0
                for i in range(gwh__lrsrl):
                    if np.isfinite(mat[i, yzb__ycxiq]) and np.isfinite(mat[
                        i, cwtba__zsg]):
                        gyqw__qxq = mat[i, yzb__ycxiq] - fcg__zlg
                        zgh__sphsa = mat[i, cwtba__zsg] - jar__fab
                        bhwof__oge += gyqw__qxq * zgh__sphsa
                        iamzp__vme += gyqw__qxq * gyqw__qxq
                        fbfh__evc += zgh__sphsa * zgh__sphsa
                if parallel:
                    bhwof__oge = bodo.libs.distributed_api.dist_reduce(
                        bhwof__oge, sum_op)
                    iamzp__vme = bodo.libs.distributed_api.dist_reduce(
                        iamzp__vme, sum_op)
                    fbfh__evc = bodo.libs.distributed_api.dist_reduce(fbfh__evc
                        , sum_op)
                rbqkm__ohoim = smmn__vkeqh - 1.0 if cov else sqrt(
                    iamzp__vme * fbfh__evc)
                if rbqkm__ohoim != 0.0:
                    ege__onqi[yzb__ycxiq, cwtba__zsg] = ege__onqi[
                        cwtba__zsg, yzb__ycxiq] = bhwof__oge / rbqkm__ohoim
                else:
                    ege__onqi[yzb__ycxiq, cwtba__zsg] = ege__onqi[
                        cwtba__zsg, yzb__ycxiq] = np.nan
    return ege__onqi


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    gwd__jvz = n != 1
    eaaft__spe = 'def impl(data, parallel=False):\n'
    eaaft__spe += '  if parallel:\n'
    xkx__dwanj = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    eaaft__spe += f'    cpp_table = arr_info_list_to_table([{xkx__dwanj}])\n'
    eaaft__spe += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    wvej__zwh = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    eaaft__spe += f'    data = ({wvej__zwh},)\n'
    eaaft__spe += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    eaaft__spe += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    eaaft__spe += '    bodo.libs.array.delete_table(cpp_table)\n'
    eaaft__spe += '  n = len(data[0])\n'
    eaaft__spe += '  out = np.empty(n, np.bool_)\n'
    eaaft__spe += '  uniqs = dict()\n'
    if gwd__jvz:
        eaaft__spe += '  for i in range(n):\n'
        liww__zgrfh = ', '.join(f'data[{i}][i]' for i in range(n))
        xgocf__dpk = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        eaaft__spe += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({liww__zgrfh},), ({xgocf__dpk},))
"""
        eaaft__spe += '    if val in uniqs:\n'
        eaaft__spe += '      out[i] = True\n'
        eaaft__spe += '    else:\n'
        eaaft__spe += '      out[i] = False\n'
        eaaft__spe += '      uniqs[val] = 0\n'
    else:
        eaaft__spe += '  data = data[0]\n'
        eaaft__spe += '  hasna = False\n'
        eaaft__spe += '  for i in range(n):\n'
        eaaft__spe += '    if bodo.libs.array_kernels.isna(data, i):\n'
        eaaft__spe += '      out[i] = hasna\n'
        eaaft__spe += '      hasna = True\n'
        eaaft__spe += '    else:\n'
        eaaft__spe += '      val = data[i]\n'
        eaaft__spe += '      if val in uniqs:\n'
        eaaft__spe += '        out[i] = True\n'
        eaaft__spe += '      else:\n'
        eaaft__spe += '        out[i] = False\n'
        eaaft__spe += '        uniqs[val] = 0\n'
    eaaft__spe += '  if parallel:\n'
    eaaft__spe += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    eaaft__spe += '  return out\n'
    frfwx__uvc = {}
    exec(eaaft__spe, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        frfwx__uvc)
    impl = frfwx__uvc['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    xri__oybgy = len(data)
    eaaft__spe = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    eaaft__spe += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        xri__oybgy)))
    eaaft__spe += '  table_total = arr_info_list_to_table(info_list_total)\n'
    eaaft__spe += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(xri__oybgy))
    for qsn__pwb in range(xri__oybgy):
        eaaft__spe += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(qsn__pwb, qsn__pwb, qsn__pwb))
    eaaft__spe += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(xri__oybgy))
    eaaft__spe += '  delete_table(out_table)\n'
    eaaft__spe += '  delete_table(table_total)\n'
    eaaft__spe += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(xri__oybgy)))
    frfwx__uvc = {}
    exec(eaaft__spe, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, frfwx__uvc)
    impl = frfwx__uvc['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    xri__oybgy = len(data)
    eaaft__spe = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    eaaft__spe += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        xri__oybgy)))
    eaaft__spe += '  table_total = arr_info_list_to_table(info_list_total)\n'
    eaaft__spe += '  keep_i = 0\n'
    eaaft__spe += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for qsn__pwb in range(xri__oybgy):
        eaaft__spe += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(qsn__pwb, qsn__pwb, qsn__pwb))
    eaaft__spe += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(xri__oybgy))
    eaaft__spe += '  delete_table(out_table)\n'
    eaaft__spe += '  delete_table(table_total)\n'
    eaaft__spe += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(xri__oybgy)))
    frfwx__uvc = {}
    exec(eaaft__spe, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, frfwx__uvc)
    impl = frfwx__uvc['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        ypax__esdq = [array_to_info(data_arr)]
        ctrx__lesr = arr_info_list_to_table(ypax__esdq)
        lhlvy__aqt = 0
        wvv__bwge = drop_duplicates_table(ctrx__lesr, parallel, 1,
            lhlvy__aqt, False, True)
        qgjvo__sgpto = info_to_array(info_from_table(wvv__bwge, 0), data_arr)
        delete_table(wvv__bwge)
        delete_table(ctrx__lesr)
        return qgjvo__sgpto
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    cvhe__uto = len(data.types)
    drxzc__nmq = [('out' + str(i)) for i in range(cvhe__uto)]
    zjs__fyiaq = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    yjxz__jypb = ['isna(data[{}], i)'.format(i) for i in zjs__fyiaq]
    cbm__mifh = 'not ({})'.format(' or '.join(yjxz__jypb))
    if not is_overload_none(thresh):
        cbm__mifh = '(({}) <= ({}) - thresh)'.format(' + '.join(yjxz__jypb),
            cvhe__uto - 1)
    elif how == 'all':
        cbm__mifh = 'not ({})'.format(' and '.join(yjxz__jypb))
    eaaft__spe = 'def _dropna_imp(data, how, thresh, subset):\n'
    eaaft__spe += '  old_len = len(data[0])\n'
    eaaft__spe += '  new_len = 0\n'
    eaaft__spe += '  for i in range(old_len):\n'
    eaaft__spe += '    if {}:\n'.format(cbm__mifh)
    eaaft__spe += '      new_len += 1\n'
    for i, out in enumerate(drxzc__nmq):
        if isinstance(data[i], bodo.CategoricalArrayType):
            eaaft__spe += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            eaaft__spe += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    eaaft__spe += '  curr_ind = 0\n'
    eaaft__spe += '  for i in range(old_len):\n'
    eaaft__spe += '    if {}:\n'.format(cbm__mifh)
    for i in range(cvhe__uto):
        eaaft__spe += '      if isna(data[{}], i):\n'.format(i)
        eaaft__spe += '        setna({}, curr_ind)\n'.format(drxzc__nmq[i])
        eaaft__spe += '      else:\n'
        eaaft__spe += '        {}[curr_ind] = data[{}][i]\n'.format(drxzc__nmq
            [i], i)
    eaaft__spe += '      curr_ind += 1\n'
    eaaft__spe += '  return {}\n'.format(', '.join(drxzc__nmq))
    frfwx__uvc = {}
    wbyx__ktcea = {'t{}'.format(i): xzd__qbf for i, xzd__qbf in enumerate(
        data.types)}
    wbyx__ktcea.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(eaaft__spe, wbyx__ktcea, frfwx__uvc)
    ffqw__pyq = frfwx__uvc['_dropna_imp']
    return ffqw__pyq


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        xnwu__tpbfp = arr.dtype
        jjph__tsv = xnwu__tpbfp.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            croa__dkvtm = init_nested_counts(jjph__tsv)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                croa__dkvtm = add_nested_counts(croa__dkvtm, val[ind])
            qgjvo__sgpto = bodo.utils.utils.alloc_type(n, xnwu__tpbfp,
                croa__dkvtm)
            for bxxgh__qnhyz in range(n):
                if bodo.libs.array_kernels.isna(arr, bxxgh__qnhyz):
                    setna(qgjvo__sgpto, bxxgh__qnhyz)
                    continue
                val = arr[bxxgh__qnhyz]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(qgjvo__sgpto, bxxgh__qnhyz)
                    continue
                qgjvo__sgpto[bxxgh__qnhyz] = val[ind]
            return qgjvo__sgpto
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    wahr__iiiy = _to_readonly(arr_types.types[0])
    return all(isinstance(xzd__qbf, CategoricalArrayType) and _to_readonly(
        xzd__qbf) == wahr__iiiy for xzd__qbf in arr_types.types)


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
        wvru__eafl = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            kaw__flitd = 0
            yaa__enj = []
            for A in arr_list:
                czqxl__kjdkw = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                yaa__enj.append(bodo.libs.array_item_arr_ext.get_data(A))
                kaw__flitd += czqxl__kjdkw
            wcsg__xkjod = np.empty(kaw__flitd + 1, offset_type)
            bfhb__kony = bodo.libs.array_kernels.concat(yaa__enj)
            acp__zszg = np.empty(kaw__flitd + 7 >> 3, np.uint8)
            nybr__gfxi = 0
            ymrc__xdbs = 0
            for A in arr_list:
                vewhq__vtubc = bodo.libs.array_item_arr_ext.get_offsets(A)
                ccdo__lvpys = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                czqxl__kjdkw = len(A)
                aarjb__zdwfm = vewhq__vtubc[czqxl__kjdkw]
                for i in range(czqxl__kjdkw):
                    wcsg__xkjod[i + nybr__gfxi] = vewhq__vtubc[i] + ymrc__xdbs
                    mzr__laas = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ccdo__lvpys, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(acp__zszg, i +
                        nybr__gfxi, mzr__laas)
                nybr__gfxi += czqxl__kjdkw
                ymrc__xdbs += aarjb__zdwfm
            wcsg__xkjod[nybr__gfxi] = ymrc__xdbs
            qgjvo__sgpto = bodo.libs.array_item_arr_ext.init_array_item_array(
                kaw__flitd, bfhb__kony, wcsg__xkjod, acp__zszg)
            return qgjvo__sgpto
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        oci__rbg = arr_list.dtype.names
        eaaft__spe = 'def struct_array_concat_impl(arr_list):\n'
        eaaft__spe += f'    n_all = 0\n'
        for i in range(len(oci__rbg)):
            eaaft__spe += f'    concat_list{i} = []\n'
        eaaft__spe += '    for A in arr_list:\n'
        eaaft__spe += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(oci__rbg)):
            eaaft__spe += f'        concat_list{i}.append(data_tuple[{i}])\n'
        eaaft__spe += '        n_all += len(A)\n'
        eaaft__spe += '    n_bytes = (n_all + 7) >> 3\n'
        eaaft__spe += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        eaaft__spe += '    curr_bit = 0\n'
        eaaft__spe += '    for A in arr_list:\n'
        eaaft__spe += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        eaaft__spe += '        for j in range(len(A)):\n'
        eaaft__spe += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        eaaft__spe += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        eaaft__spe += '            curr_bit += 1\n'
        eaaft__spe += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        vkbzd__pnlf = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(oci__rbg))])
        eaaft__spe += f'        ({vkbzd__pnlf},),\n'
        eaaft__spe += '        new_mask,\n'
        eaaft__spe += f'        {oci__rbg},\n'
        eaaft__spe += '    )\n'
        frfwx__uvc = {}
        exec(eaaft__spe, {'bodo': bodo, 'np': np}, frfwx__uvc)
        return frfwx__uvc['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            qavyu__damr = 0
            for A in arr_list:
                qavyu__damr += len(A)
            okis__vihq = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(qavyu__damr))
            pfkyo__dyts = 0
            for A in arr_list:
                for i in range(len(A)):
                    okis__vihq._data[i + pfkyo__dyts] = A._data[i]
                    mzr__laas = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(okis__vihq.
                        _null_bitmap, i + pfkyo__dyts, mzr__laas)
                pfkyo__dyts += len(A)
            return okis__vihq
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            qavyu__damr = 0
            for A in arr_list:
                qavyu__damr += len(A)
            okis__vihq = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(qavyu__damr))
            pfkyo__dyts = 0
            for A in arr_list:
                for i in range(len(A)):
                    okis__vihq._days_data[i + pfkyo__dyts] = A._days_data[i]
                    okis__vihq._seconds_data[i + pfkyo__dyts
                        ] = A._seconds_data[i]
                    okis__vihq._microseconds_data[i + pfkyo__dyts
                        ] = A._microseconds_data[i]
                    mzr__laas = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(okis__vihq.
                        _null_bitmap, i + pfkyo__dyts, mzr__laas)
                pfkyo__dyts += len(A)
            return okis__vihq
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        jpb__olzud = arr_list.dtype.precision
        qgc__jcxa = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            qavyu__damr = 0
            for A in arr_list:
                qavyu__damr += len(A)
            okis__vihq = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                qavyu__damr, jpb__olzud, qgc__jcxa)
            pfkyo__dyts = 0
            for A in arr_list:
                for i in range(len(A)):
                    okis__vihq._data[i + pfkyo__dyts] = A._data[i]
                    mzr__laas = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(okis__vihq.
                        _null_bitmap, i + pfkyo__dyts, mzr__laas)
                pfkyo__dyts += len(A)
            return okis__vihq
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        xzd__qbf) for xzd__qbf in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            chnc__okfb = arr_list.types[0]
        else:
            chnc__okfb = arr_list.dtype
        chnc__okfb = to_str_arr_if_dict_array(chnc__okfb)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            jeu__udycw = 0
            zyd__iea = 0
            for A in arr_list:
                arr = A
                jeu__udycw += len(arr)
                zyd__iea += bodo.libs.str_arr_ext.num_total_chars(arr)
            qgjvo__sgpto = bodo.utils.utils.alloc_type(jeu__udycw,
                chnc__okfb, (zyd__iea,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(qgjvo__sgpto, -1)
            ifdrx__nmd = 0
            xwbur__msgvv = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(qgjvo__sgpto,
                    arr, ifdrx__nmd, xwbur__msgvv)
                ifdrx__nmd += len(arr)
                xwbur__msgvv += bodo.libs.str_arr_ext.num_total_chars(arr)
            return qgjvo__sgpto
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(xzd__qbf.dtype, types.Integer) for
        xzd__qbf in arr_list.types) and any(isinstance(xzd__qbf,
        IntegerArrayType) for xzd__qbf in arr_list.types):

        def impl_int_arr_list(arr_list):
            oov__lri = convert_to_nullable_tup(arr_list)
            fyq__rvbqh = []
            oxo__kgg = 0
            for A in oov__lri:
                fyq__rvbqh.append(A._data)
                oxo__kgg += len(A)
            bfhb__kony = bodo.libs.array_kernels.concat(fyq__rvbqh)
            mpxbl__hjd = oxo__kgg + 7 >> 3
            inkes__xfakq = np.empty(mpxbl__hjd, np.uint8)
            fqv__zirm = 0
            for A in oov__lri:
                xnok__rksc = A._null_bitmap
                for bxxgh__qnhyz in range(len(A)):
                    mzr__laas = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        xnok__rksc, bxxgh__qnhyz)
                    bodo.libs.int_arr_ext.set_bit_to_arr(inkes__xfakq,
                        fqv__zirm, mzr__laas)
                    fqv__zirm += 1
            return bodo.libs.int_arr_ext.init_integer_array(bfhb__kony,
                inkes__xfakq)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(xzd__qbf.dtype == types.bool_ for xzd__qbf in
        arr_list.types) and any(xzd__qbf == boolean_array for xzd__qbf in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            oov__lri = convert_to_nullable_tup(arr_list)
            fyq__rvbqh = []
            oxo__kgg = 0
            for A in oov__lri:
                fyq__rvbqh.append(A._data)
                oxo__kgg += len(A)
            bfhb__kony = bodo.libs.array_kernels.concat(fyq__rvbqh)
            mpxbl__hjd = oxo__kgg + 7 >> 3
            inkes__xfakq = np.empty(mpxbl__hjd, np.uint8)
            fqv__zirm = 0
            for A in oov__lri:
                xnok__rksc = A._null_bitmap
                for bxxgh__qnhyz in range(len(A)):
                    mzr__laas = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        xnok__rksc, bxxgh__qnhyz)
                    bodo.libs.int_arr_ext.set_bit_to_arr(inkes__xfakq,
                        fqv__zirm, mzr__laas)
                    fqv__zirm += 1
            return bodo.libs.bool_arr_ext.init_bool_array(bfhb__kony,
                inkes__xfakq)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            sva__dld = []
            for A in arr_list:
                sva__dld.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                sva__dld), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        ktdq__zjv = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        eaaft__spe = 'def impl(arr_list):\n'
        eaaft__spe += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({ktdq__zjv},)), arr_list[0].dtype)
"""
        eek__bkzey = {}
        exec(eaaft__spe, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, eek__bkzey)
        return eek__bkzey['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            oxo__kgg = 0
            for A in arr_list:
                oxo__kgg += len(A)
            qgjvo__sgpto = np.empty(oxo__kgg, dtype)
            uet__hywu = 0
            for A in arr_list:
                n = len(A)
                qgjvo__sgpto[uet__hywu:uet__hywu + n] = A
                uet__hywu += n
            return qgjvo__sgpto
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(xzd__qbf, (
        types.Array, IntegerArrayType)) and isinstance(xzd__qbf.dtype,
        types.Integer) for xzd__qbf in arr_list.types) and any(isinstance(
        xzd__qbf, types.Array) and isinstance(xzd__qbf.dtype, types.Float) for
        xzd__qbf in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            kxtia__auzk = []
            for A in arr_list:
                kxtia__auzk.append(A._data)
            xvtkk__laijy = bodo.libs.array_kernels.concat(kxtia__auzk)
            ege__onqi = bodo.libs.map_arr_ext.init_map_arr(xvtkk__laijy)
            return ege__onqi
        return impl_map_arr_list
    for djb__fncmu in arr_list:
        if not isinstance(djb__fncmu, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(xzd__qbf.astype(np.float64) for xzd__qbf in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    xri__oybgy = len(arr_tup.types)
    eaaft__spe = 'def f(arr_tup):\n'
    eaaft__spe += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        xri__oybgy)), ',' if xri__oybgy == 1 else '')
    frfwx__uvc = {}
    exec(eaaft__spe, {'np': np}, frfwx__uvc)
    wsfv__jcmr = frfwx__uvc['f']
    return wsfv__jcmr


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    xri__oybgy = len(arr_tup.types)
    wrpu__wzk = find_common_np_dtype(arr_tup.types)
    jjph__tsv = None
    jihiz__zlxm = ''
    if isinstance(wrpu__wzk, types.Integer):
        jjph__tsv = bodo.libs.int_arr_ext.IntDtype(wrpu__wzk)
        jihiz__zlxm = '.astype(out_dtype, False)'
    eaaft__spe = 'def f(arr_tup):\n'
    eaaft__spe += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, jihiz__zlxm) for i in range(xri__oybgy)), ',' if 
        xri__oybgy == 1 else '')
    frfwx__uvc = {}
    exec(eaaft__spe, {'bodo': bodo, 'out_dtype': jjph__tsv}, frfwx__uvc)
    dweay__ojwmj = frfwx__uvc['f']
    return dweay__ojwmj


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, xuz__gtso = build_set_seen_na(A)
        return len(s) + int(not dropna and xuz__gtso)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        ism__aqbf = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        rzzmt__edry = len(ism__aqbf)
        return bodo.libs.distributed_api.dist_reduce(rzzmt__edry, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([uprb__bkeze for uprb__bkeze in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        nuch__rph = np.finfo(A.dtype(1).dtype).max
    else:
        nuch__rph = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        qgjvo__sgpto = np.empty(n, A.dtype)
        epo__baaeb = nuch__rph
        for i in range(n):
            epo__baaeb = min(epo__baaeb, A[i])
            qgjvo__sgpto[i] = epo__baaeb
        return qgjvo__sgpto
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        nuch__rph = np.finfo(A.dtype(1).dtype).min
    else:
        nuch__rph = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        qgjvo__sgpto = np.empty(n, A.dtype)
        epo__baaeb = nuch__rph
        for i in range(n):
            epo__baaeb = max(epo__baaeb, A[i])
            qgjvo__sgpto[i] = epo__baaeb
        return qgjvo__sgpto
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        qye__oyliz = arr_info_list_to_table([array_to_info(A)])
        kfvp__hrr = 1
        lhlvy__aqt = 0
        wvv__bwge = drop_duplicates_table(qye__oyliz, parallel, kfvp__hrr,
            lhlvy__aqt, dropna, True)
        qgjvo__sgpto = info_to_array(info_from_table(wvv__bwge, 0), A)
        delete_table(qye__oyliz)
        delete_table(wvv__bwge)
        return qgjvo__sgpto
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    wvru__eafl = bodo.utils.typing.to_nullable_type(arr.dtype)
    npup__znklq = index_arr
    moscy__ofeff = npup__znklq.dtype

    def impl(arr, index_arr):
        n = len(arr)
        croa__dkvtm = init_nested_counts(wvru__eafl)
        wuno__bykfs = init_nested_counts(moscy__ofeff)
        for i in range(n):
            fku__wxr = index_arr[i]
            if isna(arr, i):
                croa__dkvtm = (croa__dkvtm[0] + 1,) + croa__dkvtm[1:]
                wuno__bykfs = add_nested_counts(wuno__bykfs, fku__wxr)
                continue
            wuycf__raj = arr[i]
            if len(wuycf__raj) == 0:
                croa__dkvtm = (croa__dkvtm[0] + 1,) + croa__dkvtm[1:]
                wuno__bykfs = add_nested_counts(wuno__bykfs, fku__wxr)
                continue
            croa__dkvtm = add_nested_counts(croa__dkvtm, wuycf__raj)
            for sjp__qrgf in range(len(wuycf__raj)):
                wuno__bykfs = add_nested_counts(wuno__bykfs, fku__wxr)
        qgjvo__sgpto = bodo.utils.utils.alloc_type(croa__dkvtm[0],
            wvru__eafl, croa__dkvtm[1:])
        dfirh__ucxzq = bodo.utils.utils.alloc_type(croa__dkvtm[0],
            npup__znklq, wuno__bykfs)
        ymrc__xdbs = 0
        for i in range(n):
            if isna(arr, i):
                setna(qgjvo__sgpto, ymrc__xdbs)
                dfirh__ucxzq[ymrc__xdbs] = index_arr[i]
                ymrc__xdbs += 1
                continue
            wuycf__raj = arr[i]
            aarjb__zdwfm = len(wuycf__raj)
            if aarjb__zdwfm == 0:
                setna(qgjvo__sgpto, ymrc__xdbs)
                dfirh__ucxzq[ymrc__xdbs] = index_arr[i]
                ymrc__xdbs += 1
                continue
            qgjvo__sgpto[ymrc__xdbs:ymrc__xdbs + aarjb__zdwfm] = wuycf__raj
            dfirh__ucxzq[ymrc__xdbs:ymrc__xdbs + aarjb__zdwfm] = index_arr[i]
            ymrc__xdbs += aarjb__zdwfm
        return qgjvo__sgpto, dfirh__ucxzq
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    wvru__eafl = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        croa__dkvtm = init_nested_counts(wvru__eafl)
        for i in range(n):
            if isna(arr, i):
                croa__dkvtm = (croa__dkvtm[0] + 1,) + croa__dkvtm[1:]
                wcj__qmy = 1
            else:
                wuycf__raj = arr[i]
                nyczz__thm = len(wuycf__raj)
                if nyczz__thm == 0:
                    croa__dkvtm = (croa__dkvtm[0] + 1,) + croa__dkvtm[1:]
                    wcj__qmy = 1
                    continue
                else:
                    croa__dkvtm = add_nested_counts(croa__dkvtm, wuycf__raj)
                    wcj__qmy = nyczz__thm
            if counts[i] != wcj__qmy:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        qgjvo__sgpto = bodo.utils.utils.alloc_type(croa__dkvtm[0],
            wvru__eafl, croa__dkvtm[1:])
        ymrc__xdbs = 0
        for i in range(n):
            if isna(arr, i):
                setna(qgjvo__sgpto, ymrc__xdbs)
                ymrc__xdbs += 1
                continue
            wuycf__raj = arr[i]
            aarjb__zdwfm = len(wuycf__raj)
            if aarjb__zdwfm == 0:
                setna(qgjvo__sgpto, ymrc__xdbs)
                ymrc__xdbs += 1
                continue
            qgjvo__sgpto[ymrc__xdbs:ymrc__xdbs + aarjb__zdwfm] = wuycf__raj
            ymrc__xdbs += aarjb__zdwfm
        return qgjvo__sgpto
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(qflsv__hdyno) for qflsv__hdyno in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        unyxy__qotl = 'np.empty(n, np.int64)'
        yoaj__igfdo = 'out_arr[i] = 1'
        icac__jio = 'max(len(arr[i]), 1)'
    else:
        unyxy__qotl = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        yoaj__igfdo = 'bodo.libs.array_kernels.setna(out_arr, i)'
        icac__jio = 'len(arr[i])'
    eaaft__spe = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {unyxy__qotl}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {yoaj__igfdo}
        else:
            out_arr[i] = {icac__jio}
    return out_arr
    """
    frfwx__uvc = {}
    exec(eaaft__spe, {'bodo': bodo, 'numba': numba, 'np': np}, frfwx__uvc)
    impl = frfwx__uvc['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    npup__znklq = index_arr
    moscy__ofeff = npup__znklq.dtype

    def impl(arr, pat, n, index_arr):
        oac__ugnf = pat is not None and len(pat) > 1
        if oac__ugnf:
            qtn__wiv = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        vgmum__fugmz = len(arr)
        jeu__udycw = 0
        zyd__iea = 0
        wuno__bykfs = init_nested_counts(moscy__ofeff)
        for i in range(vgmum__fugmz):
            fku__wxr = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                jeu__udycw += 1
                wuno__bykfs = add_nested_counts(wuno__bykfs, fku__wxr)
                continue
            if oac__ugnf:
                ewrcu__acv = qtn__wiv.split(arr[i], maxsplit=n)
            else:
                ewrcu__acv = arr[i].split(pat, n)
            jeu__udycw += len(ewrcu__acv)
            for s in ewrcu__acv:
                wuno__bykfs = add_nested_counts(wuno__bykfs, fku__wxr)
                zyd__iea += bodo.libs.str_arr_ext.get_utf8_size(s)
        qgjvo__sgpto = bodo.libs.str_arr_ext.pre_alloc_string_array(jeu__udycw,
            zyd__iea)
        dfirh__ucxzq = bodo.utils.utils.alloc_type(jeu__udycw, npup__znklq,
            wuno__bykfs)
        ims__qaym = 0
        for bxxgh__qnhyz in range(vgmum__fugmz):
            if isna(arr, bxxgh__qnhyz):
                qgjvo__sgpto[ims__qaym] = ''
                bodo.libs.array_kernels.setna(qgjvo__sgpto, ims__qaym)
                dfirh__ucxzq[ims__qaym] = index_arr[bxxgh__qnhyz]
                ims__qaym += 1
                continue
            if oac__ugnf:
                ewrcu__acv = qtn__wiv.split(arr[bxxgh__qnhyz], maxsplit=n)
            else:
                ewrcu__acv = arr[bxxgh__qnhyz].split(pat, n)
            oep__vehrc = len(ewrcu__acv)
            qgjvo__sgpto[ims__qaym:ims__qaym + oep__vehrc] = ewrcu__acv
            dfirh__ucxzq[ims__qaym:ims__qaym + oep__vehrc] = index_arr[
                bxxgh__qnhyz]
            ims__qaym += oep__vehrc
        return qgjvo__sgpto, dfirh__ucxzq
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
            qgjvo__sgpto = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                qgjvo__sgpto[i] = np.nan
            return qgjvo__sgpto
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            yfaqy__clcuk = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            ehcvp__rpky = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(ehcvp__rpky, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(yfaqy__clcuk,
                ehcvp__rpky, True)
        return impl_dict
    hqts__tqm = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        qgjvo__sgpto = bodo.utils.utils.alloc_type(n, hqts__tqm, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(qgjvo__sgpto, i)
        return qgjvo__sgpto
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
    ncxo__mejkd = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            qgjvo__sgpto = bodo.utils.utils.alloc_type(new_len, ncxo__mejkd)
            bodo.libs.str_arr_ext.str_copy_ptr(qgjvo__sgpto.ctypes, 0, A.
                ctypes, old_size)
            return qgjvo__sgpto
        return impl_char

    def impl(A, old_size, new_len):
        qgjvo__sgpto = bodo.utils.utils.alloc_type(new_len, ncxo__mejkd, (-1,))
        qgjvo__sgpto[:old_size] = A[:old_size]
        return qgjvo__sgpto
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    tcny__kjo = math.ceil((stop - start) / step)
    return int(max(tcny__kjo, 0))


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
    if any(isinstance(uprb__bkeze, types.Complex) for uprb__bkeze in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            new__nqd = (stop - start) / step
            tcny__kjo = math.ceil(new__nqd.real)
            laig__lvivg = math.ceil(new__nqd.imag)
            bqf__wxo = int(max(min(laig__lvivg, tcny__kjo), 0))
            arr = np.empty(bqf__wxo, dtype)
            for i in numba.parfors.parfor.internal_prange(bqf__wxo):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            bqf__wxo = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(bqf__wxo, dtype)
            for i in numba.parfors.parfor.internal_prange(bqf__wxo):
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
        enbec__soju = arr,
        if not inplace:
            enbec__soju = arr.copy(),
        uuij__omwc = bodo.libs.str_arr_ext.to_list_if_immutable_arr(enbec__soju
            )
        fqv__zutiy = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(uuij__omwc, 0, n, fqv__zutiy)
        if not ascending:
            bodo.libs.timsort.reverseRange(uuij__omwc, 0, n, fqv__zutiy)
        bodo.libs.str_arr_ext.cp_str_list_to_array(enbec__soju, uuij__omwc)
        return enbec__soju[0]
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
        ege__onqi = []
        for i in range(n):
            if A[i]:
                ege__onqi.append(i + offset)
        return np.array(ege__onqi, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    ncxo__mejkd = element_type(A)
    if ncxo__mejkd == types.unicode_type:
        null_value = '""'
    elif ncxo__mejkd == types.bool_:
        null_value = 'False'
    elif ncxo__mejkd == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif ncxo__mejkd == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    ims__qaym = 'i'
    dura__kjdqm = False
    iyk__njf = get_overload_const_str(method)
    if iyk__njf in ('ffill', 'pad'):
        jvv__cgfzy = 'n'
        send_right = True
    elif iyk__njf in ('backfill', 'bfill'):
        jvv__cgfzy = 'n-1, -1, -1'
        send_right = False
        if ncxo__mejkd == types.unicode_type:
            ims__qaym = '(n - 1) - i'
            dura__kjdqm = True
    eaaft__spe = 'def impl(A, method, parallel=False):\n'
    eaaft__spe += '  A = decode_if_dict_array(A)\n'
    eaaft__spe += '  has_last_value = False\n'
    eaaft__spe += f'  last_value = {null_value}\n'
    eaaft__spe += '  if parallel:\n'
    eaaft__spe += '    rank = bodo.libs.distributed_api.get_rank()\n'
    eaaft__spe += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    eaaft__spe += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    eaaft__spe += '  n = len(A)\n'
    eaaft__spe += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    eaaft__spe += f'  for i in range({jvv__cgfzy}):\n'
    eaaft__spe += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    eaaft__spe += (
        f'      bodo.libs.array_kernels.setna(out_arr, {ims__qaym})\n')
    eaaft__spe += '      continue\n'
    eaaft__spe += '    s = A[i]\n'
    eaaft__spe += '    if bodo.libs.array_kernels.isna(A, i):\n'
    eaaft__spe += '      s = last_value\n'
    eaaft__spe += f'    out_arr[{ims__qaym}] = s\n'
    eaaft__spe += '    last_value = s\n'
    eaaft__spe += '    has_last_value = True\n'
    if dura__kjdqm:
        eaaft__spe += '  return out_arr[::-1]\n'
    else:
        eaaft__spe += '  return out_arr\n'
    yjl__shz = {}
    exec(eaaft__spe, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, yjl__shz)
    impl = yjl__shz['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        ihx__bazlg = 0
        ojzq__ttb = n_pes - 1
        jxbd__ysto = np.int32(rank + 1)
        ztqw__ikhs = np.int32(rank - 1)
        wubd__xvt = len(in_arr) - 1
        fftfg__lduo = -1
        zsnz__uvlq = -1
    else:
        ihx__bazlg = n_pes - 1
        ojzq__ttb = 0
        jxbd__ysto = np.int32(rank - 1)
        ztqw__ikhs = np.int32(rank + 1)
        wubd__xvt = 0
        fftfg__lduo = len(in_arr)
        zsnz__uvlq = 1
    dthxk__cgzms = np.int32(bodo.hiframes.rolling.comm_border_tag)
    bgl__nmjb = np.empty(1, dtype=np.bool_)
    jmu__uxtl = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    tjz__jemz = np.empty(1, dtype=np.bool_)
    wksbv__dndgr = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    qld__gpqdq = False
    iuy__kzn = null_value
    for i in range(wubd__xvt, fftfg__lduo, zsnz__uvlq):
        if not isna(in_arr, i):
            qld__gpqdq = True
            iuy__kzn = in_arr[i]
            break
    if rank != ihx__bazlg:
        mqjy__dzolt = bodo.libs.distributed_api.irecv(bgl__nmjb, 1,
            ztqw__ikhs, dthxk__cgzms, True)
        bodo.libs.distributed_api.wait(mqjy__dzolt, True)
        zaya__fic = bodo.libs.distributed_api.irecv(jmu__uxtl, 1,
            ztqw__ikhs, dthxk__cgzms, True)
        bodo.libs.distributed_api.wait(zaya__fic, True)
        ztu__rxksw = bgl__nmjb[0]
        rias__dbdf = jmu__uxtl[0]
    else:
        ztu__rxksw = False
        rias__dbdf = null_value
    if qld__gpqdq:
        tjz__jemz[0] = qld__gpqdq
        wksbv__dndgr[0] = iuy__kzn
    else:
        tjz__jemz[0] = ztu__rxksw
        wksbv__dndgr[0] = rias__dbdf
    if rank != ojzq__ttb:
        lln__unxkl = bodo.libs.distributed_api.isend(tjz__jemz, 1,
            jxbd__ysto, dthxk__cgzms, True)
        gwcxl__cqznm = bodo.libs.distributed_api.isend(wksbv__dndgr, 1,
            jxbd__ysto, dthxk__cgzms, True)
    return ztu__rxksw, rias__dbdf


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    gop__yjg = {'axis': axis, 'kind': kind, 'order': order}
    oknc__ebs = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', gop__yjg, oknc__ebs, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    ncxo__mejkd = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            vgmum__fugmz = len(A)
            qgjvo__sgpto = bodo.utils.utils.alloc_type(vgmum__fugmz *
                repeats, ncxo__mejkd, (-1,))
            for i in range(vgmum__fugmz):
                ims__qaym = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for bxxgh__qnhyz in range(repeats):
                        bodo.libs.array_kernels.setna(qgjvo__sgpto, 
                            ims__qaym + bxxgh__qnhyz)
                else:
                    qgjvo__sgpto[ims__qaym:ims__qaym + repeats] = A[i]
            return qgjvo__sgpto
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        vgmum__fugmz = len(A)
        qgjvo__sgpto = bodo.utils.utils.alloc_type(repeats.sum(),
            ncxo__mejkd, (-1,))
        ims__qaym = 0
        for i in range(vgmum__fugmz):
            qelw__kplx = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for bxxgh__qnhyz in range(qelw__kplx):
                    bodo.libs.array_kernels.setna(qgjvo__sgpto, ims__qaym +
                        bxxgh__qnhyz)
            else:
                qgjvo__sgpto[ims__qaym:ims__qaym + qelw__kplx] = A[i]
            ims__qaym += qelw__kplx
        return qgjvo__sgpto
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
        offx__vshc = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(offx__vshc, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        inr__ybyux = bodo.libs.array_kernels.concat([A1, A2])
        lurjo__vdva = bodo.libs.array_kernels.unique(inr__ybyux)
        return pd.Series(lurjo__vdva).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    gop__yjg = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    oknc__ebs = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', gop__yjg, oknc__ebs, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        shz__trage = bodo.libs.array_kernels.unique(A1)
        cpwkn__gtg = bodo.libs.array_kernels.unique(A2)
        inr__ybyux = bodo.libs.array_kernels.concat([shz__trage, cpwkn__gtg])
        vryml__tic = pd.Series(inr__ybyux).sort_values().values
        return slice_array_intersect1d(vryml__tic)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    voi__dzy = arr[1:] == arr[:-1]
    return arr[:-1][voi__dzy]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    dthxk__cgzms = np.int32(bodo.hiframes.rolling.comm_border_tag)
    nqb__btxif = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        fhh__etfe = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), dthxk__cgzms, True)
        bodo.libs.distributed_api.wait(fhh__etfe, True)
    if rank == n_pes - 1:
        return None
    else:
        aru__nlub = bodo.libs.distributed_api.irecv(nqb__btxif, 1, np.int32
            (rank + 1), dthxk__cgzms, True)
        bodo.libs.distributed_api.wait(aru__nlub, True)
        return nqb__btxif[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    voi__dzy = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            voi__dzy[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        jaf__asmw = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == jaf__asmw:
            voi__dzy[n - 1] = True
    return voi__dzy


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    gop__yjg = {'assume_unique': assume_unique}
    oknc__ebs = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', gop__yjg, oknc__ebs, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        shz__trage = bodo.libs.array_kernels.unique(A1)
        cpwkn__gtg = bodo.libs.array_kernels.unique(A2)
        voi__dzy = calculate_mask_setdiff1d(shz__trage, cpwkn__gtg)
        return pd.Series(shz__trage[voi__dzy]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    voi__dzy = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        voi__dzy &= A1 != A2[i]
    return voi__dzy


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    gop__yjg = {'retstep': retstep, 'axis': axis}
    oknc__ebs = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', gop__yjg, oknc__ebs, 'numpy')
    kood__kqnl = False
    if is_overload_none(dtype):
        ncxo__mejkd = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            kood__kqnl = True
        ncxo__mejkd = numba.np.numpy_support.as_dtype(dtype).type
    if kood__kqnl:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            pyjet__gyddb = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            qgjvo__sgpto = np.empty(num, ncxo__mejkd)
            for i in numba.parfors.parfor.internal_prange(num):
                qgjvo__sgpto[i] = ncxo__mejkd(np.floor(start + i *
                    pyjet__gyddb))
            return qgjvo__sgpto
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            pyjet__gyddb = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            qgjvo__sgpto = np.empty(num, ncxo__mejkd)
            for i in numba.parfors.parfor.internal_prange(num):
                qgjvo__sgpto[i] = ncxo__mejkd(start + i * pyjet__gyddb)
            return qgjvo__sgpto
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
        xri__oybgy = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                xri__oybgy += A[i] == val
        return xri__oybgy > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    gop__yjg = {'axis': axis, 'out': out, 'keepdims': keepdims}
    oknc__ebs = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', gop__yjg, oknc__ebs, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        xri__oybgy = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                xri__oybgy += int(bool(A[i]))
        return xri__oybgy > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    gop__yjg = {'axis': axis, 'out': out, 'keepdims': keepdims}
    oknc__ebs = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', gop__yjg, oknc__ebs, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        xri__oybgy = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                xri__oybgy += int(bool(A[i]))
        return xri__oybgy == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    gop__yjg = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    oknc__ebs = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', gop__yjg, oknc__ebs, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        hfvxv__ere = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            qgjvo__sgpto = np.empty(n, hfvxv__ere)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(qgjvo__sgpto, i)
                    continue
                qgjvo__sgpto[i] = np_cbrt_scalar(A[i], hfvxv__ere)
            return qgjvo__sgpto
        return impl_arr
    hfvxv__ere = np.promote_types(numba.np.numpy_support.as_dtype(A), numba
        .np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, hfvxv__ere)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    kkrl__shvhi = x < 0
    if kkrl__shvhi:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if kkrl__shvhi:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    ske__mhwmt = isinstance(tup, (types.BaseTuple, types.List))
    lwl__qof = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for djb__fncmu in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                djb__fncmu, 'numpy.hstack()')
            ske__mhwmt = ske__mhwmt and bodo.utils.utils.is_array_typ(
                djb__fncmu, False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        ske__mhwmt = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif lwl__qof:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        eyqsx__urz = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for djb__fncmu in eyqsx__urz.types:
            lwl__qof = lwl__qof and bodo.utils.utils.is_array_typ(djb__fncmu,
                False)
    if not (ske__mhwmt or lwl__qof):
        return
    if lwl__qof:

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
    gop__yjg = {'check_valid': check_valid, 'tol': tol}
    oknc__ebs = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', gop__yjg,
        oknc__ebs, 'numpy')
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
        gwh__lrsrl = mean.shape[0]
        iwk__qqdl = size, gwh__lrsrl
        mbn__scll = np.random.standard_normal(iwk__qqdl)
        cov = cov.astype(np.float64)
        onwwh__nljy, s, urop__vkzj = np.linalg.svd(cov)
        res = np.dot(mbn__scll, np.sqrt(s).reshape(gwh__lrsrl, 1) * urop__vkzj)
        wdjs__ekou = res + mean
        return wdjs__ekou
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
            gqq__ktds = bodo.hiframes.series_kernels._get_type_max_value(arr)
            rxrh__qnd = typing.builtins.IndexValue(-1, gqq__ktds)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pkbz__qoptn = typing.builtins.IndexValue(i, arr[i])
                rxrh__qnd = min(rxrh__qnd, pkbz__qoptn)
            return rxrh__qnd.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        ojpfm__wkg = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            nqya__hizbu = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            gqq__ktds = ojpfm__wkg(len(arr.dtype.categories) + 1)
            rxrh__qnd = typing.builtins.IndexValue(-1, gqq__ktds)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pkbz__qoptn = typing.builtins.IndexValue(i, nqya__hizbu[i])
                rxrh__qnd = min(rxrh__qnd, pkbz__qoptn)
            return rxrh__qnd.index
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
            gqq__ktds = bodo.hiframes.series_kernels._get_type_min_value(arr)
            rxrh__qnd = typing.builtins.IndexValue(-1, gqq__ktds)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pkbz__qoptn = typing.builtins.IndexValue(i, arr[i])
                rxrh__qnd = max(rxrh__qnd, pkbz__qoptn)
            return rxrh__qnd.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        ojpfm__wkg = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            nqya__hizbu = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            gqq__ktds = ojpfm__wkg(-1)
            rxrh__qnd = typing.builtins.IndexValue(-1, gqq__ktds)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                pkbz__qoptn = typing.builtins.IndexValue(i, nqya__hizbu[i])
                rxrh__qnd = max(rxrh__qnd, pkbz__qoptn)
            return rxrh__qnd.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
