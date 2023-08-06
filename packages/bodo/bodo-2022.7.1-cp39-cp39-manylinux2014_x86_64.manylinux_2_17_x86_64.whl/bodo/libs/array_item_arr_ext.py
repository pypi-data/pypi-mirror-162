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
        mdi__bcqco = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, mdi__bcqco)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        mdi__bcqco = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, mdi__bcqco)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    rowbj__pwjeg = builder.module
    pmxzd__tkn = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    eukm__pegi = cgutils.get_or_insert_function(rowbj__pwjeg, pmxzd__tkn,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not eukm__pegi.is_declaration:
        return eukm__pegi
    eukm__pegi.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(eukm__pegi.append_basic_block())
    xski__ucr = eukm__pegi.args[0]
    qrjfl__qtlsm = context.get_value_type(payload_type).as_pointer()
    gksux__qjve = builder.bitcast(xski__ucr, qrjfl__qtlsm)
    xeg__ony = context.make_helper(builder, payload_type, ref=gksux__qjve)
    context.nrt.decref(builder, array_item_type.dtype, xeg__ony.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'), xeg__ony.
        offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), xeg__ony.
        null_bitmap)
    builder.ret_void()
    return eukm__pegi


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    jdijq__idy = context.get_value_type(payload_type)
    pbmse__lkgsv = context.get_abi_sizeof(jdijq__idy)
    qdb__nzwqd = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    powk__bfib = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, pbmse__lkgsv), qdb__nzwqd)
    ciky__lkdcs = context.nrt.meminfo_data(builder, powk__bfib)
    xppbn__wuak = builder.bitcast(ciky__lkdcs, jdijq__idy.as_pointer())
    xeg__ony = cgutils.create_struct_proxy(payload_type)(context, builder)
    xeg__ony.n_arrays = n_arrays
    bsiwd__keui = n_elems.type.count
    lzbul__daqp = builder.extract_value(n_elems, 0)
    rvk__nnqjy = cgutils.alloca_once_value(builder, lzbul__daqp)
    mrdy__dcnv = builder.icmp_signed('==', lzbul__daqp, lir.Constant(
        lzbul__daqp.type, -1))
    with builder.if_then(mrdy__dcnv):
        builder.store(n_arrays, rvk__nnqjy)
    n_elems = cgutils.pack_array(builder, [builder.load(rvk__nnqjy)] + [
        builder.extract_value(n_elems, wyxu__xjf) for wyxu__xjf in range(1,
        bsiwd__keui)])
    xeg__ony.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    nswe__yemo = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    wjwq__aqzi = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [nswe__yemo])
    offsets_ptr = wjwq__aqzi.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    xeg__ony.offsets = wjwq__aqzi._getvalue()
    ygng__oeoj = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    dxqy__vsa = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [ygng__oeoj])
    null_bitmap_ptr = dxqy__vsa.data
    xeg__ony.null_bitmap = dxqy__vsa._getvalue()
    builder.store(xeg__ony._getvalue(), xppbn__wuak)
    return powk__bfib, xeg__ony.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    smwuh__kihn, zgd__djpc = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    jll__vzmi = context.insert_const_string(builder.module, 'pandas')
    wpqwx__pdadg = c.pyapi.import_module_noblock(jll__vzmi)
    ygyws__gzbjf = c.pyapi.object_getattr_string(wpqwx__pdadg, 'NA')
    knlv__egow = c.context.get_constant(offset_type, 0)
    builder.store(knlv__egow, offsets_ptr)
    sens__onh = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as qafhg__iits:
        lkmjs__isrr = qafhg__iits.index
        item_ind = builder.load(sens__onh)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [lkmjs__isrr]))
        arr_obj = seq_getitem(builder, context, val, lkmjs__isrr)
        set_bitmap_bit(builder, null_bitmap_ptr, lkmjs__isrr, 0)
        kdr__xumco = is_na_value(builder, context, arr_obj, ygyws__gzbjf)
        zltlq__pkm = builder.icmp_unsigned('!=', kdr__xumco, lir.Constant(
            kdr__xumco.type, 1))
        with builder.if_then(zltlq__pkm):
            set_bitmap_bit(builder, null_bitmap_ptr, lkmjs__isrr, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), sens__onh)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(sens__onh), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(wpqwx__pdadg)
    c.pyapi.decref(ygyws__gzbjf)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    wvu__mczbm = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if wvu__mczbm:
        pmxzd__tkn = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        zhlk__nxhx = cgutils.get_or_insert_function(c.builder.module,
            pmxzd__tkn, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(zhlk__nxhx,
            [val])])
    else:
        cwmci__gxc = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            cwmci__gxc, wyxu__xjf) for wyxu__xjf in range(1, cwmci__gxc.
            type.count)])
    powk__bfib, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if wvu__mczbm:
        kmffj__kcd = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        llelx__demy = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        pmxzd__tkn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        eukm__pegi = cgutils.get_or_insert_function(c.builder.module,
            pmxzd__tkn, name='array_item_array_from_sequence')
        c.builder.call(eukm__pegi, [val, c.builder.bitcast(llelx__demy, lir
            .IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), kmffj__kcd)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    nyslq__bcrqg = c.context.make_helper(c.builder, typ)
    nyslq__bcrqg.meminfo = powk__bfib
    lewli__ihlba = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(nyslq__bcrqg._getvalue(), is_error=lewli__ihlba)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    nyslq__bcrqg = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    ciky__lkdcs = context.nrt.meminfo_data(builder, nyslq__bcrqg.meminfo)
    xppbn__wuak = builder.bitcast(ciky__lkdcs, context.get_value_type(
        payload_type).as_pointer())
    xeg__ony = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(xppbn__wuak))
    return xeg__ony


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    jll__vzmi = context.insert_const_string(builder.module, 'numpy')
    qfcg__ngaq = c.pyapi.import_module_noblock(jll__vzmi)
    uygf__iojls = c.pyapi.object_getattr_string(qfcg__ngaq, 'object_')
    kttt__pkheo = c.pyapi.long_from_longlong(n_arrays)
    ecvsi__djlph = c.pyapi.call_method(qfcg__ngaq, 'ndarray', (kttt__pkheo,
        uygf__iojls))
    pmvy__eea = c.pyapi.object_getattr_string(qfcg__ngaq, 'nan')
    sens__onh = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (64), 0))
    with cgutils.for_range(builder, n_arrays) as qafhg__iits:
        lkmjs__isrr = qafhg__iits.index
        pyarray_setitem(builder, context, ecvsi__djlph, lkmjs__isrr, pmvy__eea)
        lij__cses = get_bitmap_bit(builder, null_bitmap_ptr, lkmjs__isrr)
        dwl__tzlz = builder.icmp_unsigned('!=', lij__cses, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(dwl__tzlz):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(lkmjs__isrr, lir.Constant(
                lkmjs__isrr.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [lkmjs__isrr]))), lir.IntType(64))
            item_ind = builder.load(sens__onh)
            smwuh__kihn, uqnv__lmesb = c.pyapi.call_jit_code(lambda
                data_arr, item_ind, n_items: data_arr[item_ind:item_ind +
                n_items], typ.dtype(typ.dtype, types.int64, types.int64), [
                data_arr, item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), sens__onh)
            arr_obj = c.pyapi.from_native_value(typ.dtype, uqnv__lmesb, c.
                env_manager)
            pyarray_setitem(builder, context, ecvsi__djlph, lkmjs__isrr,
                arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(qfcg__ngaq)
    c.pyapi.decref(uygf__iojls)
    c.pyapi.decref(kttt__pkheo)
    c.pyapi.decref(pmvy__eea)
    return ecvsi__djlph


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    xeg__ony = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = xeg__ony.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), xeg__ony.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), xeg__ony.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        kmffj__kcd = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        llelx__demy = c.context.make_helper(c.builder, typ.dtype, data_arr
            ).data
        pmxzd__tkn = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        icbz__afd = cgutils.get_or_insert_function(c.builder.module,
            pmxzd__tkn, name='np_array_from_array_item_array')
        arr = c.builder.call(icbz__afd, [xeg__ony.n_arrays, c.builder.
            bitcast(llelx__demy, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), kmffj__kcd)])
    else:
        arr = _box_array_item_array_generic(typ, c, xeg__ony.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    gzj__pggl, vsawd__zjz, wju__vysk = args
    xond__zwlva = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    rnelq__klxz = sig.args[1]
    if not isinstance(rnelq__klxz, types.UniTuple):
        vsawd__zjz = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for wju__vysk in range(xond__zwlva)])
    elif rnelq__klxz.count < xond__zwlva:
        vsawd__zjz = cgutils.pack_array(builder, [builder.extract_value(
            vsawd__zjz, wyxu__xjf) for wyxu__xjf in range(rnelq__klxz.count
            )] + [lir.Constant(lir.IntType(64), -1) for wju__vysk in range(
            xond__zwlva - rnelq__klxz.count)])
    powk__bfib, wju__vysk, wju__vysk, wju__vysk = construct_array_item_array(
        context, builder, array_item_type, gzj__pggl, vsawd__zjz)
    nyslq__bcrqg = context.make_helper(builder, array_item_type)
    nyslq__bcrqg.meminfo = powk__bfib
    return nyslq__bcrqg._getvalue()


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
    n_arrays, tks__tbrbx, wjwq__aqzi, dxqy__vsa = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    jdijq__idy = context.get_value_type(payload_type)
    pbmse__lkgsv = context.get_abi_sizeof(jdijq__idy)
    qdb__nzwqd = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    powk__bfib = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, pbmse__lkgsv), qdb__nzwqd)
    ciky__lkdcs = context.nrt.meminfo_data(builder, powk__bfib)
    xppbn__wuak = builder.bitcast(ciky__lkdcs, jdijq__idy.as_pointer())
    xeg__ony = cgutils.create_struct_proxy(payload_type)(context, builder)
    xeg__ony.n_arrays = n_arrays
    xeg__ony.data = tks__tbrbx
    xeg__ony.offsets = wjwq__aqzi
    xeg__ony.null_bitmap = dxqy__vsa
    builder.store(xeg__ony._getvalue(), xppbn__wuak)
    context.nrt.incref(builder, signature.args[1], tks__tbrbx)
    context.nrt.incref(builder, signature.args[2], wjwq__aqzi)
    context.nrt.incref(builder, signature.args[3], dxqy__vsa)
    nyslq__bcrqg = context.make_helper(builder, array_item_type)
    nyslq__bcrqg.meminfo = powk__bfib
    return nyslq__bcrqg._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    agdyn__inis = ArrayItemArrayType(data_type)
    sig = agdyn__inis(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        xeg__ony = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            xeg__ony.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        xeg__ony = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        llelx__demy = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, xeg__ony.offsets).data
        wjwq__aqzi = builder.bitcast(llelx__demy, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(wjwq__aqzi, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        xeg__ony = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            xeg__ony.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        xeg__ony = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            xeg__ony.null_bitmap)
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
        xeg__ony = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return xeg__ony.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, nfo__itj = args
        nyslq__bcrqg = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        ciky__lkdcs = context.nrt.meminfo_data(builder, nyslq__bcrqg.meminfo)
        xppbn__wuak = builder.bitcast(ciky__lkdcs, context.get_value_type(
            payload_type).as_pointer())
        xeg__ony = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(xppbn__wuak))
        context.nrt.decref(builder, data_typ, xeg__ony.data)
        xeg__ony.data = nfo__itj
        context.nrt.incref(builder, data_typ, nfo__itj)
        builder.store(xeg__ony._getvalue(), xppbn__wuak)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    tks__tbrbx = get_data(arr)
    xban__lrhja = len(tks__tbrbx)
    if xban__lrhja < new_size:
        tvxu__lcodb = max(2 * xban__lrhja, new_size)
        nfo__itj = bodo.libs.array_kernels.resize_and_copy(tks__tbrbx,
            old_size, tvxu__lcodb)
        replace_data_arr(arr, nfo__itj)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    tks__tbrbx = get_data(arr)
    wjwq__aqzi = get_offsets(arr)
    jgbzt__qbih = len(tks__tbrbx)
    lhqih__svll = wjwq__aqzi[-1]
    if jgbzt__qbih != lhqih__svll:
        nfo__itj = bodo.libs.array_kernels.resize_and_copy(tks__tbrbx,
            lhqih__svll, lhqih__svll)
        replace_data_arr(arr, nfo__itj)


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
            wjwq__aqzi = get_offsets(arr)
            tks__tbrbx = get_data(arr)
            qcnna__lmtv = wjwq__aqzi[ind]
            ains__opgb = wjwq__aqzi[ind + 1]
            return tks__tbrbx[qcnna__lmtv:ains__opgb]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        duwh__onheo = arr.dtype

        def impl_bool(arr, ind):
            bcgwb__sqhos = len(arr)
            if bcgwb__sqhos != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            dxqy__vsa = get_null_bitmap(arr)
            n_arrays = 0
            sdhar__rcvmy = init_nested_counts(duwh__onheo)
            for wyxu__xjf in range(bcgwb__sqhos):
                if ind[wyxu__xjf]:
                    n_arrays += 1
                    zas__shvv = arr[wyxu__xjf]
                    sdhar__rcvmy = add_nested_counts(sdhar__rcvmy, zas__shvv)
            ecvsi__djlph = pre_alloc_array_item_array(n_arrays,
                sdhar__rcvmy, duwh__onheo)
            yhg__wvhv = get_null_bitmap(ecvsi__djlph)
            wxuxx__slz = 0
            for fbila__onxk in range(bcgwb__sqhos):
                if ind[fbila__onxk]:
                    ecvsi__djlph[wxuxx__slz] = arr[fbila__onxk]
                    kkvqn__aipu = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        dxqy__vsa, fbila__onxk)
                    bodo.libs.int_arr_ext.set_bit_to_arr(yhg__wvhv,
                        wxuxx__slz, kkvqn__aipu)
                    wxuxx__slz += 1
            return ecvsi__djlph
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        duwh__onheo = arr.dtype

        def impl_int(arr, ind):
            dxqy__vsa = get_null_bitmap(arr)
            bcgwb__sqhos = len(ind)
            n_arrays = bcgwb__sqhos
            sdhar__rcvmy = init_nested_counts(duwh__onheo)
            for cevbo__uqhx in range(bcgwb__sqhos):
                wyxu__xjf = ind[cevbo__uqhx]
                zas__shvv = arr[wyxu__xjf]
                sdhar__rcvmy = add_nested_counts(sdhar__rcvmy, zas__shvv)
            ecvsi__djlph = pre_alloc_array_item_array(n_arrays,
                sdhar__rcvmy, duwh__onheo)
            yhg__wvhv = get_null_bitmap(ecvsi__djlph)
            for keynv__ngjxo in range(bcgwb__sqhos):
                fbila__onxk = ind[keynv__ngjxo]
                ecvsi__djlph[keynv__ngjxo] = arr[fbila__onxk]
                kkvqn__aipu = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    dxqy__vsa, fbila__onxk)
                bodo.libs.int_arr_ext.set_bit_to_arr(yhg__wvhv,
                    keynv__ngjxo, kkvqn__aipu)
            return ecvsi__djlph
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            bcgwb__sqhos = len(arr)
            anwj__jgpp = numba.cpython.unicode._normalize_slice(ind,
                bcgwb__sqhos)
            eknmo__raw = np.arange(anwj__jgpp.start, anwj__jgpp.stop,
                anwj__jgpp.step)
            return arr[eknmo__raw]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            wjwq__aqzi = get_offsets(A)
            dxqy__vsa = get_null_bitmap(A)
            if idx == 0:
                wjwq__aqzi[0] = 0
            n_items = len(val)
            qkkx__kcqab = wjwq__aqzi[idx] + n_items
            ensure_data_capacity(A, wjwq__aqzi[idx], qkkx__kcqab)
            tks__tbrbx = get_data(A)
            wjwq__aqzi[idx + 1] = wjwq__aqzi[idx] + n_items
            tks__tbrbx[wjwq__aqzi[idx]:wjwq__aqzi[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(dxqy__vsa, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            anwj__jgpp = numba.cpython.unicode._normalize_slice(idx, len(A))
            for wyxu__xjf in range(anwj__jgpp.start, anwj__jgpp.stop,
                anwj__jgpp.step):
                A[wyxu__xjf] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            wjwq__aqzi = get_offsets(A)
            dxqy__vsa = get_null_bitmap(A)
            qkhy__lirh = get_offsets(val)
            uacr__fad = get_data(val)
            cie__yutzc = get_null_bitmap(val)
            bcgwb__sqhos = len(A)
            anwj__jgpp = numba.cpython.unicode._normalize_slice(idx,
                bcgwb__sqhos)
            klghw__zwa, pio__exns = anwj__jgpp.start, anwj__jgpp.stop
            assert anwj__jgpp.step == 1
            if klghw__zwa == 0:
                wjwq__aqzi[klghw__zwa] = 0
            yllg__vma = wjwq__aqzi[klghw__zwa]
            qkkx__kcqab = yllg__vma + len(uacr__fad)
            ensure_data_capacity(A, yllg__vma, qkkx__kcqab)
            tks__tbrbx = get_data(A)
            tks__tbrbx[yllg__vma:yllg__vma + len(uacr__fad)] = uacr__fad
            wjwq__aqzi[klghw__zwa:pio__exns + 1] = qkhy__lirh + yllg__vma
            kmmx__zfbqt = 0
            for wyxu__xjf in range(klghw__zwa, pio__exns):
                kkvqn__aipu = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    cie__yutzc, kmmx__zfbqt)
                bodo.libs.int_arr_ext.set_bit_to_arr(dxqy__vsa, wyxu__xjf,
                    kkvqn__aipu)
                kmmx__zfbqt += 1
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
