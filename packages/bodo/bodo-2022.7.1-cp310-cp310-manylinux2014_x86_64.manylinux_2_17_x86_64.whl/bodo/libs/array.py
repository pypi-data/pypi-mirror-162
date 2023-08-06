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
        zomkx__biiw = context.make_helper(builder, arr_type, in_arr)
        in_arr = zomkx__biiw.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        yqjl__xhhfq = context.make_helper(builder, arr_type, in_arr)
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='list_string_array_to_info')
        return builder.call(betpo__xin, [yqjl__xhhfq.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                phuyq__cxqj = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for ovnx__swb in arr_typ.data:
                    phuyq__cxqj += get_types(ovnx__swb)
                return phuyq__cxqj
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
            jck__ikgu = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                ikj__dafp = context.make_helper(builder, arr_typ, value=arr)
                llbzb__ksbbb = get_lengths(_get_map_arr_data_type(arr_typ),
                    ikj__dafp.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                zds__enbes = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                llbzb__ksbbb = get_lengths(arr_typ.dtype, zds__enbes.data)
                llbzb__ksbbb = cgutils.pack_array(builder, [zds__enbes.
                    n_arrays] + [builder.extract_value(llbzb__ksbbb,
                    kazz__ruf) for kazz__ruf in range(llbzb__ksbbb.type.count)]
                    )
            elif isinstance(arr_typ, StructArrayType):
                zds__enbes = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                llbzb__ksbbb = []
                for kazz__ruf, ovnx__swb in enumerate(arr_typ.data):
                    zblyg__brrd = get_lengths(ovnx__swb, builder.
                        extract_value(zds__enbes.data, kazz__ruf))
                    llbzb__ksbbb += [builder.extract_value(zblyg__brrd,
                        yfwsa__czcey) for yfwsa__czcey in range(zblyg__brrd
                        .type.count)]
                llbzb__ksbbb = cgutils.pack_array(builder, [jck__ikgu,
                    context.get_constant(types.int64, -1)] + llbzb__ksbbb)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                llbzb__ksbbb = cgutils.pack_array(builder, [jck__ikgu])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return llbzb__ksbbb

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                ikj__dafp = context.make_helper(builder, arr_typ, value=arr)
                knkg__flzub = get_buffers(_get_map_arr_data_type(arr_typ),
                    ikj__dafp.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                zds__enbes = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                mtk__dvt = get_buffers(arr_typ.dtype, zds__enbes.data)
                quf__twx = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, zds__enbes.offsets)
                gnu__tqris = builder.bitcast(quf__twx.data, lir.IntType(8).
                    as_pointer())
                meaxm__ydryp = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, zds__enbes.null_bitmap)
                xzbv__onlr = builder.bitcast(meaxm__ydryp.data, lir.IntType
                    (8).as_pointer())
                knkg__flzub = cgutils.pack_array(builder, [gnu__tqris,
                    xzbv__onlr] + [builder.extract_value(mtk__dvt,
                    kazz__ruf) for kazz__ruf in range(mtk__dvt.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                zds__enbes = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                mtk__dvt = []
                for kazz__ruf, ovnx__swb in enumerate(arr_typ.data):
                    shr__vmzkl = get_buffers(ovnx__swb, builder.
                        extract_value(zds__enbes.data, kazz__ruf))
                    mtk__dvt += [builder.extract_value(shr__vmzkl,
                        yfwsa__czcey) for yfwsa__czcey in range(shr__vmzkl.
                        type.count)]
                meaxm__ydryp = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, zds__enbes.null_bitmap)
                xzbv__onlr = builder.bitcast(meaxm__ydryp.data, lir.IntType
                    (8).as_pointer())
                knkg__flzub = cgutils.pack_array(builder, [xzbv__onlr] +
                    mtk__dvt)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                sof__dbshi = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    sof__dbshi = int128_type
                elif arr_typ == datetime_date_array_type:
                    sof__dbshi = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                gcbbj__qqtd = context.make_array(types.Array(sof__dbshi, 1,
                    'C'))(context, builder, arr.data)
                meaxm__ydryp = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, arr.null_bitmap)
                axyn__drsr = builder.bitcast(gcbbj__qqtd.data, lir.IntType(
                    8).as_pointer())
                xzbv__onlr = builder.bitcast(meaxm__ydryp.data, lir.IntType
                    (8).as_pointer())
                knkg__flzub = cgutils.pack_array(builder, [xzbv__onlr,
                    axyn__drsr])
            elif arr_typ in (string_array_type, binary_array_type):
                zds__enbes = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                qwa__rheht = context.make_helper(builder, offset_arr_type,
                    zds__enbes.offsets).data
                fgpw__gknlt = context.make_helper(builder, char_arr_type,
                    zds__enbes.data).data
                vll__yiac = context.make_helper(builder,
                    null_bitmap_arr_type, zds__enbes.null_bitmap).data
                knkg__flzub = cgutils.pack_array(builder, [builder.bitcast(
                    qwa__rheht, lir.IntType(8).as_pointer()), builder.
                    bitcast(vll__yiac, lir.IntType(8).as_pointer()),
                    builder.bitcast(fgpw__gknlt, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                axyn__drsr = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                uowt__aaxzt = lir.Constant(lir.IntType(8).as_pointer(), None)
                knkg__flzub = cgutils.pack_array(builder, [uowt__aaxzt,
                    axyn__drsr])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return knkg__flzub

        def get_field_names(arr_typ):
            zss__mtn = []
            if isinstance(arr_typ, StructArrayType):
                for ihl__hrflq, kret__xbytx in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    zss__mtn.append(ihl__hrflq)
                    zss__mtn += get_field_names(kret__xbytx)
            elif isinstance(arr_typ, ArrayItemArrayType):
                zss__mtn += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                zss__mtn += get_field_names(_get_map_arr_data_type(arr_typ))
            return zss__mtn
        phuyq__cxqj = get_types(arr_type)
        vgksd__chqsv = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in phuyq__cxqj])
        jovl__jsyrk = cgutils.alloca_once_value(builder, vgksd__chqsv)
        llbzb__ksbbb = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, llbzb__ksbbb)
        knkg__flzub = get_buffers(arr_type, in_arr)
        yeb__pobt = cgutils.alloca_once_value(builder, knkg__flzub)
        zss__mtn = get_field_names(arr_type)
        if len(zss__mtn) == 0:
            zss__mtn = ['irrelevant']
        pmrvj__mktrr = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in zss__mtn])
        cxl__amu = cgutils.alloca_once_value(builder, pmrvj__mktrr)
        if isinstance(arr_type, MapArrayType):
            zlx__kylax = _get_map_arr_data_type(arr_type)
            stoci__egc = context.make_helper(builder, arr_type, value=in_arr)
            pqdx__dmvv = stoci__egc.data
        else:
            zlx__kylax = arr_type
            pqdx__dmvv = in_arr
        uiqqt__cme = context.make_helper(builder, zlx__kylax, pqdx__dmvv)
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='nested_array_to_info')
        smhrt__ovsq = builder.call(betpo__xin, [builder.bitcast(jovl__jsyrk,
            lir.IntType(32).as_pointer()), builder.bitcast(yeb__pobt, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            cxl__amu, lir.IntType(8).as_pointer()), uiqqt__cme.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
    if arr_type in (string_array_type, binary_array_type):
        vdbr__vxkmb = context.make_helper(builder, arr_type, in_arr)
        sywmt__xfzog = ArrayItemArrayType(char_arr_type)
        yqjl__xhhfq = context.make_helper(builder, sywmt__xfzog,
            vdbr__vxkmb.data)
        zds__enbes = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        qwa__rheht = context.make_helper(builder, offset_arr_type,
            zds__enbes.offsets).data
        fgpw__gknlt = context.make_helper(builder, char_arr_type,
            zds__enbes.data).data
        vll__yiac = context.make_helper(builder, null_bitmap_arr_type,
            zds__enbes.null_bitmap).data
        ohy__kkgoq = builder.zext(builder.load(builder.gep(qwa__rheht, [
            zds__enbes.n_arrays])), lir.IntType(64))
        ogq__yqlf = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='string_array_to_info')
        return builder.call(betpo__xin, [zds__enbes.n_arrays, ohy__kkgoq,
            fgpw__gknlt, qwa__rheht, vll__yiac, yqjl__xhhfq.meminfo, ogq__yqlf]
            )
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        hiqh__ygr = arr.data
        jzhtx__egddf = arr.indices
        sig = array_info_type(arr_type.data)
        xuqv__qgk = array_to_info_codegen(context, builder, sig, (hiqh__ygr
            ,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        zmv__cddk = array_to_info_codegen(context, builder, sig, (
            jzhtx__egddf,), False)
        xytg__qsy = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, jzhtx__egddf)
        xzbv__onlr = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, xytg__qsy.null_bitmap).data
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='dict_str_array_to_info')
        yhdpx__yvdq = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(betpo__xin, [xuqv__qgk, zmv__cddk, builder.
            bitcast(xzbv__onlr, lir.IntType(8).as_pointer()), yhdpx__yvdq])
    lrajk__ginv = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        razz__dpvp = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        ntd__pzz = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(ntd__pzz, 1, 'C')
        lrajk__ginv = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if lrajk__ginv:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        jck__ikgu = builder.extract_value(arr.shape, 0)
        fqe__ndxg = arr_type.dtype
        mtbu__kpt = numba_to_c_type(fqe__ndxg)
        wdpp__zhqhr = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), mtbu__kpt))
        if lrajk__ginv:
            mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            betpo__xin = cgutils.get_or_insert_function(builder.module,
                mpm__mbs, name='categorical_array_to_info')
            return builder.call(betpo__xin, [jck__ikgu, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                wdpp__zhqhr), razz__dpvp, arr.meminfo])
        else:
            mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            betpo__xin = cgutils.get_or_insert_function(builder.module,
                mpm__mbs, name='numpy_array_to_info')
            return builder.call(betpo__xin, [jck__ikgu, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                wdpp__zhqhr), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        fqe__ndxg = arr_type.dtype
        sof__dbshi = fqe__ndxg
        if isinstance(arr_type, DecimalArrayType):
            sof__dbshi = int128_type
        if arr_type == datetime_date_array_type:
            sof__dbshi = types.int64
        gcbbj__qqtd = context.make_array(types.Array(sof__dbshi, 1, 'C'))(
            context, builder, arr.data)
        jck__ikgu = builder.extract_value(gcbbj__qqtd.shape, 0)
        akk__idc = context.make_array(types.Array(types.uint8, 1, 'C'))(context
            , builder, arr.null_bitmap)
        mtbu__kpt = numba_to_c_type(fqe__ndxg)
        wdpp__zhqhr = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), mtbu__kpt))
        if isinstance(arr_type, DecimalArrayType):
            mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            betpo__xin = cgutils.get_or_insert_function(builder.module,
                mpm__mbs, name='decimal_array_to_info')
            return builder.call(betpo__xin, [jck__ikgu, builder.bitcast(
                gcbbj__qqtd.data, lir.IntType(8).as_pointer()), builder.
                load(wdpp__zhqhr), builder.bitcast(akk__idc.data, lir.
                IntType(8).as_pointer()), gcbbj__qqtd.meminfo, akk__idc.
                meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
                IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            betpo__xin = cgutils.get_or_insert_function(builder.module,
                mpm__mbs, name='nullable_array_to_info')
            return builder.call(betpo__xin, [jck__ikgu, builder.bitcast(
                gcbbj__qqtd.data, lir.IntType(8).as_pointer()), builder.
                load(wdpp__zhqhr), builder.bitcast(akk__idc.data, lir.
                IntType(8).as_pointer()), gcbbj__qqtd.meminfo, akk__idc.
                meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        pgen__xmbrt = context.make_array(arr_type.arr_type)(context,
            builder, arr.left)
        inin__ktukl = context.make_array(arr_type.arr_type)(context,
            builder, arr.right)
        jck__ikgu = builder.extract_value(pgen__xmbrt.shape, 0)
        mtbu__kpt = numba_to_c_type(arr_type.arr_type.dtype)
        wdpp__zhqhr = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), mtbu__kpt))
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='interval_array_to_info')
        return builder.call(betpo__xin, [jck__ikgu, builder.bitcast(
            pgen__xmbrt.data, lir.IntType(8).as_pointer()), builder.bitcast
            (inin__ktukl.data, lir.IntType(8).as_pointer()), builder.load(
            wdpp__zhqhr), pgen__xmbrt.meminfo, inin__ktukl.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    wxdn__fwawk = cgutils.alloca_once(builder, lir.IntType(64))
    axyn__drsr = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    fln__dhx = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer(
        ), lir.IntType(64).as_pointer(), lir.IntType(8).as_pointer().
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    betpo__xin = cgutils.get_or_insert_function(builder.module, mpm__mbs,
        name='info_to_numpy_array')
    builder.call(betpo__xin, [in_info, wxdn__fwawk, axyn__drsr, fln__dhx])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    vxyj__qztp = context.get_value_type(types.intp)
    dstd__dkcoh = cgutils.pack_array(builder, [builder.load(wxdn__fwawk)],
        ty=vxyj__qztp)
    rvi__mim = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    qta__leiw = cgutils.pack_array(builder, [rvi__mim], ty=vxyj__qztp)
    fgpw__gknlt = builder.bitcast(builder.load(axyn__drsr), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=fgpw__gknlt, shape=
        dstd__dkcoh, strides=qta__leiw, itemsize=rvi__mim, meminfo=builder.
        load(fln__dhx))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    ryvz__duhio = context.make_helper(builder, arr_type)
    mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer(
        ), lir.IntType(8).as_pointer().as_pointer()])
    betpo__xin = cgutils.get_or_insert_function(builder.module, mpm__mbs,
        name='info_to_list_string_array')
    builder.call(betpo__xin, [in_info, ryvz__duhio._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return ryvz__duhio._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    tvdul__zel = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        htiki__rqj = lengths_pos
        yiv__ymm = infos_pos
        przf__zlgmr, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        fehn__skp = ArrayItemArrayPayloadType(arr_typ)
        djao__dphvt = context.get_data_type(fehn__skp)
        cfih__nkir = context.get_abi_sizeof(djao__dphvt)
        rby__uhc = define_array_item_dtor(context, builder, arr_typ, fehn__skp)
        bbfsw__edbrn = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, cfih__nkir), rby__uhc)
        vun__rjq = context.nrt.meminfo_data(builder, bbfsw__edbrn)
        ayy__wipa = builder.bitcast(vun__rjq, djao__dphvt.as_pointer())
        zds__enbes = cgutils.create_struct_proxy(fehn__skp)(context, builder)
        zds__enbes.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), htiki__rqj)
        zds__enbes.data = przf__zlgmr
        jyt__ghucw = builder.load(array_infos_ptr)
        pdcp__trc = builder.bitcast(builder.extract_value(jyt__ghucw,
            yiv__ymm), tvdul__zel)
        zds__enbes.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, pdcp__trc)
        hdy__crxev = builder.bitcast(builder.extract_value(jyt__ghucw, 
            yiv__ymm + 1), tvdul__zel)
        zds__enbes.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, hdy__crxev)
        builder.store(zds__enbes._getvalue(), ayy__wipa)
        yqjl__xhhfq = context.make_helper(builder, arr_typ)
        yqjl__xhhfq.meminfo = bbfsw__edbrn
        return yqjl__xhhfq._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        vdt__mnu = []
        yiv__ymm = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for yvczv__ofbv in arr_typ.data:
            przf__zlgmr, lengths_pos, infos_pos = nested_to_array(context,
                builder, yvczv__ofbv, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            vdt__mnu.append(przf__zlgmr)
        fehn__skp = StructArrayPayloadType(arr_typ.data)
        djao__dphvt = context.get_value_type(fehn__skp)
        cfih__nkir = context.get_abi_sizeof(djao__dphvt)
        rby__uhc = define_struct_arr_dtor(context, builder, arr_typ, fehn__skp)
        bbfsw__edbrn = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, cfih__nkir), rby__uhc)
        vun__rjq = context.nrt.meminfo_data(builder, bbfsw__edbrn)
        ayy__wipa = builder.bitcast(vun__rjq, djao__dphvt.as_pointer())
        zds__enbes = cgutils.create_struct_proxy(fehn__skp)(context, builder)
        zds__enbes.data = cgutils.pack_array(builder, vdt__mnu
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, vdt__mnu)
        jyt__ghucw = builder.load(array_infos_ptr)
        hdy__crxev = builder.bitcast(builder.extract_value(jyt__ghucw,
            yiv__ymm), tvdul__zel)
        zds__enbes.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, hdy__crxev)
        builder.store(zds__enbes._getvalue(), ayy__wipa)
        yryx__imkac = context.make_helper(builder, arr_typ)
        yryx__imkac.meminfo = bbfsw__edbrn
        return yryx__imkac._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        jyt__ghucw = builder.load(array_infos_ptr)
        ngsdx__qhb = builder.bitcast(builder.extract_value(jyt__ghucw,
            infos_pos), tvdul__zel)
        vdbr__vxkmb = context.make_helper(builder, arr_typ)
        sywmt__xfzog = ArrayItemArrayType(char_arr_type)
        yqjl__xhhfq = context.make_helper(builder, sywmt__xfzog)
        mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='info_to_string_array')
        builder.call(betpo__xin, [ngsdx__qhb, yqjl__xhhfq._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        vdbr__vxkmb.data = yqjl__xhhfq._getvalue()
        return vdbr__vxkmb._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        jyt__ghucw = builder.load(array_infos_ptr)
        qohxs__vuvu = builder.bitcast(builder.extract_value(jyt__ghucw, 
            infos_pos + 1), tvdul__zel)
        return _lower_info_to_array_numpy(arr_typ, context, builder,
            qohxs__vuvu), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        sof__dbshi = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            sof__dbshi = int128_type
        elif arr_typ == datetime_date_array_type:
            sof__dbshi = types.int64
        jyt__ghucw = builder.load(array_infos_ptr)
        hdy__crxev = builder.bitcast(builder.extract_value(jyt__ghucw,
            infos_pos), tvdul__zel)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, hdy__crxev)
        qohxs__vuvu = builder.bitcast(builder.extract_value(jyt__ghucw, 
            infos_pos + 1), tvdul__zel)
        arr.data = _lower_info_to_array_numpy(types.Array(sof__dbshi, 1,
            'C'), context, builder, qohxs__vuvu)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, sdmv__wia = args
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
                return 1 + sum([get_num_arrays(yvczv__ofbv) for yvczv__ofbv in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(yvczv__ofbv) for yvczv__ofbv in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            czk__vtn = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            czk__vtn = _get_map_arr_data_type(arr_type)
        else:
            czk__vtn = arr_type
        bos__rcg = get_num_arrays(czk__vtn)
        llbzb__ksbbb = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), 0) for sdmv__wia in range(bos__rcg)])
        lengths_ptr = cgutils.alloca_once_value(builder, llbzb__ksbbb)
        uowt__aaxzt = lir.Constant(lir.IntType(8).as_pointer(), None)
        slyc__vqls = cgutils.pack_array(builder, [uowt__aaxzt for sdmv__wia in
            range(get_num_infos(czk__vtn))])
        array_infos_ptr = cgutils.alloca_once_value(builder, slyc__vqls)
        mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='info_to_nested_array')
        builder.call(betpo__xin, [in_info, builder.bitcast(lengths_ptr, lir
            .IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, sdmv__wia, sdmv__wia = nested_to_array(context, builder,
            czk__vtn, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            zomkx__biiw = context.make_helper(builder, arr_type)
            zomkx__biiw.data = arr
            context.nrt.incref(builder, czk__vtn, arr)
            arr = zomkx__biiw._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, czk__vtn)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        vdbr__vxkmb = context.make_helper(builder, arr_type)
        sywmt__xfzog = ArrayItemArrayType(char_arr_type)
        yqjl__xhhfq = context.make_helper(builder, sywmt__xfzog)
        mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='info_to_string_array')
        builder.call(betpo__xin, [in_info, yqjl__xhhfq._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        vdbr__vxkmb.data = yqjl__xhhfq._getvalue()
        return vdbr__vxkmb._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='get_nested_info')
        xuqv__qgk = builder.call(betpo__xin, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        zmv__cddk = builder.call(betpo__xin, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        raog__hkjs = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        raog__hkjs.data = info_to_array_codegen(context, builder, sig, (
            xuqv__qgk, context.get_constant_null(arr_type.data)))
        fat__txzqw = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = fat__txzqw(array_info_type, fat__txzqw)
        raog__hkjs.indices = info_to_array_codegen(context, builder, sig, (
            zmv__cddk, context.get_constant_null(fat__txzqw)))
        mpm__mbs = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='get_has_global_dictionary')
        yhdpx__yvdq = builder.call(betpo__xin, [in_info])
        raog__hkjs.has_global_dictionary = builder.trunc(yhdpx__yvdq,
            cgutils.bool_t)
        return raog__hkjs._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        ntd__pzz = get_categories_int_type(arr_type.dtype)
        nzo__spj = types.Array(ntd__pzz, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(nzo__spj, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            ock__zug = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(ock__zug))
            int_type = arr_type.dtype.int_type
            vbbxw__vqyb = arr_type.dtype.data.data
            ynitg__zpxw = context.get_constant_generic(builder, vbbxw__vqyb,
                ock__zug)
            fqe__ndxg = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(vbbxw__vqyb), [ynitg__zpxw])
        else:
            fqe__ndxg = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, fqe__ndxg)
        out_arr.dtype = fqe__ndxg
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        fgpw__gknlt = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = fgpw__gknlt
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        sof__dbshi = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            sof__dbshi = int128_type
        elif arr_type == datetime_date_array_type:
            sof__dbshi = types.int64
        gxd__mfr = types.Array(sof__dbshi, 1, 'C')
        gcbbj__qqtd = context.make_array(gxd__mfr)(context, builder)
        goi__llh = types.Array(types.uint8, 1, 'C')
        rak__xnyxf = context.make_array(goi__llh)(context, builder)
        wxdn__fwawk = cgutils.alloca_once(builder, lir.IntType(64))
        kgvl__fzypz = cgutils.alloca_once(builder, lir.IntType(64))
        axyn__drsr = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        ocqd__ytmtv = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        fln__dhx = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        txt__xmq = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='info_to_nullable_array')
        builder.call(betpo__xin, [in_info, wxdn__fwawk, kgvl__fzypz,
            axyn__drsr, ocqd__ytmtv, fln__dhx, txt__xmq])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        vxyj__qztp = context.get_value_type(types.intp)
        dstd__dkcoh = cgutils.pack_array(builder, [builder.load(wxdn__fwawk
            )], ty=vxyj__qztp)
        rvi__mim = context.get_constant(types.intp, context.get_abi_sizeof(
            context.get_data_type(sof__dbshi)))
        qta__leiw = cgutils.pack_array(builder, [rvi__mim], ty=vxyj__qztp)
        fgpw__gknlt = builder.bitcast(builder.load(axyn__drsr), context.
            get_data_type(sof__dbshi).as_pointer())
        numba.np.arrayobj.populate_array(gcbbj__qqtd, data=fgpw__gknlt,
            shape=dstd__dkcoh, strides=qta__leiw, itemsize=rvi__mim,
            meminfo=builder.load(fln__dhx))
        arr.data = gcbbj__qqtd._getvalue()
        dstd__dkcoh = cgutils.pack_array(builder, [builder.load(kgvl__fzypz
            )], ty=vxyj__qztp)
        rvi__mim = context.get_constant(types.intp, context.get_abi_sizeof(
            context.get_data_type(types.uint8)))
        qta__leiw = cgutils.pack_array(builder, [rvi__mim], ty=vxyj__qztp)
        fgpw__gknlt = builder.bitcast(builder.load(ocqd__ytmtv), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(rak__xnyxf, data=fgpw__gknlt,
            shape=dstd__dkcoh, strides=qta__leiw, itemsize=rvi__mim,
            meminfo=builder.load(txt__xmq))
        arr.null_bitmap = rak__xnyxf._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        pgen__xmbrt = context.make_array(arr_type.arr_type)(context, builder)
        inin__ktukl = context.make_array(arr_type.arr_type)(context, builder)
        wxdn__fwawk = cgutils.alloca_once(builder, lir.IntType(64))
        hlq__jmao = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        wdqzc__ocu = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        huxsy__lbbwi = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        uyje__rzmcm = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='info_to_interval_array')
        builder.call(betpo__xin, [in_info, wxdn__fwawk, hlq__jmao,
            wdqzc__ocu, huxsy__lbbwi, uyje__rzmcm])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        vxyj__qztp = context.get_value_type(types.intp)
        dstd__dkcoh = cgutils.pack_array(builder, [builder.load(wxdn__fwawk
            )], ty=vxyj__qztp)
        rvi__mim = context.get_constant(types.intp, context.get_abi_sizeof(
            context.get_data_type(arr_type.arr_type.dtype)))
        qta__leiw = cgutils.pack_array(builder, [rvi__mim], ty=vxyj__qztp)
        yoy__sckm = builder.bitcast(builder.load(hlq__jmao), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(pgen__xmbrt, data=yoy__sckm, shape
            =dstd__dkcoh, strides=qta__leiw, itemsize=rvi__mim, meminfo=
            builder.load(huxsy__lbbwi))
        arr.left = pgen__xmbrt._getvalue()
        ladj__sbb = builder.bitcast(builder.load(wdqzc__ocu), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(inin__ktukl, data=ladj__sbb, shape
            =dstd__dkcoh, strides=qta__leiw, itemsize=rvi__mim, meminfo=
            builder.load(uyje__rzmcm))
        arr.right = inin__ktukl._getvalue()
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
        jck__ikgu, sdmv__wia = args
        mtbu__kpt = numba_to_c_type(array_type.dtype)
        wdpp__zhqhr = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), mtbu__kpt))
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='alloc_numpy')
        return builder.call(betpo__xin, [jck__ikgu, builder.load(wdpp__zhqhr)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        jck__ikgu, qrycq__auxdv = args
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='alloc_string_array')
        return builder.call(betpo__xin, [jck__ikgu, qrycq__auxdv])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    unwte__lyhr, = args
    pizlj__lvt = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], unwte__lyhr)
    mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(8
        ).as_pointer().as_pointer(), lir.IntType(64)])
    betpo__xin = cgutils.get_or_insert_function(builder.module, mpm__mbs,
        name='arr_info_list_to_table')
    return builder.call(betpo__xin, [pizlj__lvt.data, pizlj__lvt.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='info_from_table')
        return builder.call(betpo__xin, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    blv__bgy = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, dfdt__dghnv, sdmv__wia = args
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='info_from_table')
        jgfpu__sdop = cgutils.create_struct_proxy(blv__bgy)(context, builder)
        jgfpu__sdop.parent = cgutils.get_null_value(jgfpu__sdop.parent.type)
        ofoeu__vzso = context.make_array(table_idx_arr_t)(context, builder,
            dfdt__dghnv)
        pbv__ahcwu = context.get_constant(types.int64, -1)
        xjfw__yvy = context.get_constant(types.int64, 0)
        uhuy__riykb = cgutils.alloca_once_value(builder, xjfw__yvy)
        for t, drni__dlk in blv__bgy.type_to_blk.items():
            cru__wwn = context.get_constant(types.int64, len(blv__bgy.
                block_to_arr_ind[drni__dlk]))
            sdmv__wia, xdnad__lwn = ListInstance.allocate_ex(context,
                builder, types.List(t), cru__wwn)
            xdnad__lwn.size = cru__wwn
            nwehx__wek = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(blv__bgy.block_to_arr_ind[
                drni__dlk], dtype=np.int64))
            qep__tfm = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, nwehx__wek)
            with cgutils.for_range(builder, cru__wwn) as pqemf__neim:
                kazz__ruf = pqemf__neim.index
                twbmu__xeqk = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), qep__tfm,
                    kazz__ruf)
                rekzp__oza = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, ofoeu__vzso, twbmu__xeqk)
                tjdy__lcrlf = builder.icmp_unsigned('!=', rekzp__oza,
                    pbv__ahcwu)
                with builder.if_else(tjdy__lcrlf) as (znxb__aue, uqbyj__ktqx):
                    with znxb__aue:
                        lwxww__suop = builder.call(betpo__xin, [cpp_table,
                            rekzp__oza])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            lwxww__suop])
                        xdnad__lwn.inititem(kazz__ruf, arr, incref=False)
                        jck__ikgu = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(jck__ikgu, uhuy__riykb)
                    with uqbyj__ktqx:
                        sqwkm__mxuce = context.get_constant_null(t)
                        xdnad__lwn.inititem(kazz__ruf, sqwkm__mxuce, incref
                            =False)
            setattr(jgfpu__sdop, f'block_{drni__dlk}', xdnad__lwn.value)
        jgfpu__sdop.len = builder.load(uhuy__riykb)
        return jgfpu__sdop._getvalue()
    return blv__bgy(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    qfnl__fsrw = out_col_inds_t.instance_type.meta
    blv__bgy = unwrap_typeref(out_types_t.types[0])
    eelk__lkgv = [unwrap_typeref(out_types_t.types[kazz__ruf]) for
        kazz__ruf in range(1, len(out_types_t.types))]
    agb__wan = {}
    vwy__xmt = get_overload_const_int(n_table_cols_t)
    lxujp__dixu = {oubyb__iwf: kazz__ruf for kazz__ruf, oubyb__iwf in
        enumerate(qfnl__fsrw)}
    if not is_overload_none(unknown_cat_arrs_t):
        pqzav__anez = {iprer__ayvi: kazz__ruf for kazz__ruf, iprer__ayvi in
            enumerate(cat_inds_t.instance_type.meta)}
    chwq__ktdg = []
    oofm__lxn = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(blv__bgy, bodo.TableType):
        oofm__lxn += f'  py_table = init_table(py_table_type, False)\n'
        oofm__lxn += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for swn__nnnyy, drni__dlk in blv__bgy.type_to_blk.items():
            pvboi__bgdlc = [lxujp__dixu.get(kazz__ruf, -1) for kazz__ruf in
                blv__bgy.block_to_arr_ind[drni__dlk]]
            agb__wan[f'out_inds_{drni__dlk}'] = np.array(pvboi__bgdlc, np.int64
                )
            agb__wan[f'out_type_{drni__dlk}'] = swn__nnnyy
            agb__wan[f'typ_list_{drni__dlk}'] = types.List(swn__nnnyy)
            dzkv__fdtm = f'out_type_{drni__dlk}'
            if type_has_unknown_cats(swn__nnnyy):
                if is_overload_none(unknown_cat_arrs_t):
                    oofm__lxn += f"""  in_arr_list_{drni__dlk} = get_table_block(out_types_t[0], {drni__dlk})
"""
                    dzkv__fdtm = f'in_arr_list_{drni__dlk}[i]'
                else:
                    agb__wan[f'cat_arr_inds_{drni__dlk}'] = np.array([
                        pqzav__anez.get(kazz__ruf, -1) for kazz__ruf in
                        blv__bgy.block_to_arr_ind[drni__dlk]], np.int64)
                    dzkv__fdtm = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{drni__dlk}[i]]')
            cru__wwn = len(blv__bgy.block_to_arr_ind[drni__dlk])
            oofm__lxn += f"""  arr_list_{drni__dlk} = alloc_list_like(typ_list_{drni__dlk}, {cru__wwn}, False)
"""
            oofm__lxn += f'  for i in range(len(arr_list_{drni__dlk})):\n'
            oofm__lxn += f'    cpp_ind_{drni__dlk} = out_inds_{drni__dlk}[i]\n'
            oofm__lxn += f'    if cpp_ind_{drni__dlk} == -1:\n'
            oofm__lxn += f'      continue\n'
            oofm__lxn += f"""    arr_{drni__dlk} = info_to_array(info_from_table(cpp_table, cpp_ind_{drni__dlk}), {dzkv__fdtm})
"""
            oofm__lxn += f'    arr_list_{drni__dlk}[i] = arr_{drni__dlk}\n'
            oofm__lxn += f"""  py_table = set_table_block(py_table, arr_list_{drni__dlk}, {drni__dlk})
"""
        chwq__ktdg.append('py_table')
    elif blv__bgy != types.none:
        dxl__xaf = lxujp__dixu.get(0, -1)
        if dxl__xaf != -1:
            agb__wan[f'arr_typ_arg0'] = blv__bgy
            dzkv__fdtm = f'arr_typ_arg0'
            if type_has_unknown_cats(blv__bgy):
                if is_overload_none(unknown_cat_arrs_t):
                    dzkv__fdtm = f'out_types_t[0]'
                else:
                    dzkv__fdtm = f'unknown_cat_arrs_t[{pqzav__anez[0]}]'
            oofm__lxn += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {dxl__xaf}), {dzkv__fdtm})
"""
            chwq__ktdg.append('out_arg0')
    for kazz__ruf, t in enumerate(eelk__lkgv):
        dxl__xaf = lxujp__dixu.get(vwy__xmt + kazz__ruf, -1)
        if dxl__xaf != -1:
            agb__wan[f'extra_arr_type_{kazz__ruf}'] = t
            dzkv__fdtm = f'extra_arr_type_{kazz__ruf}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    dzkv__fdtm = f'out_types_t[{kazz__ruf + 1}]'
                else:
                    dzkv__fdtm = (
                        f'unknown_cat_arrs_t[{pqzav__anez[vwy__xmt + kazz__ruf]}]'
                        )
            oofm__lxn += f"""  out_{kazz__ruf} = info_to_array(info_from_table(cpp_table, {dxl__xaf}), {dzkv__fdtm})
"""
            chwq__ktdg.append(f'out_{kazz__ruf}')
    uhlow__shg = ',' if len(chwq__ktdg) == 1 else ''
    oofm__lxn += f"  return ({', '.join(chwq__ktdg)}{uhlow__shg})\n"
    agb__wan.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(qfnl__fsrw), 'py_table_type': blv__bgy})
    siaru__ouda = {}
    exec(oofm__lxn, agb__wan, siaru__ouda)
    return siaru__ouda['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    blv__bgy = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, sdmv__wia = args
        buxwl__acl = cgutils.create_struct_proxy(blv__bgy)(context, builder,
            py_table)
        if blv__bgy.has_runtime_cols:
            qehdv__gttj = lir.Constant(lir.IntType(64), 0)
            for drni__dlk, t in enumerate(blv__bgy.arr_types):
                kesh__hibqk = getattr(buxwl__acl, f'block_{drni__dlk}')
                fyfs__pguq = ListInstance(context, builder, types.List(t),
                    kesh__hibqk)
                qehdv__gttj = builder.add(qehdv__gttj, fyfs__pguq.size)
        else:
            qehdv__gttj = lir.Constant(lir.IntType(64), len(blv__bgy.arr_types)
                )
        sdmv__wia, ivn__eoqw = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), qehdv__gttj)
        ivn__eoqw.size = qehdv__gttj
        if blv__bgy.has_runtime_cols:
            iqinf__owe = lir.Constant(lir.IntType(64), 0)
            for drni__dlk, t in enumerate(blv__bgy.arr_types):
                kesh__hibqk = getattr(buxwl__acl, f'block_{drni__dlk}')
                fyfs__pguq = ListInstance(context, builder, types.List(t),
                    kesh__hibqk)
                cru__wwn = fyfs__pguq.size
                with cgutils.for_range(builder, cru__wwn) as pqemf__neim:
                    kazz__ruf = pqemf__neim.index
                    arr = fyfs__pguq.getitem(kazz__ruf)
                    oppvy__dag = signature(array_info_type, t)
                    apklh__ruy = arr,
                    ity__ffyx = array_to_info_codegen(context, builder,
                        oppvy__dag, apklh__ruy)
                    ivn__eoqw.inititem(builder.add(iqinf__owe, kazz__ruf),
                        ity__ffyx, incref=False)
                iqinf__owe = builder.add(iqinf__owe, cru__wwn)
        else:
            for t, drni__dlk in blv__bgy.type_to_blk.items():
                cru__wwn = context.get_constant(types.int64, len(blv__bgy.
                    block_to_arr_ind[drni__dlk]))
                kesh__hibqk = getattr(buxwl__acl, f'block_{drni__dlk}')
                fyfs__pguq = ListInstance(context, builder, types.List(t),
                    kesh__hibqk)
                nwehx__wek = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(blv__bgy.
                    block_to_arr_ind[drni__dlk], dtype=np.int64))
                qep__tfm = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, nwehx__wek)
                with cgutils.for_range(builder, cru__wwn) as pqemf__neim:
                    kazz__ruf = pqemf__neim.index
                    twbmu__xeqk = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), qep__tfm, kazz__ruf)
                    njmv__pqq = signature(types.none, blv__bgy, types.List(
                        t), types.int64, types.int64)
                    ian__dlr = py_table, kesh__hibqk, kazz__ruf, twbmu__xeqk
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, njmv__pqq, ian__dlr)
                    arr = fyfs__pguq.getitem(kazz__ruf)
                    oppvy__dag = signature(array_info_type, t)
                    apklh__ruy = arr,
                    ity__ffyx = array_to_info_codegen(context, builder,
                        oppvy__dag, apklh__ruy)
                    ivn__eoqw.inititem(twbmu__xeqk, ity__ffyx, incref=False)
        ngas__zzz = ivn__eoqw.value
        ugs__jciik = signature(table_type, types.List(array_info_type))
        dbfo__ebvje = ngas__zzz,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            ugs__jciik, dbfo__ebvje)
        context.nrt.decref(builder, types.List(array_info_type), ngas__zzz)
        return cpp_table
    return table_type(blv__bgy, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    olqv__lmv = in_col_inds_t.instance_type.meta
    agb__wan = {}
    vwy__xmt = get_overload_const_int(n_table_cols_t)
    zxk__uxydg = defaultdict(list)
    lxujp__dixu = {}
    for kazz__ruf, oubyb__iwf in enumerate(olqv__lmv):
        if oubyb__iwf in lxujp__dixu:
            zxk__uxydg[oubyb__iwf].append(kazz__ruf)
        else:
            lxujp__dixu[oubyb__iwf] = kazz__ruf
    oofm__lxn = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    oofm__lxn += (
        f'  cpp_arr_list = alloc_empty_list_type({len(olqv__lmv)}, array_info_type)\n'
        )
    if py_table != types.none:
        for drni__dlk in py_table.type_to_blk.values():
            pvboi__bgdlc = [lxujp__dixu.get(kazz__ruf, -1) for kazz__ruf in
                py_table.block_to_arr_ind[drni__dlk]]
            agb__wan[f'out_inds_{drni__dlk}'] = np.array(pvboi__bgdlc, np.int64
                )
            agb__wan[f'arr_inds_{drni__dlk}'] = np.array(py_table.
                block_to_arr_ind[drni__dlk], np.int64)
            oofm__lxn += (
                f'  arr_list_{drni__dlk} = get_table_block(py_table, {drni__dlk})\n'
                )
            oofm__lxn += f'  for i in range(len(arr_list_{drni__dlk})):\n'
            oofm__lxn += (
                f'    out_arr_ind_{drni__dlk} = out_inds_{drni__dlk}[i]\n')
            oofm__lxn += f'    if out_arr_ind_{drni__dlk} == -1:\n'
            oofm__lxn += f'      continue\n'
            oofm__lxn += f'    arr_ind_{drni__dlk} = arr_inds_{drni__dlk}[i]\n'
            oofm__lxn += f"""    ensure_column_unboxed(py_table, arr_list_{drni__dlk}, i, arr_ind_{drni__dlk})
"""
            oofm__lxn += f"""    cpp_arr_list[out_arr_ind_{drni__dlk}] = array_to_info(arr_list_{drni__dlk}[i])
"""
        for ngqlp__emx, agnej__xeo in zxk__uxydg.items():
            if ngqlp__emx < vwy__xmt:
                drni__dlk = py_table.block_nums[ngqlp__emx]
                cro__voqs = py_table.block_offsets[ngqlp__emx]
                for dxl__xaf in agnej__xeo:
                    oofm__lxn += f"""  cpp_arr_list[{dxl__xaf}] = array_to_info(arr_list_{drni__dlk}[{cro__voqs}])
"""
    for kazz__ruf in range(len(extra_arrs_tup)):
        msuv__gps = lxujp__dixu.get(vwy__xmt + kazz__ruf, -1)
        if msuv__gps != -1:
            yih__iybz = [msuv__gps] + zxk__uxydg.get(vwy__xmt + kazz__ruf, [])
            for dxl__xaf in yih__iybz:
                oofm__lxn += f"""  cpp_arr_list[{dxl__xaf}] = array_to_info(extra_arrs_tup[{kazz__ruf}])
"""
    oofm__lxn += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    agb__wan.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    siaru__ouda = {}
    exec(oofm__lxn, agb__wan, siaru__ouda)
    return siaru__ouda['impl']


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
        mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='delete_table')
        builder.call(betpo__xin, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='shuffle_table')
        smhrt__ovsq = builder.call(betpo__xin, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
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
        mpm__mbs = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='delete_shuffle_info')
        return builder.call(betpo__xin, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='reverse_shuffle_table')
        return builder.call(betpo__xin, args)
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
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='hash_join_table')
        smhrt__ovsq = builder.call(betpo__xin, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
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
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='sort_values_table')
        smhrt__ovsq = builder.call(betpo__xin, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='sample_table')
        smhrt__ovsq = builder.call(betpo__xin, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='shuffle_renormalization')
        smhrt__ovsq = builder.call(betpo__xin, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='shuffle_renormalization_group')
        smhrt__ovsq = builder.call(betpo__xin, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='drop_duplicates_table')
        smhrt__ovsq = builder.call(betpo__xin, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
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
        mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        betpo__xin = cgutils.get_or_insert_function(builder.module,
            mpm__mbs, name='groupby_and_aggregate')
        smhrt__ovsq = builder.call(betpo__xin, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return smhrt__ovsq
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
    hovod__iifc = array_to_info(in_arr)
    hixsm__kzqiv = array_to_info(in_values)
    xzq__ujsd = array_to_info(out_arr)
    klgv__dxhb = arr_info_list_to_table([hovod__iifc, hixsm__kzqiv, xzq__ujsd])
    _array_isin(xzq__ujsd, hovod__iifc, hixsm__kzqiv, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(klgv__dxhb)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    hovod__iifc = array_to_info(in_arr)
    xzq__ujsd = array_to_info(out_arr)
    _get_search_regex(hovod__iifc, case, match, pat, xzq__ujsd)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    wks__yjke = col_array_typ.dtype
    if isinstance(wks__yjke, types.Number) or wks__yjke in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                jgfpu__sdop, unkhx__tgsz = args
                jgfpu__sdop = builder.bitcast(jgfpu__sdop, lir.IntType(8).
                    as_pointer().as_pointer())
                ekh__elsa = lir.Constant(lir.IntType(64), c_ind)
                qckrs__yts = builder.load(builder.gep(jgfpu__sdop, [ekh__elsa])
                    )
                qckrs__yts = builder.bitcast(qckrs__yts, context.
                    get_data_type(wks__yjke).as_pointer())
                return builder.load(builder.gep(qckrs__yts, [unkhx__tgsz]))
            return wks__yjke(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                jgfpu__sdop, unkhx__tgsz = args
                jgfpu__sdop = builder.bitcast(jgfpu__sdop, lir.IntType(8).
                    as_pointer().as_pointer())
                ekh__elsa = lir.Constant(lir.IntType(64), c_ind)
                qckrs__yts = builder.load(builder.gep(jgfpu__sdop, [ekh__elsa])
                    )
                mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                rlcbm__frb = cgutils.get_or_insert_function(builder.module,
                    mpm__mbs, name='array_info_getitem')
                nrs__wug = cgutils.alloca_once(builder, lir.IntType(64))
                args = qckrs__yts, unkhx__tgsz, nrs__wug
                axyn__drsr = builder.call(rlcbm__frb, args)
                return context.make_tuple(builder, sig.return_type, [
                    axyn__drsr, builder.load(nrs__wug)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                amc__auyo = lir.Constant(lir.IntType(64), 1)
                emudl__kyft = lir.Constant(lir.IntType(64), 2)
                jgfpu__sdop, unkhx__tgsz = args
                jgfpu__sdop = builder.bitcast(jgfpu__sdop, lir.IntType(8).
                    as_pointer().as_pointer())
                ekh__elsa = lir.Constant(lir.IntType(64), c_ind)
                qckrs__yts = builder.load(builder.gep(jgfpu__sdop, [ekh__elsa])
                    )
                mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64)])
                kkns__ulupd = cgutils.get_or_insert_function(builder.module,
                    mpm__mbs, name='get_nested_info')
                args = qckrs__yts, emudl__kyft
                gpnaa__cpxz = builder.call(kkns__ulupd, args)
                mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer()])
                stj__vin = cgutils.get_or_insert_function(builder.module,
                    mpm__mbs, name='array_info_getdata1')
                args = gpnaa__cpxz,
                abkb__yjkf = builder.call(stj__vin, args)
                abkb__yjkf = builder.bitcast(abkb__yjkf, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                uhmag__eef = builder.sext(builder.load(builder.gep(
                    abkb__yjkf, [unkhx__tgsz])), lir.IntType(64))
                args = qckrs__yts, amc__auyo
                csl__gsi = builder.call(kkns__ulupd, args)
                mpm__mbs = lir.FunctionType(lir.IntType(8).as_pointer(), [
                    lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                rlcbm__frb = cgutils.get_or_insert_function(builder.module,
                    mpm__mbs, name='array_info_getitem')
                nrs__wug = cgutils.alloca_once(builder, lir.IntType(64))
                args = csl__gsi, uhmag__eef, nrs__wug
                axyn__drsr = builder.call(rlcbm__frb, args)
                return context.make_tuple(builder, sig.return_type, [
                    axyn__drsr, builder.load(nrs__wug)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{wks__yjke}' column data type not supported"
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
                oipb__izic, unkhx__tgsz = args
                oipb__izic = builder.bitcast(oipb__izic, lir.IntType(8).
                    as_pointer().as_pointer())
                ekh__elsa = lir.Constant(lir.IntType(64), c_ind)
                qckrs__yts = builder.load(builder.gep(oipb__izic, [ekh__elsa]))
                vll__yiac = builder.bitcast(qckrs__yts, context.
                    get_data_type(types.bool_).as_pointer())
                dinaa__zcyy = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    vll__yiac, unkhx__tgsz)
                kzts__qwtk = builder.icmp_unsigned('!=', dinaa__zcyy, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(kzts__qwtk, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        wks__yjke = col_array_dtype.dtype
        if wks__yjke in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    jgfpu__sdop, unkhx__tgsz = args
                    jgfpu__sdop = builder.bitcast(jgfpu__sdop, lir.IntType(
                        8).as_pointer().as_pointer())
                    ekh__elsa = lir.Constant(lir.IntType(64), c_ind)
                    qckrs__yts = builder.load(builder.gep(jgfpu__sdop, [
                        ekh__elsa]))
                    qckrs__yts = builder.bitcast(qckrs__yts, context.
                        get_data_type(wks__yjke).as_pointer())
                    tlbp__pnq = builder.load(builder.gep(qckrs__yts, [
                        unkhx__tgsz]))
                    kzts__qwtk = builder.icmp_unsigned('!=', tlbp__pnq, lir
                        .Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(kzts__qwtk, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(wks__yjke, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    jgfpu__sdop, unkhx__tgsz = args
                    jgfpu__sdop = builder.bitcast(jgfpu__sdop, lir.IntType(
                        8).as_pointer().as_pointer())
                    ekh__elsa = lir.Constant(lir.IntType(64), c_ind)
                    qckrs__yts = builder.load(builder.gep(jgfpu__sdop, [
                        ekh__elsa]))
                    qckrs__yts = builder.bitcast(qckrs__yts, context.
                        get_data_type(wks__yjke).as_pointer())
                    tlbp__pnq = builder.load(builder.gep(qckrs__yts, [
                        unkhx__tgsz]))
                    ven__asax = signature(types.bool_, wks__yjke)
                    dinaa__zcyy = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, ven__asax, (tlbp__pnq,))
                    return builder.not_(builder.sext(dinaa__zcyy, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
