"""Array implementation for map values.
Corresponds to Spark's MapType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Map arrays: https://github.com/apache/arrow/blob/master/format/Schema.fbs

The implementation uses an array(struct) array underneath similar to Spark and Arrow.
For example: [{1: 2.1, 3: 1.1}, {5: -1.0}]
[[{"key": 1, "value" 2.1}, {"key": 3, "value": 1.1}], [{"key": 5, "value": -1.0}]]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, _get_array_item_arr_payload, offset_type
from bodo.libs.struct_arr_ext import StructArrayType, _get_struct_arr_payload
from bodo.utils.cg_helpers import dict_keys, dict_merge_from_seq2, dict_values, gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit
from bodo.utils.typing import BodoError
from bodo.libs import array_ext, hdist
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('map_array_from_sequence', array_ext.map_array_from_sequence)
ll.add_symbol('np_array_from_map_array', array_ext.np_array_from_map_array)


class MapArrayType(types.ArrayCompatible):

    def __init__(self, key_arr_type, value_arr_type):
        self.key_arr_type = key_arr_type
        self.value_arr_type = value_arr_type
        super(MapArrayType, self).__init__(name='MapArrayType({}, {})'.
            format(key_arr_type, value_arr_type))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.DictType(self.key_arr_type.dtype, self.value_arr_type.
            dtype)

    def copy(self):
        return MapArrayType(self.key_arr_type, self.value_arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_map_arr_data_type(map_type):
    eepo__cxzq = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(eepo__cxzq)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lzxlj__satnf = _get_map_arr_data_type(fe_type)
        fla__iwzay = [('data', lzxlj__satnf)]
        models.StructModel.__init__(self, dmm, fe_type, fla__iwzay)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    qdes__oqehu = all(isinstance(vum__pjugm, types.Array) and vum__pjugm.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for vum__pjugm in (typ.key_arr_type, typ.
        value_arr_type))
    if qdes__oqehu:
        ttl__ynrnb = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        blpw__gmwd = cgutils.get_or_insert_function(c.builder.module,
            ttl__ynrnb, name='count_total_elems_list_array')
        ulsf__ddzi = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            blpw__gmwd, [val])])
    else:
        ulsf__ddzi = get_array_elem_counts(c, c.builder, c.context, val, typ)
    lzxlj__satnf = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, lzxlj__satnf,
        ulsf__ddzi, c)
    iws__iot = _get_array_item_arr_payload(c.context, c.builder,
        lzxlj__satnf, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, iws__iot.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, iws__iot.offsets).data
    yen__kxwn = _get_struct_arr_payload(c.context, c.builder, lzxlj__satnf.
        dtype, iws__iot.data)
    key_arr = c.builder.extract_value(yen__kxwn.data, 0)
    value_arr = c.builder.extract_value(yen__kxwn.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    pwjh__gszfk, gyvwp__eeug = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [yen__kxwn.null_bitmap])
    if qdes__oqehu:
        znmk__zggor = c.context.make_array(lzxlj__satnf.dtype.data[0])(c.
            context, c.builder, key_arr).data
        atw__eqqx = c.context.make_array(lzxlj__satnf.dtype.data[1])(c.
            context, c.builder, value_arr).data
        ttl__ynrnb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        jme__njj = cgutils.get_or_insert_function(c.builder.module,
            ttl__ynrnb, name='map_array_from_sequence')
        vdpa__kbfwj = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        ugbcl__muqwa = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.
            dtype)
        c.builder.call(jme__njj, [val, c.builder.bitcast(znmk__zggor, lir.
            IntType(8).as_pointer()), c.builder.bitcast(atw__eqqx, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), vdpa__kbfwj), lir.Constant(lir.
            IntType(32), ugbcl__muqwa)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    bmg__hmjvb = c.context.make_helper(c.builder, typ)
    bmg__hmjvb.data = data_arr
    dvg__qxooc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bmg__hmjvb._getvalue(), is_error=dvg__qxooc)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    aks__zvk = context.insert_const_string(builder.module, 'pandas')
    nzgth__vsc = c.pyapi.import_module_noblock(aks__zvk)
    gnx__rfu = c.pyapi.object_getattr_string(nzgth__vsc, 'NA')
    vcce__dyed = c.context.get_constant(offset_type, 0)
    builder.store(vcce__dyed, offsets_ptr)
    age__neayi = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as hwkca__rzd:
        ppuc__bjjg = hwkca__rzd.index
        item_ind = builder.load(age__neayi)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [ppuc__bjjg]))
        nmf__ilhsb = seq_getitem(builder, context, val, ppuc__bjjg)
        set_bitmap_bit(builder, null_bitmap_ptr, ppuc__bjjg, 0)
        svn__ctxrw = is_na_value(builder, context, nmf__ilhsb, gnx__rfu)
        noztx__ajc = builder.icmp_unsigned('!=', svn__ctxrw, lir.Constant(
            svn__ctxrw.type, 1))
        with builder.if_then(noztx__ajc):
            set_bitmap_bit(builder, null_bitmap_ptr, ppuc__bjjg, 1)
            juesb__cdkfy = dict_keys(builder, context, nmf__ilhsb)
            rqtlz__qmdoc = dict_values(builder, context, nmf__ilhsb)
            n_items = bodo.utils.utils.object_length(c, juesb__cdkfy)
            _unbox_array_item_array_copy_data(typ.key_arr_type,
                juesb__cdkfy, c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                rqtlz__qmdoc, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), age__neayi)
            c.pyapi.decref(juesb__cdkfy)
            c.pyapi.decref(rqtlz__qmdoc)
        c.pyapi.decref(nmf__ilhsb)
    builder.store(builder.trunc(builder.load(age__neayi), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(nzgth__vsc)
    c.pyapi.decref(gnx__rfu)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    bmg__hmjvb = c.context.make_helper(c.builder, typ, val)
    data_arr = bmg__hmjvb.data
    lzxlj__satnf = _get_map_arr_data_type(typ)
    iws__iot = _get_array_item_arr_payload(c.context, c.builder,
        lzxlj__satnf, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, iws__iot.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, iws__iot.offsets).data
    yen__kxwn = _get_struct_arr_payload(c.context, c.builder, lzxlj__satnf.
        dtype, iws__iot.data)
    key_arr = c.builder.extract_value(yen__kxwn.data, 0)
    value_arr = c.builder.extract_value(yen__kxwn.data, 1)
    if all(isinstance(vum__pjugm, types.Array) and vum__pjugm.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        vum__pjugm in (typ.key_arr_type, typ.value_arr_type)):
        znmk__zggor = c.context.make_array(lzxlj__satnf.dtype.data[0])(c.
            context, c.builder, key_arr).data
        atw__eqqx = c.context.make_array(lzxlj__satnf.dtype.data[1])(c.
            context, c.builder, value_arr).data
        ttl__ynrnb = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        wglv__qjmhk = cgutils.get_or_insert_function(c.builder.module,
            ttl__ynrnb, name='np_array_from_map_array')
        vdpa__kbfwj = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        ugbcl__muqwa = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.
            dtype)
        arr = c.builder.call(wglv__qjmhk, [iws__iot.n_arrays, c.builder.
            bitcast(znmk__zggor, lir.IntType(8).as_pointer()), c.builder.
            bitcast(atw__eqqx, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), vdpa__kbfwj),
            lir.Constant(lir.IntType(32), ugbcl__muqwa)])
    else:
        arr = _box_map_array_generic(typ, c, iws__iot.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    aks__zvk = context.insert_const_string(builder.module, 'numpy')
    tzse__bvnjf = c.pyapi.import_module_noblock(aks__zvk)
    fbzb__fddx = c.pyapi.object_getattr_string(tzse__bvnjf, 'object_')
    sabpu__bpt = c.pyapi.long_from_longlong(n_maps)
    lhwj__lzfdw = c.pyapi.call_method(tzse__bvnjf, 'ndarray', (sabpu__bpt,
        fbzb__fddx))
    qng__vsqcl = c.pyapi.object_getattr_string(tzse__bvnjf, 'nan')
    ujzgg__ebic = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    age__neayi = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as hwkca__rzd:
        nzox__fimjv = hwkca__rzd.index
        pyarray_setitem(builder, context, lhwj__lzfdw, nzox__fimjv, qng__vsqcl)
        gahcc__djviq = get_bitmap_bit(builder, null_bitmap_ptr, nzox__fimjv)
        ddz__ujlk = builder.icmp_unsigned('!=', gahcc__djviq, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(ddz__ujlk):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(nzox__fimjv, lir.Constant(
                nzox__fimjv.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [nzox__fimjv]))), lir.IntType(64))
            item_ind = builder.load(age__neayi)
            nmf__ilhsb = c.pyapi.dict_new()
            fyyzo__yro = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            pwjh__gszfk, bwn__vsu = c.pyapi.call_jit_code(fyyzo__yro, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            pwjh__gszfk, nxamk__cbfkw = c.pyapi.call_jit_code(fyyzo__yro,
                typ.value_arr_type(typ.value_arr_type, types.int64, types.
                int64), [value_arr, item_ind, n_items])
            kgjj__ycuu = c.pyapi.from_native_value(typ.key_arr_type,
                bwn__vsu, c.env_manager)
            ooto__yiye = c.pyapi.from_native_value(typ.value_arr_type,
                nxamk__cbfkw, c.env_manager)
            gapg__awekh = c.pyapi.call_function_objargs(ujzgg__ebic, (
                kgjj__ycuu, ooto__yiye))
            dict_merge_from_seq2(builder, context, nmf__ilhsb, gapg__awekh)
            builder.store(builder.add(item_ind, n_items), age__neayi)
            pyarray_setitem(builder, context, lhwj__lzfdw, nzox__fimjv,
                nmf__ilhsb)
            c.pyapi.decref(gapg__awekh)
            c.pyapi.decref(kgjj__ycuu)
            c.pyapi.decref(ooto__yiye)
            c.pyapi.decref(nmf__ilhsb)
    c.pyapi.decref(ujzgg__ebic)
    c.pyapi.decref(tzse__bvnjf)
    c.pyapi.decref(fbzb__fddx)
    c.pyapi.decref(sabpu__bpt)
    c.pyapi.decref(qng__vsqcl)
    return lhwj__lzfdw


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    bmg__hmjvb = context.make_helper(builder, sig.return_type)
    bmg__hmjvb.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return bmg__hmjvb._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    rctd__vwdw = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return rctd__vwdw(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    qndj__ijzz = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(qndj__ijzz)


def pre_alloc_map_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_map_arr_ext_pre_alloc_map_array
    ) = pre_alloc_map_array_equiv


@overload(len, no_unliteral=True)
def overload_map_arr_len(A):
    if isinstance(A, MapArrayType):
        return lambda A: len(A._data)


@overload_attribute(MapArrayType, 'shape')
def overload_map_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(MapArrayType, 'dtype')
def overload_map_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(MapArrayType, 'ndim')
def overload_map_arr_ndim(A):
    return lambda A: 1


@overload_attribute(MapArrayType, 'nbytes')
def overload_map_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(MapArrayType, 'copy')
def overload_map_arr_copy(A):
    return lambda A: init_map_arr(A._data.copy())


@overload(operator.setitem, no_unliteral=True)
def map_arr_setitem(arr, ind, val):
    if not isinstance(arr, MapArrayType):
        return
    dgii__nom = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            upq__arb = val.keys()
            oxgss__miec = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), dgii__nom, ('key', 'value'))
            for ebkj__pjwx, dtr__hmea in enumerate(upq__arb):
                oxgss__miec[ebkj__pjwx] = bodo.libs.struct_arr_ext.init_struct(
                    (dtr__hmea, val[dtr__hmea]), ('key', 'value'))
            arr._data[ind] = oxgss__miec
        return map_arr_setitem_impl
    raise BodoError(
        'operator.setitem with MapArrays is only supported with an integer index.'
        )


@overload(operator.getitem, no_unliteral=True)
def map_arr_getitem(arr, ind):
    if not isinstance(arr, MapArrayType):
        return
    if isinstance(ind, types.Integer):

        def map_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            pgluu__buk = dict()
            ewvq__ohil = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            oxgss__miec = bodo.libs.array_item_arr_ext.get_data(arr._data)
            msex__unm, xhdh__whfa = bodo.libs.struct_arr_ext.get_data(
                oxgss__miec)
            znca__acv = ewvq__ohil[ind]
            zbpn__vhn = ewvq__ohil[ind + 1]
            for ebkj__pjwx in range(znca__acv, zbpn__vhn):
                pgluu__buk[msex__unm[ebkj__pjwx]] = xhdh__whfa[ebkj__pjwx]
            return pgluu__buk
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
