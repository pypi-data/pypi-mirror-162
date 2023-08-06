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
    tgkbw__qolsi = tuple(val.columns.to_list())
    negeg__zdag = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        huaks__yfv = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        huaks__yfv = numba.typeof(val.index)
    exwu__fqruz = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    kdnqy__afuhm = len(negeg__zdag) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(negeg__zdag, huaks__yfv, tgkbw__qolsi, exwu__fqruz,
        is_table_format=kdnqy__afuhm)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    exwu__fqruz = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        xfoig__wyrp = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        xfoig__wyrp = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    xfl__sqd = dtype_to_array_type(dtype)
    if _use_dict_str_type and xfl__sqd == string_array_type:
        xfl__sqd = bodo.dict_str_arr_type
    return SeriesType(dtype, data=xfl__sqd, index=xfoig__wyrp, name_typ=
        numba.typeof(val.name), dist=exwu__fqruz)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    bsqhw__kxaf = c.pyapi.object_getattr_string(val, 'index')
    mwxbj__pxup = c.pyapi.to_native_value(typ.index, bsqhw__kxaf).value
    c.pyapi.decref(bsqhw__kxaf)
    if typ.is_table_format:
        zmez__nydo = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        zmez__nydo.parent = val
        for piqw__xlzg, qyx__etilm in typ.table_type.type_to_blk.items():
            bpex__lagnn = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[qyx__etilm]))
            fbby__lpvx, sxh__aslu = ListInstance.allocate_ex(c.context, c.
                builder, types.List(piqw__xlzg), bpex__lagnn)
            sxh__aslu.size = bpex__lagnn
            setattr(zmez__nydo, f'block_{qyx__etilm}', sxh__aslu.value)
        acgzw__lcw = c.pyapi.call_method(val, '__len__', ())
        kmmg__obpm = c.pyapi.long_as_longlong(acgzw__lcw)
        c.pyapi.decref(acgzw__lcw)
        zmez__nydo.len = kmmg__obpm
        vqcb__mxq = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [zmez__nydo._getvalue()])
    else:
        veqph__rba = [c.context.get_constant_null(piqw__xlzg) for
            piqw__xlzg in typ.data]
        vqcb__mxq = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            veqph__rba)
    zip__ulew = construct_dataframe(c.context, c.builder, typ, vqcb__mxq,
        mwxbj__pxup, val, None)
    return NativeValue(zip__ulew)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        adkg__dcpb = df._bodo_meta['type_metadata'][1]
    else:
        adkg__dcpb = [None] * len(df.columns)
    zibwj__clmti = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=adkg__dcpb[i])) for i in range(len(df.columns))]
    zibwj__clmti = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        piqw__xlzg == string_array_type else piqw__xlzg) for piqw__xlzg in
        zibwj__clmti]
    return tuple(zibwj__clmti)


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
    ozlhy__bap, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(ozlhy__bap) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {ozlhy__bap}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        ptr__nzhdr, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return ptr__nzhdr, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        ptr__nzhdr, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return ptr__nzhdr, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        sdfk__tkfk = typ_enum_list[1]
        yjdbk__fuf = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(sdfk__tkfk, yjdbk__fuf)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        prar__siy = typ_enum_list[1]
        jjw__jyag = tuple(typ_enum_list[2:2 + prar__siy])
        xrqmb__ezydx = typ_enum_list[2 + prar__siy:]
        uerti__ndnit = []
        for i in range(prar__siy):
            xrqmb__ezydx, jqhsu__mdnrw = _dtype_from_type_enum_list_recursor(
                xrqmb__ezydx)
            uerti__ndnit.append(jqhsu__mdnrw)
        return xrqmb__ezydx, StructType(tuple(uerti__ndnit), jjw__jyag)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        aclxe__gspk = typ_enum_list[1]
        xrqmb__ezydx = typ_enum_list[2:]
        return xrqmb__ezydx, aclxe__gspk
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        aclxe__gspk = typ_enum_list[1]
        xrqmb__ezydx = typ_enum_list[2:]
        return xrqmb__ezydx, numba.types.literal(aclxe__gspk)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        xrqmb__ezydx, igc__itc = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        xrqmb__ezydx, uyc__isq = _dtype_from_type_enum_list_recursor(
            xrqmb__ezydx)
        xrqmb__ezydx, poj__lry = _dtype_from_type_enum_list_recursor(
            xrqmb__ezydx)
        xrqmb__ezydx, nxu__bqdef = _dtype_from_type_enum_list_recursor(
            xrqmb__ezydx)
        xrqmb__ezydx, zqh__knj = _dtype_from_type_enum_list_recursor(
            xrqmb__ezydx)
        return xrqmb__ezydx, PDCategoricalDtype(igc__itc, uyc__isq,
            poj__lry, nxu__bqdef, zqh__knj)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        xrqmb__ezydx, hbzme__jgjf = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return xrqmb__ezydx, DatetimeIndexType(hbzme__jgjf)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        xrqmb__ezydx, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        xrqmb__ezydx, hbzme__jgjf = _dtype_from_type_enum_list_recursor(
            xrqmb__ezydx)
        xrqmb__ezydx, nxu__bqdef = _dtype_from_type_enum_list_recursor(
            xrqmb__ezydx)
        return xrqmb__ezydx, NumericIndexType(dtype, hbzme__jgjf, nxu__bqdef)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        xrqmb__ezydx, tuie__abm = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        xrqmb__ezydx, hbzme__jgjf = _dtype_from_type_enum_list_recursor(
            xrqmb__ezydx)
        return xrqmb__ezydx, PeriodIndexType(tuie__abm, hbzme__jgjf)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        xrqmb__ezydx, nxu__bqdef = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        xrqmb__ezydx, hbzme__jgjf = _dtype_from_type_enum_list_recursor(
            xrqmb__ezydx)
        return xrqmb__ezydx, CategoricalIndexType(nxu__bqdef, hbzme__jgjf)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        xrqmb__ezydx, hbzme__jgjf = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return xrqmb__ezydx, RangeIndexType(hbzme__jgjf)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        xrqmb__ezydx, hbzme__jgjf = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return xrqmb__ezydx, StringIndexType(hbzme__jgjf)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        xrqmb__ezydx, hbzme__jgjf = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return xrqmb__ezydx, BinaryIndexType(hbzme__jgjf)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        xrqmb__ezydx, hbzme__jgjf = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return xrqmb__ezydx, TimedeltaIndexType(hbzme__jgjf)
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
        cathv__xxlv = get_overload_const_int(typ)
        if numba.types.maybe_literal(cathv__xxlv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, cathv__xxlv]
    elif is_overload_constant_str(typ):
        cathv__xxlv = get_overload_const_str(typ)
        if numba.types.maybe_literal(cathv__xxlv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, cathv__xxlv]
    elif is_overload_constant_bool(typ):
        cathv__xxlv = get_overload_const_bool(typ)
        if numba.types.maybe_literal(cathv__xxlv) == typ:
            return [SeriesDtypeEnum.LiteralType.value, cathv__xxlv]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        fkute__ugf = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for ledeq__jckk in typ.names:
            fkute__ugf.append(ledeq__jckk)
        for iax__qnw in typ.data:
            fkute__ugf += _dtype_to_type_enum_list_recursor(iax__qnw)
        return fkute__ugf
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        lvbq__yorm = _dtype_to_type_enum_list_recursor(typ.categories)
        gwg__yufvw = _dtype_to_type_enum_list_recursor(typ.elem_type)
        abl__mxfjs = _dtype_to_type_enum_list_recursor(typ.ordered)
        mhqbv__tojrx = _dtype_to_type_enum_list_recursor(typ.data)
        qsr__ztqt = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + lvbq__yorm + gwg__yufvw + abl__mxfjs + mhqbv__tojrx + qsr__ztqt
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                mdzj__zkcv = types.float64
                num__dkeg = types.Array(mdzj__zkcv, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                mdzj__zkcv = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    num__dkeg = IntegerArrayType(mdzj__zkcv)
                else:
                    num__dkeg = types.Array(mdzj__zkcv, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                mdzj__zkcv = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    num__dkeg = IntegerArrayType(mdzj__zkcv)
                else:
                    num__dkeg = types.Array(mdzj__zkcv, 1, 'C')
            elif typ.dtype == types.bool_:
                mdzj__zkcv = typ.dtype
                num__dkeg = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(mdzj__zkcv
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(num__dkeg)
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
                fnof__jmrho = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(fnof__jmrho)
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
        yng__ypgdo = S.dtype.unit
        if yng__ypgdo != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        wex__unzkv = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(wex__unzkv)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    umu__tfw = cgutils.is_not_null(builder, parent_obj)
    nfmkf__uyj = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(umu__tfw):
        hbxj__dtukh = pyapi.object_getattr_string(parent_obj, 'columns')
        acgzw__lcw = pyapi.call_method(hbxj__dtukh, '__len__', ())
        builder.store(pyapi.long_as_longlong(acgzw__lcw), nfmkf__uyj)
        pyapi.decref(acgzw__lcw)
        pyapi.decref(hbxj__dtukh)
    use_parent_obj = builder.and_(umu__tfw, builder.icmp_unsigned('==',
        builder.load(nfmkf__uyj), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        fdhw__olxsw = df_typ.runtime_colname_typ
        context.nrt.incref(builder, fdhw__olxsw, dataframe_payload.columns)
        return pyapi.from_native_value(fdhw__olxsw, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        jzble__csmie = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        jzble__csmie = np.array(df_typ.columns, 'int64')
    else:
        jzble__csmie = df_typ.columns
    mwdb__dmwfm = numba.typeof(jzble__csmie)
    liot__xhbdb = context.get_constant_generic(builder, mwdb__dmwfm,
        jzble__csmie)
    ldpr__geadx = pyapi.from_native_value(mwdb__dmwfm, liot__xhbdb, c.
        env_manager)
    return ldpr__geadx


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (ohdl__zdgrj, mmmr__fcytq):
        with ohdl__zdgrj:
            pyapi.incref(obj)
            hcc__ukn = context.insert_const_string(c.builder.module, 'numpy')
            mlbt__pahv = pyapi.import_module_noblock(hcc__ukn)
            if df_typ.has_runtime_cols:
                gytab__ybtqc = 0
            else:
                gytab__ybtqc = len(df_typ.columns)
            twoyh__nmar = pyapi.long_from_longlong(lir.Constant(lir.IntType
                (64), gytab__ybtqc))
            uta__epmt = pyapi.call_method(mlbt__pahv, 'arange', (twoyh__nmar,))
            pyapi.object_setattr_string(obj, 'columns', uta__epmt)
            pyapi.decref(mlbt__pahv)
            pyapi.decref(uta__epmt)
            pyapi.decref(twoyh__nmar)
        with mmmr__fcytq:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            gwrih__ner = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            hcc__ukn = context.insert_const_string(c.builder.module, 'pandas')
            mlbt__pahv = pyapi.import_module_noblock(hcc__ukn)
            df_obj = pyapi.call_method(mlbt__pahv, 'DataFrame', (pyapi.
                borrow_none(), gwrih__ner))
            pyapi.decref(mlbt__pahv)
            pyapi.decref(gwrih__ner)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    fwo__kkzs = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = fwo__kkzs.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        buizr__wjy = typ.table_type
        zmez__nydo = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, buizr__wjy, zmez__nydo)
        yitbv__glvey = box_table(buizr__wjy, zmez__nydo, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (etkw__plf, bancx__vbht):
            with etkw__plf:
                vlm__escan = pyapi.object_getattr_string(yitbv__glvey, 'arrays'
                    )
                gjcge__xcx = c.pyapi.make_none()
                if n_cols is None:
                    acgzw__lcw = pyapi.call_method(vlm__escan, '__len__', ())
                    bpex__lagnn = pyapi.long_as_longlong(acgzw__lcw)
                    pyapi.decref(acgzw__lcw)
                else:
                    bpex__lagnn = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, bpex__lagnn) as glio__fon:
                    i = glio__fon.index
                    tumf__hvbl = pyapi.list_getitem(vlm__escan, i)
                    not__gov = c.builder.icmp_unsigned('!=', tumf__hvbl,
                        gjcge__xcx)
                    with builder.if_then(not__gov):
                        vre__jqngu = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, vre__jqngu, tumf__hvbl)
                        pyapi.decref(vre__jqngu)
                pyapi.decref(vlm__escan)
                pyapi.decref(gjcge__xcx)
            with bancx__vbht:
                df_obj = builder.load(res)
                gwrih__ner = pyapi.object_getattr_string(df_obj, 'index')
                kdlgr__idfmf = c.pyapi.call_method(yitbv__glvey,
                    'to_pandas', (gwrih__ner,))
                builder.store(kdlgr__idfmf, res)
                pyapi.decref(df_obj)
                pyapi.decref(gwrih__ner)
        pyapi.decref(yitbv__glvey)
    else:
        enyx__ydx = [builder.extract_value(dataframe_payload.data, i) for i in
            range(n_cols)]
        npv__bhrk = typ.data
        for i, gnya__jhwt, xfl__sqd in zip(range(n_cols), enyx__ydx, npv__bhrk
            ):
            rph__xwnrz = cgutils.alloca_once_value(builder, gnya__jhwt)
            xuov__pqwxp = cgutils.alloca_once_value(builder, context.
                get_constant_null(xfl__sqd))
            not__gov = builder.not_(is_ll_eq(builder, rph__xwnrz, xuov__pqwxp))
            sschw__nxut = builder.or_(builder.not_(use_parent_obj), builder
                .and_(use_parent_obj, not__gov))
            with builder.if_then(sschw__nxut):
                vre__jqngu = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, xfl__sqd, gnya__jhwt)
                arr_obj = pyapi.from_native_value(xfl__sqd, gnya__jhwt, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, vre__jqngu, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(vre__jqngu)
    df_obj = builder.load(res)
    ldpr__geadx = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', ldpr__geadx)
    pyapi.decref(ldpr__geadx)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    gjcge__xcx = pyapi.borrow_none()
    qaq__bpbut = pyapi.unserialize(pyapi.serialize_object(slice))
    fkxbe__klyca = pyapi.call_function_objargs(qaq__bpbut, [gjcge__xcx])
    aidio__fokj = pyapi.long_from_longlong(col_ind)
    fvn__grj = pyapi.tuple_pack([fkxbe__klyca, aidio__fokj])
    stbb__fcuqh = pyapi.object_getattr_string(df_obj, 'iloc')
    sqdy__ozvmh = pyapi.object_getitem(stbb__fcuqh, fvn__grj)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        iam__pmuf = pyapi.object_getattr_string(sqdy__ozvmh, 'array')
    else:
        iam__pmuf = pyapi.object_getattr_string(sqdy__ozvmh, 'values')
    if isinstance(data_typ, types.Array):
        uysr__jnqi = context.insert_const_string(builder.module, 'numpy')
        onah__koza = pyapi.import_module_noblock(uysr__jnqi)
        arr_obj = pyapi.call_method(onah__koza, 'ascontiguousarray', (
            iam__pmuf,))
        pyapi.decref(iam__pmuf)
        pyapi.decref(onah__koza)
    else:
        arr_obj = iam__pmuf
    pyapi.decref(qaq__bpbut)
    pyapi.decref(fkxbe__klyca)
    pyapi.decref(aidio__fokj)
    pyapi.decref(fvn__grj)
    pyapi.decref(stbb__fcuqh)
    pyapi.decref(sqdy__ozvmh)
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
        fwo__kkzs = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            fwo__kkzs.parent, args[1], data_typ)
        xvrkh__jisf = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            zmez__nydo = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            qyx__etilm = df_typ.table_type.type_to_blk[data_typ]
            rohw__ndbpd = getattr(zmez__nydo, f'block_{qyx__etilm}')
            dxkut__jqpsv = ListInstance(c.context, c.builder, types.List(
                data_typ), rohw__ndbpd)
            wwud__joml = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            dxkut__jqpsv.inititem(wwud__joml, xvrkh__jisf.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, xvrkh__jisf.value, col_ind)
        pfq__fifix = DataFramePayloadType(df_typ)
        yiu__uevv = context.nrt.meminfo_data(builder, fwo__kkzs.meminfo)
        fnwy__zrm = context.get_value_type(pfq__fifix).as_pointer()
        yiu__uevv = builder.bitcast(yiu__uevv, fnwy__zrm)
        builder.store(dataframe_payload._getvalue(), yiu__uevv)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        iam__pmuf = c.pyapi.object_getattr_string(val, 'array')
    else:
        iam__pmuf = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        uysr__jnqi = c.context.insert_const_string(c.builder.module, 'numpy')
        onah__koza = c.pyapi.import_module_noblock(uysr__jnqi)
        arr_obj = c.pyapi.call_method(onah__koza, 'ascontiguousarray', (
            iam__pmuf,))
        c.pyapi.decref(iam__pmuf)
        c.pyapi.decref(onah__koza)
    else:
        arr_obj = iam__pmuf
    phmn__skvc = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    gwrih__ner = c.pyapi.object_getattr_string(val, 'index')
    mwxbj__pxup = c.pyapi.to_native_value(typ.index, gwrih__ner).value
    goezo__rhe = c.pyapi.object_getattr_string(val, 'name')
    ycqw__iywng = c.pyapi.to_native_value(typ.name_typ, goezo__rhe).value
    vyj__zyso = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, phmn__skvc, mwxbj__pxup, ycqw__iywng)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(gwrih__ner)
    c.pyapi.decref(goezo__rhe)
    return NativeValue(vyj__zyso)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        ifcr__lxf = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(ifcr__lxf._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    hcc__ukn = c.context.insert_const_string(c.builder.module, 'pandas')
    xlb__ngxu = c.pyapi.import_module_noblock(hcc__ukn)
    pybgb__prh = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, pybgb__prh.data)
    c.context.nrt.incref(c.builder, typ.index, pybgb__prh.index)
    c.context.nrt.incref(c.builder, typ.name_typ, pybgb__prh.name)
    arr_obj = c.pyapi.from_native_value(typ.data, pybgb__prh.data, c.
        env_manager)
    gwrih__ner = c.pyapi.from_native_value(typ.index, pybgb__prh.index, c.
        env_manager)
    goezo__rhe = c.pyapi.from_native_value(typ.name_typ, pybgb__prh.name, c
        .env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(xlb__ngxu, 'Series', (arr_obj, gwrih__ner,
        dtype, goezo__rhe))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(gwrih__ner)
    c.pyapi.decref(goezo__rhe)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(xlb__ngxu)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    ler__rjw = []
    for bld__yahch in typ_list:
        if isinstance(bld__yahch, int) and not isinstance(bld__yahch, bool):
            ixcew__nqd = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), bld__yahch))
        else:
            pdkoh__gwx = numba.typeof(bld__yahch)
            jqa__bdhdg = context.get_constant_generic(builder, pdkoh__gwx,
                bld__yahch)
            ixcew__nqd = pyapi.from_native_value(pdkoh__gwx, jqa__bdhdg,
                env_manager)
        ler__rjw.append(ixcew__nqd)
    wkb__fosow = pyapi.list_pack(ler__rjw)
    for val in ler__rjw:
        pyapi.decref(val)
    return wkb__fosow


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    bnn__awc = not typ.has_runtime_cols
    xugv__qkfqm = 2 if bnn__awc else 1
    frt__pkd = pyapi.dict_new(xugv__qkfqm)
    mflop__dvvkz = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(frt__pkd, 'dist', mflop__dvvkz)
    pyapi.decref(mflop__dvvkz)
    if bnn__awc:
        bul__aiynv = _dtype_to_type_enum_list(typ.index)
        if bul__aiynv != None:
            cvnj__uzfhl = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, bul__aiynv)
        else:
            cvnj__uzfhl = pyapi.make_none()
        if typ.is_table_format:
            piqw__xlzg = typ.table_type
            dyd__jinep = pyapi.list_new(lir.Constant(lir.IntType(64), len(
                typ.data)))
            for qyx__etilm, dtype in piqw__xlzg.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                bpex__lagnn = c.context.get_constant(types.int64, len(
                    piqw__xlzg.block_to_arr_ind[qyx__etilm]))
                uqpt__ikenu = c.context.make_constant_array(c.builder,
                    types.Array(types.int64, 1, 'C'), np.array(piqw__xlzg.
                    block_to_arr_ind[qyx__etilm], dtype=np.int64))
                qayi__kwve = c.context.make_array(types.Array(types.int64, 
                    1, 'C'))(c.context, c.builder, uqpt__ikenu)
                with cgutils.for_range(c.builder, bpex__lagnn) as glio__fon:
                    i = glio__fon.index
                    kjgfu__mcmco = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), qayi__kwve, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(dyd__jinep, kjgfu__mcmco, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            ahhx__wbvck = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    wkb__fosow = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    wkb__fosow = pyapi.make_none()
                ahhx__wbvck.append(wkb__fosow)
            dyd__jinep = pyapi.list_pack(ahhx__wbvck)
            for val in ahhx__wbvck:
                pyapi.decref(val)
        ffcbf__cppao = pyapi.list_pack([cvnj__uzfhl, dyd__jinep])
        pyapi.dict_setitem_string(frt__pkd, 'type_metadata', ffcbf__cppao)
    pyapi.object_setattr_string(obj, '_bodo_meta', frt__pkd)
    pyapi.decref(frt__pkd)


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
    frt__pkd = pyapi.dict_new(2)
    mflop__dvvkz = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    bul__aiynv = _dtype_to_type_enum_list(typ.index)
    if bul__aiynv != None:
        cvnj__uzfhl = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, bul__aiynv)
    else:
        cvnj__uzfhl = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            lfbl__iscw = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            lfbl__iscw = pyapi.make_none()
    else:
        lfbl__iscw = pyapi.make_none()
    izm__beoy = pyapi.list_pack([cvnj__uzfhl, lfbl__iscw])
    pyapi.dict_setitem_string(frt__pkd, 'type_metadata', izm__beoy)
    pyapi.decref(izm__beoy)
    pyapi.dict_setitem_string(frt__pkd, 'dist', mflop__dvvkz)
    pyapi.object_setattr_string(obj, '_bodo_meta', frt__pkd)
    pyapi.decref(frt__pkd)
    pyapi.decref(mflop__dvvkz)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as lpw__qsp:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    oxps__yfixq = numba.np.numpy_support.map_layout(val)
    umyf__guahp = not val.flags.writeable
    return types.Array(dtype, val.ndim, oxps__yfixq, readonly=umyf__guahp)


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
    cii__adtzg = val[i]
    if isinstance(cii__adtzg, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(cii__adtzg, bytes):
        return binary_array_type
    elif isinstance(cii__adtzg, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(cii__adtzg, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(cii__adtzg))
    elif isinstance(cii__adtzg, (dict, Dict)) and all(isinstance(mnq__sitfk,
        str) for mnq__sitfk in cii__adtzg.keys()):
        jjw__jyag = tuple(cii__adtzg.keys())
        vyzl__hbocr = tuple(_get_struct_value_arr_type(v) for v in
            cii__adtzg.values())
        return StructArrayType(vyzl__hbocr, jjw__jyag)
    elif isinstance(cii__adtzg, (dict, Dict)):
        bqgle__wfz = numba.typeof(_value_to_array(list(cii__adtzg.keys())))
        hwl__ylp = numba.typeof(_value_to_array(list(cii__adtzg.values())))
        bqgle__wfz = to_str_arr_if_dict_array(bqgle__wfz)
        hwl__ylp = to_str_arr_if_dict_array(hwl__ylp)
        return MapArrayType(bqgle__wfz, hwl__ylp)
    elif isinstance(cii__adtzg, tuple):
        vyzl__hbocr = tuple(_get_struct_value_arr_type(v) for v in cii__adtzg)
        return TupleArrayType(vyzl__hbocr)
    if isinstance(cii__adtzg, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(cii__adtzg, list):
            cii__adtzg = _value_to_array(cii__adtzg)
        dsb__byu = numba.typeof(cii__adtzg)
        dsb__byu = to_str_arr_if_dict_array(dsb__byu)
        return ArrayItemArrayType(dsb__byu)
    if isinstance(cii__adtzg, datetime.date):
        return datetime_date_array_type
    if isinstance(cii__adtzg, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(cii__adtzg, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(cii__adtzg, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {cii__adtzg}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    gbwc__nwlsu = val.copy()
    gbwc__nwlsu.append(None)
    gnya__jhwt = np.array(gbwc__nwlsu, np.object_)
    if len(val) and isinstance(val[0], float):
        gnya__jhwt = np.array(val, np.float64)
    return gnya__jhwt


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
    xfl__sqd = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        xfl__sqd = to_nullable_type(xfl__sqd)
    return xfl__sqd
