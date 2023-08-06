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
        hqnli__npp = context.make_helper(builder, arr_type, in_arr)
        in_arr = hqnli__npp.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        hox__zpkr = context.make_helper(builder, arr_type, in_arr)
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='list_string_array_to_info')
        return builder.call(dmq__gcl, [hox__zpkr.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                nzwqj__mal = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for cex__rgehu in arr_typ.data:
                    nzwqj__mal += get_types(cex__rgehu)
                return nzwqj__mal
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
            uks__qykrq = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                ijox__hdsb = context.make_helper(builder, arr_typ, value=arr)
                pmnas__cber = get_lengths(_get_map_arr_data_type(arr_typ),
                    ijox__hdsb.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ueq__uoc = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                pmnas__cber = get_lengths(arr_typ.dtype, ueq__uoc.data)
                pmnas__cber = cgutils.pack_array(builder, [ueq__uoc.
                    n_arrays] + [builder.extract_value(pmnas__cber,
                    kni__aab) for kni__aab in range(pmnas__cber.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                ueq__uoc = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                pmnas__cber = []
                for kni__aab, cex__rgehu in enumerate(arr_typ.data):
                    lhon__viau = get_lengths(cex__rgehu, builder.
                        extract_value(ueq__uoc.data, kni__aab))
                    pmnas__cber += [builder.extract_value(lhon__viau,
                        eik__tvx) for eik__tvx in range(lhon__viau.type.count)]
                pmnas__cber = cgutils.pack_array(builder, [uks__qykrq,
                    context.get_constant(types.int64, -1)] + pmnas__cber)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                pmnas__cber = cgutils.pack_array(builder, [uks__qykrq])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return pmnas__cber

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                ijox__hdsb = context.make_helper(builder, arr_typ, value=arr)
                ckl__aolgu = get_buffers(_get_map_arr_data_type(arr_typ),
                    ijox__hdsb.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ueq__uoc = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                pfzpr__wsdbl = get_buffers(arr_typ.dtype, ueq__uoc.data)
                ngbfc__rrqfm = context.make_array(types.Array(offset_type, 
                    1, 'C'))(context, builder, ueq__uoc.offsets)
                txg__woc = builder.bitcast(ngbfc__rrqfm.data, lir.IntType(8
                    ).as_pointer())
                dde__pdkc = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, ueq__uoc.null_bitmap)
                ukd__qcrb = builder.bitcast(dde__pdkc.data, lir.IntType(8).
                    as_pointer())
                ckl__aolgu = cgutils.pack_array(builder, [txg__woc,
                    ukd__qcrb] + [builder.extract_value(pfzpr__wsdbl,
                    kni__aab) for kni__aab in range(pfzpr__wsdbl.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                ueq__uoc = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                pfzpr__wsdbl = []
                for kni__aab, cex__rgehu in enumerate(arr_typ.data):
                    sutxd__wyt = get_buffers(cex__rgehu, builder.
                        extract_value(ueq__uoc.data, kni__aab))
                    pfzpr__wsdbl += [builder.extract_value(sutxd__wyt,
                        eik__tvx) for eik__tvx in range(sutxd__wyt.type.count)]
                dde__pdkc = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, ueq__uoc.null_bitmap)
                ukd__qcrb = builder.bitcast(dde__pdkc.data, lir.IntType(8).
                    as_pointer())
                ckl__aolgu = cgutils.pack_array(builder, [ukd__qcrb] +
                    pfzpr__wsdbl)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                mhf__xeq = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    mhf__xeq = int128_type
                elif arr_typ == datetime_date_array_type:
                    mhf__xeq = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                pfnjd__fzxc = context.make_array(types.Array(mhf__xeq, 1, 'C')
                    )(context, builder, arr.data)
                dde__pdkc = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                xps__fofy = builder.bitcast(pfnjd__fzxc.data, lir.IntType(8
                    ).as_pointer())
                ukd__qcrb = builder.bitcast(dde__pdkc.data, lir.IntType(8).
                    as_pointer())
                ckl__aolgu = cgutils.pack_array(builder, [ukd__qcrb, xps__fofy]
                    )
            elif arr_typ in (string_array_type, binary_array_type):
                ueq__uoc = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                decu__qflr = context.make_helper(builder, offset_arr_type,
                    ueq__uoc.offsets).data
                eqeuj__kthko = context.make_helper(builder, char_arr_type,
                    ueq__uoc.data).data
                qhjl__uivt = context.make_helper(builder,
                    null_bitmap_arr_type, ueq__uoc.null_bitmap).data
                ckl__aolgu = cgutils.pack_array(builder, [builder.bitcast(
                    decu__qflr, lir.IntType(8).as_pointer()), builder.
                    bitcast(qhjl__uivt, lir.IntType(8).as_pointer()),
                    builder.bitcast(eqeuj__kthko, lir.IntType(8).as_pointer())]
                    )
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                xps__fofy = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                peqrb__fsi = lir.Constant(lir.IntType(8).as_pointer(), None)
                ckl__aolgu = cgutils.pack_array(builder, [peqrb__fsi,
                    xps__fofy])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return ckl__aolgu

        def get_field_names(arr_typ):
            coase__ztjc = []
            if isinstance(arr_typ, StructArrayType):
                for ryga__fze, bkuu__sfkjk in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    coase__ztjc.append(ryga__fze)
                    coase__ztjc += get_field_names(bkuu__sfkjk)
            elif isinstance(arr_typ, ArrayItemArrayType):
                coase__ztjc += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                coase__ztjc += get_field_names(_get_map_arr_data_type(arr_typ))
            return coase__ztjc
        nzwqj__mal = get_types(arr_type)
        rit__atuz = cgutils.pack_array(builder, [context.get_constant(types
            .int32, t) for t in nzwqj__mal])
        szlp__punb = cgutils.alloca_once_value(builder, rit__atuz)
        pmnas__cber = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, pmnas__cber)
        ckl__aolgu = get_buffers(arr_type, in_arr)
        ewwmv__eits = cgutils.alloca_once_value(builder, ckl__aolgu)
        coase__ztjc = get_field_names(arr_type)
        if len(coase__ztjc) == 0:
            coase__ztjc = ['irrelevant']
        dze__oqg = cgutils.pack_array(builder, [context.insert_const_string
            (builder.module, a) for a in coase__ztjc])
        phg__iclf = cgutils.alloca_once_value(builder, dze__oqg)
        if isinstance(arr_type, MapArrayType):
            rjnpf__wkti = _get_map_arr_data_type(arr_type)
            ajla__fjk = context.make_helper(builder, arr_type, value=in_arr)
            wckee__spl = ajla__fjk.data
        else:
            rjnpf__wkti = arr_type
            wckee__spl = in_arr
        uict__agwk = context.make_helper(builder, rjnpf__wkti, wckee__spl)
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='nested_array_to_info')
        ldcfu__csz = builder.call(dmq__gcl, [builder.bitcast(szlp__punb,
            lir.IntType(32).as_pointer()), builder.bitcast(ewwmv__eits, lir
            .IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            phg__iclf, lir.IntType(8).as_pointer()), uict__agwk.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
    if arr_type in (string_array_type, binary_array_type):
        tlyzh__msj = context.make_helper(builder, arr_type, in_arr)
        zvecy__shz = ArrayItemArrayType(char_arr_type)
        hox__zpkr = context.make_helper(builder, zvecy__shz, tlyzh__msj.data)
        ueq__uoc = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        decu__qflr = context.make_helper(builder, offset_arr_type, ueq__uoc
            .offsets).data
        eqeuj__kthko = context.make_helper(builder, char_arr_type, ueq__uoc
            .data).data
        qhjl__uivt = context.make_helper(builder, null_bitmap_arr_type,
            ueq__uoc.null_bitmap).data
        wxerm__wsy = builder.zext(builder.load(builder.gep(decu__qflr, [
            ueq__uoc.n_arrays])), lir.IntType(64))
        ieiwc__blto = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='string_array_to_info')
        return builder.call(dmq__gcl, [ueq__uoc.n_arrays, wxerm__wsy,
            eqeuj__kthko, decu__qflr, qhjl__uivt, hox__zpkr.meminfo,
            ieiwc__blto])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        ycthq__yrb = arr.data
        gem__sqd = arr.indices
        sig = array_info_type(arr_type.data)
        wqk__loj = array_to_info_codegen(context, builder, sig, (ycthq__yrb
            ,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        cms__lcurt = array_to_info_codegen(context, builder, sig, (gem__sqd
            ,), False)
        tsiz__rplt = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, gem__sqd)
        ukd__qcrb = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, tsiz__rplt.null_bitmap).data
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='dict_str_array_to_info')
        mmpzq__dnm = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(dmq__gcl, [wqk__loj, cms__lcurt, builder.
            bitcast(ukd__qcrb, lir.IntType(8).as_pointer()), mmpzq__dnm])
    kwc__hrs = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        whx__mxd = context.compile_internal(builder, lambda a: len(a.dtype.
            categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        bfc__qzqm = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(bfc__qzqm, 1, 'C')
        kwc__hrs = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if kwc__hrs:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        uks__qykrq = builder.extract_value(arr.shape, 0)
        ehair__ehpwn = arr_type.dtype
        kswz__and = numba_to_c_type(ehair__ehpwn)
        leaqn__uhvl = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), kswz__and))
        if kwc__hrs:
            tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            dmq__gcl = cgutils.get_or_insert_function(builder.module,
                tkh__gfiym, name='categorical_array_to_info')
            return builder.call(dmq__gcl, [uks__qykrq, builder.bitcast(arr.
                data, lir.IntType(8).as_pointer()), builder.load(
                leaqn__uhvl), whx__mxd, arr.meminfo])
        else:
            tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            dmq__gcl = cgutils.get_or_insert_function(builder.module,
                tkh__gfiym, name='numpy_array_to_info')
            return builder.call(dmq__gcl, [uks__qykrq, builder.bitcast(arr.
                data, lir.IntType(8).as_pointer()), builder.load(
                leaqn__uhvl), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        ehair__ehpwn = arr_type.dtype
        mhf__xeq = ehair__ehpwn
        if isinstance(arr_type, DecimalArrayType):
            mhf__xeq = int128_type
        if arr_type == datetime_date_array_type:
            mhf__xeq = types.int64
        pfnjd__fzxc = context.make_array(types.Array(mhf__xeq, 1, 'C'))(context
            , builder, arr.data)
        uks__qykrq = builder.extract_value(pfnjd__fzxc.shape, 0)
        opzee__tro = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        kswz__and = numba_to_c_type(ehair__ehpwn)
        leaqn__uhvl = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), kswz__and))
        if isinstance(arr_type, DecimalArrayType):
            tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            dmq__gcl = cgutils.get_or_insert_function(builder.module,
                tkh__gfiym, name='decimal_array_to_info')
            return builder.call(dmq__gcl, [uks__qykrq, builder.bitcast(
                pfnjd__fzxc.data, lir.IntType(8).as_pointer()), builder.
                load(leaqn__uhvl), builder.bitcast(opzee__tro.data, lir.
                IntType(8).as_pointer()), pfnjd__fzxc.meminfo, opzee__tro.
                meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            dmq__gcl = cgutils.get_or_insert_function(builder.module,
                tkh__gfiym, name='nullable_array_to_info')
            return builder.call(dmq__gcl, [uks__qykrq, builder.bitcast(
                pfnjd__fzxc.data, lir.IntType(8).as_pointer()), builder.
                load(leaqn__uhvl), builder.bitcast(opzee__tro.data, lir.
                IntType(8).as_pointer()), pfnjd__fzxc.meminfo, opzee__tro.
                meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        skc__xmc = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        pgpvt__assf = context.make_array(arr_type.arr_type)(context,
            builder, arr.right)
        uks__qykrq = builder.extract_value(skc__xmc.shape, 0)
        kswz__and = numba_to_c_type(arr_type.arr_type.dtype)
        leaqn__uhvl = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), kswz__and))
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='interval_array_to_info')
        return builder.call(dmq__gcl, [uks__qykrq, builder.bitcast(skc__xmc
            .data, lir.IntType(8).as_pointer()), builder.bitcast(
            pgpvt__assf.data, lir.IntType(8).as_pointer()), builder.load(
            leaqn__uhvl), skc__xmc.meminfo, pgpvt__assf.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    zqhjx__xzegf = cgutils.alloca_once(builder, lir.IntType(64))
    xps__fofy = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    mdjdc__anw = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    dmq__gcl = cgutils.get_or_insert_function(builder.module, tkh__gfiym,
        name='info_to_numpy_array')
    builder.call(dmq__gcl, [in_info, zqhjx__xzegf, xps__fofy, mdjdc__anw])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    psl__fmui = context.get_value_type(types.intp)
    kcrto__zwng = cgutils.pack_array(builder, [builder.load(zqhjx__xzegf)],
        ty=psl__fmui)
    tsc__mikmr = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    yqf__ijmmp = cgutils.pack_array(builder, [tsc__mikmr], ty=psl__fmui)
    eqeuj__kthko = builder.bitcast(builder.load(xps__fofy), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=eqeuj__kthko, shape=
        kcrto__zwng, strides=yqf__ijmmp, itemsize=tsc__mikmr, meminfo=
        builder.load(mdjdc__anw))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    jtvqk__ejtm = context.make_helper(builder, arr_type)
    tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    dmq__gcl = cgutils.get_or_insert_function(builder.module, tkh__gfiym,
        name='info_to_list_string_array')
    builder.call(dmq__gcl, [in_info, jtvqk__ejtm._get_ptr_by_name('meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return jtvqk__ejtm._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    cadc__fzxoe = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        wxbwb__zueua = lengths_pos
        ddizr__eri = infos_pos
        ppl__lfosw, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        rrjxb__ssf = ArrayItemArrayPayloadType(arr_typ)
        pxwxl__qcoya = context.get_data_type(rrjxb__ssf)
        atd__qax = context.get_abi_sizeof(pxwxl__qcoya)
        rlpw__wtjio = define_array_item_dtor(context, builder, arr_typ,
            rrjxb__ssf)
        fxc__wbv = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, atd__qax), rlpw__wtjio)
        ztsyh__lhm = context.nrt.meminfo_data(builder, fxc__wbv)
        girt__ndj = builder.bitcast(ztsyh__lhm, pxwxl__qcoya.as_pointer())
        ueq__uoc = cgutils.create_struct_proxy(rrjxb__ssf)(context, builder)
        ueq__uoc.n_arrays = builder.extract_value(builder.load(lengths_ptr),
            wxbwb__zueua)
        ueq__uoc.data = ppl__lfosw
        sitdq__foc = builder.load(array_infos_ptr)
        wlqks__dqogt = builder.bitcast(builder.extract_value(sitdq__foc,
            ddizr__eri), cadc__fzxoe)
        ueq__uoc.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, wlqks__dqogt)
        ewk__kiib = builder.bitcast(builder.extract_value(sitdq__foc, 
            ddizr__eri + 1), cadc__fzxoe)
        ueq__uoc.null_bitmap = _lower_info_to_array_numpy(types.Array(types
            .uint8, 1, 'C'), context, builder, ewk__kiib)
        builder.store(ueq__uoc._getvalue(), girt__ndj)
        hox__zpkr = context.make_helper(builder, arr_typ)
        hox__zpkr.meminfo = fxc__wbv
        return hox__zpkr._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        fujex__kkz = []
        ddizr__eri = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for lotzr__nhzq in arr_typ.data:
            ppl__lfosw, lengths_pos, infos_pos = nested_to_array(context,
                builder, lotzr__nhzq, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            fujex__kkz.append(ppl__lfosw)
        rrjxb__ssf = StructArrayPayloadType(arr_typ.data)
        pxwxl__qcoya = context.get_value_type(rrjxb__ssf)
        atd__qax = context.get_abi_sizeof(pxwxl__qcoya)
        rlpw__wtjio = define_struct_arr_dtor(context, builder, arr_typ,
            rrjxb__ssf)
        fxc__wbv = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, atd__qax), rlpw__wtjio)
        ztsyh__lhm = context.nrt.meminfo_data(builder, fxc__wbv)
        girt__ndj = builder.bitcast(ztsyh__lhm, pxwxl__qcoya.as_pointer())
        ueq__uoc = cgutils.create_struct_proxy(rrjxb__ssf)(context, builder)
        ueq__uoc.data = cgutils.pack_array(builder, fujex__kkz
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, fujex__kkz)
        sitdq__foc = builder.load(array_infos_ptr)
        ewk__kiib = builder.bitcast(builder.extract_value(sitdq__foc,
            ddizr__eri), cadc__fzxoe)
        ueq__uoc.null_bitmap = _lower_info_to_array_numpy(types.Array(types
            .uint8, 1, 'C'), context, builder, ewk__kiib)
        builder.store(ueq__uoc._getvalue(), girt__ndj)
        oqez__ofogn = context.make_helper(builder, arr_typ)
        oqez__ofogn.meminfo = fxc__wbv
        return oqez__ofogn._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        sitdq__foc = builder.load(array_infos_ptr)
        fzl__ozpng = builder.bitcast(builder.extract_value(sitdq__foc,
            infos_pos), cadc__fzxoe)
        tlyzh__msj = context.make_helper(builder, arr_typ)
        zvecy__shz = ArrayItemArrayType(char_arr_type)
        hox__zpkr = context.make_helper(builder, zvecy__shz)
        tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='info_to_string_array')
        builder.call(dmq__gcl, [fzl__ozpng, hox__zpkr._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        tlyzh__msj.data = hox__zpkr._getvalue()
        return tlyzh__msj._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        sitdq__foc = builder.load(array_infos_ptr)
        wta__uvcb = builder.bitcast(builder.extract_value(sitdq__foc, 
            infos_pos + 1), cadc__fzxoe)
        return _lower_info_to_array_numpy(arr_typ, context, builder, wta__uvcb
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        mhf__xeq = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            mhf__xeq = int128_type
        elif arr_typ == datetime_date_array_type:
            mhf__xeq = types.int64
        sitdq__foc = builder.load(array_infos_ptr)
        ewk__kiib = builder.bitcast(builder.extract_value(sitdq__foc,
            infos_pos), cadc__fzxoe)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, ewk__kiib)
        wta__uvcb = builder.bitcast(builder.extract_value(sitdq__foc, 
            infos_pos + 1), cadc__fzxoe)
        arr.data = _lower_info_to_array_numpy(types.Array(mhf__xeq, 1, 'C'),
            context, builder, wta__uvcb)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, hiq__ixf = args
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
                return 1 + sum([get_num_arrays(lotzr__nhzq) for lotzr__nhzq in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(lotzr__nhzq) for lotzr__nhzq in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            zyack__xuj = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            zyack__xuj = _get_map_arr_data_type(arr_type)
        else:
            zyack__xuj = arr_type
        ohij__prmh = get_num_arrays(zyack__xuj)
        pmnas__cber = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), 0) for hiq__ixf in range(ohij__prmh)])
        lengths_ptr = cgutils.alloca_once_value(builder, pmnas__cber)
        peqrb__fsi = lir.Constant(lir.IntType(8).as_pointer(), None)
        pxti__oba = cgutils.pack_array(builder, [peqrb__fsi for hiq__ixf in
            range(get_num_infos(zyack__xuj))])
        array_infos_ptr = cgutils.alloca_once_value(builder, pxti__oba)
        tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='info_to_nested_array')
        builder.call(dmq__gcl, [in_info, builder.bitcast(lengths_ptr, lir.
            IntType(64).as_pointer()), builder.bitcast(array_infos_ptr, lir
            .IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, hiq__ixf, hiq__ixf = nested_to_array(context, builder,
            zyack__xuj, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            hqnli__npp = context.make_helper(builder, arr_type)
            hqnli__npp.data = arr
            context.nrt.incref(builder, zyack__xuj, arr)
            arr = hqnli__npp._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, zyack__xuj)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        tlyzh__msj = context.make_helper(builder, arr_type)
        zvecy__shz = ArrayItemArrayType(char_arr_type)
        hox__zpkr = context.make_helper(builder, zvecy__shz)
        tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='info_to_string_array')
        builder.call(dmq__gcl, [in_info, hox__zpkr._get_ptr_by_name('meminfo')]
            )
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        tlyzh__msj.data = hox__zpkr._getvalue()
        return tlyzh__msj._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='get_nested_info')
        wqk__loj = builder.call(dmq__gcl, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        cms__lcurt = builder.call(dmq__gcl, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        tde__ffopu = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        tde__ffopu.data = info_to_array_codegen(context, builder, sig, (
            wqk__loj, context.get_constant_null(arr_type.data)))
        clxj__bdo = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = clxj__bdo(array_info_type, clxj__bdo)
        tde__ffopu.indices = info_to_array_codegen(context, builder, sig, (
            cms__lcurt, context.get_constant_null(clxj__bdo)))
        tkh__gfiym = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='get_has_global_dictionary')
        mmpzq__dnm = builder.call(dmq__gcl, [in_info])
        tde__ffopu.has_global_dictionary = builder.trunc(mmpzq__dnm,
            cgutils.bool_t)
        return tde__ffopu._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        bfc__qzqm = get_categories_int_type(arr_type.dtype)
        stf__dqq = types.Array(bfc__qzqm, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(stf__dqq, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            efnnz__roxt = bodo.utils.utils.create_categorical_type(arr_type
                .dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(efnnz__roxt))
            int_type = arr_type.dtype.int_type
            pcx__ujpd = arr_type.dtype.data.data
            ekj__dwkai = context.get_constant_generic(builder, pcx__ujpd,
                efnnz__roxt)
            ehair__ehpwn = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(pcx__ujpd), [ekj__dwkai])
        else:
            ehair__ehpwn = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, ehair__ehpwn)
        out_arr.dtype = ehair__ehpwn
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        eqeuj__kthko = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = eqeuj__kthko
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        mhf__xeq = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            mhf__xeq = int128_type
        elif arr_type == datetime_date_array_type:
            mhf__xeq = types.int64
        xtj__coq = types.Array(mhf__xeq, 1, 'C')
        pfnjd__fzxc = context.make_array(xtj__coq)(context, builder)
        gjxd__igx = types.Array(types.uint8, 1, 'C')
        wmwp__eqvj = context.make_array(gjxd__igx)(context, builder)
        zqhjx__xzegf = cgutils.alloca_once(builder, lir.IntType(64))
        wowg__qalx = cgutils.alloca_once(builder, lir.IntType(64))
        xps__fofy = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        gez__ybsef = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        mdjdc__anw = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        bkqy__nltwf = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='info_to_nullable_array')
        builder.call(dmq__gcl, [in_info, zqhjx__xzegf, wowg__qalx,
            xps__fofy, gez__ybsef, mdjdc__anw, bkqy__nltwf])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        psl__fmui = context.get_value_type(types.intp)
        kcrto__zwng = cgutils.pack_array(builder, [builder.load(
            zqhjx__xzegf)], ty=psl__fmui)
        tsc__mikmr = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(mhf__xeq)))
        yqf__ijmmp = cgutils.pack_array(builder, [tsc__mikmr], ty=psl__fmui)
        eqeuj__kthko = builder.bitcast(builder.load(xps__fofy), context.
            get_data_type(mhf__xeq).as_pointer())
        numba.np.arrayobj.populate_array(pfnjd__fzxc, data=eqeuj__kthko,
            shape=kcrto__zwng, strides=yqf__ijmmp, itemsize=tsc__mikmr,
            meminfo=builder.load(mdjdc__anw))
        arr.data = pfnjd__fzxc._getvalue()
        kcrto__zwng = cgutils.pack_array(builder, [builder.load(wowg__qalx)
            ], ty=psl__fmui)
        tsc__mikmr = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        yqf__ijmmp = cgutils.pack_array(builder, [tsc__mikmr], ty=psl__fmui)
        eqeuj__kthko = builder.bitcast(builder.load(gez__ybsef), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(wmwp__eqvj, data=eqeuj__kthko,
            shape=kcrto__zwng, strides=yqf__ijmmp, itemsize=tsc__mikmr,
            meminfo=builder.load(bkqy__nltwf))
        arr.null_bitmap = wmwp__eqvj._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        skc__xmc = context.make_array(arr_type.arr_type)(context, builder)
        pgpvt__assf = context.make_array(arr_type.arr_type)(context, builder)
        zqhjx__xzegf = cgutils.alloca_once(builder, lir.IntType(64))
        lev__lapy = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        zxmjv__wad = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        pnrfd__nnauh = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        mvuo__kkd = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='info_to_interval_array')
        builder.call(dmq__gcl, [in_info, zqhjx__xzegf, lev__lapy,
            zxmjv__wad, pnrfd__nnauh, mvuo__kkd])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        psl__fmui = context.get_value_type(types.intp)
        kcrto__zwng = cgutils.pack_array(builder, [builder.load(
            zqhjx__xzegf)], ty=psl__fmui)
        tsc__mikmr = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        yqf__ijmmp = cgutils.pack_array(builder, [tsc__mikmr], ty=psl__fmui)
        ows__biaqz = builder.bitcast(builder.load(lev__lapy), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(skc__xmc, data=ows__biaqz, shape=
            kcrto__zwng, strides=yqf__ijmmp, itemsize=tsc__mikmr, meminfo=
            builder.load(pnrfd__nnauh))
        arr.left = skc__xmc._getvalue()
        uwybk__nocf = builder.bitcast(builder.load(zxmjv__wad), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(pgpvt__assf, data=uwybk__nocf,
            shape=kcrto__zwng, strides=yqf__ijmmp, itemsize=tsc__mikmr,
            meminfo=builder.load(mvuo__kkd))
        arr.right = pgpvt__assf._getvalue()
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
        uks__qykrq, hiq__ixf = args
        kswz__and = numba_to_c_type(array_type.dtype)
        leaqn__uhvl = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), kswz__and))
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='alloc_numpy')
        return builder.call(dmq__gcl, [uks__qykrq, builder.load(leaqn__uhvl)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        uks__qykrq, pmxpx__kxw = args
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='alloc_string_array')
        return builder.call(dmq__gcl, [uks__qykrq, pmxpx__kxw])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    uts__faaq, = args
    rczsu__ysyo = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], uts__faaq)
    tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer().as_pointer(), lir.IntType(64)])
    dmq__gcl = cgutils.get_or_insert_function(builder.module, tkh__gfiym,
        name='arr_info_list_to_table')
    return builder.call(dmq__gcl, [rczsu__ysyo.data, rczsu__ysyo.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='info_from_table')
        return builder.call(dmq__gcl, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    lubok__wggt = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, lij__leb, hiq__ixf = args
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='info_from_table')
        kgv__bfzv = cgutils.create_struct_proxy(lubok__wggt)(context, builder)
        kgv__bfzv.parent = cgutils.get_null_value(kgv__bfzv.parent.type)
        zoht__wwt = context.make_array(table_idx_arr_t)(context, builder,
            lij__leb)
        aqod__jap = context.get_constant(types.int64, -1)
        hdzj__khs = context.get_constant(types.int64, 0)
        kjsjx__aaf = cgutils.alloca_once_value(builder, hdzj__khs)
        for t, yxcuq__izb in lubok__wggt.type_to_blk.items():
            purp__zrijf = context.get_constant(types.int64, len(lubok__wggt
                .block_to_arr_ind[yxcuq__izb]))
            hiq__ixf, pthln__duk = ListInstance.allocate_ex(context,
                builder, types.List(t), purp__zrijf)
            pthln__duk.size = purp__zrijf
            gzqgt__vsxnn = context.make_constant_array(builder, types.Array
                (types.int64, 1, 'C'), np.array(lubok__wggt.
                block_to_arr_ind[yxcuq__izb], dtype=np.int64))
            rttoo__bkc = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, gzqgt__vsxnn)
            with cgutils.for_range(builder, purp__zrijf) as jrh__lbdd:
                kni__aab = jrh__lbdd.index
                qzhw__obqdb = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    rttoo__bkc, kni__aab)
                rhzzn__tqyik = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, zoht__wwt, qzhw__obqdb)
                oqcge__gdonn = builder.icmp_unsigned('!=', rhzzn__tqyik,
                    aqod__jap)
                with builder.if_else(oqcge__gdonn) as (dxqnj__dael, zcfa__lupdb
                    ):
                    with dxqnj__dael:
                        wgym__gba = builder.call(dmq__gcl, [cpp_table,
                            rhzzn__tqyik])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            wgym__gba])
                        pthln__duk.inititem(kni__aab, arr, incref=False)
                        uks__qykrq = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(uks__qykrq, kjsjx__aaf)
                    with zcfa__lupdb:
                        qltvo__enecj = context.get_constant_null(t)
                        pthln__duk.inititem(kni__aab, qltvo__enecj, incref=
                            False)
            setattr(kgv__bfzv, f'block_{yxcuq__izb}', pthln__duk.value)
        kgv__bfzv.len = builder.load(kjsjx__aaf)
        return kgv__bfzv._getvalue()
    return lubok__wggt(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    pdmt__pyksa = out_col_inds_t.instance_type.meta
    lubok__wggt = unwrap_typeref(out_types_t.types[0])
    yso__hsxc = [unwrap_typeref(out_types_t.types[kni__aab]) for kni__aab in
        range(1, len(out_types_t.types))]
    yqz__yii = {}
    wst__kfgz = get_overload_const_int(n_table_cols_t)
    dwt__yux = {uwt__nexg: kni__aab for kni__aab, uwt__nexg in enumerate(
        pdmt__pyksa)}
    if not is_overload_none(unknown_cat_arrs_t):
        wldc__dgep = {lqwwb__ejn: kni__aab for kni__aab, lqwwb__ejn in
            enumerate(cat_inds_t.instance_type.meta)}
    wyc__akcfo = []
    pbpc__jbhln = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(lubok__wggt, bodo.TableType):
        pbpc__jbhln += f'  py_table = init_table(py_table_type, False)\n'
        pbpc__jbhln += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for sdty__jfgk, yxcuq__izb in lubok__wggt.type_to_blk.items():
            ymqe__vtxs = [dwt__yux.get(kni__aab, -1) for kni__aab in
                lubok__wggt.block_to_arr_ind[yxcuq__izb]]
            yqz__yii[f'out_inds_{yxcuq__izb}'] = np.array(ymqe__vtxs, np.int64)
            yqz__yii[f'out_type_{yxcuq__izb}'] = sdty__jfgk
            yqz__yii[f'typ_list_{yxcuq__izb}'] = types.List(sdty__jfgk)
            jemwd__bjn = f'out_type_{yxcuq__izb}'
            if type_has_unknown_cats(sdty__jfgk):
                if is_overload_none(unknown_cat_arrs_t):
                    pbpc__jbhln += f"""  in_arr_list_{yxcuq__izb} = get_table_block(out_types_t[0], {yxcuq__izb})
"""
                    jemwd__bjn = f'in_arr_list_{yxcuq__izb}[i]'
                else:
                    yqz__yii[f'cat_arr_inds_{yxcuq__izb}'] = np.array([
                        wldc__dgep.get(kni__aab, -1) for kni__aab in
                        lubok__wggt.block_to_arr_ind[yxcuq__izb]], np.int64)
                    jemwd__bjn = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{yxcuq__izb}[i]]')
            purp__zrijf = len(lubok__wggt.block_to_arr_ind[yxcuq__izb])
            pbpc__jbhln += f"""  arr_list_{yxcuq__izb} = alloc_list_like(typ_list_{yxcuq__izb}, {purp__zrijf}, False)
"""
            pbpc__jbhln += f'  for i in range(len(arr_list_{yxcuq__izb})):\n'
            pbpc__jbhln += (
                f'    cpp_ind_{yxcuq__izb} = out_inds_{yxcuq__izb}[i]\n')
            pbpc__jbhln += f'    if cpp_ind_{yxcuq__izb} == -1:\n'
            pbpc__jbhln += f'      continue\n'
            pbpc__jbhln += f"""    arr_{yxcuq__izb} = info_to_array(info_from_table(cpp_table, cpp_ind_{yxcuq__izb}), {jemwd__bjn})
"""
            pbpc__jbhln += f'    arr_list_{yxcuq__izb}[i] = arr_{yxcuq__izb}\n'
            pbpc__jbhln += f"""  py_table = set_table_block(py_table, arr_list_{yxcuq__izb}, {yxcuq__izb})
"""
        wyc__akcfo.append('py_table')
    elif lubok__wggt != types.none:
        ivcp__pnfx = dwt__yux.get(0, -1)
        if ivcp__pnfx != -1:
            yqz__yii[f'arr_typ_arg0'] = lubok__wggt
            jemwd__bjn = f'arr_typ_arg0'
            if type_has_unknown_cats(lubok__wggt):
                if is_overload_none(unknown_cat_arrs_t):
                    jemwd__bjn = f'out_types_t[0]'
                else:
                    jemwd__bjn = f'unknown_cat_arrs_t[{wldc__dgep[0]}]'
            pbpc__jbhln += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {ivcp__pnfx}), {jemwd__bjn})
"""
            wyc__akcfo.append('out_arg0')
    for kni__aab, t in enumerate(yso__hsxc):
        ivcp__pnfx = dwt__yux.get(wst__kfgz + kni__aab, -1)
        if ivcp__pnfx != -1:
            yqz__yii[f'extra_arr_type_{kni__aab}'] = t
            jemwd__bjn = f'extra_arr_type_{kni__aab}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    jemwd__bjn = f'out_types_t[{kni__aab + 1}]'
                else:
                    jemwd__bjn = (
                        f'unknown_cat_arrs_t[{wldc__dgep[wst__kfgz + kni__aab]}]'
                        )
            pbpc__jbhln += f"""  out_{kni__aab} = info_to_array(info_from_table(cpp_table, {ivcp__pnfx}), {jemwd__bjn})
"""
            wyc__akcfo.append(f'out_{kni__aab}')
    urg__vdpc = ',' if len(wyc__akcfo) == 1 else ''
    pbpc__jbhln += f"  return ({', '.join(wyc__akcfo)}{urg__vdpc})\n"
    yqz__yii.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(pdmt__pyksa), 'py_table_type': lubok__wggt})
    yluop__tju = {}
    exec(pbpc__jbhln, yqz__yii, yluop__tju)
    return yluop__tju['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    lubok__wggt = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, hiq__ixf = args
        yvfam__xcp = cgutils.create_struct_proxy(lubok__wggt)(context,
            builder, py_table)
        if lubok__wggt.has_runtime_cols:
            dzla__ztxt = lir.Constant(lir.IntType(64), 0)
            for yxcuq__izb, t in enumerate(lubok__wggt.arr_types):
                menn__qxd = getattr(yvfam__xcp, f'block_{yxcuq__izb}')
                abny__xkvh = ListInstance(context, builder, types.List(t),
                    menn__qxd)
                dzla__ztxt = builder.add(dzla__ztxt, abny__xkvh.size)
        else:
            dzla__ztxt = lir.Constant(lir.IntType(64), len(lubok__wggt.
                arr_types))
        hiq__ixf, snkjj__fporb = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), dzla__ztxt)
        snkjj__fporb.size = dzla__ztxt
        if lubok__wggt.has_runtime_cols:
            xau__tqlh = lir.Constant(lir.IntType(64), 0)
            for yxcuq__izb, t in enumerate(lubok__wggt.arr_types):
                menn__qxd = getattr(yvfam__xcp, f'block_{yxcuq__izb}')
                abny__xkvh = ListInstance(context, builder, types.List(t),
                    menn__qxd)
                purp__zrijf = abny__xkvh.size
                with cgutils.for_range(builder, purp__zrijf) as jrh__lbdd:
                    kni__aab = jrh__lbdd.index
                    arr = abny__xkvh.getitem(kni__aab)
                    cqhe__agsyz = signature(array_info_type, t)
                    ptel__kym = arr,
                    bvhrk__kgdr = array_to_info_codegen(context, builder,
                        cqhe__agsyz, ptel__kym)
                    snkjj__fporb.inititem(builder.add(xau__tqlh, kni__aab),
                        bvhrk__kgdr, incref=False)
                xau__tqlh = builder.add(xau__tqlh, purp__zrijf)
        else:
            for t, yxcuq__izb in lubok__wggt.type_to_blk.items():
                purp__zrijf = context.get_constant(types.int64, len(
                    lubok__wggt.block_to_arr_ind[yxcuq__izb]))
                menn__qxd = getattr(yvfam__xcp, f'block_{yxcuq__izb}')
                abny__xkvh = ListInstance(context, builder, types.List(t),
                    menn__qxd)
                gzqgt__vsxnn = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(lubok__wggt.
                    block_to_arr_ind[yxcuq__izb], dtype=np.int64))
                rttoo__bkc = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, gzqgt__vsxnn)
                with cgutils.for_range(builder, purp__zrijf) as jrh__lbdd:
                    kni__aab = jrh__lbdd.index
                    qzhw__obqdb = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), rttoo__bkc, kni__aab)
                    yir__alfmz = signature(types.none, lubok__wggt, types.
                        List(t), types.int64, types.int64)
                    gts__mvx = py_table, menn__qxd, kni__aab, qzhw__obqdb
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, yir__alfmz, gts__mvx)
                    arr = abny__xkvh.getitem(kni__aab)
                    cqhe__agsyz = signature(array_info_type, t)
                    ptel__kym = arr,
                    bvhrk__kgdr = array_to_info_codegen(context, builder,
                        cqhe__agsyz, ptel__kym)
                    snkjj__fporb.inititem(qzhw__obqdb, bvhrk__kgdr, incref=
                        False)
        nrfba__ocy = snkjj__fporb.value
        xrdh__efrt = signature(table_type, types.List(array_info_type))
        zxwh__klrq = nrfba__ocy,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            xrdh__efrt, zxwh__klrq)
        context.nrt.decref(builder, types.List(array_info_type), nrfba__ocy)
        return cpp_table
    return table_type(lubok__wggt, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    aro__tfj = in_col_inds_t.instance_type.meta
    yqz__yii = {}
    wst__kfgz = get_overload_const_int(n_table_cols_t)
    ikzv__pndg = defaultdict(list)
    dwt__yux = {}
    for kni__aab, uwt__nexg in enumerate(aro__tfj):
        if uwt__nexg in dwt__yux:
            ikzv__pndg[uwt__nexg].append(kni__aab)
        else:
            dwt__yux[uwt__nexg] = kni__aab
    pbpc__jbhln = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    pbpc__jbhln += (
        f'  cpp_arr_list = alloc_empty_list_type({len(aro__tfj)}, array_info_type)\n'
        )
    if py_table != types.none:
        for yxcuq__izb in py_table.type_to_blk.values():
            ymqe__vtxs = [dwt__yux.get(kni__aab, -1) for kni__aab in
                py_table.block_to_arr_ind[yxcuq__izb]]
            yqz__yii[f'out_inds_{yxcuq__izb}'] = np.array(ymqe__vtxs, np.int64)
            yqz__yii[f'arr_inds_{yxcuq__izb}'] = np.array(py_table.
                block_to_arr_ind[yxcuq__izb], np.int64)
            pbpc__jbhln += (
                f'  arr_list_{yxcuq__izb} = get_table_block(py_table, {yxcuq__izb})\n'
                )
            pbpc__jbhln += f'  for i in range(len(arr_list_{yxcuq__izb})):\n'
            pbpc__jbhln += (
                f'    out_arr_ind_{yxcuq__izb} = out_inds_{yxcuq__izb}[i]\n')
            pbpc__jbhln += f'    if out_arr_ind_{yxcuq__izb} == -1:\n'
            pbpc__jbhln += f'      continue\n'
            pbpc__jbhln += (
                f'    arr_ind_{yxcuq__izb} = arr_inds_{yxcuq__izb}[i]\n')
            pbpc__jbhln += f"""    ensure_column_unboxed(py_table, arr_list_{yxcuq__izb}, i, arr_ind_{yxcuq__izb})
"""
            pbpc__jbhln += f"""    cpp_arr_list[out_arr_ind_{yxcuq__izb}] = array_to_info(arr_list_{yxcuq__izb}[i])
"""
        for rinok__nnch, ytfyr__fzse in ikzv__pndg.items():
            if rinok__nnch < wst__kfgz:
                yxcuq__izb = py_table.block_nums[rinok__nnch]
                xgul__nvra = py_table.block_offsets[rinok__nnch]
                for ivcp__pnfx in ytfyr__fzse:
                    pbpc__jbhln += f"""  cpp_arr_list[{ivcp__pnfx}] = array_to_info(arr_list_{yxcuq__izb}[{xgul__nvra}])
"""
    for kni__aab in range(len(extra_arrs_tup)):
        rat__xam = dwt__yux.get(wst__kfgz + kni__aab, -1)
        if rat__xam != -1:
            ein__sva = [rat__xam] + ikzv__pndg.get(wst__kfgz + kni__aab, [])
            for ivcp__pnfx in ein__sva:
                pbpc__jbhln += f"""  cpp_arr_list[{ivcp__pnfx}] = array_to_info(extra_arrs_tup[{kni__aab}])
"""
    pbpc__jbhln += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    yqz__yii.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    yluop__tju = {}
    exec(pbpc__jbhln, yqz__yii, yluop__tju)
    return yluop__tju['impl']


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
        tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='delete_table')
        builder.call(dmq__gcl, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='shuffle_table')
        ldcfu__csz = builder.call(dmq__gcl, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
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
        tkh__gfiym = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='delete_shuffle_info')
        return builder.call(dmq__gcl, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='reverse_shuffle_table')
        return builder.call(dmq__gcl, args)
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
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='hash_join_table')
        ldcfu__csz = builder.call(dmq__gcl, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
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
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='sort_values_table')
        ldcfu__csz = builder.call(dmq__gcl, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='sample_table')
        ldcfu__csz = builder.call(dmq__gcl, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='shuffle_renormalization')
        ldcfu__csz = builder.call(dmq__gcl, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='shuffle_renormalization_group')
        ldcfu__csz = builder.call(dmq__gcl, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='drop_duplicates_table')
        ldcfu__csz = builder.call(dmq__gcl, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
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
        tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        dmq__gcl = cgutils.get_or_insert_function(builder.module,
            tkh__gfiym, name='groupby_and_aggregate')
        ldcfu__csz = builder.call(dmq__gcl, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return ldcfu__csz
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
    olu__dnlq = array_to_info(in_arr)
    kzfog__hvspi = array_to_info(in_values)
    afckq__ugz = array_to_info(out_arr)
    gfsvt__jdk = arr_info_list_to_table([olu__dnlq, kzfog__hvspi, afckq__ugz])
    _array_isin(afckq__ugz, olu__dnlq, kzfog__hvspi, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(gfsvt__jdk)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    olu__dnlq = array_to_info(in_arr)
    afckq__ugz = array_to_info(out_arr)
    _get_search_regex(olu__dnlq, case, match, pat, afckq__ugz)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    lhbl__zjy = col_array_typ.dtype
    if isinstance(lhbl__zjy, types.Number) or lhbl__zjy in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                kgv__bfzv, dqh__qcir = args
                kgv__bfzv = builder.bitcast(kgv__bfzv, lir.IntType(8).
                    as_pointer().as_pointer())
                euymx__ska = lir.Constant(lir.IntType(64), c_ind)
                ukw__zaja = builder.load(builder.gep(kgv__bfzv, [euymx__ska]))
                ukw__zaja = builder.bitcast(ukw__zaja, context.
                    get_data_type(lhbl__zjy).as_pointer())
                return builder.load(builder.gep(ukw__zaja, [dqh__qcir]))
            return lhbl__zjy(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                kgv__bfzv, dqh__qcir = args
                kgv__bfzv = builder.bitcast(kgv__bfzv, lir.IntType(8).
                    as_pointer().as_pointer())
                euymx__ska = lir.Constant(lir.IntType(64), c_ind)
                ukw__zaja = builder.load(builder.gep(kgv__bfzv, [euymx__ska]))
                tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                kdavw__gsbhs = cgutils.get_or_insert_function(builder.
                    module, tkh__gfiym, name='array_info_getitem')
                rlir__gcn = cgutils.alloca_once(builder, lir.IntType(64))
                args = ukw__zaja, dqh__qcir, rlir__gcn
                xps__fofy = builder.call(kdavw__gsbhs, args)
                return context.make_tuple(builder, sig.return_type, [
                    xps__fofy, builder.load(rlir__gcn)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                qpwj__kjz = lir.Constant(lir.IntType(64), 1)
                cnnio__xcxx = lir.Constant(lir.IntType(64), 2)
                kgv__bfzv, dqh__qcir = args
                kgv__bfzv = builder.bitcast(kgv__bfzv, lir.IntType(8).
                    as_pointer().as_pointer())
                euymx__ska = lir.Constant(lir.IntType(64), c_ind)
                ukw__zaja = builder.load(builder.gep(kgv__bfzv, [euymx__ska]))
                tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                fhel__njx = cgutils.get_or_insert_function(builder.module,
                    tkh__gfiym, name='get_nested_info')
                args = ukw__zaja, cnnio__xcxx
                xnjy__pcci = builder.call(fhel__njx, args)
                tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                xaace__fiej = cgutils.get_or_insert_function(builder.module,
                    tkh__gfiym, name='array_info_getdata1')
                args = xnjy__pcci,
                irdow__wjc = builder.call(xaace__fiej, args)
                irdow__wjc = builder.bitcast(irdow__wjc, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                tvoz__aykj = builder.sext(builder.load(builder.gep(
                    irdow__wjc, [dqh__qcir])), lir.IntType(64))
                args = ukw__zaja, qpwj__kjz
                tpkr__ayif = builder.call(fhel__njx, args)
                tkh__gfiym = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                kdavw__gsbhs = cgutils.get_or_insert_function(builder.
                    module, tkh__gfiym, name='array_info_getitem')
                rlir__gcn = cgutils.alloca_once(builder, lir.IntType(64))
                args = tpkr__ayif, tvoz__aykj, rlir__gcn
                xps__fofy = builder.call(kdavw__gsbhs, args)
                return context.make_tuple(builder, sig.return_type, [
                    xps__fofy, builder.load(rlir__gcn)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{lhbl__zjy}' column data type not supported"
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
                nydd__pnwy, dqh__qcir = args
                nydd__pnwy = builder.bitcast(nydd__pnwy, lir.IntType(8).
                    as_pointer().as_pointer())
                euymx__ska = lir.Constant(lir.IntType(64), c_ind)
                ukw__zaja = builder.load(builder.gep(nydd__pnwy, [euymx__ska]))
                qhjl__uivt = builder.bitcast(ukw__zaja, context.
                    get_data_type(types.bool_).as_pointer())
                yhc__gza = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    qhjl__uivt, dqh__qcir)
                uyaj__owq = builder.icmp_unsigned('!=', yhc__gza, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(uyaj__owq, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        lhbl__zjy = col_array_dtype.dtype
        if lhbl__zjy in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    kgv__bfzv, dqh__qcir = args
                    kgv__bfzv = builder.bitcast(kgv__bfzv, lir.IntType(8).
                        as_pointer().as_pointer())
                    euymx__ska = lir.Constant(lir.IntType(64), c_ind)
                    ukw__zaja = builder.load(builder.gep(kgv__bfzv, [
                        euymx__ska]))
                    ukw__zaja = builder.bitcast(ukw__zaja, context.
                        get_data_type(lhbl__zjy).as_pointer())
                    xce__ogl = builder.load(builder.gep(ukw__zaja, [dqh__qcir])
                        )
                    uyaj__owq = builder.icmp_unsigned('!=', xce__ogl, lir.
                        Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(uyaj__owq, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(lhbl__zjy, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    kgv__bfzv, dqh__qcir = args
                    kgv__bfzv = builder.bitcast(kgv__bfzv, lir.IntType(8).
                        as_pointer().as_pointer())
                    euymx__ska = lir.Constant(lir.IntType(64), c_ind)
                    ukw__zaja = builder.load(builder.gep(kgv__bfzv, [
                        euymx__ska]))
                    ukw__zaja = builder.bitcast(ukw__zaja, context.
                        get_data_type(lhbl__zjy).as_pointer())
                    xce__ogl = builder.load(builder.gep(ukw__zaja, [dqh__qcir])
                        )
                    eti__pfk = signature(types.bool_, lhbl__zjy)
                    yhc__gza = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, eti__pfk, (xce__ogl,))
                    return builder.not_(builder.sext(yhc__gza, lir.IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
