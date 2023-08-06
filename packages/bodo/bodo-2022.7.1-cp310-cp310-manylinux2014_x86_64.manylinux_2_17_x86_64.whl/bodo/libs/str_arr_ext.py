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
        ilgo__advg = ArrayItemArrayType(char_arr_type)
        har__rxh = [('data', ilgo__advg)]
        models.StructModel.__init__(self, dmm, fe_type, har__rxh)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        kcl__lab, = args
        dkczq__ttk = context.make_helper(builder, string_array_type)
        dkczq__ttk.data = kcl__lab
        context.nrt.incref(builder, data_typ, kcl__lab)
        return dkczq__ttk._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    afk__ujr = c.context.insert_const_string(c.builder.module, 'pandas')
    oytt__gdyoc = c.pyapi.import_module_noblock(afk__ujr)
    jgx__jtq = c.pyapi.call_method(oytt__gdyoc, 'StringDtype', ())
    c.pyapi.decref(oytt__gdyoc)
    return jgx__jtq


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        qekx__rvcb = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs
            )
        if qekx__rvcb is not None:
            return qekx__rvcb
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                rqu__hof = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(rqu__hof)
                for i in numba.parfors.parfor.internal_prange(rqu__hof):
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
                rqu__hof = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(rqu__hof)
                for i in numba.parfors.parfor.internal_prange(rqu__hof):
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
                rqu__hof = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(rqu__hof)
                for i in numba.parfors.parfor.internal_prange(rqu__hof):
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
    ljxt__okwh = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    mmq__idg = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and mmq__idg or ljxt__okwh and is_str_arr_type(rhs
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
    psaj__kssgt = context.make_helper(builder, arr_typ, arr_value)
    ilgo__advg = ArrayItemArrayType(char_arr_type)
    rsoq__xmew = _get_array_item_arr_payload(context, builder, ilgo__advg,
        psaj__kssgt.data)
    return rsoq__xmew


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return rsoq__xmew.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        utt__ukl = context.make_helper(builder, offset_arr_type, rsoq__xmew
            .offsets).data
        return _get_num_total_chars(builder, utt__ukl, rsoq__xmew.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        dlpk__tsz = context.make_helper(builder, offset_arr_type,
            rsoq__xmew.offsets)
        ajy__kqfo = context.make_helper(builder, offset_ctypes_type)
        ajy__kqfo.data = builder.bitcast(dlpk__tsz.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        ajy__kqfo.meminfo = dlpk__tsz.meminfo
        jgx__jtq = ajy__kqfo._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type, jgx__jtq
            )
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kcl__lab = context.make_helper(builder, char_arr_type, rsoq__xmew.data)
        ajy__kqfo = context.make_helper(builder, data_ctypes_type)
        ajy__kqfo.data = kcl__lab.data
        ajy__kqfo.meminfo = kcl__lab.meminfo
        jgx__jtq = ajy__kqfo._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, jgx__jtq)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        djkt__ffk, ind = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            djkt__ffk, sig.args[0])
        kcl__lab = context.make_helper(builder, char_arr_type, rsoq__xmew.data)
        ajy__kqfo = context.make_helper(builder, data_ctypes_type)
        ajy__kqfo.data = builder.gep(kcl__lab.data, [ind])
        ajy__kqfo.meminfo = kcl__lab.meminfo
        jgx__jtq = ajy__kqfo._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, jgx__jtq)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        kodlv__khep, kgv__oygig, pmdr__pvr, olo__wcay = args
        lgcwp__lpnc = builder.bitcast(builder.gep(kodlv__khep, [kgv__oygig]
            ), lir.IntType(8).as_pointer())
        yqiu__gka = builder.bitcast(builder.gep(pmdr__pvr, [olo__wcay]),
            lir.IntType(8).as_pointer())
        wpoj__ftwq = builder.load(yqiu__gka)
        builder.store(wpoj__ftwq, lgcwp__lpnc)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        rpkch__mewr = context.make_helper(builder, null_bitmap_arr_type,
            rsoq__xmew.null_bitmap)
        ajy__kqfo = context.make_helper(builder, data_ctypes_type)
        ajy__kqfo.data = rpkch__mewr.data
        ajy__kqfo.meminfo = rpkch__mewr.meminfo
        jgx__jtq = ajy__kqfo._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, jgx__jtq)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        utt__ukl = context.make_helper(builder, offset_arr_type, rsoq__xmew
            .offsets).data
        return builder.load(builder.gep(utt__ukl, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, rsoq__xmew.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        joeg__tca, ind = args
        if in_bitmap_typ == data_ctypes_type:
            ajy__kqfo = context.make_helper(builder, data_ctypes_type,
                joeg__tca)
            joeg__tca = ajy__kqfo.data
        return builder.load(builder.gep(joeg__tca, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        joeg__tca, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            ajy__kqfo = context.make_helper(builder, data_ctypes_type,
                joeg__tca)
            joeg__tca = ajy__kqfo.data
        builder.store(val, builder.gep(joeg__tca, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        psgv__eyiwj = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        utauq__utnxb = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        obf__tkjef = context.make_helper(builder, offset_arr_type,
            psgv__eyiwj.offsets).data
        ltmg__vuyo = context.make_helper(builder, offset_arr_type,
            utauq__utnxb.offsets).data
        aiay__dluc = context.make_helper(builder, char_arr_type,
            psgv__eyiwj.data).data
        ymh__akak = context.make_helper(builder, char_arr_type,
            utauq__utnxb.data).data
        byomn__hpcc = context.make_helper(builder, null_bitmap_arr_type,
            psgv__eyiwj.null_bitmap).data
        eftq__cbnhz = context.make_helper(builder, null_bitmap_arr_type,
            utauq__utnxb.null_bitmap).data
        icty__rwb = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, ltmg__vuyo, obf__tkjef, icty__rwb)
        cgutils.memcpy(builder, ymh__akak, aiay__dluc, builder.load(builder
            .gep(obf__tkjef, [ind])))
        dnwkf__dyci = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        sxhe__bif = builder.lshr(dnwkf__dyci, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, eftq__cbnhz, byomn__hpcc, sxhe__bif)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        psgv__eyiwj = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        utauq__utnxb = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        obf__tkjef = context.make_helper(builder, offset_arr_type,
            psgv__eyiwj.offsets).data
        aiay__dluc = context.make_helper(builder, char_arr_type,
            psgv__eyiwj.data).data
        ymh__akak = context.make_helper(builder, char_arr_type,
            utauq__utnxb.data).data
        num_total_chars = _get_num_total_chars(builder, obf__tkjef,
            psgv__eyiwj.n_arrays)
        cgutils.memcpy(builder, ymh__akak, aiay__dluc, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        psgv__eyiwj = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        utauq__utnxb = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        obf__tkjef = context.make_helper(builder, offset_arr_type,
            psgv__eyiwj.offsets).data
        ltmg__vuyo = context.make_helper(builder, offset_arr_type,
            utauq__utnxb.offsets).data
        byomn__hpcc = context.make_helper(builder, null_bitmap_arr_type,
            psgv__eyiwj.null_bitmap).data
        rqu__hof = psgv__eyiwj.n_arrays
        nrm__jrcje = context.get_constant(offset_type, 0)
        ofw__alrs = cgutils.alloca_once_value(builder, nrm__jrcje)
        with cgutils.for_range(builder, rqu__hof) as rurh__cuiif:
            qmxwh__qshq = lower_is_na(context, builder, byomn__hpcc,
                rurh__cuiif.index)
            with cgutils.if_likely(builder, builder.not_(qmxwh__qshq)):
                wimbk__avxp = builder.load(builder.gep(obf__tkjef, [
                    rurh__cuiif.index]))
                lbr__amnpf = builder.load(ofw__alrs)
                builder.store(wimbk__avxp, builder.gep(ltmg__vuyo, [
                    lbr__amnpf]))
                builder.store(builder.add(lbr__amnpf, lir.Constant(context.
                    get_value_type(offset_type), 1)), ofw__alrs)
        lbr__amnpf = builder.load(ofw__alrs)
        wimbk__avxp = builder.load(builder.gep(obf__tkjef, [rqu__hof]))
        builder.store(wimbk__avxp, builder.gep(ltmg__vuyo, [lbr__amnpf]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        eea__mid, ind, str, ekjwc__vjmn = args
        eea__mid = context.make_array(sig.args[0])(context, builder, eea__mid)
        lagy__mkce = builder.gep(eea__mid.data, [ind])
        cgutils.raw_memcpy(builder, lagy__mkce, str, ekjwc__vjmn, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        lagy__mkce, ind, wen__wok, ekjwc__vjmn = args
        lagy__mkce = builder.gep(lagy__mkce, [ind])
        cgutils.raw_memcpy(builder, lagy__mkce, wen__wok, ekjwc__vjmn, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            csgv__lcg = A._data
            return np.int64(getitem_str_offset(csgv__lcg, idx + 1) -
                getitem_str_offset(csgv__lcg, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    his__gsqww = np.int64(getitem_str_offset(A, i))
    losqq__bxrk = np.int64(getitem_str_offset(A, i + 1))
    l = losqq__bxrk - his__gsqww
    nkgf__ynonq = get_data_ptr_ind(A, his__gsqww)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(nkgf__ynonq, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    dyb__gbpqe = getitem_str_offset(A, i)
    npwm__jhfu = getitem_str_offset(A, i + 1)
    xoqza__famj = npwm__jhfu - dyb__gbpqe
    nvm__xqo = getitem_str_offset(B, j)
    rxzdl__jmi = nvm__xqo + xoqza__famj
    setitem_str_offset(B, j + 1, rxzdl__jmi)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if xoqza__famj != 0:
        kcl__lab = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(kcl__lab, np.
            int64(nvm__xqo), np.int64(rxzdl__jmi))
        flnsf__fram = get_data_ptr(B).data
        qtf__xtm = get_data_ptr(A).data
        memcpy_region(flnsf__fram, nvm__xqo, qtf__xtm, dyb__gbpqe,
            xoqza__famj, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    rqu__hof = len(str_arr)
    xjlbj__bbk = np.empty(rqu__hof, np.bool_)
    for i in range(rqu__hof):
        xjlbj__bbk[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return xjlbj__bbk


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            rqu__hof = len(data)
            l = []
            for i in range(rqu__hof):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        hqadd__yexm = data.count
        hpev__ibh = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(hqadd__yexm)]
        if is_overload_true(str_null_bools):
            hpev__ibh += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(hqadd__yexm) if is_str_arr_type(data.types[i]) or 
                data.types[i] == binary_array_type]
        ubte__ovun = 'def f(data, str_null_bools=None):\n'
        ubte__ovun += '  return ({}{})\n'.format(', '.join(hpev__ibh), ',' if
            hqadd__yexm == 1 else '')
        funxr__htgcm = {}
        exec(ubte__ovun, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, funxr__htgcm)
        hhm__zbta = funxr__htgcm['f']
        return hhm__zbta
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                rqu__hof = len(list_data)
                for i in range(rqu__hof):
                    wen__wok = list_data[i]
                    str_arr[i] = wen__wok
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                rqu__hof = len(list_data)
                for i in range(rqu__hof):
                    wen__wok = list_data[i]
                    str_arr[i] = wen__wok
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        hqadd__yexm = str_arr.count
        pszh__mwu = 0
        ubte__ovun = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(hqadd__yexm):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                ubte__ovun += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, hqadd__yexm + pszh__mwu))
                pszh__mwu += 1
            else:
                ubte__ovun += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        ubte__ovun += '  return\n'
        funxr__htgcm = {}
        exec(ubte__ovun, {'cp_str_list_to_array': cp_str_list_to_array},
            funxr__htgcm)
        dfz__bity = funxr__htgcm['f']
        return dfz__bity
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            rqu__hof = len(str_list)
            str_arr = pre_alloc_string_array(rqu__hof, -1)
            for i in range(rqu__hof):
                wen__wok = str_list[i]
                str_arr[i] = wen__wok
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            rqu__hof = len(A)
            hax__fkmb = 0
            for i in range(rqu__hof):
                wen__wok = A[i]
                hax__fkmb += get_utf8_size(wen__wok)
            return hax__fkmb
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        rqu__hof = len(arr)
        n_chars = num_total_chars(arr)
        zjyp__dzbf = pre_alloc_string_array(rqu__hof, np.int64(n_chars))
        copy_str_arr_slice(zjyp__dzbf, arr, rqu__hof)
        return zjyp__dzbf
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
    ubte__ovun = 'def f(in_seq):\n'
    ubte__ovun += '    n_strs = len(in_seq)\n'
    ubte__ovun += '    A = pre_alloc_string_array(n_strs, -1)\n'
    ubte__ovun += '    return A\n'
    funxr__htgcm = {}
    exec(ubte__ovun, {'pre_alloc_string_array': pre_alloc_string_array},
        funxr__htgcm)
    qeb__qjpn = funxr__htgcm['f']
    return qeb__qjpn


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        ypv__afrqb = 'pre_alloc_binary_array'
    else:
        ypv__afrqb = 'pre_alloc_string_array'
    ubte__ovun = 'def f(in_seq):\n'
    ubte__ovun += '    n_strs = len(in_seq)\n'
    ubte__ovun += f'    A = {ypv__afrqb}(n_strs, -1)\n'
    ubte__ovun += '    for i in range(n_strs):\n'
    ubte__ovun += '        A[i] = in_seq[i]\n'
    ubte__ovun += '    return A\n'
    funxr__htgcm = {}
    exec(ubte__ovun, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, funxr__htgcm)
    qeb__qjpn = funxr__htgcm['f']
    return qeb__qjpn


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        mlykz__wvo = builder.add(rsoq__xmew.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        owiu__enu = builder.lshr(lir.Constant(lir.IntType(64), offset_type.
            bitwidth), lir.Constant(lir.IntType(64), 3))
        sxhe__bif = builder.mul(mlykz__wvo, owiu__enu)
        zpaf__kfsn = context.make_array(offset_arr_type)(context, builder,
            rsoq__xmew.offsets).data
        cgutils.memset(builder, zpaf__kfsn, sxhe__bif, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        cdz__oid = rsoq__xmew.n_arrays
        sxhe__bif = builder.lshr(builder.add(cdz__oid, lir.Constant(lir.
            IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        wgrv__zzd = context.make_array(null_bitmap_arr_type)(context,
            builder, rsoq__xmew.null_bitmap).data
        cgutils.memset(builder, wgrv__zzd, sxhe__bif, 0)
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
    buz__hqclh = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        ritd__mjjjd = len(len_arr)
        for i in range(ritd__mjjjd):
            offsets[i] = buz__hqclh
            buz__hqclh += len_arr[i]
        offsets[ritd__mjjjd] = buz__hqclh
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    hlktb__drebz = i // 8
    pdgwd__kgtjs = getitem_str_bitmap(bits, hlktb__drebz)
    pdgwd__kgtjs ^= np.uint8(-np.uint8(bit_is_set) ^ pdgwd__kgtjs) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, hlktb__drebz, pdgwd__kgtjs)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    afe__srxpb = get_null_bitmap_ptr(out_str_arr)
    eml__zkaxm = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        undnz__ctu = get_bit_bitmap(eml__zkaxm, j)
        set_bit_to(afe__srxpb, out_start + j, undnz__ctu)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, djkt__ffk, oid__jwwip, cqfm__iir = args
        psgv__eyiwj = _get_str_binary_arr_payload(context, builder,
            djkt__ffk, string_array_type)
        utauq__utnxb = _get_str_binary_arr_payload(context, builder,
            out_arr, string_array_type)
        obf__tkjef = context.make_helper(builder, offset_arr_type,
            psgv__eyiwj.offsets).data
        ltmg__vuyo = context.make_helper(builder, offset_arr_type,
            utauq__utnxb.offsets).data
        aiay__dluc = context.make_helper(builder, char_arr_type,
            psgv__eyiwj.data).data
        ymh__akak = context.make_helper(builder, char_arr_type,
            utauq__utnxb.data).data
        num_total_chars = _get_num_total_chars(builder, obf__tkjef,
            psgv__eyiwj.n_arrays)
        wldc__rafk = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        iyqfv__qwcta = cgutils.get_or_insert_function(builder.module,
            wldc__rafk, name='set_string_array_range')
        builder.call(iyqfv__qwcta, [ltmg__vuyo, ymh__akak, obf__tkjef,
            aiay__dluc, oid__jwwip, cqfm__iir, psgv__eyiwj.n_arrays,
            num_total_chars])
        rkv__uss = context.typing_context.resolve_value_type(copy_nulls_range)
        bsc__wdma = rkv__uss.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        uzkke__lwn = context.get_function(rkv__uss, bsc__wdma)
        uzkke__lwn(builder, (out_arr, djkt__ffk, oid__jwwip))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    eybwb__cedty = c.context.make_helper(c.builder, typ, val)
    ilgo__advg = ArrayItemArrayType(char_arr_type)
    rsoq__xmew = _get_array_item_arr_payload(c.context, c.builder,
        ilgo__advg, eybwb__cedty.data)
    ebk__gtwc = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    aos__wsolp = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        aos__wsolp = 'pd_array_from_string_array'
    wldc__rafk = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    nibcf__ekhf = cgutils.get_or_insert_function(c.builder.module,
        wldc__rafk, name=aos__wsolp)
    utt__ukl = c.context.make_array(offset_arr_type)(c.context, c.builder,
        rsoq__xmew.offsets).data
    nkgf__ynonq = c.context.make_array(char_arr_type)(c.context, c.builder,
        rsoq__xmew.data).data
    wgrv__zzd = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, rsoq__xmew.null_bitmap).data
    arr = c.builder.call(nibcf__ekhf, [rsoq__xmew.n_arrays, utt__ukl,
        nkgf__ynonq, wgrv__zzd, ebk__gtwc])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        wgrv__zzd = context.make_array(null_bitmap_arr_type)(context,
            builder, rsoq__xmew.null_bitmap).data
        pdhfy__zrw = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        arm__xsdul = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        pdgwd__kgtjs = builder.load(builder.gep(wgrv__zzd, [pdhfy__zrw],
            inbounds=True))
        ntnh__chht = lir.ArrayType(lir.IntType(8), 8)
        rmar__jsf = cgutils.alloca_once_value(builder, lir.Constant(
            ntnh__chht, (1, 2, 4, 8, 16, 32, 64, 128)))
        rwxft__lmt = builder.load(builder.gep(rmar__jsf, [lir.Constant(lir.
            IntType(64), 0), arm__xsdul], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(pdgwd__kgtjs,
            rwxft__lmt), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pdhfy__zrw = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        arm__xsdul = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        wgrv__zzd = context.make_array(null_bitmap_arr_type)(context,
            builder, rsoq__xmew.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, rsoq__xmew.
            offsets).data
        matz__dyqb = builder.gep(wgrv__zzd, [pdhfy__zrw], inbounds=True)
        pdgwd__kgtjs = builder.load(matz__dyqb)
        ntnh__chht = lir.ArrayType(lir.IntType(8), 8)
        rmar__jsf = cgutils.alloca_once_value(builder, lir.Constant(
            ntnh__chht, (1, 2, 4, 8, 16, 32, 64, 128)))
        rwxft__lmt = builder.load(builder.gep(rmar__jsf, [lir.Constant(lir.
            IntType(64), 0), arm__xsdul], inbounds=True))
        rwxft__lmt = builder.xor(rwxft__lmt, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(pdgwd__kgtjs, rwxft__lmt), matz__dyqb)
        if str_arr_typ == string_array_type:
            qlel__floij = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            qzl__xvo = builder.icmp_unsigned('!=', qlel__floij, rsoq__xmew.
                n_arrays)
            with builder.if_then(qzl__xvo):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [qlel__floij]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pdhfy__zrw = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        arm__xsdul = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        wgrv__zzd = context.make_array(null_bitmap_arr_type)(context,
            builder, rsoq__xmew.null_bitmap).data
        matz__dyqb = builder.gep(wgrv__zzd, [pdhfy__zrw], inbounds=True)
        pdgwd__kgtjs = builder.load(matz__dyqb)
        ntnh__chht = lir.ArrayType(lir.IntType(8), 8)
        rmar__jsf = cgutils.alloca_once_value(builder, lir.Constant(
            ntnh__chht, (1, 2, 4, 8, 16, 32, 64, 128)))
        rwxft__lmt = builder.load(builder.gep(rmar__jsf, [lir.Constant(lir.
            IntType(64), 0), arm__xsdul], inbounds=True))
        builder.store(builder.or_(pdgwd__kgtjs, rwxft__lmt), matz__dyqb)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        sxhe__bif = builder.udiv(builder.add(rsoq__xmew.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        wgrv__zzd = context.make_array(null_bitmap_arr_type)(context,
            builder, rsoq__xmew.null_bitmap).data
        cgutils.memset(builder, wgrv__zzd, sxhe__bif, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    uou__rxr = context.make_helper(builder, string_array_type, str_arr)
    ilgo__advg = ArrayItemArrayType(char_arr_type)
    ziydz__mzgze = context.make_helper(builder, ilgo__advg, uou__rxr.data)
    nmjpj__bkauv = ArrayItemArrayPayloadType(ilgo__advg)
    ceqi__wipi = context.nrt.meminfo_data(builder, ziydz__mzgze.meminfo)
    sbgl__vjavw = builder.bitcast(ceqi__wipi, context.get_value_type(
        nmjpj__bkauv).as_pointer())
    return sbgl__vjavw


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        ywak__gpz, zsv__dwmy = args
        yjmn__jpiy = _get_str_binary_arr_data_payload_ptr(context, builder,
            zsv__dwmy)
        cchu__fahts = _get_str_binary_arr_data_payload_ptr(context, builder,
            ywak__gpz)
        kfb__hcy = _get_str_binary_arr_payload(context, builder, zsv__dwmy,
            sig.args[1])
        abj__cdnki = _get_str_binary_arr_payload(context, builder,
            ywak__gpz, sig.args[0])
        context.nrt.incref(builder, char_arr_type, kfb__hcy.data)
        context.nrt.incref(builder, offset_arr_type, kfb__hcy.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, kfb__hcy.null_bitmap)
        context.nrt.decref(builder, char_arr_type, abj__cdnki.data)
        context.nrt.decref(builder, offset_arr_type, abj__cdnki.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, abj__cdnki.
            null_bitmap)
        builder.store(builder.load(yjmn__jpiy), cchu__fahts)
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
        rqu__hof = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return rqu__hof
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, lagy__mkce, rhh__tvsrh = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder, arr, sig
            .args[0])
        offsets = context.make_helper(builder, offset_arr_type, rsoq__xmew.
            offsets).data
        data = context.make_helper(builder, char_arr_type, rsoq__xmew.data
            ).data
        wldc__rafk = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        eswvq__eoug = cgutils.get_or_insert_function(builder.module,
            wldc__rafk, name='setitem_string_array')
        stfl__jchcu = context.get_constant(types.int32, -1)
        gsa__vqw = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, rsoq__xmew
            .n_arrays)
        builder.call(eswvq__eoug, [offsets, data, num_total_chars, builder.
            extract_value(lagy__mkce, 0), rhh__tvsrh, stfl__jchcu, gsa__vqw,
            ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    wldc__rafk = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    byzkt__dta = cgutils.get_or_insert_function(builder.module, wldc__rafk,
        name='is_na')
    return builder.call(byzkt__dta, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        lgcwp__lpnc, yqiu__gka, hqadd__yexm, tqf__brip = args
        cgutils.raw_memcpy(builder, lgcwp__lpnc, yqiu__gka, hqadd__yexm,
            tqf__brip)
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
        lxur__kipq, ayp__jwc = unicode_to_utf8_and_len(val)
        ugl__jsw = getitem_str_offset(A, ind)
        kocd__usogg = getitem_str_offset(A, ind + 1)
        awbx__caxqh = kocd__usogg - ugl__jsw
        if awbx__caxqh != ayp__jwc:
            return False
        lagy__mkce = get_data_ptr_ind(A, ugl__jsw)
        return memcmp(lagy__mkce, lxur__kipq, ayp__jwc) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        ugl__jsw = getitem_str_offset(A, ind)
        awbx__caxqh = bodo.libs.str_ext.int_to_str_len(val)
        tsd__pxy = ugl__jsw + awbx__caxqh
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data, ugl__jsw,
            tsd__pxy)
        lagy__mkce = get_data_ptr_ind(A, ugl__jsw)
        inplace_int64_to_str(lagy__mkce, awbx__caxqh, val)
        setitem_str_offset(A, ind + 1, ugl__jsw + awbx__caxqh)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        lagy__mkce, = args
        xjtfl__eycg = context.insert_const_string(builder.module, '<NA>')
        zuj__cdz = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, lagy__mkce, xjtfl__eycg, zuj__cdz, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    fkgei__tgyty = len('<NA>')

    def impl(A, ind):
        ugl__jsw = getitem_str_offset(A, ind)
        tsd__pxy = ugl__jsw + fkgei__tgyty
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data, ugl__jsw,
            tsd__pxy)
        lagy__mkce = get_data_ptr_ind(A, ugl__jsw)
        inplace_set_NA_str(lagy__mkce)
        setitem_str_offset(A, ind + 1, ugl__jsw + fkgei__tgyty)
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
            ugl__jsw = getitem_str_offset(A, ind)
            kocd__usogg = getitem_str_offset(A, ind + 1)
            rhh__tvsrh = kocd__usogg - ugl__jsw
            lagy__mkce = get_data_ptr_ind(A, ugl__jsw)
            rdsuy__uvmol = decode_utf8(lagy__mkce, rhh__tvsrh)
            return rdsuy__uvmol
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            rqu__hof = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(rqu__hof):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            flnsf__fram = get_data_ptr(out_arr).data
            qtf__xtm = get_data_ptr(A).data
            pszh__mwu = 0
            lbr__amnpf = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(rqu__hof):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    vxf__cuymi = get_str_arr_item_length(A, i)
                    if vxf__cuymi == 1:
                        copy_single_char(flnsf__fram, lbr__amnpf, qtf__xtm,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(flnsf__fram, lbr__amnpf, qtf__xtm,
                            getitem_str_offset(A, i), vxf__cuymi, 1)
                    lbr__amnpf += vxf__cuymi
                    setitem_str_offset(out_arr, pszh__mwu + 1, lbr__amnpf)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, pszh__mwu)
                    else:
                        str_arr_set_not_na(out_arr, pszh__mwu)
                    pszh__mwu += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            rqu__hof = len(ind)
            out_arr = pre_alloc_string_array(rqu__hof, -1)
            pszh__mwu = 0
            for i in range(rqu__hof):
                wen__wok = A[ind[i]]
                out_arr[pszh__mwu] = wen__wok
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, pszh__mwu)
                pszh__mwu += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            rqu__hof = len(A)
            czxl__ogrye = numba.cpython.unicode._normalize_slice(ind, rqu__hof)
            fbbt__wmquk = numba.cpython.unicode._slice_span(czxl__ogrye)
            if czxl__ogrye.step == 1:
                ugl__jsw = getitem_str_offset(A, czxl__ogrye.start)
                kocd__usogg = getitem_str_offset(A, czxl__ogrye.stop)
                n_chars = kocd__usogg - ugl__jsw
                zjyp__dzbf = pre_alloc_string_array(fbbt__wmquk, np.int64(
                    n_chars))
                for i in range(fbbt__wmquk):
                    zjyp__dzbf[i] = A[czxl__ogrye.start + i]
                    if str_arr_is_na(A, czxl__ogrye.start + i):
                        str_arr_set_na(zjyp__dzbf, i)
                return zjyp__dzbf
            else:
                zjyp__dzbf = pre_alloc_string_array(fbbt__wmquk, -1)
                for i in range(fbbt__wmquk):
                    zjyp__dzbf[i] = A[czxl__ogrye.start + i * czxl__ogrye.step]
                    if str_arr_is_na(A, czxl__ogrye.start + i * czxl__ogrye
                        .step):
                        str_arr_set_na(zjyp__dzbf, i)
                return zjyp__dzbf
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
    rrqp__kphaf = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(rrqp__kphaf)
        rkcc__rlfkz = 4

        def impl_scalar(A, idx, val):
            vvvg__diztx = (val._length if val._is_ascii else rkcc__rlfkz *
                val._length)
            kcl__lab = A._data
            ugl__jsw = np.int64(getitem_str_offset(A, idx))
            tsd__pxy = ugl__jsw + vvvg__diztx
            bodo.libs.array_item_arr_ext.ensure_data_capacity(kcl__lab,
                ugl__jsw, tsd__pxy)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                tsd__pxy, val._data, val._length, val._kind, val._is_ascii, idx
                )
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                czxl__ogrye = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                his__gsqww = czxl__ogrye.start
                kcl__lab = A._data
                ugl__jsw = np.int64(getitem_str_offset(A, his__gsqww))
                tsd__pxy = ugl__jsw + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(kcl__lab,
                    ugl__jsw, tsd__pxy)
                set_string_array_range(A, val, his__gsqww, ugl__jsw)
                vzyd__jzuwx = 0
                for i in range(czxl__ogrye.start, czxl__ogrye.stop,
                    czxl__ogrye.step):
                    if str_arr_is_na(val, vzyd__jzuwx):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    vzyd__jzuwx += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                osyve__lzxz = str_list_to_array(val)
                A[idx] = osyve__lzxz
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                czxl__ogrye = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                for i in range(czxl__ogrye.start, czxl__ogrye.stop,
                    czxl__ogrye.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(rrqp__kphaf)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                rqu__hof = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(rqu__hof, -1)
                for i in numba.parfors.parfor.internal_prange(rqu__hof):
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
                rqu__hof = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(rqu__hof, -1)
                rypxx__ovhq = 0
                for i in numba.parfors.parfor.internal_prange(rqu__hof):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, rypxx__ovhq):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, rypxx__ovhq)
                        else:
                            out_arr[i] = str(val[rypxx__ovhq])
                        rypxx__ovhq += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(rrqp__kphaf)
    raise BodoError(rrqp__kphaf)


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
    lnhl__ahp = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(lnhl__ahp, (types.Float, types.Integer)
        ) and lnhl__ahp not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(lnhl__ahp, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            rqu__hof = len(A)
            B = np.empty(rqu__hof, lnhl__ahp)
            for i in numba.parfors.parfor.internal_prange(rqu__hof):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif lnhl__ahp == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            rqu__hof = len(A)
            B = np.empty(rqu__hof, lnhl__ahp)
            for i in numba.parfors.parfor.internal_prange(rqu__hof):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif lnhl__ahp == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            rqu__hof = len(A)
            B = np.empty(rqu__hof, lnhl__ahp)
            for i in numba.parfors.parfor.internal_prange(rqu__hof):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            rqu__hof = len(A)
            B = np.empty(rqu__hof, lnhl__ahp)
            for i in numba.parfors.parfor.internal_prange(rqu__hof):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        lagy__mkce, rhh__tvsrh = args
        vomj__his = context.get_python_api(builder)
        zzl__yjjx = vomj__his.string_from_string_and_size(lagy__mkce,
            rhh__tvsrh)
        tljm__rox = vomj__his.to_native_value(string_type, zzl__yjjx).value
        lulp__gwve = cgutils.create_struct_proxy(string_type)(context,
            builder, tljm__rox)
        lulp__gwve.hash = lulp__gwve.hash.type(-1)
        vomj__his.decref(zzl__yjjx)
        return lulp__gwve._getvalue()
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
        snhvz__cjcz, arr, ind, ucpwb__cgbof = args
        rsoq__xmew = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, rsoq__xmew.
            offsets).data
        data = context.make_helper(builder, char_arr_type, rsoq__xmew.data
            ).data
        wldc__rafk = lir.FunctionType(lir.IntType(32), [snhvz__cjcz.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        utu__tkqk = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            utu__tkqk = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        gzs__cdc = cgutils.get_or_insert_function(builder.module,
            wldc__rafk, utu__tkqk)
        return builder.call(gzs__cdc, [snhvz__cjcz, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    ebk__gtwc = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    wldc__rafk = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(32)])
    edjec__yhh = cgutils.get_or_insert_function(c.builder.module,
        wldc__rafk, name='string_array_from_sequence')
    ygh__fgz = c.builder.call(edjec__yhh, [val, ebk__gtwc])
    ilgo__advg = ArrayItemArrayType(char_arr_type)
    ziydz__mzgze = c.context.make_helper(c.builder, ilgo__advg)
    ziydz__mzgze.meminfo = ygh__fgz
    uou__rxr = c.context.make_helper(c.builder, typ)
    kcl__lab = ziydz__mzgze._getvalue()
    uou__rxr.data = kcl__lab
    wpd__lxlpy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uou__rxr._getvalue(), is_error=wpd__lxlpy)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    rqu__hof = len(pyval)
    lbr__amnpf = 0
    kmmnv__dzji = np.empty(rqu__hof + 1, np_offset_type)
    jzmxy__aep = []
    excv__zlnk = np.empty(rqu__hof + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        kmmnv__dzji[i] = lbr__amnpf
        qyyl__xcgzy = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(excv__zlnk, i, int(not
            qyyl__xcgzy))
        if qyyl__xcgzy:
            continue
        xguy__uwg = list(s.encode()) if isinstance(s, str) else list(s)
        jzmxy__aep.extend(xguy__uwg)
        lbr__amnpf += len(xguy__uwg)
    kmmnv__dzji[rqu__hof] = lbr__amnpf
    scq__kiwqo = np.array(jzmxy__aep, np.uint8)
    uck__tjuw = context.get_constant(types.int64, rqu__hof)
    myz__qana = context.get_constant_generic(builder, char_arr_type, scq__kiwqo
        )
    cldeg__suf = context.get_constant_generic(builder, offset_arr_type,
        kmmnv__dzji)
    rmwl__agg = context.get_constant_generic(builder, null_bitmap_arr_type,
        excv__zlnk)
    rsoq__xmew = lir.Constant.literal_struct([uck__tjuw, myz__qana,
        cldeg__suf, rmwl__agg])
    rsoq__xmew = cgutils.global_constant(builder, '.const.payload', rsoq__xmew
        ).bitcast(cgutils.voidptr_t)
    euxj__giki = context.get_constant(types.int64, -1)
    ivpqz__mwii = context.get_constant_null(types.voidptr)
    kjl__elkm = lir.Constant.literal_struct([euxj__giki, ivpqz__mwii,
        ivpqz__mwii, rsoq__xmew, euxj__giki])
    kjl__elkm = cgutils.global_constant(builder, '.const.meminfo', kjl__elkm
        ).bitcast(cgutils.voidptr_t)
    kcl__lab = lir.Constant.literal_struct([kjl__elkm])
    uou__rxr = lir.Constant.literal_struct([kcl__lab])
    return uou__rxr


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
