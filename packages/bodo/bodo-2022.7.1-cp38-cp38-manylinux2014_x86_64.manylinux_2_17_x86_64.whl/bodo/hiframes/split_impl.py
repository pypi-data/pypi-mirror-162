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
        zhxhy__zxg = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, zhxhy__zxg)


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
    tsus__vemx = context.get_value_type(str_arr_split_view_payload_type)
    sysdk__lquuf = context.get_abi_sizeof(tsus__vemx)
    uyyo__tofqv = context.get_value_type(types.voidptr)
    tnly__lnc = context.get_value_type(types.uintp)
    fhnxl__leqb = lir.FunctionType(lir.VoidType(), [uyyo__tofqv, tnly__lnc,
        uyyo__tofqv])
    gfue__cpr = cgutils.get_or_insert_function(builder.module, fhnxl__leqb,
        name='dtor_str_arr_split_view')
    szgj__zpxl = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, sysdk__lquuf), gfue__cpr)
    kex__dirsf = context.nrt.meminfo_data(builder, szgj__zpxl)
    lvfft__dhyrw = builder.bitcast(kex__dirsf, tsus__vemx.as_pointer())
    return szgj__zpxl, lvfft__dhyrw


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        rydj__jkt, tsa__xxj = args
        szgj__zpxl, lvfft__dhyrw = construct_str_arr_split_view(context,
            builder)
        fqj__onbh = _get_str_binary_arr_payload(context, builder, rydj__jkt,
            string_array_type)
        dmy__kmy = lir.FunctionType(lir.VoidType(), [lvfft__dhyrw.type, lir
            .IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        rgmj__ittb = cgutils.get_or_insert_function(builder.module,
            dmy__kmy, name='str_arr_split_view_impl')
        hnnnv__tqheg = context.make_helper(builder, offset_arr_type,
            fqj__onbh.offsets).data
        yydh__nkft = context.make_helper(builder, char_arr_type, fqj__onbh.data
            ).data
        oifow__xfim = context.make_helper(builder, null_bitmap_arr_type,
            fqj__onbh.null_bitmap).data
        cglq__xcb = context.get_constant(types.int8, ord(sep_typ.literal_value)
            )
        builder.call(rgmj__ittb, [lvfft__dhyrw, fqj__onbh.n_arrays,
            hnnnv__tqheg, yydh__nkft, oifow__xfim, cglq__xcb])
        ugxob__oeskm = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(lvfft__dhyrw))
        upl__pnsq = context.make_helper(builder, string_array_split_view_type)
        upl__pnsq.num_items = fqj__onbh.n_arrays
        upl__pnsq.index_offsets = ugxob__oeskm.index_offsets
        upl__pnsq.data_offsets = ugxob__oeskm.data_offsets
        upl__pnsq.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [rydj__jkt])
        upl__pnsq.null_bitmap = ugxob__oeskm.null_bitmap
        upl__pnsq.meminfo = szgj__zpxl
        msas__gxur = upl__pnsq._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, msas__gxur)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    lza__kiy = context.make_helper(builder, string_array_split_view_type, val)
    ihqxj__nqt = context.insert_const_string(builder.module, 'numpy')
    ycwwo__ubjfg = c.pyapi.import_module_noblock(ihqxj__nqt)
    dtype = c.pyapi.object_getattr_string(ycwwo__ubjfg, 'object_')
    plm__atbf = builder.sext(lza__kiy.num_items, c.pyapi.longlong)
    ykjzp__rhapj = c.pyapi.long_from_longlong(plm__atbf)
    zeftc__cvri = c.pyapi.call_method(ycwwo__ubjfg, 'ndarray', (
        ykjzp__rhapj, dtype))
    cnh__gklj = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    lqp__orkll = c.pyapi._get_function(cnh__gklj, name='array_getptr1')
    dhv__kzah = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    tvc__fhmb = c.pyapi._get_function(dhv__kzah, name='array_setitem')
    sthj__ittbd = c.pyapi.object_getattr_string(ycwwo__ubjfg, 'nan')
    with cgutils.for_range(builder, lza__kiy.num_items) as uymk__pva:
        str_ind = uymk__pva.index
        orip__hpg = builder.sext(builder.load(builder.gep(lza__kiy.
            index_offsets, [str_ind])), lir.IntType(64))
        jch__aht = builder.sext(builder.load(builder.gep(lza__kiy.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        esui__epf = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        rsig__fowq = builder.gep(lza__kiy.null_bitmap, [esui__epf])
        hvkq__rqkb = builder.load(rsig__fowq)
        sjc__cugwd = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(hvkq__rqkb, sjc__cugwd), lir.
            Constant(lir.IntType(8), 1))
        yfjkh__ump = builder.sub(jch__aht, orip__hpg)
        yfjkh__ump = builder.sub(yfjkh__ump, yfjkh__ump.type(1))
        gyq__wyrw = builder.call(lqp__orkll, [zeftc__cvri, str_ind])
        nuoat__jch = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(nuoat__jch) as (yra__cco, hzz__vani):
            with yra__cco:
                bewi__zqbp = c.pyapi.list_new(yfjkh__ump)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    bewi__zqbp), likely=True):
                    with cgutils.for_range(c.builder, yfjkh__ump) as uymk__pva:
                        mxk__cjn = builder.add(orip__hpg, uymk__pva.index)
                        data_start = builder.load(builder.gep(lza__kiy.
                            data_offsets, [mxk__cjn]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        vcfn__kat = builder.load(builder.gep(lza__kiy.
                            data_offsets, [builder.add(mxk__cjn, mxk__cjn.
                            type(1))]))
                        omjky__bqmn = builder.gep(builder.extract_value(
                            lza__kiy.data, 0), [data_start])
                        qtbiz__bylmm = builder.sext(builder.sub(vcfn__kat,
                            data_start), lir.IntType(64))
                        scej__aycvn = c.pyapi.string_from_string_and_size(
                            omjky__bqmn, qtbiz__bylmm)
                        c.pyapi.list_setitem(bewi__zqbp, uymk__pva.index,
                            scej__aycvn)
                builder.call(tvc__fhmb, [zeftc__cvri, gyq__wyrw, bewi__zqbp])
            with hzz__vani:
                builder.call(tvc__fhmb, [zeftc__cvri, gyq__wyrw, sthj__ittbd])
    c.pyapi.decref(ycwwo__ubjfg)
    c.pyapi.decref(dtype)
    c.pyapi.decref(sthj__ittbd)
    return zeftc__cvri


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        esf__lcedr, xtb__knzhq, omjky__bqmn = args
        szgj__zpxl, lvfft__dhyrw = construct_str_arr_split_view(context,
            builder)
        dmy__kmy = lir.FunctionType(lir.VoidType(), [lvfft__dhyrw.type, lir
            .IntType(64), lir.IntType(64)])
        rgmj__ittb = cgutils.get_or_insert_function(builder.module,
            dmy__kmy, name='str_arr_split_view_alloc')
        builder.call(rgmj__ittb, [lvfft__dhyrw, esf__lcedr, xtb__knzhq])
        ugxob__oeskm = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(lvfft__dhyrw))
        upl__pnsq = context.make_helper(builder, string_array_split_view_type)
        upl__pnsq.num_items = esf__lcedr
        upl__pnsq.index_offsets = ugxob__oeskm.index_offsets
        upl__pnsq.data_offsets = ugxob__oeskm.data_offsets
        upl__pnsq.data = omjky__bqmn
        upl__pnsq.null_bitmap = ugxob__oeskm.null_bitmap
        context.nrt.incref(builder, data_t, omjky__bqmn)
        upl__pnsq.meminfo = szgj__zpxl
        msas__gxur = upl__pnsq._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, msas__gxur)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        lsay__bius, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            lsay__bius = builder.extract_value(lsay__bius, 0)
        return builder.bitcast(builder.gep(lsay__bius, [ind]), lir.IntType(
            8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        lsay__bius, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            lsay__bius = builder.extract_value(lsay__bius, 0)
        return builder.load(builder.gep(lsay__bius, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        lsay__bius, ind, rkij__cbcgz = args
        tpx__qend = builder.gep(lsay__bius, [ind])
        builder.store(rkij__cbcgz, tpx__qend)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        fptsj__rkauq, ind = args
        rhib__zad = context.make_helper(builder, arr_ctypes_t, fptsj__rkauq)
        ibngi__pzs = context.make_helper(builder, arr_ctypes_t)
        ibngi__pzs.data = builder.gep(rhib__zad.data, [ind])
        ibngi__pzs.meminfo = rhib__zad.meminfo
        nhdex__wpkcr = ibngi__pzs._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, nhdex__wpkcr)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    uer__cpi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not uer__cpi:
        return 0, 0, 0
    mxk__cjn = getitem_c_arr(arr._index_offsets, item_ind)
    gbx__fui = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    szgq__aia = gbx__fui - mxk__cjn
    if str_ind >= szgq__aia:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, mxk__cjn + str_ind)
    data_start += 1
    if mxk__cjn + str_ind == 0:
        data_start = 0
    vcfn__kat = getitem_c_arr(arr._data_offsets, mxk__cjn + str_ind + 1)
    ftepq__dkya = vcfn__kat - data_start
    return 1, data_start, ftepq__dkya


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
        nev__oyu = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            mxk__cjn = getitem_c_arr(A._index_offsets, ind)
            gbx__fui = getitem_c_arr(A._index_offsets, ind + 1)
            dlw__gds = gbx__fui - mxk__cjn - 1
            rydj__jkt = bodo.libs.str_arr_ext.pre_alloc_string_array(dlw__gds,
                -1)
            for bdvjw__aij in range(dlw__gds):
                data_start = getitem_c_arr(A._data_offsets, mxk__cjn +
                    bdvjw__aij)
                data_start += 1
                if mxk__cjn + bdvjw__aij == 0:
                    data_start = 0
                vcfn__kat = getitem_c_arr(A._data_offsets, mxk__cjn +
                    bdvjw__aij + 1)
                ftepq__dkya = vcfn__kat - data_start
                tpx__qend = get_array_ctypes_ptr(A._data, data_start)
                vuvxv__ilmcv = bodo.libs.str_arr_ext.decode_utf8(tpx__qend,
                    ftepq__dkya)
                rydj__jkt[bdvjw__aij] = vuvxv__ilmcv
            return rydj__jkt
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        cnhvy__tvt = offset_type.bitwidth // 8

        def _impl(A, ind):
            dlw__gds = len(A)
            if dlw__gds != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            esf__lcedr = 0
            xtb__knzhq = 0
            for bdvjw__aij in range(dlw__gds):
                if ind[bdvjw__aij]:
                    esf__lcedr += 1
                    mxk__cjn = getitem_c_arr(A._index_offsets, bdvjw__aij)
                    gbx__fui = getitem_c_arr(A._index_offsets, bdvjw__aij + 1)
                    xtb__knzhq += gbx__fui - mxk__cjn
            zeftc__cvri = pre_alloc_str_arr_view(esf__lcedr, xtb__knzhq, A.
                _data)
            item_ind = 0
            zhwsv__htnde = 0
            for bdvjw__aij in range(dlw__gds):
                if ind[bdvjw__aij]:
                    mxk__cjn = getitem_c_arr(A._index_offsets, bdvjw__aij)
                    gbx__fui = getitem_c_arr(A._index_offsets, bdvjw__aij + 1)
                    hdvr__cqaou = gbx__fui - mxk__cjn
                    setitem_c_arr(zeftc__cvri._index_offsets, item_ind,
                        zhwsv__htnde)
                    tpx__qend = get_c_arr_ptr(A._data_offsets, mxk__cjn)
                    lxy__zmf = get_c_arr_ptr(zeftc__cvri._data_offsets,
                        zhwsv__htnde)
                    _memcpy(lxy__zmf, tpx__qend, hdvr__cqaou, cnhvy__tvt)
                    uer__cpi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, bdvjw__aij)
                    bodo.libs.int_arr_ext.set_bit_to_arr(zeftc__cvri.
                        _null_bitmap, item_ind, uer__cpi)
                    item_ind += 1
                    zhwsv__htnde += hdvr__cqaou
            setitem_c_arr(zeftc__cvri._index_offsets, item_ind, zhwsv__htnde)
            return zeftc__cvri
        return _impl
