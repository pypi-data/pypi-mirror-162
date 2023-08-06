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
        vbx__zso = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = vbx__zso
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        vbx__zso = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = vbx__zso
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
            rssf__ywr = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            rssf__ywr[ind + 1] = rssf__ywr[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            rssf__ywr = bodo.libs.array_item_arr_ext.get_offsets(arr)
            rssf__ywr[ind + 1] = rssf__ywr[ind]
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
    ljw__ghiz = arr_tup.count
    sqxb__jpug = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(ljw__ghiz):
        sqxb__jpug += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    sqxb__jpug += '  return\n'
    bvi__woat = {}
    exec(sqxb__jpug, {'setna': setna}, bvi__woat)
    impl = bvi__woat['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        kab__kxbr = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(kab__kxbr.start, kab__kxbr.stop, kab__kxbr.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        rhear__vzrm = 'n'
        bvuy__mmg = 'n_pes'
        xpzv__fkzcv = 'min_op'
    else:
        rhear__vzrm = 'n-1, -1, -1'
        bvuy__mmg = '-1'
        xpzv__fkzcv = 'max_op'
    sqxb__jpug = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {bvuy__mmg}
    for i in range({rhear__vzrm}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {xpzv__fkzcv}))
        if possible_valid_rank != {bvuy__mmg}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    bvi__woat = {}
    exec(sqxb__jpug, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, bvi__woat)
    impl = bvi__woat['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    pljw__agqjz = array_to_info(arr)
    _median_series_computation(res, pljw__agqjz, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pljw__agqjz)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    pljw__agqjz = array_to_info(arr)
    _autocorr_series_computation(res, pljw__agqjz, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pljw__agqjz)


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
    pljw__agqjz = array_to_info(arr)
    _compute_series_monotonicity(res, pljw__agqjz, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(pljw__agqjz)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    jpn__sst = res[0] > 0.5
    return jpn__sst


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        waxjb__yrx = '-'
        gdf__iyz = 'index_arr[0] > threshhold_date'
        rhear__vzrm = '1, n+1'
        qqvzj__ibgwq = 'index_arr[-i] <= threshhold_date'
        fumvz__kec = 'i - 1'
    else:
        waxjb__yrx = '+'
        gdf__iyz = 'index_arr[-1] < threshhold_date'
        rhear__vzrm = 'n'
        qqvzj__ibgwq = 'index_arr[i] >= threshhold_date'
        fumvz__kec = 'i'
    sqxb__jpug = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        sqxb__jpug += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        sqxb__jpug += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            sqxb__jpug += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            sqxb__jpug += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            sqxb__jpug += '    else:\n'
            sqxb__jpug += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            sqxb__jpug += (
                f'    threshhold_date = initial_date {waxjb__yrx} date_offset\n'
                )
    else:
        sqxb__jpug += f'  threshhold_date = initial_date {waxjb__yrx} offset\n'
    sqxb__jpug += '  local_valid = 0\n'
    sqxb__jpug += f'  n = len(index_arr)\n'
    sqxb__jpug += f'  if n:\n'
    sqxb__jpug += f'    if {gdf__iyz}:\n'
    sqxb__jpug += '      loc_valid = n\n'
    sqxb__jpug += '    else:\n'
    sqxb__jpug += f'      for i in range({rhear__vzrm}):\n'
    sqxb__jpug += f'        if {qqvzj__ibgwq}:\n'
    sqxb__jpug += f'          loc_valid = {fumvz__kec}\n'
    sqxb__jpug += '          break\n'
    sqxb__jpug += '  if is_parallel:\n'
    sqxb__jpug += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    sqxb__jpug += '    return total_valid\n'
    sqxb__jpug += '  else:\n'
    sqxb__jpug += '    return loc_valid\n'
    bvi__woat = {}
    exec(sqxb__jpug, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, bvi__woat)
    return bvi__woat['impl']


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
    dehb__xakwe = numba_to_c_type(sig.args[0].dtype)
    jlk__love = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), dehb__xakwe))
    zklzl__uget = args[0]
    ewuh__etugr = sig.args[0]
    if isinstance(ewuh__etugr, (IntegerArrayType, BooleanArrayType)):
        zklzl__uget = cgutils.create_struct_proxy(ewuh__etugr)(context,
            builder, zklzl__uget).data
        ewuh__etugr = types.Array(ewuh__etugr.dtype, 1, 'C')
    assert ewuh__etugr.ndim == 1
    arr = make_array(ewuh__etugr)(context, builder, zklzl__uget)
    asb__qpz = builder.extract_value(arr.shape, 0)
    wqiwu__gnadc = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        asb__qpz, args[1], builder.load(jlk__love)]
    lhza__qazwr = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    wmfdd__ndk = lir.FunctionType(lir.DoubleType(), lhza__qazwr)
    sbea__tgrd = cgutils.get_or_insert_function(builder.module, wmfdd__ndk,
        name='quantile_sequential')
    utohn__uwmic = builder.call(sbea__tgrd, wqiwu__gnadc)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return utohn__uwmic


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    dehb__xakwe = numba_to_c_type(sig.args[0].dtype)
    jlk__love = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), dehb__xakwe))
    zklzl__uget = args[0]
    ewuh__etugr = sig.args[0]
    if isinstance(ewuh__etugr, (IntegerArrayType, BooleanArrayType)):
        zklzl__uget = cgutils.create_struct_proxy(ewuh__etugr)(context,
            builder, zklzl__uget).data
        ewuh__etugr = types.Array(ewuh__etugr.dtype, 1, 'C')
    assert ewuh__etugr.ndim == 1
    arr = make_array(ewuh__etugr)(context, builder, zklzl__uget)
    asb__qpz = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        qvu__hjnvx = args[2]
    else:
        qvu__hjnvx = asb__qpz
    wqiwu__gnadc = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        asb__qpz, qvu__hjnvx, args[1], builder.load(jlk__love)]
    lhza__qazwr = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        IntType(64), lir.DoubleType(), lir.IntType(32)]
    wmfdd__ndk = lir.FunctionType(lir.DoubleType(), lhza__qazwr)
    sbea__tgrd = cgutils.get_or_insert_function(builder.module, wmfdd__ndk,
        name='quantile_parallel')
    utohn__uwmic = builder.call(sbea__tgrd, wqiwu__gnadc)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return utohn__uwmic


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        cmg__vws = np.nonzero(pd.isna(arr))[0]
        isqsh__xcdy = arr[1:] != arr[:-1]
        isqsh__xcdy[pd.isna(isqsh__xcdy)] = False
        eiqo__puw = isqsh__xcdy.astype(np.bool_)
        fzckd__yvl = np.concatenate((np.array([True]), eiqo__puw))
        if cmg__vws.size:
            anp__cvq, fsw__vljj = cmg__vws[0], cmg__vws[1:]
            fzckd__yvl[anp__cvq] = True
            if fsw__vljj.size:
                fzckd__yvl[fsw__vljj] = False
                if fsw__vljj[-1] + 1 < fzckd__yvl.size:
                    fzckd__yvl[fsw__vljj[-1] + 1] = True
            elif anp__cvq + 1 < fzckd__yvl.size:
                fzckd__yvl[anp__cvq + 1] = True
        return fzckd__yvl
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
    sqxb__jpug = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    sqxb__jpug += '  na_idxs = pd.isna(arr)\n'
    sqxb__jpug += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    sqxb__jpug += '  nas = sum(na_idxs)\n'
    if not ascending:
        sqxb__jpug += '  if nas and nas < (sorter.size - 1):\n'
        sqxb__jpug += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        sqxb__jpug += '  else:\n'
        sqxb__jpug += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        sqxb__jpug += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    sqxb__jpug += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    sqxb__jpug += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        sqxb__jpug += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        sqxb__jpug += '    inv,\n'
        sqxb__jpug += '    new_dtype=np.float64,\n'
        sqxb__jpug += '    copy=True,\n'
        sqxb__jpug += '    nan_to_str=False,\n'
        sqxb__jpug += '    from_series=True,\n'
        sqxb__jpug += '    ) + 1\n'
    else:
        sqxb__jpug += '  arr = arr[sorter]\n'
        sqxb__jpug += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        sqxb__jpug += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            sqxb__jpug += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            sqxb__jpug += '    dense,\n'
            sqxb__jpug += '    new_dtype=np.float64,\n'
            sqxb__jpug += '    copy=True,\n'
            sqxb__jpug += '    nan_to_str=False,\n'
            sqxb__jpug += '    from_series=True,\n'
            sqxb__jpug += '  )\n'
        else:
            sqxb__jpug += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            sqxb__jpug += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                sqxb__jpug += '  ret = count_float[dense]\n'
            elif method == 'min':
                sqxb__jpug += '  ret = count_float[dense - 1] + 1\n'
            else:
                sqxb__jpug += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                sqxb__jpug += '  ret[na_idxs] = -1\n'
            sqxb__jpug += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            sqxb__jpug += '  div_val = arr.size - nas\n'
        else:
            sqxb__jpug += '  div_val = arr.size\n'
        sqxb__jpug += '  for i in range(len(ret)):\n'
        sqxb__jpug += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        sqxb__jpug += '  ret[na_idxs] = np.nan\n'
    sqxb__jpug += '  return ret\n'
    bvi__woat = {}
    exec(sqxb__jpug, {'np': np, 'pd': pd, 'bodo': bodo}, bvi__woat)
    return bvi__woat['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    ybkj__qaowh = start
    ubdqc__zbpb = 2 * start + 1
    smy__bvfa = 2 * start + 2
    if ubdqc__zbpb < n and not cmp_f(arr[ubdqc__zbpb], arr[ybkj__qaowh]):
        ybkj__qaowh = ubdqc__zbpb
    if smy__bvfa < n and not cmp_f(arr[smy__bvfa], arr[ybkj__qaowh]):
        ybkj__qaowh = smy__bvfa
    if ybkj__qaowh != start:
        arr[start], arr[ybkj__qaowh] = arr[ybkj__qaowh], arr[start]
        ind_arr[start], ind_arr[ybkj__qaowh] = ind_arr[ybkj__qaowh], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, ybkj__qaowh, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        lpm__ytzrz = np.empty(k, A.dtype)
        szi__sylww = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                lpm__ytzrz[ind] = A[i]
                szi__sylww[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            lpm__ytzrz = lpm__ytzrz[:ind]
            szi__sylww = szi__sylww[:ind]
        return lpm__ytzrz, szi__sylww, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        uyq__ksi = np.sort(A)
        bbr__lpz = index_arr[np.argsort(A)]
        byozf__hwh = pd.Series(uyq__ksi).notna().values
        uyq__ksi = uyq__ksi[byozf__hwh]
        bbr__lpz = bbr__lpz[byozf__hwh]
        if is_largest:
            uyq__ksi = uyq__ksi[::-1]
            bbr__lpz = bbr__lpz[::-1]
        return np.ascontiguousarray(uyq__ksi), np.ascontiguousarray(bbr__lpz)
    lpm__ytzrz, szi__sylww, start = select_k_nonan(A, index_arr, m, k)
    szi__sylww = szi__sylww[lpm__ytzrz.argsort()]
    lpm__ytzrz.sort()
    if not is_largest:
        lpm__ytzrz = np.ascontiguousarray(lpm__ytzrz[::-1])
        szi__sylww = np.ascontiguousarray(szi__sylww[::-1])
    for i in range(start, m):
        if cmp_f(A[i], lpm__ytzrz[0]):
            lpm__ytzrz[0] = A[i]
            szi__sylww[0] = index_arr[i]
            min_heapify(lpm__ytzrz, szi__sylww, k, 0, cmp_f)
    szi__sylww = szi__sylww[lpm__ytzrz.argsort()]
    lpm__ytzrz.sort()
    if is_largest:
        lpm__ytzrz = lpm__ytzrz[::-1]
        szi__sylww = szi__sylww[::-1]
    return np.ascontiguousarray(lpm__ytzrz), np.ascontiguousarray(szi__sylww)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    lrez__yndp = bodo.libs.distributed_api.get_rank()
    wqb__zdq, cik__rrqg = nlargest(A, I, k, is_largest, cmp_f)
    ogx__uen = bodo.libs.distributed_api.gatherv(wqb__zdq)
    jnl__gxv = bodo.libs.distributed_api.gatherv(cik__rrqg)
    if lrez__yndp == MPI_ROOT:
        res, hmih__rllq = nlargest(ogx__uen, jnl__gxv, k, is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        hmih__rllq = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(hmih__rllq)
    return res, hmih__rllq


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    cwamk__ktdr, ejhv__rvo = mat.shape
    rsuu__qoxeb = np.empty((ejhv__rvo, ejhv__rvo), dtype=np.float64)
    for vjrvh__qvv in range(ejhv__rvo):
        for xubi__qamrt in range(vjrvh__qvv + 1):
            xkey__xpyfr = 0
            uyxkp__dpr = lxxf__cyin = keo__ebbkx = syj__ydp = 0.0
            for i in range(cwamk__ktdr):
                if np.isfinite(mat[i, vjrvh__qvv]) and np.isfinite(mat[i,
                    xubi__qamrt]):
                    imqp__zjm = mat[i, vjrvh__qvv]
                    bjoj__ckubg = mat[i, xubi__qamrt]
                    xkey__xpyfr += 1
                    keo__ebbkx += imqp__zjm
                    syj__ydp += bjoj__ckubg
            if parallel:
                xkey__xpyfr = bodo.libs.distributed_api.dist_reduce(xkey__xpyfr
                    , sum_op)
                keo__ebbkx = bodo.libs.distributed_api.dist_reduce(keo__ebbkx,
                    sum_op)
                syj__ydp = bodo.libs.distributed_api.dist_reduce(syj__ydp,
                    sum_op)
            if xkey__xpyfr < minpv:
                rsuu__qoxeb[vjrvh__qvv, xubi__qamrt] = rsuu__qoxeb[
                    xubi__qamrt, vjrvh__qvv] = np.nan
            else:
                pdv__tgu = keo__ebbkx / xkey__xpyfr
                lkzpx__peq = syj__ydp / xkey__xpyfr
                keo__ebbkx = 0.0
                for i in range(cwamk__ktdr):
                    if np.isfinite(mat[i, vjrvh__qvv]) and np.isfinite(mat[
                        i, xubi__qamrt]):
                        imqp__zjm = mat[i, vjrvh__qvv] - pdv__tgu
                        bjoj__ckubg = mat[i, xubi__qamrt] - lkzpx__peq
                        keo__ebbkx += imqp__zjm * bjoj__ckubg
                        uyxkp__dpr += imqp__zjm * imqp__zjm
                        lxxf__cyin += bjoj__ckubg * bjoj__ckubg
                if parallel:
                    keo__ebbkx = bodo.libs.distributed_api.dist_reduce(
                        keo__ebbkx, sum_op)
                    uyxkp__dpr = bodo.libs.distributed_api.dist_reduce(
                        uyxkp__dpr, sum_op)
                    lxxf__cyin = bodo.libs.distributed_api.dist_reduce(
                        lxxf__cyin, sum_op)
                mwqis__zymn = xkey__xpyfr - 1.0 if cov else sqrt(uyxkp__dpr *
                    lxxf__cyin)
                if mwqis__zymn != 0.0:
                    rsuu__qoxeb[vjrvh__qvv, xubi__qamrt] = rsuu__qoxeb[
                        xubi__qamrt, vjrvh__qvv] = keo__ebbkx / mwqis__zymn
                else:
                    rsuu__qoxeb[vjrvh__qvv, xubi__qamrt] = rsuu__qoxeb[
                        xubi__qamrt, vjrvh__qvv] = np.nan
    return rsuu__qoxeb


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    djsz__lnwgm = n != 1
    sqxb__jpug = 'def impl(data, parallel=False):\n'
    sqxb__jpug += '  if parallel:\n'
    ant__xdqw = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    sqxb__jpug += f'    cpp_table = arr_info_list_to_table([{ant__xdqw}])\n'
    sqxb__jpug += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    aonza__qwvn = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    sqxb__jpug += f'    data = ({aonza__qwvn},)\n'
    sqxb__jpug += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    sqxb__jpug += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    sqxb__jpug += '    bodo.libs.array.delete_table(cpp_table)\n'
    sqxb__jpug += '  n = len(data[0])\n'
    sqxb__jpug += '  out = np.empty(n, np.bool_)\n'
    sqxb__jpug += '  uniqs = dict()\n'
    if djsz__lnwgm:
        sqxb__jpug += '  for i in range(n):\n'
        vtp__xxz = ', '.join(f'data[{i}][i]' for i in range(n))
        hbarf__vkxe = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        sqxb__jpug += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({vtp__xxz},), ({hbarf__vkxe},))
"""
        sqxb__jpug += '    if val in uniqs:\n'
        sqxb__jpug += '      out[i] = True\n'
        sqxb__jpug += '    else:\n'
        sqxb__jpug += '      out[i] = False\n'
        sqxb__jpug += '      uniqs[val] = 0\n'
    else:
        sqxb__jpug += '  data = data[0]\n'
        sqxb__jpug += '  hasna = False\n'
        sqxb__jpug += '  for i in range(n):\n'
        sqxb__jpug += '    if bodo.libs.array_kernels.isna(data, i):\n'
        sqxb__jpug += '      out[i] = hasna\n'
        sqxb__jpug += '      hasna = True\n'
        sqxb__jpug += '    else:\n'
        sqxb__jpug += '      val = data[i]\n'
        sqxb__jpug += '      if val in uniqs:\n'
        sqxb__jpug += '        out[i] = True\n'
        sqxb__jpug += '      else:\n'
        sqxb__jpug += '        out[i] = False\n'
        sqxb__jpug += '        uniqs[val] = 0\n'
    sqxb__jpug += '  if parallel:\n'
    sqxb__jpug += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    sqxb__jpug += '  return out\n'
    bvi__woat = {}
    exec(sqxb__jpug, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        bvi__woat)
    impl = bvi__woat['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    ljw__ghiz = len(data)
    sqxb__jpug = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    sqxb__jpug += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        ljw__ghiz)))
    sqxb__jpug += '  table_total = arr_info_list_to_table(info_list_total)\n'
    sqxb__jpug += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(ljw__ghiz))
    for uvj__gbcg in range(ljw__ghiz):
        sqxb__jpug += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(uvj__gbcg, uvj__gbcg, uvj__gbcg))
    sqxb__jpug += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(ljw__ghiz))
    sqxb__jpug += '  delete_table(out_table)\n'
    sqxb__jpug += '  delete_table(table_total)\n'
    sqxb__jpug += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(ljw__ghiz)))
    bvi__woat = {}
    exec(sqxb__jpug, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, bvi__woat)
    impl = bvi__woat['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    ljw__ghiz = len(data)
    sqxb__jpug = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    sqxb__jpug += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        ljw__ghiz)))
    sqxb__jpug += '  table_total = arr_info_list_to_table(info_list_total)\n'
    sqxb__jpug += '  keep_i = 0\n'
    sqxb__jpug += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for uvj__gbcg in range(ljw__ghiz):
        sqxb__jpug += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(uvj__gbcg, uvj__gbcg, uvj__gbcg))
    sqxb__jpug += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(ljw__ghiz))
    sqxb__jpug += '  delete_table(out_table)\n'
    sqxb__jpug += '  delete_table(table_total)\n'
    sqxb__jpug += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(ljw__ghiz)))
    bvi__woat = {}
    exec(sqxb__jpug, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, bvi__woat)
    impl = bvi__woat['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        gspr__pvyiy = [array_to_info(data_arr)]
        etx__mezwd = arr_info_list_to_table(gspr__pvyiy)
        woznl__uukp = 0
        uzbfu__vag = drop_duplicates_table(etx__mezwd, parallel, 1,
            woznl__uukp, False, True)
        ymd__jkcx = info_to_array(info_from_table(uzbfu__vag, 0), data_arr)
        delete_table(uzbfu__vag)
        delete_table(etx__mezwd)
        return ymd__jkcx
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    jhz__imnc = len(data.types)
    vjrt__dll = [('out' + str(i)) for i in range(jhz__imnc)]
    jtiv__maq = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    fcs__nfpc = ['isna(data[{}], i)'.format(i) for i in jtiv__maq]
    udjt__iggc = 'not ({})'.format(' or '.join(fcs__nfpc))
    if not is_overload_none(thresh):
        udjt__iggc = '(({}) <= ({}) - thresh)'.format(' + '.join(fcs__nfpc),
            jhz__imnc - 1)
    elif how == 'all':
        udjt__iggc = 'not ({})'.format(' and '.join(fcs__nfpc))
    sqxb__jpug = 'def _dropna_imp(data, how, thresh, subset):\n'
    sqxb__jpug += '  old_len = len(data[0])\n'
    sqxb__jpug += '  new_len = 0\n'
    sqxb__jpug += '  for i in range(old_len):\n'
    sqxb__jpug += '    if {}:\n'.format(udjt__iggc)
    sqxb__jpug += '      new_len += 1\n'
    for i, out in enumerate(vjrt__dll):
        if isinstance(data[i], bodo.CategoricalArrayType):
            sqxb__jpug += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            sqxb__jpug += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    sqxb__jpug += '  curr_ind = 0\n'
    sqxb__jpug += '  for i in range(old_len):\n'
    sqxb__jpug += '    if {}:\n'.format(udjt__iggc)
    for i in range(jhz__imnc):
        sqxb__jpug += '      if isna(data[{}], i):\n'.format(i)
        sqxb__jpug += '        setna({}, curr_ind)\n'.format(vjrt__dll[i])
        sqxb__jpug += '      else:\n'
        sqxb__jpug += '        {}[curr_ind] = data[{}][i]\n'.format(vjrt__dll
            [i], i)
    sqxb__jpug += '      curr_ind += 1\n'
    sqxb__jpug += '  return {}\n'.format(', '.join(vjrt__dll))
    bvi__woat = {}
    hbv__pzg = {'t{}'.format(i): xgor__edpq for i, xgor__edpq in enumerate(
        data.types)}
    hbv__pzg.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(sqxb__jpug, hbv__pzg, bvi__woat)
    siyfw__xsvel = bvi__woat['_dropna_imp']
    return siyfw__xsvel


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        ewuh__etugr = arr.dtype
        xfsz__vmm = ewuh__etugr.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            tcce__cksnp = init_nested_counts(xfsz__vmm)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                tcce__cksnp = add_nested_counts(tcce__cksnp, val[ind])
            ymd__jkcx = bodo.utils.utils.alloc_type(n, ewuh__etugr, tcce__cksnp
                )
            for lbb__acoxq in range(n):
                if bodo.libs.array_kernels.isna(arr, lbb__acoxq):
                    setna(ymd__jkcx, lbb__acoxq)
                    continue
                val = arr[lbb__acoxq]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(ymd__jkcx, lbb__acoxq)
                    continue
                ymd__jkcx[lbb__acoxq] = val[ind]
            return ymd__jkcx
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    yoio__tnov = _to_readonly(arr_types.types[0])
    return all(isinstance(xgor__edpq, CategoricalArrayType) and 
        _to_readonly(xgor__edpq) == yoio__tnov for xgor__edpq in arr_types.
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
        dxl__vgsmr = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            azcdv__ofal = 0
            oqgpv__icg = []
            for A in arr_list:
                mtlnu__agnjf = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                oqgpv__icg.append(bodo.libs.array_item_arr_ext.get_data(A))
                azcdv__ofal += mtlnu__agnjf
            jnxkr__orhuq = np.empty(azcdv__ofal + 1, offset_type)
            fknv__yyk = bodo.libs.array_kernels.concat(oqgpv__icg)
            dkxa__rwkop = np.empty(azcdv__ofal + 7 >> 3, np.uint8)
            zqe__gen = 0
            anuf__lbtsl = 0
            for A in arr_list:
                axiqo__mhl = bodo.libs.array_item_arr_ext.get_offsets(A)
                cok__tcgzk = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                mtlnu__agnjf = len(A)
                blm__jqir = axiqo__mhl[mtlnu__agnjf]
                for i in range(mtlnu__agnjf):
                    jnxkr__orhuq[i + zqe__gen] = axiqo__mhl[i] + anuf__lbtsl
                    pjh__qvb = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        cok__tcgzk, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(dkxa__rwkop, i +
                        zqe__gen, pjh__qvb)
                zqe__gen += mtlnu__agnjf
                anuf__lbtsl += blm__jqir
            jnxkr__orhuq[zqe__gen] = anuf__lbtsl
            ymd__jkcx = bodo.libs.array_item_arr_ext.init_array_item_array(
                azcdv__ofal, fknv__yyk, jnxkr__orhuq, dkxa__rwkop)
            return ymd__jkcx
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        dmda__pktf = arr_list.dtype.names
        sqxb__jpug = 'def struct_array_concat_impl(arr_list):\n'
        sqxb__jpug += f'    n_all = 0\n'
        for i in range(len(dmda__pktf)):
            sqxb__jpug += f'    concat_list{i} = []\n'
        sqxb__jpug += '    for A in arr_list:\n'
        sqxb__jpug += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(dmda__pktf)):
            sqxb__jpug += f'        concat_list{i}.append(data_tuple[{i}])\n'
        sqxb__jpug += '        n_all += len(A)\n'
        sqxb__jpug += '    n_bytes = (n_all + 7) >> 3\n'
        sqxb__jpug += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        sqxb__jpug += '    curr_bit = 0\n'
        sqxb__jpug += '    for A in arr_list:\n'
        sqxb__jpug += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        sqxb__jpug += '        for j in range(len(A)):\n'
        sqxb__jpug += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        sqxb__jpug += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        sqxb__jpug += '            curr_bit += 1\n'
        sqxb__jpug += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        wuf__qebcj = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(dmda__pktf))])
        sqxb__jpug += f'        ({wuf__qebcj},),\n'
        sqxb__jpug += '        new_mask,\n'
        sqxb__jpug += f'        {dmda__pktf},\n'
        sqxb__jpug += '    )\n'
        bvi__woat = {}
        exec(sqxb__jpug, {'bodo': bodo, 'np': np}, bvi__woat)
        return bvi__woat['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            movjt__algtz = 0
            for A in arr_list:
                movjt__algtz += len(A)
            xya__vqp = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(movjt__algtz))
            piira__ebg = 0
            for A in arr_list:
                for i in range(len(A)):
                    xya__vqp._data[i + piira__ebg] = A._data[i]
                    pjh__qvb = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(xya__vqp.
                        _null_bitmap, i + piira__ebg, pjh__qvb)
                piira__ebg += len(A)
            return xya__vqp
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            movjt__algtz = 0
            for A in arr_list:
                movjt__algtz += len(A)
            xya__vqp = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(movjt__algtz))
            piira__ebg = 0
            for A in arr_list:
                for i in range(len(A)):
                    xya__vqp._days_data[i + piira__ebg] = A._days_data[i]
                    xya__vqp._seconds_data[i + piira__ebg] = A._seconds_data[i]
                    xya__vqp._microseconds_data[i + piira__ebg
                        ] = A._microseconds_data[i]
                    pjh__qvb = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(xya__vqp.
                        _null_bitmap, i + piira__ebg, pjh__qvb)
                piira__ebg += len(A)
            return xya__vqp
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        syh__dvqnj = arr_list.dtype.precision
        bigup__ibpwe = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            movjt__algtz = 0
            for A in arr_list:
                movjt__algtz += len(A)
            xya__vqp = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                movjt__algtz, syh__dvqnj, bigup__ibpwe)
            piira__ebg = 0
            for A in arr_list:
                for i in range(len(A)):
                    xya__vqp._data[i + piira__ebg] = A._data[i]
                    pjh__qvb = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(xya__vqp.
                        _null_bitmap, i + piira__ebg, pjh__qvb)
                piira__ebg += len(A)
            return xya__vqp
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        xgor__edpq) for xgor__edpq in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            ogkh__cjm = arr_list.types[0]
        else:
            ogkh__cjm = arr_list.dtype
        ogkh__cjm = to_str_arr_if_dict_array(ogkh__cjm)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            bzzs__zefwt = 0
            htif__asrv = 0
            for A in arr_list:
                arr = A
                bzzs__zefwt += len(arr)
                htif__asrv += bodo.libs.str_arr_ext.num_total_chars(arr)
            ymd__jkcx = bodo.utils.utils.alloc_type(bzzs__zefwt, ogkh__cjm,
                (htif__asrv,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(ymd__jkcx, -1)
            emx__pcxo = 0
            wsdd__wcsvq = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(ymd__jkcx, arr,
                    emx__pcxo, wsdd__wcsvq)
                emx__pcxo += len(arr)
                wsdd__wcsvq += bodo.libs.str_arr_ext.num_total_chars(arr)
            return ymd__jkcx
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(xgor__edpq.dtype, types.Integer) for
        xgor__edpq in arr_list.types) and any(isinstance(xgor__edpq,
        IntegerArrayType) for xgor__edpq in arr_list.types):

        def impl_int_arr_list(arr_list):
            eyaa__jtxz = convert_to_nullable_tup(arr_list)
            mcum__oltq = []
            fbiw__vxn = 0
            for A in eyaa__jtxz:
                mcum__oltq.append(A._data)
                fbiw__vxn += len(A)
            fknv__yyk = bodo.libs.array_kernels.concat(mcum__oltq)
            ynuuu__pwaq = fbiw__vxn + 7 >> 3
            wyrth__yvght = np.empty(ynuuu__pwaq, np.uint8)
            mpvo__mzogr = 0
            for A in eyaa__jtxz:
                ibet__hvkxv = A._null_bitmap
                for lbb__acoxq in range(len(A)):
                    pjh__qvb = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ibet__hvkxv, lbb__acoxq)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wyrth__yvght,
                        mpvo__mzogr, pjh__qvb)
                    mpvo__mzogr += 1
            return bodo.libs.int_arr_ext.init_integer_array(fknv__yyk,
                wyrth__yvght)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(xgor__edpq.dtype == types.bool_ for xgor__edpq in
        arr_list.types) and any(xgor__edpq == boolean_array for xgor__edpq in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            eyaa__jtxz = convert_to_nullable_tup(arr_list)
            mcum__oltq = []
            fbiw__vxn = 0
            for A in eyaa__jtxz:
                mcum__oltq.append(A._data)
                fbiw__vxn += len(A)
            fknv__yyk = bodo.libs.array_kernels.concat(mcum__oltq)
            ynuuu__pwaq = fbiw__vxn + 7 >> 3
            wyrth__yvght = np.empty(ynuuu__pwaq, np.uint8)
            mpvo__mzogr = 0
            for A in eyaa__jtxz:
                ibet__hvkxv = A._null_bitmap
                for lbb__acoxq in range(len(A)):
                    pjh__qvb = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ibet__hvkxv, lbb__acoxq)
                    bodo.libs.int_arr_ext.set_bit_to_arr(wyrth__yvght,
                        mpvo__mzogr, pjh__qvb)
                    mpvo__mzogr += 1
            return bodo.libs.bool_arr_ext.init_bool_array(fknv__yyk,
                wyrth__yvght)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            lsm__durlk = []
            for A in arr_list:
                lsm__durlk.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                lsm__durlk), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        jfi__mfdjk = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        sqxb__jpug = 'def impl(arr_list):\n'
        sqxb__jpug += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({jfi__mfdjk},)), arr_list[0].dtype)
"""
        uvyy__zcq = {}
        exec(sqxb__jpug, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, uvyy__zcq)
        return uvyy__zcq['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            fbiw__vxn = 0
            for A in arr_list:
                fbiw__vxn += len(A)
            ymd__jkcx = np.empty(fbiw__vxn, dtype)
            murrq__xpap = 0
            for A in arr_list:
                n = len(A)
                ymd__jkcx[murrq__xpap:murrq__xpap + n] = A
                murrq__xpap += n
            return ymd__jkcx
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(xgor__edpq,
        (types.Array, IntegerArrayType)) and isinstance(xgor__edpq.dtype,
        types.Integer) for xgor__edpq in arr_list.types) and any(isinstance
        (xgor__edpq, types.Array) and isinstance(xgor__edpq.dtype, types.
        Float) for xgor__edpq in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            yslly__bhvmn = []
            for A in arr_list:
                yslly__bhvmn.append(A._data)
            rrsae__zsf = bodo.libs.array_kernels.concat(yslly__bhvmn)
            rsuu__qoxeb = bodo.libs.map_arr_ext.init_map_arr(rrsae__zsf)
            return rsuu__qoxeb
        return impl_map_arr_list
    for byxrk__mtyh in arr_list:
        if not isinstance(byxrk__mtyh, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(xgor__edpq.astype(np.float64) for xgor__edpq in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    ljw__ghiz = len(arr_tup.types)
    sqxb__jpug = 'def f(arr_tup):\n'
    sqxb__jpug += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(ljw__ghiz
        )), ',' if ljw__ghiz == 1 else '')
    bvi__woat = {}
    exec(sqxb__jpug, {'np': np}, bvi__woat)
    reql__zrfe = bvi__woat['f']
    return reql__zrfe


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    ljw__ghiz = len(arr_tup.types)
    lsim__hvlaz = find_common_np_dtype(arr_tup.types)
    xfsz__vmm = None
    wohz__wws = ''
    if isinstance(lsim__hvlaz, types.Integer):
        xfsz__vmm = bodo.libs.int_arr_ext.IntDtype(lsim__hvlaz)
        wohz__wws = '.astype(out_dtype, False)'
    sqxb__jpug = 'def f(arr_tup):\n'
    sqxb__jpug += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, wohz__wws) for i in range(ljw__ghiz)), ',' if ljw__ghiz ==
        1 else '')
    bvi__woat = {}
    exec(sqxb__jpug, {'bodo': bodo, 'out_dtype': xfsz__vmm}, bvi__woat)
    ekdf__anz = bvi__woat['f']
    return ekdf__anz


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, zajfu__cmgn = build_set_seen_na(A)
        return len(s) + int(not dropna and zajfu__cmgn)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        zkbix__akkjj = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        xgv__gbigl = len(zkbix__akkjj)
        return bodo.libs.distributed_api.dist_reduce(xgv__gbigl, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([rolm__axcc for rolm__axcc in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        tde__gokja = np.finfo(A.dtype(1).dtype).max
    else:
        tde__gokja = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        ymd__jkcx = np.empty(n, A.dtype)
        xzae__ijo = tde__gokja
        for i in range(n):
            xzae__ijo = min(xzae__ijo, A[i])
            ymd__jkcx[i] = xzae__ijo
        return ymd__jkcx
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        tde__gokja = np.finfo(A.dtype(1).dtype).min
    else:
        tde__gokja = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        ymd__jkcx = np.empty(n, A.dtype)
        xzae__ijo = tde__gokja
        for i in range(n):
            xzae__ijo = max(xzae__ijo, A[i])
            ymd__jkcx[i] = xzae__ijo
        return ymd__jkcx
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        lhqib__ncy = arr_info_list_to_table([array_to_info(A)])
        fdd__zjlhf = 1
        woznl__uukp = 0
        uzbfu__vag = drop_duplicates_table(lhqib__ncy, parallel, fdd__zjlhf,
            woznl__uukp, dropna, True)
        ymd__jkcx = info_to_array(info_from_table(uzbfu__vag, 0), A)
        delete_table(lhqib__ncy)
        delete_table(uzbfu__vag)
        return ymd__jkcx
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    dxl__vgsmr = bodo.utils.typing.to_nullable_type(arr.dtype)
    mjqql__zwdc = index_arr
    vni__rxd = mjqql__zwdc.dtype

    def impl(arr, index_arr):
        n = len(arr)
        tcce__cksnp = init_nested_counts(dxl__vgsmr)
        pdya__jvbar = init_nested_counts(vni__rxd)
        for i in range(n):
            snu__exh = index_arr[i]
            if isna(arr, i):
                tcce__cksnp = (tcce__cksnp[0] + 1,) + tcce__cksnp[1:]
                pdya__jvbar = add_nested_counts(pdya__jvbar, snu__exh)
                continue
            zku__yfza = arr[i]
            if len(zku__yfza) == 0:
                tcce__cksnp = (tcce__cksnp[0] + 1,) + tcce__cksnp[1:]
                pdya__jvbar = add_nested_counts(pdya__jvbar, snu__exh)
                continue
            tcce__cksnp = add_nested_counts(tcce__cksnp, zku__yfza)
            for rdsoc__hgsel in range(len(zku__yfza)):
                pdya__jvbar = add_nested_counts(pdya__jvbar, snu__exh)
        ymd__jkcx = bodo.utils.utils.alloc_type(tcce__cksnp[0], dxl__vgsmr,
            tcce__cksnp[1:])
        ttwbj__ctl = bodo.utils.utils.alloc_type(tcce__cksnp[0],
            mjqql__zwdc, pdya__jvbar)
        anuf__lbtsl = 0
        for i in range(n):
            if isna(arr, i):
                setna(ymd__jkcx, anuf__lbtsl)
                ttwbj__ctl[anuf__lbtsl] = index_arr[i]
                anuf__lbtsl += 1
                continue
            zku__yfza = arr[i]
            blm__jqir = len(zku__yfza)
            if blm__jqir == 0:
                setna(ymd__jkcx, anuf__lbtsl)
                ttwbj__ctl[anuf__lbtsl] = index_arr[i]
                anuf__lbtsl += 1
                continue
            ymd__jkcx[anuf__lbtsl:anuf__lbtsl + blm__jqir] = zku__yfza
            ttwbj__ctl[anuf__lbtsl:anuf__lbtsl + blm__jqir] = index_arr[i]
            anuf__lbtsl += blm__jqir
        return ymd__jkcx, ttwbj__ctl
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    dxl__vgsmr = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        tcce__cksnp = init_nested_counts(dxl__vgsmr)
        for i in range(n):
            if isna(arr, i):
                tcce__cksnp = (tcce__cksnp[0] + 1,) + tcce__cksnp[1:]
                zswcj__zsn = 1
            else:
                zku__yfza = arr[i]
                cgao__adpqm = len(zku__yfza)
                if cgao__adpqm == 0:
                    tcce__cksnp = (tcce__cksnp[0] + 1,) + tcce__cksnp[1:]
                    zswcj__zsn = 1
                    continue
                else:
                    tcce__cksnp = add_nested_counts(tcce__cksnp, zku__yfza)
                    zswcj__zsn = cgao__adpqm
            if counts[i] != zswcj__zsn:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        ymd__jkcx = bodo.utils.utils.alloc_type(tcce__cksnp[0], dxl__vgsmr,
            tcce__cksnp[1:])
        anuf__lbtsl = 0
        for i in range(n):
            if isna(arr, i):
                setna(ymd__jkcx, anuf__lbtsl)
                anuf__lbtsl += 1
                continue
            zku__yfza = arr[i]
            blm__jqir = len(zku__yfza)
            if blm__jqir == 0:
                setna(ymd__jkcx, anuf__lbtsl)
                anuf__lbtsl += 1
                continue
            ymd__jkcx[anuf__lbtsl:anuf__lbtsl + blm__jqir] = zku__yfza
            anuf__lbtsl += blm__jqir
        return ymd__jkcx
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(wcuv__ohfcg) for wcuv__ohfcg in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        fgy__nvl = 'np.empty(n, np.int64)'
        ftagu__fpslt = 'out_arr[i] = 1'
        cjti__yabac = 'max(len(arr[i]), 1)'
    else:
        fgy__nvl = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        ftagu__fpslt = 'bodo.libs.array_kernels.setna(out_arr, i)'
        cjti__yabac = 'len(arr[i])'
    sqxb__jpug = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {fgy__nvl}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {ftagu__fpslt}
        else:
            out_arr[i] = {cjti__yabac}
    return out_arr
    """
    bvi__woat = {}
    exec(sqxb__jpug, {'bodo': bodo, 'numba': numba, 'np': np}, bvi__woat)
    impl = bvi__woat['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    mjqql__zwdc = index_arr
    vni__rxd = mjqql__zwdc.dtype

    def impl(arr, pat, n, index_arr):
        wyhhs__ovd = pat is not None and len(pat) > 1
        if wyhhs__ovd:
            hyu__cit = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        hhm__arqmi = len(arr)
        bzzs__zefwt = 0
        htif__asrv = 0
        pdya__jvbar = init_nested_counts(vni__rxd)
        for i in range(hhm__arqmi):
            snu__exh = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                bzzs__zefwt += 1
                pdya__jvbar = add_nested_counts(pdya__jvbar, snu__exh)
                continue
            if wyhhs__ovd:
                zjkl__jlt = hyu__cit.split(arr[i], maxsplit=n)
            else:
                zjkl__jlt = arr[i].split(pat, n)
            bzzs__zefwt += len(zjkl__jlt)
            for s in zjkl__jlt:
                pdya__jvbar = add_nested_counts(pdya__jvbar, snu__exh)
                htif__asrv += bodo.libs.str_arr_ext.get_utf8_size(s)
        ymd__jkcx = bodo.libs.str_arr_ext.pre_alloc_string_array(bzzs__zefwt,
            htif__asrv)
        ttwbj__ctl = bodo.utils.utils.alloc_type(bzzs__zefwt, mjqql__zwdc,
            pdya__jvbar)
        jbiku__uci = 0
        for lbb__acoxq in range(hhm__arqmi):
            if isna(arr, lbb__acoxq):
                ymd__jkcx[jbiku__uci] = ''
                bodo.libs.array_kernels.setna(ymd__jkcx, jbiku__uci)
                ttwbj__ctl[jbiku__uci] = index_arr[lbb__acoxq]
                jbiku__uci += 1
                continue
            if wyhhs__ovd:
                zjkl__jlt = hyu__cit.split(arr[lbb__acoxq], maxsplit=n)
            else:
                zjkl__jlt = arr[lbb__acoxq].split(pat, n)
            yocg__nuq = len(zjkl__jlt)
            ymd__jkcx[jbiku__uci:jbiku__uci + yocg__nuq] = zjkl__jlt
            ttwbj__ctl[jbiku__uci:jbiku__uci + yocg__nuq] = index_arr[
                lbb__acoxq]
            jbiku__uci += yocg__nuq
        return ymd__jkcx, ttwbj__ctl
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
            ymd__jkcx = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                ymd__jkcx[i] = np.nan
            return ymd__jkcx
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            qyn__tshg = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            kuq__rnvj = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(kuq__rnvj, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(qyn__tshg,
                kuq__rnvj, True)
        return impl_dict
    wvd__vdz = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        ymd__jkcx = bodo.utils.utils.alloc_type(n, wvd__vdz, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(ymd__jkcx, i)
        return ymd__jkcx
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
    tsq__volor = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            ymd__jkcx = bodo.utils.utils.alloc_type(new_len, tsq__volor)
            bodo.libs.str_arr_ext.str_copy_ptr(ymd__jkcx.ctypes, 0, A.
                ctypes, old_size)
            return ymd__jkcx
        return impl_char

    def impl(A, old_size, new_len):
        ymd__jkcx = bodo.utils.utils.alloc_type(new_len, tsq__volor, (-1,))
        ymd__jkcx[:old_size] = A[:old_size]
        return ymd__jkcx
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    gjdgm__zii = math.ceil((stop - start) / step)
    return int(max(gjdgm__zii, 0))


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
    if any(isinstance(rolm__axcc, types.Complex) for rolm__axcc in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            obe__otkf = (stop - start) / step
            gjdgm__zii = math.ceil(obe__otkf.real)
            mrokg__yaahr = math.ceil(obe__otkf.imag)
            lwo__mwamn = int(max(min(mrokg__yaahr, gjdgm__zii), 0))
            arr = np.empty(lwo__mwamn, dtype)
            for i in numba.parfors.parfor.internal_prange(lwo__mwamn):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            lwo__mwamn = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(lwo__mwamn, dtype)
            for i in numba.parfors.parfor.internal_prange(lwo__mwamn):
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
        gfr__txhnq = arr,
        if not inplace:
            gfr__txhnq = arr.copy(),
        upw__tmyfw = bodo.libs.str_arr_ext.to_list_if_immutable_arr(gfr__txhnq)
        idp__uke = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(upw__tmyfw, 0, n, idp__uke)
        if not ascending:
            bodo.libs.timsort.reverseRange(upw__tmyfw, 0, n, idp__uke)
        bodo.libs.str_arr_ext.cp_str_list_to_array(gfr__txhnq, upw__tmyfw)
        return gfr__txhnq[0]
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
        rsuu__qoxeb = []
        for i in range(n):
            if A[i]:
                rsuu__qoxeb.append(i + offset)
        return np.array(rsuu__qoxeb, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    tsq__volor = element_type(A)
    if tsq__volor == types.unicode_type:
        null_value = '""'
    elif tsq__volor == types.bool_:
        null_value = 'False'
    elif tsq__volor == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif tsq__volor == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    jbiku__uci = 'i'
    ipv__mlt = False
    lsow__mypwt = get_overload_const_str(method)
    if lsow__mypwt in ('ffill', 'pad'):
        kfw__lpviu = 'n'
        send_right = True
    elif lsow__mypwt in ('backfill', 'bfill'):
        kfw__lpviu = 'n-1, -1, -1'
        send_right = False
        if tsq__volor == types.unicode_type:
            jbiku__uci = '(n - 1) - i'
            ipv__mlt = True
    sqxb__jpug = 'def impl(A, method, parallel=False):\n'
    sqxb__jpug += '  A = decode_if_dict_array(A)\n'
    sqxb__jpug += '  has_last_value = False\n'
    sqxb__jpug += f'  last_value = {null_value}\n'
    sqxb__jpug += '  if parallel:\n'
    sqxb__jpug += '    rank = bodo.libs.distributed_api.get_rank()\n'
    sqxb__jpug += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    sqxb__jpug += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    sqxb__jpug += '  n = len(A)\n'
    sqxb__jpug += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    sqxb__jpug += f'  for i in range({kfw__lpviu}):\n'
    sqxb__jpug += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    sqxb__jpug += (
        f'      bodo.libs.array_kernels.setna(out_arr, {jbiku__uci})\n')
    sqxb__jpug += '      continue\n'
    sqxb__jpug += '    s = A[i]\n'
    sqxb__jpug += '    if bodo.libs.array_kernels.isna(A, i):\n'
    sqxb__jpug += '      s = last_value\n'
    sqxb__jpug += f'    out_arr[{jbiku__uci}] = s\n'
    sqxb__jpug += '    last_value = s\n'
    sqxb__jpug += '    has_last_value = True\n'
    if ipv__mlt:
        sqxb__jpug += '  return out_arr[::-1]\n'
    else:
        sqxb__jpug += '  return out_arr\n'
    zrx__uqgm = {}
    exec(sqxb__jpug, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, zrx__uqgm)
    impl = zrx__uqgm['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        zrzgg__onmsc = 0
        urqip__hzeuc = n_pes - 1
        rhax__repcw = np.int32(rank + 1)
        vnj__mvlsn = np.int32(rank - 1)
        hqr__jsq = len(in_arr) - 1
        xfzl__rjnl = -1
        fdmrn__orft = -1
    else:
        zrzgg__onmsc = n_pes - 1
        urqip__hzeuc = 0
        rhax__repcw = np.int32(rank - 1)
        vnj__mvlsn = np.int32(rank + 1)
        hqr__jsq = 0
        xfzl__rjnl = len(in_arr)
        fdmrn__orft = 1
    mcw__nywag = np.int32(bodo.hiframes.rolling.comm_border_tag)
    jpcat__ylsd = np.empty(1, dtype=np.bool_)
    sigcn__wxh = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    zfpid__xiego = np.empty(1, dtype=np.bool_)
    tggp__walp = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    dwh__haeej = False
    pdgw__sws = null_value
    for i in range(hqr__jsq, xfzl__rjnl, fdmrn__orft):
        if not isna(in_arr, i):
            dwh__haeej = True
            pdgw__sws = in_arr[i]
            break
    if rank != zrzgg__onmsc:
        xtoil__wxgq = bodo.libs.distributed_api.irecv(jpcat__ylsd, 1,
            vnj__mvlsn, mcw__nywag, True)
        bodo.libs.distributed_api.wait(xtoil__wxgq, True)
        ibvl__fvx = bodo.libs.distributed_api.irecv(sigcn__wxh, 1,
            vnj__mvlsn, mcw__nywag, True)
        bodo.libs.distributed_api.wait(ibvl__fvx, True)
        gmwf__wnrw = jpcat__ylsd[0]
        tfn__glb = sigcn__wxh[0]
    else:
        gmwf__wnrw = False
        tfn__glb = null_value
    if dwh__haeej:
        zfpid__xiego[0] = dwh__haeej
        tggp__walp[0] = pdgw__sws
    else:
        zfpid__xiego[0] = gmwf__wnrw
        tggp__walp[0] = tfn__glb
    if rank != urqip__hzeuc:
        qar__bnuri = bodo.libs.distributed_api.isend(zfpid__xiego, 1,
            rhax__repcw, mcw__nywag, True)
        aaw__bkgho = bodo.libs.distributed_api.isend(tggp__walp, 1,
            rhax__repcw, mcw__nywag, True)
    return gmwf__wnrw, tfn__glb


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    msb__qvr = {'axis': axis, 'kind': kind, 'order': order}
    bhgwk__lhd = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', msb__qvr, bhgwk__lhd, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    tsq__volor = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            hhm__arqmi = len(A)
            ymd__jkcx = bodo.utils.utils.alloc_type(hhm__arqmi * repeats,
                tsq__volor, (-1,))
            for i in range(hhm__arqmi):
                jbiku__uci = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for lbb__acoxq in range(repeats):
                        bodo.libs.array_kernels.setna(ymd__jkcx, jbiku__uci +
                            lbb__acoxq)
                else:
                    ymd__jkcx[jbiku__uci:jbiku__uci + repeats] = A[i]
            return ymd__jkcx
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        hhm__arqmi = len(A)
        ymd__jkcx = bodo.utils.utils.alloc_type(repeats.sum(), tsq__volor,
            (-1,))
        jbiku__uci = 0
        for i in range(hhm__arqmi):
            bckl__igetm = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for lbb__acoxq in range(bckl__igetm):
                    bodo.libs.array_kernels.setna(ymd__jkcx, jbiku__uci +
                        lbb__acoxq)
            else:
                ymd__jkcx[jbiku__uci:jbiku__uci + bckl__igetm] = A[i]
            jbiku__uci += bckl__igetm
        return ymd__jkcx
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
        ldwgh__ypj = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(ldwgh__ypj, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        ytajc__itsx = bodo.libs.array_kernels.concat([A1, A2])
        dnfh__yqn = bodo.libs.array_kernels.unique(ytajc__itsx)
        return pd.Series(dnfh__yqn).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    msb__qvr = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    bhgwk__lhd = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', msb__qvr, bhgwk__lhd, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        gxhqq__bqp = bodo.libs.array_kernels.unique(A1)
        ricfv__avitf = bodo.libs.array_kernels.unique(A2)
        ytajc__itsx = bodo.libs.array_kernels.concat([gxhqq__bqp, ricfv__avitf]
            )
        edx__gsysx = pd.Series(ytajc__itsx).sort_values().values
        return slice_array_intersect1d(edx__gsysx)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    byozf__hwh = arr[1:] == arr[:-1]
    return arr[:-1][byozf__hwh]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    mcw__nywag = np.int32(bodo.hiframes.rolling.comm_border_tag)
    wjdo__lrij = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        oiaah__eeqb = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), mcw__nywag, True)
        bodo.libs.distributed_api.wait(oiaah__eeqb, True)
    if rank == n_pes - 1:
        return None
    else:
        owpd__rxh = bodo.libs.distributed_api.irecv(wjdo__lrij, 1, np.int32
            (rank + 1), mcw__nywag, True)
        bodo.libs.distributed_api.wait(owpd__rxh, True)
        return wjdo__lrij[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    byozf__hwh = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            byozf__hwh[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        ygbb__pdhhg = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == ygbb__pdhhg:
            byozf__hwh[n - 1] = True
    return byozf__hwh


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    msb__qvr = {'assume_unique': assume_unique}
    bhgwk__lhd = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', msb__qvr, bhgwk__lhd, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        gxhqq__bqp = bodo.libs.array_kernels.unique(A1)
        ricfv__avitf = bodo.libs.array_kernels.unique(A2)
        byozf__hwh = calculate_mask_setdiff1d(gxhqq__bqp, ricfv__avitf)
        return pd.Series(gxhqq__bqp[byozf__hwh]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    byozf__hwh = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        byozf__hwh &= A1 != A2[i]
    return byozf__hwh


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    msb__qvr = {'retstep': retstep, 'axis': axis}
    bhgwk__lhd = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', msb__qvr, bhgwk__lhd, 'numpy')
    eox__jkm = False
    if is_overload_none(dtype):
        tsq__volor = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            eox__jkm = True
        tsq__volor = numba.np.numpy_support.as_dtype(dtype).type
    if eox__jkm:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            xih__bsjyi = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            ymd__jkcx = np.empty(num, tsq__volor)
            for i in numba.parfors.parfor.internal_prange(num):
                ymd__jkcx[i] = tsq__volor(np.floor(start + i * xih__bsjyi))
            return ymd__jkcx
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            xih__bsjyi = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            ymd__jkcx = np.empty(num, tsq__volor)
            for i in numba.parfors.parfor.internal_prange(num):
                ymd__jkcx[i] = tsq__volor(start + i * xih__bsjyi)
            return ymd__jkcx
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
        ljw__ghiz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                ljw__ghiz += A[i] == val
        return ljw__ghiz > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    msb__qvr = {'axis': axis, 'out': out, 'keepdims': keepdims}
    bhgwk__lhd = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', msb__qvr, bhgwk__lhd, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        ljw__ghiz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                ljw__ghiz += int(bool(A[i]))
        return ljw__ghiz > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    msb__qvr = {'axis': axis, 'out': out, 'keepdims': keepdims}
    bhgwk__lhd = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', msb__qvr, bhgwk__lhd, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        ljw__ghiz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                ljw__ghiz += int(bool(A[i]))
        return ljw__ghiz == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    msb__qvr = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    bhgwk__lhd = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', msb__qvr, bhgwk__lhd, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        fsd__bcjbs = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            ymd__jkcx = np.empty(n, fsd__bcjbs)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(ymd__jkcx, i)
                    continue
                ymd__jkcx[i] = np_cbrt_scalar(A[i], fsd__bcjbs)
            return ymd__jkcx
        return impl_arr
    fsd__bcjbs = np.promote_types(numba.np.numpy_support.as_dtype(A), numba
        .np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, fsd__bcjbs)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    itu__trsaq = x < 0
    if itu__trsaq:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if itu__trsaq:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    gxr__atrk = isinstance(tup, (types.BaseTuple, types.List))
    rkenn__pfor = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for byxrk__mtyh in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                byxrk__mtyh, 'numpy.hstack()')
            gxr__atrk = gxr__atrk and bodo.utils.utils.is_array_typ(byxrk__mtyh
                , False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        gxr__atrk = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif rkenn__pfor:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        limrc__vrcxz = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for byxrk__mtyh in limrc__vrcxz.types:
            rkenn__pfor = rkenn__pfor and bodo.utils.utils.is_array_typ(
                byxrk__mtyh, False)
    if not (gxr__atrk or rkenn__pfor):
        return
    if rkenn__pfor:

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
    msb__qvr = {'check_valid': check_valid, 'tol': tol}
    bhgwk__lhd = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', msb__qvr,
        bhgwk__lhd, 'numpy')
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
        cwamk__ktdr = mean.shape[0]
        wmcyz__dyr = size, cwamk__ktdr
        euuhd__ixfdu = np.random.standard_normal(wmcyz__dyr)
        cov = cov.astype(np.float64)
        cpoca__atpa, s, qnjl__gmahe = np.linalg.svd(cov)
        res = np.dot(euuhd__ixfdu, np.sqrt(s).reshape(cwamk__ktdr, 1) *
            qnjl__gmahe)
        pbi__qidf = res + mean
        return pbi__qidf
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
            bvuy__mmg = bodo.hiframes.series_kernels._get_type_max_value(arr)
            qrxho__vim = typing.builtins.IndexValue(-1, bvuy__mmg)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                xcolz__nrd = typing.builtins.IndexValue(i, arr[i])
                qrxho__vim = min(qrxho__vim, xcolz__nrd)
            return qrxho__vim.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        zwmmz__xkpfp = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def impl_cat_arr(arr):
            chad__ybxx = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            bvuy__mmg = zwmmz__xkpfp(len(arr.dtype.categories) + 1)
            qrxho__vim = typing.builtins.IndexValue(-1, bvuy__mmg)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                xcolz__nrd = typing.builtins.IndexValue(i, chad__ybxx[i])
                qrxho__vim = min(qrxho__vim, xcolz__nrd)
            return qrxho__vim.index
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
            bvuy__mmg = bodo.hiframes.series_kernels._get_type_min_value(arr)
            qrxho__vim = typing.builtins.IndexValue(-1, bvuy__mmg)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                xcolz__nrd = typing.builtins.IndexValue(i, arr[i])
                qrxho__vim = max(qrxho__vim, xcolz__nrd)
            return qrxho__vim.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        zwmmz__xkpfp = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def impl_cat_arr(arr):
            n = len(arr)
            chad__ybxx = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            bvuy__mmg = zwmmz__xkpfp(-1)
            qrxho__vim = typing.builtins.IndexValue(-1, bvuy__mmg)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                xcolz__nrd = typing.builtins.IndexValue(i, chad__ybxx[i])
                qrxho__vim = max(qrxho__vim, xcolz__nrd)
            return qrxho__vim.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
