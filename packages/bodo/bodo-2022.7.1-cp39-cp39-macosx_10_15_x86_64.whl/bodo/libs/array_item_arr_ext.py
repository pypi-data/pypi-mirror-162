"""Array implementation for variable-size array items.
Corresponds to Spark's ArrayType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Variable-size List: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in a contingous data array, while an offsets array marks the
individual arrays. For example:
value:             [[1, 2], [3], None, [5, 4, 6], []]
data:              [1, 2, 3, 5, 4, 6]
offsets:           [0, 2, 3, 3, 6, 6]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('array_item_array_from_sequence', array_ext.
    array_item_array_from_sequence)
ll.add_symbol('np_array_from_array_item_array', array_ext.
    np_array_from_array_item_array)
offset_type = types.uint64
np_offset_type = numba.np.numpy_support.as_dtype(offset_type)


class ArrayItemArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        assert bodo.utils.utils.is_array_typ(dtype, False)
        self.dtype = dtype
        super(ArrayItemArrayType, self).__init__(name=
            'ArrayItemArrayType({})'.format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return ArrayItemArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class ArrayItemArrayPayloadType(types.Type):

    def __init__(self, array_type):
        self.array_type = array_type
        super(ArrayItemArrayPayloadType, self).__init__(name=
            'ArrayItemArrayPayloadType({})'.format(array_type))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(ArrayItemArrayPayloadType)
class ArrayItemArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dnxzu__abr = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, dnxzu__abr)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        dnxzu__abr = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, dnxzu__abr)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    uwsii__kaig = builder.module
    pxp__wcyp = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    uyzx__lhkj = cgutils.get_or_insert_function(uwsii__kaig, pxp__wcyp,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not uyzx__lhkj.is_declaration:
        return uyzx__lhkj
    uyzx__lhkj.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(uyzx__lhkj.append_basic_block())
    ftyko__euv = uyzx__lhkj.args[0]
    qmgxz__ladys = context.get_value_type(payload_type).as_pointer()
    jic__vac = builder.bitcast(ftyko__euv, qmgxz__ladys)
    wfyt__reaua = context.make_helper(builder, payload_type, ref=jic__vac)
    context.nrt.decref(builder, array_item_type.dtype, wfyt__reaua.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        wfyt__reaua.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        wfyt__reaua.null_bitmap)
    builder.ret_void()
    return uyzx__lhkj


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    avbud__nar = context.get_value_type(payload_type)
    mmm__tzn = context.get_abi_sizeof(avbud__nar)
    ufcsa__qopb = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    gzsq__akz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, mmm__tzn), ufcsa__qopb)
    evnus__tkx = context.nrt.meminfo_data(builder, gzsq__akz)
    vbcol__mwrf = builder.bitcast(evnus__tkx, avbud__nar.as_pointer())
    wfyt__reaua = cgutils.create_struct_proxy(payload_type)(context, builder)
    wfyt__reaua.n_arrays = n_arrays
    yuik__xiti = n_elems.type.count
    zjgbh__lyz = builder.extract_value(n_elems, 0)
    ida__nfpmm = cgutils.alloca_once_value(builder, zjgbh__lyz)
    rxkbm__mdqqc = builder.icmp_signed('==', zjgbh__lyz, lir.Constant(
        zjgbh__lyz.type, -1))
    with builder.if_then(rxkbm__mdqqc):
        builder.store(n_arrays, ida__nfpmm)
    n_elems = cgutils.pack_array(builder, [builder.load(ida__nfpmm)] + [
        builder.extract_value(n_elems, nsvd__fjvp) for nsvd__fjvp in range(
        1, yuik__xiti)])
    wfyt__reaua.data = gen_allocate_array(context, builder, array_item_type
        .dtype, n_elems, c)
    mjsy__ual = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    wze__zzf = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [mjsy__ual])
    offsets_ptr = wze__zzf.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    wfyt__reaua.offsets = wze__zzf._getvalue()
    xvqz__qlly = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    ybbh__izlbw = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [xvqz__qlly])
    null_bitmap_ptr = ybbh__izlbw.data
    wfyt__reaua.null_bitmap = ybbh__izlbw._getvalue()
    builder.store(wfyt__reaua._getvalue(), vbcol__mwrf)
    return gzsq__akz, wfyt__reaua.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    lpac__xlk, xxjru__bepsq = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    nkrwn__qds = context.insert_const_string(builder.module, 'pandas')
    zlt__jnqyk = c.pyapi.import_module_noblock(nkrwn__qds)
    senu__cyv = c.pyapi.object_getattr_string(zlt__jnqyk, 'NA')
    yvz__vyxq = c.context.get_constant(offset_type, 0)
    builder.store(yvz__vyxq, offsets_ptr)
    phb__cfv = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as tgkn__qsl:
        pch__sids = tgkn__qsl.index
        item_ind = builder.load(phb__cfv)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [pch__sids]))
        arr_obj = seq_getitem(builder, context, val, pch__sids)
        set_bitmap_bit(builder, null_bitmap_ptr, pch__sids, 0)
        grl__jemff = is_na_value(builder, context, arr_obj, senu__cyv)
        jrxb__fdm = builder.icmp_unsigned('!=', grl__jemff, lir.Constant(
            grl__jemff.type, 1))
        with builder.if_then(jrxb__fdm):
            set_bitmap_bit(builder, null_bitmap_ptr, pch__sids, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), phb__cfv)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(phb__cfv), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(zlt__jnqyk)
    c.pyapi.decref(senu__cyv)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    biogl__wji = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if biogl__wji:
        pxp__wcyp = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        puc__qsn = cgutils.get_or_insert_function(c.builder.module,
            pxp__wcyp, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(puc__qsn, [
            val])])
    else:
        gazb__pnhfa = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            gazb__pnhfa, nsvd__fjvp) for nsvd__fjvp in range(1, gazb__pnhfa
            .type.count)])
    gzsq__akz, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if biogl__wji:
        weai__puyw = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        babcd__haf = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        pxp__wcyp = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        uyzx__lhkj = cgutils.get_or_insert_function(c.builder.module,
            pxp__wcyp, name='array_item_array_from_sequence')
        c.builder.call(uyzx__lhkj, [val, c.builder.bitcast(babcd__haf, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), weai__puyw)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    aiu__uigx = c.context.make_helper(c.builder, typ)
    aiu__uigx.meminfo = gzsq__akz
    gcq__xkj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(aiu__uigx._getvalue(), is_error=gcq__xkj)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    aiu__uigx = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    evnus__tkx = context.nrt.meminfo_data(builder, aiu__uigx.meminfo)
    vbcol__mwrf = builder.bitcast(evnus__tkx, context.get_value_type(
        payload_type).as_pointer())
    wfyt__reaua = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(vbcol__mwrf))
    return wfyt__reaua


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    nkrwn__qds = context.insert_const_string(builder.module, 'numpy')
    dmu__hdjht = c.pyapi.import_module_noblock(nkrwn__qds)
    ocvl__uck = c.pyapi.object_getattr_string(dmu__hdjht, 'object_')
    hjo__qht = c.pyapi.long_from_longlong(n_arrays)
    ifs__tqdl = c.pyapi.call_method(dmu__hdjht, 'ndarray', (hjo__qht,
        ocvl__uck))
    njc__oioil = c.pyapi.object_getattr_string(dmu__hdjht, 'nan')
    phb__cfv = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType(
        64), 0))
    with cgutils.for_range(builder, n_arrays) as tgkn__qsl:
        pch__sids = tgkn__qsl.index
        pyarray_setitem(builder, context, ifs__tqdl, pch__sids, njc__oioil)
        ssjv__tgv = get_bitmap_bit(builder, null_bitmap_ptr, pch__sids)
        gvxcx__wigsc = builder.icmp_unsigned('!=', ssjv__tgv, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(gvxcx__wigsc):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(pch__sids, lir.Constant(pch__sids
                .type, 1))])), builder.load(builder.gep(offsets_ptr, [
                pch__sids]))), lir.IntType(64))
            item_ind = builder.load(phb__cfv)
            lpac__xlk, mcfh__rwpz = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), phb__cfv)
            arr_obj = c.pyapi.from_native_value(typ.dtype, mcfh__rwpz, c.
                env_manager)
            pyarray_setitem(builder, context, ifs__tqdl, pch__sids, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(dmu__hdjht)
    c.pyapi.decref(ocvl__uck)
    c.pyapi.decref(hjo__qht)
    c.pyapi.decref(njc__oioil)
    return ifs__tqdl


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    wfyt__reaua = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = wfyt__reaua.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), wfyt__reaua.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), wfyt__reaua.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        weai__puyw = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        babcd__haf = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        pxp__wcyp = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        ajwt__wpqr = cgutils.get_or_insert_function(c.builder.module,
            pxp__wcyp, name='np_array_from_array_item_array')
        arr = c.builder.call(ajwt__wpqr, [wfyt__reaua.n_arrays, c.builder.
            bitcast(babcd__haf, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), weai__puyw)])
    else:
        arr = _box_array_item_array_generic(typ, c, wfyt__reaua.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    lfc__saz, csfy__gmvzx, xdh__qyfsy = args
    cvior__lwck = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    hxz__xliao = sig.args[1]
    if not isinstance(hxz__xliao, types.UniTuple):
        csfy__gmvzx = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), -1) for xdh__qyfsy in range(cvior__lwck)])
    elif hxz__xliao.count < cvior__lwck:
        csfy__gmvzx = cgutils.pack_array(builder, [builder.extract_value(
            csfy__gmvzx, nsvd__fjvp) for nsvd__fjvp in range(hxz__xliao.
            count)] + [lir.Constant(lir.IntType(64), -1) for xdh__qyfsy in
            range(cvior__lwck - hxz__xliao.count)])
    gzsq__akz, xdh__qyfsy, xdh__qyfsy, xdh__qyfsy = construct_array_item_array(
        context, builder, array_item_type, lfc__saz, csfy__gmvzx)
    aiu__uigx = context.make_helper(builder, array_item_type)
    aiu__uigx.meminfo = gzsq__akz
    return aiu__uigx._getvalue()


@intrinsic
def pre_alloc_array_item_array(typingctx, num_arrs_typ, num_values_typ,
    dtype_typ=None):
    assert isinstance(num_arrs_typ, types.Integer)
    array_item_type = ArrayItemArrayType(dtype_typ.instance_type)
    num_values_typ = types.unliteral(num_values_typ)
    return array_item_type(types.int64, num_values_typ, dtype_typ
        ), lower_pre_alloc_array_item_array


def pre_alloc_array_item_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_array_item_arr_ext_pre_alloc_array_item_array
    ) = pre_alloc_array_item_array_equiv


def init_array_item_array_codegen(context, builder, signature, args):
    n_arrays, bsob__fpoyj, wze__zzf, ybbh__izlbw = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    avbud__nar = context.get_value_type(payload_type)
    mmm__tzn = context.get_abi_sizeof(avbud__nar)
    ufcsa__qopb = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    gzsq__akz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, mmm__tzn), ufcsa__qopb)
    evnus__tkx = context.nrt.meminfo_data(builder, gzsq__akz)
    vbcol__mwrf = builder.bitcast(evnus__tkx, avbud__nar.as_pointer())
    wfyt__reaua = cgutils.create_struct_proxy(payload_type)(context, builder)
    wfyt__reaua.n_arrays = n_arrays
    wfyt__reaua.data = bsob__fpoyj
    wfyt__reaua.offsets = wze__zzf
    wfyt__reaua.null_bitmap = ybbh__izlbw
    builder.store(wfyt__reaua._getvalue(), vbcol__mwrf)
    context.nrt.incref(builder, signature.args[1], bsob__fpoyj)
    context.nrt.incref(builder, signature.args[2], wze__zzf)
    context.nrt.incref(builder, signature.args[3], ybbh__izlbw)
    aiu__uigx = context.make_helper(builder, array_item_type)
    aiu__uigx.meminfo = gzsq__akz
    return aiu__uigx._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    lkry__lctoh = ArrayItemArrayType(data_type)
    sig = lkry__lctoh(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        wfyt__reaua = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            wfyt__reaua.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        wfyt__reaua = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        babcd__haf = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, wfyt__reaua.offsets).data
        wze__zzf = builder.bitcast(babcd__haf, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(wze__zzf, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        wfyt__reaua = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            wfyt__reaua.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        wfyt__reaua = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            wfyt__reaua.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


def alias_ext_single_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_offsets',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_data',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_null_bitmap',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array


@intrinsic
def get_n_arrays(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        wfyt__reaua = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return wfyt__reaua.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, wksyf__lopiu = args
        aiu__uigx = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        evnus__tkx = context.nrt.meminfo_data(builder, aiu__uigx.meminfo)
        vbcol__mwrf = builder.bitcast(evnus__tkx, context.get_value_type(
            payload_type).as_pointer())
        wfyt__reaua = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(vbcol__mwrf))
        context.nrt.decref(builder, data_typ, wfyt__reaua.data)
        wfyt__reaua.data = wksyf__lopiu
        context.nrt.incref(builder, data_typ, wksyf__lopiu)
        builder.store(wfyt__reaua._getvalue(), vbcol__mwrf)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    bsob__fpoyj = get_data(arr)
    bcmmd__dtjeq = len(bsob__fpoyj)
    if bcmmd__dtjeq < new_size:
        mkw__lpfn = max(2 * bcmmd__dtjeq, new_size)
        wksyf__lopiu = bodo.libs.array_kernels.resize_and_copy(bsob__fpoyj,
            old_size, mkw__lpfn)
        replace_data_arr(arr, wksyf__lopiu)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    bsob__fpoyj = get_data(arr)
    wze__zzf = get_offsets(arr)
    umwh__pdl = len(bsob__fpoyj)
    chkcm__bzpei = wze__zzf[-1]
    if umwh__pdl != chkcm__bzpei:
        wksyf__lopiu = bodo.libs.array_kernels.resize_and_copy(bsob__fpoyj,
            chkcm__bzpei, chkcm__bzpei)
        replace_data_arr(arr, wksyf__lopiu)


@overload(len, no_unliteral=True)
def overload_array_item_arr_len(A):
    if isinstance(A, ArrayItemArrayType):
        return lambda A: get_n_arrays(A)


@overload_attribute(ArrayItemArrayType, 'shape')
def overload_array_item_arr_shape(A):
    return lambda A: (get_n_arrays(A),)


@overload_attribute(ArrayItemArrayType, 'dtype')
def overload_array_item_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(ArrayItemArrayType, 'ndim')
def overload_array_item_arr_ndim(A):
    return lambda A: 1


@overload_attribute(ArrayItemArrayType, 'nbytes')
def overload_array_item_arr_nbytes(A):
    return lambda A: get_data(A).nbytes + get_offsets(A
        ).nbytes + get_null_bitmap(A).nbytes


@overload(operator.getitem, no_unliteral=True)
def array_item_arr_getitem_array(arr, ind):
    if not isinstance(arr, ArrayItemArrayType):
        return
    if isinstance(ind, types.Integer):

        def array_item_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            wze__zzf = get_offsets(arr)
            bsob__fpoyj = get_data(arr)
            ohbm__xcogs = wze__zzf[ind]
            beghg__sbix = wze__zzf[ind + 1]
            return bsob__fpoyj[ohbm__xcogs:beghg__sbix]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        xxs__bfag = arr.dtype

        def impl_bool(arr, ind):
            ltt__pjj = len(arr)
            if ltt__pjj != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ybbh__izlbw = get_null_bitmap(arr)
            n_arrays = 0
            wkjs__pviay = init_nested_counts(xxs__bfag)
            for nsvd__fjvp in range(ltt__pjj):
                if ind[nsvd__fjvp]:
                    n_arrays += 1
                    kmi__sfik = arr[nsvd__fjvp]
                    wkjs__pviay = add_nested_counts(wkjs__pviay, kmi__sfik)
            ifs__tqdl = pre_alloc_array_item_array(n_arrays, wkjs__pviay,
                xxs__bfag)
            nqwa__gehl = get_null_bitmap(ifs__tqdl)
            plxz__usxf = 0
            for fbneb__spgx in range(ltt__pjj):
                if ind[fbneb__spgx]:
                    ifs__tqdl[plxz__usxf] = arr[fbneb__spgx]
                    fbxk__dfgqo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ybbh__izlbw, fbneb__spgx)
                    bodo.libs.int_arr_ext.set_bit_to_arr(nqwa__gehl,
                        plxz__usxf, fbxk__dfgqo)
                    plxz__usxf += 1
            return ifs__tqdl
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        xxs__bfag = arr.dtype

        def impl_int(arr, ind):
            ybbh__izlbw = get_null_bitmap(arr)
            ltt__pjj = len(ind)
            n_arrays = ltt__pjj
            wkjs__pviay = init_nested_counts(xxs__bfag)
            for kze__dwwgd in range(ltt__pjj):
                nsvd__fjvp = ind[kze__dwwgd]
                kmi__sfik = arr[nsvd__fjvp]
                wkjs__pviay = add_nested_counts(wkjs__pviay, kmi__sfik)
            ifs__tqdl = pre_alloc_array_item_array(n_arrays, wkjs__pviay,
                xxs__bfag)
            nqwa__gehl = get_null_bitmap(ifs__tqdl)
            for qobk__idhgm in range(ltt__pjj):
                fbneb__spgx = ind[qobk__idhgm]
                ifs__tqdl[qobk__idhgm] = arr[fbneb__spgx]
                fbxk__dfgqo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    ybbh__izlbw, fbneb__spgx)
                bodo.libs.int_arr_ext.set_bit_to_arr(nqwa__gehl,
                    qobk__idhgm, fbxk__dfgqo)
            return ifs__tqdl
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            ltt__pjj = len(arr)
            clss__mkxg = numba.cpython.unicode._normalize_slice(ind, ltt__pjj)
            vaca__ayjgi = np.arange(clss__mkxg.start, clss__mkxg.stop,
                clss__mkxg.step)
            return arr[vaca__ayjgi]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            wze__zzf = get_offsets(A)
            ybbh__izlbw = get_null_bitmap(A)
            if idx == 0:
                wze__zzf[0] = 0
            n_items = len(val)
            gnpme__cjgbc = wze__zzf[idx] + n_items
            ensure_data_capacity(A, wze__zzf[idx], gnpme__cjgbc)
            bsob__fpoyj = get_data(A)
            wze__zzf[idx + 1] = wze__zzf[idx] + n_items
            bsob__fpoyj[wze__zzf[idx]:wze__zzf[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(ybbh__izlbw, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            clss__mkxg = numba.cpython.unicode._normalize_slice(idx, len(A))
            for nsvd__fjvp in range(clss__mkxg.start, clss__mkxg.stop,
                clss__mkxg.step):
                A[nsvd__fjvp] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            wze__zzf = get_offsets(A)
            ybbh__izlbw = get_null_bitmap(A)
            yiv__vjou = get_offsets(val)
            lsvjl__uxj = get_data(val)
            wfmlq__yhucb = get_null_bitmap(val)
            ltt__pjj = len(A)
            clss__mkxg = numba.cpython.unicode._normalize_slice(idx, ltt__pjj)
            hgyfx__jtc, zmvp__evr = clss__mkxg.start, clss__mkxg.stop
            assert clss__mkxg.step == 1
            if hgyfx__jtc == 0:
                wze__zzf[hgyfx__jtc] = 0
            cvlzm__aryt = wze__zzf[hgyfx__jtc]
            gnpme__cjgbc = cvlzm__aryt + len(lsvjl__uxj)
            ensure_data_capacity(A, cvlzm__aryt, gnpme__cjgbc)
            bsob__fpoyj = get_data(A)
            bsob__fpoyj[cvlzm__aryt:cvlzm__aryt + len(lsvjl__uxj)] = lsvjl__uxj
            wze__zzf[hgyfx__jtc:zmvp__evr + 1] = yiv__vjou + cvlzm__aryt
            rwc__xvufl = 0
            for nsvd__fjvp in range(hgyfx__jtc, zmvp__evr):
                fbxk__dfgqo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    wfmlq__yhucb, rwc__xvufl)
                bodo.libs.int_arr_ext.set_bit_to_arr(ybbh__izlbw,
                    nsvd__fjvp, fbxk__dfgqo)
                rwc__xvufl += 1
        return impl_slice
    raise BodoError(
        'only setitem with scalar index is currently supported for list arrays'
        )


@overload_method(ArrayItemArrayType, 'copy', no_unliteral=True)
def overload_array_item_arr_copy(A):

    def copy_impl(A):
        return init_array_item_array(len(A), get_data(A).copy(),
            get_offsets(A).copy(), get_null_bitmap(A).copy())
    return copy_impl
