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
        ycaj__bbarw = int(np.log2(self.dtype.bitwidth // 8))
        wxt__xio = 0 if self.dtype.signed else 4
        idx = ycaj__bbarw + wxt__xio
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        oxx__uerpr = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, oxx__uerpr)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    vzm__cfrv = 8 * val.dtype.itemsize
    iuux__lkesm = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(iuux__lkesm, vzm__cfrv))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        xutu__fnufk = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(xutu__fnufk)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    atudr__bju = c.context.insert_const_string(c.builder.module, 'pandas')
    lcdhd__yigo = c.pyapi.import_module_noblock(atudr__bju)
    mnybd__wry = c.pyapi.call_method(lcdhd__yigo, str(typ)[:-2], ())
    c.pyapi.decref(lcdhd__yigo)
    return mnybd__wry


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    vzm__cfrv = 8 * val.itemsize
    iuux__lkesm = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(iuux__lkesm, vzm__cfrv))
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
    arep__zkcz = n + 7 >> 3
    nkptm__ckwr = np.empty(arep__zkcz, np.uint8)
    for i in range(n):
        slmeu__kbhim = i // 8
        nkptm__ckwr[slmeu__kbhim] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            nkptm__ckwr[slmeu__kbhim]) & kBitmask[i % 8]
    return nkptm__ckwr


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    wbht__yod = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(wbht__yod)
    c.pyapi.decref(wbht__yod)
    cmoqq__aomi = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    arep__zkcz = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    ivbki__fsr = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [arep__zkcz])
    qum__lnqrt = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    qlt__zqo = cgutils.get_or_insert_function(c.builder.module, qum__lnqrt,
        name='is_pd_int_array')
    kfqaz__nzi = c.builder.call(qlt__zqo, [obj])
    fdqbc__hsuc = c.builder.icmp_unsigned('!=', kfqaz__nzi, kfqaz__nzi.type(0))
    with c.builder.if_else(fdqbc__hsuc) as (opyt__xawhy, akc__gslr):
        with opyt__xawhy:
            fiimi__kbm = c.pyapi.object_getattr_string(obj, '_data')
            cmoqq__aomi.data = c.pyapi.to_native_value(types.Array(typ.
                dtype, 1, 'C'), fiimi__kbm).value
            mal__alma = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), mal__alma).value
            c.pyapi.decref(fiimi__kbm)
            c.pyapi.decref(mal__alma)
            ncuu__knnf = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            qum__lnqrt = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            qlt__zqo = cgutils.get_or_insert_function(c.builder.module,
                qum__lnqrt, name='mask_arr_to_bitmap')
            c.builder.call(qlt__zqo, [ivbki__fsr.data, ncuu__knnf.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with akc__gslr:
            rllt__khxvs = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            qum__lnqrt = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            qzaji__nhl = cgutils.get_or_insert_function(c.builder.module,
                qum__lnqrt, name='int_array_from_sequence')
            c.builder.call(qzaji__nhl, [obj, c.builder.bitcast(rllt__khxvs.
                data, lir.IntType(8).as_pointer()), ivbki__fsr.data])
            cmoqq__aomi.data = rllt__khxvs._getvalue()
    cmoqq__aomi.null_bitmap = ivbki__fsr._getvalue()
    iqg__bng = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cmoqq__aomi._getvalue(), is_error=iqg__bng)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    cmoqq__aomi = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        cmoqq__aomi.data, c.env_manager)
    nvmcv__jbn = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, cmoqq__aomi.null_bitmap).data
    wbht__yod = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(wbht__yod)
    atudr__bju = c.context.insert_const_string(c.builder.module, 'numpy')
    wnan__nzgri = c.pyapi.import_module_noblock(atudr__bju)
    far__bpi = c.pyapi.object_getattr_string(wnan__nzgri, 'bool_')
    mask_arr = c.pyapi.call_method(wnan__nzgri, 'empty', (wbht__yod, far__bpi))
    dorup__sxmea = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    mfe__cylh = c.pyapi.object_getattr_string(dorup__sxmea, 'data')
    xoh__bnhe = c.builder.inttoptr(c.pyapi.long_as_longlong(mfe__cylh), lir
        .IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as vset__pmroq:
        i = vset__pmroq.index
        rwtn__aemta = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        ziq__hdhuf = c.builder.load(cgutils.gep(c.builder, nvmcv__jbn,
            rwtn__aemta))
        psdft__glosw = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(ziq__hdhuf, psdft__glosw), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        yqfc__dtkne = cgutils.gep(c.builder, xoh__bnhe, i)
        c.builder.store(val, yqfc__dtkne)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        cmoqq__aomi.null_bitmap)
    atudr__bju = c.context.insert_const_string(c.builder.module, 'pandas')
    lcdhd__yigo = c.pyapi.import_module_noblock(atudr__bju)
    tylb__unedi = c.pyapi.object_getattr_string(lcdhd__yigo, 'arrays')
    mnybd__wry = c.pyapi.call_method(tylb__unedi, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(lcdhd__yigo)
    c.pyapi.decref(wbht__yod)
    c.pyapi.decref(wnan__nzgri)
    c.pyapi.decref(far__bpi)
    c.pyapi.decref(dorup__sxmea)
    c.pyapi.decref(mfe__cylh)
    c.pyapi.decref(tylb__unedi)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return mnybd__wry


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        lsk__nhp, alecd__qizk = args
        cmoqq__aomi = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        cmoqq__aomi.data = lsk__nhp
        cmoqq__aomi.null_bitmap = alecd__qizk
        context.nrt.incref(builder, signature.args[0], lsk__nhp)
        context.nrt.incref(builder, signature.args[1], alecd__qizk)
        return cmoqq__aomi._getvalue()
    yjo__ivgfu = IntegerArrayType(data.dtype)
    eod__mdg = yjo__ivgfu(data, null_bitmap)
    return eod__mdg, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    zkv__znc = np.empty(n, pyval.dtype.type)
    fge__ktrn = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        muys__ydr = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(fge__ktrn, i, int(not muys__ydr))
        if not muys__ydr:
            zkv__znc[i] = s
    aykww__hiy = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), zkv__znc)
    bfu__ipq = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), fge__ktrn)
    return lir.Constant.literal_struct([aykww__hiy, bfu__ipq])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    qosp__axc = args[0]
    if equiv_set.has_shape(qosp__axc):
        return ArrayAnalysis.AnalyzeResult(shape=qosp__axc, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    qosp__axc = args[0]
    if equiv_set.has_shape(qosp__axc):
        return ArrayAnalysis.AnalyzeResult(shape=qosp__axc, pre=[])
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
    zkv__znc = np.empty(n, dtype)
    bcbkv__dfyb = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(zkv__znc, bcbkv__dfyb)


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
            vbz__iax, ttq__gzm = array_getitem_bool_index(A, ind)
            return init_integer_array(vbz__iax, ttq__gzm)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            vbz__iax, ttq__gzm = array_getitem_int_index(A, ind)
            return init_integer_array(vbz__iax, ttq__gzm)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            vbz__iax, ttq__gzm = array_getitem_slice_index(A, ind)
            return init_integer_array(vbz__iax, ttq__gzm)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    bgh__twxk = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    voul__ojyl = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if voul__ojyl:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(bgh__twxk)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or voul__ojyl):
        raise BodoError(bgh__twxk)
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
            hpth__pnv = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                hpth__pnv[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    hpth__pnv[i] = np.nan
            return hpth__pnv
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
                jazz__jrnlq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                xwak__tpw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                rfvi__gox = jazz__jrnlq & xwak__tpw
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, rfvi__gox)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        arep__zkcz = n + 7 >> 3
        hpth__pnv = np.empty(arep__zkcz, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            jazz__jrnlq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            xwak__tpw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            rfvi__gox = jazz__jrnlq & xwak__tpw
            bodo.libs.int_arr_ext.set_bit_to_arr(hpth__pnv, i, rfvi__gox)
        return hpth__pnv
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
    for iwrgw__qqx in numba.np.ufunc_db.get_ufuncs():
        jsqi__fsb = create_op_overload(iwrgw__qqx, iwrgw__qqx.nin)
        overload(iwrgw__qqx, no_unliteral=True)(jsqi__fsb)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        jsqi__fsb = create_op_overload(op, 2)
        overload(op)(jsqi__fsb)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        jsqi__fsb = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(jsqi__fsb)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        jsqi__fsb = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(jsqi__fsb)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    hlk__fhfh = len(arrs.types)
    ekhlx__sef = 'def f(arrs):\n'
    mnybd__wry = ', '.join('arrs[{}]._data'.format(i) for i in range(hlk__fhfh)
        )
    ekhlx__sef += '  return ({}{})\n'.format(mnybd__wry, ',' if hlk__fhfh ==
        1 else '')
    bibq__atxd = {}
    exec(ekhlx__sef, {}, bibq__atxd)
    impl = bibq__atxd['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    hlk__fhfh = len(arrs.types)
    spkd__joqm = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        hlk__fhfh))
    ekhlx__sef = 'def f(arrs):\n'
    ekhlx__sef += '  n = {}\n'.format(spkd__joqm)
    ekhlx__sef += '  n_bytes = (n + 7) >> 3\n'
    ekhlx__sef += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    ekhlx__sef += '  curr_bit = 0\n'
    for i in range(hlk__fhfh):
        ekhlx__sef += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        ekhlx__sef += '  for j in range(len(arrs[{}])):\n'.format(i)
        ekhlx__sef += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        ekhlx__sef += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        ekhlx__sef += '    curr_bit += 1\n'
    ekhlx__sef += '  return new_mask\n'
    bibq__atxd = {}
    exec(ekhlx__sef, {'np': np, 'bodo': bodo}, bibq__atxd)
    impl = bibq__atxd['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    xtkab__fai = dict(skipna=skipna, min_count=min_count)
    hdrs__ssrkj = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', xtkab__fai, hdrs__ssrkj)

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
        psdft__glosw = []
        xem__ttriu = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not xem__ttriu:
                    data.append(dtype(1))
                    psdft__glosw.append(False)
                    xem__ttriu = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                psdft__glosw.append(True)
        vbz__iax = np.array(data)
        n = len(vbz__iax)
        arep__zkcz = n + 7 >> 3
        ttq__gzm = np.empty(arep__zkcz, np.uint8)
        for avzbi__ikpox in range(n):
            set_bit_to_arr(ttq__gzm, avzbi__ikpox, psdft__glosw[avzbi__ikpox])
        return init_integer_array(vbz__iax, ttq__gzm)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    iyjm__jdocf = numba.core.registry.cpu_target.typing_context
    ugnpj__oaw = iyjm__jdocf.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    ugnpj__oaw = to_nullable_type(ugnpj__oaw)

    def impl(A):
        n = len(A)
        pgsdn__wxaz = bodo.utils.utils.alloc_type(n, ugnpj__oaw, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(pgsdn__wxaz, i)
                continue
            pgsdn__wxaz[i] = op(A[i])
        return pgsdn__wxaz
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    fuih__uil = isinstance(lhs, (types.Number, types.Boolean))
    mnffo__pvgl = isinstance(rhs, (types.Number, types.Boolean))
    fbwt__rnhfh = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    ijqoi__qrsz = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    iyjm__jdocf = numba.core.registry.cpu_target.typing_context
    ugnpj__oaw = iyjm__jdocf.resolve_function_type(op, (fbwt__rnhfh,
        ijqoi__qrsz), {}).return_type
    ugnpj__oaw = to_nullable_type(ugnpj__oaw)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    wmij__yjw = 'lhs' if fuih__uil else 'lhs[i]'
    uqfbd__hdn = 'rhs' if mnffo__pvgl else 'rhs[i]'
    bhd__dlbnv = ('False' if fuih__uil else
        'bodo.libs.array_kernels.isna(lhs, i)')
    flovk__ghnax = ('False' if mnffo__pvgl else
        'bodo.libs.array_kernels.isna(rhs, i)')
    ekhlx__sef = 'def impl(lhs, rhs):\n'
    ekhlx__sef += '  n = len({})\n'.format('lhs' if not fuih__uil else 'rhs')
    if inplace:
        ekhlx__sef += '  out_arr = {}\n'.format('lhs' if not fuih__uil else
            'rhs')
    else:
        ekhlx__sef += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    ekhlx__sef += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ekhlx__sef += '    if ({}\n'.format(bhd__dlbnv)
    ekhlx__sef += '        or {}):\n'.format(flovk__ghnax)
    ekhlx__sef += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    ekhlx__sef += '      continue\n'
    ekhlx__sef += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(wmij__yjw, uqfbd__hdn))
    ekhlx__sef += '  return out_arr\n'
    bibq__atxd = {}
    exec(ekhlx__sef, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        ugnpj__oaw, 'op': op}, bibq__atxd)
    impl = bibq__atxd['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        fuih__uil = lhs in [pd_timedelta_type]
        mnffo__pvgl = rhs in [pd_timedelta_type]
        if fuih__uil:

            def impl(lhs, rhs):
                n = len(rhs)
                pgsdn__wxaz = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(pgsdn__wxaz, i)
                        continue
                    pgsdn__wxaz[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs, rhs[i]))
                return pgsdn__wxaz
            return impl
        elif mnffo__pvgl:

            def impl(lhs, rhs):
                n = len(lhs)
                pgsdn__wxaz = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(pgsdn__wxaz, i)
                        continue
                    pgsdn__wxaz[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs[i], rhs))
                return pgsdn__wxaz
            return impl
    return impl
