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
        qxw__kgoa = ArrayItemArrayType(char_arr_type)
        clws__nzao = [('data', qxw__kgoa)]
        models.StructModel.__init__(self, dmm, fe_type, clws__nzao)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        dmph__xls, = args
        cwvy__jja = context.make_helper(builder, string_array_type)
        cwvy__jja.data = dmph__xls
        context.nrt.incref(builder, data_typ, dmph__xls)
        return cwvy__jja._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    yyc__cam = c.context.insert_const_string(c.builder.module, 'pandas')
    wgok__ailcb = c.pyapi.import_module_noblock(yyc__cam)
    aalh__lvvan = c.pyapi.call_method(wgok__ailcb, 'StringDtype', ())
    c.pyapi.decref(wgok__ailcb)
    return aalh__lvvan


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        zctjr__qwd = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs
            )
        if zctjr__qwd is not None:
            return zctjr__qwd
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                xsoo__dsszb = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(xsoo__dsszb)
                for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
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
                xsoo__dsszb = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(xsoo__dsszb)
                for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
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
                xsoo__dsszb = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(xsoo__dsszb)
                for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
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
    vpk__nkqf = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    cdp__yjzyo = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and cdp__yjzyo or vpk__nkqf and is_str_arr_type(rhs
        ):

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
    rat__qvg = context.make_helper(builder, arr_typ, arr_value)
    qxw__kgoa = ArrayItemArrayType(char_arr_type)
    sdwvc__bhahg = _get_array_item_arr_payload(context, builder, qxw__kgoa,
        rat__qvg.data)
    return sdwvc__bhahg


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return sdwvc__bhahg.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        qlmn__puzj = context.make_helper(builder, offset_arr_type,
            sdwvc__bhahg.offsets).data
        return _get_num_total_chars(builder, qlmn__puzj, sdwvc__bhahg.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        zgxv__vhk = context.make_helper(builder, offset_arr_type,
            sdwvc__bhahg.offsets)
        xocus__mbeez = context.make_helper(builder, offset_ctypes_type)
        xocus__mbeez.data = builder.bitcast(zgxv__vhk.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        xocus__mbeez.meminfo = zgxv__vhk.meminfo
        aalh__lvvan = xocus__mbeez._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            aalh__lvvan)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        dmph__xls = context.make_helper(builder, char_arr_type,
            sdwvc__bhahg.data)
        xocus__mbeez = context.make_helper(builder, data_ctypes_type)
        xocus__mbeez.data = dmph__xls.data
        xocus__mbeez.meminfo = dmph__xls.meminfo
        aalh__lvvan = xocus__mbeez._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            aalh__lvvan)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        ghsk__kkboo, ind = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            ghsk__kkboo, sig.args[0])
        dmph__xls = context.make_helper(builder, char_arr_type,
            sdwvc__bhahg.data)
        xocus__mbeez = context.make_helper(builder, data_ctypes_type)
        xocus__mbeez.data = builder.gep(dmph__xls.data, [ind])
        xocus__mbeez.meminfo = dmph__xls.meminfo
        aalh__lvvan = xocus__mbeez._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            aalh__lvvan)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        agtw__blz, tgog__mgme, eth__rme, wdci__oxkow = args
        ezbvh__isal = builder.bitcast(builder.gep(agtw__blz, [tgog__mgme]),
            lir.IntType(8).as_pointer())
        hpqew__vltz = builder.bitcast(builder.gep(eth__rme, [wdci__oxkow]),
            lir.IntType(8).as_pointer())
        ebss__peiud = builder.load(hpqew__vltz)
        builder.store(ebss__peiud, ezbvh__isal)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        tno__mixj = context.make_helper(builder, null_bitmap_arr_type,
            sdwvc__bhahg.null_bitmap)
        xocus__mbeez = context.make_helper(builder, data_ctypes_type)
        xocus__mbeez.data = tno__mixj.data
        xocus__mbeez.meminfo = tno__mixj.meminfo
        aalh__lvvan = xocus__mbeez._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            aalh__lvvan)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        qlmn__puzj = context.make_helper(builder, offset_arr_type,
            sdwvc__bhahg.offsets).data
        return builder.load(builder.gep(qlmn__puzj, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type,
            sdwvc__bhahg.offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        xed__top, ind = args
        if in_bitmap_typ == data_ctypes_type:
            xocus__mbeez = context.make_helper(builder, data_ctypes_type,
                xed__top)
            xed__top = xocus__mbeez.data
        return builder.load(builder.gep(xed__top, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        xed__top, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            xocus__mbeez = context.make_helper(builder, data_ctypes_type,
                xed__top)
            xed__top = xocus__mbeez.data
        builder.store(val, builder.gep(xed__top, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        kmdm__kibbl = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        cktp__lvxvm = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        nqpib__ekej = context.make_helper(builder, offset_arr_type,
            kmdm__kibbl.offsets).data
        iuhj__xyn = context.make_helper(builder, offset_arr_type,
            cktp__lvxvm.offsets).data
        yxme__vyfk = context.make_helper(builder, char_arr_type,
            kmdm__kibbl.data).data
        mdg__txw = context.make_helper(builder, char_arr_type, cktp__lvxvm.data
            ).data
        vtzfb__trhvj = context.make_helper(builder, null_bitmap_arr_type,
            kmdm__kibbl.null_bitmap).data
        rlxbq__jgm = context.make_helper(builder, null_bitmap_arr_type,
            cktp__lvxvm.null_bitmap).data
        zunwz__xacgw = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, iuhj__xyn, nqpib__ekej, zunwz__xacgw)
        cgutils.memcpy(builder, mdg__txw, yxme__vyfk, builder.load(builder.
            gep(nqpib__ekej, [ind])))
        iok__tuj = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        iky__itlb = builder.lshr(iok__tuj, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, rlxbq__jgm, vtzfb__trhvj, iky__itlb)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        kmdm__kibbl = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        cktp__lvxvm = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        nqpib__ekej = context.make_helper(builder, offset_arr_type,
            kmdm__kibbl.offsets).data
        yxme__vyfk = context.make_helper(builder, char_arr_type,
            kmdm__kibbl.data).data
        mdg__txw = context.make_helper(builder, char_arr_type, cktp__lvxvm.data
            ).data
        num_total_chars = _get_num_total_chars(builder, nqpib__ekej,
            kmdm__kibbl.n_arrays)
        cgutils.memcpy(builder, mdg__txw, yxme__vyfk, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        kmdm__kibbl = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        cktp__lvxvm = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        nqpib__ekej = context.make_helper(builder, offset_arr_type,
            kmdm__kibbl.offsets).data
        iuhj__xyn = context.make_helper(builder, offset_arr_type,
            cktp__lvxvm.offsets).data
        vtzfb__trhvj = context.make_helper(builder, null_bitmap_arr_type,
            kmdm__kibbl.null_bitmap).data
        xsoo__dsszb = kmdm__kibbl.n_arrays
        svyt__cnnit = context.get_constant(offset_type, 0)
        axzkw__ewgsx = cgutils.alloca_once_value(builder, svyt__cnnit)
        with cgutils.for_range(builder, xsoo__dsszb) as tilxf__mqrac:
            kvyqn__wfeqp = lower_is_na(context, builder, vtzfb__trhvj,
                tilxf__mqrac.index)
            with cgutils.if_likely(builder, builder.not_(kvyqn__wfeqp)):
                exbm__fzg = builder.load(builder.gep(nqpib__ekej, [
                    tilxf__mqrac.index]))
                knao__noe = builder.load(axzkw__ewgsx)
                builder.store(exbm__fzg, builder.gep(iuhj__xyn, [knao__noe]))
                builder.store(builder.add(knao__noe, lir.Constant(context.
                    get_value_type(offset_type), 1)), axzkw__ewgsx)
        knao__noe = builder.load(axzkw__ewgsx)
        exbm__fzg = builder.load(builder.gep(nqpib__ekej, [xsoo__dsszb]))
        builder.store(exbm__fzg, builder.gep(iuhj__xyn, [knao__noe]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        yvjdy__dvrs, ind, str, anrxs__ppyj = args
        yvjdy__dvrs = context.make_array(sig.args[0])(context, builder,
            yvjdy__dvrs)
        peqbb__thfk = builder.gep(yvjdy__dvrs.data, [ind])
        cgutils.raw_memcpy(builder, peqbb__thfk, str, anrxs__ppyj, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        peqbb__thfk, ind, mluga__fbtq, anrxs__ppyj = args
        peqbb__thfk = builder.gep(peqbb__thfk, [ind])
        cgutils.raw_memcpy(builder, peqbb__thfk, mluga__fbtq, anrxs__ppyj, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            zdr__cish = A._data
            return np.int64(getitem_str_offset(zdr__cish, idx + 1) -
                getitem_str_offset(zdr__cish, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    cpc__iua = np.int64(getitem_str_offset(A, i))
    bgtfq__ocw = np.int64(getitem_str_offset(A, i + 1))
    l = bgtfq__ocw - cpc__iua
    wgly__yvnql = get_data_ptr_ind(A, cpc__iua)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(wgly__yvnql, j) >= 128:
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
        cndg__ajvns = 'in_str_arr = A._data'
        mndfg__oxg = 'input_index = A._indices[i]'
    else:
        cndg__ajvns = 'in_str_arr = A'
        mndfg__oxg = 'input_index = i'
    ewbjq__cif = f"""def impl(B, j, A, i):
        if j == 0:
            setitem_str_offset(B, 0, 0)

        {cndg__ajvns}
        {mndfg__oxg}

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
    vtmat__hlbt = {}
    exec(ewbjq__cif, {'setitem_str_offset': setitem_str_offset,
        'memcpy_region': memcpy_region, 'getitem_str_offset':
        getitem_str_offset, 'str_arr_set_na': str_arr_set_na,
        'str_arr_set_not_na': str_arr_set_not_na, 'get_data_ptr':
        get_data_ptr, 'bodo': bodo, 'np': np}, vtmat__hlbt)
    impl = vtmat__hlbt['impl']
    return impl


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    xsoo__dsszb = len(str_arr)
    gsjcn__ofvm = np.empty(xsoo__dsszb, np.bool_)
    for i in range(xsoo__dsszb):
        gsjcn__ofvm[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return gsjcn__ofvm


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            xsoo__dsszb = len(data)
            l = []
            for i in range(xsoo__dsszb):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        oeenb__axg = data.count
        efibg__ewh = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(oeenb__axg)]
        if is_overload_true(str_null_bools):
            efibg__ewh += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(oeenb__axg) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        ewbjq__cif = 'def f(data, str_null_bools=None):\n'
        ewbjq__cif += '  return ({}{})\n'.format(', '.join(efibg__ewh), ',' if
            oeenb__axg == 1 else '')
        vtmat__hlbt = {}
        exec(ewbjq__cif, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, vtmat__hlbt)
        gaej__nkt = vtmat__hlbt['f']
        return gaej__nkt
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                xsoo__dsszb = len(list_data)
                for i in range(xsoo__dsszb):
                    mluga__fbtq = list_data[i]
                    str_arr[i] = mluga__fbtq
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                xsoo__dsszb = len(list_data)
                for i in range(xsoo__dsszb):
                    mluga__fbtq = list_data[i]
                    str_arr[i] = mluga__fbtq
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        oeenb__axg = str_arr.count
        rvl__rsxif = 0
        ewbjq__cif = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(oeenb__axg):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                ewbjq__cif += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, oeenb__axg + rvl__rsxif))
                rvl__rsxif += 1
            else:
                ewbjq__cif += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        ewbjq__cif += '  return\n'
        vtmat__hlbt = {}
        exec(ewbjq__cif, {'cp_str_list_to_array': cp_str_list_to_array},
            vtmat__hlbt)
        qaw__xebe = vtmat__hlbt['f']
        return qaw__xebe
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            xsoo__dsszb = len(str_list)
            str_arr = pre_alloc_string_array(xsoo__dsszb, -1)
            for i in range(xsoo__dsszb):
                mluga__fbtq = str_list[i]
                str_arr[i] = mluga__fbtq
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            xsoo__dsszb = len(A)
            auqdx__jide = 0
            for i in range(xsoo__dsszb):
                mluga__fbtq = A[i]
                auqdx__jide += get_utf8_size(mluga__fbtq)
            return auqdx__jide
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        xsoo__dsszb = len(arr)
        n_chars = num_total_chars(arr)
        sutn__iwhkm = pre_alloc_string_array(xsoo__dsszb, np.int64(n_chars))
        copy_str_arr_slice(sutn__iwhkm, arr, xsoo__dsszb)
        return sutn__iwhkm
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
    ewbjq__cif = 'def f(in_seq):\n'
    ewbjq__cif += '    n_strs = len(in_seq)\n'
    ewbjq__cif += '    A = pre_alloc_string_array(n_strs, -1)\n'
    ewbjq__cif += '    return A\n'
    vtmat__hlbt = {}
    exec(ewbjq__cif, {'pre_alloc_string_array': pre_alloc_string_array},
        vtmat__hlbt)
    wba__mdkrq = vtmat__hlbt['f']
    return wba__mdkrq


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        hnv__ggs = 'pre_alloc_binary_array'
    else:
        hnv__ggs = 'pre_alloc_string_array'
    ewbjq__cif = 'def f(in_seq):\n'
    ewbjq__cif += '    n_strs = len(in_seq)\n'
    ewbjq__cif += f'    A = {hnv__ggs}(n_strs, -1)\n'
    ewbjq__cif += '    for i in range(n_strs):\n'
    ewbjq__cif += '        A[i] = in_seq[i]\n'
    ewbjq__cif += '    return A\n'
    vtmat__hlbt = {}
    exec(ewbjq__cif, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, vtmat__hlbt)
    wba__mdkrq = vtmat__hlbt['f']
    return wba__mdkrq


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        epw__vsag = builder.add(sdwvc__bhahg.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        gzjfs__txk = builder.lshr(lir.Constant(lir.IntType(64), offset_type
            .bitwidth), lir.Constant(lir.IntType(64), 3))
        iky__itlb = builder.mul(epw__vsag, gzjfs__txk)
        lcdj__iwtgf = context.make_array(offset_arr_type)(context, builder,
            sdwvc__bhahg.offsets).data
        cgutils.memset(builder, lcdj__iwtgf, iky__itlb, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ffuoq__phb = sdwvc__bhahg.n_arrays
        iky__itlb = builder.lshr(builder.add(ffuoq__phb, lir.Constant(lir.
            IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        odzf__bbp = context.make_array(null_bitmap_arr_type)(context,
            builder, sdwvc__bhahg.null_bitmap).data
        cgutils.memset(builder, odzf__bbp, iky__itlb, 0)
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
    pwq__qotrk = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        ejln__adxt = len(len_arr)
        for i in range(ejln__adxt):
            offsets[i] = pwq__qotrk
            pwq__qotrk += len_arr[i]
        offsets[ejln__adxt] = pwq__qotrk
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    uip__uai = i // 8
    adi__pmcbv = getitem_str_bitmap(bits, uip__uai)
    adi__pmcbv ^= np.uint8(-np.uint8(bit_is_set) ^ adi__pmcbv) & kBitmask[i % 8
        ]
    setitem_str_bitmap(bits, uip__uai, adi__pmcbv)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    pzyxk__blt = get_null_bitmap_ptr(out_str_arr)
    ajwq__qtrj = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        pkqr__plb = get_bit_bitmap(ajwq__qtrj, j)
        set_bit_to(pzyxk__blt, out_start + j, pkqr__plb)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, ghsk__kkboo, svkg__jlzos, qamb__tup = args
        kmdm__kibbl = _get_str_binary_arr_payload(context, builder,
            ghsk__kkboo, string_array_type)
        cktp__lvxvm = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        nqpib__ekej = context.make_helper(builder, offset_arr_type,
            kmdm__kibbl.offsets).data
        iuhj__xyn = context.make_helper(builder, offset_arr_type,
            cktp__lvxvm.offsets).data
        yxme__vyfk = context.make_helper(builder, char_arr_type,
            kmdm__kibbl.data).data
        mdg__txw = context.make_helper(builder, char_arr_type, cktp__lvxvm.data
            ).data
        num_total_chars = _get_num_total_chars(builder, nqpib__ekej,
            kmdm__kibbl.n_arrays)
        rseoj__uxwv = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        qhem__rene = cgutils.get_or_insert_function(builder.module,
            rseoj__uxwv, name='set_string_array_range')
        builder.call(qhem__rene, [iuhj__xyn, mdg__txw, nqpib__ekej,
            yxme__vyfk, svkg__jlzos, qamb__tup, kmdm__kibbl.n_arrays,
            num_total_chars])
        bmv__ixiw = context.typing_context.resolve_value_type(copy_nulls_range)
        ymr__mrbtu = bmv__ixiw.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        ngsm__eai = context.get_function(bmv__ixiw, ymr__mrbtu)
        ngsm__eai(builder, (out_arr, ghsk__kkboo, svkg__jlzos))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    hfxx__cqkwg = c.context.make_helper(c.builder, typ, val)
    qxw__kgoa = ArrayItemArrayType(char_arr_type)
    sdwvc__bhahg = _get_array_item_arr_payload(c.context, c.builder,
        qxw__kgoa, hfxx__cqkwg.data)
    vdqbf__rxpcp = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    eqa__wzk = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        eqa__wzk = 'pd_array_from_string_array'
    rseoj__uxwv = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    mufb__mzf = cgutils.get_or_insert_function(c.builder.module,
        rseoj__uxwv, name=eqa__wzk)
    qlmn__puzj = c.context.make_array(offset_arr_type)(c.context, c.builder,
        sdwvc__bhahg.offsets).data
    wgly__yvnql = c.context.make_array(char_arr_type)(c.context, c.builder,
        sdwvc__bhahg.data).data
    odzf__bbp = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, sdwvc__bhahg.null_bitmap).data
    arr = c.builder.call(mufb__mzf, [sdwvc__bhahg.n_arrays, qlmn__puzj,
        wgly__yvnql, odzf__bbp, vdqbf__rxpcp])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        odzf__bbp = context.make_array(null_bitmap_arr_type)(context,
            builder, sdwvc__bhahg.null_bitmap).data
        sqwen__didi = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        kbp__wfe = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        adi__pmcbv = builder.load(builder.gep(odzf__bbp, [sqwen__didi],
            inbounds=True))
        jswjy__dvodf = lir.ArrayType(lir.IntType(8), 8)
        eojlv__dtru = cgutils.alloca_once_value(builder, lir.Constant(
            jswjy__dvodf, (1, 2, 4, 8, 16, 32, 64, 128)))
        dxcn__jfgq = builder.load(builder.gep(eojlv__dtru, [lir.Constant(
            lir.IntType(64), 0), kbp__wfe], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(adi__pmcbv,
            dxcn__jfgq), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        sqwen__didi = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        kbp__wfe = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        odzf__bbp = context.make_array(null_bitmap_arr_type)(context,
            builder, sdwvc__bhahg.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type,
            sdwvc__bhahg.offsets).data
        xpy__hir = builder.gep(odzf__bbp, [sqwen__didi], inbounds=True)
        adi__pmcbv = builder.load(xpy__hir)
        jswjy__dvodf = lir.ArrayType(lir.IntType(8), 8)
        eojlv__dtru = cgutils.alloca_once_value(builder, lir.Constant(
            jswjy__dvodf, (1, 2, 4, 8, 16, 32, 64, 128)))
        dxcn__jfgq = builder.load(builder.gep(eojlv__dtru, [lir.Constant(
            lir.IntType(64), 0), kbp__wfe], inbounds=True))
        dxcn__jfgq = builder.xor(dxcn__jfgq, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(adi__pmcbv, dxcn__jfgq), xpy__hir)
        if str_arr_typ == string_array_type:
            huxn__kozq = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            itti__lhfwn = builder.icmp_unsigned('!=', huxn__kozq,
                sdwvc__bhahg.n_arrays)
            with builder.if_then(itti__lhfwn):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [huxn__kozq]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        sqwen__didi = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        kbp__wfe = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        odzf__bbp = context.make_array(null_bitmap_arr_type)(context,
            builder, sdwvc__bhahg.null_bitmap).data
        xpy__hir = builder.gep(odzf__bbp, [sqwen__didi], inbounds=True)
        adi__pmcbv = builder.load(xpy__hir)
        jswjy__dvodf = lir.ArrayType(lir.IntType(8), 8)
        eojlv__dtru = cgutils.alloca_once_value(builder, lir.Constant(
            jswjy__dvodf, (1, 2, 4, 8, 16, 32, 64, 128)))
        dxcn__jfgq = builder.load(builder.gep(eojlv__dtru, [lir.Constant(
            lir.IntType(64), 0), kbp__wfe], inbounds=True))
        builder.store(builder.or_(adi__pmcbv, dxcn__jfgq), xpy__hir)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        iky__itlb = builder.udiv(builder.add(sdwvc__bhahg.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        odzf__bbp = context.make_array(null_bitmap_arr_type)(context,
            builder, sdwvc__bhahg.null_bitmap).data
        cgutils.memset(builder, odzf__bbp, iky__itlb, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    tjevd__xlqz = context.make_helper(builder, string_array_type, str_arr)
    qxw__kgoa = ArrayItemArrayType(char_arr_type)
    cesl__odpia = context.make_helper(builder, qxw__kgoa, tjevd__xlqz.data)
    jtf__zzcr = ArrayItemArrayPayloadType(qxw__kgoa)
    chs__vii = context.nrt.meminfo_data(builder, cesl__odpia.meminfo)
    inb__ceqrp = builder.bitcast(chs__vii, context.get_value_type(jtf__zzcr
        ).as_pointer())
    return inb__ceqrp


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        bvz__ajpr, ugqe__pbeg = args
        yrg__jxzri = _get_str_binary_arr_data_payload_ptr(context, builder,
            ugqe__pbeg)
        gukke__beuid = _get_str_binary_arr_data_payload_ptr(context,
            builder, bvz__ajpr)
        ocdww__iab = _get_str_binary_arr_payload(context, builder,
            ugqe__pbeg, sig.args[1])
        ktemw__jkjt = _get_str_binary_arr_payload(context, builder,
            bvz__ajpr, sig.args[0])
        context.nrt.incref(builder, char_arr_type, ocdww__iab.data)
        context.nrt.incref(builder, offset_arr_type, ocdww__iab.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, ocdww__iab.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, ktemw__jkjt.data)
        context.nrt.decref(builder, offset_arr_type, ktemw__jkjt.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, ktemw__jkjt.
            null_bitmap)
        builder.store(builder.load(yrg__jxzri), gukke__beuid)
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
        xsoo__dsszb = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return xsoo__dsszb
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, peqbb__thfk, eag__dwbj = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder, arr,
            sig.args[0])
        offsets = context.make_helper(builder, offset_arr_type,
            sdwvc__bhahg.offsets).data
        data = context.make_helper(builder, char_arr_type, sdwvc__bhahg.data
            ).data
        rseoj__uxwv = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        geh__tppmp = cgutils.get_or_insert_function(builder.module,
            rseoj__uxwv, name='setitem_string_array')
        inp__wtrj = context.get_constant(types.int32, -1)
        zvb__ayyqv = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets,
            sdwvc__bhahg.n_arrays)
        builder.call(geh__tppmp, [offsets, data, num_total_chars, builder.
            extract_value(peqbb__thfk, 0), eag__dwbj, inp__wtrj, zvb__ayyqv,
            ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    rseoj__uxwv = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    etbjr__rdclu = cgutils.get_or_insert_function(builder.module,
        rseoj__uxwv, name='is_na')
    return builder.call(etbjr__rdclu, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        ezbvh__isal, hpqew__vltz, oeenb__axg, cqxg__kecby = args
        cgutils.raw_memcpy(builder, ezbvh__isal, hpqew__vltz, oeenb__axg,
            cqxg__kecby)
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
        buuk__rqw, kjm__yvsm = unicode_to_utf8_and_len(val)
        cpmn__cgmvp = getitem_str_offset(A, ind)
        jlxc__ppfq = getitem_str_offset(A, ind + 1)
        oiig__jxyh = jlxc__ppfq - cpmn__cgmvp
        if oiig__jxyh != kjm__yvsm:
            return False
        peqbb__thfk = get_data_ptr_ind(A, cpmn__cgmvp)
        return memcmp(peqbb__thfk, buuk__rqw, kjm__yvsm) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        cpmn__cgmvp = getitem_str_offset(A, ind)
        oiig__jxyh = bodo.libs.str_ext.int_to_str_len(val)
        icmpu__zay = cpmn__cgmvp + oiig__jxyh
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            cpmn__cgmvp, icmpu__zay)
        peqbb__thfk = get_data_ptr_ind(A, cpmn__cgmvp)
        inplace_int64_to_str(peqbb__thfk, oiig__jxyh, val)
        setitem_str_offset(A, ind + 1, cpmn__cgmvp + oiig__jxyh)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        peqbb__thfk, = args
        lfh__tel = context.insert_const_string(builder.module, '<NA>')
        kqt__zfoi = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, peqbb__thfk, lfh__tel, kqt__zfoi, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    eqv__fmsa = len('<NA>')

    def impl(A, ind):
        cpmn__cgmvp = getitem_str_offset(A, ind)
        icmpu__zay = cpmn__cgmvp + eqv__fmsa
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            cpmn__cgmvp, icmpu__zay)
        peqbb__thfk = get_data_ptr_ind(A, cpmn__cgmvp)
        inplace_set_NA_str(peqbb__thfk)
        setitem_str_offset(A, ind + 1, cpmn__cgmvp + eqv__fmsa)
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
            cpmn__cgmvp = getitem_str_offset(A, ind)
            jlxc__ppfq = getitem_str_offset(A, ind + 1)
            eag__dwbj = jlxc__ppfq - cpmn__cgmvp
            peqbb__thfk = get_data_ptr_ind(A, cpmn__cgmvp)
            qmes__ewg = decode_utf8(peqbb__thfk, eag__dwbj)
            return qmes__ewg
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            xsoo__dsszb = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(xsoo__dsszb):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            biyeo__vcmf = get_data_ptr(out_arr).data
            odktq__wmm = get_data_ptr(A).data
            rvl__rsxif = 0
            knao__noe = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(xsoo__dsszb):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    wyj__zexhf = get_str_arr_item_length(A, i)
                    if wyj__zexhf == 1:
                        copy_single_char(biyeo__vcmf, knao__noe, odktq__wmm,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(biyeo__vcmf, knao__noe, odktq__wmm,
                            getitem_str_offset(A, i), wyj__zexhf, 1)
                    knao__noe += wyj__zexhf
                    setitem_str_offset(out_arr, rvl__rsxif + 1, knao__noe)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, rvl__rsxif)
                    else:
                        str_arr_set_not_na(out_arr, rvl__rsxif)
                    rvl__rsxif += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            xsoo__dsszb = len(ind)
            out_arr = pre_alloc_string_array(xsoo__dsszb, -1)
            rvl__rsxif = 0
            for i in range(xsoo__dsszb):
                mluga__fbtq = A[ind[i]]
                out_arr[rvl__rsxif] = mluga__fbtq
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, rvl__rsxif)
                rvl__rsxif += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            xsoo__dsszb = len(A)
            xpd__mbgi = numba.cpython.unicode._normalize_slice(ind, xsoo__dsszb
                )
            azf__ojvi = numba.cpython.unicode._slice_span(xpd__mbgi)
            if xpd__mbgi.step == 1:
                cpmn__cgmvp = getitem_str_offset(A, xpd__mbgi.start)
                jlxc__ppfq = getitem_str_offset(A, xpd__mbgi.stop)
                n_chars = jlxc__ppfq - cpmn__cgmvp
                sutn__iwhkm = pre_alloc_string_array(azf__ojvi, np.int64(
                    n_chars))
                for i in range(azf__ojvi):
                    sutn__iwhkm[i] = A[xpd__mbgi.start + i]
                    if str_arr_is_na(A, xpd__mbgi.start + i):
                        str_arr_set_na(sutn__iwhkm, i)
                return sutn__iwhkm
            else:
                sutn__iwhkm = pre_alloc_string_array(azf__ojvi, -1)
                for i in range(azf__ojvi):
                    sutn__iwhkm[i] = A[xpd__mbgi.start + i * xpd__mbgi.step]
                    if str_arr_is_na(A, xpd__mbgi.start + i * xpd__mbgi.step):
                        str_arr_set_na(sutn__iwhkm, i)
                return sutn__iwhkm
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
    rpo__zwtjl = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(rpo__zwtjl)
        bgoss__mjjub = 4

        def impl_scalar(A, idx, val):
            nmi__eks = (val._length if val._is_ascii else bgoss__mjjub *
                val._length)
            dmph__xls = A._data
            cpmn__cgmvp = np.int64(getitem_str_offset(A, idx))
            icmpu__zay = cpmn__cgmvp + nmi__eks
            bodo.libs.array_item_arr_ext.ensure_data_capacity(dmph__xls,
                cpmn__cgmvp, icmpu__zay)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                icmpu__zay, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                xpd__mbgi = numba.cpython.unicode._normalize_slice(idx, len(A))
                cpc__iua = xpd__mbgi.start
                dmph__xls = A._data
                cpmn__cgmvp = np.int64(getitem_str_offset(A, cpc__iua))
                icmpu__zay = cpmn__cgmvp + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(dmph__xls,
                    cpmn__cgmvp, icmpu__zay)
                set_string_array_range(A, val, cpc__iua, cpmn__cgmvp)
                vlro__aelz = 0
                for i in range(xpd__mbgi.start, xpd__mbgi.stop, xpd__mbgi.step
                    ):
                    if str_arr_is_na(val, vlro__aelz):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    vlro__aelz += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                ursbd__nlst = str_list_to_array(val)
                A[idx] = ursbd__nlst
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                xpd__mbgi = numba.cpython.unicode._normalize_slice(idx, len(A))
                for i in range(xpd__mbgi.start, xpd__mbgi.stop, xpd__mbgi.step
                    ):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(rpo__zwtjl)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                xsoo__dsszb = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(xsoo__dsszb, -1)
                for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
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
                xsoo__dsszb = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(xsoo__dsszb, -1)
                ietd__fclp = 0
                for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, ietd__fclp):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, ietd__fclp)
                        else:
                            out_arr[i] = str(val[ietd__fclp])
                        ietd__fclp += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(rpo__zwtjl)
    raise BodoError(rpo__zwtjl)


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
    pax__pwd = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(pax__pwd, (types.Float, types.Integer)
        ) and pax__pwd not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(pax__pwd, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            xsoo__dsszb = len(A)
            B = np.empty(xsoo__dsszb, pax__pwd)
            for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif pax__pwd == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            xsoo__dsszb = len(A)
            B = np.empty(xsoo__dsszb, pax__pwd)
            for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif pax__pwd == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            xsoo__dsszb = len(A)
            B = np.empty(xsoo__dsszb, pax__pwd)
            for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            xsoo__dsszb = len(A)
            B = np.empty(xsoo__dsszb, pax__pwd)
            for i in numba.parfors.parfor.internal_prange(xsoo__dsszb):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        peqbb__thfk, eag__dwbj = args
        fegd__srmcz = context.get_python_api(builder)
        pltuy__inclb = fegd__srmcz.string_from_string_and_size(peqbb__thfk,
            eag__dwbj)
        sbs__ytqsf = fegd__srmcz.to_native_value(string_type, pltuy__inclb
            ).value
        llue__qsbb = cgutils.create_struct_proxy(string_type)(context,
            builder, sbs__ytqsf)
        llue__qsbb.hash = llue__qsbb.hash.type(-1)
        fegd__srmcz.decref(pltuy__inclb)
        return llue__qsbb._getvalue()
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
        audkt__spw, arr, ind, wnimh__dvz = args
        sdwvc__bhahg = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type,
            sdwvc__bhahg.offsets).data
        data = context.make_helper(builder, char_arr_type, sdwvc__bhahg.data
            ).data
        rseoj__uxwv = lir.FunctionType(lir.IntType(32), [audkt__spw.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        ubf__gzu = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            ubf__gzu = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        fdau__ixq = cgutils.get_or_insert_function(builder.module,
            rseoj__uxwv, ubf__gzu)
        return builder.call(fdau__ixq, [audkt__spw, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    vdqbf__rxpcp = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    rseoj__uxwv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(32)])
    plr__coxh = cgutils.get_or_insert_function(c.builder.module,
        rseoj__uxwv, name='string_array_from_sequence')
    cbmd__puv = c.builder.call(plr__coxh, [val, vdqbf__rxpcp])
    qxw__kgoa = ArrayItemArrayType(char_arr_type)
    cesl__odpia = c.context.make_helper(c.builder, qxw__kgoa)
    cesl__odpia.meminfo = cbmd__puv
    tjevd__xlqz = c.context.make_helper(c.builder, typ)
    dmph__xls = cesl__odpia._getvalue()
    tjevd__xlqz.data = dmph__xls
    hnyoi__ydkxy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tjevd__xlqz._getvalue(), is_error=hnyoi__ydkxy)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    xsoo__dsszb = len(pyval)
    knao__noe = 0
    jryk__rny = np.empty(xsoo__dsszb + 1, np_offset_type)
    dmutl__xtpv = []
    samwy__wgvxy = np.empty(xsoo__dsszb + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        jryk__rny[i] = knao__noe
        meay__lcgfo = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(samwy__wgvxy, i, int(not
            meay__lcgfo))
        if meay__lcgfo:
            continue
        ypx__tskki = list(s.encode()) if isinstance(s, str) else list(s)
        dmutl__xtpv.extend(ypx__tskki)
        knao__noe += len(ypx__tskki)
    jryk__rny[xsoo__dsszb] = knao__noe
    srihp__bkzk = np.array(dmutl__xtpv, np.uint8)
    ggh__gqa = context.get_constant(types.int64, xsoo__dsszb)
    dwg__vxjq = context.get_constant_generic(builder, char_arr_type,
        srihp__bkzk)
    twj__edof = context.get_constant_generic(builder, offset_arr_type,
        jryk__rny)
    rlvl__hhk = context.get_constant_generic(builder, null_bitmap_arr_type,
        samwy__wgvxy)
    sdwvc__bhahg = lir.Constant.literal_struct([ggh__gqa, dwg__vxjq,
        twj__edof, rlvl__hhk])
    sdwvc__bhahg = cgutils.global_constant(builder, '.const.payload',
        sdwvc__bhahg).bitcast(cgutils.voidptr_t)
    euxve__xyp = context.get_constant(types.int64, -1)
    mwylk__acxka = context.get_constant_null(types.voidptr)
    hbvqp__jeim = lir.Constant.literal_struct([euxve__xyp, mwylk__acxka,
        mwylk__acxka, sdwvc__bhahg, euxve__xyp])
    hbvqp__jeim = cgutils.global_constant(builder, '.const.meminfo',
        hbvqp__jeim).bitcast(cgutils.voidptr_t)
    dmph__xls = lir.Constant.literal_struct([hbvqp__jeim])
    tjevd__xlqz = lir.Constant.literal_struct([dmph__xls])
    return tjevd__xlqz


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
