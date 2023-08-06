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
            .utils.is_array_typ(sqmd__xyls, False) for sqmd__xyls in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(sqmd__xyls,
                str) for sqmd__xyls in names) and len(names) == len(data)
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
        return StructType(tuple(scvbr__rfgvf.dtype for scvbr__rfgvf in self
            .data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(sqmd__xyls) for sqmd__xyls in d.keys())
        data = tuple(dtype_to_array_type(scvbr__rfgvf) for scvbr__rfgvf in
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
            is_array_typ(sqmd__xyls, False) for sqmd__xyls in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rhhj__fwdcm = [('data', types.BaseTuple.from_types(fe_type.data)),
            ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, rhhj__fwdcm)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        rhhj__fwdcm = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, rhhj__fwdcm)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    bsu__fvwtu = builder.module
    hnv__mcwgv = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    qohw__omzz = cgutils.get_or_insert_function(bsu__fvwtu, hnv__mcwgv,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not qohw__omzz.is_declaration:
        return qohw__omzz
    qohw__omzz.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(qohw__omzz.append_basic_block())
    olx__nkzud = qohw__omzz.args[0]
    xzxe__phgqz = context.get_value_type(payload_type).as_pointer()
    bsng__rbq = builder.bitcast(olx__nkzud, xzxe__phgqz)
    ypkt__ngn = context.make_helper(builder, payload_type, ref=bsng__rbq)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), ypkt__ngn.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), ypkt__ngn
        .null_bitmap)
    builder.ret_void()
    return qohw__omzz


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    uxam__jor = context.get_value_type(payload_type)
    fdxc__qea = context.get_abi_sizeof(uxam__jor)
    qeub__mvqqd = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    hdsi__qhr = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, fdxc__qea), qeub__mvqqd)
    khk__bgwoi = context.nrt.meminfo_data(builder, hdsi__qhr)
    rae__xgp = builder.bitcast(khk__bgwoi, uxam__jor.as_pointer())
    ypkt__ngn = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    wxzyd__dyrdy = 0
    for arr_typ in struct_arr_type.data:
        jgog__mxir = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        pry__ere = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(wxzyd__dyrdy, 
            wxzyd__dyrdy + jgog__mxir)])
        arr = gen_allocate_array(context, builder, arr_typ, pry__ere, c)
        arrs.append(arr)
        wxzyd__dyrdy += jgog__mxir
    ypkt__ngn.data = cgutils.pack_array(builder, arrs) if types.is_homogeneous(
        *struct_arr_type.data) else cgutils.pack_struct(builder, arrs)
    gak__zmb = builder.udiv(builder.add(n_structs, lir.Constant(lir.IntType
        (64), 7)), lir.Constant(lir.IntType(64), 8))
    kdiy__own = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [gak__zmb])
    null_bitmap_ptr = kdiy__own.data
    ypkt__ngn.null_bitmap = kdiy__own._getvalue()
    builder.store(ypkt__ngn._getvalue(), rae__xgp)
    return hdsi__qhr, ypkt__ngn.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    nef__mqc = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        jnm__luz = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            jnm__luz)
        nef__mqc.append(arr.data)
    pgt__pvmp = cgutils.pack_array(c.builder, nef__mqc
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, nef__mqc)
    vypbm__lwsq = cgutils.alloca_once_value(c.builder, pgt__pvmp)
    trv__hvh = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(sqmd__xyls.dtype)) for sqmd__xyls in data_typ]
    zdkb__lrkc = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, trv__hvh))
    kpfj__pifix = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, sqmd__xyls) for sqmd__xyls in
        names])
    gwnz__joy = cgutils.alloca_once_value(c.builder, kpfj__pifix)
    return vypbm__lwsq, zdkb__lrkc, gwnz__joy


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    kxxcf__gbkv = all(isinstance(scvbr__rfgvf, types.Array) and 
        scvbr__rfgvf.dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for scvbr__rfgvf in typ.data)
    if kxxcf__gbkv:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        fgcs__ehmk = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            fgcs__ehmk, i) for i in range(1, fgcs__ehmk.type.count)], lir.
            IntType(64))
    hdsi__qhr, data_tup, null_bitmap_ptr = construct_struct_array(c.context,
        c.builder, typ, n_structs, n_elems, c)
    if kxxcf__gbkv:
        vypbm__lwsq, zdkb__lrkc, gwnz__joy = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        hnv__mcwgv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        qohw__omzz = cgutils.get_or_insert_function(c.builder.module,
            hnv__mcwgv, name='struct_array_from_sequence')
        c.builder.call(qohw__omzz, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(vypbm__lwsq, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(zdkb__lrkc,
            lir.IntType(8).as_pointer()), c.builder.bitcast(gwnz__joy, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    qpdgu__ked = c.context.make_helper(c.builder, typ)
    qpdgu__ked.meminfo = hdsi__qhr
    lig__cwm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qpdgu__ked._getvalue(), is_error=lig__cwm)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    oewsj__vrkob = context.insert_const_string(builder.module, 'pandas')
    lyklt__wprp = c.pyapi.import_module_noblock(oewsj__vrkob)
    tdo__qhu = c.pyapi.object_getattr_string(lyklt__wprp, 'NA')
    with cgutils.for_range(builder, n_structs) as jre__lauv:
        quk__neilx = jre__lauv.index
        nwaul__txh = seq_getitem(builder, context, val, quk__neilx)
        set_bitmap_bit(builder, null_bitmap_ptr, quk__neilx, 0)
        for zzu__kfowg in range(len(typ.data)):
            arr_typ = typ.data[zzu__kfowg]
            data_arr = builder.extract_value(data_tup, zzu__kfowg)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            hjv__ddng, fwje__fsdy = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, quk__neilx])
        udvbp__xswc = is_na_value(builder, context, nwaul__txh, tdo__qhu)
        cbi__vwh = builder.icmp_unsigned('!=', udvbp__xswc, lir.Constant(
            udvbp__xswc.type, 1))
        with builder.if_then(cbi__vwh):
            set_bitmap_bit(builder, null_bitmap_ptr, quk__neilx, 1)
            for zzu__kfowg in range(len(typ.data)):
                arr_typ = typ.data[zzu__kfowg]
                if is_tuple_array:
                    mfr__wglsd = c.pyapi.tuple_getitem(nwaul__txh, zzu__kfowg)
                else:
                    mfr__wglsd = c.pyapi.dict_getitem_string(nwaul__txh,
                        typ.names[zzu__kfowg])
                udvbp__xswc = is_na_value(builder, context, mfr__wglsd,
                    tdo__qhu)
                cbi__vwh = builder.icmp_unsigned('!=', udvbp__xswc, lir.
                    Constant(udvbp__xswc.type, 1))
                with builder.if_then(cbi__vwh):
                    mfr__wglsd = to_arr_obj_if_list_obj(c, context, builder,
                        mfr__wglsd, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        mfr__wglsd).value
                    data_arr = builder.extract_value(data_tup, zzu__kfowg)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    hjv__ddng, fwje__fsdy = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, quk__neilx, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(nwaul__txh)
    c.pyapi.decref(lyklt__wprp)
    c.pyapi.decref(tdo__qhu)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    qpdgu__ked = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    khk__bgwoi = context.nrt.meminfo_data(builder, qpdgu__ked.meminfo)
    rae__xgp = builder.bitcast(khk__bgwoi, context.get_value_type(
        payload_type).as_pointer())
    ypkt__ngn = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(rae__xgp))
    return ypkt__ngn


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    ypkt__ngn = _get_struct_arr_payload(c.context, c.builder, typ, val)
    hjv__ddng, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64
        (typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), ypkt__ngn.null_bitmap).data
    kxxcf__gbkv = all(isinstance(scvbr__rfgvf, types.Array) and 
        scvbr__rfgvf.dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for scvbr__rfgvf in typ.data)
    if kxxcf__gbkv:
        vypbm__lwsq, zdkb__lrkc, gwnz__joy = _get_C_API_ptrs(c, ypkt__ngn.
            data, typ.data, typ.names)
        hnv__mcwgv = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        psx__fsjvx = cgutils.get_or_insert_function(c.builder.module,
            hnv__mcwgv, name='np_array_from_struct_array')
        arr = c.builder.call(psx__fsjvx, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(vypbm__lwsq, lir
            .IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            zdkb__lrkc, lir.IntType(8).as_pointer()), c.builder.bitcast(
            gwnz__joy, lir.IntType(8).as_pointer()), c.context.get_constant
            (types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, ypkt__ngn.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    oewsj__vrkob = context.insert_const_string(builder.module, 'numpy')
    etalj__joaab = c.pyapi.import_module_noblock(oewsj__vrkob)
    fymqy__xct = c.pyapi.object_getattr_string(etalj__joaab, 'object_')
    ewfko__vep = c.pyapi.long_from_longlong(length)
    gkmg__sboql = c.pyapi.call_method(etalj__joaab, 'ndarray', (ewfko__vep,
        fymqy__xct))
    mhb__rfjrj = c.pyapi.object_getattr_string(etalj__joaab, 'nan')
    with cgutils.for_range(builder, length) as jre__lauv:
        quk__neilx = jre__lauv.index
        pyarray_setitem(builder, context, gkmg__sboql, quk__neilx, mhb__rfjrj)
        ekjyd__yxsjq = get_bitmap_bit(builder, null_bitmap_ptr, quk__neilx)
        mogq__gyuig = builder.icmp_unsigned('!=', ekjyd__yxsjq, lir.
            Constant(lir.IntType(8), 0))
        with builder.if_then(mogq__gyuig):
            if is_tuple_array:
                nwaul__txh = c.pyapi.tuple_new(len(typ.data))
            else:
                nwaul__txh = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(mhb__rfjrj)
                    c.pyapi.tuple_setitem(nwaul__txh, i, mhb__rfjrj)
                else:
                    c.pyapi.dict_setitem_string(nwaul__txh, typ.names[i],
                        mhb__rfjrj)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                hjv__ddng, eiv__fwwmh = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, quk__neilx])
                with builder.if_then(eiv__fwwmh):
                    hjv__ddng, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, quk__neilx])
                    hecne__yitsw = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(nwaul__txh, i, hecne__yitsw)
                    else:
                        c.pyapi.dict_setitem_string(nwaul__txh, typ.names[i
                            ], hecne__yitsw)
                        c.pyapi.decref(hecne__yitsw)
            pyarray_setitem(builder, context, gkmg__sboql, quk__neilx,
                nwaul__txh)
            c.pyapi.decref(nwaul__txh)
    c.pyapi.decref(etalj__joaab)
    c.pyapi.decref(fymqy__xct)
    c.pyapi.decref(ewfko__vep)
    c.pyapi.decref(mhb__rfjrj)
    return gkmg__sboql


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    wpn__rbuk = bodo.utils.transform.get_type_alloc_counts(struct_arr_type) - 1
    if wpn__rbuk == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for zac__mbos in range(wpn__rbuk)])
    elif nested_counts_type.count < wpn__rbuk:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for zac__mbos in range(
            wpn__rbuk - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(scvbr__rfgvf) for scvbr__rfgvf in
            names_typ.types)
    kqzv__kog = tuple(scvbr__rfgvf.instance_type for scvbr__rfgvf in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(kqzv__kog, names)

    def codegen(context, builder, sig, args):
        ruya__uml, nested_counts, zac__mbos, zac__mbos = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        hdsi__qhr, zac__mbos, zac__mbos = construct_struct_array(context,
            builder, struct_arr_type, ruya__uml, nested_counts)
        qpdgu__ked = context.make_helper(builder, struct_arr_type)
        qpdgu__ked.meminfo = hdsi__qhr
        return qpdgu__ked._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(sqmd__xyls, str) for
            sqmd__xyls in names) and len(names) == len(data)
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
        rhhj__fwdcm = [('data', types.BaseTuple.from_types(fe_type.data)),
            ('null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, rhhj__fwdcm)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        rhhj__fwdcm = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, rhhj__fwdcm)


def define_struct_dtor(context, builder, struct_type, payload_type):
    bsu__fvwtu = builder.module
    hnv__mcwgv = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    qohw__omzz = cgutils.get_or_insert_function(bsu__fvwtu, hnv__mcwgv,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not qohw__omzz.is_declaration:
        return qohw__omzz
    qohw__omzz.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(qohw__omzz.append_basic_block())
    olx__nkzud = qohw__omzz.args[0]
    xzxe__phgqz = context.get_value_type(payload_type).as_pointer()
    bsng__rbq = builder.bitcast(olx__nkzud, xzxe__phgqz)
    ypkt__ngn = context.make_helper(builder, payload_type, ref=bsng__rbq)
    for i in range(len(struct_type.data)):
        scxc__ofsc = builder.extract_value(ypkt__ngn.null_bitmap, i)
        mogq__gyuig = builder.icmp_unsigned('==', scxc__ofsc, lir.Constant(
            scxc__ofsc.type, 1))
        with builder.if_then(mogq__gyuig):
            val = builder.extract_value(ypkt__ngn.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return qohw__omzz


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    khk__bgwoi = context.nrt.meminfo_data(builder, struct.meminfo)
    rae__xgp = builder.bitcast(khk__bgwoi, context.get_value_type(
        payload_type).as_pointer())
    ypkt__ngn = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(rae__xgp))
    return ypkt__ngn, rae__xgp


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    oewsj__vrkob = context.insert_const_string(builder.module, 'pandas')
    lyklt__wprp = c.pyapi.import_module_noblock(oewsj__vrkob)
    tdo__qhu = c.pyapi.object_getattr_string(lyklt__wprp, 'NA')
    gora__xxbf = []
    nulls = []
    for i, scvbr__rfgvf in enumerate(typ.data):
        hecne__yitsw = c.pyapi.dict_getitem_string(val, typ.names[i])
        tluf__mnv = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        efo__kjp = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(scvbr__rfgvf)))
        udvbp__xswc = is_na_value(builder, context, hecne__yitsw, tdo__qhu)
        mogq__gyuig = builder.icmp_unsigned('!=', udvbp__xswc, lir.Constant
            (udvbp__xswc.type, 1))
        with builder.if_then(mogq__gyuig):
            builder.store(context.get_constant(types.uint8, 1), tluf__mnv)
            field_val = c.pyapi.to_native_value(scvbr__rfgvf, hecne__yitsw
                ).value
            builder.store(field_val, efo__kjp)
        gora__xxbf.append(builder.load(efo__kjp))
        nulls.append(builder.load(tluf__mnv))
    c.pyapi.decref(lyklt__wprp)
    c.pyapi.decref(tdo__qhu)
    hdsi__qhr = construct_struct(context, builder, typ, gora__xxbf, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = hdsi__qhr
    lig__cwm = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=lig__cwm)


@box(StructType)
def box_struct(typ, val, c):
    ashx__llgmp = c.pyapi.dict_new(len(typ.data))
    ypkt__ngn, zac__mbos = _get_struct_payload(c.context, c.builder, typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(ashx__llgmp, typ.names[i], c.pyapi.
            borrow_none())
        scxc__ofsc = c.builder.extract_value(ypkt__ngn.null_bitmap, i)
        mogq__gyuig = c.builder.icmp_unsigned('==', scxc__ofsc, lir.
            Constant(scxc__ofsc.type, 1))
        with c.builder.if_then(mogq__gyuig):
            rsho__mpijn = c.builder.extract_value(ypkt__ngn.data, i)
            c.context.nrt.incref(c.builder, val_typ, rsho__mpijn)
            mfr__wglsd = c.pyapi.from_native_value(val_typ, rsho__mpijn, c.
                env_manager)
            c.pyapi.dict_setitem_string(ashx__llgmp, typ.names[i], mfr__wglsd)
            c.pyapi.decref(mfr__wglsd)
    c.context.nrt.decref(c.builder, typ, val)
    return ashx__llgmp


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(scvbr__rfgvf) for scvbr__rfgvf in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, mva__dhsds = args
        payload_type = StructPayloadType(struct_type.data)
        uxam__jor = context.get_value_type(payload_type)
        fdxc__qea = context.get_abi_sizeof(uxam__jor)
        qeub__mvqqd = define_struct_dtor(context, builder, struct_type,
            payload_type)
        hdsi__qhr = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, fdxc__qea), qeub__mvqqd)
        khk__bgwoi = context.nrt.meminfo_data(builder, hdsi__qhr)
        rae__xgp = builder.bitcast(khk__bgwoi, uxam__jor.as_pointer())
        ypkt__ngn = cgutils.create_struct_proxy(payload_type)(context, builder)
        ypkt__ngn.data = data
        ypkt__ngn.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for zac__mbos in range(len(
            data_typ.types))])
        builder.store(ypkt__ngn._getvalue(), rae__xgp)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = hdsi__qhr
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        ypkt__ngn, zac__mbos = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ypkt__ngn.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        ypkt__ngn, zac__mbos = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ypkt__ngn.null_bitmap)
    pulau__tlhev = types.UniTuple(types.int8, len(struct_typ.data))
    return pulau__tlhev(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, zac__mbos, val = args
        ypkt__ngn, rae__xgp = _get_struct_payload(context, builder,
            struct_typ, struct)
        oyq__ornuj = ypkt__ngn.data
        qsd__uzh = builder.insert_value(oyq__ornuj, val, field_ind)
        ggmnx__suxz = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, ggmnx__suxz, oyq__ornuj)
        context.nrt.incref(builder, ggmnx__suxz, qsd__uzh)
        ypkt__ngn.data = qsd__uzh
        builder.store(ypkt__ngn._getvalue(), rae__xgp)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    nuc__wsq = get_overload_const_str(ind)
    if nuc__wsq not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            nuc__wsq, struct))
    return struct.names.index(nuc__wsq)


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
    uxam__jor = context.get_value_type(payload_type)
    fdxc__qea = context.get_abi_sizeof(uxam__jor)
    qeub__mvqqd = define_struct_dtor(context, builder, struct_type,
        payload_type)
    hdsi__qhr = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, fdxc__qea), qeub__mvqqd)
    khk__bgwoi = context.nrt.meminfo_data(builder, hdsi__qhr)
    rae__xgp = builder.bitcast(khk__bgwoi, uxam__jor.as_pointer())
    ypkt__ngn = cgutils.create_struct_proxy(payload_type)(context, builder)
    ypkt__ngn.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    ypkt__ngn.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(ypkt__ngn._getvalue(), rae__xgp)
    return hdsi__qhr


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    xjo__qxn = tuple(d.dtype for d in struct_arr_typ.data)
    eyzm__nbv = StructType(xjo__qxn, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        awurx__lkmya, ind = args
        ypkt__ngn = _get_struct_arr_payload(context, builder,
            struct_arr_typ, awurx__lkmya)
        gora__xxbf = []
        umyan__vhm = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            jnm__luz = builder.extract_value(ypkt__ngn.data, i)
            lat__szr = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [jnm__luz, ind]
                )
            umyan__vhm.append(lat__szr)
            puong__zsjk = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            mogq__gyuig = builder.icmp_unsigned('==', lat__szr, lir.
                Constant(lat__szr.type, 1))
            with builder.if_then(mogq__gyuig):
                fopz__qxp = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    jnm__luz, ind])
                builder.store(fopz__qxp, puong__zsjk)
            gora__xxbf.append(builder.load(puong__zsjk))
        if isinstance(eyzm__nbv, types.DictType):
            qhjg__rfvhp = [context.insert_const_string(builder.module,
                ptqhz__vso) for ptqhz__vso in struct_arr_typ.names]
            xge__ottwk = cgutils.pack_array(builder, gora__xxbf)
            nfy__gwmqs = cgutils.pack_array(builder, qhjg__rfvhp)

            def impl(names, vals):
                d = {}
                for i, ptqhz__vso in enumerate(names):
                    d[ptqhz__vso] = vals[i]
                return d
            vhvp__tdfe = context.compile_internal(builder, impl, eyzm__nbv(
                types.Tuple(tuple(types.StringLiteral(ptqhz__vso) for
                ptqhz__vso in struct_arr_typ.names)), types.Tuple(xjo__qxn)
                ), [nfy__gwmqs, xge__ottwk])
            context.nrt.decref(builder, types.BaseTuple.from_types(xjo__qxn
                ), xge__ottwk)
            return vhvp__tdfe
        hdsi__qhr = construct_struct(context, builder, eyzm__nbv,
            gora__xxbf, umyan__vhm)
        struct = context.make_helper(builder, eyzm__nbv)
        struct.meminfo = hdsi__qhr
        return struct._getvalue()
    return eyzm__nbv(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ypkt__ngn = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ypkt__ngn.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ypkt__ngn = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ypkt__ngn.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(scvbr__rfgvf) for scvbr__rfgvf in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, kdiy__own, mva__dhsds = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        uxam__jor = context.get_value_type(payload_type)
        fdxc__qea = context.get_abi_sizeof(uxam__jor)
        qeub__mvqqd = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        hdsi__qhr = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, fdxc__qea), qeub__mvqqd)
        khk__bgwoi = context.nrt.meminfo_data(builder, hdsi__qhr)
        rae__xgp = builder.bitcast(khk__bgwoi, uxam__jor.as_pointer())
        ypkt__ngn = cgutils.create_struct_proxy(payload_type)(context, builder)
        ypkt__ngn.data = data
        ypkt__ngn.null_bitmap = kdiy__own
        builder.store(ypkt__ngn._getvalue(), rae__xgp)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, kdiy__own)
        qpdgu__ked = context.make_helper(builder, struct_arr_type)
        qpdgu__ked.meminfo = hdsi__qhr
        return qpdgu__ked._getvalue()
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
    oclqp__ofmen = len(arr.data)
    xszz__rql = 'def impl(arr, ind):\n'
    xszz__rql += '  data = get_data(arr)\n'
    xszz__rql += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        xszz__rql += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        xszz__rql += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        xszz__rql += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    xszz__rql += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(oclqp__ofmen)), ', '.join("'{}'".format(ptqhz__vso) for
        ptqhz__vso in arr.names)))
    taic__qhnpz = {}
    exec(xszz__rql, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, taic__qhnpz)
    impl = taic__qhnpz['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        oclqp__ofmen = len(arr.data)
        xszz__rql = 'def impl(arr, ind, val):\n'
        xszz__rql += '  data = get_data(arr)\n'
        xszz__rql += '  null_bitmap = get_null_bitmap(arr)\n'
        xszz__rql += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(oclqp__ofmen):
            if isinstance(val, StructType):
                xszz__rql += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                xszz__rql += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                xszz__rql += '  else:\n'
                xszz__rql += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                xszz__rql += "  data[{}][ind] = val['{}']\n".format(i, arr.
                    names[i])
        taic__qhnpz = {}
        exec(xszz__rql, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, taic__qhnpz)
        impl = taic__qhnpz['impl']
        return impl
    if isinstance(ind, types.SliceType):
        oclqp__ofmen = len(arr.data)
        xszz__rql = 'def impl(arr, ind, val):\n'
        xszz__rql += '  data = get_data(arr)\n'
        xszz__rql += '  null_bitmap = get_null_bitmap(arr)\n'
        xszz__rql += '  val_data = get_data(val)\n'
        xszz__rql += '  val_null_bitmap = get_null_bitmap(val)\n'
        xszz__rql += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(oclqp__ofmen):
            xszz__rql += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        taic__qhnpz = {}
        exec(xszz__rql, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, taic__qhnpz)
        impl = taic__qhnpz['impl']
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
    xszz__rql = 'def impl(A):\n'
    xszz__rql += '  total_nbytes = 0\n'
    xszz__rql += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        xszz__rql += f'  total_nbytes += data[{i}].nbytes\n'
    xszz__rql += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    xszz__rql += '  return total_nbytes\n'
    taic__qhnpz = {}
    exec(xszz__rql, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, taic__qhnpz)
    impl = taic__qhnpz['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        kdiy__own = get_null_bitmap(A)
        ruqf__igr = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        mxr__sdp = kdiy__own.copy()
        return init_struct_arr(ruqf__igr, mxr__sdp, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(sqmd__xyls.copy() for sqmd__xyls in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    lhfzc__qmxwr = arrs.count
    xszz__rql = 'def f(arrs):\n'
    xszz__rql += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(lhfzc__qmxwr)))
    taic__qhnpz = {}
    exec(xszz__rql, {}, taic__qhnpz)
    impl = taic__qhnpz['f']
    return impl
