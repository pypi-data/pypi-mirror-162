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
        avz__aoqo = context.make_helper(builder, arr_type, in_arr)
        in_arr = avz__aoqo.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        bvsq__eka = context.make_helper(builder, arr_type, in_arr)
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='list_string_array_to_info')
        return builder.call(dgixg__vhgvi, [bvsq__eka.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                gwyzy__ptpus = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for zsl__xle in arr_typ.data:
                    gwyzy__ptpus += get_types(zsl__xle)
                return gwyzy__ptpus
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
            duy__iencq = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                hyv__gyuv = context.make_helper(builder, arr_typ, value=arr)
                vux__blvi = get_lengths(_get_map_arr_data_type(arr_typ),
                    hyv__gyuv.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                gpu__nckxa = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                vux__blvi = get_lengths(arr_typ.dtype, gpu__nckxa.data)
                vux__blvi = cgutils.pack_array(builder, [gpu__nckxa.
                    n_arrays] + [builder.extract_value(vux__blvi,
                    dmjhw__cvi) for dmjhw__cvi in range(vux__blvi.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                gpu__nckxa = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                vux__blvi = []
                for dmjhw__cvi, zsl__xle in enumerate(arr_typ.data):
                    xko__gkoq = get_lengths(zsl__xle, builder.extract_value
                        (gpu__nckxa.data, dmjhw__cvi))
                    vux__blvi += [builder.extract_value(xko__gkoq,
                        gmnm__aqr) for gmnm__aqr in range(xko__gkoq.type.count)
                        ]
                vux__blvi = cgutils.pack_array(builder, [duy__iencq,
                    context.get_constant(types.int64, -1)] + vux__blvi)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                vux__blvi = cgutils.pack_array(builder, [duy__iencq])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return vux__blvi

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                hyv__gyuv = context.make_helper(builder, arr_typ, value=arr)
                aze__suhoq = get_buffers(_get_map_arr_data_type(arr_typ),
                    hyv__gyuv.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                gpu__nckxa = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                neb__cyhyq = get_buffers(arr_typ.dtype, gpu__nckxa.data)
                xkyvp__tsx = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, gpu__nckxa.offsets)
                jcyc__himhp = builder.bitcast(xkyvp__tsx.data, lir.IntType(
                    8).as_pointer())
                aqe__mrgsz = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, gpu__nckxa.null_bitmap)
                ycuc__gzi = builder.bitcast(aqe__mrgsz.data, lir.IntType(8)
                    .as_pointer())
                aze__suhoq = cgutils.pack_array(builder, [jcyc__himhp,
                    ycuc__gzi] + [builder.extract_value(neb__cyhyq,
                    dmjhw__cvi) for dmjhw__cvi in range(neb__cyhyq.type.count)]
                    )
            elif isinstance(arr_typ, StructArrayType):
                gpu__nckxa = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                neb__cyhyq = []
                for dmjhw__cvi, zsl__xle in enumerate(arr_typ.data):
                    csdv__noh = get_buffers(zsl__xle, builder.extract_value
                        (gpu__nckxa.data, dmjhw__cvi))
                    neb__cyhyq += [builder.extract_value(csdv__noh,
                        gmnm__aqr) for gmnm__aqr in range(csdv__noh.type.count)
                        ]
                aqe__mrgsz = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, gpu__nckxa.null_bitmap)
                ycuc__gzi = builder.bitcast(aqe__mrgsz.data, lir.IntType(8)
                    .as_pointer())
                aze__suhoq = cgutils.pack_array(builder, [ycuc__gzi] +
                    neb__cyhyq)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                nesax__ylkx = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    nesax__ylkx = int128_type
                elif arr_typ == datetime_date_array_type:
                    nesax__ylkx = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                tcyx__inex = context.make_array(types.Array(nesax__ylkx, 1,
                    'C'))(context, builder, arr.data)
                aqe__mrgsz = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, arr.null_bitmap)
                ngyi__lka = builder.bitcast(tcyx__inex.data, lir.IntType(8)
                    .as_pointer())
                ycuc__gzi = builder.bitcast(aqe__mrgsz.data, lir.IntType(8)
                    .as_pointer())
                aze__suhoq = cgutils.pack_array(builder, [ycuc__gzi, ngyi__lka]
                    )
            elif arr_typ in (string_array_type, binary_array_type):
                gpu__nckxa = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                qate__vbas = context.make_helper(builder, offset_arr_type,
                    gpu__nckxa.offsets).data
                pkw__csl = context.make_helper(builder, char_arr_type,
                    gpu__nckxa.data).data
                ajyjd__gwwhl = context.make_helper(builder,
                    null_bitmap_arr_type, gpu__nckxa.null_bitmap).data
                aze__suhoq = cgutils.pack_array(builder, [builder.bitcast(
                    qate__vbas, lir.IntType(8).as_pointer()), builder.
                    bitcast(ajyjd__gwwhl, lir.IntType(8).as_pointer()),
                    builder.bitcast(pkw__csl, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                ngyi__lka = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                pviem__omy = lir.Constant(lir.IntType(8).as_pointer(), None)
                aze__suhoq = cgutils.pack_array(builder, [pviem__omy,
                    ngyi__lka])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return aze__suhoq

        def get_field_names(arr_typ):
            fkc__zzed = []
            if isinstance(arr_typ, StructArrayType):
                for ianb__vgsl, jay__vkmk in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    fkc__zzed.append(ianb__vgsl)
                    fkc__zzed += get_field_names(jay__vkmk)
            elif isinstance(arr_typ, ArrayItemArrayType):
                fkc__zzed += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                fkc__zzed += get_field_names(_get_map_arr_data_type(arr_typ))
            return fkc__zzed
        gwyzy__ptpus = get_types(arr_type)
        usxg__zokm = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in gwyzy__ptpus])
        kclet__wexhh = cgutils.alloca_once_value(builder, usxg__zokm)
        vux__blvi = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, vux__blvi)
        aze__suhoq = get_buffers(arr_type, in_arr)
        nabmt__oxsv = cgutils.alloca_once_value(builder, aze__suhoq)
        fkc__zzed = get_field_names(arr_type)
        if len(fkc__zzed) == 0:
            fkc__zzed = ['irrelevant']
        dno__ftup = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in fkc__zzed])
        mlw__bsdnm = cgutils.alloca_once_value(builder, dno__ftup)
        if isinstance(arr_type, MapArrayType):
            xcw__etzk = _get_map_arr_data_type(arr_type)
            auk__mujv = context.make_helper(builder, arr_type, value=in_arr)
            twh__frd = auk__mujv.data
        else:
            xcw__etzk = arr_type
            twh__frd = in_arr
        dnjx__bhvce = context.make_helper(builder, xcw__etzk, twh__frd)
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='nested_array_to_info')
        fpn__jevyh = builder.call(dgixg__vhgvi, [builder.bitcast(
            kclet__wexhh, lir.IntType(32).as_pointer()), builder.bitcast(
            nabmt__oxsv, lir.IntType(8).as_pointer().as_pointer()), builder
            .bitcast(lengths_ptr, lir.IntType(64).as_pointer()), builder.
            bitcast(mlw__bsdnm, lir.IntType(8).as_pointer()), dnjx__bhvce.
            meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
    if arr_type in (string_array_type, binary_array_type):
        rkffq__aoe = context.make_helper(builder, arr_type, in_arr)
        cst__puoe = ArrayItemArrayType(char_arr_type)
        bvsq__eka = context.make_helper(builder, cst__puoe, rkffq__aoe.data)
        gpu__nckxa = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        qate__vbas = context.make_helper(builder, offset_arr_type,
            gpu__nckxa.offsets).data
        pkw__csl = context.make_helper(builder, char_arr_type, gpu__nckxa.data
            ).data
        ajyjd__gwwhl = context.make_helper(builder, null_bitmap_arr_type,
            gpu__nckxa.null_bitmap).data
        ytx__qwehj = builder.zext(builder.load(builder.gep(qate__vbas, [
            gpu__nckxa.n_arrays])), lir.IntType(64))
        slbh__iuaf = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='string_array_to_info')
        return builder.call(dgixg__vhgvi, [gpu__nckxa.n_arrays, ytx__qwehj,
            pkw__csl, qate__vbas, ajyjd__gwwhl, bvsq__eka.meminfo, slbh__iuaf])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        jzsb__cmmd = arr.data
        cai__ijmoa = arr.indices
        sig = array_info_type(arr_type.data)
        ynb__jmsj = array_to_info_codegen(context, builder, sig, (
            jzsb__cmmd,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        oiou__tla = array_to_info_codegen(context, builder, sig, (
            cai__ijmoa,), False)
        udr__kfg = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, cai__ijmoa)
        ycuc__gzi = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, udr__kfg.null_bitmap).data
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='dict_str_array_to_info')
        ifsuo__stzov = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(dgixg__vhgvi, [ynb__jmsj, oiou__tla, builder.
            bitcast(ycuc__gzi, lir.IntType(8).as_pointer()), ifsuo__stzov])
    cas__gcbhz = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        porr__lnzpa = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        ectns__fgvq = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(ectns__fgvq, 1, 'C')
        cas__gcbhz = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if cas__gcbhz:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        duy__iencq = builder.extract_value(arr.shape, 0)
        oeya__mgr = arr_type.dtype
        dxb__hvuxo = numba_to_c_type(oeya__mgr)
        nrgmk__nwrh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), dxb__hvuxo))
        if cas__gcbhz:
            mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
                mjf__volyz, name='categorical_array_to_info')
            return builder.call(dgixg__vhgvi, [duy__iencq, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                nrgmk__nwrh), porr__lnzpa, arr.meminfo])
        else:
            mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
                mjf__volyz, name='numpy_array_to_info')
            return builder.call(dgixg__vhgvi, [duy__iencq, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                nrgmk__nwrh), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        oeya__mgr = arr_type.dtype
        nesax__ylkx = oeya__mgr
        if isinstance(arr_type, DecimalArrayType):
            nesax__ylkx = int128_type
        if arr_type == datetime_date_array_type:
            nesax__ylkx = types.int64
        tcyx__inex = context.make_array(types.Array(nesax__ylkx, 1, 'C'))(
            context, builder, arr.data)
        duy__iencq = builder.extract_value(tcyx__inex.shape, 0)
        yjf__hkma = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        dxb__hvuxo = numba_to_c_type(oeya__mgr)
        nrgmk__nwrh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), dxb__hvuxo))
        if isinstance(arr_type, DecimalArrayType):
            mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
                mjf__volyz, name='decimal_array_to_info')
            return builder.call(dgixg__vhgvi, [duy__iencq, builder.bitcast(
                tcyx__inex.data, lir.IntType(8).as_pointer()), builder.load
                (nrgmk__nwrh), builder.bitcast(yjf__hkma.data, lir.IntType(
                8).as_pointer()), tcyx__inex.meminfo, yjf__hkma.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        else:
            mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
                mjf__volyz, name='nullable_array_to_info')
            return builder.call(dgixg__vhgvi, [duy__iencq, builder.bitcast(
                tcyx__inex.data, lir.IntType(8).as_pointer()), builder.load
                (nrgmk__nwrh), builder.bitcast(yjf__hkma.data, lir.IntType(
                8).as_pointer()), tcyx__inex.meminfo, yjf__hkma.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        svnj__enrh = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        xfqf__yls = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        duy__iencq = builder.extract_value(svnj__enrh.shape, 0)
        dxb__hvuxo = numba_to_c_type(arr_type.arr_type.dtype)
        nrgmk__nwrh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), dxb__hvuxo))
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='interval_array_to_info')
        return builder.call(dgixg__vhgvi, [duy__iencq, builder.bitcast(
            svnj__enrh.data, lir.IntType(8).as_pointer()), builder.bitcast(
            xfqf__yls.data, lir.IntType(8).as_pointer()), builder.load(
            nrgmk__nwrh), svnj__enrh.meminfo, xfqf__yls.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    svyfu__rfto = cgutils.alloca_once(builder, lir.IntType(64))
    ngyi__lka = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    fpb__xfn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
        mjf__volyz, name='info_to_numpy_array')
    builder.call(dgixg__vhgvi, [in_info, svyfu__rfto, ngyi__lka, fpb__xfn])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    dxfy__ssbao = context.get_value_type(types.intp)
    vrczm__qbc = cgutils.pack_array(builder, [builder.load(svyfu__rfto)],
        ty=dxfy__ssbao)
    ipzq__rncn = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    elqf__tlc = cgutils.pack_array(builder, [ipzq__rncn], ty=dxfy__ssbao)
    pkw__csl = builder.bitcast(builder.load(ngyi__lka), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=pkw__csl, shape=vrczm__qbc,
        strides=elqf__tlc, itemsize=ipzq__rncn, meminfo=builder.load(fpb__xfn))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    tpus__kxs = context.make_helper(builder, arr_type)
    mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
        mjf__volyz, name='info_to_list_string_array')
    builder.call(dgixg__vhgvi, [in_info, tpus__kxs._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return tpus__kxs._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    qprjc__pwtk = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        ozwxg__yovzj = lengths_pos
        dzssb__ooyyd = infos_pos
        eoy__fltdo, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        znugk__gafdn = ArrayItemArrayPayloadType(arr_typ)
        zadua__qcpog = context.get_data_type(znugk__gafdn)
        kxgd__bxr = context.get_abi_sizeof(zadua__qcpog)
        olb__ipdz = define_array_item_dtor(context, builder, arr_typ,
            znugk__gafdn)
        nklys__lnso = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, kxgd__bxr), olb__ipdz)
        dtyl__grev = context.nrt.meminfo_data(builder, nklys__lnso)
        ujwh__ghvq = builder.bitcast(dtyl__grev, zadua__qcpog.as_pointer())
        gpu__nckxa = cgutils.create_struct_proxy(znugk__gafdn)(context, builder
            )
        gpu__nckxa.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), ozwxg__yovzj)
        gpu__nckxa.data = eoy__fltdo
        ntds__rhekx = builder.load(array_infos_ptr)
        het__yzi = builder.bitcast(builder.extract_value(ntds__rhekx,
            dzssb__ooyyd), qprjc__pwtk)
        gpu__nckxa.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, het__yzi)
        kyuv__rix = builder.bitcast(builder.extract_value(ntds__rhekx, 
            dzssb__ooyyd + 1), qprjc__pwtk)
        gpu__nckxa.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, kyuv__rix)
        builder.store(gpu__nckxa._getvalue(), ujwh__ghvq)
        bvsq__eka = context.make_helper(builder, arr_typ)
        bvsq__eka.meminfo = nklys__lnso
        return bvsq__eka._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        trr__uwtn = []
        dzssb__ooyyd = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for slp__jbfq in arr_typ.data:
            eoy__fltdo, lengths_pos, infos_pos = nested_to_array(context,
                builder, slp__jbfq, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            trr__uwtn.append(eoy__fltdo)
        znugk__gafdn = StructArrayPayloadType(arr_typ.data)
        zadua__qcpog = context.get_value_type(znugk__gafdn)
        kxgd__bxr = context.get_abi_sizeof(zadua__qcpog)
        olb__ipdz = define_struct_arr_dtor(context, builder, arr_typ,
            znugk__gafdn)
        nklys__lnso = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, kxgd__bxr), olb__ipdz)
        dtyl__grev = context.nrt.meminfo_data(builder, nklys__lnso)
        ujwh__ghvq = builder.bitcast(dtyl__grev, zadua__qcpog.as_pointer())
        gpu__nckxa = cgutils.create_struct_proxy(znugk__gafdn)(context, builder
            )
        gpu__nckxa.data = cgutils.pack_array(builder, trr__uwtn
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, trr__uwtn)
        ntds__rhekx = builder.load(array_infos_ptr)
        kyuv__rix = builder.bitcast(builder.extract_value(ntds__rhekx,
            dzssb__ooyyd), qprjc__pwtk)
        gpu__nckxa.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, kyuv__rix)
        builder.store(gpu__nckxa._getvalue(), ujwh__ghvq)
        badvz__rgeih = context.make_helper(builder, arr_typ)
        badvz__rgeih.meminfo = nklys__lnso
        return badvz__rgeih._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        ntds__rhekx = builder.load(array_infos_ptr)
        cmwja__tbphz = builder.bitcast(builder.extract_value(ntds__rhekx,
            infos_pos), qprjc__pwtk)
        rkffq__aoe = context.make_helper(builder, arr_typ)
        cst__puoe = ArrayItemArrayType(char_arr_type)
        bvsq__eka = context.make_helper(builder, cst__puoe)
        mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='info_to_string_array')
        builder.call(dgixg__vhgvi, [cmwja__tbphz, bvsq__eka.
            _get_ptr_by_name('meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        rkffq__aoe.data = bvsq__eka._getvalue()
        return rkffq__aoe._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        ntds__rhekx = builder.load(array_infos_ptr)
        ikxgb__vzcfw = builder.bitcast(builder.extract_value(ntds__rhekx, 
            infos_pos + 1), qprjc__pwtk)
        return _lower_info_to_array_numpy(arr_typ, context, builder,
            ikxgb__vzcfw), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        nesax__ylkx = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            nesax__ylkx = int128_type
        elif arr_typ == datetime_date_array_type:
            nesax__ylkx = types.int64
        ntds__rhekx = builder.load(array_infos_ptr)
        kyuv__rix = builder.bitcast(builder.extract_value(ntds__rhekx,
            infos_pos), qprjc__pwtk)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, kyuv__rix)
        ikxgb__vzcfw = builder.bitcast(builder.extract_value(ntds__rhekx, 
            infos_pos + 1), qprjc__pwtk)
        arr.data = _lower_info_to_array_numpy(types.Array(nesax__ylkx, 1,
            'C'), context, builder, ikxgb__vzcfw)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, pane__jpafk = args
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
                return 1 + sum([get_num_arrays(slp__jbfq) for slp__jbfq in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(slp__jbfq) for slp__jbfq in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            tdld__hrzaj = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            tdld__hrzaj = _get_map_arr_data_type(arr_type)
        else:
            tdld__hrzaj = arr_type
        qce__nle = get_num_arrays(tdld__hrzaj)
        vux__blvi = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), 0) for pane__jpafk in range(qce__nle)])
        lengths_ptr = cgutils.alloca_once_value(builder, vux__blvi)
        pviem__omy = lir.Constant(lir.IntType(8).as_pointer(), None)
        tfjq__rhji = cgutils.pack_array(builder, [pviem__omy for
            pane__jpafk in range(get_num_infos(tdld__hrzaj))])
        array_infos_ptr = cgutils.alloca_once_value(builder, tfjq__rhji)
        mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='info_to_nested_array')
        builder.call(dgixg__vhgvi, [in_info, builder.bitcast(lengths_ptr,
            lir.IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, pane__jpafk, pane__jpafk = nested_to_array(context, builder,
            tdld__hrzaj, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            avz__aoqo = context.make_helper(builder, arr_type)
            avz__aoqo.data = arr
            context.nrt.incref(builder, tdld__hrzaj, arr)
            arr = avz__aoqo._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, tdld__hrzaj)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        rkffq__aoe = context.make_helper(builder, arr_type)
        cst__puoe = ArrayItemArrayType(char_arr_type)
        bvsq__eka = context.make_helper(builder, cst__puoe)
        mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='info_to_string_array')
        builder.call(dgixg__vhgvi, [in_info, bvsq__eka._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        rkffq__aoe.data = bvsq__eka._getvalue()
        return rkffq__aoe._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='get_nested_info')
        ynb__jmsj = builder.call(dgixg__vhgvi, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        oiou__tla = builder.call(dgixg__vhgvi, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        ykyim__ambf = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        ykyim__ambf.data = info_to_array_codegen(context, builder, sig, (
            ynb__jmsj, context.get_constant_null(arr_type.data)))
        vnd__hqa = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = vnd__hqa(array_info_type, vnd__hqa)
        ykyim__ambf.indices = info_to_array_codegen(context, builder, sig,
            (oiou__tla, context.get_constant_null(vnd__hqa)))
        mjf__volyz = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='get_has_global_dictionary')
        ifsuo__stzov = builder.call(dgixg__vhgvi, [in_info])
        ykyim__ambf.has_global_dictionary = builder.trunc(ifsuo__stzov,
            cgutils.bool_t)
        return ykyim__ambf._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        ectns__fgvq = get_categories_int_type(arr_type.dtype)
        kdlu__ure = types.Array(ectns__fgvq, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(kdlu__ure, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            vue__qknlq = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(vue__qknlq))
            int_type = arr_type.dtype.int_type
            tbi__zjtyl = arr_type.dtype.data.data
            ncvcm__cvt = context.get_constant_generic(builder, tbi__zjtyl,
                vue__qknlq)
            oeya__mgr = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(tbi__zjtyl), [ncvcm__cvt])
        else:
            oeya__mgr = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, oeya__mgr)
        out_arr.dtype = oeya__mgr
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        pkw__csl = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = pkw__csl
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        nesax__ylkx = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            nesax__ylkx = int128_type
        elif arr_type == datetime_date_array_type:
            nesax__ylkx = types.int64
        wlx__avx = types.Array(nesax__ylkx, 1, 'C')
        tcyx__inex = context.make_array(wlx__avx)(context, builder)
        wpz__ehjvf = types.Array(types.uint8, 1, 'C')
        jwehy__lljdm = context.make_array(wpz__ehjvf)(context, builder)
        svyfu__rfto = cgutils.alloca_once(builder, lir.IntType(64))
        fji__wva = cgutils.alloca_once(builder, lir.IntType(64))
        ngyi__lka = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        nmiwm__hcq = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        fpb__xfn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        quj__uhjb = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='info_to_nullable_array')
        builder.call(dgixg__vhgvi, [in_info, svyfu__rfto, fji__wva,
            ngyi__lka, nmiwm__hcq, fpb__xfn, quj__uhjb])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        dxfy__ssbao = context.get_value_type(types.intp)
        vrczm__qbc = cgutils.pack_array(builder, [builder.load(svyfu__rfto)
            ], ty=dxfy__ssbao)
        ipzq__rncn = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(nesax__ylkx)))
        elqf__tlc = cgutils.pack_array(builder, [ipzq__rncn], ty=dxfy__ssbao)
        pkw__csl = builder.bitcast(builder.load(ngyi__lka), context.
            get_data_type(nesax__ylkx).as_pointer())
        numba.np.arrayobj.populate_array(tcyx__inex, data=pkw__csl, shape=
            vrczm__qbc, strides=elqf__tlc, itemsize=ipzq__rncn, meminfo=
            builder.load(fpb__xfn))
        arr.data = tcyx__inex._getvalue()
        vrczm__qbc = cgutils.pack_array(builder, [builder.load(fji__wva)],
            ty=dxfy__ssbao)
        ipzq__rncn = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        elqf__tlc = cgutils.pack_array(builder, [ipzq__rncn], ty=dxfy__ssbao)
        pkw__csl = builder.bitcast(builder.load(nmiwm__hcq), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(jwehy__lljdm, data=pkw__csl, shape
            =vrczm__qbc, strides=elqf__tlc, itemsize=ipzq__rncn, meminfo=
            builder.load(quj__uhjb))
        arr.null_bitmap = jwehy__lljdm._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        svnj__enrh = context.make_array(arr_type.arr_type)(context, builder)
        xfqf__yls = context.make_array(arr_type.arr_type)(context, builder)
        svyfu__rfto = cgutils.alloca_once(builder, lir.IntType(64))
        jvers__its = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        seke__mjb = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        pot__qtun = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        eolk__bwt = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='info_to_interval_array')
        builder.call(dgixg__vhgvi, [in_info, svyfu__rfto, jvers__its,
            seke__mjb, pot__qtun, eolk__bwt])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        dxfy__ssbao = context.get_value_type(types.intp)
        vrczm__qbc = cgutils.pack_array(builder, [builder.load(svyfu__rfto)
            ], ty=dxfy__ssbao)
        ipzq__rncn = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        elqf__tlc = cgutils.pack_array(builder, [ipzq__rncn], ty=dxfy__ssbao)
        sfazf__dzxm = builder.bitcast(builder.load(jvers__its), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(svnj__enrh, data=sfazf__dzxm,
            shape=vrczm__qbc, strides=elqf__tlc, itemsize=ipzq__rncn,
            meminfo=builder.load(pot__qtun))
        arr.left = svnj__enrh._getvalue()
        iir__srst = builder.bitcast(builder.load(seke__mjb), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(xfqf__yls, data=iir__srst, shape=
            vrczm__qbc, strides=elqf__tlc, itemsize=ipzq__rncn, meminfo=
            builder.load(eolk__bwt))
        arr.right = xfqf__yls._getvalue()
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
        duy__iencq, pane__jpafk = args
        dxb__hvuxo = numba_to_c_type(array_type.dtype)
        nrgmk__nwrh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), dxb__hvuxo))
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='alloc_numpy')
        return builder.call(dgixg__vhgvi, [duy__iencq, builder.load(
            nrgmk__nwrh)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        duy__iencq, ualz__xuua = args
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='alloc_string_array')
        return builder.call(dgixg__vhgvi, [duy__iencq, ualz__xuua])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    kdj__todh, = args
    eygdm__qcgxv = numba.cpython.listobj.ListInstance(context, builder, sig
        .args[0], kdj__todh)
    mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer().as_pointer(), lir.IntType(64)])
    dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
        mjf__volyz, name='arr_info_list_to_table')
    return builder.call(dgixg__vhgvi, [eygdm__qcgxv.data, eygdm__qcgxv.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='info_from_table')
        return builder.call(dgixg__vhgvi, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    qyjp__otd = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, agkb__qll, pane__jpafk = args
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='info_from_table')
        auzxw__goc = cgutils.create_struct_proxy(qyjp__otd)(context, builder)
        auzxw__goc.parent = cgutils.get_null_value(auzxw__goc.parent.type)
        rck__jqjo = context.make_array(table_idx_arr_t)(context, builder,
            agkb__qll)
        grf__uvx = context.get_constant(types.int64, -1)
        wumby__ltw = context.get_constant(types.int64, 0)
        xmpgj__rclt = cgutils.alloca_once_value(builder, wumby__ltw)
        for t, odv__grt in qyjp__otd.type_to_blk.items():
            rcx__fjrry = context.get_constant(types.int64, len(qyjp__otd.
                block_to_arr_ind[odv__grt]))
            pane__jpafk, ndt__zpjcr = ListInstance.allocate_ex(context,
                builder, types.List(t), rcx__fjrry)
            ndt__zpjcr.size = rcx__fjrry
            jxsms__bipna = context.make_constant_array(builder, types.Array
                (types.int64, 1, 'C'), np.array(qyjp__otd.block_to_arr_ind[
                odv__grt], dtype=np.int64))
            elo__gbm = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, jxsms__bipna)
            with cgutils.for_range(builder, rcx__fjrry) as tduui__wao:
                dmjhw__cvi = tduui__wao.index
                eyvf__clngh = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), elo__gbm,
                    dmjhw__cvi)
                xyzrj__zgz = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, rck__jqjo, eyvf__clngh)
                dheht__pbrmp = builder.icmp_unsigned('!=', xyzrj__zgz, grf__uvx
                    )
                with builder.if_else(dheht__pbrmp) as (faeur__zmir, wdgl__sibt
                    ):
                    with faeur__zmir:
                        oyzt__gas = builder.call(dgixg__vhgvi, [cpp_table,
                            xyzrj__zgz])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            oyzt__gas])
                        ndt__zpjcr.inititem(dmjhw__cvi, arr, incref=False)
                        duy__iencq = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(duy__iencq, xmpgj__rclt)
                    with wdgl__sibt:
                        cyc__afd = context.get_constant_null(t)
                        ndt__zpjcr.inititem(dmjhw__cvi, cyc__afd, incref=False)
            setattr(auzxw__goc, f'block_{odv__grt}', ndt__zpjcr.value)
        auzxw__goc.len = builder.load(xmpgj__rclt)
        return auzxw__goc._getvalue()
    return qyjp__otd(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    imhb__yqavp = out_col_inds_t.instance_type.meta
    qyjp__otd = unwrap_typeref(out_types_t.types[0])
    nuog__leg = [unwrap_typeref(out_types_t.types[dmjhw__cvi]) for
        dmjhw__cvi in range(1, len(out_types_t.types))]
    jsdg__wqu = {}
    tyiv__ypnit = get_overload_const_int(n_table_cols_t)
    lfrkc__nvq = {rnex__iam: dmjhw__cvi for dmjhw__cvi, rnex__iam in
        enumerate(imhb__yqavp)}
    if not is_overload_none(unknown_cat_arrs_t):
        mqtj__easr = {xwxnm__ukbq: dmjhw__cvi for dmjhw__cvi, xwxnm__ukbq in
            enumerate(cat_inds_t.instance_type.meta)}
    gbzuz__qny = []
    ovfbk__krm = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(qyjp__otd, bodo.TableType):
        ovfbk__krm += f'  py_table = init_table(py_table_type, False)\n'
        ovfbk__krm += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for dks__zrpc, odv__grt in qyjp__otd.type_to_blk.items():
            kdxc__ofppu = [lfrkc__nvq.get(dmjhw__cvi, -1) for dmjhw__cvi in
                qyjp__otd.block_to_arr_ind[odv__grt]]
            jsdg__wqu[f'out_inds_{odv__grt}'] = np.array(kdxc__ofppu, np.int64)
            jsdg__wqu[f'out_type_{odv__grt}'] = dks__zrpc
            jsdg__wqu[f'typ_list_{odv__grt}'] = types.List(dks__zrpc)
            yhci__orq = f'out_type_{odv__grt}'
            if type_has_unknown_cats(dks__zrpc):
                if is_overload_none(unknown_cat_arrs_t):
                    ovfbk__krm += f"""  in_arr_list_{odv__grt} = get_table_block(out_types_t[0], {odv__grt})
"""
                    yhci__orq = f'in_arr_list_{odv__grt}[i]'
                else:
                    jsdg__wqu[f'cat_arr_inds_{odv__grt}'] = np.array([
                        mqtj__easr.get(dmjhw__cvi, -1) for dmjhw__cvi in
                        qyjp__otd.block_to_arr_ind[odv__grt]], np.int64)
                    yhci__orq = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{odv__grt}[i]]')
            rcx__fjrry = len(qyjp__otd.block_to_arr_ind[odv__grt])
            ovfbk__krm += f"""  arr_list_{odv__grt} = alloc_list_like(typ_list_{odv__grt}, {rcx__fjrry}, False)
"""
            ovfbk__krm += f'  for i in range(len(arr_list_{odv__grt})):\n'
            ovfbk__krm += f'    cpp_ind_{odv__grt} = out_inds_{odv__grt}[i]\n'
            ovfbk__krm += f'    if cpp_ind_{odv__grt} == -1:\n'
            ovfbk__krm += f'      continue\n'
            ovfbk__krm += f"""    arr_{odv__grt} = info_to_array(info_from_table(cpp_table, cpp_ind_{odv__grt}), {yhci__orq})
"""
            ovfbk__krm += f'    arr_list_{odv__grt}[i] = arr_{odv__grt}\n'
            ovfbk__krm += f"""  py_table = set_table_block(py_table, arr_list_{odv__grt}, {odv__grt})
"""
        gbzuz__qny.append('py_table')
    elif qyjp__otd != types.none:
        opb__feyi = lfrkc__nvq.get(0, -1)
        if opb__feyi != -1:
            jsdg__wqu[f'arr_typ_arg0'] = qyjp__otd
            yhci__orq = f'arr_typ_arg0'
            if type_has_unknown_cats(qyjp__otd):
                if is_overload_none(unknown_cat_arrs_t):
                    yhci__orq = f'out_types_t[0]'
                else:
                    yhci__orq = f'unknown_cat_arrs_t[{mqtj__easr[0]}]'
            ovfbk__krm += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {opb__feyi}), {yhci__orq})
"""
            gbzuz__qny.append('out_arg0')
    for dmjhw__cvi, t in enumerate(nuog__leg):
        opb__feyi = lfrkc__nvq.get(tyiv__ypnit + dmjhw__cvi, -1)
        if opb__feyi != -1:
            jsdg__wqu[f'extra_arr_type_{dmjhw__cvi}'] = t
            yhci__orq = f'extra_arr_type_{dmjhw__cvi}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    yhci__orq = f'out_types_t[{dmjhw__cvi + 1}]'
                else:
                    yhci__orq = (
                        f'unknown_cat_arrs_t[{mqtj__easr[tyiv__ypnit + dmjhw__cvi]}]'
                        )
            ovfbk__krm += f"""  out_{dmjhw__cvi} = info_to_array(info_from_table(cpp_table, {opb__feyi}), {yhci__orq})
"""
            gbzuz__qny.append(f'out_{dmjhw__cvi}')
    llyds__hoobn = ',' if len(gbzuz__qny) == 1 else ''
    ovfbk__krm += f"  return ({', '.join(gbzuz__qny)}{llyds__hoobn})\n"
    jsdg__wqu.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(imhb__yqavp), 'py_table_type': qyjp__otd})
    praz__lmg = {}
    exec(ovfbk__krm, jsdg__wqu, praz__lmg)
    return praz__lmg['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    qyjp__otd = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, pane__jpafk = args
        hfb__srnb = cgutils.create_struct_proxy(qyjp__otd)(context, builder,
            py_table)
        if qyjp__otd.has_runtime_cols:
            vbq__fiwck = lir.Constant(lir.IntType(64), 0)
            for odv__grt, t in enumerate(qyjp__otd.arr_types):
                ioshh__dhu = getattr(hfb__srnb, f'block_{odv__grt}')
                stg__ebax = ListInstance(context, builder, types.List(t),
                    ioshh__dhu)
                vbq__fiwck = builder.add(vbq__fiwck, stg__ebax.size)
        else:
            vbq__fiwck = lir.Constant(lir.IntType(64), len(qyjp__otd.arr_types)
                )
        pane__jpafk, yhcyd__zcsc = ListInstance.allocate_ex(context,
            builder, types.List(array_info_type), vbq__fiwck)
        yhcyd__zcsc.size = vbq__fiwck
        if qyjp__otd.has_runtime_cols:
            fgl__zqer = lir.Constant(lir.IntType(64), 0)
            for odv__grt, t in enumerate(qyjp__otd.arr_types):
                ioshh__dhu = getattr(hfb__srnb, f'block_{odv__grt}')
                stg__ebax = ListInstance(context, builder, types.List(t),
                    ioshh__dhu)
                rcx__fjrry = stg__ebax.size
                with cgutils.for_range(builder, rcx__fjrry) as tduui__wao:
                    dmjhw__cvi = tduui__wao.index
                    arr = stg__ebax.getitem(dmjhw__cvi)
                    xtue__mefe = signature(array_info_type, t)
                    xnxgv__wkstw = arr,
                    pfku__jgm = array_to_info_codegen(context, builder,
                        xtue__mefe, xnxgv__wkstw)
                    yhcyd__zcsc.inititem(builder.add(fgl__zqer, dmjhw__cvi),
                        pfku__jgm, incref=False)
                fgl__zqer = builder.add(fgl__zqer, rcx__fjrry)
        else:
            for t, odv__grt in qyjp__otd.type_to_blk.items():
                rcx__fjrry = context.get_constant(types.int64, len(
                    qyjp__otd.block_to_arr_ind[odv__grt]))
                ioshh__dhu = getattr(hfb__srnb, f'block_{odv__grt}')
                stg__ebax = ListInstance(context, builder, types.List(t),
                    ioshh__dhu)
                jxsms__bipna = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(qyjp__otd.
                    block_to_arr_ind[odv__grt], dtype=np.int64))
                elo__gbm = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, jxsms__bipna)
                with cgutils.for_range(builder, rcx__fjrry) as tduui__wao:
                    dmjhw__cvi = tduui__wao.index
                    eyvf__clngh = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), elo__gbm, dmjhw__cvi)
                    zlumc__jdql = signature(types.none, qyjp__otd, types.
                        List(t), types.int64, types.int64)
                    pcrhr__tdw = py_table, ioshh__dhu, dmjhw__cvi, eyvf__clngh
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, zlumc__jdql, pcrhr__tdw)
                    arr = stg__ebax.getitem(dmjhw__cvi)
                    xtue__mefe = signature(array_info_type, t)
                    xnxgv__wkstw = arr,
                    pfku__jgm = array_to_info_codegen(context, builder,
                        xtue__mefe, xnxgv__wkstw)
                    yhcyd__zcsc.inititem(eyvf__clngh, pfku__jgm, incref=False)
        ysr__gtc = yhcyd__zcsc.value
        weg__iktu = signature(table_type, types.List(array_info_type))
        qyqfu__gsh = ysr__gtc,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            weg__iktu, qyqfu__gsh)
        context.nrt.decref(builder, types.List(array_info_type), ysr__gtc)
        return cpp_table
    return table_type(qyjp__otd, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    yjkqk__dyc = in_col_inds_t.instance_type.meta
    jsdg__wqu = {}
    tyiv__ypnit = get_overload_const_int(n_table_cols_t)
    klpzg__ewk = defaultdict(list)
    lfrkc__nvq = {}
    for dmjhw__cvi, rnex__iam in enumerate(yjkqk__dyc):
        if rnex__iam in lfrkc__nvq:
            klpzg__ewk[rnex__iam].append(dmjhw__cvi)
        else:
            lfrkc__nvq[rnex__iam] = dmjhw__cvi
    ovfbk__krm = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    ovfbk__krm += (
        f'  cpp_arr_list = alloc_empty_list_type({len(yjkqk__dyc)}, array_info_type)\n'
        )
    if py_table != types.none:
        for odv__grt in py_table.type_to_blk.values():
            kdxc__ofppu = [lfrkc__nvq.get(dmjhw__cvi, -1) for dmjhw__cvi in
                py_table.block_to_arr_ind[odv__grt]]
            jsdg__wqu[f'out_inds_{odv__grt}'] = np.array(kdxc__ofppu, np.int64)
            jsdg__wqu[f'arr_inds_{odv__grt}'] = np.array(py_table.
                block_to_arr_ind[odv__grt], np.int64)
            ovfbk__krm += (
                f'  arr_list_{odv__grt} = get_table_block(py_table, {odv__grt})\n'
                )
            ovfbk__krm += f'  for i in range(len(arr_list_{odv__grt})):\n'
            ovfbk__krm += (
                f'    out_arr_ind_{odv__grt} = out_inds_{odv__grt}[i]\n')
            ovfbk__krm += f'    if out_arr_ind_{odv__grt} == -1:\n'
            ovfbk__krm += f'      continue\n'
            ovfbk__krm += f'    arr_ind_{odv__grt} = arr_inds_{odv__grt}[i]\n'
            ovfbk__krm += f"""    ensure_column_unboxed(py_table, arr_list_{odv__grt}, i, arr_ind_{odv__grt})
"""
            ovfbk__krm += f"""    cpp_arr_list[out_arr_ind_{odv__grt}] = array_to_info(arr_list_{odv__grt}[i])
"""
        for nimie__dypd, ysbkh__crpxo in klpzg__ewk.items():
            if nimie__dypd < tyiv__ypnit:
                odv__grt = py_table.block_nums[nimie__dypd]
                xiw__apa = py_table.block_offsets[nimie__dypd]
                for opb__feyi in ysbkh__crpxo:
                    ovfbk__krm += f"""  cpp_arr_list[{opb__feyi}] = array_to_info(arr_list_{odv__grt}[{xiw__apa}])
"""
    for dmjhw__cvi in range(len(extra_arrs_tup)):
        dhc__zkcnm = lfrkc__nvq.get(tyiv__ypnit + dmjhw__cvi, -1)
        if dhc__zkcnm != -1:
            uwxz__lziq = [dhc__zkcnm] + klpzg__ewk.get(tyiv__ypnit +
                dmjhw__cvi, [])
            for opb__feyi in uwxz__lziq:
                ovfbk__krm += f"""  cpp_arr_list[{opb__feyi}] = array_to_info(extra_arrs_tup[{dmjhw__cvi}])
"""
    ovfbk__krm += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    jsdg__wqu.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    praz__lmg = {}
    exec(ovfbk__krm, jsdg__wqu, praz__lmg)
    return praz__lmg['impl']


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
        mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='delete_table')
        builder.call(dgixg__vhgvi, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='shuffle_table')
        fpn__jevyh = builder.call(dgixg__vhgvi, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
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
        mjf__volyz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='delete_shuffle_info')
        return builder.call(dgixg__vhgvi, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='reverse_shuffle_table')
        return builder.call(dgixg__vhgvi, args)
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
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='hash_join_table')
        fpn__jevyh = builder.call(dgixg__vhgvi, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
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
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='sort_values_table')
        fpn__jevyh = builder.call(dgixg__vhgvi, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='sample_table')
        fpn__jevyh = builder.call(dgixg__vhgvi, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='shuffle_renormalization')
        fpn__jevyh = builder.call(dgixg__vhgvi, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='shuffle_renormalization_group')
        fpn__jevyh = builder.call(dgixg__vhgvi, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='drop_duplicates_table')
        fpn__jevyh = builder.call(dgixg__vhgvi, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
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
        mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        dgixg__vhgvi = cgutils.get_or_insert_function(builder.module,
            mjf__volyz, name='groupby_and_aggregate')
        fpn__jevyh = builder.call(dgixg__vhgvi, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return fpn__jevyh
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
    ihk__wil = array_to_info(in_arr)
    reo__umpq = array_to_info(in_values)
    ncr__xmeoq = array_to_info(out_arr)
    cxhj__ilpj = arr_info_list_to_table([ihk__wil, reo__umpq, ncr__xmeoq])
    _array_isin(ncr__xmeoq, ihk__wil, reo__umpq, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(cxhj__ilpj)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    ihk__wil = array_to_info(in_arr)
    ncr__xmeoq = array_to_info(out_arr)
    _get_search_regex(ihk__wil, case, match, pat, ncr__xmeoq)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    kmpgk__axz = col_array_typ.dtype
    if isinstance(kmpgk__axz, types.Number) or kmpgk__axz in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                auzxw__goc, qpmk__for = args
                auzxw__goc = builder.bitcast(auzxw__goc, lir.IntType(8).
                    as_pointer().as_pointer())
                rbgqf__rasq = lir.Constant(lir.IntType(64), c_ind)
                oto__efxvi = builder.load(builder.gep(auzxw__goc, [
                    rbgqf__rasq]))
                oto__efxvi = builder.bitcast(oto__efxvi, context.
                    get_data_type(kmpgk__axz).as_pointer())
                return builder.load(builder.gep(oto__efxvi, [qpmk__for]))
            return kmpgk__axz(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                auzxw__goc, qpmk__for = args
                auzxw__goc = builder.bitcast(auzxw__goc, lir.IntType(8).
                    as_pointer().as_pointer())
                rbgqf__rasq = lir.Constant(lir.IntType(64), c_ind)
                oto__efxvi = builder.load(builder.gep(auzxw__goc, [
                    rbgqf__rasq]))
                mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                dla__lbe = cgutils.get_or_insert_function(builder.module,
                    mjf__volyz, name='array_info_getitem')
                gdin__turjn = cgutils.alloca_once(builder, lir.IntType(64))
                args = oto__efxvi, qpmk__for, gdin__turjn
                ngyi__lka = builder.call(dla__lbe, args)
                return context.make_tuple(builder, sig.return_type, [
                    ngyi__lka, builder.load(gdin__turjn)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                idb__ivhb = lir.Constant(lir.IntType(64), 1)
                nkw__iuz = lir.Constant(lir.IntType(64), 2)
                auzxw__goc, qpmk__for = args
                auzxw__goc = builder.bitcast(auzxw__goc, lir.IntType(8).
                    as_pointer().as_pointer())
                rbgqf__rasq = lir.Constant(lir.IntType(64), c_ind)
                oto__efxvi = builder.load(builder.gep(auzxw__goc, [
                    rbgqf__rasq]))
                mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                zrbtp__hpa = cgutils.get_or_insert_function(builder.module,
                    mjf__volyz, name='get_nested_info')
                args = oto__efxvi, nkw__iuz
                lyvjt__zujgx = builder.call(zrbtp__hpa, args)
                mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                zdzar__drac = cgutils.get_or_insert_function(builder.module,
                    mjf__volyz, name='array_info_getdata1')
                args = lyvjt__zujgx,
                arciu__ris = builder.call(zdzar__drac, args)
                arciu__ris = builder.bitcast(arciu__ris, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                rbtxc__obt = builder.sext(builder.load(builder.gep(
                    arciu__ris, [qpmk__for])), lir.IntType(64))
                args = oto__efxvi, idb__ivhb
                czo__bzn = builder.call(zrbtp__hpa, args)
                mjf__volyz = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                dla__lbe = cgutils.get_or_insert_function(builder.module,
                    mjf__volyz, name='array_info_getitem')
                gdin__turjn = cgutils.alloca_once(builder, lir.IntType(64))
                args = czo__bzn, rbtxc__obt, gdin__turjn
                ngyi__lka = builder.call(dla__lbe, args)
                return context.make_tuple(builder, sig.return_type, [
                    ngyi__lka, builder.load(gdin__turjn)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{kmpgk__axz}' column data type not supported"
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
                bocrn__zewb, qpmk__for = args
                bocrn__zewb = builder.bitcast(bocrn__zewb, lir.IntType(8).
                    as_pointer().as_pointer())
                rbgqf__rasq = lir.Constant(lir.IntType(64), c_ind)
                oto__efxvi = builder.load(builder.gep(bocrn__zewb, [
                    rbgqf__rasq]))
                ajyjd__gwwhl = builder.bitcast(oto__efxvi, context.
                    get_data_type(types.bool_).as_pointer())
                ffme__kedrh = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    ajyjd__gwwhl, qpmk__for)
                ihdj__cvi = builder.icmp_unsigned('!=', ffme__kedrh, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(ihdj__cvi, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        kmpgk__axz = col_array_dtype.dtype
        if kmpgk__axz in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    auzxw__goc, qpmk__for = args
                    auzxw__goc = builder.bitcast(auzxw__goc, lir.IntType(8)
                        .as_pointer().as_pointer())
                    rbgqf__rasq = lir.Constant(lir.IntType(64), c_ind)
                    oto__efxvi = builder.load(builder.gep(auzxw__goc, [
                        rbgqf__rasq]))
                    oto__efxvi = builder.bitcast(oto__efxvi, context.
                        get_data_type(kmpgk__axz).as_pointer())
                    uft__rfdz = builder.load(builder.gep(oto__efxvi, [
                        qpmk__for]))
                    ihdj__cvi = builder.icmp_unsigned('!=', uft__rfdz, lir.
                        Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(ihdj__cvi, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(kmpgk__axz, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    auzxw__goc, qpmk__for = args
                    auzxw__goc = builder.bitcast(auzxw__goc, lir.IntType(8)
                        .as_pointer().as_pointer())
                    rbgqf__rasq = lir.Constant(lir.IntType(64), c_ind)
                    oto__efxvi = builder.load(builder.gep(auzxw__goc, [
                        rbgqf__rasq]))
                    oto__efxvi = builder.bitcast(oto__efxvi, context.
                        get_data_type(kmpgk__axz).as_pointer())
                    uft__rfdz = builder.load(builder.gep(oto__efxvi, [
                        qpmk__for]))
                    hlxnn__bgqsu = signature(types.bool_, kmpgk__axz)
                    ffme__kedrh = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, hlxnn__bgqsu, (uft__rfdz,))
                    return builder.not_(builder.sext(ffme__kedrh, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
