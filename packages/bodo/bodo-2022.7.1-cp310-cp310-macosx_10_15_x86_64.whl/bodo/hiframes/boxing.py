"""
Boxing and unboxing support for DataFrame, Series, etc.
"""
import datetime
import decimal
import warnings
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.ir_utils import GuardException, guard
from numba.core.typing import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, intrinsic, typeof_impl, unbox
from numba.np import numpy_support
from numba.np.arrayobj import _getitem_array_single_int
from numba.typed.typeddict import Dict
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFramePayloadType, DataFrameType, check_runtime_cols_unsupported, construct_dataframe
from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType, typeof_pd_int_dtype
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType, PandasDatetimeTZDtype
from bodo.libs.str_arr_ext import string_array_type, string_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import BodoError, BodoWarning, dtype_to_array_type, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
ll.add_symbol('is_np_array', hstr_ext.is_np_array)
ll.add_symbol('array_size', hstr_ext.array_size)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
TABLE_FORMAT_THRESHOLD = 20
_use_dict_str_type = False


def _set_bodo_meta_in_pandas():
    if '_bodo_meta' not in pd.Series._metadata:
        pd.Series._metadata.append('_bodo_meta')
    if '_bodo_meta' not in pd.DataFrame._metadata:
        pd.DataFrame._metadata.append('_bodo_meta')


_set_bodo_meta_in_pandas()


@typeof_impl.register(pd.DataFrame)
def typeof_pd_dataframe(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    cap__ndlz = tuple(val.columns.to_list())
    vqrb__nztf = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        guajg__gfrg = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        guajg__gfrg = numba.typeof(val.index)
    gyem__hqtv = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    gsbb__ltz = len(vqrb__nztf) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(vqrb__nztf, guajg__gfrg, cap__ndlz, gyem__hqtv,
        is_table_format=gsbb__ltz)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    gyem__hqtv = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        elvwm__hgyc = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        elvwm__hgyc = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    mqvh__nwok = dtype_to_array_type(dtype)
    if _use_dict_str_type and mqvh__nwok == string_array_type:
        mqvh__nwok = bodo.dict_str_arr_type
    return SeriesType(dtype, data=mqvh__nwok, index=elvwm__hgyc, name_typ=
        numba.typeof(val.name), dist=gyem__hqtv)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    cal__chgs = c.pyapi.object_getattr_string(val, 'index')
    maoue__lhb = c.pyapi.to_native_value(typ.index, cal__chgs).value
    c.pyapi.decref(cal__chgs)
    if typ.is_table_format:
        zkr__dpnz = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        zkr__dpnz.parent = val
        for trptj__hbq, sdhm__drkuy in typ.table_type.type_to_blk.items():
            fap__ykdi = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[sdhm__drkuy]))
            rtw__yeg, kbkcp__vik = ListInstance.allocate_ex(c.context, c.
                builder, types.List(trptj__hbq), fap__ykdi)
            kbkcp__vik.size = fap__ykdi
            setattr(zkr__dpnz, f'block_{sdhm__drkuy}', kbkcp__vik.value)
        ydc__fsyv = c.pyapi.call_method(val, '__len__', ())
        akz__xcx = c.pyapi.long_as_longlong(ydc__fsyv)
        c.pyapi.decref(ydc__fsyv)
        zkr__dpnz.len = akz__xcx
        bpv__zyqmj = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [zkr__dpnz._getvalue()])
    else:
        xdhpy__bkeo = [c.context.get_constant_null(trptj__hbq) for
            trptj__hbq in typ.data]
        bpv__zyqmj = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            xdhpy__bkeo)
    ihxc__jpm = construct_dataframe(c.context, c.builder, typ, bpv__zyqmj,
        maoue__lhb, val, None)
    return NativeValue(ihxc__jpm)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        tzvoj__ypn = df._bodo_meta['type_metadata'][1]
    else:
        tzvoj__ypn = [None] * len(df.columns)
    whwl__pktpn = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=tzvoj__ypn[i])) for i in range(len(df.columns))]
    whwl__pktpn = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        trptj__hbq == string_array_type else trptj__hbq) for trptj__hbq in
        whwl__pktpn]
    return tuple(whwl__pktpn)


class SeriesDtypeEnum(Enum):
    Int8 = 0
    UInt8 = 1
    Int32 = 2
    UInt32 = 3
    Int64 = 4
    UInt64 = 7
    Float32 = 5
    Float64 = 6
    Int16 = 8
    UInt16 = 9
    STRING = 10
    Bool = 11
    Decimal = 12
    Datime_Date = 13
    NP_Datetime64ns = 14
    NP_Timedelta64ns = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 21
    ARRAY = 22
    PD_nullable_Int8 = 23
    PD_nullable_UInt8 = 24
    PD_nullable_Int16 = 25
    PD_nullable_UInt16 = 26
    PD_nullable_Int32 = 27
    PD_nullable_UInt32 = 28
    PD_nullable_Int64 = 29
    PD_nullable_UInt64 = 30
    PD_nullable_bool = 31
    CategoricalType = 32
    NoneType = 33
    Literal = 34
    IntegerArray = 35
    RangeIndexType = 36
    DatetimeIndexType = 37
    NumericIndexType = 38
    PeriodIndexType = 39
    IntervalIndexType = 40
    CategoricalIndexType = 41
    StringIndexType = 42
    BinaryIndexType = 43
    TimedeltaIndexType = 44
    LiteralType = 45


_one_to_one_type_to_enum_map = {types.int8: SeriesDtypeEnum.Int8.value,
    types.uint8: SeriesDtypeEnum.UInt8.value, types.int32: SeriesDtypeEnum.
    Int32.value, types.uint32: SeriesDtypeEnum.UInt32.value, types.int64:
    SeriesDtypeEnum.Int64.value, types.uint64: SeriesDtypeEnum.UInt64.value,
    types.float32: SeriesDtypeEnum.Float32.value, types.float64:
    SeriesDtypeEnum.Float64.value, types.NPDatetime('ns'): SeriesDtypeEnum.
    NP_Datetime64ns.value, types.NPTimedelta('ns'): SeriesDtypeEnum.
    NP_Timedelta64ns.value, types.bool_: SeriesDtypeEnum.Bool.value, types.
    int16: SeriesDtypeEnum.Int16.value, types.uint16: SeriesDtypeEnum.
    UInt16.value, types.Integer('int128', 128): SeriesDtypeEnum.Int128.
    value, bodo.hiframes.datetime_date_ext.datetime_date_type:
    SeriesDtypeEnum.Datime_Date.value, IntDtype(types.int8):
    SeriesDtypeEnum.PD_nullable_Int8.value, IntDtype(types.uint8):
    SeriesDtypeEnum.PD_nullable_UInt8.value, IntDtype(types.int16):
    SeriesDtypeEnum.PD_nullable_Int16.value, IntDtype(types.uint16):
    SeriesDtypeEnum.PD_nullable_UInt16.value, IntDtype(types.int32):
    SeriesDtypeEnum.PD_nullable_Int32.value, IntDtype(types.uint32):
    SeriesDtypeEnum.PD_nullable_UInt32.value, IntDtype(types.int64):
    SeriesDtypeEnum.PD_nullable_Int64.value, IntDtype(types.uint64):
    SeriesDtypeEnum.PD_nullable_UInt64.value, bytes_type: SeriesDtypeEnum.
    BINARY.value, string_type: SeriesDtypeEnum.STRING.value, bodo.bool_:
    SeriesDtypeEnum.Bool.value, types.none: SeriesDtypeEnum.NoneType.value}
_one_to_one_enum_to_type_map = {SeriesDtypeEnum.Int8.value: types.int8,
    SeriesDtypeEnum.UInt8.value: types.uint8, SeriesDtypeEnum.Int32.value:
    types.int32, SeriesDtypeEnum.UInt32.value: types.uint32,
    SeriesDtypeEnum.Int64.value: types.int64, SeriesDtypeEnum.UInt64.value:
    types.uint64, SeriesDtypeEnum.Float32.value: types.float32,
    SeriesDtypeEnum.Float64.value: types.float64, SeriesDtypeEnum.
    NP_Datetime64ns.value: types.NPDatetime('ns'), SeriesDtypeEnum.
    NP_Timedelta64ns.value: types.NPTimedelta('ns'), SeriesDtypeEnum.Int16.
    value: types.int16, SeriesDtypeEnum.UInt16.value: types.uint16,
    SeriesDtypeEnum.Int128.value: types.Integer('int128', 128),
    SeriesDtypeEnum.Datime_Date.value: bodo.hiframes.datetime_date_ext.
    datetime_date_type, SeriesDtypeEnum.PD_nullable_Int8.value: IntDtype(
    types.int8), SeriesDtypeEnum.PD_nullable_UInt8.value: IntDtype(types.
    uint8), SeriesDtypeEnum.PD_nullable_Int16.value: IntDtype(types.int16),
    SeriesDtypeEnum.PD_nullable_UInt16.value: IntDtype(types.uint16),
    SeriesDtypeEnum.PD_nullable_Int32.value: IntDtype(types.int32),
    SeriesDtypeEnum.PD_nullable_UInt32.value: IntDtype(types.uint32),
    SeriesDtypeEnum.PD_nullable_Int64.value: IntDtype(types.int64),
    SeriesDtypeEnum.PD_nullable_UInt64.value: IntDtype(types.uint64),
    SeriesDtypeEnum.BINARY.value: bytes_type, SeriesDtypeEnum.STRING.value:
    string_type, SeriesDtypeEnum.Bool.value: bodo.bool_, SeriesDtypeEnum.
    NoneType.value: types.none}


def _dtype_from_type_enum_list(typ_enum_list):
    lpem__kov, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(lpem__kov) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {lpem__kov}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        mjqr__wkhpt, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return mjqr__wkhpt, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        mjqr__wkhpt, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return mjqr__wkhpt, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        dtc__tuk = typ_enum_list[1]
        qbjl__brb = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(dtc__tuk, qbjl__brb)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        tjrai__bpdio = typ_enum_list[1]
        revpq__uzvb = tuple(typ_enum_list[2:2 + tjrai__bpdio])
        vynl__ycx = typ_enum_list[2 + tjrai__bpdio:]
        jlgaa__lys = []
        for i in range(tjrai__bpdio):
            vynl__ycx, enfpn__rtlbh = _dtype_from_type_enum_list_recursor(
                vynl__ycx)
            jlgaa__lys.append(enfpn__rtlbh)
        return vynl__ycx, StructType(tuple(jlgaa__lys), revpq__uzvb)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        bbwma__swtu = typ_enum_list[1]
        vynl__ycx = typ_enum_list[2:]
        return vynl__ycx, bbwma__swtu
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        bbwma__swtu = typ_enum_list[1]
        vynl__ycx = typ_enum_list[2:]
        return vynl__ycx, numba.types.literal(bbwma__swtu)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        vynl__ycx, xwmc__vgdbd = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        vynl__ycx, krwo__xwfeq = _dtype_from_type_enum_list_recursor(vynl__ycx)
        vynl__ycx, oeia__iczxo = _dtype_from_type_enum_list_recursor(vynl__ycx)
        vynl__ycx, flqxn__fykh = _dtype_from_type_enum_list_recursor(vynl__ycx)
        vynl__ycx, mgy__hyhr = _dtype_from_type_enum_list_recursor(vynl__ycx)
        return vynl__ycx, PDCategoricalDtype(xwmc__vgdbd, krwo__xwfeq,
            oeia__iczxo, flqxn__fykh, mgy__hyhr)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        vynl__ycx, dypu__ognl = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return vynl__ycx, DatetimeIndexType(dypu__ognl)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        vynl__ycx, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        vynl__ycx, dypu__ognl = _dtype_from_type_enum_list_recursor(vynl__ycx)
        vynl__ycx, flqxn__fykh = _dtype_from_type_enum_list_recursor(vynl__ycx)
        return vynl__ycx, NumericIndexType(dtype, dypu__ognl, flqxn__fykh)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        vynl__ycx, qlfq__giwhr = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        vynl__ycx, dypu__ognl = _dtype_from_type_enum_list_recursor(vynl__ycx)
        return vynl__ycx, PeriodIndexType(qlfq__giwhr, dypu__ognl)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        vynl__ycx, flqxn__fykh = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        vynl__ycx, dypu__ognl = _dtype_from_type_enum_list_recursor(vynl__ycx)
        return vynl__ycx, CategoricalIndexType(flqxn__fykh, dypu__ognl)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        vynl__ycx, dypu__ognl = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return vynl__ycx, RangeIndexType(dypu__ognl)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        vynl__ycx, dypu__ognl = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return vynl__ycx, StringIndexType(dypu__ognl)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        vynl__ycx, dypu__ognl = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return vynl__ycx, BinaryIndexType(dypu__ognl)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        vynl__ycx, dypu__ognl = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return vynl__ycx, TimedeltaIndexType(dypu__ognl)
    else:
        raise_bodo_error(
            f'Unexpected Internal Error while converting typing metadata: unable to infer dtype for type enum {typ_enum_list[0]}. Please file the error here: https://github.com/Bodo-inc/Feedback'
            )


def _dtype_to_type_enum_list(typ):
    return guard(_dtype_to_type_enum_list_recursor, typ)


def _dtype_to_type_enum_list_recursor(typ, upcast_numeric_index=True):
    if typ.__hash__ and typ in _one_to_one_type_to_enum_map:
        return [_one_to_one_type_to_enum_map[typ]]
    if isinstance(typ, (dict, int, list, tuple, str, bool, bytes, float)):
        return [SeriesDtypeEnum.Literal.value, typ]
    elif typ is None:
        return [SeriesDtypeEnum.Literal.value, typ]
    elif is_overload_constant_int(typ):
        wlat__apuu = get_overload_const_int(typ)
        if numba.types.maybe_literal(wlat__apuu) == typ:
            return [SeriesDtypeEnum.LiteralType.value, wlat__apuu]
    elif is_overload_constant_str(typ):
        wlat__apuu = get_overload_const_str(typ)
        if numba.types.maybe_literal(wlat__apuu) == typ:
            return [SeriesDtypeEnum.LiteralType.value, wlat__apuu]
    elif is_overload_constant_bool(typ):
        wlat__apuu = get_overload_const_bool(typ)
        if numba.types.maybe_literal(wlat__apuu) == typ:
            return [SeriesDtypeEnum.LiteralType.value, wlat__apuu]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        vrytd__lwmlk = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for fkn__ufzd in typ.names:
            vrytd__lwmlk.append(fkn__ufzd)
        for vqx__reffk in typ.data:
            vrytd__lwmlk += _dtype_to_type_enum_list_recursor(vqx__reffk)
        return vrytd__lwmlk
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        han__sbrj = _dtype_to_type_enum_list_recursor(typ.categories)
        jyc__tkk = _dtype_to_type_enum_list_recursor(typ.elem_type)
        udz__unrud = _dtype_to_type_enum_list_recursor(typ.ordered)
        koriu__dnxw = _dtype_to_type_enum_list_recursor(typ.data)
        ukvds__pym = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + han__sbrj + jyc__tkk + udz__unrud + koriu__dnxw + ukvds__pym
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                epkl__obx = types.float64
                pfyv__kbsem = types.Array(epkl__obx, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                epkl__obx = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    pfyv__kbsem = IntegerArrayType(epkl__obx)
                else:
                    pfyv__kbsem = types.Array(epkl__obx, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                epkl__obx = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    pfyv__kbsem = IntegerArrayType(epkl__obx)
                else:
                    pfyv__kbsem = types.Array(epkl__obx, 1, 'C')
            elif typ.dtype == types.bool_:
                epkl__obx = typ.dtype
                pfyv__kbsem = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(epkl__obx
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(pfyv__kbsem)
        else:
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(typ.dtype
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(typ.data)
    elif isinstance(typ, PeriodIndexType):
        return [SeriesDtypeEnum.PeriodIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.freq
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, CategoricalIndexType):
        return [SeriesDtypeEnum.CategoricalIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.data
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, RangeIndexType):
        return [SeriesDtypeEnum.RangeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, StringIndexType):
        return [SeriesDtypeEnum.StringIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, BinaryIndexType):
        return [SeriesDtypeEnum.BinaryIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, TimedeltaIndexType):
        return [SeriesDtypeEnum.TimedeltaIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    else:
        raise GuardException('Unable to convert type')


def _infer_series_dtype(S, array_metadata=None):
    if S.dtype == np.dtype('O'):
        if len(S.values) == 0 or S.isna().sum() == len(S):
            if array_metadata != None:
                return _dtype_from_type_enum_list(array_metadata).dtype
            elif hasattr(S, '_bodo_meta'
                ) and S._bodo_meta is not None and 'type_metadata' in S._bodo_meta and S._bodo_meta[
                'type_metadata'][1] is not None:
                aqvf__niw = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(aqvf__niw)
        return numba.typeof(S.values).dtype
    if isinstance(S.dtype, pd.core.arrays.floating.FloatingDtype):
        raise BodoError(
            """Bodo does not currently support Series constructed with Pandas FloatingArray.
Please use Series.astype() to convert any input Series input to Bodo JIT functions."""
            )
    if isinstance(S.dtype, pd.core.arrays.integer._IntegerDtype):
        return typeof_pd_int_dtype(S.dtype, None)
    elif isinstance(S.dtype, pd.CategoricalDtype):
        return bodo.typeof(S.dtype)
    elif isinstance(S.dtype, pd.StringDtype):
        return string_type
    elif isinstance(S.dtype, pd.BooleanDtype):
        return types.bool_
    if isinstance(S.dtype, pd.DatetimeTZDtype):
        apd__vcxi = S.dtype.unit
        if apd__vcxi != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        hpdhi__ienqn = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(hpdhi__ienqn)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    mjxz__iep = cgutils.is_not_null(builder, parent_obj)
    gzfew__ajgww = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(mjxz__iep):
        jiv__many = pyapi.object_getattr_string(parent_obj, 'columns')
        ydc__fsyv = pyapi.call_method(jiv__many, '__len__', ())
        builder.store(pyapi.long_as_longlong(ydc__fsyv), gzfew__ajgww)
        pyapi.decref(ydc__fsyv)
        pyapi.decref(jiv__many)
    use_parent_obj = builder.and_(mjxz__iep, builder.icmp_unsigned('==',
        builder.load(gzfew__ajgww), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        enr__wjmql = df_typ.runtime_colname_typ
        context.nrt.incref(builder, enr__wjmql, dataframe_payload.columns)
        return pyapi.from_native_value(enr__wjmql, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        lzs__ocko = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        lzs__ocko = np.array(df_typ.columns, 'int64')
    else:
        lzs__ocko = df_typ.columns
    jllgr__adywj = numba.typeof(lzs__ocko)
    pcxm__bjt = context.get_constant_generic(builder, jllgr__adywj, lzs__ocko)
    vckcs__fesmc = pyapi.from_native_value(jllgr__adywj, pcxm__bjt, c.
        env_manager)
    return vckcs__fesmc


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (bjoz__hmy, qtgg__xohwp):
        with bjoz__hmy:
            pyapi.incref(obj)
            ysalk__teh = context.insert_const_string(c.builder.module, 'numpy')
            ilou__malil = pyapi.import_module_noblock(ysalk__teh)
            if df_typ.has_runtime_cols:
                trqbv__tscga = 0
            else:
                trqbv__tscga = len(df_typ.columns)
            ydd__pak = pyapi.long_from_longlong(lir.Constant(lir.IntType(64
                ), trqbv__tscga))
            hkkg__ldxoq = pyapi.call_method(ilou__malil, 'arange', (ydd__pak,))
            pyapi.object_setattr_string(obj, 'columns', hkkg__ldxoq)
            pyapi.decref(ilou__malil)
            pyapi.decref(hkkg__ldxoq)
            pyapi.decref(ydd__pak)
        with qtgg__xohwp:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            essqw__ewr = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            ysalk__teh = context.insert_const_string(c.builder.module, 'pandas'
                )
            ilou__malil = pyapi.import_module_noblock(ysalk__teh)
            df_obj = pyapi.call_method(ilou__malil, 'DataFrame', (pyapi.
                borrow_none(), essqw__ewr))
            pyapi.decref(ilou__malil)
            pyapi.decref(essqw__ewr)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    rpxtx__snbvj = cgutils.create_struct_proxy(typ)(context, builder, value=val
        )
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = rpxtx__snbvj.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        magg__gsi = typ.table_type
        zkr__dpnz = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, magg__gsi, zkr__dpnz)
        tbjk__suo = box_table(magg__gsi, zkr__dpnz, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (vakp__kqmtz, qwejp__drrwe):
            with vakp__kqmtz:
                cwvc__ssqmm = pyapi.object_getattr_string(tbjk__suo, 'arrays')
                bxap__rlvqp = c.pyapi.make_none()
                if n_cols is None:
                    ydc__fsyv = pyapi.call_method(cwvc__ssqmm, '__len__', ())
                    fap__ykdi = pyapi.long_as_longlong(ydc__fsyv)
                    pyapi.decref(ydc__fsyv)
                else:
                    fap__ykdi = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, fap__ykdi) as wifmj__bxld:
                    i = wifmj__bxld.index
                    cfxix__xjp = pyapi.list_getitem(cwvc__ssqmm, i)
                    pllp__wkscb = c.builder.icmp_unsigned('!=', cfxix__xjp,
                        bxap__rlvqp)
                    with builder.if_then(pllp__wkscb):
                        slhr__tdu = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, slhr__tdu, cfxix__xjp)
                        pyapi.decref(slhr__tdu)
                pyapi.decref(cwvc__ssqmm)
                pyapi.decref(bxap__rlvqp)
            with qwejp__drrwe:
                df_obj = builder.load(res)
                essqw__ewr = pyapi.object_getattr_string(df_obj, 'index')
                fdpfh__thbe = c.pyapi.call_method(tbjk__suo, 'to_pandas', (
                    essqw__ewr,))
                builder.store(fdpfh__thbe, res)
                pyapi.decref(df_obj)
                pyapi.decref(essqw__ewr)
        pyapi.decref(tbjk__suo)
    else:
        qbj__pfik = [builder.extract_value(dataframe_payload.data, i) for i in
            range(n_cols)]
        cuzea__ghr = typ.data
        for i, wvd__bkrxq, mqvh__nwok in zip(range(n_cols), qbj__pfik,
            cuzea__ghr):
            eol__wbgl = cgutils.alloca_once_value(builder, wvd__bkrxq)
            fqkga__vlarc = cgutils.alloca_once_value(builder, context.
                get_constant_null(mqvh__nwok))
            pllp__wkscb = builder.not_(is_ll_eq(builder, eol__wbgl,
                fqkga__vlarc))
            tkyl__jiod = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, pllp__wkscb))
            with builder.if_then(tkyl__jiod):
                slhr__tdu = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, mqvh__nwok, wvd__bkrxq)
                arr_obj = pyapi.from_native_value(mqvh__nwok, wvd__bkrxq, c
                    .env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, slhr__tdu, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(slhr__tdu)
    df_obj = builder.load(res)
    vckcs__fesmc = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', vckcs__fesmc)
    pyapi.decref(vckcs__fesmc)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    bxap__rlvqp = pyapi.borrow_none()
    oih__bxdgq = pyapi.unserialize(pyapi.serialize_object(slice))
    yhfmv__nhzbi = pyapi.call_function_objargs(oih__bxdgq, [bxap__rlvqp])
    kdsg__del = pyapi.long_from_longlong(col_ind)
    hjhb__yoemx = pyapi.tuple_pack([yhfmv__nhzbi, kdsg__del])
    bxdy__qrg = pyapi.object_getattr_string(df_obj, 'iloc')
    gebv__aeewj = pyapi.object_getitem(bxdy__qrg, hjhb__yoemx)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        qep__pnv = pyapi.object_getattr_string(gebv__aeewj, 'array')
    else:
        qep__pnv = pyapi.object_getattr_string(gebv__aeewj, 'values')
    if isinstance(data_typ, types.Array):
        durri__ugaj = context.insert_const_string(builder.module, 'numpy')
        ern__epax = pyapi.import_module_noblock(durri__ugaj)
        arr_obj = pyapi.call_method(ern__epax, 'ascontiguousarray', (qep__pnv,)
            )
        pyapi.decref(qep__pnv)
        pyapi.decref(ern__epax)
    else:
        arr_obj = qep__pnv
    pyapi.decref(oih__bxdgq)
    pyapi.decref(yhfmv__nhzbi)
    pyapi.decref(kdsg__del)
    pyapi.decref(hjhb__yoemx)
    pyapi.decref(bxdy__qrg)
    pyapi.decref(gebv__aeewj)
    return arr_obj


@intrinsic
def unbox_dataframe_column(typingctx, df, i=None):
    assert isinstance(df, DataFrameType) and is_overload_constant_int(i)

    def codegen(context, builder, sig, args):
        pyapi = context.get_python_api(builder)
        c = numba.core.pythonapi._UnboxContext(context, builder, pyapi)
        df_typ = sig.args[0]
        col_ind = get_overload_const_int(sig.args[1])
        data_typ = df_typ.data[col_ind]
        rpxtx__snbvj = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            rpxtx__snbvj.parent, args[1], data_typ)
        jehc__rcks = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            zkr__dpnz = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            sdhm__drkuy = df_typ.table_type.type_to_blk[data_typ]
            rsc__euno = getattr(zkr__dpnz, f'block_{sdhm__drkuy}')
            pffo__wnqq = ListInstance(c.context, c.builder, types.List(
                data_typ), rsc__euno)
            gvs__fmchy = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            pffo__wnqq.inititem(gvs__fmchy, jehc__rcks.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, jehc__rcks.value, col_ind)
        ghsq__izdm = DataFramePayloadType(df_typ)
        xhj__fmazh = context.nrt.meminfo_data(builder, rpxtx__snbvj.meminfo)
        mpf__qnli = context.get_value_type(ghsq__izdm).as_pointer()
        xhj__fmazh = builder.bitcast(xhj__fmazh, mpf__qnli)
        builder.store(dataframe_payload._getvalue(), xhj__fmazh)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        qep__pnv = c.pyapi.object_getattr_string(val, 'array')
    else:
        qep__pnv = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        durri__ugaj = c.context.insert_const_string(c.builder.module, 'numpy')
        ern__epax = c.pyapi.import_module_noblock(durri__ugaj)
        arr_obj = c.pyapi.call_method(ern__epax, 'ascontiguousarray', (
            qep__pnv,))
        c.pyapi.decref(qep__pnv)
        c.pyapi.decref(ern__epax)
    else:
        arr_obj = qep__pnv
    aabzu__nqvs = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    essqw__ewr = c.pyapi.object_getattr_string(val, 'index')
    maoue__lhb = c.pyapi.to_native_value(typ.index, essqw__ewr).value
    mlxz__lan = c.pyapi.object_getattr_string(val, 'name')
    awwo__zwha = c.pyapi.to_native_value(typ.name_typ, mlxz__lan).value
    ntnt__zqxj = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, aabzu__nqvs, maoue__lhb, awwo__zwha)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(essqw__ewr)
    c.pyapi.decref(mlxz__lan)
    return NativeValue(ntnt__zqxj)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        wbgir__ccht = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(wbgir__ccht._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    ysalk__teh = c.context.insert_const_string(c.builder.module, 'pandas')
    jpvgv__sdj = c.pyapi.import_module_noblock(ysalk__teh)
    oqul__wqn = bodo.hiframes.pd_series_ext.get_series_payload(c.context, c
        .builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, oqul__wqn.data)
    c.context.nrt.incref(c.builder, typ.index, oqul__wqn.index)
    c.context.nrt.incref(c.builder, typ.name_typ, oqul__wqn.name)
    arr_obj = c.pyapi.from_native_value(typ.data, oqul__wqn.data, c.env_manager
        )
    essqw__ewr = c.pyapi.from_native_value(typ.index, oqul__wqn.index, c.
        env_manager)
    mlxz__lan = c.pyapi.from_native_value(typ.name_typ, oqul__wqn.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(jpvgv__sdj, 'Series', (arr_obj, essqw__ewr,
        dtype, mlxz__lan))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(essqw__ewr)
    c.pyapi.decref(mlxz__lan)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(jpvgv__sdj)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    oodv__vje = []
    for pfhc__bgj in typ_list:
        if isinstance(pfhc__bgj, int) and not isinstance(pfhc__bgj, bool):
            nak__jahq = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), pfhc__bgj))
        else:
            rjb__huz = numba.typeof(pfhc__bgj)
            pcu__rttaa = context.get_constant_generic(builder, rjb__huz,
                pfhc__bgj)
            nak__jahq = pyapi.from_native_value(rjb__huz, pcu__rttaa,
                env_manager)
        oodv__vje.append(nak__jahq)
    xdsef__geqd = pyapi.list_pack(oodv__vje)
    for val in oodv__vje:
        pyapi.decref(val)
    return xdsef__geqd


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    xsmjv__schqp = not typ.has_runtime_cols
    xyd__dtvyj = 2 if xsmjv__schqp else 1
    pqnxo__xfbt = pyapi.dict_new(xyd__dtvyj)
    zwi__wkrpw = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    pyapi.dict_setitem_string(pqnxo__xfbt, 'dist', zwi__wkrpw)
    pyapi.decref(zwi__wkrpw)
    if xsmjv__schqp:
        hpnvk__wyvlj = _dtype_to_type_enum_list(typ.index)
        if hpnvk__wyvlj != None:
            dgc__bdc = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, hpnvk__wyvlj)
        else:
            dgc__bdc = pyapi.make_none()
        if typ.is_table_format:
            trptj__hbq = typ.table_type
            nzoa__vaoba = pyapi.list_new(lir.Constant(lir.IntType(64), len(
                typ.data)))
            for sdhm__drkuy, dtype in trptj__hbq.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                fap__ykdi = c.context.get_constant(types.int64, len(
                    trptj__hbq.block_to_arr_ind[sdhm__drkuy]))
                prc__ftns = c.context.make_constant_array(c.builder, types.
                    Array(types.int64, 1, 'C'), np.array(trptj__hbq.
                    block_to_arr_ind[sdhm__drkuy], dtype=np.int64))
                tgvx__jbr = c.context.make_array(types.Array(types.int64, 1,
                    'C'))(c.context, c.builder, prc__ftns)
                with cgutils.for_range(c.builder, fap__ykdi) as wifmj__bxld:
                    i = wifmj__bxld.index
                    lzczs__qsa = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), tgvx__jbr, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(nzoa__vaoba, lzczs__qsa, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            ssbtc__iuzfe = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    xdsef__geqd = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    xdsef__geqd = pyapi.make_none()
                ssbtc__iuzfe.append(xdsef__geqd)
            nzoa__vaoba = pyapi.list_pack(ssbtc__iuzfe)
            for val in ssbtc__iuzfe:
                pyapi.decref(val)
        vgot__rcaoo = pyapi.list_pack([dgc__bdc, nzoa__vaoba])
        pyapi.dict_setitem_string(pqnxo__xfbt, 'type_metadata', vgot__rcaoo)
    pyapi.object_setattr_string(obj, '_bodo_meta', pqnxo__xfbt)
    pyapi.decref(pqnxo__xfbt)


def get_series_dtype_handle_null_int_and_hetrogenous(series_typ):
    if isinstance(series_typ, HeterogeneousSeriesType):
        return None
    if isinstance(series_typ.dtype, types.Number) and isinstance(series_typ
        .data, IntegerArrayType):
        return IntDtype(series_typ.dtype)
    return series_typ.dtype


def _set_bodo_meta_series(obj, c, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    pqnxo__xfbt = pyapi.dict_new(2)
    zwi__wkrpw = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    hpnvk__wyvlj = _dtype_to_type_enum_list(typ.index)
    if hpnvk__wyvlj != None:
        dgc__bdc = type_enum_list_to_py_list_obj(pyapi, context, builder, c
            .env_manager, hpnvk__wyvlj)
    else:
        dgc__bdc = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            ymkt__qwdn = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            ymkt__qwdn = pyapi.make_none()
    else:
        ymkt__qwdn = pyapi.make_none()
    bylsw__sxk = pyapi.list_pack([dgc__bdc, ymkt__qwdn])
    pyapi.dict_setitem_string(pqnxo__xfbt, 'type_metadata', bylsw__sxk)
    pyapi.decref(bylsw__sxk)
    pyapi.dict_setitem_string(pqnxo__xfbt, 'dist', zwi__wkrpw)
    pyapi.object_setattr_string(obj, '_bodo_meta', pqnxo__xfbt)
    pyapi.decref(pqnxo__xfbt)
    pyapi.decref(zwi__wkrpw)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as hck__kfyfv:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    iza__yhhmm = numba.np.numpy_support.map_layout(val)
    mcik__womj = not val.flags.writeable
    return types.Array(dtype, val.ndim, iza__yhhmm, readonly=mcik__womj)


def _infer_ndarray_obj_dtype(val):
    if not val.dtype == np.dtype('O'):
        raise BodoError('Unsupported array dtype: {}'.format(val.dtype))
    i = 0
    while i < len(val) and (pd.api.types.is_scalar(val[i]) and pd.isna(val[
        i]) or not pd.api.types.is_scalar(val[i]) and len(val[i]) == 0):
        i += 1
    if i == len(val):
        warnings.warn(BodoWarning(
            'Empty object array passed to Bodo, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    qmp__trcxz = val[i]
    if isinstance(qmp__trcxz, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(qmp__trcxz, bytes):
        return binary_array_type
    elif isinstance(qmp__trcxz, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(qmp__trcxz, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(qmp__trcxz))
    elif isinstance(qmp__trcxz, (dict, Dict)) and all(isinstance(
        btzcl__dwenx, str) for btzcl__dwenx in qmp__trcxz.keys()):
        revpq__uzvb = tuple(qmp__trcxz.keys())
        iue__pjxcw = tuple(_get_struct_value_arr_type(v) for v in
            qmp__trcxz.values())
        return StructArrayType(iue__pjxcw, revpq__uzvb)
    elif isinstance(qmp__trcxz, (dict, Dict)):
        utjuh__uhhz = numba.typeof(_value_to_array(list(qmp__trcxz.keys())))
        geic__ibq = numba.typeof(_value_to_array(list(qmp__trcxz.values())))
        utjuh__uhhz = to_str_arr_if_dict_array(utjuh__uhhz)
        geic__ibq = to_str_arr_if_dict_array(geic__ibq)
        return MapArrayType(utjuh__uhhz, geic__ibq)
    elif isinstance(qmp__trcxz, tuple):
        iue__pjxcw = tuple(_get_struct_value_arr_type(v) for v in qmp__trcxz)
        return TupleArrayType(iue__pjxcw)
    if isinstance(qmp__trcxz, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(qmp__trcxz, list):
            qmp__trcxz = _value_to_array(qmp__trcxz)
        sfzk__wwve = numba.typeof(qmp__trcxz)
        sfzk__wwve = to_str_arr_if_dict_array(sfzk__wwve)
        return ArrayItemArrayType(sfzk__wwve)
    if isinstance(qmp__trcxz, datetime.date):
        return datetime_date_array_type
    if isinstance(qmp__trcxz, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(qmp__trcxz, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(qmp__trcxz, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {qmp__trcxz}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    ltg__eosur = val.copy()
    ltg__eosur.append(None)
    wvd__bkrxq = np.array(ltg__eosur, np.object_)
    if len(val) and isinstance(val[0], float):
        wvd__bkrxq = np.array(val, np.float64)
    return wvd__bkrxq


def _get_struct_value_arr_type(v):
    if isinstance(v, (dict, Dict)):
        return numba.typeof(_value_to_array(v))
    if isinstance(v, list):
        return dtype_to_array_type(numba.typeof(_value_to_array(v)))
    if pd.api.types.is_scalar(v) and pd.isna(v):
        warnings.warn(BodoWarning(
            'Field value in struct array is NA, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    mqvh__nwok = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        mqvh__nwok = to_nullable_type(mqvh__nwok)
    return mqvh__nwok
