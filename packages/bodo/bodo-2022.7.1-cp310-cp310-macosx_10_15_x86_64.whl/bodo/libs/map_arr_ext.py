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
    iwuv__fquv = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(iwuv__fquv)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fpcw__yoxmg = _get_map_arr_data_type(fe_type)
        cebe__wtyv = [('data', fpcw__yoxmg)]
        models.StructModel.__init__(self, dmm, fe_type, cebe__wtyv)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    oqza__wos = all(isinstance(cedqq__qdeo, types.Array) and cedqq__qdeo.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for cedqq__qdeo in (typ.key_arr_type, typ.
        value_arr_type))
    if oqza__wos:
        nqh__mbl = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        pgt__ini = cgutils.get_or_insert_function(c.builder.module,
            nqh__mbl, name='count_total_elems_list_array')
        nkbby__uoh = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            pgt__ini, [val])])
    else:
        nkbby__uoh = get_array_elem_counts(c, c.builder, c.context, val, typ)
    fpcw__yoxmg = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, fpcw__yoxmg,
        nkbby__uoh, c)
    zvle__ckody = _get_array_item_arr_payload(c.context, c.builder,
        fpcw__yoxmg, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, zvle__ckody.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, zvle__ckody.offsets).data
    feg__tjng = _get_struct_arr_payload(c.context, c.builder, fpcw__yoxmg.
        dtype, zvle__ckody.data)
    key_arr = c.builder.extract_value(feg__tjng.data, 0)
    value_arr = c.builder.extract_value(feg__tjng.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    dde__vkr, qqqeb__yvdfb = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [feg__tjng.null_bitmap])
    if oqza__wos:
        wua__bnw = c.context.make_array(fpcw__yoxmg.dtype.data[0])(c.
            context, c.builder, key_arr).data
        uyhij__qad = c.context.make_array(fpcw__yoxmg.dtype.data[1])(c.
            context, c.builder, value_arr).data
        nqh__mbl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        sar__tuqq = cgutils.get_or_insert_function(c.builder.module,
            nqh__mbl, name='map_array_from_sequence')
        wam__uhf = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zzpid__ehd = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(sar__tuqq, [val, c.builder.bitcast(wua__bnw, lir.
            IntType(8).as_pointer()), c.builder.bitcast(uyhij__qad, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), wam__uhf), lir.Constant(lir.IntType(
            32), zzpid__ehd)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    lqskj__kwr = c.context.make_helper(c.builder, typ)
    lqskj__kwr.data = data_arr
    sur__rvc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(lqskj__kwr._getvalue(), is_error=sur__rvc)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    mhsf__pkca = context.insert_const_string(builder.module, 'pandas')
    xdzr__iicnf = c.pyapi.import_module_noblock(mhsf__pkca)
    erhu__psr = c.pyapi.object_getattr_string(xdzr__iicnf, 'NA')
    ssx__toq = c.context.get_constant(offset_type, 0)
    builder.store(ssx__toq, offsets_ptr)
    esze__qqkr = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as rkfu__anjd:
        xvxs__oyzd = rkfu__anjd.index
        item_ind = builder.load(esze__qqkr)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [xvxs__oyzd]))
        uhok__icat = seq_getitem(builder, context, val, xvxs__oyzd)
        set_bitmap_bit(builder, null_bitmap_ptr, xvxs__oyzd, 0)
        dfsb__yzfyx = is_na_value(builder, context, uhok__icat, erhu__psr)
        sabzx__oqhh = builder.icmp_unsigned('!=', dfsb__yzfyx, lir.Constant
            (dfsb__yzfyx.type, 1))
        with builder.if_then(sabzx__oqhh):
            set_bitmap_bit(builder, null_bitmap_ptr, xvxs__oyzd, 1)
            gmtje__nbnw = dict_keys(builder, context, uhok__icat)
            teud__pvpm = dict_values(builder, context, uhok__icat)
            n_items = bodo.utils.utils.object_length(c, gmtje__nbnw)
            _unbox_array_item_array_copy_data(typ.key_arr_type, gmtje__nbnw,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                teud__pvpm, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), esze__qqkr)
            c.pyapi.decref(gmtje__nbnw)
            c.pyapi.decref(teud__pvpm)
        c.pyapi.decref(uhok__icat)
    builder.store(builder.trunc(builder.load(esze__qqkr), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(xdzr__iicnf)
    c.pyapi.decref(erhu__psr)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    lqskj__kwr = c.context.make_helper(c.builder, typ, val)
    data_arr = lqskj__kwr.data
    fpcw__yoxmg = _get_map_arr_data_type(typ)
    zvle__ckody = _get_array_item_arr_payload(c.context, c.builder,
        fpcw__yoxmg, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, zvle__ckody.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, zvle__ckody.offsets).data
    feg__tjng = _get_struct_arr_payload(c.context, c.builder, fpcw__yoxmg.
        dtype, zvle__ckody.data)
    key_arr = c.builder.extract_value(feg__tjng.data, 0)
    value_arr = c.builder.extract_value(feg__tjng.data, 1)
    if all(isinstance(cedqq__qdeo, types.Array) and cedqq__qdeo.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        cedqq__qdeo in (typ.key_arr_type, typ.value_arr_type)):
        wua__bnw = c.context.make_array(fpcw__yoxmg.dtype.data[0])(c.
            context, c.builder, key_arr).data
        uyhij__qad = c.context.make_array(fpcw__yoxmg.dtype.data[1])(c.
            context, c.builder, value_arr).data
        nqh__mbl = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        izlf__tyyb = cgutils.get_or_insert_function(c.builder.module,
            nqh__mbl, name='np_array_from_map_array')
        wam__uhf = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zzpid__ehd = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(izlf__tyyb, [zvle__ckody.n_arrays, c.builder.
            bitcast(wua__bnw, lir.IntType(8).as_pointer()), c.builder.
            bitcast(uyhij__qad, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), wam__uhf), lir.
            Constant(lir.IntType(32), zzpid__ehd)])
    else:
        arr = _box_map_array_generic(typ, c, zvle__ckody.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    mhsf__pkca = context.insert_const_string(builder.module, 'numpy')
    krgsl__mzoxx = c.pyapi.import_module_noblock(mhsf__pkca)
    cieyi__glcy = c.pyapi.object_getattr_string(krgsl__mzoxx, 'object_')
    rwum__wivd = c.pyapi.long_from_longlong(n_maps)
    vvgin__glabc = c.pyapi.call_method(krgsl__mzoxx, 'ndarray', (rwum__wivd,
        cieyi__glcy))
    xfkrt__pqm = c.pyapi.object_getattr_string(krgsl__mzoxx, 'nan')
    hvmg__bdovd = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    esze__qqkr = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as rkfu__anjd:
        vuz__pvkut = rkfu__anjd.index
        pyarray_setitem(builder, context, vvgin__glabc, vuz__pvkut, xfkrt__pqm)
        blw__cvto = get_bitmap_bit(builder, null_bitmap_ptr, vuz__pvkut)
        bperp__mkh = builder.icmp_unsigned('!=', blw__cvto, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(bperp__mkh):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(vuz__pvkut, lir.Constant(
                vuz__pvkut.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [vuz__pvkut]))), lir.IntType(64))
            item_ind = builder.load(esze__qqkr)
            uhok__icat = c.pyapi.dict_new()
            ugbbp__cyt = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            dde__vkr, mowxo__ebdd = c.pyapi.call_jit_code(ugbbp__cyt, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            dde__vkr, hgh__gpd = c.pyapi.call_jit_code(ugbbp__cyt, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            evfj__krkca = c.pyapi.from_native_value(typ.key_arr_type,
                mowxo__ebdd, c.env_manager)
            djks__ibkz = c.pyapi.from_native_value(typ.value_arr_type,
                hgh__gpd, c.env_manager)
            mwlx__eeg = c.pyapi.call_function_objargs(hvmg__bdovd, (
                evfj__krkca, djks__ibkz))
            dict_merge_from_seq2(builder, context, uhok__icat, mwlx__eeg)
            builder.store(builder.add(item_ind, n_items), esze__qqkr)
            pyarray_setitem(builder, context, vvgin__glabc, vuz__pvkut,
                uhok__icat)
            c.pyapi.decref(mwlx__eeg)
            c.pyapi.decref(evfj__krkca)
            c.pyapi.decref(djks__ibkz)
            c.pyapi.decref(uhok__icat)
    c.pyapi.decref(hvmg__bdovd)
    c.pyapi.decref(krgsl__mzoxx)
    c.pyapi.decref(cieyi__glcy)
    c.pyapi.decref(rwum__wivd)
    c.pyapi.decref(xfkrt__pqm)
    return vvgin__glabc


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    lqskj__kwr = context.make_helper(builder, sig.return_type)
    lqskj__kwr.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return lqskj__kwr._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    shg__xyprx = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return shg__xyprx(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    kqjd__irkd = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(kqjd__irkd)


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
    wtqhp__yofsa = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            enksy__snw = val.keys()
            ccla__tjvci = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), wtqhp__yofsa, ('key', 'value'))
            for vnc__mff, mtmqi__fexl in enumerate(enksy__snw):
                ccla__tjvci[vnc__mff] = bodo.libs.struct_arr_ext.init_struct((
                    mtmqi__fexl, val[mtmqi__fexl]), ('key', 'value'))
            arr._data[ind] = ccla__tjvci
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
            hidfr__kpio = dict()
            lfph__dzwq = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            ccla__tjvci = bodo.libs.array_item_arr_ext.get_data(arr._data)
            yzsy__jpcrq, itk__gncjk = bodo.libs.struct_arr_ext.get_data(
                ccla__tjvci)
            yyzo__slcu = lfph__dzwq[ind]
            lfop__wcc = lfph__dzwq[ind + 1]
            for vnc__mff in range(yyzo__slcu, lfop__wcc):
                hidfr__kpio[yzsy__jpcrq[vnc__mff]] = itk__gncjk[vnc__mff]
            return hidfr__kpio
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
