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
    eks__oko = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(eks__oko)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xqnrq__ygj = _get_map_arr_data_type(fe_type)
        pmirn__kkt = [('data', xqnrq__ygj)]
        models.StructModel.__init__(self, dmm, fe_type, pmirn__kkt)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    nqw__uga = all(isinstance(nlhq__efrl, types.Array) and nlhq__efrl.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        nlhq__efrl in (typ.key_arr_type, typ.value_arr_type))
    if nqw__uga:
        fvdl__lwyu = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        ceu__ler = cgutils.get_or_insert_function(c.builder.module,
            fvdl__lwyu, name='count_total_elems_list_array')
        mna__torsu = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            ceu__ler, [val])])
    else:
        mna__torsu = get_array_elem_counts(c, c.builder, c.context, val, typ)
    xqnrq__ygj = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, xqnrq__ygj,
        mna__torsu, c)
    wht__qbjbc = _get_array_item_arr_payload(c.context, c.builder,
        xqnrq__ygj, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, wht__qbjbc.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, wht__qbjbc.offsets).data
    cavd__hwerk = _get_struct_arr_payload(c.context, c.builder, xqnrq__ygj.
        dtype, wht__qbjbc.data)
    key_arr = c.builder.extract_value(cavd__hwerk.data, 0)
    value_arr = c.builder.extract_value(cavd__hwerk.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    ptbh__ivgmv, lbvzk__vudq = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [cavd__hwerk.null_bitmap])
    if nqw__uga:
        ctdl__auv = c.context.make_array(xqnrq__ygj.dtype.data[0])(c.
            context, c.builder, key_arr).data
        rhpa__zlk = c.context.make_array(xqnrq__ygj.dtype.data[1])(c.
            context, c.builder, value_arr).data
        fvdl__lwyu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        quhwv__ddzh = cgutils.get_or_insert_function(c.builder.module,
            fvdl__lwyu, name='map_array_from_sequence')
        cazi__ouyto = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zzb__qmrbm = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(quhwv__ddzh, [val, c.builder.bitcast(ctdl__auv, lir.
            IntType(8).as_pointer()), c.builder.bitcast(rhpa__zlk, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), cazi__ouyto), lir.Constant(lir.
            IntType(32), zzb__qmrbm)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    rwu__rsasj = c.context.make_helper(c.builder, typ)
    rwu__rsasj.data = data_arr
    mbu__dur = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rwu__rsasj._getvalue(), is_error=mbu__dur)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    cru__bve = context.insert_const_string(builder.module, 'pandas')
    tvc__avh = c.pyapi.import_module_noblock(cru__bve)
    igd__ook = c.pyapi.object_getattr_string(tvc__avh, 'NA')
    aen__cqkwz = c.context.get_constant(offset_type, 0)
    builder.store(aen__cqkwz, offsets_ptr)
    grp__xtj = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as pvg__hery:
        hwuf__lvxa = pvg__hery.index
        item_ind = builder.load(grp__xtj)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [hwuf__lvxa]))
        mzbde__cilb = seq_getitem(builder, context, val, hwuf__lvxa)
        set_bitmap_bit(builder, null_bitmap_ptr, hwuf__lvxa, 0)
        vdw__elcim = is_na_value(builder, context, mzbde__cilb, igd__ook)
        udl__geujd = builder.icmp_unsigned('!=', vdw__elcim, lir.Constant(
            vdw__elcim.type, 1))
        with builder.if_then(udl__geujd):
            set_bitmap_bit(builder, null_bitmap_ptr, hwuf__lvxa, 1)
            kur__xxpcp = dict_keys(builder, context, mzbde__cilb)
            qnd__cfyql = dict_values(builder, context, mzbde__cilb)
            n_items = bodo.utils.utils.object_length(c, kur__xxpcp)
            _unbox_array_item_array_copy_data(typ.key_arr_type, kur__xxpcp,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                qnd__cfyql, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), grp__xtj)
            c.pyapi.decref(kur__xxpcp)
            c.pyapi.decref(qnd__cfyql)
        c.pyapi.decref(mzbde__cilb)
    builder.store(builder.trunc(builder.load(grp__xtj), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(tvc__avh)
    c.pyapi.decref(igd__ook)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    rwu__rsasj = c.context.make_helper(c.builder, typ, val)
    data_arr = rwu__rsasj.data
    xqnrq__ygj = _get_map_arr_data_type(typ)
    wht__qbjbc = _get_array_item_arr_payload(c.context, c.builder,
        xqnrq__ygj, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, wht__qbjbc.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, wht__qbjbc.offsets).data
    cavd__hwerk = _get_struct_arr_payload(c.context, c.builder, xqnrq__ygj.
        dtype, wht__qbjbc.data)
    key_arr = c.builder.extract_value(cavd__hwerk.data, 0)
    value_arr = c.builder.extract_value(cavd__hwerk.data, 1)
    if all(isinstance(nlhq__efrl, types.Array) and nlhq__efrl.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        nlhq__efrl in (typ.key_arr_type, typ.value_arr_type)):
        ctdl__auv = c.context.make_array(xqnrq__ygj.dtype.data[0])(c.
            context, c.builder, key_arr).data
        rhpa__zlk = c.context.make_array(xqnrq__ygj.dtype.data[1])(c.
            context, c.builder, value_arr).data
        fvdl__lwyu = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        hqqli__dkdgw = cgutils.get_or_insert_function(c.builder.module,
            fvdl__lwyu, name='np_array_from_map_array')
        cazi__ouyto = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zzb__qmrbm = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(hqqli__dkdgw, [wht__qbjbc.n_arrays, c.builder.
            bitcast(ctdl__auv, lir.IntType(8).as_pointer()), c.builder.
            bitcast(rhpa__zlk, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), cazi__ouyto),
            lir.Constant(lir.IntType(32), zzb__qmrbm)])
    else:
        arr = _box_map_array_generic(typ, c, wht__qbjbc.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    cru__bve = context.insert_const_string(builder.module, 'numpy')
    wso__ckgkq = c.pyapi.import_module_noblock(cru__bve)
    qhskm__kxqv = c.pyapi.object_getattr_string(wso__ckgkq, 'object_')
    gat__rqy = c.pyapi.long_from_longlong(n_maps)
    vlnr__bdwv = c.pyapi.call_method(wso__ckgkq, 'ndarray', (gat__rqy,
        qhskm__kxqv))
    oxd__fpyd = c.pyapi.object_getattr_string(wso__ckgkq, 'nan')
    knutv__kdj = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    grp__xtj = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType(
        64), 0))
    with cgutils.for_range(builder, n_maps) as pvg__hery:
        fgz__fqpd = pvg__hery.index
        pyarray_setitem(builder, context, vlnr__bdwv, fgz__fqpd, oxd__fpyd)
        gdhtf__ohju = get_bitmap_bit(builder, null_bitmap_ptr, fgz__fqpd)
        kysk__nbi = builder.icmp_unsigned('!=', gdhtf__ohju, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(kysk__nbi):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(fgz__fqpd, lir.Constant(fgz__fqpd
                .type, 1))])), builder.load(builder.gep(offsets_ptr, [
                fgz__fqpd]))), lir.IntType(64))
            item_ind = builder.load(grp__xtj)
            mzbde__cilb = c.pyapi.dict_new()
            rrei__lkl = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            ptbh__ivgmv, qfk__cvx = c.pyapi.call_jit_code(rrei__lkl, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            ptbh__ivgmv, ueu__vcvt = c.pyapi.call_jit_code(rrei__lkl, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            knhy__ckdzr = c.pyapi.from_native_value(typ.key_arr_type,
                qfk__cvx, c.env_manager)
            euam__rhx = c.pyapi.from_native_value(typ.value_arr_type,
                ueu__vcvt, c.env_manager)
            zewez__ioqcl = c.pyapi.call_function_objargs(knutv__kdj, (
                knhy__ckdzr, euam__rhx))
            dict_merge_from_seq2(builder, context, mzbde__cilb, zewez__ioqcl)
            builder.store(builder.add(item_ind, n_items), grp__xtj)
            pyarray_setitem(builder, context, vlnr__bdwv, fgz__fqpd,
                mzbde__cilb)
            c.pyapi.decref(zewez__ioqcl)
            c.pyapi.decref(knhy__ckdzr)
            c.pyapi.decref(euam__rhx)
            c.pyapi.decref(mzbde__cilb)
    c.pyapi.decref(knutv__kdj)
    c.pyapi.decref(wso__ckgkq)
    c.pyapi.decref(qhskm__kxqv)
    c.pyapi.decref(gat__rqy)
    c.pyapi.decref(oxd__fpyd)
    return vlnr__bdwv


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    rwu__rsasj = context.make_helper(builder, sig.return_type)
    rwu__rsasj.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return rwu__rsasj._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    lvoqd__doo = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return lvoqd__doo(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    jgxe__frko = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(jgxe__frko)


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
    nwem__sgym = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            blhmx__fona = val.keys()
            qmwyw__hpa = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), nwem__sgym, ('key', 'value'))
            for lywhh__cyj, gonc__scqlw in enumerate(blhmx__fona):
                qmwyw__hpa[lywhh__cyj] = bodo.libs.struct_arr_ext.init_struct((
                    gonc__scqlw, val[gonc__scqlw]), ('key', 'value'))
            arr._data[ind] = qmwyw__hpa
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
            vbdgg__bfbgu = dict()
            cdxve__zijuj = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            qmwyw__hpa = bodo.libs.array_item_arr_ext.get_data(arr._data)
            nremb__jsut, nhocw__yzj = bodo.libs.struct_arr_ext.get_data(
                qmwyw__hpa)
            lwlal__ept = cdxve__zijuj[ind]
            ykvg__gcy = cdxve__zijuj[ind + 1]
            for lywhh__cyj in range(lwlal__ept, ykvg__gcy):
                vbdgg__bfbgu[nremb__jsut[lywhh__cyj]] = nhocw__yzj[lywhh__cyj]
            return vbdgg__bfbgu
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
