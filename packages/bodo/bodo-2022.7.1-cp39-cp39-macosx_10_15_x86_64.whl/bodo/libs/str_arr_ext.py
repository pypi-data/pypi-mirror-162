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
        hwvxs__ayn = ArrayItemArrayType(char_arr_type)
        sor__sdnl = [('data', hwvxs__ayn)]
        models.StructModel.__init__(self, dmm, fe_type, sor__sdnl)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        gazyf__nne, = args
        irz__tqez = context.make_helper(builder, string_array_type)
        irz__tqez.data = gazyf__nne
        context.nrt.incref(builder, data_typ, gazyf__nne)
        return irz__tqez._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    kutng__ztyjx = c.context.insert_const_string(c.builder.module, 'pandas')
    sqmt__rqbo = c.pyapi.import_module_noblock(kutng__ztyjx)
    gzcdy__band = c.pyapi.call_method(sqmt__rqbo, 'StringDtype', ())
    c.pyapi.decref(sqmt__rqbo)
    return gzcdy__band


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        nodh__acqrg = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs,
            rhs)
        if nodh__acqrg is not None:
            return nodh__acqrg
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                itkj__iufjv = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(itkj__iufjv)
                for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
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
                itkj__iufjv = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(itkj__iufjv)
                for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
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
                itkj__iufjv = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(itkj__iufjv)
                for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
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
    naknt__hsdc = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    jtko__vpsqt = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and jtko__vpsqt or naknt__hsdc and is_str_arr_type(
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
    jfg__aenu = context.make_helper(builder, arr_typ, arr_value)
    hwvxs__ayn = ArrayItemArrayType(char_arr_type)
    qzlzt__dmema = _get_array_item_arr_payload(context, builder, hwvxs__ayn,
        jfg__aenu.data)
    return qzlzt__dmema


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return qzlzt__dmema.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        jko__mbquh = context.make_helper(builder, offset_arr_type,
            qzlzt__dmema.offsets).data
        return _get_num_total_chars(builder, jko__mbquh, qzlzt__dmema.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ckhnh__rqqak = context.make_helper(builder, offset_arr_type,
            qzlzt__dmema.offsets)
        uhvj__vnt = context.make_helper(builder, offset_ctypes_type)
        uhvj__vnt.data = builder.bitcast(ckhnh__rqqak.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        uhvj__vnt.meminfo = ckhnh__rqqak.meminfo
        gzcdy__band = uhvj__vnt._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            gzcdy__band)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        gazyf__nne = context.make_helper(builder, char_arr_type,
            qzlzt__dmema.data)
        uhvj__vnt = context.make_helper(builder, data_ctypes_type)
        uhvj__vnt.data = gazyf__nne.data
        uhvj__vnt.meminfo = gazyf__nne.meminfo
        gzcdy__band = uhvj__vnt._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            gzcdy__band)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        scs__qppoq, ind = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            scs__qppoq, sig.args[0])
        gazyf__nne = context.make_helper(builder, char_arr_type,
            qzlzt__dmema.data)
        uhvj__vnt = context.make_helper(builder, data_ctypes_type)
        uhvj__vnt.data = builder.gep(gazyf__nne.data, [ind])
        uhvj__vnt.meminfo = gazyf__nne.meminfo
        gzcdy__band = uhvj__vnt._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            gzcdy__band)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        gppe__iuxdo, ftq__ccfrg, obe__kxacz, hcplw__knxfw = args
        mbdx__yia = builder.bitcast(builder.gep(gppe__iuxdo, [ftq__ccfrg]),
            lir.IntType(8).as_pointer())
        ceomt__goa = builder.bitcast(builder.gep(obe__kxacz, [hcplw__knxfw]
            ), lir.IntType(8).as_pointer())
        kgle__gvuz = builder.load(ceomt__goa)
        builder.store(kgle__gvuz, mbdx__yia)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        iqfla__pjafv = context.make_helper(builder, null_bitmap_arr_type,
            qzlzt__dmema.null_bitmap)
        uhvj__vnt = context.make_helper(builder, data_ctypes_type)
        uhvj__vnt.data = iqfla__pjafv.data
        uhvj__vnt.meminfo = iqfla__pjafv.meminfo
        gzcdy__band = uhvj__vnt._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            gzcdy__band)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        jko__mbquh = context.make_helper(builder, offset_arr_type,
            qzlzt__dmema.offsets).data
        return builder.load(builder.gep(jko__mbquh, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type,
            qzlzt__dmema.offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        bzxi__uyy, ind = args
        if in_bitmap_typ == data_ctypes_type:
            uhvj__vnt = context.make_helper(builder, data_ctypes_type,
                bzxi__uyy)
            bzxi__uyy = uhvj__vnt.data
        return builder.load(builder.gep(bzxi__uyy, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        bzxi__uyy, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            uhvj__vnt = context.make_helper(builder, data_ctypes_type,
                bzxi__uyy)
            bzxi__uyy = uhvj__vnt.data
        builder.store(val, builder.gep(bzxi__uyy, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        zhuew__mjpb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        owbn__nojhl = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        myesp__demrb = context.make_helper(builder, offset_arr_type,
            zhuew__mjpb.offsets).data
        grei__ghuhc = context.make_helper(builder, offset_arr_type,
            owbn__nojhl.offsets).data
        ppvc__voxzd = context.make_helper(builder, char_arr_type,
            zhuew__mjpb.data).data
        fprd__ygrn = context.make_helper(builder, char_arr_type,
            owbn__nojhl.data).data
        efaz__nrjzu = context.make_helper(builder, null_bitmap_arr_type,
            zhuew__mjpb.null_bitmap).data
        zii__fltch = context.make_helper(builder, null_bitmap_arr_type,
            owbn__nojhl.null_bitmap).data
        mxm__fqxu = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, grei__ghuhc, myesp__demrb, mxm__fqxu)
        cgutils.memcpy(builder, fprd__ygrn, ppvc__voxzd, builder.load(
            builder.gep(myesp__demrb, [ind])))
        vqp__dqxg = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        fytg__jwyd = builder.lshr(vqp__dqxg, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, zii__fltch, efaz__nrjzu, fytg__jwyd)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        zhuew__mjpb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        owbn__nojhl = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        myesp__demrb = context.make_helper(builder, offset_arr_type,
            zhuew__mjpb.offsets).data
        ppvc__voxzd = context.make_helper(builder, char_arr_type,
            zhuew__mjpb.data).data
        fprd__ygrn = context.make_helper(builder, char_arr_type,
            owbn__nojhl.data).data
        num_total_chars = _get_num_total_chars(builder, myesp__demrb,
            zhuew__mjpb.n_arrays)
        cgutils.memcpy(builder, fprd__ygrn, ppvc__voxzd, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        zhuew__mjpb = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        owbn__nojhl = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        myesp__demrb = context.make_helper(builder, offset_arr_type,
            zhuew__mjpb.offsets).data
        grei__ghuhc = context.make_helper(builder, offset_arr_type,
            owbn__nojhl.offsets).data
        efaz__nrjzu = context.make_helper(builder, null_bitmap_arr_type,
            zhuew__mjpb.null_bitmap).data
        itkj__iufjv = zhuew__mjpb.n_arrays
        tqqsr__qsg = context.get_constant(offset_type, 0)
        bfba__rsdy = cgutils.alloca_once_value(builder, tqqsr__qsg)
        with cgutils.for_range(builder, itkj__iufjv) as duxkj__zsg:
            waz__rpnwb = lower_is_na(context, builder, efaz__nrjzu,
                duxkj__zsg.index)
            with cgutils.if_likely(builder, builder.not_(waz__rpnwb)):
                hyy__awn = builder.load(builder.gep(myesp__demrb, [
                    duxkj__zsg.index]))
                wtagf__dmb = builder.load(bfba__rsdy)
                builder.store(hyy__awn, builder.gep(grei__ghuhc, [wtagf__dmb]))
                builder.store(builder.add(wtagf__dmb, lir.Constant(context.
                    get_value_type(offset_type), 1)), bfba__rsdy)
        wtagf__dmb = builder.load(bfba__rsdy)
        hyy__awn = builder.load(builder.gep(myesp__demrb, [itkj__iufjv]))
        builder.store(hyy__awn, builder.gep(grei__ghuhc, [wtagf__dmb]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        ztrdj__dofxf, ind, str, ajs__epak = args
        ztrdj__dofxf = context.make_array(sig.args[0])(context, builder,
            ztrdj__dofxf)
        ypvzt__nvkh = builder.gep(ztrdj__dofxf.data, [ind])
        cgutils.raw_memcpy(builder, ypvzt__nvkh, str, ajs__epak, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        ypvzt__nvkh, ind, pubxt__het, ajs__epak = args
        ypvzt__nvkh = builder.gep(ypvzt__nvkh, [ind])
        cgutils.raw_memcpy(builder, ypvzt__nvkh, pubxt__het, ajs__epak, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            jasso__cynrj = A._data
            return np.int64(getitem_str_offset(jasso__cynrj, idx + 1) -
                getitem_str_offset(jasso__cynrj, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    bgafc__gsect = np.int64(getitem_str_offset(A, i))
    kgj__llpbs = np.int64(getitem_str_offset(A, i + 1))
    l = kgj__llpbs - bgafc__gsect
    fogii__fufyf = get_data_ptr_ind(A, bgafc__gsect)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(fogii__fufyf, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    nzpa__iov = getitem_str_offset(A, i)
    vtsj__vmqdg = getitem_str_offset(A, i + 1)
    ejhp__qrdx = vtsj__vmqdg - nzpa__iov
    ewis__xjxu = getitem_str_offset(B, j)
    hdiy__dvv = ewis__xjxu + ejhp__qrdx
    setitem_str_offset(B, j + 1, hdiy__dvv)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if ejhp__qrdx != 0:
        gazyf__nne = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(gazyf__nne, np.
            int64(ewis__xjxu), np.int64(hdiy__dvv))
        dtuig__xakei = get_data_ptr(B).data
        omm__gmfc = get_data_ptr(A).data
        memcpy_region(dtuig__xakei, ewis__xjxu, omm__gmfc, nzpa__iov,
            ejhp__qrdx, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    itkj__iufjv = len(str_arr)
    semmv__smyd = np.empty(itkj__iufjv, np.bool_)
    for i in range(itkj__iufjv):
        semmv__smyd[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return semmv__smyd


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            itkj__iufjv = len(data)
            l = []
            for i in range(itkj__iufjv):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        odcd__qjav = data.count
        uen__pmap = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(odcd__qjav)]
        if is_overload_true(str_null_bools):
            uen__pmap += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(odcd__qjav) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        afenx__lqy = 'def f(data, str_null_bools=None):\n'
        afenx__lqy += '  return ({}{})\n'.format(', '.join(uen__pmap), ',' if
            odcd__qjav == 1 else '')
        kxfum__obh = {}
        exec(afenx__lqy, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, kxfum__obh)
        fjn__uhtua = kxfum__obh['f']
        return fjn__uhtua
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                itkj__iufjv = len(list_data)
                for i in range(itkj__iufjv):
                    pubxt__het = list_data[i]
                    str_arr[i] = pubxt__het
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                itkj__iufjv = len(list_data)
                for i in range(itkj__iufjv):
                    pubxt__het = list_data[i]
                    str_arr[i] = pubxt__het
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        odcd__qjav = str_arr.count
        msirv__geo = 0
        afenx__lqy = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(odcd__qjav):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                afenx__lqy += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, odcd__qjav + msirv__geo))
                msirv__geo += 1
            else:
                afenx__lqy += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        afenx__lqy += '  return\n'
        kxfum__obh = {}
        exec(afenx__lqy, {'cp_str_list_to_array': cp_str_list_to_array},
            kxfum__obh)
        qhpx__soztz = kxfum__obh['f']
        return qhpx__soztz
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            itkj__iufjv = len(str_list)
            str_arr = pre_alloc_string_array(itkj__iufjv, -1)
            for i in range(itkj__iufjv):
                pubxt__het = str_list[i]
                str_arr[i] = pubxt__het
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            itkj__iufjv = len(A)
            mzir__yvbre = 0
            for i in range(itkj__iufjv):
                pubxt__het = A[i]
                mzir__yvbre += get_utf8_size(pubxt__het)
            return mzir__yvbre
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        itkj__iufjv = len(arr)
        n_chars = num_total_chars(arr)
        sompd__vvl = pre_alloc_string_array(itkj__iufjv, np.int64(n_chars))
        copy_str_arr_slice(sompd__vvl, arr, itkj__iufjv)
        return sompd__vvl
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
    afenx__lqy = 'def f(in_seq):\n'
    afenx__lqy += '    n_strs = len(in_seq)\n'
    afenx__lqy += '    A = pre_alloc_string_array(n_strs, -1)\n'
    afenx__lqy += '    return A\n'
    kxfum__obh = {}
    exec(afenx__lqy, {'pre_alloc_string_array': pre_alloc_string_array},
        kxfum__obh)
    hiimq__rqxzs = kxfum__obh['f']
    return hiimq__rqxzs


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        owza__myuy = 'pre_alloc_binary_array'
    else:
        owza__myuy = 'pre_alloc_string_array'
    afenx__lqy = 'def f(in_seq):\n'
    afenx__lqy += '    n_strs = len(in_seq)\n'
    afenx__lqy += f'    A = {owza__myuy}(n_strs, -1)\n'
    afenx__lqy += '    for i in range(n_strs):\n'
    afenx__lqy += '        A[i] = in_seq[i]\n'
    afenx__lqy += '    return A\n'
    kxfum__obh = {}
    exec(afenx__lqy, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, kxfum__obh)
    hiimq__rqxzs = kxfum__obh['f']
    return hiimq__rqxzs


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xgkw__med = builder.add(qzlzt__dmema.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        dcctf__cas = builder.lshr(lir.Constant(lir.IntType(64), offset_type
            .bitwidth), lir.Constant(lir.IntType(64), 3))
        fytg__jwyd = builder.mul(xgkw__med, dcctf__cas)
        oap__vorr = context.make_array(offset_arr_type)(context, builder,
            qzlzt__dmema.offsets).data
        cgutils.memset(builder, oap__vorr, fytg__jwyd, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        qizv__ffn = qzlzt__dmema.n_arrays
        fytg__jwyd = builder.lshr(builder.add(qizv__ffn, lir.Constant(lir.
            IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        zwv__vkvq = context.make_array(null_bitmap_arr_type)(context,
            builder, qzlzt__dmema.null_bitmap).data
        cgutils.memset(builder, zwv__vkvq, fytg__jwyd, 0)
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
    fyvw__bfd = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        xmv__ees = len(len_arr)
        for i in range(xmv__ees):
            offsets[i] = fyvw__bfd
            fyvw__bfd += len_arr[i]
        offsets[xmv__ees] = fyvw__bfd
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    xmp__pth = i // 8
    eagzr__omjg = getitem_str_bitmap(bits, xmp__pth)
    eagzr__omjg ^= np.uint8(-np.uint8(bit_is_set) ^ eagzr__omjg) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, xmp__pth, eagzr__omjg)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    xos__xiyv = get_null_bitmap_ptr(out_str_arr)
    lqhy__cufcc = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        ivdp__lfv = get_bit_bitmap(lqhy__cufcc, j)
        set_bit_to(xos__xiyv, out_start + j, ivdp__lfv)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, scs__qppoq, xdo__slpa, gfa__kbohx = args
        zhuew__mjpb = _get_str_binary_arr_payload(context, builder,
            scs__qppoq, string_array_type)
        owbn__nojhl = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        myesp__demrb = context.make_helper(builder, offset_arr_type,
            zhuew__mjpb.offsets).data
        grei__ghuhc = context.make_helper(builder, offset_arr_type,
            owbn__nojhl.offsets).data
        ppvc__voxzd = context.make_helper(builder, char_arr_type,
            zhuew__mjpb.data).data
        fprd__ygrn = context.make_helper(builder, char_arr_type,
            owbn__nojhl.data).data
        num_total_chars = _get_num_total_chars(builder, myesp__demrb,
            zhuew__mjpb.n_arrays)
        wyhb__fccr = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        pocv__nupue = cgutils.get_or_insert_function(builder.module,
            wyhb__fccr, name='set_string_array_range')
        builder.call(pocv__nupue, [grei__ghuhc, fprd__ygrn, myesp__demrb,
            ppvc__voxzd, xdo__slpa, gfa__kbohx, zhuew__mjpb.n_arrays,
            num_total_chars])
        oua__glv = context.typing_context.resolve_value_type(copy_nulls_range)
        uqlz__lnqft = oua__glv.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        hqz__mxy = context.get_function(oua__glv, uqlz__lnqft)
        hqz__mxy(builder, (out_arr, scs__qppoq, xdo__slpa))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    dwke__npkyg = c.context.make_helper(c.builder, typ, val)
    hwvxs__ayn = ArrayItemArrayType(char_arr_type)
    qzlzt__dmema = _get_array_item_arr_payload(c.context, c.builder,
        hwvxs__ayn, dwke__npkyg.data)
    gref__tpizs = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    goe__pdcqc = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        goe__pdcqc = 'pd_array_from_string_array'
    wyhb__fccr = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    ehoub__mvs = cgutils.get_or_insert_function(c.builder.module,
        wyhb__fccr, name=goe__pdcqc)
    jko__mbquh = c.context.make_array(offset_arr_type)(c.context, c.builder,
        qzlzt__dmema.offsets).data
    fogii__fufyf = c.context.make_array(char_arr_type)(c.context, c.builder,
        qzlzt__dmema.data).data
    zwv__vkvq = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, qzlzt__dmema.null_bitmap).data
    arr = c.builder.call(ehoub__mvs, [qzlzt__dmema.n_arrays, jko__mbquh,
        fogii__fufyf, zwv__vkvq, gref__tpizs])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        zwv__vkvq = context.make_array(null_bitmap_arr_type)(context,
            builder, qzlzt__dmema.null_bitmap).data
        uhaw__upz = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        adar__zngg = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        eagzr__omjg = builder.load(builder.gep(zwv__vkvq, [uhaw__upz],
            inbounds=True))
        zpj__qsp = lir.ArrayType(lir.IntType(8), 8)
        usb__xbpfs = cgutils.alloca_once_value(builder, lir.Constant(
            zpj__qsp, (1, 2, 4, 8, 16, 32, 64, 128)))
        tqz__qbnw = builder.load(builder.gep(usb__xbpfs, [lir.Constant(lir.
            IntType(64), 0), adar__zngg], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(eagzr__omjg,
            tqz__qbnw), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        uhaw__upz = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        adar__zngg = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        zwv__vkvq = context.make_array(null_bitmap_arr_type)(context,
            builder, qzlzt__dmema.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type,
            qzlzt__dmema.offsets).data
        mdf__fvpr = builder.gep(zwv__vkvq, [uhaw__upz], inbounds=True)
        eagzr__omjg = builder.load(mdf__fvpr)
        zpj__qsp = lir.ArrayType(lir.IntType(8), 8)
        usb__xbpfs = cgutils.alloca_once_value(builder, lir.Constant(
            zpj__qsp, (1, 2, 4, 8, 16, 32, 64, 128)))
        tqz__qbnw = builder.load(builder.gep(usb__xbpfs, [lir.Constant(lir.
            IntType(64), 0), adar__zngg], inbounds=True))
        tqz__qbnw = builder.xor(tqz__qbnw, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(eagzr__omjg, tqz__qbnw), mdf__fvpr)
        if str_arr_typ == string_array_type:
            mgaxf__bzgo = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            yopt__bebrp = builder.icmp_unsigned('!=', mgaxf__bzgo,
                qzlzt__dmema.n_arrays)
            with builder.if_then(yopt__bebrp):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [mgaxf__bzgo]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        uhaw__upz = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        adar__zngg = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        zwv__vkvq = context.make_array(null_bitmap_arr_type)(context,
            builder, qzlzt__dmema.null_bitmap).data
        mdf__fvpr = builder.gep(zwv__vkvq, [uhaw__upz], inbounds=True)
        eagzr__omjg = builder.load(mdf__fvpr)
        zpj__qsp = lir.ArrayType(lir.IntType(8), 8)
        usb__xbpfs = cgutils.alloca_once_value(builder, lir.Constant(
            zpj__qsp, (1, 2, 4, 8, 16, 32, 64, 128)))
        tqz__qbnw = builder.load(builder.gep(usb__xbpfs, [lir.Constant(lir.
            IntType(64), 0), adar__zngg], inbounds=True))
        builder.store(builder.or_(eagzr__omjg, tqz__qbnw), mdf__fvpr)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        fytg__jwyd = builder.udiv(builder.add(qzlzt__dmema.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        zwv__vkvq = context.make_array(null_bitmap_arr_type)(context,
            builder, qzlzt__dmema.null_bitmap).data
        cgutils.memset(builder, zwv__vkvq, fytg__jwyd, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    uco__czoz = context.make_helper(builder, string_array_type, str_arr)
    hwvxs__ayn = ArrayItemArrayType(char_arr_type)
    bdj__ntpk = context.make_helper(builder, hwvxs__ayn, uco__czoz.data)
    zmrjg__eov = ArrayItemArrayPayloadType(hwvxs__ayn)
    lkgca__ernk = context.nrt.meminfo_data(builder, bdj__ntpk.meminfo)
    ahft__trlvn = builder.bitcast(lkgca__ernk, context.get_value_type(
        zmrjg__eov).as_pointer())
    return ahft__trlvn


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        qsft__iidr, xhv__fnc = args
        vlgqh__actlg = _get_str_binary_arr_data_payload_ptr(context,
            builder, xhv__fnc)
        ptf__fahk = _get_str_binary_arr_data_payload_ptr(context, builder,
            qsft__iidr)
        flqy__ior = _get_str_binary_arr_payload(context, builder, xhv__fnc,
            sig.args[1])
        snzl__efv = _get_str_binary_arr_payload(context, builder,
            qsft__iidr, sig.args[0])
        context.nrt.incref(builder, char_arr_type, flqy__ior.data)
        context.nrt.incref(builder, offset_arr_type, flqy__ior.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, flqy__ior.null_bitmap
            )
        context.nrt.decref(builder, char_arr_type, snzl__efv.data)
        context.nrt.decref(builder, offset_arr_type, snzl__efv.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, snzl__efv.null_bitmap
            )
        builder.store(builder.load(vlgqh__actlg), ptf__fahk)
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
        itkj__iufjv = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return itkj__iufjv
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, ypvzt__nvkh, hwlj__uzw = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder, arr,
            sig.args[0])
        offsets = context.make_helper(builder, offset_arr_type,
            qzlzt__dmema.offsets).data
        data = context.make_helper(builder, char_arr_type, qzlzt__dmema.data
            ).data
        wyhb__fccr = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        ama__jnmpd = cgutils.get_or_insert_function(builder.module,
            wyhb__fccr, name='setitem_string_array')
        zguv__iuvl = context.get_constant(types.int32, -1)
        bvqu__qkpnb = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets,
            qzlzt__dmema.n_arrays)
        builder.call(ama__jnmpd, [offsets, data, num_total_chars, builder.
            extract_value(ypvzt__nvkh, 0), hwlj__uzw, zguv__iuvl,
            bvqu__qkpnb, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    wyhb__fccr = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    itsmf__vwm = cgutils.get_or_insert_function(builder.module, wyhb__fccr,
        name='is_na')
    return builder.call(itsmf__vwm, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        mbdx__yia, ceomt__goa, odcd__qjav, ebnd__ncsyz = args
        cgutils.raw_memcpy(builder, mbdx__yia, ceomt__goa, odcd__qjav,
            ebnd__ncsyz)
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
        ivcnm__bfr, gzbuz__gkxu = unicode_to_utf8_and_len(val)
        oxp__ckq = getitem_str_offset(A, ind)
        qze__dbz = getitem_str_offset(A, ind + 1)
        ndub__nyjzp = qze__dbz - oxp__ckq
        if ndub__nyjzp != gzbuz__gkxu:
            return False
        ypvzt__nvkh = get_data_ptr_ind(A, oxp__ckq)
        return memcmp(ypvzt__nvkh, ivcnm__bfr, gzbuz__gkxu) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        oxp__ckq = getitem_str_offset(A, ind)
        ndub__nyjzp = bodo.libs.str_ext.int_to_str_len(val)
        vrvfw__khkg = oxp__ckq + ndub__nyjzp
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data, oxp__ckq,
            vrvfw__khkg)
        ypvzt__nvkh = get_data_ptr_ind(A, oxp__ckq)
        inplace_int64_to_str(ypvzt__nvkh, ndub__nyjzp, val)
        setitem_str_offset(A, ind + 1, oxp__ckq + ndub__nyjzp)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        ypvzt__nvkh, = args
        umcez__cxcds = context.insert_const_string(builder.module, '<NA>')
        bnai__scpo = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, ypvzt__nvkh, umcez__cxcds, bnai__scpo, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    ympj__ipshg = len('<NA>')

    def impl(A, ind):
        oxp__ckq = getitem_str_offset(A, ind)
        vrvfw__khkg = oxp__ckq + ympj__ipshg
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data, oxp__ckq,
            vrvfw__khkg)
        ypvzt__nvkh = get_data_ptr_ind(A, oxp__ckq)
        inplace_set_NA_str(ypvzt__nvkh)
        setitem_str_offset(A, ind + 1, oxp__ckq + ympj__ipshg)
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
            oxp__ckq = getitem_str_offset(A, ind)
            qze__dbz = getitem_str_offset(A, ind + 1)
            hwlj__uzw = qze__dbz - oxp__ckq
            ypvzt__nvkh = get_data_ptr_ind(A, oxp__ckq)
            rauku__tgcv = decode_utf8(ypvzt__nvkh, hwlj__uzw)
            return rauku__tgcv
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            itkj__iufjv = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(itkj__iufjv):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            dtuig__xakei = get_data_ptr(out_arr).data
            omm__gmfc = get_data_ptr(A).data
            msirv__geo = 0
            wtagf__dmb = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(itkj__iufjv):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    ugt__woe = get_str_arr_item_length(A, i)
                    if ugt__woe == 1:
                        copy_single_char(dtuig__xakei, wtagf__dmb,
                            omm__gmfc, getitem_str_offset(A, i))
                    else:
                        memcpy_region(dtuig__xakei, wtagf__dmb, omm__gmfc,
                            getitem_str_offset(A, i), ugt__woe, 1)
                    wtagf__dmb += ugt__woe
                    setitem_str_offset(out_arr, msirv__geo + 1, wtagf__dmb)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, msirv__geo)
                    else:
                        str_arr_set_not_na(out_arr, msirv__geo)
                    msirv__geo += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            itkj__iufjv = len(ind)
            out_arr = pre_alloc_string_array(itkj__iufjv, -1)
            msirv__geo = 0
            for i in range(itkj__iufjv):
                pubxt__het = A[ind[i]]
                out_arr[msirv__geo] = pubxt__het
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, msirv__geo)
                msirv__geo += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            itkj__iufjv = len(A)
            rbzgr__ksghn = numba.cpython.unicode._normalize_slice(ind,
                itkj__iufjv)
            lkc__xzdx = numba.cpython.unicode._slice_span(rbzgr__ksghn)
            if rbzgr__ksghn.step == 1:
                oxp__ckq = getitem_str_offset(A, rbzgr__ksghn.start)
                qze__dbz = getitem_str_offset(A, rbzgr__ksghn.stop)
                n_chars = qze__dbz - oxp__ckq
                sompd__vvl = pre_alloc_string_array(lkc__xzdx, np.int64(
                    n_chars))
                for i in range(lkc__xzdx):
                    sompd__vvl[i] = A[rbzgr__ksghn.start + i]
                    if str_arr_is_na(A, rbzgr__ksghn.start + i):
                        str_arr_set_na(sompd__vvl, i)
                return sompd__vvl
            else:
                sompd__vvl = pre_alloc_string_array(lkc__xzdx, -1)
                for i in range(lkc__xzdx):
                    sompd__vvl[i] = A[rbzgr__ksghn.start + i * rbzgr__ksghn
                        .step]
                    if str_arr_is_na(A, rbzgr__ksghn.start + i *
                        rbzgr__ksghn.step):
                        str_arr_set_na(sompd__vvl, i)
                return sompd__vvl
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
    vwwr__yora = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(vwwr__yora)
        igety__oxubt = 4

        def impl_scalar(A, idx, val):
            phnlf__cbii = (val._length if val._is_ascii else igety__oxubt *
                val._length)
            gazyf__nne = A._data
            oxp__ckq = np.int64(getitem_str_offset(A, idx))
            vrvfw__khkg = oxp__ckq + phnlf__cbii
            bodo.libs.array_item_arr_ext.ensure_data_capacity(gazyf__nne,
                oxp__ckq, vrvfw__khkg)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                vrvfw__khkg, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                rbzgr__ksghn = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                bgafc__gsect = rbzgr__ksghn.start
                gazyf__nne = A._data
                oxp__ckq = np.int64(getitem_str_offset(A, bgafc__gsect))
                vrvfw__khkg = oxp__ckq + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(gazyf__nne,
                    oxp__ckq, vrvfw__khkg)
                set_string_array_range(A, val, bgafc__gsect, oxp__ckq)
                akve__oegu = 0
                for i in range(rbzgr__ksghn.start, rbzgr__ksghn.stop,
                    rbzgr__ksghn.step):
                    if str_arr_is_na(val, akve__oegu):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    akve__oegu += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                ivpq__vwn = str_list_to_array(val)
                A[idx] = ivpq__vwn
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                rbzgr__ksghn = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                for i in range(rbzgr__ksghn.start, rbzgr__ksghn.stop,
                    rbzgr__ksghn.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(vwwr__yora)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                itkj__iufjv = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(itkj__iufjv, -1)
                for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
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
                itkj__iufjv = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(itkj__iufjv, -1)
                pfa__hnrc = 0
                for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, pfa__hnrc):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, pfa__hnrc)
                        else:
                            out_arr[i] = str(val[pfa__hnrc])
                        pfa__hnrc += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(vwwr__yora)
    raise BodoError(vwwr__yora)


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
    zca__bkcrm = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(zca__bkcrm, (types.Float, types.Integer)
        ) and zca__bkcrm not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(zca__bkcrm, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            itkj__iufjv = len(A)
            B = np.empty(itkj__iufjv, zca__bkcrm)
            for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif zca__bkcrm == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            itkj__iufjv = len(A)
            B = np.empty(itkj__iufjv, zca__bkcrm)
            for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif zca__bkcrm == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            itkj__iufjv = len(A)
            B = np.empty(itkj__iufjv, zca__bkcrm)
            for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            itkj__iufjv = len(A)
            B = np.empty(itkj__iufjv, zca__bkcrm)
            for i in numba.parfors.parfor.internal_prange(itkj__iufjv):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        ypvzt__nvkh, hwlj__uzw = args
        ily__wigw = context.get_python_api(builder)
        pnh__tsma = ily__wigw.string_from_string_and_size(ypvzt__nvkh,
            hwlj__uzw)
        fkjot__lrui = ily__wigw.to_native_value(string_type, pnh__tsma).value
        qzbob__wtpma = cgutils.create_struct_proxy(string_type)(context,
            builder, fkjot__lrui)
        qzbob__wtpma.hash = qzbob__wtpma.hash.type(-1)
        ily__wigw.decref(pnh__tsma)
        return qzbob__wtpma._getvalue()
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
        dktti__amtvb, arr, ind, jpy__tmbo = args
        qzlzt__dmema = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type,
            qzlzt__dmema.offsets).data
        data = context.make_helper(builder, char_arr_type, qzlzt__dmema.data
            ).data
        wyhb__fccr = lir.FunctionType(lir.IntType(32), [dktti__amtvb.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        jxbyu__eima = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            jxbyu__eima = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        gns__awm = cgutils.get_or_insert_function(builder.module,
            wyhb__fccr, jxbyu__eima)
        return builder.call(gns__awm, [dktti__amtvb, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    gref__tpizs = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    wyhb__fccr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(32)])
    unky__sbhgt = cgutils.get_or_insert_function(c.builder.module,
        wyhb__fccr, name='string_array_from_sequence')
    zxxy__wpu = c.builder.call(unky__sbhgt, [val, gref__tpizs])
    hwvxs__ayn = ArrayItemArrayType(char_arr_type)
    bdj__ntpk = c.context.make_helper(c.builder, hwvxs__ayn)
    bdj__ntpk.meminfo = zxxy__wpu
    uco__czoz = c.context.make_helper(c.builder, typ)
    gazyf__nne = bdj__ntpk._getvalue()
    uco__czoz.data = gazyf__nne
    ckev__xajbc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uco__czoz._getvalue(), is_error=ckev__xajbc)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    itkj__iufjv = len(pyval)
    wtagf__dmb = 0
    pxwy__oww = np.empty(itkj__iufjv + 1, np_offset_type)
    xcd__csh = []
    scpbo__xiqug = np.empty(itkj__iufjv + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        pxwy__oww[i] = wtagf__dmb
        cnjri__nyl = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(scpbo__xiqug, i, int(not
            cnjri__nyl))
        if cnjri__nyl:
            continue
        tpo__doe = list(s.encode()) if isinstance(s, str) else list(s)
        xcd__csh.extend(tpo__doe)
        wtagf__dmb += len(tpo__doe)
    pxwy__oww[itkj__iufjv] = wtagf__dmb
    mvfod__hho = np.array(xcd__csh, np.uint8)
    nacua__xnan = context.get_constant(types.int64, itkj__iufjv)
    jqvvj__qlsc = context.get_constant_generic(builder, char_arr_type,
        mvfod__hho)
    wpjup__bicc = context.get_constant_generic(builder, offset_arr_type,
        pxwy__oww)
    npgvq__sns = context.get_constant_generic(builder, null_bitmap_arr_type,
        scpbo__xiqug)
    qzlzt__dmema = lir.Constant.literal_struct([nacua__xnan, jqvvj__qlsc,
        wpjup__bicc, npgvq__sns])
    qzlzt__dmema = cgutils.global_constant(builder, '.const.payload',
        qzlzt__dmema).bitcast(cgutils.voidptr_t)
    jzfod__rans = context.get_constant(types.int64, -1)
    antng__nnsjv = context.get_constant_null(types.voidptr)
    lao__ilwul = lir.Constant.literal_struct([jzfod__rans, antng__nnsjv,
        antng__nnsjv, qzlzt__dmema, jzfod__rans])
    lao__ilwul = cgutils.global_constant(builder, '.const.meminfo', lao__ilwul
        ).bitcast(cgutils.voidptr_t)
    gazyf__nne = lir.Constant.literal_struct([lao__ilwul])
    uco__czoz = lir.Constant.literal_struct([gazyf__nne])
    return uco__czoz


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
