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
    sjoru__snozo = tuple(val.columns.to_list())
    rebwh__oex = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        yihk__aebyw = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        yihk__aebyw = numba.typeof(val.index)
    pbbh__lumn = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    iggqk__kzovn = len(rebwh__oex) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(rebwh__oex, yihk__aebyw, sjoru__snozo, pbbh__lumn,
        is_table_format=iggqk__kzovn)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    pbbh__lumn = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        meje__cirxw = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        meje__cirxw = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    oqzvy__qzzht = dtype_to_array_type(dtype)
    if _use_dict_str_type and oqzvy__qzzht == string_array_type:
        oqzvy__qzzht = bodo.dict_str_arr_type
    return SeriesType(dtype, data=oqzvy__qzzht, index=meje__cirxw, name_typ
        =numba.typeof(val.name), dist=pbbh__lumn)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    gbt__arcw = c.pyapi.object_getattr_string(val, 'index')
    yfme__ohk = c.pyapi.to_native_value(typ.index, gbt__arcw).value
    c.pyapi.decref(gbt__arcw)
    if typ.is_table_format:
        uqqwh__jkyo = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        uqqwh__jkyo.parent = val
        for rpr__gnxji, aqzx__zld in typ.table_type.type_to_blk.items():
            uyg__rsw = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[aqzx__zld]))
            msy__oxc, fbrb__ing = ListInstance.allocate_ex(c.context, c.
                builder, types.List(rpr__gnxji), uyg__rsw)
            fbrb__ing.size = uyg__rsw
            setattr(uqqwh__jkyo, f'block_{aqzx__zld}', fbrb__ing.value)
        pbyw__pdpb = c.pyapi.call_method(val, '__len__', ())
        ofnr__mcgh = c.pyapi.long_as_longlong(pbyw__pdpb)
        c.pyapi.decref(pbyw__pdpb)
        uqqwh__jkyo.len = ofnr__mcgh
        fqdxo__amsnq = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [uqqwh__jkyo._getvalue()])
    else:
        wcvs__bfyj = [c.context.get_constant_null(rpr__gnxji) for
            rpr__gnxji in typ.data]
        fqdxo__amsnq = c.context.make_tuple(c.builder, types.Tuple(typ.data
            ), wcvs__bfyj)
    kjk__rzvk = construct_dataframe(c.context, c.builder, typ, fqdxo__amsnq,
        yfme__ohk, val, None)
    return NativeValue(kjk__rzvk)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        yziu__wammh = df._bodo_meta['type_metadata'][1]
    else:
        yziu__wammh = [None] * len(df.columns)
    djah__motog = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=yziu__wammh[i])) for i in range(len(df.columns))]
    djah__motog = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        rpr__gnxji == string_array_type else rpr__gnxji) for rpr__gnxji in
        djah__motog]
    return tuple(djah__motog)


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
    vng__shsc, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(vng__shsc) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {vng__shsc}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        lzn__juc, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return lzn__juc, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        lzn__juc, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return lzn__juc, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        bmcd__cbo = typ_enum_list[1]
        idrd__iwp = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(bmcd__cbo, idrd__iwp)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        sjgdt__orc = typ_enum_list[1]
        uso__xcr = tuple(typ_enum_list[2:2 + sjgdt__orc])
        kabo__iom = typ_enum_list[2 + sjgdt__orc:]
        pnic__aonq = []
        for i in range(sjgdt__orc):
            kabo__iom, sdql__ohh = _dtype_from_type_enum_list_recursor(
                kabo__iom)
            pnic__aonq.append(sdql__ohh)
        return kabo__iom, StructType(tuple(pnic__aonq), uso__xcr)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        orzno__ntlh = typ_enum_list[1]
        kabo__iom = typ_enum_list[2:]
        return kabo__iom, orzno__ntlh
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        orzno__ntlh = typ_enum_list[1]
        kabo__iom = typ_enum_list[2:]
        return kabo__iom, numba.types.literal(orzno__ntlh)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        kabo__iom, hvfm__atf = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        kabo__iom, pme__twl = _dtype_from_type_enum_list_recursor(kabo__iom)
        kabo__iom, tcjs__nsf = _dtype_from_type_enum_list_recursor(kabo__iom)
        kabo__iom, rjqdi__itqx = _dtype_from_type_enum_list_recursor(kabo__iom)
        kabo__iom, mor__rcq = _dtype_from_type_enum_list_recursor(kabo__iom)
        return kabo__iom, PDCategoricalDtype(hvfm__atf, pme__twl, tcjs__nsf,
            rjqdi__itqx, mor__rcq)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        kabo__iom, bcsty__leoov = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return kabo__iom, DatetimeIndexType(bcsty__leoov)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        kabo__iom, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        kabo__iom, bcsty__leoov = _dtype_from_type_enum_list_recursor(kabo__iom
            )
        kabo__iom, rjqdi__itqx = _dtype_from_type_enum_list_recursor(kabo__iom)
        return kabo__iom, NumericIndexType(dtype, bcsty__leoov, rjqdi__itqx)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        kabo__iom, uhrq__vtpq = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        kabo__iom, bcsty__leoov = _dtype_from_type_enum_list_recursor(kabo__iom
            )
        return kabo__iom, PeriodIndexType(uhrq__vtpq, bcsty__leoov)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        kabo__iom, rjqdi__itqx = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        kabo__iom, bcsty__leoov = _dtype_from_type_enum_list_recursor(kabo__iom
            )
        return kabo__iom, CategoricalIndexType(rjqdi__itqx, bcsty__leoov)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        kabo__iom, bcsty__leoov = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return kabo__iom, RangeIndexType(bcsty__leoov)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        kabo__iom, bcsty__leoov = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return kabo__iom, StringIndexType(bcsty__leoov)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        kabo__iom, bcsty__leoov = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return kabo__iom, BinaryIndexType(bcsty__leoov)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        kabo__iom, bcsty__leoov = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return kabo__iom, TimedeltaIndexType(bcsty__leoov)
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
        kjag__cfnd = get_overload_const_int(typ)
        if numba.types.maybe_literal(kjag__cfnd) == typ:
            return [SeriesDtypeEnum.LiteralType.value, kjag__cfnd]
    elif is_overload_constant_str(typ):
        kjag__cfnd = get_overload_const_str(typ)
        if numba.types.maybe_literal(kjag__cfnd) == typ:
            return [SeriesDtypeEnum.LiteralType.value, kjag__cfnd]
    elif is_overload_constant_bool(typ):
        kjag__cfnd = get_overload_const_bool(typ)
        if numba.types.maybe_literal(kjag__cfnd) == typ:
            return [SeriesDtypeEnum.LiteralType.value, kjag__cfnd]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        nyujs__skn = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for qcree__fuo in typ.names:
            nyujs__skn.append(qcree__fuo)
        for arfp__kgou in typ.data:
            nyujs__skn += _dtype_to_type_enum_list_recursor(arfp__kgou)
        return nyujs__skn
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        loq__lxyr = _dtype_to_type_enum_list_recursor(typ.categories)
        tzs__mymi = _dtype_to_type_enum_list_recursor(typ.elem_type)
        wzehg__vqgwa = _dtype_to_type_enum_list_recursor(typ.ordered)
        zvrbd__juwbb = _dtype_to_type_enum_list_recursor(typ.data)
        ufnfo__puqor = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + loq__lxyr + tzs__mymi + wzehg__vqgwa + zvrbd__juwbb + ufnfo__puqor
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                fhymk__vcbk = types.float64
                ugjc__ozfuj = types.Array(fhymk__vcbk, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                fhymk__vcbk = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    ugjc__ozfuj = IntegerArrayType(fhymk__vcbk)
                else:
                    ugjc__ozfuj = types.Array(fhymk__vcbk, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                fhymk__vcbk = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    ugjc__ozfuj = IntegerArrayType(fhymk__vcbk)
                else:
                    ugjc__ozfuj = types.Array(fhymk__vcbk, 1, 'C')
            elif typ.dtype == types.bool_:
                fhymk__vcbk = typ.dtype
                ugjc__ozfuj = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(fhymk__vcbk
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(ugjc__ozfuj)
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
                izt__egd = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(izt__egd)
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
        kvh__klpfp = S.dtype.unit
        if kvh__klpfp != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        gytl__suu = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.dtype.tz
            )
        return PandasDatetimeTZDtype(gytl__suu)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    vpjat__aggmf = cgutils.is_not_null(builder, parent_obj)
    jeaza__wzg = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(vpjat__aggmf):
        iljxp__hrp = pyapi.object_getattr_string(parent_obj, 'columns')
        pbyw__pdpb = pyapi.call_method(iljxp__hrp, '__len__', ())
        builder.store(pyapi.long_as_longlong(pbyw__pdpb), jeaza__wzg)
        pyapi.decref(pbyw__pdpb)
        pyapi.decref(iljxp__hrp)
    use_parent_obj = builder.and_(vpjat__aggmf, builder.icmp_unsigned('==',
        builder.load(jeaza__wzg), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        ilye__bei = df_typ.runtime_colname_typ
        context.nrt.incref(builder, ilye__bei, dataframe_payload.columns)
        return pyapi.from_native_value(ilye__bei, dataframe_payload.columns,
            c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        afylp__phuhu = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        afylp__phuhu = np.array(df_typ.columns, 'int64')
    else:
        afylp__phuhu = df_typ.columns
    uqhew__vrkaq = numba.typeof(afylp__phuhu)
    hoaqz__hwdnh = context.get_constant_generic(builder, uqhew__vrkaq,
        afylp__phuhu)
    rvod__hrq = pyapi.from_native_value(uqhew__vrkaq, hoaqz__hwdnh, c.
        env_manager)
    return rvod__hrq


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (hkdqp__wxe, veea__tpea):
        with hkdqp__wxe:
            pyapi.incref(obj)
            ehdc__wwh = context.insert_const_string(c.builder.module, 'numpy')
            bqwwz__qfiv = pyapi.import_module_noblock(ehdc__wwh)
            if df_typ.has_runtime_cols:
                upb__hbl = 0
            else:
                upb__hbl = len(df_typ.columns)
            cmz__rell = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), upb__hbl))
            dab__mvgt = pyapi.call_method(bqwwz__qfiv, 'arange', (cmz__rell,))
            pyapi.object_setattr_string(obj, 'columns', dab__mvgt)
            pyapi.decref(bqwwz__qfiv)
            pyapi.decref(dab__mvgt)
            pyapi.decref(cmz__rell)
        with veea__tpea:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            gck__fgi = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            ehdc__wwh = context.insert_const_string(c.builder.module, 'pandas')
            bqwwz__qfiv = pyapi.import_module_noblock(ehdc__wwh)
            df_obj = pyapi.call_method(bqwwz__qfiv, 'DataFrame', (pyapi.
                borrow_none(), gck__fgi))
            pyapi.decref(bqwwz__qfiv)
            pyapi.decref(gck__fgi)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    uuz__bbc = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = uuz__bbc.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        rregu__ptmcj = typ.table_type
        uqqwh__jkyo = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, rregu__ptmcj, uqqwh__jkyo)
        gche__zxv = box_table(rregu__ptmcj, uqqwh__jkyo, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (vpubn__qqpb, ibi__gvj):
            with vpubn__qqpb:
                lua__ywalx = pyapi.object_getattr_string(gche__zxv, 'arrays')
                emd__xdfku = c.pyapi.make_none()
                if n_cols is None:
                    pbyw__pdpb = pyapi.call_method(lua__ywalx, '__len__', ())
                    uyg__rsw = pyapi.long_as_longlong(pbyw__pdpb)
                    pyapi.decref(pbyw__pdpb)
                else:
                    uyg__rsw = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, uyg__rsw) as ollus__hju:
                    i = ollus__hju.index
                    wnp__ttqu = pyapi.list_getitem(lua__ywalx, i)
                    aypk__vhbd = c.builder.icmp_unsigned('!=', wnp__ttqu,
                        emd__xdfku)
                    with builder.if_then(aypk__vhbd):
                        xsxz__rewau = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, xsxz__rewau, wnp__ttqu)
                        pyapi.decref(xsxz__rewau)
                pyapi.decref(lua__ywalx)
                pyapi.decref(emd__xdfku)
            with ibi__gvj:
                df_obj = builder.load(res)
                gck__fgi = pyapi.object_getattr_string(df_obj, 'index')
                yacz__pdtba = c.pyapi.call_method(gche__zxv, 'to_pandas', (
                    gck__fgi,))
                builder.store(yacz__pdtba, res)
                pyapi.decref(df_obj)
                pyapi.decref(gck__fgi)
        pyapi.decref(gche__zxv)
    else:
        iavux__wxe = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        edpn__vdgsy = typ.data
        for i, pqsg__dqn, oqzvy__qzzht in zip(range(n_cols), iavux__wxe,
            edpn__vdgsy):
            ottn__ucmlm = cgutils.alloca_once_value(builder, pqsg__dqn)
            bklu__igiuj = cgutils.alloca_once_value(builder, context.
                get_constant_null(oqzvy__qzzht))
            aypk__vhbd = builder.not_(is_ll_eq(builder, ottn__ucmlm,
                bklu__igiuj))
            uperz__zogw = builder.or_(builder.not_(use_parent_obj), builder
                .and_(use_parent_obj, aypk__vhbd))
            with builder.if_then(uperz__zogw):
                xsxz__rewau = pyapi.long_from_longlong(context.get_constant
                    (types.int64, i))
                context.nrt.incref(builder, oqzvy__qzzht, pqsg__dqn)
                arr_obj = pyapi.from_native_value(oqzvy__qzzht, pqsg__dqn,
                    c.env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, xsxz__rewau, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(xsxz__rewau)
    df_obj = builder.load(res)
    rvod__hrq = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', rvod__hrq)
    pyapi.decref(rvod__hrq)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    emd__xdfku = pyapi.borrow_none()
    tiyyd__xjuhq = pyapi.unserialize(pyapi.serialize_object(slice))
    fmbex__lvd = pyapi.call_function_objargs(tiyyd__xjuhq, [emd__xdfku])
    zszz__yldt = pyapi.long_from_longlong(col_ind)
    cau__lvta = pyapi.tuple_pack([fmbex__lvd, zszz__yldt])
    pawc__wjp = pyapi.object_getattr_string(df_obj, 'iloc')
    rta__mtrq = pyapi.object_getitem(pawc__wjp, cau__lvta)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        uxa__mespi = pyapi.object_getattr_string(rta__mtrq, 'array')
    else:
        uxa__mespi = pyapi.object_getattr_string(rta__mtrq, 'values')
    if isinstance(data_typ, types.Array):
        hhipg__zsm = context.insert_const_string(builder.module, 'numpy')
        eymj__ddubf = pyapi.import_module_noblock(hhipg__zsm)
        arr_obj = pyapi.call_method(eymj__ddubf, 'ascontiguousarray', (
            uxa__mespi,))
        pyapi.decref(uxa__mespi)
        pyapi.decref(eymj__ddubf)
    else:
        arr_obj = uxa__mespi
    pyapi.decref(tiyyd__xjuhq)
    pyapi.decref(fmbex__lvd)
    pyapi.decref(zszz__yldt)
    pyapi.decref(cau__lvta)
    pyapi.decref(pawc__wjp)
    pyapi.decref(rta__mtrq)
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
        uuz__bbc = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            uuz__bbc.parent, args[1], data_typ)
        cvaz__srj = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            uqqwh__jkyo = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            aqzx__zld = df_typ.table_type.type_to_blk[data_typ]
            twoa__iqill = getattr(uqqwh__jkyo, f'block_{aqzx__zld}')
            snmu__tsof = ListInstance(c.context, c.builder, types.List(
                data_typ), twoa__iqill)
            wlr__ayni = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[col_ind])
            snmu__tsof.inititem(wlr__ayni, cvaz__srj.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, cvaz__srj.value, col_ind)
        erh__mdqcw = DataFramePayloadType(df_typ)
        ocoh__xamcr = context.nrt.meminfo_data(builder, uuz__bbc.meminfo)
        rtcj__abb = context.get_value_type(erh__mdqcw).as_pointer()
        ocoh__xamcr = builder.bitcast(ocoh__xamcr, rtcj__abb)
        builder.store(dataframe_payload._getvalue(), ocoh__xamcr)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        uxa__mespi = c.pyapi.object_getattr_string(val, 'array')
    else:
        uxa__mespi = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        hhipg__zsm = c.context.insert_const_string(c.builder.module, 'numpy')
        eymj__ddubf = c.pyapi.import_module_noblock(hhipg__zsm)
        arr_obj = c.pyapi.call_method(eymj__ddubf, 'ascontiguousarray', (
            uxa__mespi,))
        c.pyapi.decref(uxa__mespi)
        c.pyapi.decref(eymj__ddubf)
    else:
        arr_obj = uxa__mespi
    gkapk__uyei = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    gck__fgi = c.pyapi.object_getattr_string(val, 'index')
    yfme__ohk = c.pyapi.to_native_value(typ.index, gck__fgi).value
    ryjh__vlemi = c.pyapi.object_getattr_string(val, 'name')
    rvmh__wndx = c.pyapi.to_native_value(typ.name_typ, ryjh__vlemi).value
    ajnqn__loyib = bodo.hiframes.pd_series_ext.construct_series(c.context,
        c.builder, typ, gkapk__uyei, yfme__ohk, rvmh__wndx)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(gck__fgi)
    c.pyapi.decref(ryjh__vlemi)
    return NativeValue(ajnqn__loyib)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        zid__qmgo = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(zid__qmgo._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    ehdc__wwh = c.context.insert_const_string(c.builder.module, 'pandas')
    hvxwn__alam = c.pyapi.import_module_noblock(ehdc__wwh)
    cyb__nudij = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, cyb__nudij.data)
    c.context.nrt.incref(c.builder, typ.index, cyb__nudij.index)
    c.context.nrt.incref(c.builder, typ.name_typ, cyb__nudij.name)
    arr_obj = c.pyapi.from_native_value(typ.data, cyb__nudij.data, c.
        env_manager)
    gck__fgi = c.pyapi.from_native_value(typ.index, cyb__nudij.index, c.
        env_manager)
    ryjh__vlemi = c.pyapi.from_native_value(typ.name_typ, cyb__nudij.name,
        c.env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(hvxwn__alam, 'Series', (arr_obj, gck__fgi,
        dtype, ryjh__vlemi))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(gck__fgi)
    c.pyapi.decref(ryjh__vlemi)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(hvxwn__alam)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    nfpa__waak = []
    for vcsts__xxzxn in typ_list:
        if isinstance(vcsts__xxzxn, int) and not isinstance(vcsts__xxzxn, bool
            ):
            pqqjc__ord = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), vcsts__xxzxn))
        else:
            rimc__ssiyz = numba.typeof(vcsts__xxzxn)
            tzo__bltu = context.get_constant_generic(builder, rimc__ssiyz,
                vcsts__xxzxn)
            pqqjc__ord = pyapi.from_native_value(rimc__ssiyz, tzo__bltu,
                env_manager)
        nfpa__waak.append(pqqjc__ord)
    ivleh__xbr = pyapi.list_pack(nfpa__waak)
    for val in nfpa__waak:
        pyapi.decref(val)
    return ivleh__xbr


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    mkld__phr = not typ.has_runtime_cols
    rcdc__kkzw = 2 if mkld__phr else 1
    cndg__rsk = pyapi.dict_new(rcdc__kkzw)
    bmyd__ztyvk = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(cndg__rsk, 'dist', bmyd__ztyvk)
    pyapi.decref(bmyd__ztyvk)
    if mkld__phr:
        bdap__trobw = _dtype_to_type_enum_list(typ.index)
        if bdap__trobw != None:
            eam__cfm = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, bdap__trobw)
        else:
            eam__cfm = pyapi.make_none()
        if typ.is_table_format:
            rpr__gnxji = typ.table_type
            ptlgj__itq = pyapi.list_new(lir.Constant(lir.IntType(64), len(
                typ.data)))
            for aqzx__zld, dtype in rpr__gnxji.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                uyg__rsw = c.context.get_constant(types.int64, len(
                    rpr__gnxji.block_to_arr_ind[aqzx__zld]))
                pyzwt__tryv = c.context.make_constant_array(c.builder,
                    types.Array(types.int64, 1, 'C'), np.array(rpr__gnxji.
                    block_to_arr_ind[aqzx__zld], dtype=np.int64))
                gewu__zom = c.context.make_array(types.Array(types.int64, 1,
                    'C'))(c.context, c.builder, pyzwt__tryv)
                with cgutils.for_range(c.builder, uyg__rsw) as ollus__hju:
                    i = ollus__hju.index
                    zse__uuvat = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), gewu__zom, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(ptlgj__itq, zse__uuvat, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            pkz__bypp = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    ivleh__xbr = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    ivleh__xbr = pyapi.make_none()
                pkz__bypp.append(ivleh__xbr)
            ptlgj__itq = pyapi.list_pack(pkz__bypp)
            for val in pkz__bypp:
                pyapi.decref(val)
        uqi__dlhvy = pyapi.list_pack([eam__cfm, ptlgj__itq])
        pyapi.dict_setitem_string(cndg__rsk, 'type_metadata', uqi__dlhvy)
    pyapi.object_setattr_string(obj, '_bodo_meta', cndg__rsk)
    pyapi.decref(cndg__rsk)


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
    cndg__rsk = pyapi.dict_new(2)
    bmyd__ztyvk = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    bdap__trobw = _dtype_to_type_enum_list(typ.index)
    if bdap__trobw != None:
        eam__cfm = type_enum_list_to_py_list_obj(pyapi, context, builder, c
            .env_manager, bdap__trobw)
    else:
        eam__cfm = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            typo__hppt = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            typo__hppt = pyapi.make_none()
    else:
        typo__hppt = pyapi.make_none()
    jdbyl__dvkmf = pyapi.list_pack([eam__cfm, typo__hppt])
    pyapi.dict_setitem_string(cndg__rsk, 'type_metadata', jdbyl__dvkmf)
    pyapi.decref(jdbyl__dvkmf)
    pyapi.dict_setitem_string(cndg__rsk, 'dist', bmyd__ztyvk)
    pyapi.object_setattr_string(obj, '_bodo_meta', cndg__rsk)
    pyapi.decref(cndg__rsk)
    pyapi.decref(bmyd__ztyvk)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as hwmia__tjvg:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    rlgnw__cczbj = numba.np.numpy_support.map_layout(val)
    zuoya__llfy = not val.flags.writeable
    return types.Array(dtype, val.ndim, rlgnw__cczbj, readonly=zuoya__llfy)


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
    vqulm__xbea = val[i]
    if isinstance(vqulm__xbea, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(vqulm__xbea, bytes):
        return binary_array_type
    elif isinstance(vqulm__xbea, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(vqulm__xbea, (int, np.int8, np.int16, np.int32, np.
        int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(vqulm__xbea)
            )
    elif isinstance(vqulm__xbea, (dict, Dict)) and all(isinstance(qzn__lmla,
        str) for qzn__lmla in vqulm__xbea.keys()):
        uso__xcr = tuple(vqulm__xbea.keys())
        ytru__prt = tuple(_get_struct_value_arr_type(v) for v in
            vqulm__xbea.values())
        return StructArrayType(ytru__prt, uso__xcr)
    elif isinstance(vqulm__xbea, (dict, Dict)):
        fymt__tlfpg = numba.typeof(_value_to_array(list(vqulm__xbea.keys())))
        gtm__eylc = numba.typeof(_value_to_array(list(vqulm__xbea.values())))
        fymt__tlfpg = to_str_arr_if_dict_array(fymt__tlfpg)
        gtm__eylc = to_str_arr_if_dict_array(gtm__eylc)
        return MapArrayType(fymt__tlfpg, gtm__eylc)
    elif isinstance(vqulm__xbea, tuple):
        ytru__prt = tuple(_get_struct_value_arr_type(v) for v in vqulm__xbea)
        return TupleArrayType(ytru__prt)
    if isinstance(vqulm__xbea, (list, np.ndarray, pd.arrays.BooleanArray,
        pd.arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(vqulm__xbea, list):
            vqulm__xbea = _value_to_array(vqulm__xbea)
        opue__kuhuu = numba.typeof(vqulm__xbea)
        opue__kuhuu = to_str_arr_if_dict_array(opue__kuhuu)
        return ArrayItemArrayType(opue__kuhuu)
    if isinstance(vqulm__xbea, datetime.date):
        return datetime_date_array_type
    if isinstance(vqulm__xbea, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(vqulm__xbea, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(vqulm__xbea, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {vqulm__xbea}'
        )


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    dpl__pkjr = val.copy()
    dpl__pkjr.append(None)
    pqsg__dqn = np.array(dpl__pkjr, np.object_)
    if len(val) and isinstance(val[0], float):
        pqsg__dqn = np.array(val, np.float64)
    return pqsg__dqn


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
    oqzvy__qzzht = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        oqzvy__qzzht = to_nullable_type(oqzvy__qzzht)
    return oqzvy__qzzht
