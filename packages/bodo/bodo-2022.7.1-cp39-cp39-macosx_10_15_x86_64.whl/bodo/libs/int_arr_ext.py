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
        crkrj__qvfw = int(np.log2(self.dtype.bitwidth // 8))
        josu__peofe = 0 if self.dtype.signed else 4
        idx = crkrj__qvfw + josu__peofe
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rivvw__atjzf = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, rivvw__atjzf)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    pma__dca = 8 * val.dtype.itemsize
    gtxks__pea = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(gtxks__pea, pma__dca))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        mdr__ubabs = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(mdr__ubabs)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    trdek__xvbh = c.context.insert_const_string(c.builder.module, 'pandas')
    junud__vdmev = c.pyapi.import_module_noblock(trdek__xvbh)
    lcapw__wiqs = c.pyapi.call_method(junud__vdmev, str(typ)[:-2], ())
    c.pyapi.decref(junud__vdmev)
    return lcapw__wiqs


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    pma__dca = 8 * val.itemsize
    gtxks__pea = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(gtxks__pea, pma__dca))
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
    uqvm__dprx = n + 7 >> 3
    mwwdc__qpq = np.empty(uqvm__dprx, np.uint8)
    for i in range(n):
        cddp__kumy = i // 8
        mwwdc__qpq[cddp__kumy] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            mwwdc__qpq[cddp__kumy]) & kBitmask[i % 8]
    return mwwdc__qpq


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    lth__edpg = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(lth__edpg)
    c.pyapi.decref(lth__edpg)
    sgmyp__glu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    uqvm__dprx = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    hogu__wsb = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [uqvm__dprx])
    ggo__swz = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()])
    pek__whn = cgutils.get_or_insert_function(c.builder.module, ggo__swz,
        name='is_pd_int_array')
    epm__jfmbb = c.builder.call(pek__whn, [obj])
    egaxi__yxvpn = c.builder.icmp_unsigned('!=', epm__jfmbb, epm__jfmbb.type(0)
        )
    with c.builder.if_else(egaxi__yxvpn) as (zfdnd__fzv, wkhi__wwo):
        with zfdnd__fzv:
            edpe__gccrr = c.pyapi.object_getattr_string(obj, '_data')
            sgmyp__glu.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), edpe__gccrr).value
            hosdh__czv = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), hosdh__czv).value
            c.pyapi.decref(edpe__gccrr)
            c.pyapi.decref(hosdh__czv)
            laey__dehep = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            ggo__swz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            pek__whn = cgutils.get_or_insert_function(c.builder.module,
                ggo__swz, name='mask_arr_to_bitmap')
            c.builder.call(pek__whn, [hogu__wsb.data, laey__dehep.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with wkhi__wwo:
            mllf__qnb = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            ggo__swz = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            vku__caamr = cgutils.get_or_insert_function(c.builder.module,
                ggo__swz, name='int_array_from_sequence')
            c.builder.call(vku__caamr, [obj, c.builder.bitcast(mllf__qnb.
                data, lir.IntType(8).as_pointer()), hogu__wsb.data])
            sgmyp__glu.data = mllf__qnb._getvalue()
    sgmyp__glu.null_bitmap = hogu__wsb._getvalue()
    ldp__hzir = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(sgmyp__glu._getvalue(), is_error=ldp__hzir)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    sgmyp__glu = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        sgmyp__glu.data, c.env_manager)
    sky__gvemv = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, sgmyp__glu.null_bitmap).data
    lth__edpg = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(lth__edpg)
    trdek__xvbh = c.context.insert_const_string(c.builder.module, 'numpy')
    hew__yqhl = c.pyapi.import_module_noblock(trdek__xvbh)
    fpx__apxmy = c.pyapi.object_getattr_string(hew__yqhl, 'bool_')
    mask_arr = c.pyapi.call_method(hew__yqhl, 'empty', (lth__edpg, fpx__apxmy))
    ekln__due = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    hwrar__kflv = c.pyapi.object_getattr_string(ekln__due, 'data')
    elngg__hkau = c.builder.inttoptr(c.pyapi.long_as_longlong(hwrar__kflv),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as anl__hwk:
        i = anl__hwk.index
        czp__yjl = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        alkt__zre = c.builder.load(cgutils.gep(c.builder, sky__gvemv, czp__yjl)
            )
        rykaq__jeplq = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(alkt__zre, rykaq__jeplq), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        pftg__qorfe = cgutils.gep(c.builder, elngg__hkau, i)
        c.builder.store(val, pftg__qorfe)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        sgmyp__glu.null_bitmap)
    trdek__xvbh = c.context.insert_const_string(c.builder.module, 'pandas')
    junud__vdmev = c.pyapi.import_module_noblock(trdek__xvbh)
    lso__tygh = c.pyapi.object_getattr_string(junud__vdmev, 'arrays')
    lcapw__wiqs = c.pyapi.call_method(lso__tygh, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(junud__vdmev)
    c.pyapi.decref(lth__edpg)
    c.pyapi.decref(hew__yqhl)
    c.pyapi.decref(fpx__apxmy)
    c.pyapi.decref(ekln__due)
    c.pyapi.decref(hwrar__kflv)
    c.pyapi.decref(lso__tygh)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return lcapw__wiqs


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        cepvo__pjqfl, gmwn__gbxkk = args
        sgmyp__glu = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        sgmyp__glu.data = cepvo__pjqfl
        sgmyp__glu.null_bitmap = gmwn__gbxkk
        context.nrt.incref(builder, signature.args[0], cepvo__pjqfl)
        context.nrt.incref(builder, signature.args[1], gmwn__gbxkk)
        return sgmyp__glu._getvalue()
    bcjgr__lznqb = IntegerArrayType(data.dtype)
    smxvh__qyzz = bcjgr__lznqb(data, null_bitmap)
    return smxvh__qyzz, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    gdstg__chdgf = np.empty(n, pyval.dtype.type)
    fkalv__bhgqj = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        rkkgk__hir = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(fkalv__bhgqj, i, int(not
            rkkgk__hir))
        if not rkkgk__hir:
            gdstg__chdgf[i] = s
    fkvd__bbkoi = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), gdstg__chdgf)
    wpfa__axr = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), fkalv__bhgqj)
    return lir.Constant.literal_struct([fkvd__bbkoi, wpfa__axr])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    nibel__wyhj = args[0]
    if equiv_set.has_shape(nibel__wyhj):
        return ArrayAnalysis.AnalyzeResult(shape=nibel__wyhj, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    nibel__wyhj = args[0]
    if equiv_set.has_shape(nibel__wyhj):
        return ArrayAnalysis.AnalyzeResult(shape=nibel__wyhj, pre=[])
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
    gdstg__chdgf = np.empty(n, dtype)
    stu__tpe = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(gdstg__chdgf, stu__tpe)


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
            euhe__ohb, pix__zbbwz = array_getitem_bool_index(A, ind)
            return init_integer_array(euhe__ohb, pix__zbbwz)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            euhe__ohb, pix__zbbwz = array_getitem_int_index(A, ind)
            return init_integer_array(euhe__ohb, pix__zbbwz)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            euhe__ohb, pix__zbbwz = array_getitem_slice_index(A, ind)
            return init_integer_array(euhe__ohb, pix__zbbwz)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    yxy__hfbaw = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    lrkfq__ipr = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if lrkfq__ipr:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(yxy__hfbaw)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or lrkfq__ipr):
        raise BodoError(yxy__hfbaw)
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
            gji__iktri = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                gji__iktri[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    gji__iktri[i] = np.nan
            return gji__iktri
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
                tvf__gltuw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                wland__jfr = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                xvx__zrnzq = tvf__gltuw & wland__jfr
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, xvx__zrnzq)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        uqvm__dprx = n + 7 >> 3
        gji__iktri = np.empty(uqvm__dprx, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            tvf__gltuw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            wland__jfr = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            xvx__zrnzq = tvf__gltuw & wland__jfr
            bodo.libs.int_arr_ext.set_bit_to_arr(gji__iktri, i, xvx__zrnzq)
        return gji__iktri
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
    for upx__lwk in numba.np.ufunc_db.get_ufuncs():
        fnxce__amj = create_op_overload(upx__lwk, upx__lwk.nin)
        overload(upx__lwk, no_unliteral=True)(fnxce__amj)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        fnxce__amj = create_op_overload(op, 2)
        overload(op)(fnxce__amj)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        fnxce__amj = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(fnxce__amj)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        fnxce__amj = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(fnxce__amj)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    koh__rmob = len(arrs.types)
    rbsmw__qslqk = 'def f(arrs):\n'
    lcapw__wiqs = ', '.join('arrs[{}]._data'.format(i) for i in range(
        koh__rmob))
    rbsmw__qslqk += '  return ({}{})\n'.format(lcapw__wiqs, ',' if 
        koh__rmob == 1 else '')
    fgrj__vfsc = {}
    exec(rbsmw__qslqk, {}, fgrj__vfsc)
    impl = fgrj__vfsc['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    koh__rmob = len(arrs.types)
    tmelr__htau = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        koh__rmob))
    rbsmw__qslqk = 'def f(arrs):\n'
    rbsmw__qslqk += '  n = {}\n'.format(tmelr__htau)
    rbsmw__qslqk += '  n_bytes = (n + 7) >> 3\n'
    rbsmw__qslqk += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    rbsmw__qslqk += '  curr_bit = 0\n'
    for i in range(koh__rmob):
        rbsmw__qslqk += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        rbsmw__qslqk += '  for j in range(len(arrs[{}])):\n'.format(i)
        rbsmw__qslqk += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        rbsmw__qslqk += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        rbsmw__qslqk += '    curr_bit += 1\n'
    rbsmw__qslqk += '  return new_mask\n'
    fgrj__vfsc = {}
    exec(rbsmw__qslqk, {'np': np, 'bodo': bodo}, fgrj__vfsc)
    impl = fgrj__vfsc['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    amrrk__zew = dict(skipna=skipna, min_count=min_count)
    fgyv__zulu = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', amrrk__zew, fgyv__zulu)

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
        rykaq__jeplq = []
        mwrxg__josu = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not mwrxg__josu:
                    data.append(dtype(1))
                    rykaq__jeplq.append(False)
                    mwrxg__josu = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                rykaq__jeplq.append(True)
        euhe__ohb = np.array(data)
        n = len(euhe__ohb)
        uqvm__dprx = n + 7 >> 3
        pix__zbbwz = np.empty(uqvm__dprx, np.uint8)
        for cdqo__gzsjk in range(n):
            set_bit_to_arr(pix__zbbwz, cdqo__gzsjk, rykaq__jeplq[cdqo__gzsjk])
        return init_integer_array(euhe__ohb, pix__zbbwz)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    jnbgr__phkid = numba.core.registry.cpu_target.typing_context
    ubb__evp = jnbgr__phkid.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    ubb__evp = to_nullable_type(ubb__evp)

    def impl(A):
        n = len(A)
        mitdx__tiwc = bodo.utils.utils.alloc_type(n, ubb__evp, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(mitdx__tiwc, i)
                continue
            mitdx__tiwc[i] = op(A[i])
        return mitdx__tiwc
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    epz__ejeo = isinstance(lhs, (types.Number, types.Boolean))
    hmfr__roph = isinstance(rhs, (types.Number, types.Boolean))
    tjb__pnp = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    ekb__eggt = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    jnbgr__phkid = numba.core.registry.cpu_target.typing_context
    ubb__evp = jnbgr__phkid.resolve_function_type(op, (tjb__pnp, ekb__eggt), {}
        ).return_type
    ubb__evp = to_nullable_type(ubb__evp)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    uiqp__secx = 'lhs' if epz__ejeo else 'lhs[i]'
    tno__xij = 'rhs' if hmfr__roph else 'rhs[i]'
    gchz__ujns = ('False' if epz__ejeo else
        'bodo.libs.array_kernels.isna(lhs, i)')
    eaqz__mfqbs = ('False' if hmfr__roph else
        'bodo.libs.array_kernels.isna(rhs, i)')
    rbsmw__qslqk = 'def impl(lhs, rhs):\n'
    rbsmw__qslqk += '  n = len({})\n'.format('lhs' if not epz__ejeo else 'rhs')
    if inplace:
        rbsmw__qslqk += '  out_arr = {}\n'.format('lhs' if not epz__ejeo else
            'rhs')
    else:
        rbsmw__qslqk += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    rbsmw__qslqk += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    rbsmw__qslqk += '    if ({}\n'.format(gchz__ujns)
    rbsmw__qslqk += '        or {}):\n'.format(eaqz__mfqbs)
    rbsmw__qslqk += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    rbsmw__qslqk += '      continue\n'
    rbsmw__qslqk += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(uiqp__secx, tno__xij))
    rbsmw__qslqk += '  return out_arr\n'
    fgrj__vfsc = {}
    exec(rbsmw__qslqk, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        ubb__evp, 'op': op}, fgrj__vfsc)
    impl = fgrj__vfsc['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        epz__ejeo = lhs in [pd_timedelta_type]
        hmfr__roph = rhs in [pd_timedelta_type]
        if epz__ejeo:

            def impl(lhs, rhs):
                n = len(rhs)
                mitdx__tiwc = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(mitdx__tiwc, i)
                        continue
                    mitdx__tiwc[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs, rhs[i]))
                return mitdx__tiwc
            return impl
        elif hmfr__roph:

            def impl(lhs, rhs):
                n = len(lhs)
                mitdx__tiwc = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(mitdx__tiwc, i)
                        continue
                    mitdx__tiwc[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs[i], rhs))
                return mitdx__tiwc
            return impl
    return impl
