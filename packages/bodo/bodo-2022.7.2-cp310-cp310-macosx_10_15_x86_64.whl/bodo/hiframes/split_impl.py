import operator
import llvmlite.binding as ll
import numba
import numba.core.typing.typeof
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, impl_ret_new_ref
from numba.extending import box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, _memcpy, char_arr_type, get_data_ptr, null_bitmap_arr_type, offset_arr_type, string_array_type
ll.add_symbol('array_setitem', hstr_ext.array_setitem)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
ll.add_symbol('dtor_str_arr_split_view', hstr_ext.dtor_str_arr_split_view)
ll.add_symbol('str_arr_split_view_impl', hstr_ext.str_arr_split_view_impl)
ll.add_symbol('str_arr_split_view_alloc', hstr_ext.str_arr_split_view_alloc)
char_typ = types.uint8
data_ctypes_type = types.ArrayCTypes(types.Array(char_typ, 1, 'C'))
offset_ctypes_type = types.ArrayCTypes(types.Array(offset_type, 1, 'C'))


class StringArraySplitViewType(types.ArrayCompatible):

    def __init__(self):
        super(StringArraySplitViewType, self).__init__(name=
            'StringArraySplitViewType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_array_type

    def copy(self):
        return StringArraySplitViewType()


string_array_split_view_type = StringArraySplitViewType()


class StringArraySplitViewPayloadType(types.Type):

    def __init__(self):
        super(StringArraySplitViewPayloadType, self).__init__(name=
            'StringArraySplitViewPayloadType()')


str_arr_split_view_payload_type = StringArraySplitViewPayloadType()


@register_model(StringArraySplitViewPayloadType)
class StringArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zaww__nhvzr = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, zaww__nhvzr)


str_arr_model_members = [('num_items', types.uint64), ('index_offsets',
    types.CPointer(offset_type)), ('data_offsets', types.CPointer(
    offset_type)), ('data', data_ctypes_type), ('null_bitmap', types.
    CPointer(char_typ)), ('meminfo', types.MemInfoPointer(
    str_arr_split_view_payload_type))]


@register_model(StringArraySplitViewType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        models.StructModel.__init__(self, dmm, fe_type, str_arr_model_members)


make_attribute_wrapper(StringArraySplitViewType, 'num_items', '_num_items')
make_attribute_wrapper(StringArraySplitViewType, 'index_offsets',
    '_index_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data_offsets',
    '_data_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data', '_data')
make_attribute_wrapper(StringArraySplitViewType, 'null_bitmap', '_null_bitmap')


def construct_str_arr_split_view(context, builder):
    qhir__sadwj = context.get_value_type(str_arr_split_view_payload_type)
    yod__rzvjg = context.get_abi_sizeof(qhir__sadwj)
    rge__qlfdd = context.get_value_type(types.voidptr)
    auc__nbah = context.get_value_type(types.uintp)
    woeok__tcfiz = lir.FunctionType(lir.VoidType(), [rge__qlfdd, auc__nbah,
        rge__qlfdd])
    cqr__weg = cgutils.get_or_insert_function(builder.module, woeok__tcfiz,
        name='dtor_str_arr_split_view')
    bfz__jlun = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, yod__rzvjg), cqr__weg)
    iscse__bzhuf = context.nrt.meminfo_data(builder, bfz__jlun)
    mhes__bciq = builder.bitcast(iscse__bzhuf, qhir__sadwj.as_pointer())
    return bfz__jlun, mhes__bciq


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        cskzi__efo, pncgd__qow = args
        bfz__jlun, mhes__bciq = construct_str_arr_split_view(context, builder)
        hyxwh__saudr = _get_str_binary_arr_payload(context, builder,
            cskzi__efo, string_array_type)
        tnatu__kgazi = lir.FunctionType(lir.VoidType(), [mhes__bciq.type,
            lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        aaode__nqfkr = cgutils.get_or_insert_function(builder.module,
            tnatu__kgazi, name='str_arr_split_view_impl')
        trlhu__vqh = context.make_helper(builder, offset_arr_type,
            hyxwh__saudr.offsets).data
        hvx__iysd = context.make_helper(builder, char_arr_type,
            hyxwh__saudr.data).data
        ncd__wms = context.make_helper(builder, null_bitmap_arr_type,
            hyxwh__saudr.null_bitmap).data
        xic__eytmi = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(aaode__nqfkr, [mhes__bciq, hyxwh__saudr.n_arrays,
            trlhu__vqh, hvx__iysd, ncd__wms, xic__eytmi])
        mplq__gjviv = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(mhes__bciq))
        mwrp__uyf = context.make_helper(builder, string_array_split_view_type)
        mwrp__uyf.num_items = hyxwh__saudr.n_arrays
        mwrp__uyf.index_offsets = mplq__gjviv.index_offsets
        mwrp__uyf.data_offsets = mplq__gjviv.data_offsets
        mwrp__uyf.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [cskzi__efo])
        mwrp__uyf.null_bitmap = mplq__gjviv.null_bitmap
        mwrp__uyf.meminfo = bfz__jlun
        dszou__ndvbj = mwrp__uyf._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, dszou__ndvbj)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    dylcu__djk = context.make_helper(builder, string_array_split_view_type, val
        )
    gys__lkes = context.insert_const_string(builder.module, 'numpy')
    lxmyc__cjb = c.pyapi.import_module_noblock(gys__lkes)
    dtype = c.pyapi.object_getattr_string(lxmyc__cjb, 'object_')
    nqai__shz = builder.sext(dylcu__djk.num_items, c.pyapi.longlong)
    qcj__ouawk = c.pyapi.long_from_longlong(nqai__shz)
    mhm__nlq = c.pyapi.call_method(lxmyc__cjb, 'ndarray', (qcj__ouawk, dtype))
    bkhdk__hzoi = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    oxwa__wjtzf = c.pyapi._get_function(bkhdk__hzoi, name='array_getptr1')
    erxnb__rzp = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    qxym__hejxb = c.pyapi._get_function(erxnb__rzp, name='array_setitem')
    zcl__nrnbb = c.pyapi.object_getattr_string(lxmyc__cjb, 'nan')
    with cgutils.for_range(builder, dylcu__djk.num_items) as mzyx__xvzg:
        str_ind = mzyx__xvzg.index
        eon__xdb = builder.sext(builder.load(builder.gep(dylcu__djk.
            index_offsets, [str_ind])), lir.IntType(64))
        rbio__jhqc = builder.sext(builder.load(builder.gep(dylcu__djk.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        zrd__xyk = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        uxijw__zmcs = builder.gep(dylcu__djk.null_bitmap, [zrd__xyk])
        dlbhw__ckw = builder.load(uxijw__zmcs)
        czv__rrmdr = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(dlbhw__ckw, czv__rrmdr), lir.
            Constant(lir.IntType(8), 1))
        yhvx__bof = builder.sub(rbio__jhqc, eon__xdb)
        yhvx__bof = builder.sub(yhvx__bof, yhvx__bof.type(1))
        svn__lnscw = builder.call(oxwa__wjtzf, [mhm__nlq, str_ind])
        vqsv__zwif = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(vqsv__zwif) as (eroh__qxtq, mbxyf__jda):
            with eroh__qxtq:
                mge__iio = c.pyapi.list_new(yhvx__bof)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    mge__iio), likely=True):
                    with cgutils.for_range(c.builder, yhvx__bof) as mzyx__xvzg:
                        wqvv__jwp = builder.add(eon__xdb, mzyx__xvzg.index)
                        data_start = builder.load(builder.gep(dylcu__djk.
                            data_offsets, [wqvv__jwp]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        ipgo__zfblm = builder.load(builder.gep(dylcu__djk.
                            data_offsets, [builder.add(wqvv__jwp, wqvv__jwp
                            .type(1))]))
                        mfbl__egpj = builder.gep(builder.extract_value(
                            dylcu__djk.data, 0), [data_start])
                        ulgq__mdu = builder.sext(builder.sub(ipgo__zfblm,
                            data_start), lir.IntType(64))
                        fch__khc = c.pyapi.string_from_string_and_size(
                            mfbl__egpj, ulgq__mdu)
                        c.pyapi.list_setitem(mge__iio, mzyx__xvzg.index,
                            fch__khc)
                builder.call(qxym__hejxb, [mhm__nlq, svn__lnscw, mge__iio])
            with mbxyf__jda:
                builder.call(qxym__hejxb, [mhm__nlq, svn__lnscw, zcl__nrnbb])
    c.pyapi.decref(lxmyc__cjb)
    c.pyapi.decref(dtype)
    c.pyapi.decref(zcl__nrnbb)
    return mhm__nlq


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        cvah__ebfz, hcxl__sogfr, mfbl__egpj = args
        bfz__jlun, mhes__bciq = construct_str_arr_split_view(context, builder)
        tnatu__kgazi = lir.FunctionType(lir.VoidType(), [mhes__bciq.type,
            lir.IntType(64), lir.IntType(64)])
        aaode__nqfkr = cgutils.get_or_insert_function(builder.module,
            tnatu__kgazi, name='str_arr_split_view_alloc')
        builder.call(aaode__nqfkr, [mhes__bciq, cvah__ebfz, hcxl__sogfr])
        mplq__gjviv = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(mhes__bciq))
        mwrp__uyf = context.make_helper(builder, string_array_split_view_type)
        mwrp__uyf.num_items = cvah__ebfz
        mwrp__uyf.index_offsets = mplq__gjviv.index_offsets
        mwrp__uyf.data_offsets = mplq__gjviv.data_offsets
        mwrp__uyf.data = mfbl__egpj
        mwrp__uyf.null_bitmap = mplq__gjviv.null_bitmap
        context.nrt.incref(builder, data_t, mfbl__egpj)
        mwrp__uyf.meminfo = bfz__jlun
        dszou__ndvbj = mwrp__uyf._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, dszou__ndvbj)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        nbo__mxxdl, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            nbo__mxxdl = builder.extract_value(nbo__mxxdl, 0)
        return builder.bitcast(builder.gep(nbo__mxxdl, [ind]), lir.IntType(
            8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        nbo__mxxdl, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            nbo__mxxdl = builder.extract_value(nbo__mxxdl, 0)
        return builder.load(builder.gep(nbo__mxxdl, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        nbo__mxxdl, ind, vvcqd__hydm = args
        gkb__axxbl = builder.gep(nbo__mxxdl, [ind])
        builder.store(vvcqd__hydm, gkb__axxbl)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        gxdna__pfg, ind = args
        xptss__hsbn = context.make_helper(builder, arr_ctypes_t, gxdna__pfg)
        xid__lxnkr = context.make_helper(builder, arr_ctypes_t)
        xid__lxnkr.data = builder.gep(xptss__hsbn.data, [ind])
        xid__lxnkr.meminfo = xptss__hsbn.meminfo
        qpdl__ymo = xid__lxnkr._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, qpdl__ymo)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    dtmuk__sllin = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr.
        _null_bitmap, item_ind)
    if not dtmuk__sllin:
        return 0, 0, 0
    wqvv__jwp = getitem_c_arr(arr._index_offsets, item_ind)
    jaa__odlzc = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    ikmai__bntk = jaa__odlzc - wqvv__jwp
    if str_ind >= ikmai__bntk:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, wqvv__jwp + str_ind)
    data_start += 1
    if wqvv__jwp + str_ind == 0:
        data_start = 0
    ipgo__zfblm = getitem_c_arr(arr._data_offsets, wqvv__jwp + str_ind + 1)
    qnu__jlmqi = ipgo__zfblm - data_start
    return 1, data_start, qnu__jlmqi


@numba.njit(no_cpython_wrapper=True)
def get_split_view_data_ptr(arr, data_start):
    return get_array_ctypes_ptr(arr._data, data_start)


@overload(len, no_unliteral=True)
def str_arr_split_view_len_overload(arr):
    if arr == string_array_split_view_type:
        return lambda arr: np.int64(arr._num_items)


@overload_attribute(StringArraySplitViewType, 'shape')
def overload_split_view_arr_shape(A):
    return lambda A: (np.int64(A._num_items),)


@overload(operator.getitem, no_unliteral=True)
def str_arr_split_view_getitem_overload(A, ind):
    if A != string_array_split_view_type:
        return
    if A == string_array_split_view_type and isinstance(ind, types.Integer):
        alp__sqfig = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            wqvv__jwp = getitem_c_arr(A._index_offsets, ind)
            jaa__odlzc = getitem_c_arr(A._index_offsets, ind + 1)
            jign__hjx = jaa__odlzc - wqvv__jwp - 1
            cskzi__efo = bodo.libs.str_arr_ext.pre_alloc_string_array(jign__hjx
                , -1)
            for zliao__tycpk in range(jign__hjx):
                data_start = getitem_c_arr(A._data_offsets, wqvv__jwp +
                    zliao__tycpk)
                data_start += 1
                if wqvv__jwp + zliao__tycpk == 0:
                    data_start = 0
                ipgo__zfblm = getitem_c_arr(A._data_offsets, wqvv__jwp +
                    zliao__tycpk + 1)
                qnu__jlmqi = ipgo__zfblm - data_start
                gkb__axxbl = get_array_ctypes_ptr(A._data, data_start)
                wlhoz__yoyxy = bodo.libs.str_arr_ext.decode_utf8(gkb__axxbl,
                    qnu__jlmqi)
                cskzi__efo[zliao__tycpk] = wlhoz__yoyxy
            return cskzi__efo
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        zekg__fmecz = offset_type.bitwidth // 8

        def _impl(A, ind):
            jign__hjx = len(A)
            if jign__hjx != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            cvah__ebfz = 0
            hcxl__sogfr = 0
            for zliao__tycpk in range(jign__hjx):
                if ind[zliao__tycpk]:
                    cvah__ebfz += 1
                    wqvv__jwp = getitem_c_arr(A._index_offsets, zliao__tycpk)
                    jaa__odlzc = getitem_c_arr(A._index_offsets, 
                        zliao__tycpk + 1)
                    hcxl__sogfr += jaa__odlzc - wqvv__jwp
            mhm__nlq = pre_alloc_str_arr_view(cvah__ebfz, hcxl__sogfr, A._data)
            item_ind = 0
            ptrg__koqtu = 0
            for zliao__tycpk in range(jign__hjx):
                if ind[zliao__tycpk]:
                    wqvv__jwp = getitem_c_arr(A._index_offsets, zliao__tycpk)
                    jaa__odlzc = getitem_c_arr(A._index_offsets, 
                        zliao__tycpk + 1)
                    nan__tef = jaa__odlzc - wqvv__jwp
                    setitem_c_arr(mhm__nlq._index_offsets, item_ind,
                        ptrg__koqtu)
                    gkb__axxbl = get_c_arr_ptr(A._data_offsets, wqvv__jwp)
                    aqjc__futd = get_c_arr_ptr(mhm__nlq._data_offsets,
                        ptrg__koqtu)
                    _memcpy(aqjc__futd, gkb__axxbl, nan__tef, zekg__fmecz)
                    dtmuk__sllin = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, zliao__tycpk)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mhm__nlq.
                        _null_bitmap, item_ind, dtmuk__sllin)
                    item_ind += 1
                    ptrg__koqtu += nan__tef
            setitem_c_arr(mhm__nlq._index_offsets, item_ind, ptrg__koqtu)
            return mhm__nlq
        return _impl
