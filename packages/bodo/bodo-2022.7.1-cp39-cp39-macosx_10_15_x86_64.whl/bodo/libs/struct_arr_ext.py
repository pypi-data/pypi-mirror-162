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
            .utils.is_array_typ(rouhp__iwczp, False) for rouhp__iwczp in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(rouhp__iwczp,
                str) for rouhp__iwczp in names) and len(names) == len(data)
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
        return StructType(tuple(uso__jyu.dtype for uso__jyu in self.data),
            self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(rouhp__iwczp) for rouhp__iwczp in d.keys())
        data = tuple(dtype_to_array_type(uso__jyu) for uso__jyu in d.values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(rouhp__iwczp, False) for rouhp__iwczp in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wqu__lmw = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, wqu__lmw)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        wqu__lmw = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, wqu__lmw)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    pglb__rpne = builder.module
    vsrrw__qdv = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    vace__hsmkq = cgutils.get_or_insert_function(pglb__rpne, vsrrw__qdv,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not vace__hsmkq.is_declaration:
        return vace__hsmkq
    vace__hsmkq.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(vace__hsmkq.append_basic_block())
    eqmmm__yfwmw = vace__hsmkq.args[0]
    ayhms__tbzsk = context.get_value_type(payload_type).as_pointer()
    ncdt__kfi = builder.bitcast(eqmmm__yfwmw, ayhms__tbzsk)
    rsnuf__uty = context.make_helper(builder, payload_type, ref=ncdt__kfi)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), rsnuf__uty.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        rsnuf__uty.null_bitmap)
    builder.ret_void()
    return vace__hsmkq


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    mwunl__bbj = context.get_value_type(payload_type)
    wcvmv__bmbx = context.get_abi_sizeof(mwunl__bbj)
    qvcqh__bxu = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    nvf__vqqd = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, wcvmv__bmbx), qvcqh__bxu)
    xuejb__ygmj = context.nrt.meminfo_data(builder, nvf__vqqd)
    udfu__nlgfy = builder.bitcast(xuejb__ygmj, mwunl__bbj.as_pointer())
    rsnuf__uty = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    ezxf__rsb = 0
    for arr_typ in struct_arr_type.data:
        fbu__pwzm = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        rrhl__meore = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(ezxf__rsb, ezxf__rsb +
            fbu__pwzm)])
        arr = gen_allocate_array(context, builder, arr_typ, rrhl__meore, c)
        arrs.append(arr)
        ezxf__rsb += fbu__pwzm
    rsnuf__uty.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    vjvew__npvfj = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    xof__uvb = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [vjvew__npvfj])
    null_bitmap_ptr = xof__uvb.data
    rsnuf__uty.null_bitmap = xof__uvb._getvalue()
    builder.store(rsnuf__uty._getvalue(), udfu__nlgfy)
    return nvf__vqqd, rsnuf__uty.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    rmanx__ekkkw = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        oli__jrh = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            oli__jrh)
        rmanx__ekkkw.append(arr.data)
    bhbrn__rtt = cgutils.pack_array(c.builder, rmanx__ekkkw
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, rmanx__ekkkw)
    rzpvu__kxxcg = cgutils.alloca_once_value(c.builder, bhbrn__rtt)
    tpjd__aivg = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(rouhp__iwczp.dtype)) for rouhp__iwczp in data_typ]
    zrf__ythu = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, tpjd__aivg))
    iagpg__uxz = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, rouhp__iwczp) for
        rouhp__iwczp in names])
    tqg__guqsy = cgutils.alloca_once_value(c.builder, iagpg__uxz)
    return rzpvu__kxxcg, zrf__ythu, tqg__guqsy


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    oig__vgak = all(isinstance(uso__jyu, types.Array) and uso__jyu.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        uso__jyu in typ.data)
    if oig__vgak:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        ksh__fxg = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            ksh__fxg, i) for i in range(1, ksh__fxg.type.count)], lir.
            IntType(64))
    nvf__vqqd, data_tup, null_bitmap_ptr = construct_struct_array(c.context,
        c.builder, typ, n_structs, n_elems, c)
    if oig__vgak:
        rzpvu__kxxcg, zrf__ythu, tqg__guqsy = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        vsrrw__qdv = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        vace__hsmkq = cgutils.get_or_insert_function(c.builder.module,
            vsrrw__qdv, name='struct_array_from_sequence')
        c.builder.call(vace__hsmkq, [val, c.context.get_constant(types.
            int32, len(typ.data)), c.builder.bitcast(rzpvu__kxxcg, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            zrf__ythu, lir.IntType(8).as_pointer()), c.builder.bitcast(
            tqg__guqsy, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    zpbzh__vgx = c.context.make_helper(c.builder, typ)
    zpbzh__vgx.meminfo = nvf__vqqd
    ftx__syvu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zpbzh__vgx._getvalue(), is_error=ftx__syvu)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    sjl__cse = context.insert_const_string(builder.module, 'pandas')
    lyzlu__szf = c.pyapi.import_module_noblock(sjl__cse)
    zutpc__fzxuq = c.pyapi.object_getattr_string(lyzlu__szf, 'NA')
    with cgutils.for_range(builder, n_structs) as bax__dpb:
        zgyfk__bzr = bax__dpb.index
        muc__bjlwu = seq_getitem(builder, context, val, zgyfk__bzr)
        set_bitmap_bit(builder, null_bitmap_ptr, zgyfk__bzr, 0)
        for qobkp__pcyml in range(len(typ.data)):
            arr_typ = typ.data[qobkp__pcyml]
            data_arr = builder.extract_value(data_tup, qobkp__pcyml)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            ubj__ogt, pan__ybm = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, zgyfk__bzr])
        zkvly__gmgl = is_na_value(builder, context, muc__bjlwu, zutpc__fzxuq)
        nccv__vdyw = builder.icmp_unsigned('!=', zkvly__gmgl, lir.Constant(
            zkvly__gmgl.type, 1))
        with builder.if_then(nccv__vdyw):
            set_bitmap_bit(builder, null_bitmap_ptr, zgyfk__bzr, 1)
            for qobkp__pcyml in range(len(typ.data)):
                arr_typ = typ.data[qobkp__pcyml]
                if is_tuple_array:
                    lmpg__pqdge = c.pyapi.tuple_getitem(muc__bjlwu,
                        qobkp__pcyml)
                else:
                    lmpg__pqdge = c.pyapi.dict_getitem_string(muc__bjlwu,
                        typ.names[qobkp__pcyml])
                zkvly__gmgl = is_na_value(builder, context, lmpg__pqdge,
                    zutpc__fzxuq)
                nccv__vdyw = builder.icmp_unsigned('!=', zkvly__gmgl, lir.
                    Constant(zkvly__gmgl.type, 1))
                with builder.if_then(nccv__vdyw):
                    lmpg__pqdge = to_arr_obj_if_list_obj(c, context,
                        builder, lmpg__pqdge, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        lmpg__pqdge).value
                    data_arr = builder.extract_value(data_tup, qobkp__pcyml)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    ubj__ogt, pan__ybm = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, zgyfk__bzr, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(muc__bjlwu)
    c.pyapi.decref(lyzlu__szf)
    c.pyapi.decref(zutpc__fzxuq)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    zpbzh__vgx = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    xuejb__ygmj = context.nrt.meminfo_data(builder, zpbzh__vgx.meminfo)
    udfu__nlgfy = builder.bitcast(xuejb__ygmj, context.get_value_type(
        payload_type).as_pointer())
    rsnuf__uty = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(udfu__nlgfy))
    return rsnuf__uty


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    rsnuf__uty = _get_struct_arr_payload(c.context, c.builder, typ, val)
    ubj__ogt, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64(
        typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), rsnuf__uty.null_bitmap).data
    oig__vgak = all(isinstance(uso__jyu, types.Array) and uso__jyu.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        uso__jyu in typ.data)
    if oig__vgak:
        rzpvu__kxxcg, zrf__ythu, tqg__guqsy = _get_C_API_ptrs(c, rsnuf__uty
            .data, typ.data, typ.names)
        vsrrw__qdv = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        uvrfe__mrncs = cgutils.get_or_insert_function(c.builder.module,
            vsrrw__qdv, name='np_array_from_struct_array')
        arr = c.builder.call(uvrfe__mrncs, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(rzpvu__kxxcg,
            lir.IntType(8).as_pointer()), null_bitmap_ptr, c.builder.
            bitcast(zrf__ythu, lir.IntType(8).as_pointer()), c.builder.
            bitcast(tqg__guqsy, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, rsnuf__uty.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    sjl__cse = context.insert_const_string(builder.module, 'numpy')
    jqoge__lmnd = c.pyapi.import_module_noblock(sjl__cse)
    xmumi__qtf = c.pyapi.object_getattr_string(jqoge__lmnd, 'object_')
    uqeb__psp = c.pyapi.long_from_longlong(length)
    bql__lizik = c.pyapi.call_method(jqoge__lmnd, 'ndarray', (uqeb__psp,
        xmumi__qtf))
    etyu__eyay = c.pyapi.object_getattr_string(jqoge__lmnd, 'nan')
    with cgutils.for_range(builder, length) as bax__dpb:
        zgyfk__bzr = bax__dpb.index
        pyarray_setitem(builder, context, bql__lizik, zgyfk__bzr, etyu__eyay)
        qaop__wwwo = get_bitmap_bit(builder, null_bitmap_ptr, zgyfk__bzr)
        zouwx__kqw = builder.icmp_unsigned('!=', qaop__wwwo, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(zouwx__kqw):
            if is_tuple_array:
                muc__bjlwu = c.pyapi.tuple_new(len(typ.data))
            else:
                muc__bjlwu = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(etyu__eyay)
                    c.pyapi.tuple_setitem(muc__bjlwu, i, etyu__eyay)
                else:
                    c.pyapi.dict_setitem_string(muc__bjlwu, typ.names[i],
                        etyu__eyay)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                ubj__ogt, fxhkc__xeq = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, zgyfk__bzr])
                with builder.if_then(fxhkc__xeq):
                    ubj__ogt, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, zgyfk__bzr])
                    wnr__quv = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(muc__bjlwu, i, wnr__quv)
                    else:
                        c.pyapi.dict_setitem_string(muc__bjlwu, typ.names[i
                            ], wnr__quv)
                        c.pyapi.decref(wnr__quv)
            pyarray_setitem(builder, context, bql__lizik, zgyfk__bzr,
                muc__bjlwu)
            c.pyapi.decref(muc__bjlwu)
    c.pyapi.decref(jqoge__lmnd)
    c.pyapi.decref(xmumi__qtf)
    c.pyapi.decref(uqeb__psp)
    c.pyapi.decref(etyu__eyay)
    return bql__lizik


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    vruc__fjsz = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if vruc__fjsz == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for oewp__ffpy in range(vruc__fjsz)])
    elif nested_counts_type.count < vruc__fjsz:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for oewp__ffpy in range(
            vruc__fjsz - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(uso__jyu) for uso__jyu in
            names_typ.types)
    xykf__aip = tuple(uso__jyu.instance_type for uso__jyu in dtypes_typ.types)
    struct_arr_type = StructArrayType(xykf__aip, names)

    def codegen(context, builder, sig, args):
        njx__tkzt, nested_counts, oewp__ffpy, oewp__ffpy = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        nvf__vqqd, oewp__ffpy, oewp__ffpy = construct_struct_array(context,
            builder, struct_arr_type, njx__tkzt, nested_counts)
        zpbzh__vgx = context.make_helper(builder, struct_arr_type)
        zpbzh__vgx.meminfo = nvf__vqqd
        return zpbzh__vgx._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(rouhp__iwczp,
            str) for rouhp__iwczp in names) and len(names) == len(data)
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
        wqu__lmw = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, wqu__lmw)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        wqu__lmw = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, wqu__lmw)


def define_struct_dtor(context, builder, struct_type, payload_type):
    pglb__rpne = builder.module
    vsrrw__qdv = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    vace__hsmkq = cgutils.get_or_insert_function(pglb__rpne, vsrrw__qdv,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not vace__hsmkq.is_declaration:
        return vace__hsmkq
    vace__hsmkq.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(vace__hsmkq.append_basic_block())
    eqmmm__yfwmw = vace__hsmkq.args[0]
    ayhms__tbzsk = context.get_value_type(payload_type).as_pointer()
    ncdt__kfi = builder.bitcast(eqmmm__yfwmw, ayhms__tbzsk)
    rsnuf__uty = context.make_helper(builder, payload_type, ref=ncdt__kfi)
    for i in range(len(struct_type.data)):
        wgunh__wak = builder.extract_value(rsnuf__uty.null_bitmap, i)
        zouwx__kqw = builder.icmp_unsigned('==', wgunh__wak, lir.Constant(
            wgunh__wak.type, 1))
        with builder.if_then(zouwx__kqw):
            val = builder.extract_value(rsnuf__uty.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return vace__hsmkq


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    xuejb__ygmj = context.nrt.meminfo_data(builder, struct.meminfo)
    udfu__nlgfy = builder.bitcast(xuejb__ygmj, context.get_value_type(
        payload_type).as_pointer())
    rsnuf__uty = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(udfu__nlgfy))
    return rsnuf__uty, udfu__nlgfy


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    sjl__cse = context.insert_const_string(builder.module, 'pandas')
    lyzlu__szf = c.pyapi.import_module_noblock(sjl__cse)
    zutpc__fzxuq = c.pyapi.object_getattr_string(lyzlu__szf, 'NA')
    jzxei__hfnzr = []
    nulls = []
    for i, uso__jyu in enumerate(typ.data):
        wnr__quv = c.pyapi.dict_getitem_string(val, typ.names[i])
        rppj__umsp = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        fmyy__uju = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(uso__jyu)))
        zkvly__gmgl = is_na_value(builder, context, wnr__quv, zutpc__fzxuq)
        zouwx__kqw = builder.icmp_unsigned('!=', zkvly__gmgl, lir.Constant(
            zkvly__gmgl.type, 1))
        with builder.if_then(zouwx__kqw):
            builder.store(context.get_constant(types.uint8, 1), rppj__umsp)
            field_val = c.pyapi.to_native_value(uso__jyu, wnr__quv).value
            builder.store(field_val, fmyy__uju)
        jzxei__hfnzr.append(builder.load(fmyy__uju))
        nulls.append(builder.load(rppj__umsp))
    c.pyapi.decref(lyzlu__szf)
    c.pyapi.decref(zutpc__fzxuq)
    nvf__vqqd = construct_struct(context, builder, typ, jzxei__hfnzr, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = nvf__vqqd
    ftx__syvu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=ftx__syvu)


@box(StructType)
def box_struct(typ, val, c):
    npzjh__iocvg = c.pyapi.dict_new(len(typ.data))
    rsnuf__uty, oewp__ffpy = _get_struct_payload(c.context, c.builder, typ, val
        )
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(npzjh__iocvg, typ.names[i], c.pyapi.
            borrow_none())
        wgunh__wak = c.builder.extract_value(rsnuf__uty.null_bitmap, i)
        zouwx__kqw = c.builder.icmp_unsigned('==', wgunh__wak, lir.Constant
            (wgunh__wak.type, 1))
        with c.builder.if_then(zouwx__kqw):
            gbhf__zng = c.builder.extract_value(rsnuf__uty.data, i)
            c.context.nrt.incref(c.builder, val_typ, gbhf__zng)
            lmpg__pqdge = c.pyapi.from_native_value(val_typ, gbhf__zng, c.
                env_manager)
            c.pyapi.dict_setitem_string(npzjh__iocvg, typ.names[i], lmpg__pqdge
                )
            c.pyapi.decref(lmpg__pqdge)
    c.context.nrt.decref(c.builder, typ, val)
    return npzjh__iocvg


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(uso__jyu) for uso__jyu in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, stwro__ozue = args
        payload_type = StructPayloadType(struct_type.data)
        mwunl__bbj = context.get_value_type(payload_type)
        wcvmv__bmbx = context.get_abi_sizeof(mwunl__bbj)
        qvcqh__bxu = define_struct_dtor(context, builder, struct_type,
            payload_type)
        nvf__vqqd = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, wcvmv__bmbx), qvcqh__bxu)
        xuejb__ygmj = context.nrt.meminfo_data(builder, nvf__vqqd)
        udfu__nlgfy = builder.bitcast(xuejb__ygmj, mwunl__bbj.as_pointer())
        rsnuf__uty = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        rsnuf__uty.data = data
        rsnuf__uty.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for oewp__ffpy in range(len(
            data_typ.types))])
        builder.store(rsnuf__uty._getvalue(), udfu__nlgfy)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = nvf__vqqd
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        rsnuf__uty, oewp__ffpy = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rsnuf__uty.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        rsnuf__uty, oewp__ffpy = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rsnuf__uty.null_bitmap)
    qepa__jcsa = types.UniTuple(types.int8, len(struct_typ.data))
    return qepa__jcsa(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, oewp__ffpy, val = args
        rsnuf__uty, udfu__nlgfy = _get_struct_payload(context, builder,
            struct_typ, struct)
        rxdxi__jksp = rsnuf__uty.data
        sovec__drgqf = builder.insert_value(rxdxi__jksp, val, field_ind)
        roulz__whit = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, roulz__whit, rxdxi__jksp)
        context.nrt.incref(builder, roulz__whit, sovec__drgqf)
        rsnuf__uty.data = sovec__drgqf
        builder.store(rsnuf__uty._getvalue(), udfu__nlgfy)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    kav__mam = get_overload_const_str(ind)
    if kav__mam not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            kav__mam, struct))
    return struct.names.index(kav__mam)


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
    mwunl__bbj = context.get_value_type(payload_type)
    wcvmv__bmbx = context.get_abi_sizeof(mwunl__bbj)
    qvcqh__bxu = define_struct_dtor(context, builder, struct_type, payload_type
        )
    nvf__vqqd = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, wcvmv__bmbx), qvcqh__bxu)
    xuejb__ygmj = context.nrt.meminfo_data(builder, nvf__vqqd)
    udfu__nlgfy = builder.bitcast(xuejb__ygmj, mwunl__bbj.as_pointer())
    rsnuf__uty = cgutils.create_struct_proxy(payload_type)(context, builder)
    rsnuf__uty.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    rsnuf__uty.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(rsnuf__uty._getvalue(), udfu__nlgfy)
    return nvf__vqqd


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    xcdf__rwmt = tuple(d.dtype for d in struct_arr_typ.data)
    wlv__llm = StructType(xcdf__rwmt, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        osv__xhzuq, ind = args
        rsnuf__uty = _get_struct_arr_payload(context, builder,
            struct_arr_typ, osv__xhzuq)
        jzxei__hfnzr = []
        kwkh__idit = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            oli__jrh = builder.extract_value(rsnuf__uty.data, i)
            uhunn__hlcg = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [oli__jrh, ind]
                )
            kwkh__idit.append(uhunn__hlcg)
            yaka__loppo = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            zouwx__kqw = builder.icmp_unsigned('==', uhunn__hlcg, lir.
                Constant(uhunn__hlcg.type, 1))
            with builder.if_then(zouwx__kqw):
                wzk__pjxik = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    oli__jrh, ind])
                builder.store(wzk__pjxik, yaka__loppo)
            jzxei__hfnzr.append(builder.load(yaka__loppo))
        if isinstance(wlv__llm, types.DictType):
            hmp__hdoii = [context.insert_const_string(builder.module,
                kmd__mtz) for kmd__mtz in struct_arr_typ.names]
            xrcwo__fwdd = cgutils.pack_array(builder, jzxei__hfnzr)
            tjqt__uwm = cgutils.pack_array(builder, hmp__hdoii)

            def impl(names, vals):
                d = {}
                for i, kmd__mtz in enumerate(names):
                    d[kmd__mtz] = vals[i]
                return d
            amiwy__qpbe = context.compile_internal(builder, impl, wlv__llm(
                types.Tuple(tuple(types.StringLiteral(kmd__mtz) for
                kmd__mtz in struct_arr_typ.names)), types.Tuple(xcdf__rwmt)
                ), [tjqt__uwm, xrcwo__fwdd])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                xcdf__rwmt), xrcwo__fwdd)
            return amiwy__qpbe
        nvf__vqqd = construct_struct(context, builder, wlv__llm,
            jzxei__hfnzr, kwkh__idit)
        struct = context.make_helper(builder, wlv__llm)
        struct.meminfo = nvf__vqqd
        return struct._getvalue()
    return wlv__llm(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        rsnuf__uty = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rsnuf__uty.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        rsnuf__uty = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rsnuf__uty.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(uso__jyu) for uso__jyu in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, xof__uvb, stwro__ozue = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        mwunl__bbj = context.get_value_type(payload_type)
        wcvmv__bmbx = context.get_abi_sizeof(mwunl__bbj)
        qvcqh__bxu = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        nvf__vqqd = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, wcvmv__bmbx), qvcqh__bxu)
        xuejb__ygmj = context.nrt.meminfo_data(builder, nvf__vqqd)
        udfu__nlgfy = builder.bitcast(xuejb__ygmj, mwunl__bbj.as_pointer())
        rsnuf__uty = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        rsnuf__uty.data = data
        rsnuf__uty.null_bitmap = xof__uvb
        builder.store(rsnuf__uty._getvalue(), udfu__nlgfy)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, xof__uvb)
        zpbzh__vgx = context.make_helper(builder, struct_arr_type)
        zpbzh__vgx.meminfo = nvf__vqqd
        return zpbzh__vgx._getvalue()
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
    wdvhk__jyzn = len(arr.data)
    fiwe__djeg = 'def impl(arr, ind):\n'
    fiwe__djeg += '  data = get_data(arr)\n'
    fiwe__djeg += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        fiwe__djeg += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        fiwe__djeg += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        fiwe__djeg += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    fiwe__djeg += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(wdvhk__jyzn)), ', '.join("'{}'".format(kmd__mtz) for
        kmd__mtz in arr.names)))
    lcs__yism = {}
    exec(fiwe__djeg, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, lcs__yism)
    impl = lcs__yism['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        wdvhk__jyzn = len(arr.data)
        fiwe__djeg = 'def impl(arr, ind, val):\n'
        fiwe__djeg += '  data = get_data(arr)\n'
        fiwe__djeg += '  null_bitmap = get_null_bitmap(arr)\n'
        fiwe__djeg += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(wdvhk__jyzn):
            if isinstance(val, StructType):
                fiwe__djeg += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                fiwe__djeg += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                fiwe__djeg += '  else:\n'
                fiwe__djeg += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                fiwe__djeg += "  data[{}][ind] = val['{}']\n".format(i, arr
                    .names[i])
        lcs__yism = {}
        exec(fiwe__djeg, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, lcs__yism)
        impl = lcs__yism['impl']
        return impl
    if isinstance(ind, types.SliceType):
        wdvhk__jyzn = len(arr.data)
        fiwe__djeg = 'def impl(arr, ind, val):\n'
        fiwe__djeg += '  data = get_data(arr)\n'
        fiwe__djeg += '  null_bitmap = get_null_bitmap(arr)\n'
        fiwe__djeg += '  val_data = get_data(val)\n'
        fiwe__djeg += '  val_null_bitmap = get_null_bitmap(val)\n'
        fiwe__djeg += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(wdvhk__jyzn):
            fiwe__djeg += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        lcs__yism = {}
        exec(fiwe__djeg, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, lcs__yism)
        impl = lcs__yism['impl']
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
    fiwe__djeg = 'def impl(A):\n'
    fiwe__djeg += '  total_nbytes = 0\n'
    fiwe__djeg += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        fiwe__djeg += f'  total_nbytes += data[{i}].nbytes\n'
    fiwe__djeg += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    fiwe__djeg += '  return total_nbytes\n'
    lcs__yism = {}
    exec(fiwe__djeg, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, lcs__yism)
    impl = lcs__yism['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        xof__uvb = get_null_bitmap(A)
        uvm__ahaxk = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        arm__mxubz = xof__uvb.copy()
        return init_struct_arr(uvm__ahaxk, arm__mxubz, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(rouhp__iwczp.copy() for rouhp__iwczp in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    zxtto__qoe = arrs.count
    fiwe__djeg = 'def f(arrs):\n'
    fiwe__djeg += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(zxtto__qoe)))
    lcs__yism = {}
    exec(fiwe__djeg, {}, lcs__yism)
    impl = lcs__yism['f']
    return impl
