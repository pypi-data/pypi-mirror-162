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
    sgxk__qfgrj = tuple(val.columns.to_list())
    iood__rnkzh = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        tnzr__uumoi = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        tnzr__uumoi = numba.typeof(val.index)
    tctf__bmzy = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    vgobb__waoh = len(iood__rnkzh) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(iood__rnkzh, tnzr__uumoi, sgxk__qfgrj, tctf__bmzy,
        is_table_format=vgobb__waoh)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    tctf__bmzy = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        mtdu__tdzdq = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        mtdu__tdzdq = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    crrw__kmf = dtype_to_array_type(dtype)
    if _use_dict_str_type and crrw__kmf == string_array_type:
        crrw__kmf = bodo.dict_str_arr_type
    return SeriesType(dtype, data=crrw__kmf, index=mtdu__tdzdq, name_typ=
        numba.typeof(val.name), dist=tctf__bmzy)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    kxqbg__kjrxd = c.pyapi.object_getattr_string(val, 'index')
    fxc__qumdr = c.pyapi.to_native_value(typ.index, kxqbg__kjrxd).value
    c.pyapi.decref(kxqbg__kjrxd)
    if typ.is_table_format:
        kucwy__ydfdl = cgutils.create_struct_proxy(typ.table_type)(c.
            context, c.builder)
        kucwy__ydfdl.parent = val
        for ica__usoqy, ggdq__hduhk in typ.table_type.type_to_blk.items():
            eqoz__pdyul = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[ggdq__hduhk]))
            xfabv__jdg, uot__ire = ListInstance.allocate_ex(c.context, c.
                builder, types.List(ica__usoqy), eqoz__pdyul)
            uot__ire.size = eqoz__pdyul
            setattr(kucwy__ydfdl, f'block_{ggdq__hduhk}', uot__ire.value)
        pnt__wsnzw = c.pyapi.call_method(val, '__len__', ())
        pbt__icfsu = c.pyapi.long_as_longlong(pnt__wsnzw)
        c.pyapi.decref(pnt__wsnzw)
        kucwy__ydfdl.len = pbt__icfsu
        ezi__kpoqh = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [kucwy__ydfdl._getvalue()])
    else:
        ssh__voa = [c.context.get_constant_null(ica__usoqy) for ica__usoqy in
            typ.data]
        ezi__kpoqh = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            ssh__voa)
    efmyb__dcg = construct_dataframe(c.context, c.builder, typ, ezi__kpoqh,
        fxc__qumdr, val, None)
    return NativeValue(efmyb__dcg)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        ipmf__falu = df._bodo_meta['type_metadata'][1]
    else:
        ipmf__falu = [None] * len(df.columns)
    ekgub__mjgr = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=ipmf__falu[i])) for i in range(len(df.columns))]
    ekgub__mjgr = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        ica__usoqy == string_array_type else ica__usoqy) for ica__usoqy in
        ekgub__mjgr]
    return tuple(ekgub__mjgr)


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
    xze__sordz, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(xze__sordz) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {xze__sordz}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        vgkc__tedz, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return vgkc__tedz, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        vgkc__tedz, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return vgkc__tedz, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        yfuar__yqyke = typ_enum_list[1]
        bees__pkfc = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(yfuar__yqyke, bees__pkfc)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        yzzgn__aiqux = typ_enum_list[1]
        mrwqr__pcpb = tuple(typ_enum_list[2:2 + yzzgn__aiqux])
        ibj__qlwip = typ_enum_list[2 + yzzgn__aiqux:]
        yveg__rbrxz = []
        for i in range(yzzgn__aiqux):
            ibj__qlwip, qam__her = _dtype_from_type_enum_list_recursor(
                ibj__qlwip)
            yveg__rbrxz.append(qam__her)
        return ibj__qlwip, StructType(tuple(yveg__rbrxz), mrwqr__pcpb)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        yfnum__ueh = typ_enum_list[1]
        ibj__qlwip = typ_enum_list[2:]
        return ibj__qlwip, yfnum__ueh
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        yfnum__ueh = typ_enum_list[1]
        ibj__qlwip = typ_enum_list[2:]
        return ibj__qlwip, numba.types.literal(yfnum__ueh)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        ibj__qlwip, lpny__nyot = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        ibj__qlwip, iiw__uiknd = _dtype_from_type_enum_list_recursor(ibj__qlwip
            )
        ibj__qlwip, odlr__xasf = _dtype_from_type_enum_list_recursor(ibj__qlwip
            )
        ibj__qlwip, bzv__efn = _dtype_from_type_enum_list_recursor(ibj__qlwip)
        ibj__qlwip, kml__ivaq = _dtype_from_type_enum_list_recursor(ibj__qlwip)
        return ibj__qlwip, PDCategoricalDtype(lpny__nyot, iiw__uiknd,
            odlr__xasf, bzv__efn, kml__ivaq)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        ibj__qlwip, dpb__ucy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ibj__qlwip, DatetimeIndexType(dpb__ucy)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        ibj__qlwip, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        ibj__qlwip, dpb__ucy = _dtype_from_type_enum_list_recursor(ibj__qlwip)
        ibj__qlwip, bzv__efn = _dtype_from_type_enum_list_recursor(ibj__qlwip)
        return ibj__qlwip, NumericIndexType(dtype, dpb__ucy, bzv__efn)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        ibj__qlwip, nkj__cbbs = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        ibj__qlwip, dpb__ucy = _dtype_from_type_enum_list_recursor(ibj__qlwip)
        return ibj__qlwip, PeriodIndexType(nkj__cbbs, dpb__ucy)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        ibj__qlwip, bzv__efn = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        ibj__qlwip, dpb__ucy = _dtype_from_type_enum_list_recursor(ibj__qlwip)
        return ibj__qlwip, CategoricalIndexType(bzv__efn, dpb__ucy)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        ibj__qlwip, dpb__ucy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ibj__qlwip, RangeIndexType(dpb__ucy)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        ibj__qlwip, dpb__ucy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ibj__qlwip, StringIndexType(dpb__ucy)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        ibj__qlwip, dpb__ucy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ibj__qlwip, BinaryIndexType(dpb__ucy)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        ibj__qlwip, dpb__ucy = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return ibj__qlwip, TimedeltaIndexType(dpb__ucy)
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
        yuhm__jkb = get_overload_const_int(typ)
        if numba.types.maybe_literal(yuhm__jkb) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yuhm__jkb]
    elif is_overload_constant_str(typ):
        yuhm__jkb = get_overload_const_str(typ)
        if numba.types.maybe_literal(yuhm__jkb) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yuhm__jkb]
    elif is_overload_constant_bool(typ):
        yuhm__jkb = get_overload_const_bool(typ)
        if numba.types.maybe_literal(yuhm__jkb) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yuhm__jkb]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        xntwq__eppzr = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for dpq__ibmm in typ.names:
            xntwq__eppzr.append(dpq__ibmm)
        for clas__qajs in typ.data:
            xntwq__eppzr += _dtype_to_type_enum_list_recursor(clas__qajs)
        return xntwq__eppzr
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        nmhp__ucxw = _dtype_to_type_enum_list_recursor(typ.categories)
        oxkky__gpmam = _dtype_to_type_enum_list_recursor(typ.elem_type)
        kkiv__jwqr = _dtype_to_type_enum_list_recursor(typ.ordered)
        ejyhl__qvm = _dtype_to_type_enum_list_recursor(typ.data)
        ssnj__rje = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + nmhp__ucxw + oxkky__gpmam + kkiv__jwqr + ejyhl__qvm + ssnj__rje
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                uur__yqz = types.float64
                tzn__hiq = types.Array(uur__yqz, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                uur__yqz = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    tzn__hiq = IntegerArrayType(uur__yqz)
                else:
                    tzn__hiq = types.Array(uur__yqz, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                uur__yqz = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    tzn__hiq = IntegerArrayType(uur__yqz)
                else:
                    tzn__hiq = types.Array(uur__yqz, 1, 'C')
            elif typ.dtype == types.bool_:
                uur__yqz = typ.dtype
                tzn__hiq = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(uur__yqz
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(tzn__hiq)
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
                awmm__ldkd = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(awmm__ldkd)
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
        oommo__iec = S.dtype.unit
        if oommo__iec != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        ppfv__fep = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.dtype.tz
            )
        return PandasDatetimeTZDtype(ppfv__fep)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    iwi__nusef = cgutils.is_not_null(builder, parent_obj)
    gnc__epb = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(iwi__nusef):
        hdo__pmx = pyapi.object_getattr_string(parent_obj, 'columns')
        pnt__wsnzw = pyapi.call_method(hdo__pmx, '__len__', ())
        builder.store(pyapi.long_as_longlong(pnt__wsnzw), gnc__epb)
        pyapi.decref(pnt__wsnzw)
        pyapi.decref(hdo__pmx)
    use_parent_obj = builder.and_(iwi__nusef, builder.icmp_unsigned('==',
        builder.load(gnc__epb), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        lhui__ijky = df_typ.runtime_colname_typ
        context.nrt.incref(builder, lhui__ijky, dataframe_payload.columns)
        return pyapi.from_native_value(lhui__ijky, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        gidn__xspxv = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        gidn__xspxv = np.array(df_typ.columns, 'int64')
    else:
        gidn__xspxv = df_typ.columns
    qctu__olkg = numba.typeof(gidn__xspxv)
    pwwcr__mxltc = context.get_constant_generic(builder, qctu__olkg,
        gidn__xspxv)
    obn__cvury = pyapi.from_native_value(qctu__olkg, pwwcr__mxltc, c.
        env_manager)
    return obn__cvury


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (xoh__pzdz, wxvte__krsvx):
        with xoh__pzdz:
            pyapi.incref(obj)
            pyt__acla = context.insert_const_string(c.builder.module, 'numpy')
            dxf__hdlfs = pyapi.import_module_noblock(pyt__acla)
            if df_typ.has_runtime_cols:
                vwof__ikq = 0
            else:
                vwof__ikq = len(df_typ.columns)
            udr__acuu = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), vwof__ikq))
            hlfny__lzd = pyapi.call_method(dxf__hdlfs, 'arange', (udr__acuu,))
            pyapi.object_setattr_string(obj, 'columns', hlfny__lzd)
            pyapi.decref(dxf__hdlfs)
            pyapi.decref(hlfny__lzd)
            pyapi.decref(udr__acuu)
        with wxvte__krsvx:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            eqofc__wmkke = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            pyt__acla = context.insert_const_string(c.builder.module, 'pandas')
            dxf__hdlfs = pyapi.import_module_noblock(pyt__acla)
            df_obj = pyapi.call_method(dxf__hdlfs, 'DataFrame', (pyapi.
                borrow_none(), eqofc__wmkke))
            pyapi.decref(dxf__hdlfs)
            pyapi.decref(eqofc__wmkke)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    vdi__sttue = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = vdi__sttue.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        dxy__ahy = typ.table_type
        kucwy__ydfdl = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, dxy__ahy, kucwy__ydfdl)
        ubai__nrpip = box_table(dxy__ahy, kucwy__ydfdl, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (ryie__lnc, nodz__jrw):
            with ryie__lnc:
                xts__yxez = pyapi.object_getattr_string(ubai__nrpip, 'arrays')
                guwmv__sjo = c.pyapi.make_none()
                if n_cols is None:
                    pnt__wsnzw = pyapi.call_method(xts__yxez, '__len__', ())
                    eqoz__pdyul = pyapi.long_as_longlong(pnt__wsnzw)
                    pyapi.decref(pnt__wsnzw)
                else:
                    eqoz__pdyul = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, eqoz__pdyul) as fzxed__fqd:
                    i = fzxed__fqd.index
                    rruux__lcpw = pyapi.list_getitem(xts__yxez, i)
                    wnol__fejs = c.builder.icmp_unsigned('!=', rruux__lcpw,
                        guwmv__sjo)
                    with builder.if_then(wnol__fejs):
                        rbhon__uvmq = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, rbhon__uvmq, rruux__lcpw)
                        pyapi.decref(rbhon__uvmq)
                pyapi.decref(xts__yxez)
                pyapi.decref(guwmv__sjo)
            with nodz__jrw:
                df_obj = builder.load(res)
                eqofc__wmkke = pyapi.object_getattr_string(df_obj, 'index')
                webuo__miy = c.pyapi.call_method(ubai__nrpip, 'to_pandas',
                    (eqofc__wmkke,))
                builder.store(webuo__miy, res)
                pyapi.decref(df_obj)
                pyapi.decref(eqofc__wmkke)
        pyapi.decref(ubai__nrpip)
    else:
        oet__jfvbr = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        fiyxb__qxqwj = typ.data
        for i, xwvmf__fjwp, crrw__kmf in zip(range(n_cols), oet__jfvbr,
            fiyxb__qxqwj):
            zxopr__qok = cgutils.alloca_once_value(builder, xwvmf__fjwp)
            pmyww__xsxr = cgutils.alloca_once_value(builder, context.
                get_constant_null(crrw__kmf))
            wnol__fejs = builder.not_(is_ll_eq(builder, zxopr__qok,
                pmyww__xsxr))
            dhldp__lmcb = builder.or_(builder.not_(use_parent_obj), builder
                .and_(use_parent_obj, wnol__fejs))
            with builder.if_then(dhldp__lmcb):
                rbhon__uvmq = pyapi.long_from_longlong(context.get_constant
                    (types.int64, i))
                context.nrt.incref(builder, crrw__kmf, xwvmf__fjwp)
                arr_obj = pyapi.from_native_value(crrw__kmf, xwvmf__fjwp, c
                    .env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, rbhon__uvmq, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(rbhon__uvmq)
    df_obj = builder.load(res)
    obn__cvury = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', obn__cvury)
    pyapi.decref(obn__cvury)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    guwmv__sjo = pyapi.borrow_none()
    qljh__wgqo = pyapi.unserialize(pyapi.serialize_object(slice))
    uxi__ejs = pyapi.call_function_objargs(qljh__wgqo, [guwmv__sjo])
    wdwz__ezu = pyapi.long_from_longlong(col_ind)
    mgkie__mavyq = pyapi.tuple_pack([uxi__ejs, wdwz__ezu])
    jdnec__lvhl = pyapi.object_getattr_string(df_obj, 'iloc')
    mgqd__ajw = pyapi.object_getitem(jdnec__lvhl, mgkie__mavyq)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        gmy__gxtz = pyapi.object_getattr_string(mgqd__ajw, 'array')
    else:
        gmy__gxtz = pyapi.object_getattr_string(mgqd__ajw, 'values')
    if isinstance(data_typ, types.Array):
        snwiq__hmmgi = context.insert_const_string(builder.module, 'numpy')
        fyi__mtv = pyapi.import_module_noblock(snwiq__hmmgi)
        arr_obj = pyapi.call_method(fyi__mtv, 'ascontiguousarray', (gmy__gxtz,)
            )
        pyapi.decref(gmy__gxtz)
        pyapi.decref(fyi__mtv)
    else:
        arr_obj = gmy__gxtz
    pyapi.decref(qljh__wgqo)
    pyapi.decref(uxi__ejs)
    pyapi.decref(wdwz__ezu)
    pyapi.decref(mgkie__mavyq)
    pyapi.decref(jdnec__lvhl)
    pyapi.decref(mgqd__ajw)
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
        vdi__sttue = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            vdi__sttue.parent, args[1], data_typ)
        wyoff__mpnev = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            kucwy__ydfdl = cgutils.create_struct_proxy(df_typ.table_type)(c
                .context, c.builder, builder.extract_value(
                dataframe_payload.data, 0))
            ggdq__hduhk = df_typ.table_type.type_to_blk[data_typ]
            tyzv__xjg = getattr(kucwy__ydfdl, f'block_{ggdq__hduhk}')
            lqiba__zlyvo = ListInstance(c.context, c.builder, types.List(
                data_typ), tyzv__xjg)
            mezqw__dugi = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            lqiba__zlyvo.inititem(mezqw__dugi, wyoff__mpnev.value, incref=False
                )
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, wyoff__mpnev.value, col_ind)
        znab__hajh = DataFramePayloadType(df_typ)
        nhan__atub = context.nrt.meminfo_data(builder, vdi__sttue.meminfo)
        vgi__ulmfw = context.get_value_type(znab__hajh).as_pointer()
        nhan__atub = builder.bitcast(nhan__atub, vgi__ulmfw)
        builder.store(dataframe_payload._getvalue(), nhan__atub)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        gmy__gxtz = c.pyapi.object_getattr_string(val, 'array')
    else:
        gmy__gxtz = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        snwiq__hmmgi = c.context.insert_const_string(c.builder.module, 'numpy')
        fyi__mtv = c.pyapi.import_module_noblock(snwiq__hmmgi)
        arr_obj = c.pyapi.call_method(fyi__mtv, 'ascontiguousarray', (
            gmy__gxtz,))
        c.pyapi.decref(gmy__gxtz)
        c.pyapi.decref(fyi__mtv)
    else:
        arr_obj = gmy__gxtz
    pgife__aopfx = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    eqofc__wmkke = c.pyapi.object_getattr_string(val, 'index')
    fxc__qumdr = c.pyapi.to_native_value(typ.index, eqofc__wmkke).value
    xibi__bahts = c.pyapi.object_getattr_string(val, 'name')
    srfk__yldot = c.pyapi.to_native_value(typ.name_typ, xibi__bahts).value
    fddzs__dtjzq = bodo.hiframes.pd_series_ext.construct_series(c.context,
        c.builder, typ, pgife__aopfx, fxc__qumdr, srfk__yldot)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(eqofc__wmkke)
    c.pyapi.decref(xibi__bahts)
    return NativeValue(fddzs__dtjzq)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        gcpup__pwgz = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(gcpup__pwgz._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    pyt__acla = c.context.insert_const_string(c.builder.module, 'pandas')
    tbxzb__ncnol = c.pyapi.import_module_noblock(pyt__acla)
    ebmu__jczen = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, ebmu__jczen.data)
    c.context.nrt.incref(c.builder, typ.index, ebmu__jczen.index)
    c.context.nrt.incref(c.builder, typ.name_typ, ebmu__jczen.name)
    arr_obj = c.pyapi.from_native_value(typ.data, ebmu__jczen.data, c.
        env_manager)
    eqofc__wmkke = c.pyapi.from_native_value(typ.index, ebmu__jczen.index,
        c.env_manager)
    xibi__bahts = c.pyapi.from_native_value(typ.name_typ, ebmu__jczen.name,
        c.env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(tbxzb__ncnol, 'Series', (arr_obj,
        eqofc__wmkke, dtype, xibi__bahts))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(eqofc__wmkke)
    c.pyapi.decref(xibi__bahts)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(tbxzb__ncnol)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    fohgn__hhlv = []
    for qemif__fui in typ_list:
        if isinstance(qemif__fui, int) and not isinstance(qemif__fui, bool):
            tplei__iucpp = pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), qemif__fui))
        else:
            bvjw__ezlmu = numba.typeof(qemif__fui)
            wwj__tuzdy = context.get_constant_generic(builder, bvjw__ezlmu,
                qemif__fui)
            tplei__iucpp = pyapi.from_native_value(bvjw__ezlmu, wwj__tuzdy,
                env_manager)
        fohgn__hhlv.append(tplei__iucpp)
    olhb__jefd = pyapi.list_pack(fohgn__hhlv)
    for val in fohgn__hhlv:
        pyapi.decref(val)
    return olhb__jefd


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    csg__gzgs = not typ.has_runtime_cols
    yhef__fhd = 2 if csg__gzgs else 1
    jcrfa__ojn = pyapi.dict_new(yhef__fhd)
    qmtf__zzira = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(jcrfa__ojn, 'dist', qmtf__zzira)
    pyapi.decref(qmtf__zzira)
    if csg__gzgs:
        jlr__ggbh = _dtype_to_type_enum_list(typ.index)
        if jlr__ggbh != None:
            idy__kkoo = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, jlr__ggbh)
        else:
            idy__kkoo = pyapi.make_none()
        if typ.is_table_format:
            ica__usoqy = typ.table_type
            cgbet__cbkp = pyapi.list_new(lir.Constant(lir.IntType(64), len(
                typ.data)))
            for ggdq__hduhk, dtype in ica__usoqy.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                eqoz__pdyul = c.context.get_constant(types.int64, len(
                    ica__usoqy.block_to_arr_ind[ggdq__hduhk]))
                qykfl__erp = c.context.make_constant_array(c.builder, types
                    .Array(types.int64, 1, 'C'), np.array(ica__usoqy.
                    block_to_arr_ind[ggdq__hduhk], dtype=np.int64))
                medc__dnym = c.context.make_array(types.Array(types.int64, 
                    1, 'C'))(c.context, c.builder, qykfl__erp)
                with cgutils.for_range(c.builder, eqoz__pdyul) as fzxed__fqd:
                    i = fzxed__fqd.index
                    sqj__aiz = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), medc__dnym, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(cgbet__cbkp, sqj__aiz, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            clij__oerz = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    olhb__jefd = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    olhb__jefd = pyapi.make_none()
                clij__oerz.append(olhb__jefd)
            cgbet__cbkp = pyapi.list_pack(clij__oerz)
            for val in clij__oerz:
                pyapi.decref(val)
        pbiv__wza = pyapi.list_pack([idy__kkoo, cgbet__cbkp])
        pyapi.dict_setitem_string(jcrfa__ojn, 'type_metadata', pbiv__wza)
    pyapi.object_setattr_string(obj, '_bodo_meta', jcrfa__ojn)
    pyapi.decref(jcrfa__ojn)


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
    jcrfa__ojn = pyapi.dict_new(2)
    qmtf__zzira = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    jlr__ggbh = _dtype_to_type_enum_list(typ.index)
    if jlr__ggbh != None:
        idy__kkoo = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, jlr__ggbh)
    else:
        idy__kkoo = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            iyd__gwlqs = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            iyd__gwlqs = pyapi.make_none()
    else:
        iyd__gwlqs = pyapi.make_none()
    pibn__bjad = pyapi.list_pack([idy__kkoo, iyd__gwlqs])
    pyapi.dict_setitem_string(jcrfa__ojn, 'type_metadata', pibn__bjad)
    pyapi.decref(pibn__bjad)
    pyapi.dict_setitem_string(jcrfa__ojn, 'dist', qmtf__zzira)
    pyapi.object_setattr_string(obj, '_bodo_meta', jcrfa__ojn)
    pyapi.decref(jcrfa__ojn)
    pyapi.decref(qmtf__zzira)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as fkl__icqm:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    dua__vpp = numba.np.numpy_support.map_layout(val)
    bnkmj__ysy = not val.flags.writeable
    return types.Array(dtype, val.ndim, dua__vpp, readonly=bnkmj__ysy)


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
    kpabt__webxb = val[i]
    if isinstance(kpabt__webxb, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(kpabt__webxb, bytes):
        return binary_array_type
    elif isinstance(kpabt__webxb, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(kpabt__webxb, (int, np.int8, np.int16, np.int32, np.
        int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(
            kpabt__webxb))
    elif isinstance(kpabt__webxb, (dict, Dict)) and all(isinstance(
        rxow__fmx, str) for rxow__fmx in kpabt__webxb.keys()):
        mrwqr__pcpb = tuple(kpabt__webxb.keys())
        vnpvv__xzrf = tuple(_get_struct_value_arr_type(v) for v in
            kpabt__webxb.values())
        return StructArrayType(vnpvv__xzrf, mrwqr__pcpb)
    elif isinstance(kpabt__webxb, (dict, Dict)):
        ctjyh__mlfwt = numba.typeof(_value_to_array(list(kpabt__webxb.keys())))
        qmitp__rbqa = numba.typeof(_value_to_array(list(kpabt__webxb.values()))
            )
        ctjyh__mlfwt = to_str_arr_if_dict_array(ctjyh__mlfwt)
        qmitp__rbqa = to_str_arr_if_dict_array(qmitp__rbqa)
        return MapArrayType(ctjyh__mlfwt, qmitp__rbqa)
    elif isinstance(kpabt__webxb, tuple):
        vnpvv__xzrf = tuple(_get_struct_value_arr_type(v) for v in kpabt__webxb
            )
        return TupleArrayType(vnpvv__xzrf)
    if isinstance(kpabt__webxb, (list, np.ndarray, pd.arrays.BooleanArray,
        pd.arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(kpabt__webxb, list):
            kpabt__webxb = _value_to_array(kpabt__webxb)
        zbpf__fmybn = numba.typeof(kpabt__webxb)
        zbpf__fmybn = to_str_arr_if_dict_array(zbpf__fmybn)
        return ArrayItemArrayType(zbpf__fmybn)
    if isinstance(kpabt__webxb, datetime.date):
        return datetime_date_array_type
    if isinstance(kpabt__webxb, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(kpabt__webxb, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(kpabt__webxb, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(
        f'Unsupported object array with first value: {kpabt__webxb}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    vau__mshuc = val.copy()
    vau__mshuc.append(None)
    xwvmf__fjwp = np.array(vau__mshuc, np.object_)
    if len(val) and isinstance(val[0], float):
        xwvmf__fjwp = np.array(val, np.float64)
    return xwvmf__fjwp


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
    crrw__kmf = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        crrw__kmf = to_nullable_type(crrw__kmf)
    return crrw__kmf
