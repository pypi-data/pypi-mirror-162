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
        bxwj__fynfy = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, bxwj__fynfy)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        bxwj__fynfy = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, bxwj__fynfy)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    xdxb__isdz = builder.module
    xzenq__gktg = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    vwdr__csjv = cgutils.get_or_insert_function(xdxb__isdz, xzenq__gktg,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not vwdr__csjv.is_declaration:
        return vwdr__csjv
    vwdr__csjv.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(vwdr__csjv.append_basic_block())
    lsqv__yemac = vwdr__csjv.args[0]
    fmmj__kvny = context.get_value_type(payload_type).as_pointer()
    mujjk__kfs = builder.bitcast(lsqv__yemac, fmmj__kvny)
    deah__kim = context.make_helper(builder, payload_type, ref=mujjk__kfs)
    context.nrt.decref(builder, array_item_type.dtype, deah__kim.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'), deah__kim
        .offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), deah__kim
        .null_bitmap)
    builder.ret_void()
    return vwdr__csjv


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    bqvo__embrj = context.get_value_type(payload_type)
    tcwa__tev = context.get_abi_sizeof(bqvo__embrj)
    ved__lbycy = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    iax__teaj = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tcwa__tev), ved__lbycy)
    glf__gatn = context.nrt.meminfo_data(builder, iax__teaj)
    guw__nttl = builder.bitcast(glf__gatn, bqvo__embrj.as_pointer())
    deah__kim = cgutils.create_struct_proxy(payload_type)(context, builder)
    deah__kim.n_arrays = n_arrays
    abu__zkty = n_elems.type.count
    byhwi__psox = builder.extract_value(n_elems, 0)
    pgtya__pqzbz = cgutils.alloca_once_value(builder, byhwi__psox)
    vte__cckoj = builder.icmp_signed('==', byhwi__psox, lir.Constant(
        byhwi__psox.type, -1))
    with builder.if_then(vte__cckoj):
        builder.store(n_arrays, pgtya__pqzbz)
    n_elems = cgutils.pack_array(builder, [builder.load(pgtya__pqzbz)] + [
        builder.extract_value(n_elems, tui__jpe) for tui__jpe in range(1,
        abu__zkty)])
    deah__kim.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    gvpqc__wbwf = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    auy__otp = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [gvpqc__wbwf])
    offsets_ptr = auy__otp.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    deah__kim.offsets = auy__otp._getvalue()
    weoj__rke = builder.udiv(builder.add(n_arrays, lir.Constant(lir.IntType
        (64), 7)), lir.Constant(lir.IntType(64), 8))
    dtaf__rcgyg = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [weoj__rke])
    null_bitmap_ptr = dtaf__rcgyg.data
    deah__kim.null_bitmap = dtaf__rcgyg._getvalue()
    builder.store(deah__kim._getvalue(), guw__nttl)
    return iax__teaj, deah__kim.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    ehn__uaw, tbbsw__sqsx = c.pyapi.call_jit_code(copy_data, sig, [data_arr,
        item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    lwbk__fqmk = context.insert_const_string(builder.module, 'pandas')
    yag__dlbok = c.pyapi.import_module_noblock(lwbk__fqmk)
    xtoo__ekdko = c.pyapi.object_getattr_string(yag__dlbok, 'NA')
    snrs__gpkts = c.context.get_constant(offset_type, 0)
    builder.store(snrs__gpkts, offsets_ptr)
    kpqm__qur = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as erat__zek:
        tytg__pbfv = erat__zek.index
        item_ind = builder.load(kpqm__qur)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [tytg__pbfv]))
        arr_obj = seq_getitem(builder, context, val, tytg__pbfv)
        set_bitmap_bit(builder, null_bitmap_ptr, tytg__pbfv, 0)
        xllgu__rqrjr = is_na_value(builder, context, arr_obj, xtoo__ekdko)
        rda__kkg = builder.icmp_unsigned('!=', xllgu__rqrjr, lir.Constant(
            xllgu__rqrjr.type, 1))
        with builder.if_then(rda__kkg):
            set_bitmap_bit(builder, null_bitmap_ptr, tytg__pbfv, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), kpqm__qur)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(kpqm__qur), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(yag__dlbok)
    c.pyapi.decref(xtoo__ekdko)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    xxn__znaj = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if xxn__znaj:
        xzenq__gktg = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        bujel__emg = cgutils.get_or_insert_function(c.builder.module,
            xzenq__gktg, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(bujel__emg,
            [val])])
    else:
        mffms__xny = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            mffms__xny, tui__jpe) for tui__jpe in range(1, mffms__xny.type.
            count)])
    iax__teaj, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if xxn__znaj:
        wjihv__eopvb = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        hhppy__xzi = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        xzenq__gktg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        vwdr__csjv = cgutils.get_or_insert_function(c.builder.module,
            xzenq__gktg, name='array_item_array_from_sequence')
        c.builder.call(vwdr__csjv, [val, c.builder.bitcast(hhppy__xzi, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), wjihv__eopvb)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    aivbn__iyy = c.context.make_helper(c.builder, typ)
    aivbn__iyy.meminfo = iax__teaj
    yhcns__jmdop = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(aivbn__iyy._getvalue(), is_error=yhcns__jmdop)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    aivbn__iyy = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    glf__gatn = context.nrt.meminfo_data(builder, aivbn__iyy.meminfo)
    guw__nttl = builder.bitcast(glf__gatn, context.get_value_type(
        payload_type).as_pointer())
    deah__kim = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(guw__nttl))
    return deah__kim


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    lwbk__fqmk = context.insert_const_string(builder.module, 'numpy')
    xscf__orvy = c.pyapi.import_module_noblock(lwbk__fqmk)
    yzt__knp = c.pyapi.object_getattr_string(xscf__orvy, 'object_')
    zvkjs__kfd = c.pyapi.long_from_longlong(n_arrays)
    vkm__pof = c.pyapi.call_method(xscf__orvy, 'ndarray', (zvkjs__kfd,
        yzt__knp))
    klem__ofpxt = c.pyapi.object_getattr_string(xscf__orvy, 'nan')
    kpqm__qur = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (64), 0))
    with cgutils.for_range(builder, n_arrays) as erat__zek:
        tytg__pbfv = erat__zek.index
        pyarray_setitem(builder, context, vkm__pof, tytg__pbfv, klem__ofpxt)
        tbtbj__cuq = get_bitmap_bit(builder, null_bitmap_ptr, tytg__pbfv)
        vopr__yybh = builder.icmp_unsigned('!=', tbtbj__cuq, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(vopr__yybh):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(tytg__pbfv, lir.Constant(
                tytg__pbfv.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [tytg__pbfv]))), lir.IntType(64))
            item_ind = builder.load(kpqm__qur)
            ehn__uaw, fne__rlfm = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), kpqm__qur)
            arr_obj = c.pyapi.from_native_value(typ.dtype, fne__rlfm, c.
                env_manager)
            pyarray_setitem(builder, context, vkm__pof, tytg__pbfv, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(xscf__orvy)
    c.pyapi.decref(yzt__knp)
    c.pyapi.decref(zvkjs__kfd)
    c.pyapi.decref(klem__ofpxt)
    return vkm__pof


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    deah__kim = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = deah__kim.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), deah__kim.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), deah__kim.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        wjihv__eopvb = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        hhppy__xzi = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        xzenq__gktg = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        odjgb__rykxj = cgutils.get_or_insert_function(c.builder.module,
            xzenq__gktg, name='np_array_from_array_item_array')
        arr = c.builder.call(odjgb__rykxj, [deah__kim.n_arrays, c.builder.
            bitcast(hhppy__xzi, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), wjihv__eopvb)])
    else:
        arr = _box_array_item_array_generic(typ, c, deah__kim.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    mqpeh__fnss, poy__eoah, qxgh__hvlgs = args
    nyabk__omwgb = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    qsirg__srr = sig.args[1]
    if not isinstance(qsirg__srr, types.UniTuple):
        poy__eoah = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for qxgh__hvlgs in range(nyabk__omwgb)])
    elif qsirg__srr.count < nyabk__omwgb:
        poy__eoah = cgutils.pack_array(builder, [builder.extract_value(
            poy__eoah, tui__jpe) for tui__jpe in range(qsirg__srr.count)] +
            [lir.Constant(lir.IntType(64), -1) for qxgh__hvlgs in range(
            nyabk__omwgb - qsirg__srr.count)])
    iax__teaj, qxgh__hvlgs, qxgh__hvlgs, qxgh__hvlgs = (
        construct_array_item_array(context, builder, array_item_type,
        mqpeh__fnss, poy__eoah))
    aivbn__iyy = context.make_helper(builder, array_item_type)
    aivbn__iyy.meminfo = iax__teaj
    return aivbn__iyy._getvalue()


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
    n_arrays, hez__rzuc, auy__otp, dtaf__rcgyg = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    bqvo__embrj = context.get_value_type(payload_type)
    tcwa__tev = context.get_abi_sizeof(bqvo__embrj)
    ved__lbycy = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    iax__teaj = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tcwa__tev), ved__lbycy)
    glf__gatn = context.nrt.meminfo_data(builder, iax__teaj)
    guw__nttl = builder.bitcast(glf__gatn, bqvo__embrj.as_pointer())
    deah__kim = cgutils.create_struct_proxy(payload_type)(context, builder)
    deah__kim.n_arrays = n_arrays
    deah__kim.data = hez__rzuc
    deah__kim.offsets = auy__otp
    deah__kim.null_bitmap = dtaf__rcgyg
    builder.store(deah__kim._getvalue(), guw__nttl)
    context.nrt.incref(builder, signature.args[1], hez__rzuc)
    context.nrt.incref(builder, signature.args[2], auy__otp)
    context.nrt.incref(builder, signature.args[3], dtaf__rcgyg)
    aivbn__iyy = context.make_helper(builder, array_item_type)
    aivbn__iyy.meminfo = iax__teaj
    return aivbn__iyy._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    hnhf__iprs = ArrayItemArrayType(data_type)
    sig = hnhf__iprs(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        deah__kim = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            deah__kim.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        deah__kim = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        hhppy__xzi = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, deah__kim.offsets).data
        auy__otp = builder.bitcast(hhppy__xzi, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(auy__otp, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        deah__kim = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            deah__kim.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        deah__kim = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            deah__kim.null_bitmap)
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
        deah__kim = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return deah__kim.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, kzald__iqql = args
        aivbn__iyy = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        glf__gatn = context.nrt.meminfo_data(builder, aivbn__iyy.meminfo)
        guw__nttl = builder.bitcast(glf__gatn, context.get_value_type(
            payload_type).as_pointer())
        deah__kim = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(guw__nttl))
        context.nrt.decref(builder, data_typ, deah__kim.data)
        deah__kim.data = kzald__iqql
        context.nrt.incref(builder, data_typ, kzald__iqql)
        builder.store(deah__kim._getvalue(), guw__nttl)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    hez__rzuc = get_data(arr)
    fuod__fpsb = len(hez__rzuc)
    if fuod__fpsb < new_size:
        iqh__any = max(2 * fuod__fpsb, new_size)
        kzald__iqql = bodo.libs.array_kernels.resize_and_copy(hez__rzuc,
            old_size, iqh__any)
        replace_data_arr(arr, kzald__iqql)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    hez__rzuc = get_data(arr)
    auy__otp = get_offsets(arr)
    ofq__gau = len(hez__rzuc)
    wmfm__rxgxb = auy__otp[-1]
    if ofq__gau != wmfm__rxgxb:
        kzald__iqql = bodo.libs.array_kernels.resize_and_copy(hez__rzuc,
            wmfm__rxgxb, wmfm__rxgxb)
        replace_data_arr(arr, kzald__iqql)


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
            auy__otp = get_offsets(arr)
            hez__rzuc = get_data(arr)
            dth__igwt = auy__otp[ind]
            jliac__lufx = auy__otp[ind + 1]
            return hez__rzuc[dth__igwt:jliac__lufx]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        aqemo__zzh = arr.dtype

        def impl_bool(arr, ind):
            xlv__nxtf = len(arr)
            if xlv__nxtf != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            dtaf__rcgyg = get_null_bitmap(arr)
            n_arrays = 0
            ojz__jcsva = init_nested_counts(aqemo__zzh)
            for tui__jpe in range(xlv__nxtf):
                if ind[tui__jpe]:
                    n_arrays += 1
                    tyohq__ndvn = arr[tui__jpe]
                    ojz__jcsva = add_nested_counts(ojz__jcsva, tyohq__ndvn)
            vkm__pof = pre_alloc_array_item_array(n_arrays, ojz__jcsva,
                aqemo__zzh)
            uzq__fhqti = get_null_bitmap(vkm__pof)
            ifdt__tnipi = 0
            for tlbj__ahs in range(xlv__nxtf):
                if ind[tlbj__ahs]:
                    vkm__pof[ifdt__tnipi] = arr[tlbj__ahs]
                    wbtl__xottj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        dtaf__rcgyg, tlbj__ahs)
                    bodo.libs.int_arr_ext.set_bit_to_arr(uzq__fhqti,
                        ifdt__tnipi, wbtl__xottj)
                    ifdt__tnipi += 1
            return vkm__pof
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        aqemo__zzh = arr.dtype

        def impl_int(arr, ind):
            dtaf__rcgyg = get_null_bitmap(arr)
            xlv__nxtf = len(ind)
            n_arrays = xlv__nxtf
            ojz__jcsva = init_nested_counts(aqemo__zzh)
            for vcj__qyu in range(xlv__nxtf):
                tui__jpe = ind[vcj__qyu]
                tyohq__ndvn = arr[tui__jpe]
                ojz__jcsva = add_nested_counts(ojz__jcsva, tyohq__ndvn)
            vkm__pof = pre_alloc_array_item_array(n_arrays, ojz__jcsva,
                aqemo__zzh)
            uzq__fhqti = get_null_bitmap(vkm__pof)
            for jfu__wqs in range(xlv__nxtf):
                tlbj__ahs = ind[jfu__wqs]
                vkm__pof[jfu__wqs] = arr[tlbj__ahs]
                wbtl__xottj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    dtaf__rcgyg, tlbj__ahs)
                bodo.libs.int_arr_ext.set_bit_to_arr(uzq__fhqti, jfu__wqs,
                    wbtl__xottj)
            return vkm__pof
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            xlv__nxtf = len(arr)
            skfb__ova = numba.cpython.unicode._normalize_slice(ind, xlv__nxtf)
            tzc__mfdms = np.arange(skfb__ova.start, skfb__ova.stop,
                skfb__ova.step)
            return arr[tzc__mfdms]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            auy__otp = get_offsets(A)
            dtaf__rcgyg = get_null_bitmap(A)
            if idx == 0:
                auy__otp[0] = 0
            n_items = len(val)
            pryzs__ubjy = auy__otp[idx] + n_items
            ensure_data_capacity(A, auy__otp[idx], pryzs__ubjy)
            hez__rzuc = get_data(A)
            auy__otp[idx + 1] = auy__otp[idx] + n_items
            hez__rzuc[auy__otp[idx]:auy__otp[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(dtaf__rcgyg, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            skfb__ova = numba.cpython.unicode._normalize_slice(idx, len(A))
            for tui__jpe in range(skfb__ova.start, skfb__ova.stop,
                skfb__ova.step):
                A[tui__jpe] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            auy__otp = get_offsets(A)
            dtaf__rcgyg = get_null_bitmap(A)
            wyspi__gcw = get_offsets(val)
            cekhe__qdap = get_data(val)
            higot__hav = get_null_bitmap(val)
            xlv__nxtf = len(A)
            skfb__ova = numba.cpython.unicode._normalize_slice(idx, xlv__nxtf)
            elgdb__jcw, yor__glkr = skfb__ova.start, skfb__ova.stop
            assert skfb__ova.step == 1
            if elgdb__jcw == 0:
                auy__otp[elgdb__jcw] = 0
            xaj__bkrru = auy__otp[elgdb__jcw]
            pryzs__ubjy = xaj__bkrru + len(cekhe__qdap)
            ensure_data_capacity(A, xaj__bkrru, pryzs__ubjy)
            hez__rzuc = get_data(A)
            hez__rzuc[xaj__bkrru:xaj__bkrru + len(cekhe__qdap)] = cekhe__qdap
            auy__otp[elgdb__jcw:yor__glkr + 1] = wyspi__gcw + xaj__bkrru
            loq__xfz = 0
            for tui__jpe in range(elgdb__jcw, yor__glkr):
                wbtl__xottj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    higot__hav, loq__xfz)
                bodo.libs.int_arr_ext.set_bit_to_arr(dtaf__rcgyg, tui__jpe,
                    wbtl__xottj)
                loq__xfz += 1
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
