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
            .utils.is_array_typ(wlx__zlx, False) for wlx__zlx in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(wlx__zlx,
                str) for wlx__zlx in names) and len(names) == len(data)
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
        return StructType(tuple(gfrxt__qwc.dtype for gfrxt__qwc in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(wlx__zlx) for wlx__zlx in d.keys())
        data = tuple(dtype_to_array_type(gfrxt__qwc) for gfrxt__qwc in d.
            values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(wlx__zlx, False) for wlx__zlx in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vix__shyb = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, vix__shyb)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        vix__shyb = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, vix__shyb)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    sjom__wao = builder.module
    mvj__iqmsh = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    ledw__zev = cgutils.get_or_insert_function(sjom__wao, mvj__iqmsh, name=
        '.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not ledw__zev.is_declaration:
        return ledw__zev
    ledw__zev.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(ledw__zev.append_basic_block())
    tuy__mevon = ledw__zev.args[0]
    eyp__lnk = context.get_value_type(payload_type).as_pointer()
    ucks__dytup = builder.bitcast(tuy__mevon, eyp__lnk)
    rammv__kfw = context.make_helper(builder, payload_type, ref=ucks__dytup)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), rammv__kfw.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        rammv__kfw.null_bitmap)
    builder.ret_void()
    return ledw__zev


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    ziyxw__iwlj = context.get_value_type(payload_type)
    qckps__gdfoy = context.get_abi_sizeof(ziyxw__iwlj)
    xtp__pxac = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    ymeek__kyljm = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qckps__gdfoy), xtp__pxac)
    aci__elw = context.nrt.meminfo_data(builder, ymeek__kyljm)
    zyny__qzm = builder.bitcast(aci__elw, ziyxw__iwlj.as_pointer())
    rammv__kfw = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    ryaag__cxvmv = 0
    for arr_typ in struct_arr_type.data:
        mxjs__uhek = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        autdv__kolii = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(ryaag__cxvmv, 
            ryaag__cxvmv + mxjs__uhek)])
        arr = gen_allocate_array(context, builder, arr_typ, autdv__kolii, c)
        arrs.append(arr)
        ryaag__cxvmv += mxjs__uhek
    rammv__kfw.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    agf__uju = builder.udiv(builder.add(n_structs, lir.Constant(lir.IntType
        (64), 7)), lir.Constant(lir.IntType(64), 8))
    ldpiv__vqkj = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [agf__uju])
    null_bitmap_ptr = ldpiv__vqkj.data
    rammv__kfw.null_bitmap = ldpiv__vqkj._getvalue()
    builder.store(rammv__kfw._getvalue(), zyny__qzm)
    return ymeek__kyljm, rammv__kfw.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    apbn__hbrs = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        xddr__ckue = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            xddr__ckue)
        apbn__hbrs.append(arr.data)
    knmq__vfhl = cgutils.pack_array(c.builder, apbn__hbrs
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, apbn__hbrs)
    uuxiy__ndu = cgutils.alloca_once_value(c.builder, knmq__vfhl)
    skn__nqj = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(wlx__zlx.dtype)) for wlx__zlx in data_typ]
    ookvu__xbbt = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, skn__nqj))
    nyka__dkj = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, wlx__zlx) for wlx__zlx in names])
    uuqp__nji = cgutils.alloca_once_value(c.builder, nyka__dkj)
    return uuxiy__ndu, ookvu__xbbt, uuqp__nji


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    zihq__hqa = all(isinstance(gfrxt__qwc, types.Array) and gfrxt__qwc.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for gfrxt__qwc in typ.data)
    if zihq__hqa:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        iilla__hfa = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            iilla__hfa, i) for i in range(1, iilla__hfa.type.count)], lir.
            IntType(64))
    ymeek__kyljm, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if zihq__hqa:
        uuxiy__ndu, ookvu__xbbt, uuqp__nji = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        mvj__iqmsh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        ledw__zev = cgutils.get_or_insert_function(c.builder.module,
            mvj__iqmsh, name='struct_array_from_sequence')
        c.builder.call(ledw__zev, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(uuxiy__ndu, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(ookvu__xbbt,
            lir.IntType(8).as_pointer()), c.builder.bitcast(uuqp__nji, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    nat__dabgz = c.context.make_helper(c.builder, typ)
    nat__dabgz.meminfo = ymeek__kyljm
    eqgpl__dlepr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(nat__dabgz._getvalue(), is_error=eqgpl__dlepr)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    ynmpy__anu = context.insert_const_string(builder.module, 'pandas')
    waimo__inyy = c.pyapi.import_module_noblock(ynmpy__anu)
    truh__htns = c.pyapi.object_getattr_string(waimo__inyy, 'NA')
    with cgutils.for_range(builder, n_structs) as fbqz__hukf:
        kxsn__xqu = fbqz__hukf.index
        gkou__mzb = seq_getitem(builder, context, val, kxsn__xqu)
        set_bitmap_bit(builder, null_bitmap_ptr, kxsn__xqu, 0)
        for dij__dzxcm in range(len(typ.data)):
            arr_typ = typ.data[dij__dzxcm]
            data_arr = builder.extract_value(data_tup, dij__dzxcm)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            mhw__aijq, jyyhk__cuz = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, kxsn__xqu])
        kdo__uejhq = is_na_value(builder, context, gkou__mzb, truh__htns)
        dqxr__qzrqk = builder.icmp_unsigned('!=', kdo__uejhq, lir.Constant(
            kdo__uejhq.type, 1))
        with builder.if_then(dqxr__qzrqk):
            set_bitmap_bit(builder, null_bitmap_ptr, kxsn__xqu, 1)
            for dij__dzxcm in range(len(typ.data)):
                arr_typ = typ.data[dij__dzxcm]
                if is_tuple_array:
                    bkgy__skuov = c.pyapi.tuple_getitem(gkou__mzb, dij__dzxcm)
                else:
                    bkgy__skuov = c.pyapi.dict_getitem_string(gkou__mzb,
                        typ.names[dij__dzxcm])
                kdo__uejhq = is_na_value(builder, context, bkgy__skuov,
                    truh__htns)
                dqxr__qzrqk = builder.icmp_unsigned('!=', kdo__uejhq, lir.
                    Constant(kdo__uejhq.type, 1))
                with builder.if_then(dqxr__qzrqk):
                    bkgy__skuov = to_arr_obj_if_list_obj(c, context,
                        builder, bkgy__skuov, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        bkgy__skuov).value
                    data_arr = builder.extract_value(data_tup, dij__dzxcm)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    mhw__aijq, jyyhk__cuz = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, kxsn__xqu, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(gkou__mzb)
    c.pyapi.decref(waimo__inyy)
    c.pyapi.decref(truh__htns)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    nat__dabgz = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    aci__elw = context.nrt.meminfo_data(builder, nat__dabgz.meminfo)
    zyny__qzm = builder.bitcast(aci__elw, context.get_value_type(
        payload_type).as_pointer())
    rammv__kfw = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(zyny__qzm))
    return rammv__kfw


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    rammv__kfw = _get_struct_arr_payload(c.context, c.builder, typ, val)
    mhw__aijq, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64
        (typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), rammv__kfw.null_bitmap).data
    zihq__hqa = all(isinstance(gfrxt__qwc, types.Array) and gfrxt__qwc.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for gfrxt__qwc in typ.data)
    if zihq__hqa:
        uuxiy__ndu, ookvu__xbbt, uuqp__nji = _get_C_API_ptrs(c, rammv__kfw.
            data, typ.data, typ.names)
        mvj__iqmsh = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        uot__bvzg = cgutils.get_or_insert_function(c.builder.module,
            mvj__iqmsh, name='np_array_from_struct_array')
        arr = c.builder.call(uot__bvzg, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(uuxiy__ndu, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            ookvu__xbbt, lir.IntType(8).as_pointer()), c.builder.bitcast(
            uuqp__nji, lir.IntType(8).as_pointer()), c.context.get_constant
            (types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, rammv__kfw.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    ynmpy__anu = context.insert_const_string(builder.module, 'numpy')
    wtb__eijwr = c.pyapi.import_module_noblock(ynmpy__anu)
    tniq__psqpz = c.pyapi.object_getattr_string(wtb__eijwr, 'object_')
    rsrp__zcpba = c.pyapi.long_from_longlong(length)
    rrcx__ilr = c.pyapi.call_method(wtb__eijwr, 'ndarray', (rsrp__zcpba,
        tniq__psqpz))
    qiexd__fpvap = c.pyapi.object_getattr_string(wtb__eijwr, 'nan')
    with cgutils.for_range(builder, length) as fbqz__hukf:
        kxsn__xqu = fbqz__hukf.index
        pyarray_setitem(builder, context, rrcx__ilr, kxsn__xqu, qiexd__fpvap)
        jal__gyu = get_bitmap_bit(builder, null_bitmap_ptr, kxsn__xqu)
        lyg__yhr = builder.icmp_unsigned('!=', jal__gyu, lir.Constant(lir.
            IntType(8), 0))
        with builder.if_then(lyg__yhr):
            if is_tuple_array:
                gkou__mzb = c.pyapi.tuple_new(len(typ.data))
            else:
                gkou__mzb = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(qiexd__fpvap)
                    c.pyapi.tuple_setitem(gkou__mzb, i, qiexd__fpvap)
                else:
                    c.pyapi.dict_setitem_string(gkou__mzb, typ.names[i],
                        qiexd__fpvap)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                mhw__aijq, kfznc__infch = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, kxsn__xqu])
                with builder.if_then(kfznc__infch):
                    mhw__aijq, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, kxsn__xqu])
                    bvgjm__odop = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(gkou__mzb, i, bvgjm__odop)
                    else:
                        c.pyapi.dict_setitem_string(gkou__mzb, typ.names[i],
                            bvgjm__odop)
                        c.pyapi.decref(bvgjm__odop)
            pyarray_setitem(builder, context, rrcx__ilr, kxsn__xqu, gkou__mzb)
            c.pyapi.decref(gkou__mzb)
    c.pyapi.decref(wtb__eijwr)
    c.pyapi.decref(tniq__psqpz)
    c.pyapi.decref(rsrp__zcpba)
    c.pyapi.decref(qiexd__fpvap)
    return rrcx__ilr


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    fbyux__sxydj = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if fbyux__sxydj == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for cfekx__bks in range(fbyux__sxydj)])
    elif nested_counts_type.count < fbyux__sxydj:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for cfekx__bks in range(
            fbyux__sxydj - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(gfrxt__qwc) for gfrxt__qwc in
            names_typ.types)
    gaq__usqla = tuple(gfrxt__qwc.instance_type for gfrxt__qwc in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(gaq__usqla, names)

    def codegen(context, builder, sig, args):
        zjgp__brvh, nested_counts, cfekx__bks, cfekx__bks = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        ymeek__kyljm, cfekx__bks, cfekx__bks = construct_struct_array(context,
            builder, struct_arr_type, zjgp__brvh, nested_counts)
        nat__dabgz = context.make_helper(builder, struct_arr_type)
        nat__dabgz.meminfo = ymeek__kyljm
        return nat__dabgz._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(wlx__zlx, str) for
            wlx__zlx in names) and len(names) == len(data)
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
        vix__shyb = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, vix__shyb)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        vix__shyb = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, vix__shyb)


def define_struct_dtor(context, builder, struct_type, payload_type):
    sjom__wao = builder.module
    mvj__iqmsh = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    ledw__zev = cgutils.get_or_insert_function(sjom__wao, mvj__iqmsh, name=
        '.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not ledw__zev.is_declaration:
        return ledw__zev
    ledw__zev.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(ledw__zev.append_basic_block())
    tuy__mevon = ledw__zev.args[0]
    eyp__lnk = context.get_value_type(payload_type).as_pointer()
    ucks__dytup = builder.bitcast(tuy__mevon, eyp__lnk)
    rammv__kfw = context.make_helper(builder, payload_type, ref=ucks__dytup)
    for i in range(len(struct_type.data)):
        fmtf__vbth = builder.extract_value(rammv__kfw.null_bitmap, i)
        lyg__yhr = builder.icmp_unsigned('==', fmtf__vbth, lir.Constant(
            fmtf__vbth.type, 1))
        with builder.if_then(lyg__yhr):
            val = builder.extract_value(rammv__kfw.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return ledw__zev


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    aci__elw = context.nrt.meminfo_data(builder, struct.meminfo)
    zyny__qzm = builder.bitcast(aci__elw, context.get_value_type(
        payload_type).as_pointer())
    rammv__kfw = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(zyny__qzm))
    return rammv__kfw, zyny__qzm


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    ynmpy__anu = context.insert_const_string(builder.module, 'pandas')
    waimo__inyy = c.pyapi.import_module_noblock(ynmpy__anu)
    truh__htns = c.pyapi.object_getattr_string(waimo__inyy, 'NA')
    kyl__pqygi = []
    nulls = []
    for i, gfrxt__qwc in enumerate(typ.data):
        bvgjm__odop = c.pyapi.dict_getitem_string(val, typ.names[i])
        ybx__urfyy = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        gjr__pad = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(gfrxt__qwc)))
        kdo__uejhq = is_na_value(builder, context, bvgjm__odop, truh__htns)
        lyg__yhr = builder.icmp_unsigned('!=', kdo__uejhq, lir.Constant(
            kdo__uejhq.type, 1))
        with builder.if_then(lyg__yhr):
            builder.store(context.get_constant(types.uint8, 1), ybx__urfyy)
            field_val = c.pyapi.to_native_value(gfrxt__qwc, bvgjm__odop).value
            builder.store(field_val, gjr__pad)
        kyl__pqygi.append(builder.load(gjr__pad))
        nulls.append(builder.load(ybx__urfyy))
    c.pyapi.decref(waimo__inyy)
    c.pyapi.decref(truh__htns)
    ymeek__kyljm = construct_struct(context, builder, typ, kyl__pqygi, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = ymeek__kyljm
    eqgpl__dlepr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=eqgpl__dlepr)


@box(StructType)
def box_struct(typ, val, c):
    fdzu__mrgtd = c.pyapi.dict_new(len(typ.data))
    rammv__kfw, cfekx__bks = _get_struct_payload(c.context, c.builder, typ, val
        )
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(fdzu__mrgtd, typ.names[i], c.pyapi.
            borrow_none())
        fmtf__vbth = c.builder.extract_value(rammv__kfw.null_bitmap, i)
        lyg__yhr = c.builder.icmp_unsigned('==', fmtf__vbth, lir.Constant(
            fmtf__vbth.type, 1))
        with c.builder.if_then(lyg__yhr):
            wdqrm__enby = c.builder.extract_value(rammv__kfw.data, i)
            c.context.nrt.incref(c.builder, val_typ, wdqrm__enby)
            bkgy__skuov = c.pyapi.from_native_value(val_typ, wdqrm__enby, c
                .env_manager)
            c.pyapi.dict_setitem_string(fdzu__mrgtd, typ.names[i], bkgy__skuov)
            c.pyapi.decref(bkgy__skuov)
    c.context.nrt.decref(c.builder, typ, val)
    return fdzu__mrgtd


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(gfrxt__qwc) for gfrxt__qwc in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, wxh__ibqm = args
        payload_type = StructPayloadType(struct_type.data)
        ziyxw__iwlj = context.get_value_type(payload_type)
        qckps__gdfoy = context.get_abi_sizeof(ziyxw__iwlj)
        xtp__pxac = define_struct_dtor(context, builder, struct_type,
            payload_type)
        ymeek__kyljm = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, qckps__gdfoy), xtp__pxac)
        aci__elw = context.nrt.meminfo_data(builder, ymeek__kyljm)
        zyny__qzm = builder.bitcast(aci__elw, ziyxw__iwlj.as_pointer())
        rammv__kfw = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        rammv__kfw.data = data
        rammv__kfw.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for cfekx__bks in range(len(
            data_typ.types))])
        builder.store(rammv__kfw._getvalue(), zyny__qzm)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = ymeek__kyljm
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        rammv__kfw, cfekx__bks = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rammv__kfw.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        rammv__kfw, cfekx__bks = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rammv__kfw.null_bitmap)
    cps__gwv = types.UniTuple(types.int8, len(struct_typ.data))
    return cps__gwv(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, cfekx__bks, val = args
        rammv__kfw, zyny__qzm = _get_struct_payload(context, builder,
            struct_typ, struct)
        hkhu__cqdnd = rammv__kfw.data
        zogw__wmk = builder.insert_value(hkhu__cqdnd, val, field_ind)
        epvnv__dkez = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, epvnv__dkez, hkhu__cqdnd)
        context.nrt.incref(builder, epvnv__dkez, zogw__wmk)
        rammv__kfw.data = zogw__wmk
        builder.store(rammv__kfw._getvalue(), zyny__qzm)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    zvmvm__snew = get_overload_const_str(ind)
    if zvmvm__snew not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            zvmvm__snew, struct))
    return struct.names.index(zvmvm__snew)


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
    ziyxw__iwlj = context.get_value_type(payload_type)
    qckps__gdfoy = context.get_abi_sizeof(ziyxw__iwlj)
    xtp__pxac = define_struct_dtor(context, builder, struct_type, payload_type)
    ymeek__kyljm = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qckps__gdfoy), xtp__pxac)
    aci__elw = context.nrt.meminfo_data(builder, ymeek__kyljm)
    zyny__qzm = builder.bitcast(aci__elw, ziyxw__iwlj.as_pointer())
    rammv__kfw = cgutils.create_struct_proxy(payload_type)(context, builder)
    rammv__kfw.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    rammv__kfw.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(rammv__kfw._getvalue(), zyny__qzm)
    return ymeek__kyljm


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    bcsh__xvd = tuple(d.dtype for d in struct_arr_typ.data)
    wfp__vnak = StructType(bcsh__xvd, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        cnnda__dumd, ind = args
        rammv__kfw = _get_struct_arr_payload(context, builder,
            struct_arr_typ, cnnda__dumd)
        kyl__pqygi = []
        bpq__fiddt = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            xddr__ckue = builder.extract_value(rammv__kfw.data, i)
            uzdp__usz = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [xddr__ckue,
                ind])
            bpq__fiddt.append(uzdp__usz)
            loqhl__uaru = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            lyg__yhr = builder.icmp_unsigned('==', uzdp__usz, lir.Constant(
                uzdp__usz.type, 1))
            with builder.if_then(lyg__yhr):
                fayo__pcwiu = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    xddr__ckue, ind])
                builder.store(fayo__pcwiu, loqhl__uaru)
            kyl__pqygi.append(builder.load(loqhl__uaru))
        if isinstance(wfp__vnak, types.DictType):
            wdvvq__ozkz = [context.insert_const_string(builder.module,
                lizpf__pzy) for lizpf__pzy in struct_arr_typ.names]
            wnuwx__pdgb = cgutils.pack_array(builder, kyl__pqygi)
            zazwi__lmdz = cgutils.pack_array(builder, wdvvq__ozkz)

            def impl(names, vals):
                d = {}
                for i, lizpf__pzy in enumerate(names):
                    d[lizpf__pzy] = vals[i]
                return d
            wvxu__hvw = context.compile_internal(builder, impl, wfp__vnak(
                types.Tuple(tuple(types.StringLiteral(lizpf__pzy) for
                lizpf__pzy in struct_arr_typ.names)), types.Tuple(bcsh__xvd
                )), [zazwi__lmdz, wnuwx__pdgb])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                bcsh__xvd), wnuwx__pdgb)
            return wvxu__hvw
        ymeek__kyljm = construct_struct(context, builder, wfp__vnak,
            kyl__pqygi, bpq__fiddt)
        struct = context.make_helper(builder, wfp__vnak)
        struct.meminfo = ymeek__kyljm
        return struct._getvalue()
    return wfp__vnak(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        rammv__kfw = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rammv__kfw.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        rammv__kfw = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rammv__kfw.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(gfrxt__qwc) for gfrxt__qwc in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, ldpiv__vqkj, wxh__ibqm = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        ziyxw__iwlj = context.get_value_type(payload_type)
        qckps__gdfoy = context.get_abi_sizeof(ziyxw__iwlj)
        xtp__pxac = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        ymeek__kyljm = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, qckps__gdfoy), xtp__pxac)
        aci__elw = context.nrt.meminfo_data(builder, ymeek__kyljm)
        zyny__qzm = builder.bitcast(aci__elw, ziyxw__iwlj.as_pointer())
        rammv__kfw = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        rammv__kfw.data = data
        rammv__kfw.null_bitmap = ldpiv__vqkj
        builder.store(rammv__kfw._getvalue(), zyny__qzm)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, ldpiv__vqkj)
        nat__dabgz = context.make_helper(builder, struct_arr_type)
        nat__dabgz.meminfo = ymeek__kyljm
        return nat__dabgz._getvalue()
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
    ealko__wvzhq = len(arr.data)
    tszae__hitc = 'def impl(arr, ind):\n'
    tszae__hitc += '  data = get_data(arr)\n'
    tszae__hitc += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        tszae__hitc += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        tszae__hitc += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        tszae__hitc += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    tszae__hitc += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(ealko__wvzhq)), ', '.join("'{}'".format(lizpf__pzy) for
        lizpf__pzy in arr.names)))
    qsz__vhmim = {}
    exec(tszae__hitc, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, qsz__vhmim)
    impl = qsz__vhmim['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        ealko__wvzhq = len(arr.data)
        tszae__hitc = 'def impl(arr, ind, val):\n'
        tszae__hitc += '  data = get_data(arr)\n'
        tszae__hitc += '  null_bitmap = get_null_bitmap(arr)\n'
        tszae__hitc += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(ealko__wvzhq):
            if isinstance(val, StructType):
                tszae__hitc += "  if is_field_value_null(val, '{}'):\n".format(
                    arr.names[i])
                tszae__hitc += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                tszae__hitc += '  else:\n'
                tszae__hitc += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                tszae__hitc += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        qsz__vhmim = {}
        exec(tszae__hitc, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, qsz__vhmim)
        impl = qsz__vhmim['impl']
        return impl
    if isinstance(ind, types.SliceType):
        ealko__wvzhq = len(arr.data)
        tszae__hitc = 'def impl(arr, ind, val):\n'
        tszae__hitc += '  data = get_data(arr)\n'
        tszae__hitc += '  null_bitmap = get_null_bitmap(arr)\n'
        tszae__hitc += '  val_data = get_data(val)\n'
        tszae__hitc += '  val_null_bitmap = get_null_bitmap(val)\n'
        tszae__hitc += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(ealko__wvzhq):
            tszae__hitc += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        qsz__vhmim = {}
        exec(tszae__hitc, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, qsz__vhmim)
        impl = qsz__vhmim['impl']
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
    tszae__hitc = 'def impl(A):\n'
    tszae__hitc += '  total_nbytes = 0\n'
    tszae__hitc += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        tszae__hitc += f'  total_nbytes += data[{i}].nbytes\n'
    tszae__hitc += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    tszae__hitc += '  return total_nbytes\n'
    qsz__vhmim = {}
    exec(tszae__hitc, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, qsz__vhmim)
    impl = qsz__vhmim['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        ldpiv__vqkj = get_null_bitmap(A)
        sakxa__sroi = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        kzkuo__lxk = ldpiv__vqkj.copy()
        return init_struct_arr(sakxa__sroi, kzkuo__lxk, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(wlx__zlx.copy() for wlx__zlx in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    oxiy__ddvb = arrs.count
    tszae__hitc = 'def f(arrs):\n'
    tszae__hitc += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(oxiy__ddvb)))
    qsz__vhmim = {}
    exec(tszae__hitc, {}, qsz__vhmim)
    impl = qsz__vhmim['f']
    return impl
