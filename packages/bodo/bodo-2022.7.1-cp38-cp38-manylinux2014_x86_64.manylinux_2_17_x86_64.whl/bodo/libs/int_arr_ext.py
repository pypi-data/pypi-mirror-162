"""Nullable integer array corresponding to Pandas IntegerArray.
However, nulls are stored in bit arrays similar to Arrow's arrays.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.str_arr_ext import kBitmask
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('mask_arr_to_bitmap', hstr_ext.mask_arr_to_bitmap)
ll.add_symbol('is_pd_int_array', array_ext.is_pd_int_array)
ll.add_symbol('int_array_from_sequence', array_ext.int_array_from_sequence)
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, check_unsupported_args, is_iterable_type, is_list_like_index_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error, to_nullable_type


class IntegerArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(IntegerArrayType, self).__init__(name=
            f'IntegerArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntegerArrayType(self.dtype)

    @property
    def get_pandas_scalar_type_instance(self):
        wim__pwucf = int(np.log2(self.dtype.bitwidth // 8))
        bektc__mlf = 0 if self.dtype.signed else 4
        idx = wim__pwucf + bektc__mlf
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        arf__saqy = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, arf__saqy)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    nsa__xmc = 8 * val.dtype.itemsize
    dkov__nsep = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(dkov__nsep, nsa__xmc))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        ngzkh__iqn = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(ngzkh__iqn)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    tzgxq__feln = c.context.insert_const_string(c.builder.module, 'pandas')
    owr__qyai = c.pyapi.import_module_noblock(tzgxq__feln)
    khwbd__sjanz = c.pyapi.call_method(owr__qyai, str(typ)[:-2], ())
    c.pyapi.decref(owr__qyai)
    return khwbd__sjanz


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    nsa__xmc = 8 * val.itemsize
    dkov__nsep = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(dkov__nsep, nsa__xmc))
    return IntDtype(dtype)


def _register_int_dtype(t):
    typeof_impl.register(t)(typeof_pd_int_dtype)
    int_dtype = typeof_pd_int_dtype(t(), None)
    type_callable(t)(lambda c: lambda : int_dtype)
    lower_builtin(t)(lambda c, b, s, a: c.get_dummy_value())


pd_int_dtype_classes = (pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.
    Int64Dtype, pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype)
for t in pd_int_dtype_classes:
    _register_int_dtype(t)


@numba.extending.register_jitable
def mask_arr_to_bitmap(mask_arr):
    n = len(mask_arr)
    tqb__xjvr = n + 7 >> 3
    ravv__oeh = np.empty(tqb__xjvr, np.uint8)
    for i in range(n):
        xjvwi__lrfp = i // 8
        ravv__oeh[xjvwi__lrfp] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            ravv__oeh[xjvwi__lrfp]) & kBitmask[i % 8]
    return ravv__oeh


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    kcfe__ieef = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(kcfe__ieef)
    c.pyapi.decref(kcfe__ieef)
    huurc__jlvlk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tqb__xjvr = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    suyp__mcy = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [tqb__xjvr])
    bpyhf__hkkx = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    ssnv__hih = cgutils.get_or_insert_function(c.builder.module,
        bpyhf__hkkx, name='is_pd_int_array')
    qmpys__vdm = c.builder.call(ssnv__hih, [obj])
    qgx__gei = c.builder.icmp_unsigned('!=', qmpys__vdm, qmpys__vdm.type(0))
    with c.builder.if_else(qgx__gei) as (ydr__euj, yxp__cyv):
        with ydr__euj:
            puzo__ots = c.pyapi.object_getattr_string(obj, '_data')
            huurc__jlvlk.data = c.pyapi.to_native_value(types.Array(typ.
                dtype, 1, 'C'), puzo__ots).value
            lgbj__csarm = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), lgbj__csarm).value
            c.pyapi.decref(puzo__ots)
            c.pyapi.decref(lgbj__csarm)
            oyw__shds = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, mask_arr)
            bpyhf__hkkx = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            ssnv__hih = cgutils.get_or_insert_function(c.builder.module,
                bpyhf__hkkx, name='mask_arr_to_bitmap')
            c.builder.call(ssnv__hih, [suyp__mcy.data, oyw__shds.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with yxp__cyv:
            ohfm__zthfh = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            bpyhf__hkkx = lir.FunctionType(lir.IntType(32), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            yrt__bzvkh = cgutils.get_or_insert_function(c.builder.module,
                bpyhf__hkkx, name='int_array_from_sequence')
            c.builder.call(yrt__bzvkh, [obj, c.builder.bitcast(ohfm__zthfh.
                data, lir.IntType(8).as_pointer()), suyp__mcy.data])
            huurc__jlvlk.data = ohfm__zthfh._getvalue()
    huurc__jlvlk.null_bitmap = suyp__mcy._getvalue()
    kuhal__irj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(huurc__jlvlk._getvalue(), is_error=kuhal__irj)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    huurc__jlvlk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        huurc__jlvlk.data, c.env_manager)
    his__lhpxw = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, huurc__jlvlk.null_bitmap).data
    kcfe__ieef = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(kcfe__ieef)
    tzgxq__feln = c.context.insert_const_string(c.builder.module, 'numpy')
    aciru__vrh = c.pyapi.import_module_noblock(tzgxq__feln)
    ixn__jdld = c.pyapi.object_getattr_string(aciru__vrh, 'bool_')
    mask_arr = c.pyapi.call_method(aciru__vrh, 'empty', (kcfe__ieef, ixn__jdld)
        )
    qkxy__bip = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    lpz__iugy = c.pyapi.object_getattr_string(qkxy__bip, 'data')
    odcmp__mwr = c.builder.inttoptr(c.pyapi.long_as_longlong(lpz__iugy),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as shh__ztbk:
        i = shh__ztbk.index
        rddw__lquai = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        omqqa__pbg = c.builder.load(cgutils.gep(c.builder, his__lhpxw,
            rddw__lquai))
        uuk__wnqpn = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(omqqa__pbg, uuk__wnqpn), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        eetw__ilr = cgutils.gep(c.builder, odcmp__mwr, i)
        c.builder.store(val, eetw__ilr)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        huurc__jlvlk.null_bitmap)
    tzgxq__feln = c.context.insert_const_string(c.builder.module, 'pandas')
    owr__qyai = c.pyapi.import_module_noblock(tzgxq__feln)
    txdz__ysyqo = c.pyapi.object_getattr_string(owr__qyai, 'arrays')
    khwbd__sjanz = c.pyapi.call_method(txdz__ysyqo, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(owr__qyai)
    c.pyapi.decref(kcfe__ieef)
    c.pyapi.decref(aciru__vrh)
    c.pyapi.decref(ixn__jdld)
    c.pyapi.decref(qkxy__bip)
    c.pyapi.decref(lpz__iugy)
    c.pyapi.decref(txdz__ysyqo)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return khwbd__sjanz


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        wvkx__qkuo, zibq__kkwv = args
        huurc__jlvlk = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        huurc__jlvlk.data = wvkx__qkuo
        huurc__jlvlk.null_bitmap = zibq__kkwv
        context.nrt.incref(builder, signature.args[0], wvkx__qkuo)
        context.nrt.incref(builder, signature.args[1], zibq__kkwv)
        return huurc__jlvlk._getvalue()
    xlah__zjewc = IntegerArrayType(data.dtype)
    ifipt__rsslv = xlah__zjewc(data, null_bitmap)
    return ifipt__rsslv, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    ibsy__tszax = np.empty(n, pyval.dtype.type)
    rll__vwk = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        axijs__elk = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(rll__vwk, i, int(not axijs__elk))
        if not axijs__elk:
            ibsy__tszax[i] = s
    zvn__kuvdt = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), ibsy__tszax)
    xru__kwkc = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), rll__vwk)
    return lir.Constant.literal_struct([zvn__kuvdt, xru__kwkc])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    nxmy__xzd = args[0]
    if equiv_set.has_shape(nxmy__xzd):
        return ArrayAnalysis.AnalyzeResult(shape=nxmy__xzd, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    nxmy__xzd = args[0]
    if equiv_set.has_shape(nxmy__xzd):
        return ArrayAnalysis.AnalyzeResult(shape=nxmy__xzd, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_init_integer_array = (
    init_integer_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_integer_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_integer_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_integer_array
numba.core.ir_utils.alias_func_extensions['get_int_arr_data',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_int_arr_bitmap',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_int_array(n, dtype):
    ibsy__tszax = np.empty(n, dtype)
    aekz__oirzs = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(ibsy__tszax, aekz__oirzs)


def alloc_int_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_alloc_int_array = (
    alloc_int_array_equiv)


@numba.extending.register_jitable
def set_bit_to_arr(bits, i, bit_is_set):
    bits[i // 8] ^= np.uint8(-np.uint8(bit_is_set) ^ bits[i // 8]) & kBitmask[
        i % 8]


@numba.extending.register_jitable
def get_bit_bitmap_arr(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@overload(operator.getitem, no_unliteral=True)
def int_arr_getitem(A, ind):
    if not isinstance(A, IntegerArrayType):
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            wrtr__ustno, mlm__vfxh = array_getitem_bool_index(A, ind)
            return init_integer_array(wrtr__ustno, mlm__vfxh)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            wrtr__ustno, mlm__vfxh = array_getitem_int_index(A, ind)
            return init_integer_array(wrtr__ustno, mlm__vfxh)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            wrtr__ustno, mlm__vfxh = array_getitem_slice_index(A, ind)
            return init_integer_array(wrtr__ustno, mlm__vfxh)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    sdz__lkik = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    dpsrk__gzo = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if dpsrk__gzo:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(sdz__lkik)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or dpsrk__gzo):
        raise BodoError(sdz__lkik)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for IntegerArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_int_arr_len(A):
    if isinstance(A, IntegerArrayType):
        return lambda A: len(A._data)


@overload_attribute(IntegerArrayType, 'shape')
def overload_int_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(IntegerArrayType, 'dtype')
def overload_int_arr_dtype(A):
    dtype_class = getattr(pd, '{}Int{}Dtype'.format('' if A.dtype.signed else
        'U', A.dtype.bitwidth))
    return lambda A: dtype_class()


@overload_attribute(IntegerArrayType, 'ndim')
def overload_int_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntegerArrayType, 'nbytes')
def int_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(IntegerArrayType, 'copy', no_unliteral=True)
def overload_int_arr_copy(A, dtype=None):
    if not is_overload_none(dtype):
        return lambda A, dtype=None: A.astype(dtype, copy=True)
    else:
        return lambda A, dtype=None: bodo.libs.int_arr_ext.init_integer_array(
            bodo.libs.int_arr_ext.get_int_arr_data(A).copy(), bodo.libs.
            int_arr_ext.get_int_arr_bitmap(A).copy())


@overload_method(IntegerArrayType, 'astype', no_unliteral=True)
def overload_int_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "IntegerArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.NumberClass):
        dtype = dtype.dtype
    if isinstance(dtype, IntDtype) and A.dtype == dtype.dtype:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    if isinstance(dtype, IntDtype):
        np_dtype = dtype.dtype
        return (lambda A, dtype, copy=True: bodo.libs.int_arr_ext.
            init_integer_array(bodo.libs.int_arr_ext.get_int_arr_data(A).
            astype(np_dtype), bodo.libs.int_arr_ext.get_int_arr_bitmap(A).
            copy()))
    nb_dtype = parse_dtype(dtype, 'IntegerArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.int_arr_ext.get_int_arr_data(A)
            n = len(data)
            xrkfr__iacp = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                xrkfr__iacp[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    xrkfr__iacp[i] = np.nan
            return xrkfr__iacp
        return impl_float
    return lambda A, dtype, copy=True: bodo.libs.int_arr_ext.get_int_arr_data(A
        ).astype(nb_dtype)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def apply_null_mask(arr, bitmap, mask_fill, inplace):
    assert isinstance(arr, types.Array)
    if isinstance(arr.dtype, types.Integer):
        if is_overload_none(inplace):
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap.copy()))
        else:
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap))
    if isinstance(arr.dtype, types.Float):

        def impl(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = np.nan
            return arr
        return impl
    if arr.dtype == types.bool_:

        def impl_bool(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = mask_fill
            return arr
        return impl_bool
    return lambda arr, bitmap, mask_fill, inplace: arr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def merge_bitmaps(B1, B2, n, inplace):
    assert B1 == types.Array(types.uint8, 1, 'C')
    assert B2 == types.Array(types.uint8, 1, 'C')
    if not is_overload_none(inplace):

        def impl_inplace(B1, B2, n, inplace):
            for i in numba.parfors.parfor.internal_prange(n):
                ujicc__ult = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                oti__dscqx = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                gwsxy__ntxhm = ujicc__ult & oti__dscqx
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, gwsxy__ntxhm)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        tqb__xjvr = n + 7 >> 3
        xrkfr__iacp = np.empty(tqb__xjvr, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            ujicc__ult = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            oti__dscqx = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            gwsxy__ntxhm = ujicc__ult & oti__dscqx
            bodo.libs.int_arr_ext.set_bit_to_arr(xrkfr__iacp, i, gwsxy__ntxhm)
        return xrkfr__iacp
    return impl


ufunc_aliases = {'subtract': 'sub', 'multiply': 'mul', 'floor_divide':
    'floordiv', 'true_divide': 'truediv', 'power': 'pow', 'remainder':
    'mod', 'divide': 'div', 'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    if n_inputs == 1:

        def overload_int_arr_op_nin_1(A):
            if isinstance(A, IntegerArrayType):
                return get_nullable_array_unary_impl(op, A)
        return overload_int_arr_op_nin_1
    elif n_inputs == 2:

        def overload_series_op_nin_2(lhs, rhs):
            if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
                IntegerArrayType):
                return get_nullable_array_binary_impl(op, lhs, rhs)
        return overload_series_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for lkie__devd in numba.np.ufunc_db.get_ufuncs():
        sibm__uoun = create_op_overload(lkie__devd, lkie__devd.nin)
        overload(lkie__devd, no_unliteral=True)(sibm__uoun)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        sibm__uoun = create_op_overload(op, 2)
        overload(op)(sibm__uoun)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        sibm__uoun = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(sibm__uoun)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        sibm__uoun = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(sibm__uoun)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    doa__lfs = len(arrs.types)
    ghyjg__eql = 'def f(arrs):\n'
    khwbd__sjanz = ', '.join('arrs[{}]._data'.format(i) for i in range(
        doa__lfs))
    ghyjg__eql += '  return ({}{})\n'.format(khwbd__sjanz, ',' if doa__lfs ==
        1 else '')
    tix__jxyz = {}
    exec(ghyjg__eql, {}, tix__jxyz)
    impl = tix__jxyz['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    doa__lfs = len(arrs.types)
    ureq__elocd = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        doa__lfs))
    ghyjg__eql = 'def f(arrs):\n'
    ghyjg__eql += '  n = {}\n'.format(ureq__elocd)
    ghyjg__eql += '  n_bytes = (n + 7) >> 3\n'
    ghyjg__eql += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    ghyjg__eql += '  curr_bit = 0\n'
    for i in range(doa__lfs):
        ghyjg__eql += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        ghyjg__eql += '  for j in range(len(arrs[{}])):\n'.format(i)
        ghyjg__eql += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        ghyjg__eql += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        ghyjg__eql += '    curr_bit += 1\n'
    ghyjg__eql += '  return new_mask\n'
    tix__jxyz = {}
    exec(ghyjg__eql, {'np': np, 'bodo': bodo}, tix__jxyz)
    impl = tix__jxyz['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    knxm__oxn = dict(skipna=skipna, min_count=min_count)
    yiz__yog = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', knxm__oxn, yiz__yog)

    def impl(A, skipna=True, min_count=0):
        numba.parfors.parfor.init_prange()
        s = 0
        for i in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, i):
                val = A[i]
            s += val
        return s
    return impl


@overload_method(IntegerArrayType, 'unique', no_unliteral=True)
def overload_unique(A):
    dtype = A.dtype

    def impl_int_arr(A):
        data = []
        uuk__wnqpn = []
        komz__huts = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not komz__huts:
                    data.append(dtype(1))
                    uuk__wnqpn.append(False)
                    komz__huts = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                uuk__wnqpn.append(True)
        wrtr__ustno = np.array(data)
        n = len(wrtr__ustno)
        tqb__xjvr = n + 7 >> 3
        mlm__vfxh = np.empty(tqb__xjvr, np.uint8)
        for fsuj__nog in range(n):
            set_bit_to_arr(mlm__vfxh, fsuj__nog, uuk__wnqpn[fsuj__nog])
        return init_integer_array(wrtr__ustno, mlm__vfxh)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    mem__iowl = numba.core.registry.cpu_target.typing_context
    cqds__uok = mem__iowl.resolve_function_type(op, (types.Array(A.dtype, 1,
        'C'),), {}).return_type
    cqds__uok = to_nullable_type(cqds__uok)

    def impl(A):
        n = len(A)
        qkz__tkx = bodo.utils.utils.alloc_type(n, cqds__uok, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(qkz__tkx, i)
                continue
            qkz__tkx[i] = op(A[i])
        return qkz__tkx
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    ozs__huj = isinstance(lhs, (types.Number, types.Boolean))
    pmb__xky = isinstance(rhs, (types.Number, types.Boolean))
    mdhhn__qddic = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    qgje__mynrk = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    mem__iowl = numba.core.registry.cpu_target.typing_context
    cqds__uok = mem__iowl.resolve_function_type(op, (mdhhn__qddic,
        qgje__mynrk), {}).return_type
    cqds__uok = to_nullable_type(cqds__uok)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    qgtj__ypo = 'lhs' if ozs__huj else 'lhs[i]'
    xlida__awx = 'rhs' if pmb__xky else 'rhs[i]'
    iissc__mvf = ('False' if ozs__huj else
        'bodo.libs.array_kernels.isna(lhs, i)')
    nuw__apb = 'False' if pmb__xky else 'bodo.libs.array_kernels.isna(rhs, i)'
    ghyjg__eql = 'def impl(lhs, rhs):\n'
    ghyjg__eql += '  n = len({})\n'.format('lhs' if not ozs__huj else 'rhs')
    if inplace:
        ghyjg__eql += '  out_arr = {}\n'.format('lhs' if not ozs__huj else
            'rhs')
    else:
        ghyjg__eql += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    ghyjg__eql += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ghyjg__eql += '    if ({}\n'.format(iissc__mvf)
    ghyjg__eql += '        or {}):\n'.format(nuw__apb)
    ghyjg__eql += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    ghyjg__eql += '      continue\n'
    ghyjg__eql += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(qgtj__ypo, xlida__awx))
    ghyjg__eql += '  return out_arr\n'
    tix__jxyz = {}
    exec(ghyjg__eql, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        cqds__uok, 'op': op}, tix__jxyz)
    impl = tix__jxyz['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        ozs__huj = lhs in [pd_timedelta_type]
        pmb__xky = rhs in [pd_timedelta_type]
        if ozs__huj:

            def impl(lhs, rhs):
                n = len(rhs)
                qkz__tkx = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(qkz__tkx, i)
                        continue
                    qkz__tkx[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return qkz__tkx
            return impl
        elif pmb__xky:

            def impl(lhs, rhs):
                n = len(lhs)
                qkz__tkx = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(qkz__tkx, i)
                        continue
                    qkz__tkx[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return qkz__tkx
            return impl
    return impl
