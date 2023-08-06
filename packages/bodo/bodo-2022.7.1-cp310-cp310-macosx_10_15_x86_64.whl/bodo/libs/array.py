"""Tools for handling bodo arrays, e.g. passing to C/C++ code
"""
from collections import defaultdict
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import intrinsic, models, register_model
from numba.np.arrayobj import _getitem_array_single_int
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, get_categories_int_type
from bodo.libs import array_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, define_array_item_dtor, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType, int128_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType, _get_map_arr_data_type, init_map_arr_codegen
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, char_arr_type, null_bitmap_arr_type, offset_arr_type, string_array_type
from bodo.libs.struct_arr_ext import StructArrayPayloadType, StructArrayType, StructType, _get_struct_arr_payload, define_struct_arr_dtor
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_overload_none, is_str_arr_type, raise_bodo_error, type_has_unknown_cats, unwrap_typeref
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, numba_to_c_type
ll.add_symbol('list_string_array_to_info', array_ext.list_string_array_to_info)
ll.add_symbol('nested_array_to_info', array_ext.nested_array_to_info)
ll.add_symbol('string_array_to_info', array_ext.string_array_to_info)
ll.add_symbol('dict_str_array_to_info', array_ext.dict_str_array_to_info)
ll.add_symbol('get_nested_info', array_ext.get_nested_info)
ll.add_symbol('get_has_global_dictionary', array_ext.get_has_global_dictionary)
ll.add_symbol('numpy_array_to_info', array_ext.numpy_array_to_info)
ll.add_symbol('categorical_array_to_info', array_ext.categorical_array_to_info)
ll.add_symbol('nullable_array_to_info', array_ext.nullable_array_to_info)
ll.add_symbol('interval_array_to_info', array_ext.interval_array_to_info)
ll.add_symbol('decimal_array_to_info', array_ext.decimal_array_to_info)
ll.add_symbol('info_to_nested_array', array_ext.info_to_nested_array)
ll.add_symbol('info_to_list_string_array', array_ext.info_to_list_string_array)
ll.add_symbol('info_to_string_array', array_ext.info_to_string_array)
ll.add_symbol('info_to_numpy_array', array_ext.info_to_numpy_array)
ll.add_symbol('info_to_nullable_array', array_ext.info_to_nullable_array)
ll.add_symbol('info_to_interval_array', array_ext.info_to_interval_array)
ll.add_symbol('alloc_numpy', array_ext.alloc_numpy)
ll.add_symbol('alloc_string_array', array_ext.alloc_string_array)
ll.add_symbol('arr_info_list_to_table', array_ext.arr_info_list_to_table)
ll.add_symbol('info_from_table', array_ext.info_from_table)
ll.add_symbol('delete_info_decref_array', array_ext.delete_info_decref_array)
ll.add_symbol('delete_table_decref_arrays', array_ext.
    delete_table_decref_arrays)
ll.add_symbol('decref_table_array', array_ext.decref_table_array)
ll.add_symbol('delete_table', array_ext.delete_table)
ll.add_symbol('shuffle_table', array_ext.shuffle_table)
ll.add_symbol('get_shuffle_info', array_ext.get_shuffle_info)
ll.add_symbol('delete_shuffle_info', array_ext.delete_shuffle_info)
ll.add_symbol('reverse_shuffle_table', array_ext.reverse_shuffle_table)
ll.add_symbol('hash_join_table', array_ext.hash_join_table)
ll.add_symbol('drop_duplicates_table', array_ext.drop_duplicates_table)
ll.add_symbol('sort_values_table', array_ext.sort_values_table)
ll.add_symbol('sample_table', array_ext.sample_table)
ll.add_symbol('shuffle_renormalization', array_ext.shuffle_renormalization)
ll.add_symbol('shuffle_renormalization_group', array_ext.
    shuffle_renormalization_group)
ll.add_symbol('groupby_and_aggregate', array_ext.groupby_and_aggregate)
ll.add_symbol('get_groupby_labels', array_ext.get_groupby_labels)
ll.add_symbol('array_isin', array_ext.array_isin)
ll.add_symbol('get_search_regex', array_ext.get_search_regex)
ll.add_symbol('array_info_getitem', array_ext.array_info_getitem)
ll.add_symbol('array_info_getdata1', array_ext.array_info_getdata1)


class ArrayInfoType(types.Type):

    def __init__(self):
        super(ArrayInfoType, self).__init__(name='ArrayInfoType()')


array_info_type = ArrayInfoType()
register_model(ArrayInfoType)(models.OpaqueModel)


class TableTypeCPP(types.Type):

    def __init__(self):
        super(TableTypeCPP, self).__init__(name='TableTypeCPP()')


table_type = TableTypeCPP()
register_model(TableTypeCPP)(models.OpaqueModel)


@intrinsic
def array_to_info(typingctx, arr_type_t=None):
    return array_info_type(arr_type_t), array_to_info_codegen


def array_to_info_codegen(context, builder, sig, args, incref=True):
    in_arr, = args
    arr_type = sig.args[0]
    if incref:
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, TupleArrayType):
        seycj__sae = context.make_helper(builder, arr_type, in_arr)
        in_arr = seycj__sae.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        wlxkd__lct = context.make_helper(builder, arr_type, in_arr)
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='list_string_array_to_info')
        return builder.call(xqn__wxyn, [wlxkd__lct.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                gez__eizg = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for ymhe__vhv in arr_typ.data:
                    gez__eizg += get_types(ymhe__vhv)
                return gez__eizg
            elif isinstance(arr_typ, (types.Array, IntegerArrayType)
                ) or arr_typ == boolean_array:
                return get_types(arr_typ.dtype)
            elif arr_typ == string_array_type:
                return [CTypeEnum.STRING.value]
            elif arr_typ == binary_array_type:
                return [CTypeEnum.BINARY.value]
            elif isinstance(arr_typ, DecimalArrayType):
                return [CTypeEnum.Decimal.value, arr_typ.precision, arr_typ
                    .scale]
            else:
                return [numba_to_c_type(arr_typ)]

        def get_lengths(arr_typ, arr):
            sspa__jwy = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                ehcf__tobdx = context.make_helper(builder, arr_typ, value=arr)
                vdre__imejt = get_lengths(_get_map_arr_data_type(arr_typ),
                    ehcf__tobdx.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                nzr__xjp = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                vdre__imejt = get_lengths(arr_typ.dtype, nzr__xjp.data)
                vdre__imejt = cgutils.pack_array(builder, [nzr__xjp.
                    n_arrays] + [builder.extract_value(vdre__imejt,
                    uetg__nwg) for uetg__nwg in range(vdre__imejt.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                nzr__xjp = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                vdre__imejt = []
                for uetg__nwg, ymhe__vhv in enumerate(arr_typ.data):
                    pra__wgm = get_lengths(ymhe__vhv, builder.extract_value
                        (nzr__xjp.data, uetg__nwg))
                    vdre__imejt += [builder.extract_value(pra__wgm,
                        qhrb__qcx) for qhrb__qcx in range(pra__wgm.type.count)]
                vdre__imejt = cgutils.pack_array(builder, [sspa__jwy,
                    context.get_constant(types.int64, -1)] + vdre__imejt)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                vdre__imejt = cgutils.pack_array(builder, [sspa__jwy])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return vdre__imejt

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                ehcf__tobdx = context.make_helper(builder, arr_typ, value=arr)
                cca__wmyy = get_buffers(_get_map_arr_data_type(arr_typ),
                    ehcf__tobdx.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                nzr__xjp = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                wgr__rref = get_buffers(arr_typ.dtype, nzr__xjp.data)
                uycs__wcsi = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, nzr__xjp.offsets)
                xiey__ebff = builder.bitcast(uycs__wcsi.data, lir.IntType(8
                    ).as_pointer())
                duel__qlqc = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, nzr__xjp.null_bitmap)
                wolgg__jjxn = builder.bitcast(duel__qlqc.data, lir.IntType(
                    8).as_pointer())
                cca__wmyy = cgutils.pack_array(builder, [xiey__ebff,
                    wolgg__jjxn] + [builder.extract_value(wgr__rref,
                    uetg__nwg) for uetg__nwg in range(wgr__rref.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                nzr__xjp = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                wgr__rref = []
                for uetg__nwg, ymhe__vhv in enumerate(arr_typ.data):
                    rkq__pvbc = get_buffers(ymhe__vhv, builder.
                        extract_value(nzr__xjp.data, uetg__nwg))
                    wgr__rref += [builder.extract_value(rkq__pvbc,
                        qhrb__qcx) for qhrb__qcx in range(rkq__pvbc.type.count)
                        ]
                duel__qlqc = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, nzr__xjp.null_bitmap)
                wolgg__jjxn = builder.bitcast(duel__qlqc.data, lir.IntType(
                    8).as_pointer())
                cca__wmyy = cgutils.pack_array(builder, [wolgg__jjxn] +
                    wgr__rref)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                guoo__scp = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    guoo__scp = int128_type
                elif arr_typ == datetime_date_array_type:
                    guoo__scp = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                xou__daaf = context.make_array(types.Array(guoo__scp, 1, 'C'))(
                    context, builder, arr.data)
                duel__qlqc = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, arr.null_bitmap)
                ngtq__cvlrs = builder.bitcast(xou__daaf.data, lir.IntType(8
                    ).as_pointer())
                wolgg__jjxn = builder.bitcast(duel__qlqc.data, lir.IntType(
                    8).as_pointer())
                cca__wmyy = cgutils.pack_array(builder, [wolgg__jjxn,
                    ngtq__cvlrs])
            elif arr_typ in (string_array_type, binary_array_type):
                nzr__xjp = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                zbdp__ytgol = context.make_helper(builder, offset_arr_type,
                    nzr__xjp.offsets).data
                fwq__mtyy = context.make_helper(builder, char_arr_type,
                    nzr__xjp.data).data
                tggha__fkh = context.make_helper(builder,
                    null_bitmap_arr_type, nzr__xjp.null_bitmap).data
                cca__wmyy = cgutils.pack_array(builder, [builder.bitcast(
                    zbdp__ytgol, lir.IntType(8).as_pointer()), builder.
                    bitcast(tggha__fkh, lir.IntType(8).as_pointer()),
                    builder.bitcast(fwq__mtyy, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                ngtq__cvlrs = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                oea__kpql = lir.Constant(lir.IntType(8).as_pointer(), None)
                cca__wmyy = cgutils.pack_array(builder, [oea__kpql,
                    ngtq__cvlrs])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return cca__wmyy

        def get_field_names(arr_typ):
            bsd__hrv = []
            if isinstance(arr_typ, StructArrayType):
                for btbep__pnby, mqvq__fmfce in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    bsd__hrv.append(btbep__pnby)
                    bsd__hrv += get_field_names(mqvq__fmfce)
            elif isinstance(arr_typ, ArrayItemArrayType):
                bsd__hrv += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                bsd__hrv += get_field_names(_get_map_arr_data_type(arr_typ))
            return bsd__hrv
        gez__eizg = get_types(arr_type)
        jzcf__fio = cgutils.pack_array(builder, [context.get_constant(types
            .int32, t) for t in gez__eizg])
        cth__azbl = cgutils.alloca_once_value(builder, jzcf__fio)
        vdre__imejt = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, vdre__imejt)
        cca__wmyy = get_buffers(arr_type, in_arr)
        elll__bbe = cgutils.alloca_once_value(builder, cca__wmyy)
        bsd__hrv = get_field_names(arr_type)
        if len(bsd__hrv) == 0:
            bsd__hrv = ['irrelevant']
        zyw__cso = cgutils.pack_array(builder, [context.insert_const_string
            (builder.module, a) for a in bsd__hrv])
        alv__bdh = cgutils.alloca_once_value(builder, zyw__cso)
        if isinstance(arr_type, MapArrayType):
            qfs__tywxb = _get_map_arr_data_type(arr_type)
            neep__bly = context.make_helper(builder, arr_type, value=in_arr)
            vmsjl__gdoww = neep__bly.data
        else:
            qfs__tywxb = arr_type
            vmsjl__gdoww = in_arr
        mzbg__txr = context.make_helper(builder, qfs__tywxb, vmsjl__gdoww)
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='nested_array_to_info')
        tchf__oyhow = builder.call(xqn__wxyn, [builder.bitcast(cth__azbl,
            lir.IntType(32).as_pointer()), builder.bitcast(elll__bbe, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            alv__bdh, lir.IntType(8).as_pointer()), mzbg__txr.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    if arr_type in (string_array_type, binary_array_type):
        ypm__bpzra = context.make_helper(builder, arr_type, in_arr)
        eca__qfd = ArrayItemArrayType(char_arr_type)
        wlxkd__lct = context.make_helper(builder, eca__qfd, ypm__bpzra.data)
        nzr__xjp = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        zbdp__ytgol = context.make_helper(builder, offset_arr_type,
            nzr__xjp.offsets).data
        fwq__mtyy = context.make_helper(builder, char_arr_type, nzr__xjp.data
            ).data
        tggha__fkh = context.make_helper(builder, null_bitmap_arr_type,
            nzr__xjp.null_bitmap).data
        exj__eih = builder.zext(builder.load(builder.gep(zbdp__ytgol, [
            nzr__xjp.n_arrays])), lir.IntType(64))
        ehdw__yxh = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='string_array_to_info')
        return builder.call(xqn__wxyn, [nzr__xjp.n_arrays, exj__eih,
            fwq__mtyy, zbdp__ytgol, tggha__fkh, wlxkd__lct.meminfo, ehdw__yxh])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        yqzue__rds = arr.data
        img__mbca = arr.indices
        sig = array_info_type(arr_type.data)
        inzfi__hgyzx = array_to_info_codegen(context, builder, sig, (
            yqzue__rds,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        qnve__ghlgg = array_to_info_codegen(context, builder, sig, (
            img__mbca,), False)
        ywgk__hylh = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, img__mbca)
        wolgg__jjxn = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, ywgk__hylh.null_bitmap).data
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='dict_str_array_to_info')
        dso__dfx = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(xqn__wxyn, [inzfi__hgyzx, qnve__ghlgg, builder.
            bitcast(wolgg__jjxn, lir.IntType(8).as_pointer()), dso__dfx])
    kck__upx = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        tpl__xji = context.compile_internal(builder, lambda a: len(a.dtype.
            categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        zri__gxjnt = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(zri__gxjnt, 1, 'C')
        kck__upx = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if kck__upx:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        sspa__jwy = builder.extract_value(arr.shape, 0)
        bqsb__xxelr = arr_type.dtype
        oase__pxb = numba_to_c_type(bqsb__xxelr)
        qayzj__kofh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), oase__pxb))
        if kck__upx:
            lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            xqn__wxyn = cgutils.get_or_insert_function(builder.module,
                lod__paal, name='categorical_array_to_info')
            return builder.call(xqn__wxyn, [sspa__jwy, builder.bitcast(arr.
                data, lir.IntType(8).as_pointer()), builder.load(
                qayzj__kofh), tpl__xji, arr.meminfo])
        else:
            lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            xqn__wxyn = cgutils.get_or_insert_function(builder.module,
                lod__paal, name='numpy_array_to_info')
            return builder.call(xqn__wxyn, [sspa__jwy, builder.bitcast(arr.
                data, lir.IntType(8).as_pointer()), builder.load(
                qayzj__kofh), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        bqsb__xxelr = arr_type.dtype
        guoo__scp = bqsb__xxelr
        if isinstance(arr_type, DecimalArrayType):
            guoo__scp = int128_type
        if arr_type == datetime_date_array_type:
            guoo__scp = types.int64
        xou__daaf = context.make_array(types.Array(guoo__scp, 1, 'C'))(context,
            builder, arr.data)
        sspa__jwy = builder.extract_value(xou__daaf.shape, 0)
        ketxw__etgr = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        oase__pxb = numba_to_c_type(bqsb__xxelr)
        qayzj__kofh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), oase__pxb))
        if isinstance(arr_type, DecimalArrayType):
            lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            xqn__wxyn = cgutils.get_or_insert_function(builder.module,
                lod__paal, name='decimal_array_to_info')
            return builder.call(xqn__wxyn, [sspa__jwy, builder.bitcast(
                xou__daaf.data, lir.IntType(8).as_pointer()), builder.load(
                qayzj__kofh), builder.bitcast(ketxw__etgr.data, lir.IntType
                (8).as_pointer()), xou__daaf.meminfo, ketxw__etgr.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        else:
            lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            xqn__wxyn = cgutils.get_or_insert_function(builder.module,
                lod__paal, name='nullable_array_to_info')
            return builder.call(xqn__wxyn, [sspa__jwy, builder.bitcast(
                xou__daaf.data, lir.IntType(8).as_pointer()), builder.load(
                qayzj__kofh), builder.bitcast(ketxw__etgr.data, lir.IntType
                (8).as_pointer()), xou__daaf.meminfo, ketxw__etgr.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        otgi__mxtnl = context.make_array(arr_type.arr_type)(context,
            builder, arr.left)
        jcgj__yvc = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        sspa__jwy = builder.extract_value(otgi__mxtnl.shape, 0)
        oase__pxb = numba_to_c_type(arr_type.arr_type.dtype)
        qayzj__kofh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), oase__pxb))
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='interval_array_to_info')
        return builder.call(xqn__wxyn, [sspa__jwy, builder.bitcast(
            otgi__mxtnl.data, lir.IntType(8).as_pointer()), builder.bitcast
            (jcgj__yvc.data, lir.IntType(8).as_pointer()), builder.load(
            qayzj__kofh), otgi__mxtnl.meminfo, jcgj__yvc.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    mceo__jiz = cgutils.alloca_once(builder, lir.IntType(64))
    ngtq__cvlrs = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    oduvq__prbgo = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer(), lir.IntType(8).as_pointer().
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    xqn__wxyn = cgutils.get_or_insert_function(builder.module, lod__paal,
        name='info_to_numpy_array')
    builder.call(xqn__wxyn, [in_info, mceo__jiz, ngtq__cvlrs, oduvq__prbgo])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    zaz__vbxpo = context.get_value_type(types.intp)
    ycow__ouum = cgutils.pack_array(builder, [builder.load(mceo__jiz)], ty=
        zaz__vbxpo)
    umpl__cxm = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    uvc__vvg = cgutils.pack_array(builder, [umpl__cxm], ty=zaz__vbxpo)
    fwq__mtyy = builder.bitcast(builder.load(ngtq__cvlrs), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=fwq__mtyy, shape=ycow__ouum,
        strides=uvc__vvg, itemsize=umpl__cxm, meminfo=builder.load(
        oduvq__prbgo))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    epw__payyv = context.make_helper(builder, arr_type)
    lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer
        (), lir.IntType(8).as_pointer().as_pointer()])
    xqn__wxyn = cgutils.get_or_insert_function(builder.module, lod__paal,
        name='info_to_list_string_array')
    builder.call(xqn__wxyn, [in_info, epw__payyv._get_ptr_by_name('meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return epw__payyv._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    lqx__lxceg = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        wux__bni = lengths_pos
        uysa__faf = infos_pos
        wyzd__jmar, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        ejpx__kij = ArrayItemArrayPayloadType(arr_typ)
        ttd__bmz = context.get_data_type(ejpx__kij)
        rdr__zozbx = context.get_abi_sizeof(ttd__bmz)
        suoco__vzlcw = define_array_item_dtor(context, builder, arr_typ,
            ejpx__kij)
        seers__nnv = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, rdr__zozbx), suoco__vzlcw)
        akjtw__zei = context.nrt.meminfo_data(builder, seers__nnv)
        wdzi__qjfic = builder.bitcast(akjtw__zei, ttd__bmz.as_pointer())
        nzr__xjp = cgutils.create_struct_proxy(ejpx__kij)(context, builder)
        nzr__xjp.n_arrays = builder.extract_value(builder.load(lengths_ptr),
            wux__bni)
        nzr__xjp.data = wyzd__jmar
        gnfk__cjk = builder.load(array_infos_ptr)
        jbiu__fqsw = builder.bitcast(builder.extract_value(gnfk__cjk,
            uysa__faf), lqx__lxceg)
        nzr__xjp.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, jbiu__fqsw)
        gvha__sbyb = builder.bitcast(builder.extract_value(gnfk__cjk, 
            uysa__faf + 1), lqx__lxceg)
        nzr__xjp.null_bitmap = _lower_info_to_array_numpy(types.Array(types
            .uint8, 1, 'C'), context, builder, gvha__sbyb)
        builder.store(nzr__xjp._getvalue(), wdzi__qjfic)
        wlxkd__lct = context.make_helper(builder, arr_typ)
        wlxkd__lct.meminfo = seers__nnv
        return wlxkd__lct._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        yqdbp__fvl = []
        uysa__faf = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for efdun__wyks in arr_typ.data:
            wyzd__jmar, lengths_pos, infos_pos = nested_to_array(context,
                builder, efdun__wyks, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            yqdbp__fvl.append(wyzd__jmar)
        ejpx__kij = StructArrayPayloadType(arr_typ.data)
        ttd__bmz = context.get_value_type(ejpx__kij)
        rdr__zozbx = context.get_abi_sizeof(ttd__bmz)
        suoco__vzlcw = define_struct_arr_dtor(context, builder, arr_typ,
            ejpx__kij)
        seers__nnv = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, rdr__zozbx), suoco__vzlcw)
        akjtw__zei = context.nrt.meminfo_data(builder, seers__nnv)
        wdzi__qjfic = builder.bitcast(akjtw__zei, ttd__bmz.as_pointer())
        nzr__xjp = cgutils.create_struct_proxy(ejpx__kij)(context, builder)
        nzr__xjp.data = cgutils.pack_array(builder, yqdbp__fvl
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, yqdbp__fvl)
        gnfk__cjk = builder.load(array_infos_ptr)
        gvha__sbyb = builder.bitcast(builder.extract_value(gnfk__cjk,
            uysa__faf), lqx__lxceg)
        nzr__xjp.null_bitmap = _lower_info_to_array_numpy(types.Array(types
            .uint8, 1, 'C'), context, builder, gvha__sbyb)
        builder.store(nzr__xjp._getvalue(), wdzi__qjfic)
        damlb__nya = context.make_helper(builder, arr_typ)
        damlb__nya.meminfo = seers__nnv
        return damlb__nya._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        gnfk__cjk = builder.load(array_infos_ptr)
        hhet__ogefr = builder.bitcast(builder.extract_value(gnfk__cjk,
            infos_pos), lqx__lxceg)
        ypm__bpzra = context.make_helper(builder, arr_typ)
        eca__qfd = ArrayItemArrayType(char_arr_type)
        wlxkd__lct = context.make_helper(builder, eca__qfd)
        lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='info_to_string_array')
        builder.call(xqn__wxyn, [hhet__ogefr, wlxkd__lct._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ypm__bpzra.data = wlxkd__lct._getvalue()
        return ypm__bpzra._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        gnfk__cjk = builder.load(array_infos_ptr)
        sxqa__mqeg = builder.bitcast(builder.extract_value(gnfk__cjk, 
            infos_pos + 1), lqx__lxceg)
        return _lower_info_to_array_numpy(arr_typ, context, builder, sxqa__mqeg
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        guoo__scp = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            guoo__scp = int128_type
        elif arr_typ == datetime_date_array_type:
            guoo__scp = types.int64
        gnfk__cjk = builder.load(array_infos_ptr)
        gvha__sbyb = builder.bitcast(builder.extract_value(gnfk__cjk,
            infos_pos), lqx__lxceg)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, gvha__sbyb)
        sxqa__mqeg = builder.bitcast(builder.extract_value(gnfk__cjk, 
            infos_pos + 1), lqx__lxceg)
        arr.data = _lower_info_to_array_numpy(types.Array(guoo__scp, 1, 'C'
            ), context, builder, sxqa__mqeg)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, oqsci__ujzcy = args
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        return _lower_info_to_array_list_string_array(arr_type, context,
            builder, in_info)
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType,
        StructArrayType, TupleArrayType)):

        def get_num_arrays(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 1 + get_num_arrays(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_arrays(efdun__wyks) for efdun__wyks in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(efdun__wyks) for efdun__wyks in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            ulf__kkejq = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            ulf__kkejq = _get_map_arr_data_type(arr_type)
        else:
            ulf__kkejq = arr_type
        dtv__tvihn = get_num_arrays(ulf__kkejq)
        vdre__imejt = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), 0) for oqsci__ujzcy in range(dtv__tvihn)])
        lengths_ptr = cgutils.alloca_once_value(builder, vdre__imejt)
        oea__kpql = lir.Constant(lir.IntType(8).as_pointer(), None)
        jbz__aurqz = cgutils.pack_array(builder, [oea__kpql for
            oqsci__ujzcy in range(get_num_infos(ulf__kkejq))])
        array_infos_ptr = cgutils.alloca_once_value(builder, jbz__aurqz)
        lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='info_to_nested_array')
        builder.call(xqn__wxyn, [in_info, builder.bitcast(lengths_ptr, lir.
            IntType(64).as_pointer()), builder.bitcast(array_infos_ptr, lir
            .IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, oqsci__ujzcy, oqsci__ujzcy = nested_to_array(context, builder,
            ulf__kkejq, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            seycj__sae = context.make_helper(builder, arr_type)
            seycj__sae.data = arr
            context.nrt.incref(builder, ulf__kkejq, arr)
            arr = seycj__sae._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, ulf__kkejq)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        ypm__bpzra = context.make_helper(builder, arr_type)
        eca__qfd = ArrayItemArrayType(char_arr_type)
        wlxkd__lct = context.make_helper(builder, eca__qfd)
        lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='info_to_string_array')
        builder.call(xqn__wxyn, [in_info, wlxkd__lct._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        ypm__bpzra.data = wlxkd__lct._getvalue()
        return ypm__bpzra._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='get_nested_info')
        inzfi__hgyzx = builder.call(xqn__wxyn, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        qnve__ghlgg = builder.call(xqn__wxyn, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        kzak__ivu = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        kzak__ivu.data = info_to_array_codegen(context, builder, sig, (
            inzfi__hgyzx, context.get_constant_null(arr_type.data)))
        ywek__shyeu = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = ywek__shyeu(array_info_type, ywek__shyeu)
        kzak__ivu.indices = info_to_array_codegen(context, builder, sig, (
            qnve__ghlgg, context.get_constant_null(ywek__shyeu)))
        lod__paal = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='get_has_global_dictionary')
        dso__dfx = builder.call(xqn__wxyn, [in_info])
        kzak__ivu.has_global_dictionary = builder.trunc(dso__dfx, cgutils.
            bool_t)
        return kzak__ivu._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        zri__gxjnt = get_categories_int_type(arr_type.dtype)
        qqdcl__lpx = types.Array(zri__gxjnt, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(qqdcl__lpx, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            fqb__yjwv = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(fqb__yjwv))
            int_type = arr_type.dtype.int_type
            jcmgz__jewoq = arr_type.dtype.data.data
            lte__mtn = context.get_constant_generic(builder, jcmgz__jewoq,
                fqb__yjwv)
            bqsb__xxelr = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(jcmgz__jewoq), [lte__mtn])
        else:
            bqsb__xxelr = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, bqsb__xxelr)
        out_arr.dtype = bqsb__xxelr
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        fwq__mtyy = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = fwq__mtyy
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        guoo__scp = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            guoo__scp = int128_type
        elif arr_type == datetime_date_array_type:
            guoo__scp = types.int64
        sqakr__vbsc = types.Array(guoo__scp, 1, 'C')
        xou__daaf = context.make_array(sqakr__vbsc)(context, builder)
        avp__vilp = types.Array(types.uint8, 1, 'C')
        aazra__pabl = context.make_array(avp__vilp)(context, builder)
        mceo__jiz = cgutils.alloca_once(builder, lir.IntType(64))
        sri__mbu = cgutils.alloca_once(builder, lir.IntType(64))
        ngtq__cvlrs = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        hwq__luk = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        oduvq__prbgo = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        ymrfh__zrh = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='info_to_nullable_array')
        builder.call(xqn__wxyn, [in_info, mceo__jiz, sri__mbu, ngtq__cvlrs,
            hwq__luk, oduvq__prbgo, ymrfh__zrh])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        zaz__vbxpo = context.get_value_type(types.intp)
        ycow__ouum = cgutils.pack_array(builder, [builder.load(mceo__jiz)],
            ty=zaz__vbxpo)
        umpl__cxm = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(guoo__scp)))
        uvc__vvg = cgutils.pack_array(builder, [umpl__cxm], ty=zaz__vbxpo)
        fwq__mtyy = builder.bitcast(builder.load(ngtq__cvlrs), context.
            get_data_type(guoo__scp).as_pointer())
        numba.np.arrayobj.populate_array(xou__daaf, data=fwq__mtyy, shape=
            ycow__ouum, strides=uvc__vvg, itemsize=umpl__cxm, meminfo=
            builder.load(oduvq__prbgo))
        arr.data = xou__daaf._getvalue()
        ycow__ouum = cgutils.pack_array(builder, [builder.load(sri__mbu)],
            ty=zaz__vbxpo)
        umpl__cxm = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(types.uint8)))
        uvc__vvg = cgutils.pack_array(builder, [umpl__cxm], ty=zaz__vbxpo)
        fwq__mtyy = builder.bitcast(builder.load(hwq__luk), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(aazra__pabl, data=fwq__mtyy, shape
            =ycow__ouum, strides=uvc__vvg, itemsize=umpl__cxm, meminfo=
            builder.load(ymrfh__zrh))
        arr.null_bitmap = aazra__pabl._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        otgi__mxtnl = context.make_array(arr_type.arr_type)(context, builder)
        jcgj__yvc = context.make_array(arr_type.arr_type)(context, builder)
        mceo__jiz = cgutils.alloca_once(builder, lir.IntType(64))
        fdl__jtvm = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        fvwie__lmr = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        xxa__dpg = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        zlk__beid = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='info_to_interval_array')
        builder.call(xqn__wxyn, [in_info, mceo__jiz, fdl__jtvm, fvwie__lmr,
            xxa__dpg, zlk__beid])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        zaz__vbxpo = context.get_value_type(types.intp)
        ycow__ouum = cgutils.pack_array(builder, [builder.load(mceo__jiz)],
            ty=zaz__vbxpo)
        umpl__cxm = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(arr_type.arr_type.dtype)))
        uvc__vvg = cgutils.pack_array(builder, [umpl__cxm], ty=zaz__vbxpo)
        svoln__ykpxu = builder.bitcast(builder.load(fdl__jtvm), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(otgi__mxtnl, data=svoln__ykpxu,
            shape=ycow__ouum, strides=uvc__vvg, itemsize=umpl__cxm, meminfo
            =builder.load(xxa__dpg))
        arr.left = otgi__mxtnl._getvalue()
        ymxt__lbh = builder.bitcast(builder.load(fvwie__lmr), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(jcgj__yvc, data=ymxt__lbh, shape=
            ycow__ouum, strides=uvc__vvg, itemsize=umpl__cxm, meminfo=
            builder.load(zlk__beid))
        arr.right = jcgj__yvc._getvalue()
        return arr._getvalue()
    raise_bodo_error(f'info_to_array(): array type {arr_type} is not supported'
        )


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type, 'info_to_array: expected info type'
    return arr_type(info_type, array_type), info_to_array_codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        sspa__jwy, oqsci__ujzcy = args
        oase__pxb = numba_to_c_type(array_type.dtype)
        qayzj__kofh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), oase__pxb))
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='alloc_numpy')
        return builder.call(xqn__wxyn, [sspa__jwy, builder.load(qayzj__kofh)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        sspa__jwy, ihcyk__mvxe = args
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='alloc_string_array')
        return builder.call(xqn__wxyn, [sspa__jwy, ihcyk__mvxe])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    opzpf__ybvoo, = args
    sdqw__yft = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], opzpf__ybvoo)
    lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer().as_pointer(), lir.IntType(64)])
    xqn__wxyn = cgutils.get_or_insert_function(builder.module, lod__paal,
        name='arr_info_list_to_table')
    return builder.call(xqn__wxyn, [sdqw__yft.data, sdqw__yft.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='info_from_table')
        return builder.call(xqn__wxyn, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    jzeus__ukl = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, ajl__mfoqv, oqsci__ujzcy = args
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='info_from_table')
        hiepc__anmxq = cgutils.create_struct_proxy(jzeus__ukl)(context, builder
            )
        hiepc__anmxq.parent = cgutils.get_null_value(hiepc__anmxq.parent.type)
        bpj__zufu = context.make_array(table_idx_arr_t)(context, builder,
            ajl__mfoqv)
        qviu__oxax = context.get_constant(types.int64, -1)
        bkdm__znq = context.get_constant(types.int64, 0)
        uhqe__yoe = cgutils.alloca_once_value(builder, bkdm__znq)
        for t, gdef__casxq in jzeus__ukl.type_to_blk.items():
            icnu__egf = context.get_constant(types.int64, len(jzeus__ukl.
                block_to_arr_ind[gdef__casxq]))
            oqsci__ujzcy, sfkw__mav = ListInstance.allocate_ex(context,
                builder, types.List(t), icnu__egf)
            sfkw__mav.size = icnu__egf
            atfh__knuda = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(jzeus__ukl.block_to_arr_ind[
                gdef__casxq], dtype=np.int64))
            jakiz__vocrk = context.make_array(types.Array(types.int64, 1, 'C')
                )(context, builder, atfh__knuda)
            with cgutils.for_range(builder, icnu__egf) as gghbg__eprk:
                uetg__nwg = gghbg__eprk.index
                qigdw__yiuz = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    jakiz__vocrk, uetg__nwg)
                nctj__ugasf = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, bpj__zufu, qigdw__yiuz)
                iok__rhflh = builder.icmp_unsigned('!=', nctj__ugasf,
                    qviu__oxax)
                with builder.if_else(iok__rhflh) as (clmr__yqbuj, jvqda__kbtjd
                    ):
                    with clmr__yqbuj:
                        brs__cyde = builder.call(xqn__wxyn, [cpp_table,
                            nctj__ugasf])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            brs__cyde])
                        sfkw__mav.inititem(uetg__nwg, arr, incref=False)
                        sspa__jwy = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(sspa__jwy, uhqe__yoe)
                    with jvqda__kbtjd:
                        djon__cyyxw = context.get_constant_null(t)
                        sfkw__mav.inititem(uetg__nwg, djon__cyyxw, incref=False
                            )
            setattr(hiepc__anmxq, f'block_{gdef__casxq}', sfkw__mav.value)
        hiepc__anmxq.len = builder.load(uhqe__yoe)
        return hiepc__anmxq._getvalue()
    return jzeus__ukl(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    hgqsg__bzg = out_col_inds_t.instance_type.meta
    jzeus__ukl = unwrap_typeref(out_types_t.types[0])
    urss__gee = [unwrap_typeref(out_types_t.types[uetg__nwg]) for uetg__nwg in
        range(1, len(out_types_t.types))]
    khg__yvlt = {}
    uyfs__djjg = get_overload_const_int(n_table_cols_t)
    onhf__drtre = {qii__wabfr: uetg__nwg for uetg__nwg, qii__wabfr in
        enumerate(hgqsg__bzg)}
    if not is_overload_none(unknown_cat_arrs_t):
        sctp__ujx = {yub__sovvb: uetg__nwg for uetg__nwg, yub__sovvb in
            enumerate(cat_inds_t.instance_type.meta)}
    bwdx__mzwlo = []
    hkwxh__rnew = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(jzeus__ukl, bodo.TableType):
        hkwxh__rnew += f'  py_table = init_table(py_table_type, False)\n'
        hkwxh__rnew += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for ipuo__hcg, gdef__casxq in jzeus__ukl.type_to_blk.items():
            res__gywqg = [onhf__drtre.get(uetg__nwg, -1) for uetg__nwg in
                jzeus__ukl.block_to_arr_ind[gdef__casxq]]
            khg__yvlt[f'out_inds_{gdef__casxq}'] = np.array(res__gywqg, np.
                int64)
            khg__yvlt[f'out_type_{gdef__casxq}'] = ipuo__hcg
            khg__yvlt[f'typ_list_{gdef__casxq}'] = types.List(ipuo__hcg)
            wlc__eojju = f'out_type_{gdef__casxq}'
            if type_has_unknown_cats(ipuo__hcg):
                if is_overload_none(unknown_cat_arrs_t):
                    hkwxh__rnew += f"""  in_arr_list_{gdef__casxq} = get_table_block(out_types_t[0], {gdef__casxq})
"""
                    wlc__eojju = f'in_arr_list_{gdef__casxq}[i]'
                else:
                    khg__yvlt[f'cat_arr_inds_{gdef__casxq}'] = np.array([
                        sctp__ujx.get(uetg__nwg, -1) for uetg__nwg in
                        jzeus__ukl.block_to_arr_ind[gdef__casxq]], np.int64)
                    wlc__eojju = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{gdef__casxq}[i]]')
            icnu__egf = len(jzeus__ukl.block_to_arr_ind[gdef__casxq])
            hkwxh__rnew += f"""  arr_list_{gdef__casxq} = alloc_list_like(typ_list_{gdef__casxq}, {icnu__egf}, False)
"""
            hkwxh__rnew += f'  for i in range(len(arr_list_{gdef__casxq})):\n'
            hkwxh__rnew += (
                f'    cpp_ind_{gdef__casxq} = out_inds_{gdef__casxq}[i]\n')
            hkwxh__rnew += f'    if cpp_ind_{gdef__casxq} == -1:\n'
            hkwxh__rnew += f'      continue\n'
            hkwxh__rnew += f"""    arr_{gdef__casxq} = info_to_array(info_from_table(cpp_table, cpp_ind_{gdef__casxq}), {wlc__eojju})
"""
            hkwxh__rnew += (
                f'    arr_list_{gdef__casxq}[i] = arr_{gdef__casxq}\n')
            hkwxh__rnew += f"""  py_table = set_table_block(py_table, arr_list_{gdef__casxq}, {gdef__casxq})
"""
        bwdx__mzwlo.append('py_table')
    elif jzeus__ukl != types.none:
        ccnm__ltgc = onhf__drtre.get(0, -1)
        if ccnm__ltgc != -1:
            khg__yvlt[f'arr_typ_arg0'] = jzeus__ukl
            wlc__eojju = f'arr_typ_arg0'
            if type_has_unknown_cats(jzeus__ukl):
                if is_overload_none(unknown_cat_arrs_t):
                    wlc__eojju = f'out_types_t[0]'
                else:
                    wlc__eojju = f'unknown_cat_arrs_t[{sctp__ujx[0]}]'
            hkwxh__rnew += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {ccnm__ltgc}), {wlc__eojju})
"""
            bwdx__mzwlo.append('out_arg0')
    for uetg__nwg, t in enumerate(urss__gee):
        ccnm__ltgc = onhf__drtre.get(uyfs__djjg + uetg__nwg, -1)
        if ccnm__ltgc != -1:
            khg__yvlt[f'extra_arr_type_{uetg__nwg}'] = t
            wlc__eojju = f'extra_arr_type_{uetg__nwg}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    wlc__eojju = f'out_types_t[{uetg__nwg + 1}]'
                else:
                    wlc__eojju = (
                        f'unknown_cat_arrs_t[{sctp__ujx[uyfs__djjg + uetg__nwg]}]'
                        )
            hkwxh__rnew += f"""  out_{uetg__nwg} = info_to_array(info_from_table(cpp_table, {ccnm__ltgc}), {wlc__eojju})
"""
            bwdx__mzwlo.append(f'out_{uetg__nwg}')
    dcfs__lqhnn = ',' if len(bwdx__mzwlo) == 1 else ''
    hkwxh__rnew += f"  return ({', '.join(bwdx__mzwlo)}{dcfs__lqhnn})\n"
    khg__yvlt.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(hgqsg__bzg), 'py_table_type': jzeus__ukl})
    hqni__mvyif = {}
    exec(hkwxh__rnew, khg__yvlt, hqni__mvyif)
    return hqni__mvyif['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    jzeus__ukl = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, oqsci__ujzcy = args
        tgs__kguc = cgutils.create_struct_proxy(jzeus__ukl)(context,
            builder, py_table)
        if jzeus__ukl.has_runtime_cols:
            mrple__xtfva = lir.Constant(lir.IntType(64), 0)
            for gdef__casxq, t in enumerate(jzeus__ukl.arr_types):
                raao__amadu = getattr(tgs__kguc, f'block_{gdef__casxq}')
                wat__hsinl = ListInstance(context, builder, types.List(t),
                    raao__amadu)
                mrple__xtfva = builder.add(mrple__xtfva, wat__hsinl.size)
        else:
            mrple__xtfva = lir.Constant(lir.IntType(64), len(jzeus__ukl.
                arr_types))
        oqsci__ujzcy, yiv__ppt = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), mrple__xtfva)
        yiv__ppt.size = mrple__xtfva
        if jzeus__ukl.has_runtime_cols:
            woeev__dmv = lir.Constant(lir.IntType(64), 0)
            for gdef__casxq, t in enumerate(jzeus__ukl.arr_types):
                raao__amadu = getattr(tgs__kguc, f'block_{gdef__casxq}')
                wat__hsinl = ListInstance(context, builder, types.List(t),
                    raao__amadu)
                icnu__egf = wat__hsinl.size
                with cgutils.for_range(builder, icnu__egf) as gghbg__eprk:
                    uetg__nwg = gghbg__eprk.index
                    arr = wat__hsinl.getitem(uetg__nwg)
                    uxlec__vog = signature(array_info_type, t)
                    cuacs__byqku = arr,
                    vhp__ldy = array_to_info_codegen(context, builder,
                        uxlec__vog, cuacs__byqku)
                    yiv__ppt.inititem(builder.add(woeev__dmv, uetg__nwg),
                        vhp__ldy, incref=False)
                woeev__dmv = builder.add(woeev__dmv, icnu__egf)
        else:
            for t, gdef__casxq in jzeus__ukl.type_to_blk.items():
                icnu__egf = context.get_constant(types.int64, len(
                    jzeus__ukl.block_to_arr_ind[gdef__casxq]))
                raao__amadu = getattr(tgs__kguc, f'block_{gdef__casxq}')
                wat__hsinl = ListInstance(context, builder, types.List(t),
                    raao__amadu)
                atfh__knuda = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(jzeus__ukl.
                    block_to_arr_ind[gdef__casxq], dtype=np.int64))
                jakiz__vocrk = context.make_array(types.Array(types.int64, 
                    1, 'C'))(context, builder, atfh__knuda)
                with cgutils.for_range(builder, icnu__egf) as gghbg__eprk:
                    uetg__nwg = gghbg__eprk.index
                    qigdw__yiuz = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), jakiz__vocrk, uetg__nwg)
                    vow__wpysb = signature(types.none, jzeus__ukl, types.
                        List(t), types.int64, types.int64)
                    tvft__xhr = py_table, raao__amadu, uetg__nwg, qigdw__yiuz
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, vow__wpysb, tvft__xhr)
                    arr = wat__hsinl.getitem(uetg__nwg)
                    uxlec__vog = signature(array_info_type, t)
                    cuacs__byqku = arr,
                    vhp__ldy = array_to_info_codegen(context, builder,
                        uxlec__vog, cuacs__byqku)
                    yiv__ppt.inititem(qigdw__yiuz, vhp__ldy, incref=False)
        ryfhi__vwqxb = yiv__ppt.value
        ihdvo__huz = signature(table_type, types.List(array_info_type))
        ldb__bvg = ryfhi__vwqxb,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            ihdvo__huz, ldb__bvg)
        context.nrt.decref(builder, types.List(array_info_type), ryfhi__vwqxb)
        return cpp_table
    return table_type(jzeus__ukl, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    mbela__drjby = in_col_inds_t.instance_type.meta
    khg__yvlt = {}
    uyfs__djjg = get_overload_const_int(n_table_cols_t)
    zchlp__yvqh = defaultdict(list)
    onhf__drtre = {}
    for uetg__nwg, qii__wabfr in enumerate(mbela__drjby):
        if qii__wabfr in onhf__drtre:
            zchlp__yvqh[qii__wabfr].append(uetg__nwg)
        else:
            onhf__drtre[qii__wabfr] = uetg__nwg
    hkwxh__rnew = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    hkwxh__rnew += (
        f'  cpp_arr_list = alloc_empty_list_type({len(mbela__drjby)}, array_info_type)\n'
        )
    if py_table != types.none:
        for gdef__casxq in py_table.type_to_blk.values():
            res__gywqg = [onhf__drtre.get(uetg__nwg, -1) for uetg__nwg in
                py_table.block_to_arr_ind[gdef__casxq]]
            khg__yvlt[f'out_inds_{gdef__casxq}'] = np.array(res__gywqg, np.
                int64)
            khg__yvlt[f'arr_inds_{gdef__casxq}'] = np.array(py_table.
                block_to_arr_ind[gdef__casxq], np.int64)
            hkwxh__rnew += (
                f'  arr_list_{gdef__casxq} = get_table_block(py_table, {gdef__casxq})\n'
                )
            hkwxh__rnew += f'  for i in range(len(arr_list_{gdef__casxq})):\n'
            hkwxh__rnew += (
                f'    out_arr_ind_{gdef__casxq} = out_inds_{gdef__casxq}[i]\n')
            hkwxh__rnew += f'    if out_arr_ind_{gdef__casxq} == -1:\n'
            hkwxh__rnew += f'      continue\n'
            hkwxh__rnew += (
                f'    arr_ind_{gdef__casxq} = arr_inds_{gdef__casxq}[i]\n')
            hkwxh__rnew += f"""    ensure_column_unboxed(py_table, arr_list_{gdef__casxq}, i, arr_ind_{gdef__casxq})
"""
            hkwxh__rnew += f"""    cpp_arr_list[out_arr_ind_{gdef__casxq}] = array_to_info(arr_list_{gdef__casxq}[i])
"""
        for dove__mktz, oda__pipx in zchlp__yvqh.items():
            if dove__mktz < uyfs__djjg:
                gdef__casxq = py_table.block_nums[dove__mktz]
                gpvn__qdb = py_table.block_offsets[dove__mktz]
                for ccnm__ltgc in oda__pipx:
                    hkwxh__rnew += f"""  cpp_arr_list[{ccnm__ltgc}] = array_to_info(arr_list_{gdef__casxq}[{gpvn__qdb}])
"""
    for uetg__nwg in range(len(extra_arrs_tup)):
        wdqnx__qfk = onhf__drtre.get(uyfs__djjg + uetg__nwg, -1)
        if wdqnx__qfk != -1:
            xsd__urdi = [wdqnx__qfk] + zchlp__yvqh.get(uyfs__djjg +
                uetg__nwg, [])
            for ccnm__ltgc in xsd__urdi:
                hkwxh__rnew += f"""  cpp_arr_list[{ccnm__ltgc}] = array_to_info(extra_arrs_tup[{uetg__nwg}])
"""
    hkwxh__rnew += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    khg__yvlt.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    hqni__mvyif = {}
    exec(hkwxh__rnew, khg__yvlt, hqni__mvyif)
    return hqni__mvyif['impl']


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))
decref_table_array = types.ExternalFunction('decref_table_array', types.
    void(table_type, types.int32))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='delete_table')
        builder.call(xqn__wxyn, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='shuffle_table')
        tchf__oyhow = builder.call(xqn__wxyn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    return table_type(table_t, types.int64, types.boolean, types.int32
        ), codegen


class ShuffleInfoType(types.Type):

    def __init__(self):
        super(ShuffleInfoType, self).__init__(name='ShuffleInfoType()')


shuffle_info_type = ShuffleInfoType()
register_model(ShuffleInfoType)(models.OpaqueModel)
get_shuffle_info = types.ExternalFunction('get_shuffle_info',
    shuffle_info_type(table_type))


@intrinsic
def delete_shuffle_info(typingctx, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[0] == types.none:
            return
        lod__paal = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='delete_shuffle_info')
        return builder.call(xqn__wxyn, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='reverse_shuffle_table')
        return builder.call(xqn__wxyn, args)
    return table_type(table_type, shuffle_info_t), codegen


@intrinsic
def get_null_shuffle_info(typingctx):

    def codegen(context, builder, sig, args):
        return context.get_constant_null(sig.return_type)
    return shuffle_info_type(), codegen


@intrinsic
def hash_join_table(typingctx, left_table_t, right_table_t, left_parallel_t,
    right_parallel_t, n_keys_t, n_data_left_t, n_data_right_t, same_vect_t,
    key_in_out_t, same_need_typechange_t, is_left_t, is_right_t, is_join_t,
    extra_data_col_t, indicator, _bodo_na_equal, cond_func, left_col_nums,
    left_col_nums_len, right_col_nums, right_col_nums_len, num_rows_ptr_t):
    assert left_table_t == table_type
    assert right_table_t == table_type

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='hash_join_table')
        tchf__oyhow = builder.call(xqn__wxyn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.boolean, types.voidptr,
        types.voidptr, types.int64, types.voidptr, types.int64, types.voidptr
        ), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, dead_keys_t, n_rows_t, parallel_t):
    assert table_t == table_type, 'C++ table type expected'

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='sort_values_table')
        tchf__oyhow = builder.call(xqn__wxyn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='sample_table')
        tchf__oyhow = builder.call(xqn__wxyn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='shuffle_renormalization')
        tchf__oyhow = builder.call(xqn__wxyn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='shuffle_renormalization_group')
        tchf__oyhow = builder.call(xqn__wxyn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='drop_duplicates_table')
        tchf__oyhow = builder.call(xqn__wxyn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    return table_type(table_t, types.boolean, types.int64, types.int64,
        types.boolean, types.boolean), codegen


@intrinsic
def groupby_and_aggregate(typingctx, table_t, n_keys_t, input_has_index,
    ftypes, func_offsets, udf_n_redvars, is_parallel, skipdropna_t,
    shift_periods_t, transform_func, head_n, return_keys, return_index,
    dropna, update_cb, combine_cb, eval_cb, general_udfs_cb,
    udf_table_dummy_t, n_out_rows_t, n_shuffle_keys_t):
    assert table_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        xqn__wxyn = cgutils.get_or_insert_function(builder.module,
            lod__paal, name='groupby_and_aggregate')
        tchf__oyhow = builder.call(xqn__wxyn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return tchf__oyhow
    return table_type(table_t, types.int64, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        int64, types.int64, types.int64, types.boolean, types.boolean,
        types.boolean, types.voidptr, types.voidptr, types.voidptr, types.
        voidptr, table_t, types.voidptr, types.int64), codegen


get_groupby_labels = types.ExternalFunction('get_groupby_labels', types.
    int64(table_type, types.voidptr, types.voidptr, types.boolean, types.bool_)
    )
_array_isin = types.ExternalFunction('array_isin', types.void(
    array_info_type, array_info_type, array_info_type, types.bool_))


@numba.njit(no_cpython_wrapper=True)
def array_isin(out_arr, in_arr, in_values, is_parallel):
    in_arr = decode_if_dict_array(in_arr)
    in_values = decode_if_dict_array(in_values)
    gkog__cbql = array_to_info(in_arr)
    cic__vfus = array_to_info(in_values)
    btti__yan = array_to_info(out_arr)
    hkkxi__xcqn = arr_info_list_to_table([gkog__cbql, cic__vfus, btti__yan])
    _array_isin(btti__yan, gkog__cbql, cic__vfus, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(hkkxi__xcqn)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    gkog__cbql = array_to_info(in_arr)
    btti__yan = array_to_info(out_arr)
    _get_search_regex(gkog__cbql, case, match, pat, btti__yan)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    xbia__bwolc = col_array_typ.dtype
    if isinstance(xbia__bwolc, types.Number) or xbia__bwolc in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                hiepc__anmxq, xzg__bzw = args
                hiepc__anmxq = builder.bitcast(hiepc__anmxq, lir.IntType(8)
                    .as_pointer().as_pointer())
                jbhj__hfk = lir.Constant(lir.IntType(64), c_ind)
                fcr__zdw = builder.load(builder.gep(hiepc__anmxq, [jbhj__hfk]))
                fcr__zdw = builder.bitcast(fcr__zdw, context.get_data_type(
                    xbia__bwolc).as_pointer())
                return builder.load(builder.gep(fcr__zdw, [xzg__bzw]))
            return xbia__bwolc(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                hiepc__anmxq, xzg__bzw = args
                hiepc__anmxq = builder.bitcast(hiepc__anmxq, lir.IntType(8)
                    .as_pointer().as_pointer())
                jbhj__hfk = lir.Constant(lir.IntType(64), c_ind)
                fcr__zdw = builder.load(builder.gep(hiepc__anmxq, [jbhj__hfk]))
                lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                dek__nna = cgutils.get_or_insert_function(builder.module,
                    lod__paal, name='array_info_getitem')
                cak__wfu = cgutils.alloca_once(builder, lir.IntType(64))
                args = fcr__zdw, xzg__bzw, cak__wfu
                ngtq__cvlrs = builder.call(dek__nna, args)
                return context.make_tuple(builder, sig.return_type, [
                    ngtq__cvlrs, builder.load(cak__wfu)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                uic__dcz = lir.Constant(lir.IntType(64), 1)
                gvwns__bxyp = lir.Constant(lir.IntType(64), 2)
                hiepc__anmxq, xzg__bzw = args
                hiepc__anmxq = builder.bitcast(hiepc__anmxq, lir.IntType(8)
                    .as_pointer().as_pointer())
                jbhj__hfk = lir.Constant(lir.IntType(64), c_ind)
                fcr__zdw = builder.load(builder.gep(hiepc__anmxq, [jbhj__hfk]))
                lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64)])
                wtfgl__ihlay = cgutils.get_or_insert_function(builder.
                    module, lod__paal, name='get_nested_info')
                args = fcr__zdw, gvwns__bxyp
                thg__snry = builder.call(wtfgl__ihlay, args)
                lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer()])
                vwpl__btbv = cgutils.get_or_insert_function(builder.module,
                    lod__paal, name='array_info_getdata1')
                args = thg__snry,
                wbzf__uyb = builder.call(vwpl__btbv, args)
                wbzf__uyb = builder.bitcast(wbzf__uyb, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                lxsq__zvt = builder.sext(builder.load(builder.gep(wbzf__uyb,
                    [xzg__bzw])), lir.IntType(64))
                args = fcr__zdw, uic__dcz
                igz__irmor = builder.call(wtfgl__ihlay, args)
                lod__paal = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                dek__nna = cgutils.get_or_insert_function(builder.module,
                    lod__paal, name='array_info_getitem')
                cak__wfu = cgutils.alloca_once(builder, lir.IntType(64))
                args = igz__irmor, lxsq__zvt, cak__wfu
                ngtq__cvlrs = builder.call(dek__nna, args)
                return context.make_tuple(builder, sig.return_type, [
                    ngtq__cvlrs, builder.load(cak__wfu)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{xbia__bwolc}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType
        ) or col_array_dtype in (bodo.libs.bool_arr_ext.boolean_array, bodo
        .binary_array_type) or is_str_arr_type(col_array_dtype) or isinstance(
        col_array_dtype, types.Array
        ) and col_array_dtype.dtype == bodo.datetime_date_type:

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                yke__mdvv, xzg__bzw = args
                yke__mdvv = builder.bitcast(yke__mdvv, lir.IntType(8).
                    as_pointer().as_pointer())
                jbhj__hfk = lir.Constant(lir.IntType(64), c_ind)
                fcr__zdw = builder.load(builder.gep(yke__mdvv, [jbhj__hfk]))
                tggha__fkh = builder.bitcast(fcr__zdw, context.
                    get_data_type(types.bool_).as_pointer())
                gbsct__eaf = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    tggha__fkh, xzg__bzw)
                plw__dmq = builder.icmp_unsigned('!=', gbsct__eaf, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(plw__dmq, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        xbia__bwolc = col_array_dtype.dtype
        if xbia__bwolc in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    hiepc__anmxq, xzg__bzw = args
                    hiepc__anmxq = builder.bitcast(hiepc__anmxq, lir.
                        IntType(8).as_pointer().as_pointer())
                    jbhj__hfk = lir.Constant(lir.IntType(64), c_ind)
                    fcr__zdw = builder.load(builder.gep(hiepc__anmxq, [
                        jbhj__hfk]))
                    fcr__zdw = builder.bitcast(fcr__zdw, context.
                        get_data_type(xbia__bwolc).as_pointer())
                    oeeb__sgi = builder.load(builder.gep(fcr__zdw, [xzg__bzw]))
                    plw__dmq = builder.icmp_unsigned('!=', oeeb__sgi, lir.
                        Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(plw__dmq, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(xbia__bwolc, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    hiepc__anmxq, xzg__bzw = args
                    hiepc__anmxq = builder.bitcast(hiepc__anmxq, lir.
                        IntType(8).as_pointer().as_pointer())
                    jbhj__hfk = lir.Constant(lir.IntType(64), c_ind)
                    fcr__zdw = builder.load(builder.gep(hiepc__anmxq, [
                        jbhj__hfk]))
                    fcr__zdw = builder.bitcast(fcr__zdw, context.
                        get_data_type(xbia__bwolc).as_pointer())
                    oeeb__sgi = builder.load(builder.gep(fcr__zdw, [xzg__bzw]))
                    xjrjj__ebuw = signature(types.bool_, xbia__bwolc)
                    gbsct__eaf = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, xjrjj__ebuw, (oeeb__sgi,))
                    return builder.not_(builder.sext(gbsct__eaf, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
