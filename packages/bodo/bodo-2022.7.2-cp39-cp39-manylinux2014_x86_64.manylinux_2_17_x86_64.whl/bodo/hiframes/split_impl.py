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
        oip__uhsa = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, oip__uhsa)


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
    buwk__lehvu = context.get_value_type(str_arr_split_view_payload_type)
    zvt__babpq = context.get_abi_sizeof(buwk__lehvu)
    ing__rlutv = context.get_value_type(types.voidptr)
    nar__urjct = context.get_value_type(types.uintp)
    ouq__nriv = lir.FunctionType(lir.VoidType(), [ing__rlutv, nar__urjct,
        ing__rlutv])
    wqhl__ldq = cgutils.get_or_insert_function(builder.module, ouq__nriv,
        name='dtor_str_arr_split_view')
    lvhnt__wov = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, zvt__babpq), wqhl__ldq)
    akya__hbn = context.nrt.meminfo_data(builder, lvhnt__wov)
    zgao__pcpgo = builder.bitcast(akya__hbn, buwk__lehvu.as_pointer())
    return lvhnt__wov, zgao__pcpgo


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        peusd__yhf, mszr__sbldy = args
        lvhnt__wov, zgao__pcpgo = construct_str_arr_split_view(context, builder
            )
        pmmo__zedk = _get_str_binary_arr_payload(context, builder,
            peusd__yhf, string_array_type)
        ibf__afg = lir.FunctionType(lir.VoidType(), [zgao__pcpgo.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        agn__ark = cgutils.get_or_insert_function(builder.module, ibf__afg,
            name='str_arr_split_view_impl')
        rxnu__cicx = context.make_helper(builder, offset_arr_type,
            pmmo__zedk.offsets).data
        uwubz__zyc = context.make_helper(builder, char_arr_type, pmmo__zedk
            .data).data
        xujcy__ukr = context.make_helper(builder, null_bitmap_arr_type,
            pmmo__zedk.null_bitmap).data
        cbz__oylza = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(agn__ark, [zgao__pcpgo, pmmo__zedk.n_arrays,
            rxnu__cicx, uwubz__zyc, xujcy__ukr, cbz__oylza])
        vqx__isd = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(zgao__pcpgo))
        ojwcl__pqi = context.make_helper(builder, string_array_split_view_type)
        ojwcl__pqi.num_items = pmmo__zedk.n_arrays
        ojwcl__pqi.index_offsets = vqx__isd.index_offsets
        ojwcl__pqi.data_offsets = vqx__isd.data_offsets
        ojwcl__pqi.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [peusd__yhf])
        ojwcl__pqi.null_bitmap = vqx__isd.null_bitmap
        ojwcl__pqi.meminfo = lvhnt__wov
        xwei__hdgq = ojwcl__pqi._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, xwei__hdgq)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    xrp__nfkz = context.make_helper(builder, string_array_split_view_type, val)
    epn__yyry = context.insert_const_string(builder.module, 'numpy')
    rla__wgsri = c.pyapi.import_module_noblock(epn__yyry)
    dtype = c.pyapi.object_getattr_string(rla__wgsri, 'object_')
    uzw__mfwg = builder.sext(xrp__nfkz.num_items, c.pyapi.longlong)
    dvj__clhid = c.pyapi.long_from_longlong(uzw__mfwg)
    atdzk__aod = c.pyapi.call_method(rla__wgsri, 'ndarray', (dvj__clhid, dtype)
        )
    wncn__zutg = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    whc__pluf = c.pyapi._get_function(wncn__zutg, name='array_getptr1')
    cxyb__seand = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    saw__mwlys = c.pyapi._get_function(cxyb__seand, name='array_setitem')
    surqu__xvl = c.pyapi.object_getattr_string(rla__wgsri, 'nan')
    with cgutils.for_range(builder, xrp__nfkz.num_items) as hgx__mabm:
        str_ind = hgx__mabm.index
        vtfg__jhoa = builder.sext(builder.load(builder.gep(xrp__nfkz.
            index_offsets, [str_ind])), lir.IntType(64))
        ryl__lnn = builder.sext(builder.load(builder.gep(xrp__nfkz.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        xyxg__bxs = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        itvml__hcdk = builder.gep(xrp__nfkz.null_bitmap, [xyxg__bxs])
        iar__zdnbi = builder.load(itvml__hcdk)
        amfdy__fgih = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(iar__zdnbi, amfdy__fgih), lir.
            Constant(lir.IntType(8), 1))
        nvq__wkjo = builder.sub(ryl__lnn, vtfg__jhoa)
        nvq__wkjo = builder.sub(nvq__wkjo, nvq__wkjo.type(1))
        vfqu__ixbo = builder.call(whc__pluf, [atdzk__aod, str_ind])
        ypxt__uahxs = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(ypxt__uahxs) as (hgl__dpm, pqqr__oya):
            with hgl__dpm:
                ajkha__aopom = c.pyapi.list_new(nvq__wkjo)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    ajkha__aopom), likely=True):
                    with cgutils.for_range(c.builder, nvq__wkjo) as hgx__mabm:
                        harh__sbeh = builder.add(vtfg__jhoa, hgx__mabm.index)
                        data_start = builder.load(builder.gep(xrp__nfkz.
                            data_offsets, [harh__sbeh]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        kkuva__juzmy = builder.load(builder.gep(xrp__nfkz.
                            data_offsets, [builder.add(harh__sbeh,
                            harh__sbeh.type(1))]))
                        gzyt__jagq = builder.gep(builder.extract_value(
                            xrp__nfkz.data, 0), [data_start])
                        nabnp__dnq = builder.sext(builder.sub(kkuva__juzmy,
                            data_start), lir.IntType(64))
                        lrwhz__ohboe = c.pyapi.string_from_string_and_size(
                            gzyt__jagq, nabnp__dnq)
                        c.pyapi.list_setitem(ajkha__aopom, hgx__mabm.index,
                            lrwhz__ohboe)
                builder.call(saw__mwlys, [atdzk__aod, vfqu__ixbo, ajkha__aopom]
                    )
            with pqqr__oya:
                builder.call(saw__mwlys, [atdzk__aod, vfqu__ixbo, surqu__xvl])
    c.pyapi.decref(rla__wgsri)
    c.pyapi.decref(dtype)
    c.pyapi.decref(surqu__xvl)
    return atdzk__aod


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        jyz__ikpu, atl__cos, gzyt__jagq = args
        lvhnt__wov, zgao__pcpgo = construct_str_arr_split_view(context, builder
            )
        ibf__afg = lir.FunctionType(lir.VoidType(), [zgao__pcpgo.type, lir.
            IntType(64), lir.IntType(64)])
        agn__ark = cgutils.get_or_insert_function(builder.module, ibf__afg,
            name='str_arr_split_view_alloc')
        builder.call(agn__ark, [zgao__pcpgo, jyz__ikpu, atl__cos])
        vqx__isd = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(zgao__pcpgo))
        ojwcl__pqi = context.make_helper(builder, string_array_split_view_type)
        ojwcl__pqi.num_items = jyz__ikpu
        ojwcl__pqi.index_offsets = vqx__isd.index_offsets
        ojwcl__pqi.data_offsets = vqx__isd.data_offsets
        ojwcl__pqi.data = gzyt__jagq
        ojwcl__pqi.null_bitmap = vqx__isd.null_bitmap
        context.nrt.incref(builder, data_t, gzyt__jagq)
        ojwcl__pqi.meminfo = lvhnt__wov
        xwei__hdgq = ojwcl__pqi._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, xwei__hdgq)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        fxao__idi, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            fxao__idi = builder.extract_value(fxao__idi, 0)
        return builder.bitcast(builder.gep(fxao__idi, [ind]), lir.IntType(8
            ).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        fxao__idi, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            fxao__idi = builder.extract_value(fxao__idi, 0)
        return builder.load(builder.gep(fxao__idi, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        fxao__idi, ind, ncuw__lfed = args
        oyohu__wkpe = builder.gep(fxao__idi, [ind])
        builder.store(ncuw__lfed, oyohu__wkpe)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        icnr__winef, ind = args
        rbog__vyb = context.make_helper(builder, arr_ctypes_t, icnr__winef)
        avun__wdpv = context.make_helper(builder, arr_ctypes_t)
        avun__wdpv.data = builder.gep(rbog__vyb.data, [ind])
        avun__wdpv.meminfo = rbog__vyb.meminfo
        vkd__vpz = avun__wdpv._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, vkd__vpz)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    jfklk__bwi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not jfklk__bwi:
        return 0, 0, 0
    harh__sbeh = getitem_c_arr(arr._index_offsets, item_ind)
    awtiu__alkil = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    smp__assq = awtiu__alkil - harh__sbeh
    if str_ind >= smp__assq:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, harh__sbeh + str_ind)
    data_start += 1
    if harh__sbeh + str_ind == 0:
        data_start = 0
    kkuva__juzmy = getitem_c_arr(arr._data_offsets, harh__sbeh + str_ind + 1)
    hbigd__qahg = kkuva__juzmy - data_start
    return 1, data_start, hbigd__qahg


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
        past__doky = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            harh__sbeh = getitem_c_arr(A._index_offsets, ind)
            awtiu__alkil = getitem_c_arr(A._index_offsets, ind + 1)
            kyix__jwux = awtiu__alkil - harh__sbeh - 1
            peusd__yhf = bodo.libs.str_arr_ext.pre_alloc_string_array(
                kyix__jwux, -1)
            for bjun__logz in range(kyix__jwux):
                data_start = getitem_c_arr(A._data_offsets, harh__sbeh +
                    bjun__logz)
                data_start += 1
                if harh__sbeh + bjun__logz == 0:
                    data_start = 0
                kkuva__juzmy = getitem_c_arr(A._data_offsets, harh__sbeh +
                    bjun__logz + 1)
                hbigd__qahg = kkuva__juzmy - data_start
                oyohu__wkpe = get_array_ctypes_ptr(A._data, data_start)
                zvr__osz = bodo.libs.str_arr_ext.decode_utf8(oyohu__wkpe,
                    hbigd__qahg)
                peusd__yhf[bjun__logz] = zvr__osz
            return peusd__yhf
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        llrii__soqi = offset_type.bitwidth // 8

        def _impl(A, ind):
            kyix__jwux = len(A)
            if kyix__jwux != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            jyz__ikpu = 0
            atl__cos = 0
            for bjun__logz in range(kyix__jwux):
                if ind[bjun__logz]:
                    jyz__ikpu += 1
                    harh__sbeh = getitem_c_arr(A._index_offsets, bjun__logz)
                    awtiu__alkil = getitem_c_arr(A._index_offsets, 
                        bjun__logz + 1)
                    atl__cos += awtiu__alkil - harh__sbeh
            atdzk__aod = pre_alloc_str_arr_view(jyz__ikpu, atl__cos, A._data)
            item_ind = 0
            pcsp__ajxjz = 0
            for bjun__logz in range(kyix__jwux):
                if ind[bjun__logz]:
                    harh__sbeh = getitem_c_arr(A._index_offsets, bjun__logz)
                    awtiu__alkil = getitem_c_arr(A._index_offsets, 
                        bjun__logz + 1)
                    jfhf__zzfkc = awtiu__alkil - harh__sbeh
                    setitem_c_arr(atdzk__aod._index_offsets, item_ind,
                        pcsp__ajxjz)
                    oyohu__wkpe = get_c_arr_ptr(A._data_offsets, harh__sbeh)
                    ifj__wyotf = get_c_arr_ptr(atdzk__aod._data_offsets,
                        pcsp__ajxjz)
                    _memcpy(ifj__wyotf, oyohu__wkpe, jfhf__zzfkc, llrii__soqi)
                    jfklk__bwi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, bjun__logz)
                    bodo.libs.int_arr_ext.set_bit_to_arr(atdzk__aod.
                        _null_bitmap, item_ind, jfklk__bwi)
                    item_ind += 1
                    pcsp__ajxjz += jfhf__zzfkc
            setitem_c_arr(atdzk__aod._index_offsets, item_ind, pcsp__ajxjz)
            return atdzk__aod
        return _impl
