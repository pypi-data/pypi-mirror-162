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
    exh__rqoux = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(exh__rqoux)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rvb__rpc = _get_map_arr_data_type(fe_type)
        dnsj__sqi = [('data', rvb__rpc)]
        models.StructModel.__init__(self, dmm, fe_type, dnsj__sqi)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    vudvk__tfvvz = all(isinstance(fniry__vys, types.Array) and fniry__vys.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for fniry__vys in (typ.key_arr_type, typ.
        value_arr_type))
    if vudvk__tfvvz:
        zuhxr__zegn = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        nhxh__lyje = cgutils.get_or_insert_function(c.builder.module,
            zuhxr__zegn, name='count_total_elems_list_array')
        imgai__hmspl = cgutils.pack_array(c.builder, [n_maps, c.builder.
            call(nhxh__lyje, [val])])
    else:
        imgai__hmspl = get_array_elem_counts(c, c.builder, c.context, val, typ)
    rvb__rpc = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, rvb__rpc,
        imgai__hmspl, c)
    teogf__baxun = _get_array_item_arr_payload(c.context, c.builder,
        rvb__rpc, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, teogf__baxun.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, teogf__baxun.offsets).data
    qfkw__cxco = _get_struct_arr_payload(c.context, c.builder, rvb__rpc.
        dtype, teogf__baxun.data)
    key_arr = c.builder.extract_value(qfkw__cxco.data, 0)
    value_arr = c.builder.extract_value(qfkw__cxco.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    jjq__qay, rfjrt__slh = c.pyapi.call_jit_code(lambda A: A.fill(255), sig,
        [qfkw__cxco.null_bitmap])
    if vudvk__tfvvz:
        kijc__niwv = c.context.make_array(rvb__rpc.dtype.data[0])(c.context,
            c.builder, key_arr).data
        kjnlx__ctomq = c.context.make_array(rvb__rpc.dtype.data[1])(c.
            context, c.builder, value_arr).data
        zuhxr__zegn = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        radps__tkzd = cgutils.get_or_insert_function(c.builder.module,
            zuhxr__zegn, name='map_array_from_sequence')
        njta__tud = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        pjc__ofze = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(radps__tkzd, [val, c.builder.bitcast(kijc__niwv, lir
            .IntType(8).as_pointer()), c.builder.bitcast(kjnlx__ctomq, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), njta__tud), lir.Constant(lir.IntType(
            32), pjc__ofze)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    ume__dtq = c.context.make_helper(c.builder, typ)
    ume__dtq.data = data_arr
    nnbf__grw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ume__dtq._getvalue(), is_error=nnbf__grw)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    zje__srw = context.insert_const_string(builder.module, 'pandas')
    ckjyc__ovxoi = c.pyapi.import_module_noblock(zje__srw)
    phmxe__qjb = c.pyapi.object_getattr_string(ckjyc__ovxoi, 'NA')
    kcmlu__arewq = c.context.get_constant(offset_type, 0)
    builder.store(kcmlu__arewq, offsets_ptr)
    tqp__ondox = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as znku__bov:
        hjayg__mhmmm = znku__bov.index
        item_ind = builder.load(tqp__ondox)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [hjayg__mhmmm]))
        nrwv__szpd = seq_getitem(builder, context, val, hjayg__mhmmm)
        set_bitmap_bit(builder, null_bitmap_ptr, hjayg__mhmmm, 0)
        ioy__gvl = is_na_value(builder, context, nrwv__szpd, phmxe__qjb)
        nfg__lxcv = builder.icmp_unsigned('!=', ioy__gvl, lir.Constant(
            ioy__gvl.type, 1))
        with builder.if_then(nfg__lxcv):
            set_bitmap_bit(builder, null_bitmap_ptr, hjayg__mhmmm, 1)
            idei__yrat = dict_keys(builder, context, nrwv__szpd)
            wfliz__cuez = dict_values(builder, context, nrwv__szpd)
            n_items = bodo.utils.utils.object_length(c, idei__yrat)
            _unbox_array_item_array_copy_data(typ.key_arr_type, idei__yrat,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                wfliz__cuez, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), tqp__ondox)
            c.pyapi.decref(idei__yrat)
            c.pyapi.decref(wfliz__cuez)
        c.pyapi.decref(nrwv__szpd)
    builder.store(builder.trunc(builder.load(tqp__ondox), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(ckjyc__ovxoi)
    c.pyapi.decref(phmxe__qjb)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    ume__dtq = c.context.make_helper(c.builder, typ, val)
    data_arr = ume__dtq.data
    rvb__rpc = _get_map_arr_data_type(typ)
    teogf__baxun = _get_array_item_arr_payload(c.context, c.builder,
        rvb__rpc, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, teogf__baxun.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, teogf__baxun.offsets).data
    qfkw__cxco = _get_struct_arr_payload(c.context, c.builder, rvb__rpc.
        dtype, teogf__baxun.data)
    key_arr = c.builder.extract_value(qfkw__cxco.data, 0)
    value_arr = c.builder.extract_value(qfkw__cxco.data, 1)
    if all(isinstance(fniry__vys, types.Array) and fniry__vys.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        fniry__vys in (typ.key_arr_type, typ.value_arr_type)):
        kijc__niwv = c.context.make_array(rvb__rpc.dtype.data[0])(c.context,
            c.builder, key_arr).data
        kjnlx__ctomq = c.context.make_array(rvb__rpc.dtype.data[1])(c.
            context, c.builder, value_arr).data
        zuhxr__zegn = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        bsaxf__svbr = cgutils.get_or_insert_function(c.builder.module,
            zuhxr__zegn, name='np_array_from_map_array')
        njta__tud = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        pjc__ofze = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(bsaxf__svbr, [teogf__baxun.n_arrays, c.builder
            .bitcast(kijc__niwv, lir.IntType(8).as_pointer()), c.builder.
            bitcast(kjnlx__ctomq, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), njta__tud), lir.
            Constant(lir.IntType(32), pjc__ofze)])
    else:
        arr = _box_map_array_generic(typ, c, teogf__baxun.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    zje__srw = context.insert_const_string(builder.module, 'numpy')
    uvhk__vao = c.pyapi.import_module_noblock(zje__srw)
    pqw__luyz = c.pyapi.object_getattr_string(uvhk__vao, 'object_')
    ppn__yuwye = c.pyapi.long_from_longlong(n_maps)
    olcd__ddj = c.pyapi.call_method(uvhk__vao, 'ndarray', (ppn__yuwye,
        pqw__luyz))
    puekk__tixne = c.pyapi.object_getattr_string(uvhk__vao, 'nan')
    gtnv__bnei = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    tqp__ondox = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as znku__bov:
        rsy__xjaaj = znku__bov.index
        pyarray_setitem(builder, context, olcd__ddj, rsy__xjaaj, puekk__tixne)
        bfdi__wplg = get_bitmap_bit(builder, null_bitmap_ptr, rsy__xjaaj)
        zatw__hkwg = builder.icmp_unsigned('!=', bfdi__wplg, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(zatw__hkwg):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(rsy__xjaaj, lir.Constant(
                rsy__xjaaj.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [rsy__xjaaj]))), lir.IntType(64))
            item_ind = builder.load(tqp__ondox)
            nrwv__szpd = c.pyapi.dict_new()
            vlvn__gzezc = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            jjq__qay, nqbbf__ktwy = c.pyapi.call_jit_code(vlvn__gzezc, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            jjq__qay, kivtn__kfam = c.pyapi.call_jit_code(vlvn__gzezc, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            jno__wkpzj = c.pyapi.from_native_value(typ.key_arr_type,
                nqbbf__ktwy, c.env_manager)
            kaik__ihe = c.pyapi.from_native_value(typ.value_arr_type,
                kivtn__kfam, c.env_manager)
            jnfsz__nunp = c.pyapi.call_function_objargs(gtnv__bnei, (
                jno__wkpzj, kaik__ihe))
            dict_merge_from_seq2(builder, context, nrwv__szpd, jnfsz__nunp)
            builder.store(builder.add(item_ind, n_items), tqp__ondox)
            pyarray_setitem(builder, context, olcd__ddj, rsy__xjaaj, nrwv__szpd
                )
            c.pyapi.decref(jnfsz__nunp)
            c.pyapi.decref(jno__wkpzj)
            c.pyapi.decref(kaik__ihe)
            c.pyapi.decref(nrwv__szpd)
    c.pyapi.decref(gtnv__bnei)
    c.pyapi.decref(uvhk__vao)
    c.pyapi.decref(pqw__luyz)
    c.pyapi.decref(ppn__yuwye)
    c.pyapi.decref(puekk__tixne)
    return olcd__ddj


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    ume__dtq = context.make_helper(builder, sig.return_type)
    ume__dtq.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return ume__dtq._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    gtr__atg = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return gtr__atg(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    zaaa__vbm = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(zaaa__vbm)


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
    ttko__lpff = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            ejqt__poodx = val.keys()
            ibqcm__nww = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), ttko__lpff, ('key', 'value'))
            for zlxod__jck, pfib__ubzzi in enumerate(ejqt__poodx):
                ibqcm__nww[zlxod__jck] = bodo.libs.struct_arr_ext.init_struct((
                    pfib__ubzzi, val[pfib__ubzzi]), ('key', 'value'))
            arr._data[ind] = ibqcm__nww
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
            zeg__nqwta = dict()
            wvbcw__chzq = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            ibqcm__nww = bodo.libs.array_item_arr_ext.get_data(arr._data)
            slgxm__fpsyu, gzrgv__ghp = bodo.libs.struct_arr_ext.get_data(
                ibqcm__nww)
            ysiom__vpk = wvbcw__chzq[ind]
            ialpi__whif = wvbcw__chzq[ind + 1]
            for zlxod__jck in range(ysiom__vpk, ialpi__whif):
                zeg__nqwta[slgxm__fpsyu[zlxod__jck]] = gzrgv__ghp[zlxod__jck]
            return zeg__nqwta
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
