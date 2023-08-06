"""Array implementation for structs of values.
Corresponds to Spark's StructType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Struct arrays: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in contiguous data arrays; one array per field. For example:
A:             ["AA", "B", "C"]
B:             [1, 2, 4]
"""
import operator
import llvmlite.binding as ll
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
from numba.typed.typedobjectutils import _cast
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_int, get_overload_const_str, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
ll.add_symbol('struct_array_from_sequence', array_ext.
    struct_array_from_sequence)
ll.add_symbol('np_array_from_struct_array', array_ext.
    np_array_from_struct_array)


class StructArrayType(types.ArrayCompatible):

    def __init__(self, data, names=None):
        assert isinstance(data, tuple) and len(data) > 0 and all(bodo.utils
            .utils.is_array_typ(puf__jhhh, False) for puf__jhhh in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(puf__jhhh,
                str) for puf__jhhh in names) and len(names) == len(data)
        else:
            names = tuple('f{}'.format(i) for i in range(len(data)))
        self.data = data
        self.names = names
        super(StructArrayType, self).__init__(name=
            'StructArrayType({}, {})'.format(data, names))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return StructType(tuple(dwpoi__zbtmm.dtype for dwpoi__zbtmm in self
            .data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(puf__jhhh) for puf__jhhh in d.keys())
        data = tuple(dtype_to_array_type(dwpoi__zbtmm) for dwpoi__zbtmm in
            d.values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(puf__jhhh, False) for puf__jhhh in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mncyl__yww = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, mncyl__yww)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        mncyl__yww = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, mncyl__yww)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    ymra__dchfr = builder.module
    bhzm__qffbl = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    zhsl__miyb = cgutils.get_or_insert_function(ymra__dchfr, bhzm__qffbl,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not zhsl__miyb.is_declaration:
        return zhsl__miyb
    zhsl__miyb.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(zhsl__miyb.append_basic_block())
    tkzor__hkoc = zhsl__miyb.args[0]
    urogi__znjh = context.get_value_type(payload_type).as_pointer()
    lav__pjo = builder.bitcast(tkzor__hkoc, urogi__znjh)
    ddj__nsucb = context.make_helper(builder, payload_type, ref=lav__pjo)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), ddj__nsucb.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        ddj__nsucb.null_bitmap)
    builder.ret_void()
    return zhsl__miyb


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    lotb__tdzn = context.get_value_type(payload_type)
    cuw__ztyv = context.get_abi_sizeof(lotb__tdzn)
    jpe__xnv = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    nbmx__kvq = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, cuw__ztyv), jpe__xnv)
    maq__ipws = context.nrt.meminfo_data(builder, nbmx__kvq)
    prtq__qboge = builder.bitcast(maq__ipws, lotb__tdzn.as_pointer())
    ddj__nsucb = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    mifc__wecww = 0
    for arr_typ in struct_arr_type.data:
        uqp__pnxc = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        hzq__hseua = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(mifc__wecww, 
            mifc__wecww + uqp__pnxc)])
        arr = gen_allocate_array(context, builder, arr_typ, hzq__hseua, c)
        arrs.append(arr)
        mifc__wecww += uqp__pnxc
    ddj__nsucb.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    ncp__inhks = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    ags__uzb = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [ncp__inhks])
    null_bitmap_ptr = ags__uzb.data
    ddj__nsucb.null_bitmap = ags__uzb._getvalue()
    builder.store(ddj__nsucb._getvalue(), prtq__qboge)
    return nbmx__kvq, ddj__nsucb.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    kixn__art = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        vmkhi__qnf = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            vmkhi__qnf)
        kixn__art.append(arr.data)
    olttg__ewd = cgutils.pack_array(c.builder, kixn__art
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, kixn__art)
    bozmc__cewzv = cgutils.alloca_once_value(c.builder, olttg__ewd)
    hdueh__ytol = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(puf__jhhh.dtype)) for puf__jhhh in data_typ]
    xgdrx__dsoby = cgutils.alloca_once_value(c.builder, cgutils.pack_array(
        c.builder, hdueh__ytol))
    ozr__rbg = cgutils.pack_array(c.builder, [c.context.insert_const_string
        (c.builder.module, puf__jhhh) for puf__jhhh in names])
    ppzt__dliy = cgutils.alloca_once_value(c.builder, ozr__rbg)
    return bozmc__cewzv, xgdrx__dsoby, ppzt__dliy


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    byss__silb = all(isinstance(dwpoi__zbtmm, types.Array) and dwpoi__zbtmm
        .dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for dwpoi__zbtmm in typ.data)
    if byss__silb:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        oqvk__haqe = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            oqvk__haqe, i) for i in range(1, oqvk__haqe.type.count)], lir.
            IntType(64))
    nbmx__kvq, data_tup, null_bitmap_ptr = construct_struct_array(c.context,
        c.builder, typ, n_structs, n_elems, c)
    if byss__silb:
        bozmc__cewzv, xgdrx__dsoby, ppzt__dliy = _get_C_API_ptrs(c,
            data_tup, typ.data, typ.names)
        bhzm__qffbl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        zhsl__miyb = cgutils.get_or_insert_function(c.builder.module,
            bhzm__qffbl, name='struct_array_from_sequence')
        c.builder.call(zhsl__miyb, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(bozmc__cewzv, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(xgdrx__dsoby,
            lir.IntType(8).as_pointer()), c.builder.bitcast(ppzt__dliy, lir
            .IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    kqlbj__wandz = c.context.make_helper(c.builder, typ)
    kqlbj__wandz.meminfo = nbmx__kvq
    prbsi__abeu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kqlbj__wandz._getvalue(), is_error=prbsi__abeu)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    sewea__zqh = context.insert_const_string(builder.module, 'pandas')
    mudw__rxcl = c.pyapi.import_module_noblock(sewea__zqh)
    otl__eyua = c.pyapi.object_getattr_string(mudw__rxcl, 'NA')
    with cgutils.for_range(builder, n_structs) as zoid__bcakl:
        vuv__hgxyy = zoid__bcakl.index
        fyehk__soyyv = seq_getitem(builder, context, val, vuv__hgxyy)
        set_bitmap_bit(builder, null_bitmap_ptr, vuv__hgxyy, 0)
        for nml__jfmo in range(len(typ.data)):
            arr_typ = typ.data[nml__jfmo]
            data_arr = builder.extract_value(data_tup, nml__jfmo)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            ehehz__rnwi, dlcd__oxi = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, vuv__hgxyy])
        ffi__eoad = is_na_value(builder, context, fyehk__soyyv, otl__eyua)
        dfi__lulo = builder.icmp_unsigned('!=', ffi__eoad, lir.Constant(
            ffi__eoad.type, 1))
        with builder.if_then(dfi__lulo):
            set_bitmap_bit(builder, null_bitmap_ptr, vuv__hgxyy, 1)
            for nml__jfmo in range(len(typ.data)):
                arr_typ = typ.data[nml__jfmo]
                if is_tuple_array:
                    vnbn__zoikf = c.pyapi.tuple_getitem(fyehk__soyyv, nml__jfmo
                        )
                else:
                    vnbn__zoikf = c.pyapi.dict_getitem_string(fyehk__soyyv,
                        typ.names[nml__jfmo])
                ffi__eoad = is_na_value(builder, context, vnbn__zoikf,
                    otl__eyua)
                dfi__lulo = builder.icmp_unsigned('!=', ffi__eoad, lir.
                    Constant(ffi__eoad.type, 1))
                with builder.if_then(dfi__lulo):
                    vnbn__zoikf = to_arr_obj_if_list_obj(c, context,
                        builder, vnbn__zoikf, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        vnbn__zoikf).value
                    data_arr = builder.extract_value(data_tup, nml__jfmo)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    ehehz__rnwi, dlcd__oxi = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, vuv__hgxyy, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(fyehk__soyyv)
    c.pyapi.decref(mudw__rxcl)
    c.pyapi.decref(otl__eyua)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    kqlbj__wandz = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    maq__ipws = context.nrt.meminfo_data(builder, kqlbj__wandz.meminfo)
    prtq__qboge = builder.bitcast(maq__ipws, context.get_value_type(
        payload_type).as_pointer())
    ddj__nsucb = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(prtq__qboge))
    return ddj__nsucb


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    ddj__nsucb = _get_struct_arr_payload(c.context, c.builder, typ, val)
    ehehz__rnwi, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), ddj__nsucb.null_bitmap).data
    byss__silb = all(isinstance(dwpoi__zbtmm, types.Array) and dwpoi__zbtmm
        .dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for dwpoi__zbtmm in typ.data)
    if byss__silb:
        bozmc__cewzv, xgdrx__dsoby, ppzt__dliy = _get_C_API_ptrs(c,
            ddj__nsucb.data, typ.data, typ.names)
        bhzm__qffbl = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        kpiq__jrs = cgutils.get_or_insert_function(c.builder.module,
            bhzm__qffbl, name='np_array_from_struct_array')
        arr = c.builder.call(kpiq__jrs, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(bozmc__cewzv,
            lir.IntType(8).as_pointer()), null_bitmap_ptr, c.builder.
            bitcast(xgdrx__dsoby, lir.IntType(8).as_pointer()), c.builder.
            bitcast(ppzt__dliy, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, ddj__nsucb.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    sewea__zqh = context.insert_const_string(builder.module, 'numpy')
    uph__vgu = c.pyapi.import_module_noblock(sewea__zqh)
    onc__ayfi = c.pyapi.object_getattr_string(uph__vgu, 'object_')
    mled__wbzrf = c.pyapi.long_from_longlong(length)
    bwpu__frcjb = c.pyapi.call_method(uph__vgu, 'ndarray', (mled__wbzrf,
        onc__ayfi))
    mutov__wne = c.pyapi.object_getattr_string(uph__vgu, 'nan')
    with cgutils.for_range(builder, length) as zoid__bcakl:
        vuv__hgxyy = zoid__bcakl.index
        pyarray_setitem(builder, context, bwpu__frcjb, vuv__hgxyy, mutov__wne)
        grv__aaw = get_bitmap_bit(builder, null_bitmap_ptr, vuv__hgxyy)
        rcpiq__muy = builder.icmp_unsigned('!=', grv__aaw, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(rcpiq__muy):
            if is_tuple_array:
                fyehk__soyyv = c.pyapi.tuple_new(len(typ.data))
            else:
                fyehk__soyyv = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(mutov__wne)
                    c.pyapi.tuple_setitem(fyehk__soyyv, i, mutov__wne)
                else:
                    c.pyapi.dict_setitem_string(fyehk__soyyv, typ.names[i],
                        mutov__wne)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                ehehz__rnwi, uxd__bpj = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, vuv__hgxyy])
                with builder.if_then(uxd__bpj):
                    ehehz__rnwi, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, vuv__hgxyy])
                    mwvs__dwxu = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(fyehk__soyyv, i, mwvs__dwxu)
                    else:
                        c.pyapi.dict_setitem_string(fyehk__soyyv, typ.names
                            [i], mwvs__dwxu)
                        c.pyapi.decref(mwvs__dwxu)
            pyarray_setitem(builder, context, bwpu__frcjb, vuv__hgxyy,
                fyehk__soyyv)
            c.pyapi.decref(fyehk__soyyv)
    c.pyapi.decref(uph__vgu)
    c.pyapi.decref(onc__ayfi)
    c.pyapi.decref(mled__wbzrf)
    c.pyapi.decref(mutov__wne)
    return bwpu__frcjb


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    khy__cbh = bodo.utils.transform.get_type_alloc_counts(struct_arr_type) - 1
    if khy__cbh == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for twhl__bne in range(khy__cbh)])
    elif nested_counts_type.count < khy__cbh:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for twhl__bne in range(
            khy__cbh - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(dwpoi__zbtmm) for dwpoi__zbtmm in
            names_typ.types)
    zqtp__yqjyh = tuple(dwpoi__zbtmm.instance_type for dwpoi__zbtmm in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(zqtp__yqjyh, names)

    def codegen(context, builder, sig, args):
        rnr__cpnda, nested_counts, twhl__bne, twhl__bne = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        nbmx__kvq, twhl__bne, twhl__bne = construct_struct_array(context,
            builder, struct_arr_type, rnr__cpnda, nested_counts)
        kqlbj__wandz = context.make_helper(builder, struct_arr_type)
        kqlbj__wandz.meminfo = nbmx__kvq
        return kqlbj__wandz._getvalue()
    return struct_arr_type(num_structs_typ, nested_counts_typ, dtypes_typ,
        names_typ), codegen


def pre_alloc_struct_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_struct_arr_ext_pre_alloc_struct_array
    ) = pre_alloc_struct_array_equiv


class StructType(types.Type):

    def __init__(self, data, names):
        assert isinstance(data, tuple) and len(data) > 0
        assert isinstance(names, tuple) and all(isinstance(puf__jhhh, str) for
            puf__jhhh in names) and len(names) == len(data)
        self.data = data
        self.names = names
        super(StructType, self).__init__(name='StructType({}, {})'.format(
            data, names))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple)
        self.data = data
        super(StructPayloadType, self).__init__(name=
            'StructPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructPayloadType)
class StructPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mncyl__yww = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, mncyl__yww)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        mncyl__yww = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, mncyl__yww)


def define_struct_dtor(context, builder, struct_type, payload_type):
    ymra__dchfr = builder.module
    bhzm__qffbl = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    zhsl__miyb = cgutils.get_or_insert_function(ymra__dchfr, bhzm__qffbl,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not zhsl__miyb.is_declaration:
        return zhsl__miyb
    zhsl__miyb.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(zhsl__miyb.append_basic_block())
    tkzor__hkoc = zhsl__miyb.args[0]
    urogi__znjh = context.get_value_type(payload_type).as_pointer()
    lav__pjo = builder.bitcast(tkzor__hkoc, urogi__znjh)
    ddj__nsucb = context.make_helper(builder, payload_type, ref=lav__pjo)
    for i in range(len(struct_type.data)):
        uvrup__ail = builder.extract_value(ddj__nsucb.null_bitmap, i)
        rcpiq__muy = builder.icmp_unsigned('==', uvrup__ail, lir.Constant(
            uvrup__ail.type, 1))
        with builder.if_then(rcpiq__muy):
            val = builder.extract_value(ddj__nsucb.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return zhsl__miyb


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    maq__ipws = context.nrt.meminfo_data(builder, struct.meminfo)
    prtq__qboge = builder.bitcast(maq__ipws, context.get_value_type(
        payload_type).as_pointer())
    ddj__nsucb = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(prtq__qboge))
    return ddj__nsucb, prtq__qboge


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    sewea__zqh = context.insert_const_string(builder.module, 'pandas')
    mudw__rxcl = c.pyapi.import_module_noblock(sewea__zqh)
    otl__eyua = c.pyapi.object_getattr_string(mudw__rxcl, 'NA')
    kogvj__gcdmq = []
    nulls = []
    for i, dwpoi__zbtmm in enumerate(typ.data):
        mwvs__dwxu = c.pyapi.dict_getitem_string(val, typ.names[i])
        cluyd__qlcg = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        xje__mrru = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(dwpoi__zbtmm)))
        ffi__eoad = is_na_value(builder, context, mwvs__dwxu, otl__eyua)
        rcpiq__muy = builder.icmp_unsigned('!=', ffi__eoad, lir.Constant(
            ffi__eoad.type, 1))
        with builder.if_then(rcpiq__muy):
            builder.store(context.get_constant(types.uint8, 1), cluyd__qlcg)
            field_val = c.pyapi.to_native_value(dwpoi__zbtmm, mwvs__dwxu).value
            builder.store(field_val, xje__mrru)
        kogvj__gcdmq.append(builder.load(xje__mrru))
        nulls.append(builder.load(cluyd__qlcg))
    c.pyapi.decref(mudw__rxcl)
    c.pyapi.decref(otl__eyua)
    nbmx__kvq = construct_struct(context, builder, typ, kogvj__gcdmq, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = nbmx__kvq
    prbsi__abeu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=prbsi__abeu)


@box(StructType)
def box_struct(typ, val, c):
    boigb__gkx = c.pyapi.dict_new(len(typ.data))
    ddj__nsucb, twhl__bne = _get_struct_payload(c.context, c.builder, typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(boigb__gkx, typ.names[i], c.pyapi.
            borrow_none())
        uvrup__ail = c.builder.extract_value(ddj__nsucb.null_bitmap, i)
        rcpiq__muy = c.builder.icmp_unsigned('==', uvrup__ail, lir.Constant
            (uvrup__ail.type, 1))
        with c.builder.if_then(rcpiq__muy):
            cutf__ogvot = c.builder.extract_value(ddj__nsucb.data, i)
            c.context.nrt.incref(c.builder, val_typ, cutf__ogvot)
            vnbn__zoikf = c.pyapi.from_native_value(val_typ, cutf__ogvot, c
                .env_manager)
            c.pyapi.dict_setitem_string(boigb__gkx, typ.names[i], vnbn__zoikf)
            c.pyapi.decref(vnbn__zoikf)
    c.context.nrt.decref(c.builder, typ, val)
    return boigb__gkx


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(dwpoi__zbtmm) for dwpoi__zbtmm in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, noyhr__oriym = args
        payload_type = StructPayloadType(struct_type.data)
        lotb__tdzn = context.get_value_type(payload_type)
        cuw__ztyv = context.get_abi_sizeof(lotb__tdzn)
        jpe__xnv = define_struct_dtor(context, builder, struct_type,
            payload_type)
        nbmx__kvq = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, cuw__ztyv), jpe__xnv)
        maq__ipws = context.nrt.meminfo_data(builder, nbmx__kvq)
        prtq__qboge = builder.bitcast(maq__ipws, lotb__tdzn.as_pointer())
        ddj__nsucb = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        ddj__nsucb.data = data
        ddj__nsucb.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for twhl__bne in range(len(
            data_typ.types))])
        builder.store(ddj__nsucb._getvalue(), prtq__qboge)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = nbmx__kvq
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        ddj__nsucb, twhl__bne = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ddj__nsucb.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        ddj__nsucb, twhl__bne = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ddj__nsucb.null_bitmap)
    hced__dkfp = types.UniTuple(types.int8, len(struct_typ.data))
    return hced__dkfp(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, twhl__bne, val = args
        ddj__nsucb, prtq__qboge = _get_struct_payload(context, builder,
            struct_typ, struct)
        nqigl__orvb = ddj__nsucb.data
        wfixs__pfly = builder.insert_value(nqigl__orvb, val, field_ind)
        fqqu__kuj = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, fqqu__kuj, nqigl__orvb)
        context.nrt.incref(builder, fqqu__kuj, wfixs__pfly)
        ddj__nsucb.data = wfixs__pfly
        builder.store(ddj__nsucb._getvalue(), prtq__qboge)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    nqxxj__vun = get_overload_const_str(ind)
    if nqxxj__vun not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            nqxxj__vun, struct))
    return struct.names.index(nqxxj__vun)


def is_field_value_null(s, field_name):
    pass


@overload(is_field_value_null, no_unliteral=True)
def overload_is_field_value_null(s, field_name):
    field_ind = _get_struct_field_ind(s, field_name, 'element access (getitem)'
        )
    return lambda s, field_name: get_struct_null_bitmap(s)[field_ind] == 0


@overload(operator.getitem, no_unliteral=True)
def struct_getitem(struct, ind):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'element access (getitem)')
    return lambda struct, ind: get_struct_data(struct)[field_ind]


@overload(operator.setitem, no_unliteral=True)
def struct_setitem(struct, ind, val):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'item assignment (setitem)')
    field_typ = struct.data[field_ind]
    return lambda struct, ind, val: set_struct_data(struct, field_ind,
        _cast(val, field_typ))


@overload(len, no_unliteral=True)
def overload_struct_arr_len(struct):
    if isinstance(struct, StructType):
        num_fields = len(struct.data)
        return lambda struct: num_fields


def construct_struct(context, builder, struct_type, values, nulls):
    payload_type = StructPayloadType(struct_type.data)
    lotb__tdzn = context.get_value_type(payload_type)
    cuw__ztyv = context.get_abi_sizeof(lotb__tdzn)
    jpe__xnv = define_struct_dtor(context, builder, struct_type, payload_type)
    nbmx__kvq = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, cuw__ztyv), jpe__xnv)
    maq__ipws = context.nrt.meminfo_data(builder, nbmx__kvq)
    prtq__qboge = builder.bitcast(maq__ipws, lotb__tdzn.as_pointer())
    ddj__nsucb = cgutils.create_struct_proxy(payload_type)(context, builder)
    ddj__nsucb.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    ddj__nsucb.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(ddj__nsucb._getvalue(), prtq__qboge)
    return nbmx__kvq


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    cxufi__ludm = tuple(d.dtype for d in struct_arr_typ.data)
    cqpo__azk = StructType(cxufi__ludm, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        bou__jjs, ind = args
        ddj__nsucb = _get_struct_arr_payload(context, builder,
            struct_arr_typ, bou__jjs)
        kogvj__gcdmq = []
        yufi__rotv = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            vmkhi__qnf = builder.extract_value(ddj__nsucb.data, i)
            uyhi__jgxup = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [vmkhi__qnf,
                ind])
            yufi__rotv.append(uyhi__jgxup)
            miro__nqe = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            rcpiq__muy = builder.icmp_unsigned('==', uyhi__jgxup, lir.
                Constant(uyhi__jgxup.type, 1))
            with builder.if_then(rcpiq__muy):
                chrfp__gyc = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    vmkhi__qnf, ind])
                builder.store(chrfp__gyc, miro__nqe)
            kogvj__gcdmq.append(builder.load(miro__nqe))
        if isinstance(cqpo__azk, types.DictType):
            kijb__kwvz = [context.insert_const_string(builder.module,
                bqxs__vqs) for bqxs__vqs in struct_arr_typ.names]
            nujb__mhxr = cgutils.pack_array(builder, kogvj__gcdmq)
            qcoi__bqb = cgutils.pack_array(builder, kijb__kwvz)

            def impl(names, vals):
                d = {}
                for i, bqxs__vqs in enumerate(names):
                    d[bqxs__vqs] = vals[i]
                return d
            djuwr__jpptb = context.compile_internal(builder, impl,
                cqpo__azk(types.Tuple(tuple(types.StringLiteral(bqxs__vqs) for
                bqxs__vqs in struct_arr_typ.names)), types.Tuple(
                cxufi__ludm)), [qcoi__bqb, nujb__mhxr])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                cxufi__ludm), nujb__mhxr)
            return djuwr__jpptb
        nbmx__kvq = construct_struct(context, builder, cqpo__azk,
            kogvj__gcdmq, yufi__rotv)
        struct = context.make_helper(builder, cqpo__azk)
        struct.meminfo = nbmx__kvq
        return struct._getvalue()
    return cqpo__azk(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ddj__nsucb = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ddj__nsucb.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ddj__nsucb = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ddj__nsucb.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(dwpoi__zbtmm) for dwpoi__zbtmm in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, ags__uzb, noyhr__oriym = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        lotb__tdzn = context.get_value_type(payload_type)
        cuw__ztyv = context.get_abi_sizeof(lotb__tdzn)
        jpe__xnv = define_struct_arr_dtor(context, builder, struct_arr_type,
            payload_type)
        nbmx__kvq = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, cuw__ztyv), jpe__xnv)
        maq__ipws = context.nrt.meminfo_data(builder, nbmx__kvq)
        prtq__qboge = builder.bitcast(maq__ipws, lotb__tdzn.as_pointer())
        ddj__nsucb = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        ddj__nsucb.data = data
        ddj__nsucb.null_bitmap = ags__uzb
        builder.store(ddj__nsucb._getvalue(), prtq__qboge)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, ags__uzb)
        kqlbj__wandz = context.make_helper(builder, struct_arr_type)
        kqlbj__wandz.meminfo = nbmx__kvq
        return kqlbj__wandz._getvalue()
    return struct_arr_type(data_typ, null_bitmap_typ, names_typ), codegen


@overload(operator.getitem, no_unliteral=True)
def struct_arr_getitem(arr, ind):
    if not isinstance(arr, StructArrayType):
        return
    if isinstance(ind, types.Integer):

        def struct_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            return struct_array_get_struct(arr, ind)
        return struct_arr_getitem_impl
    ordk__pjdt = len(arr.data)
    klavw__rwmfg = 'def impl(arr, ind):\n'
    klavw__rwmfg += '  data = get_data(arr)\n'
    klavw__rwmfg += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        klavw__rwmfg += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        klavw__rwmfg += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        klavw__rwmfg += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    klavw__rwmfg += (
        '  return init_struct_arr(({},), out_null_bitmap, ({},))\n'.format(
        ', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for i in
        range(ordk__pjdt)), ', '.join("'{}'".format(bqxs__vqs) for
        bqxs__vqs in arr.names)))
    hqdm__fbzi = {}
    exec(klavw__rwmfg, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, hqdm__fbzi)
    impl = hqdm__fbzi['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        ordk__pjdt = len(arr.data)
        klavw__rwmfg = 'def impl(arr, ind, val):\n'
        klavw__rwmfg += '  data = get_data(arr)\n'
        klavw__rwmfg += '  null_bitmap = get_null_bitmap(arr)\n'
        klavw__rwmfg += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(ordk__pjdt):
            if isinstance(val, StructType):
                klavw__rwmfg += ("  if is_field_value_null(val, '{}'):\n".
                    format(arr.names[i]))
                klavw__rwmfg += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                klavw__rwmfg += '  else:\n'
                klavw__rwmfg += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                klavw__rwmfg += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        hqdm__fbzi = {}
        exec(klavw__rwmfg, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, hqdm__fbzi)
        impl = hqdm__fbzi['impl']
        return impl
    if isinstance(ind, types.SliceType):
        ordk__pjdt = len(arr.data)
        klavw__rwmfg = 'def impl(arr, ind, val):\n'
        klavw__rwmfg += '  data = get_data(arr)\n'
        klavw__rwmfg += '  null_bitmap = get_null_bitmap(arr)\n'
        klavw__rwmfg += '  val_data = get_data(val)\n'
        klavw__rwmfg += '  val_null_bitmap = get_null_bitmap(val)\n'
        klavw__rwmfg += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(ordk__pjdt):
            klavw__rwmfg += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        hqdm__fbzi = {}
        exec(klavw__rwmfg, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, hqdm__fbzi)
        impl = hqdm__fbzi['impl']
        return impl
    raise BodoError(
        'only setitem with scalar/slice index is currently supported for struct arrays'
        )


@overload(len, no_unliteral=True)
def overload_struct_arr_len(A):
    if isinstance(A, StructArrayType):
        return lambda A: len(get_data(A)[0])


@overload_attribute(StructArrayType, 'shape')
def overload_struct_arr_shape(A):
    return lambda A: (len(get_data(A)[0]),)


@overload_attribute(StructArrayType, 'dtype')
def overload_struct_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(StructArrayType, 'ndim')
def overload_struct_arr_ndim(A):
    return lambda A: 1


@overload_attribute(StructArrayType, 'nbytes')
def overload_struct_arr_nbytes(A):
    klavw__rwmfg = 'def impl(A):\n'
    klavw__rwmfg += '  total_nbytes = 0\n'
    klavw__rwmfg += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        klavw__rwmfg += f'  total_nbytes += data[{i}].nbytes\n'
    klavw__rwmfg += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    klavw__rwmfg += '  return total_nbytes\n'
    hqdm__fbzi = {}
    exec(klavw__rwmfg, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, hqdm__fbzi)
    impl = hqdm__fbzi['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        ags__uzb = get_null_bitmap(A)
        mop__luy = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        fblii__qtma = ags__uzb.copy()
        return init_struct_arr(mop__luy, fblii__qtma, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(puf__jhhh.copy() for puf__jhhh in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    vkm__itrw = arrs.count
    klavw__rwmfg = 'def f(arrs):\n'
    klavw__rwmfg += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(vkm__itrw)))
    hqdm__fbzi = {}
    exec(klavw__rwmfg, {}, hqdm__fbzi)
    impl = hqdm__fbzi['f']
    return impl
