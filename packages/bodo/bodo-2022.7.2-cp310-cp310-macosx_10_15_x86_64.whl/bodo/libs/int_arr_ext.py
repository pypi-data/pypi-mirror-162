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
        qkj__uxece = int(np.log2(self.dtype.bitwidth // 8))
        arkl__fhhwy = 0 if self.dtype.signed else 4
        idx = qkj__uxece + arkl__fhhwy
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        oxro__pvkjy = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, oxro__pvkjy)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    cekwj__mapfo = 8 * val.dtype.itemsize
    fxdqu__oqyd = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(fxdqu__oqyd, cekwj__mapfo))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        zkpl__yefot = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(zkpl__yefot)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    bfo__aoan = c.context.insert_const_string(c.builder.module, 'pandas')
    jor__xiw = c.pyapi.import_module_noblock(bfo__aoan)
    npf__cixeu = c.pyapi.call_method(jor__xiw, str(typ)[:-2], ())
    c.pyapi.decref(jor__xiw)
    return npf__cixeu


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    cekwj__mapfo = 8 * val.itemsize
    fxdqu__oqyd = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(fxdqu__oqyd, cekwj__mapfo))
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
    wjusd__bnlcz = n + 7 >> 3
    yelcg__weya = np.empty(wjusd__bnlcz, np.uint8)
    for i in range(n):
        tmj__udyo = i // 8
        yelcg__weya[tmj__udyo] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            yelcg__weya[tmj__udyo]) & kBitmask[i % 8]
    return yelcg__weya


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    ouv__urbw = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(ouv__urbw)
    c.pyapi.decref(ouv__urbw)
    nej__qktm = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wjusd__bnlcz = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType
        (64), 7)), lir.Constant(lir.IntType(64), 8))
    rfalj__kfaqh = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [wjusd__bnlcz])
    atx__plwk = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    vtrzj__kbu = cgutils.get_or_insert_function(c.builder.module, atx__plwk,
        name='is_pd_int_array')
    syf__drogr = c.builder.call(vtrzj__kbu, [obj])
    wbi__alsu = c.builder.icmp_unsigned('!=', syf__drogr, syf__drogr.type(0))
    with c.builder.if_else(wbi__alsu) as (jjyky__iecq, mavzl__yag):
        with jjyky__iecq:
            rqii__pqlq = c.pyapi.object_getattr_string(obj, '_data')
            nej__qktm.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), rqii__pqlq).value
            sfzcj__crg = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), sfzcj__crg).value
            c.pyapi.decref(rqii__pqlq)
            c.pyapi.decref(sfzcj__crg)
            vmts__rvbu = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            atx__plwk = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            vtrzj__kbu = cgutils.get_or_insert_function(c.builder.module,
                atx__plwk, name='mask_arr_to_bitmap')
            c.builder.call(vtrzj__kbu, [rfalj__kfaqh.data, vmts__rvbu.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with mavzl__yag:
            gagh__lejsg = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            atx__plwk = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            yqt__bzw = cgutils.get_or_insert_function(c.builder.module,
                atx__plwk, name='int_array_from_sequence')
            c.builder.call(yqt__bzw, [obj, c.builder.bitcast(gagh__lejsg.
                data, lir.IntType(8).as_pointer()), rfalj__kfaqh.data])
            nej__qktm.data = gagh__lejsg._getvalue()
    nej__qktm.null_bitmap = rfalj__kfaqh._getvalue()
    zvzew__vvbi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(nej__qktm._getvalue(), is_error=zvzew__vvbi)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    nej__qktm = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        nej__qktm.data, c.env_manager)
    zkq__tbsoy = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, nej__qktm.null_bitmap).data
    ouv__urbw = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(ouv__urbw)
    bfo__aoan = c.context.insert_const_string(c.builder.module, 'numpy')
    ylnrp__nln = c.pyapi.import_module_noblock(bfo__aoan)
    gxjp__yhzib = c.pyapi.object_getattr_string(ylnrp__nln, 'bool_')
    mask_arr = c.pyapi.call_method(ylnrp__nln, 'empty', (ouv__urbw,
        gxjp__yhzib))
    oqhzs__byd = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    qoyy__txkhb = c.pyapi.object_getattr_string(oqhzs__byd, 'data')
    vzrvd__slm = c.builder.inttoptr(c.pyapi.long_as_longlong(qoyy__txkhb),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as njl__ugvls:
        i = njl__ugvls.index
        qscb__pheah = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        qgy__hhm = c.builder.load(cgutils.gep(c.builder, zkq__tbsoy,
            qscb__pheah))
        jcwn__rmgy = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(qgy__hhm, jcwn__rmgy), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        kyijy__abtov = cgutils.gep(c.builder, vzrvd__slm, i)
        c.builder.store(val, kyijy__abtov)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        nej__qktm.null_bitmap)
    bfo__aoan = c.context.insert_const_string(c.builder.module, 'pandas')
    jor__xiw = c.pyapi.import_module_noblock(bfo__aoan)
    vfyny__wwzkg = c.pyapi.object_getattr_string(jor__xiw, 'arrays')
    npf__cixeu = c.pyapi.call_method(vfyny__wwzkg, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(jor__xiw)
    c.pyapi.decref(ouv__urbw)
    c.pyapi.decref(ylnrp__nln)
    c.pyapi.decref(gxjp__yhzib)
    c.pyapi.decref(oqhzs__byd)
    c.pyapi.decref(qoyy__txkhb)
    c.pyapi.decref(vfyny__wwzkg)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return npf__cixeu


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        ircjs__xbrm, uye__wdo = args
        nej__qktm = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        nej__qktm.data = ircjs__xbrm
        nej__qktm.null_bitmap = uye__wdo
        context.nrt.incref(builder, signature.args[0], ircjs__xbrm)
        context.nrt.incref(builder, signature.args[1], uye__wdo)
        return nej__qktm._getvalue()
    kcnun__tph = IntegerArrayType(data.dtype)
    gbwnp__qvr = kcnun__tph(data, null_bitmap)
    return gbwnp__qvr, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    igekd__gvuad = np.empty(n, pyval.dtype.type)
    bxyks__mtygs = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        jtod__slxvd = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(bxyks__mtygs, i, int(not
            jtod__slxvd))
        if not jtod__slxvd:
            igekd__gvuad[i] = s
    rbkk__fydi = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), igekd__gvuad)
    ecnmr__ldhko = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), bxyks__mtygs)
    return lir.Constant.literal_struct([rbkk__fydi, ecnmr__ldhko])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    shd__wuql = args[0]
    if equiv_set.has_shape(shd__wuql):
        return ArrayAnalysis.AnalyzeResult(shape=shd__wuql, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    shd__wuql = args[0]
    if equiv_set.has_shape(shd__wuql):
        return ArrayAnalysis.AnalyzeResult(shape=shd__wuql, pre=[])
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
    igekd__gvuad = np.empty(n, dtype)
    etyc__cgu = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(igekd__gvuad, etyc__cgu)


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
            qnb__lvg, exn__gmj = array_getitem_bool_index(A, ind)
            return init_integer_array(qnb__lvg, exn__gmj)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            qnb__lvg, exn__gmj = array_getitem_int_index(A, ind)
            return init_integer_array(qnb__lvg, exn__gmj)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            qnb__lvg, exn__gmj = array_getitem_slice_index(A, ind)
            return init_integer_array(qnb__lvg, exn__gmj)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    zud__zgl = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    nnez__smm = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if nnez__smm:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(zud__zgl)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or nnez__smm):
        raise BodoError(zud__zgl)
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
            qnpt__ivp = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                qnpt__ivp[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    qnpt__ivp[i] = np.nan
            return qnpt__ivp
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
                zdt__hipjy = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                hbo__zisc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                zilu__omtoo = zdt__hipjy & hbo__zisc
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, zilu__omtoo)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        wjusd__bnlcz = n + 7 >> 3
        qnpt__ivp = np.empty(wjusd__bnlcz, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            zdt__hipjy = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            hbo__zisc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            zilu__omtoo = zdt__hipjy & hbo__zisc
            bodo.libs.int_arr_ext.set_bit_to_arr(qnpt__ivp, i, zilu__omtoo)
        return qnpt__ivp
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
    for kwwu__kmie in numba.np.ufunc_db.get_ufuncs():
        qox__zxoje = create_op_overload(kwwu__kmie, kwwu__kmie.nin)
        overload(kwwu__kmie, no_unliteral=True)(qox__zxoje)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        qox__zxoje = create_op_overload(op, 2)
        overload(op)(qox__zxoje)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        qox__zxoje = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(qox__zxoje)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        qox__zxoje = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(qox__zxoje)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    qfu__bxix = len(arrs.types)
    hwp__gfhm = 'def f(arrs):\n'
    npf__cixeu = ', '.join('arrs[{}]._data'.format(i) for i in range(qfu__bxix)
        )
    hwp__gfhm += '  return ({}{})\n'.format(npf__cixeu, ',' if qfu__bxix ==
        1 else '')
    lubpx__voxru = {}
    exec(hwp__gfhm, {}, lubpx__voxru)
    impl = lubpx__voxru['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    qfu__bxix = len(arrs.types)
    fcs__oumob = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        qfu__bxix))
    hwp__gfhm = 'def f(arrs):\n'
    hwp__gfhm += '  n = {}\n'.format(fcs__oumob)
    hwp__gfhm += '  n_bytes = (n + 7) >> 3\n'
    hwp__gfhm += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    hwp__gfhm += '  curr_bit = 0\n'
    for i in range(qfu__bxix):
        hwp__gfhm += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        hwp__gfhm += '  for j in range(len(arrs[{}])):\n'.format(i)
        hwp__gfhm += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        hwp__gfhm += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        hwp__gfhm += '    curr_bit += 1\n'
    hwp__gfhm += '  return new_mask\n'
    lubpx__voxru = {}
    exec(hwp__gfhm, {'np': np, 'bodo': bodo}, lubpx__voxru)
    impl = lubpx__voxru['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    daae__ydtz = dict(skipna=skipna, min_count=min_count)
    lgoa__lxudi = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', daae__ydtz, lgoa__lxudi)

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
        jcwn__rmgy = []
        avgem__smi = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not avgem__smi:
                    data.append(dtype(1))
                    jcwn__rmgy.append(False)
                    avgem__smi = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                jcwn__rmgy.append(True)
        qnb__lvg = np.array(data)
        n = len(qnb__lvg)
        wjusd__bnlcz = n + 7 >> 3
        exn__gmj = np.empty(wjusd__bnlcz, np.uint8)
        for fwgmv__ympf in range(n):
            set_bit_to_arr(exn__gmj, fwgmv__ympf, jcwn__rmgy[fwgmv__ympf])
        return init_integer_array(qnb__lvg, exn__gmj)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    yuz__xfrf = numba.core.registry.cpu_target.typing_context
    ncw__dyw = yuz__xfrf.resolve_function_type(op, (types.Array(A.dtype, 1,
        'C'),), {}).return_type
    ncw__dyw = to_nullable_type(ncw__dyw)

    def impl(A):
        n = len(A)
        jip__rks = bodo.utils.utils.alloc_type(n, ncw__dyw, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(jip__rks, i)
                continue
            jip__rks[i] = op(A[i])
        return jip__rks
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    oxc__yuu = isinstance(lhs, (types.Number, types.Boolean))
    uqod__ysoi = isinstance(rhs, (types.Number, types.Boolean))
    mten__clj = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    rjvt__tfx = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    yuz__xfrf = numba.core.registry.cpu_target.typing_context
    ncw__dyw = yuz__xfrf.resolve_function_type(op, (mten__clj, rjvt__tfx), {}
        ).return_type
    ncw__dyw = to_nullable_type(ncw__dyw)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    zsewl__ohjw = 'lhs' if oxc__yuu else 'lhs[i]'
    jrhqh__pjvf = 'rhs' if uqod__ysoi else 'rhs[i]'
    vcmwt__scdwx = ('False' if oxc__yuu else
        'bodo.libs.array_kernels.isna(lhs, i)')
    aulio__qnuz = ('False' if uqod__ysoi else
        'bodo.libs.array_kernels.isna(rhs, i)')
    hwp__gfhm = 'def impl(lhs, rhs):\n'
    hwp__gfhm += '  n = len({})\n'.format('lhs' if not oxc__yuu else 'rhs')
    if inplace:
        hwp__gfhm += '  out_arr = {}\n'.format('lhs' if not oxc__yuu else 'rhs'
            )
    else:
        hwp__gfhm += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    hwp__gfhm += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    hwp__gfhm += '    if ({}\n'.format(vcmwt__scdwx)
    hwp__gfhm += '        or {}):\n'.format(aulio__qnuz)
    hwp__gfhm += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    hwp__gfhm += '      continue\n'
    hwp__gfhm += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(zsewl__ohjw, jrhqh__pjvf))
    hwp__gfhm += '  return out_arr\n'
    lubpx__voxru = {}
    exec(hwp__gfhm, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        ncw__dyw, 'op': op}, lubpx__voxru)
    impl = lubpx__voxru['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        oxc__yuu = lhs in [pd_timedelta_type]
        uqod__ysoi = rhs in [pd_timedelta_type]
        if oxc__yuu:

            def impl(lhs, rhs):
                n = len(rhs)
                jip__rks = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(jip__rks, i)
                        continue
                    jip__rks[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return jip__rks
            return impl
        elif uqod__ysoi:

            def impl(lhs, rhs):
                n = len(lhs)
                jip__rks = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(jip__rks, i)
                        continue
                    jip__rks[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return jip__rks
            return impl
    return impl
