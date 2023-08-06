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
        trb__ryn = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, trb__ryn)


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
    hezuv__ymoc = context.get_value_type(str_arr_split_view_payload_type)
    fuj__cdft = context.get_abi_sizeof(hezuv__ymoc)
    jlgg__hhho = context.get_value_type(types.voidptr)
    wuv__qwipu = context.get_value_type(types.uintp)
    nti__oca = lir.FunctionType(lir.VoidType(), [jlgg__hhho, wuv__qwipu,
        jlgg__hhho])
    ynz__fvuo = cgutils.get_or_insert_function(builder.module, nti__oca,
        name='dtor_str_arr_split_view')
    qtdd__alcq = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, fuj__cdft), ynz__fvuo)
    mtjp__ylkvt = context.nrt.meminfo_data(builder, qtdd__alcq)
    eiaad__sagup = builder.bitcast(mtjp__ylkvt, hezuv__ymoc.as_pointer())
    return qtdd__alcq, eiaad__sagup


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        ltxm__lpx, hzvag__jby = args
        qtdd__alcq, eiaad__sagup = construct_str_arr_split_view(context,
            builder)
        fug__rxfp = _get_str_binary_arr_payload(context, builder, ltxm__lpx,
            string_array_type)
        bfiin__hdzy = lir.FunctionType(lir.VoidType(), [eiaad__sagup.type,
            lir.IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        cglud__niz = cgutils.get_or_insert_function(builder.module,
            bfiin__hdzy, name='str_arr_split_view_impl')
        uhc__qjkcg = context.make_helper(builder, offset_arr_type,
            fug__rxfp.offsets).data
        dqlxf__yat = context.make_helper(builder, char_arr_type, fug__rxfp.data
            ).data
        lrslz__pfgrz = context.make_helper(builder, null_bitmap_arr_type,
            fug__rxfp.null_bitmap).data
        xiyr__kbegk = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(cglud__niz, [eiaad__sagup, fug__rxfp.n_arrays,
            uhc__qjkcg, dqlxf__yat, lrslz__pfgrz, xiyr__kbegk])
        lrr__nbqa = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(eiaad__sagup))
        zkrht__ucpc = context.make_helper(builder, string_array_split_view_type
            )
        zkrht__ucpc.num_items = fug__rxfp.n_arrays
        zkrht__ucpc.index_offsets = lrr__nbqa.index_offsets
        zkrht__ucpc.data_offsets = lrr__nbqa.data_offsets
        zkrht__ucpc.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [ltxm__lpx])
        zkrht__ucpc.null_bitmap = lrr__nbqa.null_bitmap
        zkrht__ucpc.meminfo = qtdd__alcq
        jatnv__alwe = zkrht__ucpc._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, jatnv__alwe)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    vqvw__lualc = context.make_helper(builder, string_array_split_view_type,
        val)
    dubg__sbu = context.insert_const_string(builder.module, 'numpy')
    jlogn__eezjn = c.pyapi.import_module_noblock(dubg__sbu)
    dtype = c.pyapi.object_getattr_string(jlogn__eezjn, 'object_')
    ijp__ngxsh = builder.sext(vqvw__lualc.num_items, c.pyapi.longlong)
    iarbi__asf = c.pyapi.long_from_longlong(ijp__ngxsh)
    yljpb__fook = c.pyapi.call_method(jlogn__eezjn, 'ndarray', (iarbi__asf,
        dtype))
    tshig__huncs = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    aapg__zjxf = c.pyapi._get_function(tshig__huncs, name='array_getptr1')
    oyua__vobi = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    mdx__sdf = c.pyapi._get_function(oyua__vobi, name='array_setitem')
    uua__epp = c.pyapi.object_getattr_string(jlogn__eezjn, 'nan')
    with cgutils.for_range(builder, vqvw__lualc.num_items) as wyp__juj:
        str_ind = wyp__juj.index
        chi__ttwv = builder.sext(builder.load(builder.gep(vqvw__lualc.
            index_offsets, [str_ind])), lir.IntType(64))
        gkbw__gaj = builder.sext(builder.load(builder.gep(vqvw__lualc.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        yqjnh__hbqwu = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        yrid__tdgf = builder.gep(vqvw__lualc.null_bitmap, [yqjnh__hbqwu])
        ybqx__wxi = builder.load(yrid__tdgf)
        vbu__ayz = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(ybqx__wxi, vbu__ayz), lir.Constant(
            lir.IntType(8), 1))
        krdi__hsjva = builder.sub(gkbw__gaj, chi__ttwv)
        krdi__hsjva = builder.sub(krdi__hsjva, krdi__hsjva.type(1))
        mvxm__goec = builder.call(aapg__zjxf, [yljpb__fook, str_ind])
        ypl__gqkl = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(ypl__gqkl) as (jtkvn__oyan, ronab__isda):
            with jtkvn__oyan:
                xzt__amnq = c.pyapi.list_new(krdi__hsjva)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    xzt__amnq), likely=True):
                    with cgutils.for_range(c.builder, krdi__hsjva) as wyp__juj:
                        vvpug__ynh = builder.add(chi__ttwv, wyp__juj.index)
                        data_start = builder.load(builder.gep(vqvw__lualc.
                            data_offsets, [vvpug__ynh]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        cddi__sdlz = builder.load(builder.gep(vqvw__lualc.
                            data_offsets, [builder.add(vvpug__ynh,
                            vvpug__ynh.type(1))]))
                        wip__rsu = builder.gep(builder.extract_value(
                            vqvw__lualc.data, 0), [data_start])
                        hyii__mrs = builder.sext(builder.sub(cddi__sdlz,
                            data_start), lir.IntType(64))
                        alno__jvun = c.pyapi.string_from_string_and_size(
                            wip__rsu, hyii__mrs)
                        c.pyapi.list_setitem(xzt__amnq, wyp__juj.index,
                            alno__jvun)
                builder.call(mdx__sdf, [yljpb__fook, mvxm__goec, xzt__amnq])
            with ronab__isda:
                builder.call(mdx__sdf, [yljpb__fook, mvxm__goec, uua__epp])
    c.pyapi.decref(jlogn__eezjn)
    c.pyapi.decref(dtype)
    c.pyapi.decref(uua__epp)
    return yljpb__fook


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        rzwtf__gvx, mwu__fmj, wip__rsu = args
        qtdd__alcq, eiaad__sagup = construct_str_arr_split_view(context,
            builder)
        bfiin__hdzy = lir.FunctionType(lir.VoidType(), [eiaad__sagup.type,
            lir.IntType(64), lir.IntType(64)])
        cglud__niz = cgutils.get_or_insert_function(builder.module,
            bfiin__hdzy, name='str_arr_split_view_alloc')
        builder.call(cglud__niz, [eiaad__sagup, rzwtf__gvx, mwu__fmj])
        lrr__nbqa = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(eiaad__sagup))
        zkrht__ucpc = context.make_helper(builder, string_array_split_view_type
            )
        zkrht__ucpc.num_items = rzwtf__gvx
        zkrht__ucpc.index_offsets = lrr__nbqa.index_offsets
        zkrht__ucpc.data_offsets = lrr__nbqa.data_offsets
        zkrht__ucpc.data = wip__rsu
        zkrht__ucpc.null_bitmap = lrr__nbqa.null_bitmap
        context.nrt.incref(builder, data_t, wip__rsu)
        zkrht__ucpc.meminfo = qtdd__alcq
        jatnv__alwe = zkrht__ucpc._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, jatnv__alwe)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        eevc__fuz, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            eevc__fuz = builder.extract_value(eevc__fuz, 0)
        return builder.bitcast(builder.gep(eevc__fuz, [ind]), lir.IntType(8
            ).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        eevc__fuz, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            eevc__fuz = builder.extract_value(eevc__fuz, 0)
        return builder.load(builder.gep(eevc__fuz, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        eevc__fuz, ind, fpvu__rvaal = args
        aznbp__ascdw = builder.gep(eevc__fuz, [ind])
        builder.store(fpvu__rvaal, aznbp__ascdw)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        yurfr__lralg, ind = args
        mhr__hbn = context.make_helper(builder, arr_ctypes_t, yurfr__lralg)
        nkfex__cqik = context.make_helper(builder, arr_ctypes_t)
        nkfex__cqik.data = builder.gep(mhr__hbn.data, [ind])
        nkfex__cqik.meminfo = mhr__hbn.meminfo
        xzfkg__yoep = nkfex__cqik._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, xzfkg__yoep)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    wqps__ylee = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not wqps__ylee:
        return 0, 0, 0
    vvpug__ynh = getitem_c_arr(arr._index_offsets, item_ind)
    fbwo__txt = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    jdgk__fsxes = fbwo__txt - vvpug__ynh
    if str_ind >= jdgk__fsxes:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, vvpug__ynh + str_ind)
    data_start += 1
    if vvpug__ynh + str_ind == 0:
        data_start = 0
    cddi__sdlz = getitem_c_arr(arr._data_offsets, vvpug__ynh + str_ind + 1)
    rqfvi__rrxeg = cddi__sdlz - data_start
    return 1, data_start, rqfvi__rrxeg


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
        vmyiy__ukvnp = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            vvpug__ynh = getitem_c_arr(A._index_offsets, ind)
            fbwo__txt = getitem_c_arr(A._index_offsets, ind + 1)
            qoff__punp = fbwo__txt - vvpug__ynh - 1
            ltxm__lpx = bodo.libs.str_arr_ext.pre_alloc_string_array(qoff__punp
                , -1)
            for fen__fdj in range(qoff__punp):
                data_start = getitem_c_arr(A._data_offsets, vvpug__ynh +
                    fen__fdj)
                data_start += 1
                if vvpug__ynh + fen__fdj == 0:
                    data_start = 0
                cddi__sdlz = getitem_c_arr(A._data_offsets, vvpug__ynh +
                    fen__fdj + 1)
                rqfvi__rrxeg = cddi__sdlz - data_start
                aznbp__ascdw = get_array_ctypes_ptr(A._data, data_start)
                jfuec__nrhay = bodo.libs.str_arr_ext.decode_utf8(aznbp__ascdw,
                    rqfvi__rrxeg)
                ltxm__lpx[fen__fdj] = jfuec__nrhay
            return ltxm__lpx
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        ujgj__foet = offset_type.bitwidth // 8

        def _impl(A, ind):
            qoff__punp = len(A)
            if qoff__punp != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            rzwtf__gvx = 0
            mwu__fmj = 0
            for fen__fdj in range(qoff__punp):
                if ind[fen__fdj]:
                    rzwtf__gvx += 1
                    vvpug__ynh = getitem_c_arr(A._index_offsets, fen__fdj)
                    fbwo__txt = getitem_c_arr(A._index_offsets, fen__fdj + 1)
                    mwu__fmj += fbwo__txt - vvpug__ynh
            yljpb__fook = pre_alloc_str_arr_view(rzwtf__gvx, mwu__fmj, A._data)
            item_ind = 0
            cbut__zoe = 0
            for fen__fdj in range(qoff__punp):
                if ind[fen__fdj]:
                    vvpug__ynh = getitem_c_arr(A._index_offsets, fen__fdj)
                    fbwo__txt = getitem_c_arr(A._index_offsets, fen__fdj + 1)
                    vap__vxr = fbwo__txt - vvpug__ynh
                    setitem_c_arr(yljpb__fook._index_offsets, item_ind,
                        cbut__zoe)
                    aznbp__ascdw = get_c_arr_ptr(A._data_offsets, vvpug__ynh)
                    aogy__fjkk = get_c_arr_ptr(yljpb__fook._data_offsets,
                        cbut__zoe)
                    _memcpy(aogy__fjkk, aznbp__ascdw, vap__vxr, ujgj__foet)
                    wqps__ylee = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, fen__fdj)
                    bodo.libs.int_arr_ext.set_bit_to_arr(yljpb__fook.
                        _null_bitmap, item_ind, wqps__ylee)
                    item_ind += 1
                    cbut__zoe += vap__vxr
            setitem_c_arr(yljpb__fook._index_offsets, item_ind, cbut__zoe)
            return yljpb__fook
        return _impl
