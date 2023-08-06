"""Array implementation for string objects, which are usually immutable.
The characters are stored in a contingous data array, and an offsets array marks the
the individual strings. For example:
value:             ['a', 'bc', '', 'abc', None, 'bb']
data:              [a, b, c, a, b, c, b, b]
offsets:           [0, 1, 3, 3, 6, 6, 8]
"""
import glob
import operator
import numba
import numba.core.typing.typeof
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.unsafe.bytes import memcpy_region
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, pre_alloc_binary_array
from bodo.libs.str_ext import memcmp, string_type, unicode_to_utf8_and_len
from bodo.utils.typing import BodoArrayIterator, BodoError, decode_if_dict_array, is_list_like_index_type, is_overload_constant_int, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
use_pd_string_array = False
char_type = types.uint8
char_arr_type = types.Array(char_type, 1, 'C')
offset_arr_type = types.Array(offset_type, 1, 'C')
null_bitmap_arr_type = types.Array(types.uint8, 1, 'C')
data_ctypes_type = types.ArrayCTypes(char_arr_type)
offset_ctypes_type = types.ArrayCTypes(offset_arr_type)


class StringArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(StringArrayType, self).__init__(name='StringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    def copy(self):
        return StringArrayType()


string_array_type = StringArrayType()


@typeof_impl.register(pd.arrays.StringArray)
def typeof_string_array(val, c):
    return string_array_type


@register_model(BinaryArrayType)
@register_model(StringArrayType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        oky__qgj = ArrayItemArrayType(char_arr_type)
        zxxe__ggjy = [('data', oky__qgj)]
        models.StructModel.__init__(self, dmm, fe_type, zxxe__ggjy)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        mtt__myw, = args
        apf__vzysz = context.make_helper(builder, string_array_type)
        apf__vzysz.data = mtt__myw
        context.nrt.incref(builder, data_typ, mtt__myw)
        return apf__vzysz._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    nvgwr__petkq = c.context.insert_const_string(c.builder.module, 'pandas')
    ivwjq__cqnsp = c.pyapi.import_module_noblock(nvgwr__petkq)
    cxt__ffj = c.pyapi.call_method(ivwjq__cqnsp, 'StringDtype', ())
    c.pyapi.decref(ivwjq__cqnsp)
    return cxt__ffj


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        ekplv__hdtp = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs,
            rhs)
        if ekplv__hdtp is not None:
            return ekplv__hdtp
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ctng__ubdx = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ctng__ubdx)
                for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                    if bodo.libs.array_kernels.isna(lhs, i
                        ) or bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_both
        if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

            def impl_left(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ctng__ubdx = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ctng__ubdx)
                for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs)
                    out_arr[i] = val
                return out_arr
            return impl_left
        if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

            def impl_right(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ctng__ubdx = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(ctng__ubdx)
                for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs, rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_right
        raise_bodo_error(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_string_array_binary_op


def overload_add_operator_string_array(lhs, rhs):
    nrbqv__enw = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    qvg__bncth = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and qvg__bncth or nrbqv__enw and is_str_arr_type(
        rhs):

        def impl_both(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j
                    ) or bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs[j]
            return out_arr
        return impl_both
    if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

        def impl_left(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs
            return out_arr
        return impl_left
    if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

        def impl_right(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(rhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs + rhs[j]
            return out_arr
        return impl_right


def overload_mul_operator_str_arr(lhs, rhs):
    if is_str_arr_type(lhs) and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] * rhs
            return out_arr
        return impl
    if isinstance(lhs, types.Integer) and is_str_arr_type(rhs):

        def impl(lhs, rhs):
            return rhs * lhs
        return impl


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    ofepm__lstet = context.make_helper(builder, arr_typ, arr_value)
    oky__qgj = ArrayItemArrayType(char_arr_type)
    toswc__vewu = _get_array_item_arr_payload(context, builder, oky__qgj,
        ofepm__lstet.data)
    return toswc__vewu


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return toswc__vewu.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        klyrb__xxs = context.make_helper(builder, offset_arr_type,
            toswc__vewu.offsets).data
        return _get_num_total_chars(builder, klyrb__xxs, toswc__vewu.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        moogg__kcwde = context.make_helper(builder, offset_arr_type,
            toswc__vewu.offsets)
        phx__nqtba = context.make_helper(builder, offset_ctypes_type)
        phx__nqtba.data = builder.bitcast(moogg__kcwde.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        phx__nqtba.meminfo = moogg__kcwde.meminfo
        cxt__ffj = phx__nqtba._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type, cxt__ffj
            )
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        mtt__myw = context.make_helper(builder, char_arr_type, toswc__vewu.data
            )
        phx__nqtba = context.make_helper(builder, data_ctypes_type)
        phx__nqtba.data = mtt__myw.data
        phx__nqtba.meminfo = mtt__myw.meminfo
        cxt__ffj = phx__nqtba._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, cxt__ffj)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        pmh__clgx, ind = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            pmh__clgx, sig.args[0])
        mtt__myw = context.make_helper(builder, char_arr_type, toswc__vewu.data
            )
        phx__nqtba = context.make_helper(builder, data_ctypes_type)
        phx__nqtba.data = builder.gep(mtt__myw.data, [ind])
        phx__nqtba.meminfo = mtt__myw.meminfo
        cxt__ffj = phx__nqtba._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, cxt__ffj)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        jje__vrkvo, ywcn__kfy, jjiyq__cmitn, jiwwp__ojhq = args
        vnwy__uew = builder.bitcast(builder.gep(jje__vrkvo, [ywcn__kfy]),
            lir.IntType(8).as_pointer())
        mak__ylvr = builder.bitcast(builder.gep(jjiyq__cmitn, [jiwwp__ojhq]
            ), lir.IntType(8).as_pointer())
        rqs__vbsv = builder.load(mak__ylvr)
        builder.store(rqs__vbsv, vnwy__uew)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        rsfj__elts = context.make_helper(builder, null_bitmap_arr_type,
            toswc__vewu.null_bitmap)
        phx__nqtba = context.make_helper(builder, data_ctypes_type)
        phx__nqtba.data = rsfj__elts.data
        phx__nqtba.meminfo = rsfj__elts.meminfo
        cxt__ffj = phx__nqtba._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, cxt__ffj)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        klyrb__xxs = context.make_helper(builder, offset_arr_type,
            toswc__vewu.offsets).data
        return builder.load(builder.gep(klyrb__xxs, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, toswc__vewu
            .offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        xypb__lbt, ind = args
        if in_bitmap_typ == data_ctypes_type:
            phx__nqtba = context.make_helper(builder, data_ctypes_type,
                xypb__lbt)
            xypb__lbt = phx__nqtba.data
        return builder.load(builder.gep(xypb__lbt, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        xypb__lbt, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            phx__nqtba = context.make_helper(builder, data_ctypes_type,
                xypb__lbt)
            xypb__lbt = phx__nqtba.data
        builder.store(val, builder.gep(xypb__lbt, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        geqqb__mwy = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        zmqhk__ggzc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        vwn__kewjr = context.make_helper(builder, offset_arr_type,
            geqqb__mwy.offsets).data
        rapk__lls = context.make_helper(builder, offset_arr_type,
            zmqhk__ggzc.offsets).data
        ptu__lggsz = context.make_helper(builder, char_arr_type, geqqb__mwy
            .data).data
        ktj__ljulg = context.make_helper(builder, char_arr_type,
            zmqhk__ggzc.data).data
        hst__tcoxs = context.make_helper(builder, null_bitmap_arr_type,
            geqqb__mwy.null_bitmap).data
        rxgq__cdqa = context.make_helper(builder, null_bitmap_arr_type,
            zmqhk__ggzc.null_bitmap).data
        juwg__lut = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, rapk__lls, vwn__kewjr, juwg__lut)
        cgutils.memcpy(builder, ktj__ljulg, ptu__lggsz, builder.load(
            builder.gep(vwn__kewjr, [ind])))
        xwfs__jns = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        monba__xery = builder.lshr(xwfs__jns, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, rxgq__cdqa, hst__tcoxs, monba__xery)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        geqqb__mwy = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        zmqhk__ggzc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        vwn__kewjr = context.make_helper(builder, offset_arr_type,
            geqqb__mwy.offsets).data
        ptu__lggsz = context.make_helper(builder, char_arr_type, geqqb__mwy
            .data).data
        ktj__ljulg = context.make_helper(builder, char_arr_type,
            zmqhk__ggzc.data).data
        num_total_chars = _get_num_total_chars(builder, vwn__kewjr,
            geqqb__mwy.n_arrays)
        cgutils.memcpy(builder, ktj__ljulg, ptu__lggsz, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        geqqb__mwy = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        zmqhk__ggzc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        vwn__kewjr = context.make_helper(builder, offset_arr_type,
            geqqb__mwy.offsets).data
        rapk__lls = context.make_helper(builder, offset_arr_type,
            zmqhk__ggzc.offsets).data
        hst__tcoxs = context.make_helper(builder, null_bitmap_arr_type,
            geqqb__mwy.null_bitmap).data
        ctng__ubdx = geqqb__mwy.n_arrays
        wfx__kzkv = context.get_constant(offset_type, 0)
        glole__ypir = cgutils.alloca_once_value(builder, wfx__kzkv)
        with cgutils.for_range(builder, ctng__ubdx) as aueo__fjxo:
            nlywr__kaeo = lower_is_na(context, builder, hst__tcoxs,
                aueo__fjxo.index)
            with cgutils.if_likely(builder, builder.not_(nlywr__kaeo)):
                ylna__uxv = builder.load(builder.gep(vwn__kewjr, [
                    aueo__fjxo.index]))
                zmln__tfd = builder.load(glole__ypir)
                builder.store(ylna__uxv, builder.gep(rapk__lls, [zmln__tfd]))
                builder.store(builder.add(zmln__tfd, lir.Constant(context.
                    get_value_type(offset_type), 1)), glole__ypir)
        zmln__tfd = builder.load(glole__ypir)
        ylna__uxv = builder.load(builder.gep(vwn__kewjr, [ctng__ubdx]))
        builder.store(ylna__uxv, builder.gep(rapk__lls, [zmln__tfd]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        yah__yuy, ind, str, mla__rbiwv = args
        yah__yuy = context.make_array(sig.args[0])(context, builder, yah__yuy)
        vdx__jrzzj = builder.gep(yah__yuy.data, [ind])
        cgutils.raw_memcpy(builder, vdx__jrzzj, str, mla__rbiwv, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        vdx__jrzzj, ind, xsmdg__oien, mla__rbiwv = args
        vdx__jrzzj = builder.gep(vdx__jrzzj, [ind])
        cgutils.raw_memcpy(builder, vdx__jrzzj, xsmdg__oien, mla__rbiwv, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            emfnx__ruza = A._data
            return np.int64(getitem_str_offset(emfnx__ruza, idx + 1) -
                getitem_str_offset(emfnx__ruza, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    cpoux__myleq = np.int64(getitem_str_offset(A, i))
    kdpda__othh = np.int64(getitem_str_offset(A, i + 1))
    l = kdpda__othh - cpoux__myleq
    tnq__xcnmk = get_data_ptr_ind(A, cpoux__myleq)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(tnq__xcnmk, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.generated_jit(no_cpython_wrapper=True, nopython=True)
def get_str_arr_item_copy(B, j, A, i):
    if B != string_array_type:
        raise BodoError(
            'get_str_arr_item_copy(): Output array must be a string array')
    if not is_str_arr_type(A):
        raise BodoError(
            'get_str_arr_item_copy(): Input array must be a string array or dictionary encoded array'
            )
    if A == bodo.dict_str_arr_type:
        ssqoq__oaplv = 'in_str_arr = A._data'
        yjp__dqlhy = 'input_index = A._indices[i]'
    else:
        ssqoq__oaplv = 'in_str_arr = A'
        yjp__dqlhy = 'input_index = i'
    hgypc__jwv = f"""def impl(B, j, A, i):
        if j == 0:
            setitem_str_offset(B, 0, 0)

        {ssqoq__oaplv}
        {yjp__dqlhy}

        # set NA
        if bodo.libs.array_kernels.isna(A, i):
            str_arr_set_na(B, j)
            return
        else:
            str_arr_set_not_na(B, j)

        # get input array offsets
        in_start_offset = getitem_str_offset(in_str_arr, input_index)
        in_end_offset = getitem_str_offset(in_str_arr, input_index + 1)
        val_len = in_end_offset - in_start_offset

        # set output offset
        out_start_offset = getitem_str_offset(B, j)
        out_end_offset = out_start_offset + val_len
        setitem_str_offset(B, j + 1, out_end_offset)

        # copy data
        if val_len != 0:
            # ensure required space in output array
            data_arr = B._data
            bodo.libs.array_item_arr_ext.ensure_data_capacity(
                data_arr, np.int64(out_start_offset), np.int64(out_end_offset)
            )
            out_data_ptr = get_data_ptr(B).data
            in_data_ptr = get_data_ptr(in_str_arr).data
            memcpy_region(
                out_data_ptr,
                out_start_offset,
                in_data_ptr,
                in_start_offset,
                val_len,
                1,
            )"""
    mll__vjcb = {}
    exec(hgypc__jwv, {'setitem_str_offset': setitem_str_offset,
        'memcpy_region': memcpy_region, 'getitem_str_offset':
        getitem_str_offset, 'str_arr_set_na': str_arr_set_na,
        'str_arr_set_not_na': str_arr_set_not_na, 'get_data_ptr':
        get_data_ptr, 'bodo': bodo, 'np': np}, mll__vjcb)
    impl = mll__vjcb['impl']
    return impl


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    ctng__ubdx = len(str_arr)
    yuuu__bof = np.empty(ctng__ubdx, np.bool_)
    for i in range(ctng__ubdx):
        yuuu__bof[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return yuuu__bof


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            ctng__ubdx = len(data)
            l = []
            for i in range(ctng__ubdx):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        edufo__yql = data.count
        hrxnd__ffam = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(edufo__yql)]
        if is_overload_true(str_null_bools):
            hrxnd__ffam += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(edufo__yql) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        hgypc__jwv = 'def f(data, str_null_bools=None):\n'
        hgypc__jwv += '  return ({}{})\n'.format(', '.join(hrxnd__ffam), 
            ',' if edufo__yql == 1 else '')
        mll__vjcb = {}
        exec(hgypc__jwv, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, mll__vjcb)
        hdbls__dkmj = mll__vjcb['f']
        return hdbls__dkmj
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                ctng__ubdx = len(list_data)
                for i in range(ctng__ubdx):
                    xsmdg__oien = list_data[i]
                    str_arr[i] = xsmdg__oien
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                ctng__ubdx = len(list_data)
                for i in range(ctng__ubdx):
                    xsmdg__oien = list_data[i]
                    str_arr[i] = xsmdg__oien
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        edufo__yql = str_arr.count
        hjmh__dvz = 0
        hgypc__jwv = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(edufo__yql):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                hgypc__jwv += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, edufo__yql + hjmh__dvz))
                hjmh__dvz += 1
            else:
                hgypc__jwv += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        hgypc__jwv += '  return\n'
        mll__vjcb = {}
        exec(hgypc__jwv, {'cp_str_list_to_array': cp_str_list_to_array},
            mll__vjcb)
        pnwbl__zwmn = mll__vjcb['f']
        return pnwbl__zwmn
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            ctng__ubdx = len(str_list)
            str_arr = pre_alloc_string_array(ctng__ubdx, -1)
            for i in range(ctng__ubdx):
                xsmdg__oien = str_list[i]
                str_arr[i] = xsmdg__oien
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            ctng__ubdx = len(A)
            ffmh__dtdh = 0
            for i in range(ctng__ubdx):
                xsmdg__oien = A[i]
                ffmh__dtdh += get_utf8_size(xsmdg__oien)
            return ffmh__dtdh
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        ctng__ubdx = len(arr)
        n_chars = num_total_chars(arr)
        dbhk__aoane = pre_alloc_string_array(ctng__ubdx, np.int64(n_chars))
        copy_str_arr_slice(dbhk__aoane, arr, ctng__ubdx)
        return dbhk__aoane
    return copy_impl


@overload(len, no_unliteral=True)
def str_arr_len_overload(str_arr):
    if str_arr == string_array_type:

        def str_arr_len(str_arr):
            return str_arr.size
        return str_arr_len


@overload_attribute(StringArrayType, 'size')
def str_arr_size_overload(str_arr):
    return lambda str_arr: len(str_arr._data)


@overload_attribute(StringArrayType, 'shape')
def str_arr_shape_overload(str_arr):
    return lambda str_arr: (str_arr.size,)


@overload_attribute(StringArrayType, 'nbytes')
def str_arr_nbytes_overload(str_arr):
    return lambda str_arr: str_arr._data.nbytes


@overload_method(types.Array, 'tolist', no_unliteral=True)
@overload_method(StringArrayType, 'tolist', no_unliteral=True)
def overload_to_list(arr):
    return lambda arr: list(arr)


import llvmlite.binding as ll
from llvmlite import ir as lir
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('setitem_string_array', hstr_ext.setitem_string_array)
ll.add_symbol('is_na', hstr_ext.is_na)
ll.add_symbol('string_array_from_sequence', array_ext.
    string_array_from_sequence)
ll.add_symbol('pd_array_from_string_array', hstr_ext.pd_array_from_string_array
    )
ll.add_symbol('np_array_from_string_array', hstr_ext.np_array_from_string_array
    )
ll.add_symbol('convert_len_arr_to_offset32', hstr_ext.
    convert_len_arr_to_offset32)
ll.add_symbol('convert_len_arr_to_offset', hstr_ext.convert_len_arr_to_offset)
ll.add_symbol('set_string_array_range', hstr_ext.set_string_array_range)
ll.add_symbol('str_arr_to_int64', hstr_ext.str_arr_to_int64)
ll.add_symbol('str_arr_to_float64', hstr_ext.str_arr_to_float64)
ll.add_symbol('get_utf8_size', hstr_ext.get_utf8_size)
ll.add_symbol('print_str_arr', hstr_ext.print_str_arr)
ll.add_symbol('inplace_int64_to_str', hstr_ext.inplace_int64_to_str)
inplace_int64_to_str = types.ExternalFunction('inplace_int64_to_str', types
    .void(types.voidptr, types.int64, types.int64))
convert_len_arr_to_offset32 = types.ExternalFunction(
    'convert_len_arr_to_offset32', types.void(types.voidptr, types.intp))
convert_len_arr_to_offset = types.ExternalFunction('convert_len_arr_to_offset',
    types.void(types.voidptr, types.voidptr, types.intp))
setitem_string_array = types.ExternalFunction('setitem_string_array', types
    .void(types.CPointer(offset_type), types.CPointer(char_type), types.
    uint64, types.voidptr, types.intp, offset_type, offset_type, types.intp))
_get_utf8_size = types.ExternalFunction('get_utf8_size', types.intp(types.
    voidptr, types.intp, offset_type))
_print_str_arr = types.ExternalFunction('print_str_arr', types.void(types.
    uint64, types.uint64, types.CPointer(offset_type), types.CPointer(
    char_type)))


@numba.generated_jit(nopython=True)
def empty_str_arr(in_seq):
    hgypc__jwv = 'def f(in_seq):\n'
    hgypc__jwv += '    n_strs = len(in_seq)\n'
    hgypc__jwv += '    A = pre_alloc_string_array(n_strs, -1)\n'
    hgypc__jwv += '    return A\n'
    mll__vjcb = {}
    exec(hgypc__jwv, {'pre_alloc_string_array': pre_alloc_string_array},
        mll__vjcb)
    qhg__cnaoc = mll__vjcb['f']
    return qhg__cnaoc


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        gyl__snbub = 'pre_alloc_binary_array'
    else:
        gyl__snbub = 'pre_alloc_string_array'
    hgypc__jwv = 'def f(in_seq):\n'
    hgypc__jwv += '    n_strs = len(in_seq)\n'
    hgypc__jwv += f'    A = {gyl__snbub}(n_strs, -1)\n'
    hgypc__jwv += '    for i in range(n_strs):\n'
    hgypc__jwv += '        A[i] = in_seq[i]\n'
    hgypc__jwv += '    return A\n'
    mll__vjcb = {}
    exec(hgypc__jwv, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, mll__vjcb)
    qhg__cnaoc = mll__vjcb['f']
    return qhg__cnaoc


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xevtu__exrn = builder.add(toswc__vewu.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        ssakw__eslm = builder.lshr(lir.Constant(lir.IntType(64),
            offset_type.bitwidth), lir.Constant(lir.IntType(64), 3))
        monba__xery = builder.mul(xevtu__exrn, ssakw__eslm)
        poecq__voaf = context.make_array(offset_arr_type)(context, builder,
            toswc__vewu.offsets).data
        cgutils.memset(builder, poecq__voaf, monba__xery, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        qtle__sldm = toswc__vewu.n_arrays
        monba__xery = builder.lshr(builder.add(qtle__sldm, lir.Constant(lir
            .IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        heet__dneqq = context.make_array(null_bitmap_arr_type)(context,
            builder, toswc__vewu.null_bitmap).data
        cgutils.memset(builder, heet__dneqq, monba__xery, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@numba.njit
def pre_alloc_string_array(n_strs, n_chars):
    if n_chars is None:
        n_chars = -1
    str_arr = init_str_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_strs), (np.int64(n_chars),),
        char_arr_type))
    if n_chars == 0:
        set_all_offsets_to_0(str_arr)
    return str_arr


@register_jitable
def gen_na_str_array_lens(n_strs, total_len, len_arr):
    str_arr = pre_alloc_string_array(n_strs, total_len)
    set_bitmap_all_NA(str_arr)
    offsets = bodo.libs.array_item_arr_ext.get_offsets(str_arr._data)
    vkmg__bnxu = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        lolst__iqyho = len(len_arr)
        for i in range(lolst__iqyho):
            offsets[i] = vkmg__bnxu
            vkmg__bnxu += len_arr[i]
        offsets[lolst__iqyho] = vkmg__bnxu
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    hawp__qapo = i // 8
    ior__jqiug = getitem_str_bitmap(bits, hawp__qapo)
    ior__jqiug ^= np.uint8(-np.uint8(bit_is_set) ^ ior__jqiug) & kBitmask[i % 8
        ]
    setitem_str_bitmap(bits, hawp__qapo, ior__jqiug)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    ghckc__remps = get_null_bitmap_ptr(out_str_arr)
    qxtb__srfez = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        xkni__gnggc = get_bit_bitmap(qxtb__srfez, j)
        set_bit_to(ghckc__remps, out_start + j, xkni__gnggc)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, pmh__clgx, akk__smyt, dnh__dlioj = args
        geqqb__mwy = _get_str_binary_arr_payload(context, builder,
            pmh__clgx, string_array_type)
        zmqhk__ggzc = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        vwn__kewjr = context.make_helper(builder, offset_arr_type,
            geqqb__mwy.offsets).data
        rapk__lls = context.make_helper(builder, offset_arr_type,
            zmqhk__ggzc.offsets).data
        ptu__lggsz = context.make_helper(builder, char_arr_type, geqqb__mwy
            .data).data
        ktj__ljulg = context.make_helper(builder, char_arr_type,
            zmqhk__ggzc.data).data
        num_total_chars = _get_num_total_chars(builder, vwn__kewjr,
            geqqb__mwy.n_arrays)
        qba__sbef = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        jkqd__kra = cgutils.get_or_insert_function(builder.module,
            qba__sbef, name='set_string_array_range')
        builder.call(jkqd__kra, [rapk__lls, ktj__ljulg, vwn__kewjr,
            ptu__lggsz, akk__smyt, dnh__dlioj, geqqb__mwy.n_arrays,
            num_total_chars])
        pfdyb__txyvp = context.typing_context.resolve_value_type(
            copy_nulls_range)
        feg__kwvvc = pfdyb__txyvp.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        umgg__uost = context.get_function(pfdyb__txyvp, feg__kwvvc)
        umgg__uost(builder, (out_arr, pmh__clgx, akk__smyt))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    cujvl__wxplg = c.context.make_helper(c.builder, typ, val)
    oky__qgj = ArrayItemArrayType(char_arr_type)
    toswc__vewu = _get_array_item_arr_payload(c.context, c.builder,
        oky__qgj, cujvl__wxplg.data)
    tvsy__olp = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    uihs__rwyak = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        uihs__rwyak = 'pd_array_from_string_array'
    qba__sbef = lir.FunctionType(c.context.get_argument_type(types.pyobject
        ), [lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
        lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
        IntType(32)])
    dhjbk__fbis = cgutils.get_or_insert_function(c.builder.module,
        qba__sbef, name=uihs__rwyak)
    klyrb__xxs = c.context.make_array(offset_arr_type)(c.context, c.builder,
        toswc__vewu.offsets).data
    tnq__xcnmk = c.context.make_array(char_arr_type)(c.context, c.builder,
        toswc__vewu.data).data
    heet__dneqq = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, toswc__vewu.null_bitmap).data
    arr = c.builder.call(dhjbk__fbis, [toswc__vewu.n_arrays, klyrb__xxs,
        tnq__xcnmk, heet__dneqq, tvsy__olp])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        heet__dneqq = context.make_array(null_bitmap_arr_type)(context,
            builder, toswc__vewu.null_bitmap).data
        qqp__oog = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ddndm__mbu = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        ior__jqiug = builder.load(builder.gep(heet__dneqq, [qqp__oog],
            inbounds=True))
        zqe__widz = lir.ArrayType(lir.IntType(8), 8)
        tan__wdfu = cgutils.alloca_once_value(builder, lir.Constant(
            zqe__widz, (1, 2, 4, 8, 16, 32, 64, 128)))
        ofyq__tnqm = builder.load(builder.gep(tan__wdfu, [lir.Constant(lir.
            IntType(64), 0), ddndm__mbu], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(ior__jqiug,
            ofyq__tnqm), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        qqp__oog = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ddndm__mbu = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        heet__dneqq = context.make_array(null_bitmap_arr_type)(context,
            builder, toswc__vewu.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, toswc__vewu
            .offsets).data
        xupuq__bcjq = builder.gep(heet__dneqq, [qqp__oog], inbounds=True)
        ior__jqiug = builder.load(xupuq__bcjq)
        zqe__widz = lir.ArrayType(lir.IntType(8), 8)
        tan__wdfu = cgutils.alloca_once_value(builder, lir.Constant(
            zqe__widz, (1, 2, 4, 8, 16, 32, 64, 128)))
        ofyq__tnqm = builder.load(builder.gep(tan__wdfu, [lir.Constant(lir.
            IntType(64), 0), ddndm__mbu], inbounds=True))
        ofyq__tnqm = builder.xor(ofyq__tnqm, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(ior__jqiug, ofyq__tnqm), xupuq__bcjq)
        if str_arr_typ == string_array_type:
            rpuo__ascnd = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            jxbu__vdinz = builder.icmp_unsigned('!=', rpuo__ascnd,
                toswc__vewu.n_arrays)
            with builder.if_then(jxbu__vdinz):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [rpuo__ascnd]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        qqp__oog = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ddndm__mbu = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        heet__dneqq = context.make_array(null_bitmap_arr_type)(context,
            builder, toswc__vewu.null_bitmap).data
        xupuq__bcjq = builder.gep(heet__dneqq, [qqp__oog], inbounds=True)
        ior__jqiug = builder.load(xupuq__bcjq)
        zqe__widz = lir.ArrayType(lir.IntType(8), 8)
        tan__wdfu = cgutils.alloca_once_value(builder, lir.Constant(
            zqe__widz, (1, 2, 4, 8, 16, 32, 64, 128)))
        ofyq__tnqm = builder.load(builder.gep(tan__wdfu, [lir.Constant(lir.
            IntType(64), 0), ddndm__mbu], inbounds=True))
        builder.store(builder.or_(ior__jqiug, ofyq__tnqm), xupuq__bcjq)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        monba__xery = builder.udiv(builder.add(toswc__vewu.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        heet__dneqq = context.make_array(null_bitmap_arr_type)(context,
            builder, toswc__vewu.null_bitmap).data
        cgutils.memset(builder, heet__dneqq, monba__xery, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    krvl__yjt = context.make_helper(builder, string_array_type, str_arr)
    oky__qgj = ArrayItemArrayType(char_arr_type)
    vkb__zwr = context.make_helper(builder, oky__qgj, krvl__yjt.data)
    rzc__ckpe = ArrayItemArrayPayloadType(oky__qgj)
    hcbc__jaaq = context.nrt.meminfo_data(builder, vkb__zwr.meminfo)
    tufr__suk = builder.bitcast(hcbc__jaaq, context.get_value_type(
        rzc__ckpe).as_pointer())
    return tufr__suk


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        pzme__wmes, chnsk__bamn = args
        ief__nwuii = _get_str_binary_arr_data_payload_ptr(context, builder,
            chnsk__bamn)
        nae__vwq = _get_str_binary_arr_data_payload_ptr(context, builder,
            pzme__wmes)
        simzv__nehr = _get_str_binary_arr_payload(context, builder,
            chnsk__bamn, sig.args[1])
        qbt__opnnr = _get_str_binary_arr_payload(context, builder,
            pzme__wmes, sig.args[0])
        context.nrt.incref(builder, char_arr_type, simzv__nehr.data)
        context.nrt.incref(builder, offset_arr_type, simzv__nehr.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, simzv__nehr.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, qbt__opnnr.data)
        context.nrt.decref(builder, offset_arr_type, qbt__opnnr.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, qbt__opnnr.
            null_bitmap)
        builder.store(builder.load(ief__nwuii), nae__vwq)
        return context.get_dummy_value()
    return types.none(to_arr_typ, from_arr_typ), codegen


dummy_use = numba.njit(lambda a: None)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_utf8_size(s):
    if isinstance(s, types.StringLiteral):
        l = len(s.literal_value.encode())
        return lambda s: l

    def impl(s):
        if s is None:
            return 0
        s = bodo.utils.indexing.unoptional(s)
        if s._is_ascii == 1:
            return len(s)
        ctng__ubdx = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return ctng__ubdx
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, vdx__jrzzj, wbx__czlzw = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder, arr,
            sig.args[0])
        offsets = context.make_helper(builder, offset_arr_type, toswc__vewu
            .offsets).data
        data = context.make_helper(builder, char_arr_type, toswc__vewu.data
            ).data
        qba__sbef = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        bnvg__ibm = cgutils.get_or_insert_function(builder.module,
            qba__sbef, name='setitem_string_array')
        zvtpq__huswd = context.get_constant(types.int32, -1)
        dsgy__qwecb = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets,
            toswc__vewu.n_arrays)
        builder.call(bnvg__ibm, [offsets, data, num_total_chars, builder.
            extract_value(vdx__jrzzj, 0), wbx__czlzw, zvtpq__huswd,
            dsgy__qwecb, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    qba__sbef = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64)])
    uktxq__coc = cgutils.get_or_insert_function(builder.module, qba__sbef,
        name='is_na')
    return builder.call(uktxq__coc, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        vnwy__uew, mak__ylvr, edufo__yql, kgoxb__stlp = args
        cgutils.raw_memcpy(builder, vnwy__uew, mak__ylvr, edufo__yql,
            kgoxb__stlp)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.voidptr, types.intp, types.intp
        ), codegen


@numba.njit
def print_str_arr(arr):
    _print_str_arr(num_strings(arr), num_total_chars(arr), get_offset_ptr(
        arr), get_data_ptr(arr))


def inplace_eq(A, i, val):
    return A[i] == val


@overload(inplace_eq)
def inplace_eq_overload(A, ind, val):

    def impl(A, ind, val):
        kjr__ezt, pxrdf__zfqhh = unicode_to_utf8_and_len(val)
        imd__ksbxh = getitem_str_offset(A, ind)
        opru__sllw = getitem_str_offset(A, ind + 1)
        mylmx__ppf = opru__sllw - imd__ksbxh
        if mylmx__ppf != pxrdf__zfqhh:
            return False
        vdx__jrzzj = get_data_ptr_ind(A, imd__ksbxh)
        return memcmp(vdx__jrzzj, kjr__ezt, pxrdf__zfqhh) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        imd__ksbxh = getitem_str_offset(A, ind)
        mylmx__ppf = bodo.libs.str_ext.int_to_str_len(val)
        hwfg__rskf = imd__ksbxh + mylmx__ppf
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            imd__ksbxh, hwfg__rskf)
        vdx__jrzzj = get_data_ptr_ind(A, imd__ksbxh)
        inplace_int64_to_str(vdx__jrzzj, mylmx__ppf, val)
        setitem_str_offset(A, ind + 1, imd__ksbxh + mylmx__ppf)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        vdx__jrzzj, = args
        bfhbz__fjq = context.insert_const_string(builder.module, '<NA>')
        gvuoa__pbiqc = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, vdx__jrzzj, bfhbz__fjq, gvuoa__pbiqc, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    qeqs__rcjep = len('<NA>')

    def impl(A, ind):
        imd__ksbxh = getitem_str_offset(A, ind)
        hwfg__rskf = imd__ksbxh + qeqs__rcjep
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            imd__ksbxh, hwfg__rskf)
        vdx__jrzzj = get_data_ptr_ind(A, imd__ksbxh)
        inplace_set_NA_str(vdx__jrzzj)
        setitem_str_offset(A, ind + 1, imd__ksbxh + qeqs__rcjep)
        str_arr_set_not_na(A, ind)
    return impl


@overload(operator.getitem, no_unliteral=True)
def str_arr_getitem_int(A, ind):
    if A != string_array_type:
        return
    if isinstance(ind, types.Integer):

        def str_arr_getitem_impl(A, ind):
            if ind < 0:
                ind += A.size
            imd__ksbxh = getitem_str_offset(A, ind)
            opru__sllw = getitem_str_offset(A, ind + 1)
            wbx__czlzw = opru__sllw - imd__ksbxh
            vdx__jrzzj = get_data_ptr_ind(A, imd__ksbxh)
            iipzq__uqthc = decode_utf8(vdx__jrzzj, wbx__czlzw)
            return iipzq__uqthc
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            ctng__ubdx = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(ctng__ubdx):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            hmr__dllc = get_data_ptr(out_arr).data
            uit__uah = get_data_ptr(A).data
            hjmh__dvz = 0
            zmln__tfd = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(ctng__ubdx):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    yzcu__iqsmt = get_str_arr_item_length(A, i)
                    if yzcu__iqsmt == 1:
                        copy_single_char(hmr__dllc, zmln__tfd, uit__uah,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(hmr__dllc, zmln__tfd, uit__uah,
                            getitem_str_offset(A, i), yzcu__iqsmt, 1)
                    zmln__tfd += yzcu__iqsmt
                    setitem_str_offset(out_arr, hjmh__dvz + 1, zmln__tfd)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, hjmh__dvz)
                    else:
                        str_arr_set_not_na(out_arr, hjmh__dvz)
                    hjmh__dvz += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            ctng__ubdx = len(ind)
            out_arr = pre_alloc_string_array(ctng__ubdx, -1)
            hjmh__dvz = 0
            for i in range(ctng__ubdx):
                xsmdg__oien = A[ind[i]]
                out_arr[hjmh__dvz] = xsmdg__oien
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, hjmh__dvz)
                hjmh__dvz += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            ctng__ubdx = len(A)
            nmare__hzv = numba.cpython.unicode._normalize_slice(ind, ctng__ubdx
                )
            zgy__vbs = numba.cpython.unicode._slice_span(nmare__hzv)
            if nmare__hzv.step == 1:
                imd__ksbxh = getitem_str_offset(A, nmare__hzv.start)
                opru__sllw = getitem_str_offset(A, nmare__hzv.stop)
                n_chars = opru__sllw - imd__ksbxh
                dbhk__aoane = pre_alloc_string_array(zgy__vbs, np.int64(
                    n_chars))
                for i in range(zgy__vbs):
                    dbhk__aoane[i] = A[nmare__hzv.start + i]
                    if str_arr_is_na(A, nmare__hzv.start + i):
                        str_arr_set_na(dbhk__aoane, i)
                return dbhk__aoane
            else:
                dbhk__aoane = pre_alloc_string_array(zgy__vbs, -1)
                for i in range(zgy__vbs):
                    dbhk__aoane[i] = A[nmare__hzv.start + i * nmare__hzv.step]
                    if str_arr_is_na(A, nmare__hzv.start + i * nmare__hzv.step
                        ):
                        str_arr_set_na(dbhk__aoane, i)
                return dbhk__aoane
        return str_arr_slice_impl
    raise BodoError(
        f'getitem for StringArray with indexing type {ind} not supported.')


dummy_use = numba.njit(lambda a: None)


@overload(operator.setitem)
def str_arr_setitem(A, idx, val):
    if A != string_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    lvop__fku = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(lvop__fku)
        banoo__ipd = 4

        def impl_scalar(A, idx, val):
            vhln__mbals = (val._length if val._is_ascii else banoo__ipd *
                val._length)
            mtt__myw = A._data
            imd__ksbxh = np.int64(getitem_str_offset(A, idx))
            hwfg__rskf = imd__ksbxh + vhln__mbals
            bodo.libs.array_item_arr_ext.ensure_data_capacity(mtt__myw,
                imd__ksbxh, hwfg__rskf)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                hwfg__rskf, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                nmare__hzv = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                cpoux__myleq = nmare__hzv.start
                mtt__myw = A._data
                imd__ksbxh = np.int64(getitem_str_offset(A, cpoux__myleq))
                hwfg__rskf = imd__ksbxh + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(mtt__myw,
                    imd__ksbxh, hwfg__rskf)
                set_string_array_range(A, val, cpoux__myleq, imd__ksbxh)
                avor__mdsig = 0
                for i in range(nmare__hzv.start, nmare__hzv.stop,
                    nmare__hzv.step):
                    if str_arr_is_na(val, avor__mdsig):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    avor__mdsig += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                fmgv__bxw = str_list_to_array(val)
                A[idx] = fmgv__bxw
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                nmare__hzv = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                for i in range(nmare__hzv.start, nmare__hzv.stop,
                    nmare__hzv.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(lvop__fku)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                ctng__ubdx = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(ctng__ubdx, -1)
                for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        out_arr[i] = val
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_scalar
        elif val == string_array_type or isinstance(val, types.Array
            ) and isinstance(val.dtype, types.UnicodeCharSeq):

            def impl_bool_arr(A, idx, val):
                ctng__ubdx = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(ctng__ubdx, -1)
                sucxg__hpnx = 0
                for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, sucxg__hpnx):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, sucxg__hpnx)
                        else:
                            out_arr[i] = str(val[sucxg__hpnx])
                        sucxg__hpnx += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(lvop__fku)
    raise BodoError(lvop__fku)


@overload_attribute(StringArrayType, 'dtype')
def overload_str_arr_dtype(A):
    return lambda A: pd.StringDtype()


@overload_attribute(StringArrayType, 'ndim')
def overload_str_arr_ndim(A):
    return lambda A: 1


@overload_method(StringArrayType, 'astype', no_unliteral=True)
def overload_str_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "StringArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.Function) and dtype.key[0] == str:
        return lambda A, dtype, copy=True: A
    czugg__tfxnx = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(czugg__tfxnx, (types.Float, types.Integer)
        ) and czugg__tfxnx not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(czugg__tfxnx, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ctng__ubdx = len(A)
            B = np.empty(ctng__ubdx, czugg__tfxnx)
            for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif czugg__tfxnx == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ctng__ubdx = len(A)
            B = np.empty(ctng__ubdx, czugg__tfxnx)
            for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif czugg__tfxnx == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ctng__ubdx = len(A)
            B = np.empty(ctng__ubdx, czugg__tfxnx)
            for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            ctng__ubdx = len(A)
            B = np.empty(ctng__ubdx, czugg__tfxnx)
            for i in numba.parfors.parfor.internal_prange(ctng__ubdx):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        vdx__jrzzj, wbx__czlzw = args
        umnx__flvjn = context.get_python_api(builder)
        nvs__fty = umnx__flvjn.string_from_string_and_size(vdx__jrzzj,
            wbx__czlzw)
        cvh__lrepy = umnx__flvjn.to_native_value(string_type, nvs__fty).value
        aqv__heq = cgutils.create_struct_proxy(string_type)(context,
            builder, cvh__lrepy)
        aqv__heq.hash = aqv__heq.hash.type(-1)
        umnx__flvjn.decref(nvs__fty)
        return aqv__heq._getvalue()
    return string_type(types.voidptr, types.intp), codegen


def get_arr_data_ptr(arr, ind):
    return arr


@overload(get_arr_data_ptr, no_unliteral=True)
def overload_get_arr_data_ptr(arr, ind):
    assert isinstance(types.unliteral(ind), types.Integer)
    if isinstance(arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(arr, ind):
            return bodo.hiframes.split_impl.get_c_arr_ptr(arr._data.ctypes, ind
                )
        return impl_int
    assert isinstance(arr, types.Array)

    def impl_np(arr, ind):
        return bodo.hiframes.split_impl.get_c_arr_ptr(arr.ctypes, ind)
    return impl_np


def set_to_numeric_out_na_err(out_arr, out_ind, err_code):
    pass


@overload(set_to_numeric_out_na_err)
def set_to_numeric_out_na_err_overload(out_arr, out_ind, err_code):
    if isinstance(out_arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(out_arr, out_ind, err_code):
            bodo.libs.int_arr_ext.set_bit_to_arr(out_arr._null_bitmap,
                out_ind, 0 if err_code == -1 else 1)
        return impl_int
    assert isinstance(out_arr, types.Array)
    if isinstance(out_arr.dtype, types.Float):

        def impl_np(out_arr, out_ind, err_code):
            if err_code == -1:
                out_arr[out_ind] = np.nan
        return impl_np
    return lambda out_arr, out_ind, err_code: None


@numba.njit(no_cpython_wrapper=True)
def str_arr_item_to_numeric(out_arr, out_ind, str_arr, ind):
    str_arr = decode_if_dict_array(str_arr)
    err_code = _str_arr_item_to_numeric(get_arr_data_ptr(out_arr, out_ind),
        str_arr, ind, out_arr.dtype)
    set_to_numeric_out_na_err(out_arr, out_ind, err_code)


@intrinsic
def _str_arr_item_to_numeric(typingctx, out_ptr_t, str_arr_t, ind_t,
    out_dtype_t=None):
    assert str_arr_t == string_array_type, '_str_arr_item_to_numeric: str arr expected'
    assert ind_t == types.int64, '_str_arr_item_to_numeric: integer index expected'

    def codegen(context, builder, sig, args):
        pfslk__yzq, arr, ind, zicv__qyefk = args
        toswc__vewu = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, toswc__vewu
            .offsets).data
        data = context.make_helper(builder, char_arr_type, toswc__vewu.data
            ).data
        qba__sbef = lir.FunctionType(lir.IntType(32), [pfslk__yzq.type, lir
            .IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        con__rhod = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            con__rhod = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        fmv__tzwj = cgutils.get_or_insert_function(builder.module,
            qba__sbef, con__rhod)
        return builder.call(fmv__tzwj, [pfslk__yzq, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    tvsy__olp = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    qba__sbef = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer(), lir.IntType(32)])
    vnskj__ulzry = cgutils.get_or_insert_function(c.builder.module,
        qba__sbef, name='string_array_from_sequence')
    eitvf__igs = c.builder.call(vnskj__ulzry, [val, tvsy__olp])
    oky__qgj = ArrayItemArrayType(char_arr_type)
    vkb__zwr = c.context.make_helper(c.builder, oky__qgj)
    vkb__zwr.meminfo = eitvf__igs
    krvl__yjt = c.context.make_helper(c.builder, typ)
    mtt__myw = vkb__zwr._getvalue()
    krvl__yjt.data = mtt__myw
    wskjo__djrac = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(krvl__yjt._getvalue(), is_error=wskjo__djrac)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    ctng__ubdx = len(pyval)
    zmln__tfd = 0
    iqvyh__xrna = np.empty(ctng__ubdx + 1, np_offset_type)
    zadci__fahzk = []
    dgj__acjb = np.empty(ctng__ubdx + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        iqvyh__xrna[i] = zmln__tfd
        rpptj__mmo = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(dgj__acjb, i, int(not rpptj__mmo))
        if rpptj__mmo:
            continue
        cpsti__big = list(s.encode()) if isinstance(s, str) else list(s)
        zadci__fahzk.extend(cpsti__big)
        zmln__tfd += len(cpsti__big)
    iqvyh__xrna[ctng__ubdx] = zmln__tfd
    qduso__dpt = np.array(zadci__fahzk, np.uint8)
    zdrg__zrhnx = context.get_constant(types.int64, ctng__ubdx)
    wslkv__fxjdz = context.get_constant_generic(builder, char_arr_type,
        qduso__dpt)
    tmz__uxqwv = context.get_constant_generic(builder, offset_arr_type,
        iqvyh__xrna)
    osizg__ahp = context.get_constant_generic(builder, null_bitmap_arr_type,
        dgj__acjb)
    toswc__vewu = lir.Constant.literal_struct([zdrg__zrhnx, wslkv__fxjdz,
        tmz__uxqwv, osizg__ahp])
    toswc__vewu = cgutils.global_constant(builder, '.const.payload',
        toswc__vewu).bitcast(cgutils.voidptr_t)
    vrbk__rcm = context.get_constant(types.int64, -1)
    zozcv__vtn = context.get_constant_null(types.voidptr)
    waxo__xolhb = lir.Constant.literal_struct([vrbk__rcm, zozcv__vtn,
        zozcv__vtn, toswc__vewu, vrbk__rcm])
    waxo__xolhb = cgutils.global_constant(builder, '.const.meminfo',
        waxo__xolhb).bitcast(cgutils.voidptr_t)
    mtt__myw = lir.Constant.literal_struct([waxo__xolhb])
    krvl__yjt = lir.Constant.literal_struct([mtt__myw])
    return krvl__yjt


def pre_alloc_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_str_arr_ext_pre_alloc_string_array
    ) = pre_alloc_str_arr_equiv


@overload(glob.glob, no_unliteral=True)
def overload_glob_glob(pathname, recursive=False):

    def _glob_glob_impl(pathname, recursive=False):
        with numba.objmode(l='list_str_type'):
            l = glob.glob(pathname, recursive=recursive)
        return l
    return _glob_glob_impl
