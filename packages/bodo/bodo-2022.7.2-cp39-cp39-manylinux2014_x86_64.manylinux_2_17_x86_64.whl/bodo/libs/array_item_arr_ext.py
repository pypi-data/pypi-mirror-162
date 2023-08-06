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
        jlc__iplr = [('n_arrays', types.int64), ('data', fe_type.array_type
            .dtype), ('offsets', types.Array(offset_type, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, jlc__iplr)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        jlc__iplr = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, jlc__iplr)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    znmsd__kdeh = builder.module
    uzxw__kvo = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    spta__usta = cgutils.get_or_insert_function(znmsd__kdeh, uzxw__kvo,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not spta__usta.is_declaration:
        return spta__usta
    spta__usta.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(spta__usta.append_basic_block())
    qrjm__nztkv = spta__usta.args[0]
    eihfs__opqz = context.get_value_type(payload_type).as_pointer()
    gxj__tfc = builder.bitcast(qrjm__nztkv, eihfs__opqz)
    ocbh__abcpl = context.make_helper(builder, payload_type, ref=gxj__tfc)
    context.nrt.decref(builder, array_item_type.dtype, ocbh__abcpl.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        ocbh__abcpl.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        ocbh__abcpl.null_bitmap)
    builder.ret_void()
    return spta__usta


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    wjhj__xqk = context.get_value_type(payload_type)
    llujy__mur = context.get_abi_sizeof(wjhj__xqk)
    qeid__tpre = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    sovg__forn = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, llujy__mur), qeid__tpre)
    vkzjf__ufnt = context.nrt.meminfo_data(builder, sovg__forn)
    ivx__qbcet = builder.bitcast(vkzjf__ufnt, wjhj__xqk.as_pointer())
    ocbh__abcpl = cgutils.create_struct_proxy(payload_type)(context, builder)
    ocbh__abcpl.n_arrays = n_arrays
    lcnk__hvwah = n_elems.type.count
    opnon__ugz = builder.extract_value(n_elems, 0)
    ner__izct = cgutils.alloca_once_value(builder, opnon__ugz)
    trdl__jqnv = builder.icmp_signed('==', opnon__ugz, lir.Constant(
        opnon__ugz.type, -1))
    with builder.if_then(trdl__jqnv):
        builder.store(n_arrays, ner__izct)
    n_elems = cgutils.pack_array(builder, [builder.load(ner__izct)] + [
        builder.extract_value(n_elems, fpsyb__esxo) for fpsyb__esxo in
        range(1, lcnk__hvwah)])
    ocbh__abcpl.data = gen_allocate_array(context, builder, array_item_type
        .dtype, n_elems, c)
    nhvp__nrue = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    bohl__ferpz = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [nhvp__nrue])
    offsets_ptr = bohl__ferpz.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    ocbh__abcpl.offsets = bohl__ferpz._getvalue()
    dwgz__mcpj = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    zaj__uij = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [dwgz__mcpj])
    null_bitmap_ptr = zaj__uij.data
    ocbh__abcpl.null_bitmap = zaj__uij._getvalue()
    builder.store(ocbh__abcpl._getvalue(), ivx__qbcet)
    return sovg__forn, ocbh__abcpl.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    jkwup__iid, dunx__lvim = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    cen__sjh = context.insert_const_string(builder.module, 'pandas')
    flm__ddi = c.pyapi.import_module_noblock(cen__sjh)
    ojhxf__sntp = c.pyapi.object_getattr_string(flm__ddi, 'NA')
    nak__oxjn = c.context.get_constant(offset_type, 0)
    builder.store(nak__oxjn, offsets_ptr)
    kyu__jhcp = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as hfw__endzf:
        nlm__cfhsv = hfw__endzf.index
        item_ind = builder.load(kyu__jhcp)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [nlm__cfhsv]))
        arr_obj = seq_getitem(builder, context, val, nlm__cfhsv)
        set_bitmap_bit(builder, null_bitmap_ptr, nlm__cfhsv, 0)
        boig__waram = is_na_value(builder, context, arr_obj, ojhxf__sntp)
        econw__vmgs = builder.icmp_unsigned('!=', boig__waram, lir.Constant
            (boig__waram.type, 1))
        with builder.if_then(econw__vmgs):
            set_bitmap_bit(builder, null_bitmap_ptr, nlm__cfhsv, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), kyu__jhcp)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(kyu__jhcp), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(flm__ddi)
    c.pyapi.decref(ojhxf__sntp)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    liaru__mrp = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if liaru__mrp:
        uzxw__kvo = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        vkueh__axlom = cgutils.get_or_insert_function(c.builder.module,
            uzxw__kvo, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(
            vkueh__axlom, [val])])
    else:
        gjz__mvwxh = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            gjz__mvwxh, fpsyb__esxo) for fpsyb__esxo in range(1, gjz__mvwxh
            .type.count)])
    sovg__forn, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if liaru__mrp:
        kzqp__jhisk = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        ttb__mqxw = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        uzxw__kvo = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        spta__usta = cgutils.get_or_insert_function(c.builder.module,
            uzxw__kvo, name='array_item_array_from_sequence')
        c.builder.call(spta__usta, [val, c.builder.bitcast(ttb__mqxw, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), kzqp__jhisk)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    sxm__wyh = c.context.make_helper(c.builder, typ)
    sxm__wyh.meminfo = sovg__forn
    xqgp__afj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(sxm__wyh._getvalue(), is_error=xqgp__afj)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    sxm__wyh = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    vkzjf__ufnt = context.nrt.meminfo_data(builder, sxm__wyh.meminfo)
    ivx__qbcet = builder.bitcast(vkzjf__ufnt, context.get_value_type(
        payload_type).as_pointer())
    ocbh__abcpl = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(ivx__qbcet))
    return ocbh__abcpl


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    cen__sjh = context.insert_const_string(builder.module, 'numpy')
    brrgb__zmcg = c.pyapi.import_module_noblock(cen__sjh)
    cukj__tkpk = c.pyapi.object_getattr_string(brrgb__zmcg, 'object_')
    olsu__umb = c.pyapi.long_from_longlong(n_arrays)
    dep__yajq = c.pyapi.call_method(brrgb__zmcg, 'ndarray', (olsu__umb,
        cukj__tkpk))
    sshtr__vxvb = c.pyapi.object_getattr_string(brrgb__zmcg, 'nan')
    kyu__jhcp = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (64), 0))
    with cgutils.for_range(builder, n_arrays) as hfw__endzf:
        nlm__cfhsv = hfw__endzf.index
        pyarray_setitem(builder, context, dep__yajq, nlm__cfhsv, sshtr__vxvb)
        unwzo__gyeqj = get_bitmap_bit(builder, null_bitmap_ptr, nlm__cfhsv)
        mdmf__esfh = builder.icmp_unsigned('!=', unwzo__gyeqj, lir.Constant
            (lir.IntType(8), 0))
        with builder.if_then(mdmf__esfh):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(nlm__cfhsv, lir.Constant(
                nlm__cfhsv.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [nlm__cfhsv]))), lir.IntType(64))
            item_ind = builder.load(kyu__jhcp)
            jkwup__iid, vvd__izrq = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), kyu__jhcp)
            arr_obj = c.pyapi.from_native_value(typ.dtype, vvd__izrq, c.
                env_manager)
            pyarray_setitem(builder, context, dep__yajq, nlm__cfhsv, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(brrgb__zmcg)
    c.pyapi.decref(cukj__tkpk)
    c.pyapi.decref(olsu__umb)
    c.pyapi.decref(sshtr__vxvb)
    return dep__yajq


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    ocbh__abcpl = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = ocbh__abcpl.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), ocbh__abcpl.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), ocbh__abcpl.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        kzqp__jhisk = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        ttb__mqxw = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        uzxw__kvo = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        wort__zei = cgutils.get_or_insert_function(c.builder.module,
            uzxw__kvo, name='np_array_from_array_item_array')
        arr = c.builder.call(wort__zei, [ocbh__abcpl.n_arrays, c.builder.
            bitcast(ttb__mqxw, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), kzqp__jhisk)])
    else:
        arr = _box_array_item_array_generic(typ, c, ocbh__abcpl.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    kzl__huni, jxqyf__xgmwi, fuzr__idcrd = args
    vdcs__bigo = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    pqhav__lphgn = sig.args[1]
    if not isinstance(pqhav__lphgn, types.UniTuple):
        jxqyf__xgmwi = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for fuzr__idcrd in range(vdcs__bigo)])
    elif pqhav__lphgn.count < vdcs__bigo:
        jxqyf__xgmwi = cgutils.pack_array(builder, [builder.extract_value(
            jxqyf__xgmwi, fpsyb__esxo) for fpsyb__esxo in range(
            pqhav__lphgn.count)] + [lir.Constant(lir.IntType(64), -1) for
            fuzr__idcrd in range(vdcs__bigo - pqhav__lphgn.count)])
    sovg__forn, fuzr__idcrd, fuzr__idcrd, fuzr__idcrd = (
        construct_array_item_array(context, builder, array_item_type,
        kzl__huni, jxqyf__xgmwi))
    sxm__wyh = context.make_helper(builder, array_item_type)
    sxm__wyh.meminfo = sovg__forn
    return sxm__wyh._getvalue()


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
    n_arrays, vtwin__lcop, bohl__ferpz, zaj__uij = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    wjhj__xqk = context.get_value_type(payload_type)
    llujy__mur = context.get_abi_sizeof(wjhj__xqk)
    qeid__tpre = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    sovg__forn = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, llujy__mur), qeid__tpre)
    vkzjf__ufnt = context.nrt.meminfo_data(builder, sovg__forn)
    ivx__qbcet = builder.bitcast(vkzjf__ufnt, wjhj__xqk.as_pointer())
    ocbh__abcpl = cgutils.create_struct_proxy(payload_type)(context, builder)
    ocbh__abcpl.n_arrays = n_arrays
    ocbh__abcpl.data = vtwin__lcop
    ocbh__abcpl.offsets = bohl__ferpz
    ocbh__abcpl.null_bitmap = zaj__uij
    builder.store(ocbh__abcpl._getvalue(), ivx__qbcet)
    context.nrt.incref(builder, signature.args[1], vtwin__lcop)
    context.nrt.incref(builder, signature.args[2], bohl__ferpz)
    context.nrt.incref(builder, signature.args[3], zaj__uij)
    sxm__wyh = context.make_helper(builder, array_item_type)
    sxm__wyh.meminfo = sovg__forn
    return sxm__wyh._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    sxu__slww = ArrayItemArrayType(data_type)
    sig = sxu__slww(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ocbh__abcpl = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ocbh__abcpl.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        ocbh__abcpl = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        ttb__mqxw = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, ocbh__abcpl.offsets).data
        bohl__ferpz = builder.bitcast(ttb__mqxw, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(bohl__ferpz, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ocbh__abcpl = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ocbh__abcpl.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ocbh__abcpl = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ocbh__abcpl.null_bitmap)
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
        ocbh__abcpl = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return ocbh__abcpl.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, mygl__uevu = args
        sxm__wyh = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        vkzjf__ufnt = context.nrt.meminfo_data(builder, sxm__wyh.meminfo)
        ivx__qbcet = builder.bitcast(vkzjf__ufnt, context.get_value_type(
            payload_type).as_pointer())
        ocbh__abcpl = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(ivx__qbcet))
        context.nrt.decref(builder, data_typ, ocbh__abcpl.data)
        ocbh__abcpl.data = mygl__uevu
        context.nrt.incref(builder, data_typ, mygl__uevu)
        builder.store(ocbh__abcpl._getvalue(), ivx__qbcet)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    vtwin__lcop = get_data(arr)
    xcxp__jsa = len(vtwin__lcop)
    if xcxp__jsa < new_size:
        xdsx__gxvtv = max(2 * xcxp__jsa, new_size)
        mygl__uevu = bodo.libs.array_kernels.resize_and_copy(vtwin__lcop,
            old_size, xdsx__gxvtv)
        replace_data_arr(arr, mygl__uevu)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    vtwin__lcop = get_data(arr)
    bohl__ferpz = get_offsets(arr)
    glu__frrz = len(vtwin__lcop)
    zkm__xacs = bohl__ferpz[-1]
    if glu__frrz != zkm__xacs:
        mygl__uevu = bodo.libs.array_kernels.resize_and_copy(vtwin__lcop,
            zkm__xacs, zkm__xacs)
        replace_data_arr(arr, mygl__uevu)


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
            bohl__ferpz = get_offsets(arr)
            vtwin__lcop = get_data(arr)
            psa__ueew = bohl__ferpz[ind]
            inf__dfsev = bohl__ferpz[ind + 1]
            return vtwin__lcop[psa__ueew:inf__dfsev]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        cdzuc__dvst = arr.dtype

        def impl_bool(arr, ind):
            ebf__kvm = len(arr)
            if ebf__kvm != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            zaj__uij = get_null_bitmap(arr)
            n_arrays = 0
            jco__kmct = init_nested_counts(cdzuc__dvst)
            for fpsyb__esxo in range(ebf__kvm):
                if ind[fpsyb__esxo]:
                    n_arrays += 1
                    tal__xhp = arr[fpsyb__esxo]
                    jco__kmct = add_nested_counts(jco__kmct, tal__xhp)
            dep__yajq = pre_alloc_array_item_array(n_arrays, jco__kmct,
                cdzuc__dvst)
            qvo__tnid = get_null_bitmap(dep__yajq)
            qldrd__bxz = 0
            for raou__hkorf in range(ebf__kvm):
                if ind[raou__hkorf]:
                    dep__yajq[qldrd__bxz] = arr[raou__hkorf]
                    ebwti__oqd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        zaj__uij, raou__hkorf)
                    bodo.libs.int_arr_ext.set_bit_to_arr(qvo__tnid,
                        qldrd__bxz, ebwti__oqd)
                    qldrd__bxz += 1
            return dep__yajq
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        cdzuc__dvst = arr.dtype

        def impl_int(arr, ind):
            zaj__uij = get_null_bitmap(arr)
            ebf__kvm = len(ind)
            n_arrays = ebf__kvm
            jco__kmct = init_nested_counts(cdzuc__dvst)
            for mgvv__nkr in range(ebf__kvm):
                fpsyb__esxo = ind[mgvv__nkr]
                tal__xhp = arr[fpsyb__esxo]
                jco__kmct = add_nested_counts(jco__kmct, tal__xhp)
            dep__yajq = pre_alloc_array_item_array(n_arrays, jco__kmct,
                cdzuc__dvst)
            qvo__tnid = get_null_bitmap(dep__yajq)
            for kmvhc__rlfks in range(ebf__kvm):
                raou__hkorf = ind[kmvhc__rlfks]
                dep__yajq[kmvhc__rlfks] = arr[raou__hkorf]
                ebwti__oqd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(zaj__uij,
                    raou__hkorf)
                bodo.libs.int_arr_ext.set_bit_to_arr(qvo__tnid,
                    kmvhc__rlfks, ebwti__oqd)
            return dep__yajq
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            ebf__kvm = len(arr)
            vnvek__ugrl = numba.cpython.unicode._normalize_slice(ind, ebf__kvm)
            ruvmd__uca = np.arange(vnvek__ugrl.start, vnvek__ugrl.stop,
                vnvek__ugrl.step)
            return arr[ruvmd__uca]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            bohl__ferpz = get_offsets(A)
            zaj__uij = get_null_bitmap(A)
            if idx == 0:
                bohl__ferpz[0] = 0
            n_items = len(val)
            vlvm__thi = bohl__ferpz[idx] + n_items
            ensure_data_capacity(A, bohl__ferpz[idx], vlvm__thi)
            vtwin__lcop = get_data(A)
            bohl__ferpz[idx + 1] = bohl__ferpz[idx] + n_items
            vtwin__lcop[bohl__ferpz[idx]:bohl__ferpz[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(zaj__uij, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            vnvek__ugrl = numba.cpython.unicode._normalize_slice(idx, len(A))
            for fpsyb__esxo in range(vnvek__ugrl.start, vnvek__ugrl.stop,
                vnvek__ugrl.step):
                A[fpsyb__esxo] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            bohl__ferpz = get_offsets(A)
            zaj__uij = get_null_bitmap(A)
            umsfq__qokov = get_offsets(val)
            scmcg__poiby = get_data(val)
            ddz__ted = get_null_bitmap(val)
            ebf__kvm = len(A)
            vnvek__ugrl = numba.cpython.unicode._normalize_slice(idx, ebf__kvm)
            sfufg__pgrs, xvp__ktyk = vnvek__ugrl.start, vnvek__ugrl.stop
            assert vnvek__ugrl.step == 1
            if sfufg__pgrs == 0:
                bohl__ferpz[sfufg__pgrs] = 0
            ckrs__rprw = bohl__ferpz[sfufg__pgrs]
            vlvm__thi = ckrs__rprw + len(scmcg__poiby)
            ensure_data_capacity(A, ckrs__rprw, vlvm__thi)
            vtwin__lcop = get_data(A)
            vtwin__lcop[ckrs__rprw:ckrs__rprw + len(scmcg__poiby)
                ] = scmcg__poiby
            bohl__ferpz[sfufg__pgrs:xvp__ktyk + 1] = umsfq__qokov + ckrs__rprw
            kgm__pgor = 0
            for fpsyb__esxo in range(sfufg__pgrs, xvp__ktyk):
                ebwti__oqd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(ddz__ted,
                    kgm__pgor)
                bodo.libs.int_arr_ext.set_bit_to_arr(zaj__uij, fpsyb__esxo,
                    ebwti__oqd)
                kgm__pgor += 1
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
