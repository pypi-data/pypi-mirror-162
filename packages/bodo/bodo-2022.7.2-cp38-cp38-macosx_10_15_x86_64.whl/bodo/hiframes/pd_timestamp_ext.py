"""Timestamp extension for Pandas Timestamp with timezone support."""
import calendar
import datetime
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pytz
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import ConcreteTemplate, infer_global, signature
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
import bodo.libs.str_ext
import bodo.utils.utils
from bodo.hiframes.datetime_date_ext import DatetimeDateType, _ord2ymd, _ymd2ord, get_isocalendar
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, _no_input, datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdatetime_ext
from bodo.libs.pd_datetime_arr_ext import get_pytz_type_info
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import BodoError, check_unsupported_args, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_iterable_type, is_overload_constant_int, is_overload_constant_str, is_overload_none, raise_bodo_error
ll.add_symbol('extract_year_days', hdatetime_ext.extract_year_days)
ll.add_symbol('get_month_day', hdatetime_ext.get_month_day)
ll.add_symbol('npy_datetimestruct_to_datetime', hdatetime_ext.
    npy_datetimestruct_to_datetime)
npy_datetimestruct_to_datetime = types.ExternalFunction(
    'npy_datetimestruct_to_datetime', types.int64(types.int64, types.int32,
    types.int32, types.int32, types.int32, types.int32, types.int32))
date_fields = ['year', 'month', 'day', 'hour', 'minute', 'second',
    'microsecond', 'nanosecond', 'quarter', 'dayofyear', 'day_of_year',
    'dayofweek', 'day_of_week', 'daysinmonth', 'days_in_month',
    'is_leap_year', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end', 'week', 'weekofyear',
    'weekday']
date_methods = ['normalize', 'day_name', 'month_name']
timedelta_fields = ['days', 'seconds', 'microseconds', 'nanoseconds']
timedelta_methods = ['total_seconds', 'to_pytimedelta']
iNaT = pd._libs.tslibs.iNaT


class PandasTimestampType(types.Type):

    def __init__(self, tz_val=None):
        self.tz = tz_val
        if tz_val is None:
            tjk__xva = 'PandasTimestampType()'
        else:
            tjk__xva = f'PandasTimestampType({tz_val})'
        super(PandasTimestampType, self).__init__(name=tjk__xva)


pd_timestamp_type = PandasTimestampType()


def check_tz_aware_unsupported(val, func_name):
    if isinstance(val, bodo.hiframes.series_dt_impl.
        SeriesDatetimePropertiesType):
        val = val.stype
    if isinstance(val, PandasTimestampType) and val.tz is not None:
        raise BodoError(
            f'{func_name} on Timezone-aware timestamp not yet supported. Please convert to timezone naive with ts.tz_convert(None)'
            )
    elif isinstance(val, bodo.DatetimeArrayType):
        raise BodoError(
            f'{func_name} on Timezone-aware array not yet supported. Please convert to timezone naive with arr.tz_convert(None)'
            )
    elif isinstance(val, bodo.DatetimeIndexType) and isinstance(val.data,
        bodo.DatetimeArrayType):
        raise BodoError(
            f'{func_name} on Timezone-aware index not yet supported. Please convert to timezone naive with index.tz_convert(None)'
            )
    elif isinstance(val, bodo.SeriesType) and isinstance(val.data, bodo.
        DatetimeArrayType):
        raise BodoError(
            f'{func_name} on Timezone-aware series not yet supported. Please convert to timezone naive with series.dt.tz_convert(None)'
            )
    elif isinstance(val, bodo.DataFrameType):
        for uqg__vxoaf in val.data:
            if isinstance(uqg__vxoaf, bodo.DatetimeArrayType):
                raise BodoError(
                    f'{func_name} on Timezone-aware columns not yet supported. Please convert each column to timezone naive with series.dt.tz_convert(None)'
                    )


@typeof_impl.register(pd.Timestamp)
def typeof_pd_timestamp(val, c):
    return PandasTimestampType(get_pytz_type_info(val.tz) if val.tz else None)


ts_field_typ = types.int64


@register_model(PandasTimestampType)
class PandasTimestampModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        fzt__jyg = [('year', ts_field_typ), ('month', ts_field_typ), ('day',
            ts_field_typ), ('hour', ts_field_typ), ('minute', ts_field_typ),
            ('second', ts_field_typ), ('microsecond', ts_field_typ), (
            'nanosecond', ts_field_typ), ('value', ts_field_typ)]
        models.StructModel.__init__(self, dmm, fe_type, fzt__jyg)


make_attribute_wrapper(PandasTimestampType, 'year', 'year')
make_attribute_wrapper(PandasTimestampType, 'month', 'month')
make_attribute_wrapper(PandasTimestampType, 'day', 'day')
make_attribute_wrapper(PandasTimestampType, 'hour', 'hour')
make_attribute_wrapper(PandasTimestampType, 'minute', 'minute')
make_attribute_wrapper(PandasTimestampType, 'second', 'second')
make_attribute_wrapper(PandasTimestampType, 'microsecond', 'microsecond')
make_attribute_wrapper(PandasTimestampType, 'nanosecond', 'nanosecond')
make_attribute_wrapper(PandasTimestampType, 'value', 'value')


@unbox(PandasTimestampType)
def unbox_pandas_timestamp(typ, val, c):
    ekb__xama = c.pyapi.object_getattr_string(val, 'year')
    cdx__nygm = c.pyapi.object_getattr_string(val, 'month')
    waat__ahih = c.pyapi.object_getattr_string(val, 'day')
    xxqde__ytrnm = c.pyapi.object_getattr_string(val, 'hour')
    wlp__fuu = c.pyapi.object_getattr_string(val, 'minute')
    ysn__shccf = c.pyapi.object_getattr_string(val, 'second')
    wycg__dtx = c.pyapi.object_getattr_string(val, 'microsecond')
    dadio__qbbgr = c.pyapi.object_getattr_string(val, 'nanosecond')
    mse__raoiv = c.pyapi.object_getattr_string(val, 'value')
    kffm__byvp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kffm__byvp.year = c.pyapi.long_as_longlong(ekb__xama)
    kffm__byvp.month = c.pyapi.long_as_longlong(cdx__nygm)
    kffm__byvp.day = c.pyapi.long_as_longlong(waat__ahih)
    kffm__byvp.hour = c.pyapi.long_as_longlong(xxqde__ytrnm)
    kffm__byvp.minute = c.pyapi.long_as_longlong(wlp__fuu)
    kffm__byvp.second = c.pyapi.long_as_longlong(ysn__shccf)
    kffm__byvp.microsecond = c.pyapi.long_as_longlong(wycg__dtx)
    kffm__byvp.nanosecond = c.pyapi.long_as_longlong(dadio__qbbgr)
    kffm__byvp.value = c.pyapi.long_as_longlong(mse__raoiv)
    c.pyapi.decref(ekb__xama)
    c.pyapi.decref(cdx__nygm)
    c.pyapi.decref(waat__ahih)
    c.pyapi.decref(xxqde__ytrnm)
    c.pyapi.decref(wlp__fuu)
    c.pyapi.decref(ysn__shccf)
    c.pyapi.decref(wycg__dtx)
    c.pyapi.decref(dadio__qbbgr)
    c.pyapi.decref(mse__raoiv)
    lpttr__wlpaa = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kffm__byvp._getvalue(), is_error=lpttr__wlpaa)


@box(PandasTimestampType)
def box_pandas_timestamp(typ, val, c):
    ftg__psw = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    ekb__xama = c.pyapi.long_from_longlong(ftg__psw.year)
    cdx__nygm = c.pyapi.long_from_longlong(ftg__psw.month)
    waat__ahih = c.pyapi.long_from_longlong(ftg__psw.day)
    xxqde__ytrnm = c.pyapi.long_from_longlong(ftg__psw.hour)
    wlp__fuu = c.pyapi.long_from_longlong(ftg__psw.minute)
    ysn__shccf = c.pyapi.long_from_longlong(ftg__psw.second)
    yae__hkhe = c.pyapi.long_from_longlong(ftg__psw.microsecond)
    lbqoz__btump = c.pyapi.long_from_longlong(ftg__psw.nanosecond)
    alp__wulhj = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timestamp))
    if typ.tz is None:
        res = c.pyapi.call_function_objargs(alp__wulhj, (ekb__xama,
            cdx__nygm, waat__ahih, xxqde__ytrnm, wlp__fuu, ysn__shccf,
            yae__hkhe, lbqoz__btump))
    else:
        if isinstance(typ.tz, int):
            nnkd__ykzh = c.pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), typ.tz))
        else:
            lsdux__jzg = c.context.insert_const_string(c.builder.module,
                str(typ.tz))
            nnkd__ykzh = c.pyapi.string_from_string(lsdux__jzg)
        args = c.pyapi.tuple_pack(())
        kwargs = c.pyapi.dict_pack([('year', ekb__xama), ('month',
            cdx__nygm), ('day', waat__ahih), ('hour', xxqde__ytrnm), (
            'minute', wlp__fuu), ('second', ysn__shccf), ('microsecond',
            yae__hkhe), ('nanosecond', lbqoz__btump), ('tz', nnkd__ykzh)])
        res = c.pyapi.call(alp__wulhj, args, kwargs)
        c.pyapi.decref(args)
        c.pyapi.decref(kwargs)
        c.pyapi.decref(nnkd__ykzh)
    c.pyapi.decref(ekb__xama)
    c.pyapi.decref(cdx__nygm)
    c.pyapi.decref(waat__ahih)
    c.pyapi.decref(xxqde__ytrnm)
    c.pyapi.decref(wlp__fuu)
    c.pyapi.decref(ysn__shccf)
    c.pyapi.decref(yae__hkhe)
    c.pyapi.decref(lbqoz__btump)
    return res


@intrinsic
def init_timestamp(typingctx, year, month, day, hour, minute, second,
    microsecond, nanosecond, value, tz):

    def codegen(context, builder, sig, args):
        (year, month, day, hour, minute, second, fyzdl__djb, oaqu__eyvjg,
            value, fxnoj__gvre) = args
        ts = cgutils.create_struct_proxy(sig.return_type)(context, builder)
        ts.year = year
        ts.month = month
        ts.day = day
        ts.hour = hour
        ts.minute = minute
        ts.second = second
        ts.microsecond = fyzdl__djb
        ts.nanosecond = oaqu__eyvjg
        ts.value = value
        return ts._getvalue()
    if is_overload_none(tz):
        typ = pd_timestamp_type
    elif is_overload_constant_str(tz):
        typ = PandasTimestampType(get_overload_const_str(tz))
    elif is_overload_constant_int(tz):
        typ = PandasTimestampType(get_overload_const_int(tz))
    else:
        raise_bodo_error('tz must be a constant string, int, or None')
    return typ(types.int64, types.int64, types.int64, types.int64, types.
        int64, types.int64, types.int64, types.int64, types.int64, tz), codegen


@numba.generated_jit
def zero_if_none(value):
    if value == types.none:
        return lambda value: 0
    return lambda value: value


@lower_constant(PandasTimestampType)
def constant_timestamp(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    nanosecond = context.get_constant(types.int64, pyval.nanosecond)
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct((year, month, day, hour, minute,
        second, microsecond, nanosecond, value))


@overload(pd.Timestamp, no_unliteral=True)
def overload_pd_timestamp(ts_input=_no_input, freq=None, tz=None, unit=None,
    year=None, month=None, day=None, hour=None, minute=None, second=None,
    microsecond=None, nanosecond=None, tzinfo=None):
    if not is_overload_none(tz) and is_overload_constant_str(tz
        ) and get_overload_const_str(tz) not in pytz.all_timezones_set:
        raise BodoError(
            "pandas.Timestamp(): 'tz', if provided, must be constant string found in pytz.all_timezones"
            )
    if ts_input == _no_input or getattr(ts_input, 'value', None) == _no_input:

        def impl_kw(ts_input=_no_input, freq=None, tz=None, unit=None, year
            =None, month=None, day=None, hour=None, minute=None, second=
            None, microsecond=None, nanosecond=None, tzinfo=None):
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value, tz)
        return impl_kw
    if isinstance(types.unliteral(freq), types.Integer):

        def impl_pos(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            value = npy_datetimestruct_to_datetime(ts_input, freq, tz,
                zero_if_none(unit), zero_if_none(year), zero_if_none(month),
                zero_if_none(day))
            value += zero_if_none(hour)
            return init_timestamp(ts_input, freq, tz, zero_if_none(unit),
                zero_if_none(year), zero_if_none(month), zero_if_none(day),
                zero_if_none(hour), value, None)
        return impl_pos
    if isinstance(ts_input, types.Number):
        if is_overload_none(unit):
            unit = 'ns'
        if not is_overload_constant_str(unit):
            raise BodoError(
                'pandas.Timedelta(): unit argument must be a constant str')
        unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
            get_overload_const_str(unit))
        cthw__blp, precision = pd._libs.tslibs.conversion.precision_from_unit(
            unit)
        if isinstance(ts_input, types.Integer):

            def impl_int(ts_input=_no_input, freq=None, tz=None, unit=None,
                year=None, month=None, day=None, hour=None, minute=None,
                second=None, microsecond=None, nanosecond=None, tzinfo=None):
                value = ts_input * cthw__blp
                return convert_val_to_timestamp(value, tz)
            return impl_int

        def impl_float(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            gknsy__ewia = np.int64(ts_input)
            lrsf__tobh = ts_input - gknsy__ewia
            if precision:
                lrsf__tobh = np.round(lrsf__tobh, precision)
            value = gknsy__ewia * cthw__blp + np.int64(lrsf__tobh * cthw__blp)
            return convert_val_to_timestamp(value, tz)
        return impl_float
    if ts_input == bodo.string_type or is_overload_constant_str(ts_input):
        types.pd_timestamp_type = pd_timestamp_type
        if is_overload_none(tz):
            tz_val = None
        elif is_overload_constant_str(tz):
            tz_val = get_overload_const_str(tz)
        else:
            raise_bodo_error(
                'pandas.Timestamp(): tz argument must be a constant string or None'
                )
        typ = PandasTimestampType(tz_val)

        def impl_str(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            with numba.objmode(res=typ):
                res = pd.Timestamp(ts_input, tz=tz)
            return res
        return impl_str
    if ts_input == pd_timestamp_type:
        return (lambda ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None: ts_input)
    if ts_input == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:

        def impl_datetime(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            year = ts_input.year
            month = ts_input.month
            day = ts_input.day
            hour = ts_input.hour
            minute = ts_input.minute
            second = ts_input.second
            microsecond = ts_input.microsecond
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value, tz)
        return impl_datetime
    if ts_input == bodo.hiframes.datetime_date_ext.datetime_date_type:

        def impl_date(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            year = ts_input.year
            month = ts_input.month
            day = ts_input.day
            value = npy_datetimestruct_to_datetime(year, month, day,
                zero_if_none(hour), zero_if_none(minute), zero_if_none(
                second), zero_if_none(microsecond))
            value += zero_if_none(nanosecond)
            return init_timestamp(year, month, day, zero_if_none(hour),
                zero_if_none(minute), zero_if_none(second), zero_if_none(
                microsecond), zero_if_none(nanosecond), value, None)
        return impl_date
    if isinstance(ts_input, numba.core.types.scalars.NPDatetime):
        cthw__blp, precision = pd._libs.tslibs.conversion.precision_from_unit(
            ts_input.unit)

        def impl_date(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            value = np.int64(ts_input) * cthw__blp
            return convert_datetime64_to_timestamp(integer_to_dt64(value))
        return impl_date


@overload_attribute(PandasTimestampType, 'dayofyear')
@overload_attribute(PandasTimestampType, 'day_of_year')
def overload_pd_dayofyear(ptt):

    def pd_dayofyear(ptt):
        return get_day_of_year(ptt.year, ptt.month, ptt.day)
    return pd_dayofyear


@overload_method(PandasTimestampType, 'weekday')
@overload_attribute(PandasTimestampType, 'dayofweek')
@overload_attribute(PandasTimestampType, 'day_of_week')
def overload_pd_dayofweek(ptt):

    def pd_dayofweek(ptt):
        return get_day_of_week(ptt.year, ptt.month, ptt.day)
    return pd_dayofweek


@overload_attribute(PandasTimestampType, 'week')
@overload_attribute(PandasTimestampType, 'weekofyear')
def overload_week_number(ptt):

    def pd_week_number(ptt):
        fxnoj__gvre, lqlib__bjtf, fxnoj__gvre = get_isocalendar(ptt.year,
            ptt.month, ptt.day)
        return lqlib__bjtf
    return pd_week_number


@overload_method(PandasTimestampType, '__hash__', no_unliteral=True)
def dt64_hash(val):
    return lambda val: hash(val.value)


@overload_attribute(PandasTimestampType, 'days_in_month')
@overload_attribute(PandasTimestampType, 'daysinmonth')
def overload_pd_daysinmonth(ptt):

    def pd_daysinmonth(ptt):
        return get_days_in_month(ptt.year, ptt.month)
    return pd_daysinmonth


@overload_attribute(PandasTimestampType, 'is_leap_year')
def overload_pd_is_leap_year(ptt):

    def pd_is_leap_year(ptt):
        return is_leap_year(ptt.year)
    return pd_is_leap_year


@overload_attribute(PandasTimestampType, 'is_month_start')
def overload_pd_is_month_start(ptt):

    def pd_is_month_start(ptt):
        return ptt.day == 1
    return pd_is_month_start


@overload_attribute(PandasTimestampType, 'is_month_end')
def overload_pd_is_month_end(ptt):

    def pd_is_month_end(ptt):
        return ptt.day == get_days_in_month(ptt.year, ptt.month)
    return pd_is_month_end


@overload_attribute(PandasTimestampType, 'is_quarter_start')
def overload_pd_is_quarter_start(ptt):

    def pd_is_quarter_start(ptt):
        return ptt.day == 1 and ptt.month % 3 == 1
    return pd_is_quarter_start


@overload_attribute(PandasTimestampType, 'is_quarter_end')
def overload_pd_is_quarter_end(ptt):

    def pd_is_quarter_end(ptt):
        return ptt.month % 3 == 0 and ptt.day == get_days_in_month(ptt.year,
            ptt.month)
    return pd_is_quarter_end


@overload_attribute(PandasTimestampType, 'is_year_start')
def overload_pd_is_year_start(ptt):

    def pd_is_year_start(ptt):
        return ptt.day == 1 and ptt.month == 1
    return pd_is_year_start


@overload_attribute(PandasTimestampType, 'is_year_end')
def overload_pd_is_year_end(ptt):

    def pd_is_year_end(ptt):
        return ptt.day == 31 and ptt.month == 12
    return pd_is_year_end


@overload_attribute(PandasTimestampType, 'quarter')
def overload_quarter(ptt):

    def quarter(ptt):
        return (ptt.month - 1) // 3 + 1
    return quarter


@overload_method(PandasTimestampType, 'date', no_unliteral=True)
def overload_pd_timestamp_date(ptt):

    def pd_timestamp_date_impl(ptt):
        return datetime.date(ptt.year, ptt.month, ptt.day)
    return pd_timestamp_date_impl


@overload_method(PandasTimestampType, 'isocalendar', no_unliteral=True)
def overload_pd_timestamp_isocalendar(ptt):

    def impl(ptt):
        year, lqlib__bjtf, wqv__zybzi = get_isocalendar(ptt.year, ptt.month,
            ptt.day)
        return year, lqlib__bjtf, wqv__zybzi
    return impl


@overload_method(PandasTimestampType, 'isoformat', no_unliteral=True)
def overload_pd_timestamp_isoformat(ts, sep=None):
    if is_overload_none(sep):

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            cyfdw__qqkqz = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + 'T' + cyfdw__qqkqz
            return res
        return timestamp_isoformat_impl
    else:

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            cyfdw__qqkqz = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + sep + cyfdw__qqkqz
            return res
    return timestamp_isoformat_impl


@overload_method(PandasTimestampType, 'normalize', no_unliteral=True)
def overload_pd_timestamp_normalize(ptt):

    def impl(ptt):
        return pd.Timestamp(year=ptt.year, month=ptt.month, day=ptt.day)
    return impl


@overload_method(PandasTimestampType, 'day_name', no_unliteral=True)
def overload_pd_timestamp_day_name(ptt, locale=None):
    slrsh__ppu = dict(locale=locale)
    eac__jsld = dict(locale=None)
    check_unsupported_args('Timestamp.day_name', slrsh__ppu, eac__jsld,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        azv__ckza = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'Saturday', 'Sunday')
        fxnoj__gvre, fxnoj__gvre, vwz__iqp = ptt.isocalendar()
        return azv__ckza[vwz__iqp - 1]
    return impl


@overload_method(PandasTimestampType, 'month_name', no_unliteral=True)
def overload_pd_timestamp_month_name(ptt, locale=None):
    slrsh__ppu = dict(locale=locale)
    eac__jsld = dict(locale=None)
    check_unsupported_args('Timestamp.month_name', slrsh__ppu, eac__jsld,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        ybdd__tuczp = ('January', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November',
            'December')
        return ybdd__tuczp[ptt.month - 1]
    return impl


@overload_method(PandasTimestampType, 'tz_convert', no_unliteral=True)
def overload_pd_timestamp_tz_convert(ptt, tz):
    if ptt.tz is None:
        raise BodoError(
            'Cannot convert tz-naive Timestamp, use tz_localize to localize')
    if is_overload_none(tz):
        return lambda ptt, tz: convert_val_to_timestamp(ptt.value)
    elif is_overload_constant_str(tz):
        return lambda ptt, tz: convert_val_to_timestamp(ptt.value, tz=tz)


@overload_method(PandasTimestampType, 'tz_localize', no_unliteral=True)
def overload_pd_timestamp_tz_localize(ptt, tz, ambiguous='raise',
    nonexistent='raise'):
    if ptt.tz is not None and not is_overload_none(tz):
        raise BodoError(
            'Cannot localize tz-aware Timestamp, use tz_convert for conversions'
            )
    slrsh__ppu = dict(ambiguous=ambiguous, nonexistent=nonexistent)
    sal__rxl = dict(ambiguous='raise', nonexistent='raise')
    check_unsupported_args('Timestamp.tz_localize', slrsh__ppu, sal__rxl,
        package_name='pandas', module_name='Timestamp')
    if is_overload_none(tz):
        return (lambda ptt, tz, ambiguous='raise', nonexistent='raise':
            convert_val_to_timestamp(ptt.value, is_convert=False))
    elif is_overload_constant_str(tz):
        return (lambda ptt, tz, ambiguous='raise', nonexistent='raise':
            convert_val_to_timestamp(ptt.value, tz=tz, is_convert=False))


@numba.njit
def str_2d(a):
    res = str(a)
    if len(res) == 1:
        return '0' + res
    return res


@overload(str, no_unliteral=True)
def ts_str_overload(a):
    if a == pd_timestamp_type:
        return lambda a: a.isoformat(' ')


@intrinsic
def extract_year_days(typingctx, dt64_t=None):
    assert dt64_t in (types.int64, types.NPDatetime('ns'))

    def codegen(context, builder, sig, args):
        pnf__bblxn = cgutils.alloca_once(builder, lir.IntType(64))
        builder.store(args[0], pnf__bblxn)
        year = cgutils.alloca_once(builder, lir.IntType(64))
        vnc__vvu = cgutils.alloca_once(builder, lir.IntType(64))
        xrqol__cqlgq = lir.FunctionType(lir.VoidType(), [lir.IntType(64).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        jmwf__ljnbf = cgutils.get_or_insert_function(builder.module,
            xrqol__cqlgq, name='extract_year_days')
        builder.call(jmwf__ljnbf, [pnf__bblxn, year, vnc__vvu])
        return cgutils.pack_array(builder, [builder.load(pnf__bblxn),
            builder.load(year), builder.load(vnc__vvu)])
    return types.Tuple([types.int64, types.int64, types.int64])(dt64_t
        ), codegen


@intrinsic
def get_month_day(typingctx, year_t, days_t=None):
    assert year_t == types.int64
    assert days_t == types.int64

    def codegen(context, builder, sig, args):
        month = cgutils.alloca_once(builder, lir.IntType(64))
        day = cgutils.alloca_once(builder, lir.IntType(64))
        xrqol__cqlgq = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
            lir.IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        jmwf__ljnbf = cgutils.get_or_insert_function(builder.module,
            xrqol__cqlgq, name='get_month_day')
        builder.call(jmwf__ljnbf, [args[0], args[1], month, day])
        return cgutils.pack_array(builder, [builder.load(month), builder.
            load(day)])
    return types.Tuple([types.int64, types.int64])(types.int64, types.int64
        ), codegen


@register_jitable
def get_day_of_year(year, month, day):
    xio__esg = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365,
        0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    sbbjl__rupm = is_leap_year(year)
    lcd__dmbge = xio__esg[sbbjl__rupm * 13 + month - 1]
    sebut__acn = lcd__dmbge + day
    return sebut__acn


@register_jitable
def get_day_of_week(y, m, d):
    nlhlr__bit = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    y -= m < 3
    day = (y + y // 4 - y // 100 + y // 400 + nlhlr__bit[m - 1] + d) % 7
    return (day + 6) % 7


@register_jitable
def get_days_in_month(year, month):
    is_leap_year = year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)
    dobkv__gamz = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 29, 
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return dobkv__gamz[12 * is_leap_year + month - 1]


@register_jitable
def is_leap_year(year):
    return year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)


@numba.generated_jit(nopython=True)
def convert_val_to_timestamp(ts_input, tz=None, is_convert=True):
    znv__kaf = sosmt__zdvq = np.array([])
    jjqct__bmgv = '0'
    if is_overload_constant_str(tz):
        lsdux__jzg = get_overload_const_str(tz)
        nnkd__ykzh = pytz.timezone(lsdux__jzg)
        if isinstance(nnkd__ykzh, pytz.tzinfo.DstTzInfo):
            znv__kaf = np.array(nnkd__ykzh._utc_transition_times, dtype=
                'M8[ns]').view('i8')
            sosmt__zdvq = np.array(nnkd__ykzh._transition_info)[:, 0]
            sosmt__zdvq = (pd.Series(sosmt__zdvq).dt.total_seconds() * 
                1000000000).astype(np.int64).values
            jjqct__bmgv = (
                "deltas[np.searchsorted(trans, ts_input, side='right') - 1]")
        else:
            sosmt__zdvq = np.int64(nnkd__ykzh._utcoffset.total_seconds() * 
                1000000000)
            jjqct__bmgv = 'deltas'
    elif is_overload_constant_int(tz):
        iwi__yze = get_overload_const_int(tz)
        jjqct__bmgv = str(iwi__yze)
    elif not is_overload_none(tz):
        raise_bodo_error(
            'convert_val_to_timestamp(): tz value must be a constant string or None'
            )
    is_convert = get_overload_const_bool(is_convert)
    if is_convert:
        nup__wdz = 'tz_ts_input'
        hkf__gdss = 'ts_input'
    else:
        nup__wdz = 'ts_input'
        hkf__gdss = 'tz_ts_input'
    zlpw__zbvw = 'def impl(ts_input, tz=None, is_convert=True):\n'
    zlpw__zbvw += f'  tz_ts_input = ts_input + {jjqct__bmgv}\n'
    zlpw__zbvw += (
        f'  dt, year, days = extract_year_days(integer_to_dt64({nup__wdz}))\n')
    zlpw__zbvw += '  month, day = get_month_day(year, days)\n'
    zlpw__zbvw += '  return init_timestamp(\n'
    zlpw__zbvw += '    year=year,\n'
    zlpw__zbvw += '    month=month,\n'
    zlpw__zbvw += '    day=day,\n'
    zlpw__zbvw += '    hour=dt // (60 * 60 * 1_000_000_000),\n'
    zlpw__zbvw += '    minute=(dt // (60 * 1_000_000_000)) % 60,\n'
    zlpw__zbvw += '    second=(dt // 1_000_000_000) % 60,\n'
    zlpw__zbvw += '    microsecond=(dt // 1000) % 1_000_000,\n'
    zlpw__zbvw += '    nanosecond=dt % 1000,\n'
    zlpw__zbvw += f'    value={hkf__gdss},\n'
    zlpw__zbvw += '    tz=tz,\n'
    zlpw__zbvw += '  )\n'
    pqoa__awiu = {}
    exec(zlpw__zbvw, {'np': np, 'pd': pd, 'trans': znv__kaf, 'deltas':
        sosmt__zdvq, 'integer_to_dt64': integer_to_dt64,
        'extract_year_days': extract_year_days, 'get_month_day':
        get_month_day, 'init_timestamp': init_timestamp, 'zero_if_none':
        zero_if_none}, pqoa__awiu)
    impl = pqoa__awiu['impl']
    return impl


@numba.njit(no_cpython_wrapper=True)
def convert_datetime64_to_timestamp(dt64):
    pnf__bblxn, year, vnc__vvu = extract_year_days(dt64)
    month, day = get_month_day(year, vnc__vvu)
    return init_timestamp(year=year, month=month, day=day, hour=pnf__bblxn //
        (60 * 60 * 1000000000), minute=pnf__bblxn // (60 * 1000000000) % 60,
        second=pnf__bblxn // 1000000000 % 60, microsecond=pnf__bblxn // 
        1000 % 1000000, nanosecond=pnf__bblxn % 1000, value=dt64, tz=None)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_datetime_timedelta(dt64):
    zrp__wky = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    qvf__cxoo = zrp__wky // (86400 * 1000000000)
    cle__gsozc = zrp__wky - qvf__cxoo * 86400 * 1000000000
    supse__xinq = cle__gsozc // 1000000000
    qhzcs__oxnr = cle__gsozc - supse__xinq * 1000000000
    xuc__svd = qhzcs__oxnr // 1000
    return datetime.timedelta(qvf__cxoo, supse__xinq, xuc__svd)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_pd_timedelta(dt64):
    zrp__wky = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    return pd.Timedelta(zrp__wky)


@intrinsic
def integer_to_timedelta64(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.NPTimedelta('ns')(val), codegen


@intrinsic
def integer_to_dt64(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.NPDatetime('ns')(val), codegen


@intrinsic
def dt64_to_integer(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.int64(val), codegen


@lower_cast(types.NPDatetime('ns'), types.int64)
def cast_dt64_to_integer(context, builder, fromty, toty, val):
    return val


@overload_method(types.NPDatetime, '__hash__', no_unliteral=True)
def dt64_hash(val):
    return lambda val: hash(dt64_to_integer(val))


@overload_method(types.NPTimedelta, '__hash__', no_unliteral=True)
def td64_hash(val):
    return lambda val: hash(dt64_to_integer(val))


@intrinsic
def timedelta64_to_integer(typingctx, val=None):

    def codegen(context, builder, sig, args):
        return args[0]
    return types.int64(val), codegen


@lower_cast(bodo.timedelta64ns, types.int64)
def cast_td64_to_integer(context, builder, fromty, toty, val):
    return val


@numba.njit
def parse_datetime_str(val):
    with numba.objmode(res='int64'):
        res = pd.Timestamp(val).value
    return integer_to_dt64(res)


@numba.njit
def datetime_timedelta_to_timedelta64(val):
    with numba.objmode(res='NPTimedelta("ns")'):
        res = pd.to_timedelta(val)
        res = res.to_timedelta64()
    return res


@numba.njit
def series_str_dt64_astype(data):
    with numba.objmode(res="NPDatetime('ns')[::1]"):
        res = pd.Series(data).astype('datetime64[ns]').values
    return res


@numba.njit
def series_str_td64_astype(data):
    with numba.objmode(res="NPTimedelta('ns')[::1]"):
        res = data.astype('timedelta64[ns]')
    return res


@numba.njit
def datetime_datetime_to_dt64(val):
    with numba.objmode(res='NPDatetime("ns")'):
        res = np.datetime64(val).astype('datetime64[ns]')
    return res


@register_jitable
def datetime_date_arr_to_dt64_arr(arr):
    with numba.objmode(res='NPDatetime("ns")[::1]'):
        res = np.array(arr, dtype='datetime64[ns]')
    return res


types.pd_timestamp_type = pd_timestamp_type


@register_jitable
def to_datetime_scalar(a, errors='raise', dayfirst=False, yearfirst=False,
    utc=None, format=None, exact=True, unit=None, infer_datetime_format=
    False, origin='unix', cache=True):
    with numba.objmode(t='pd_timestamp_type'):
        t = pd.to_datetime(a, errors=errors, dayfirst=dayfirst, yearfirst=
            yearfirst, utc=utc, format=format, exact=exact, unit=unit,
            infer_datetime_format=infer_datetime_format, origin=origin,
            cache=cache)
    return t


@numba.njit
def pandas_string_array_to_datetime(arr, errors, dayfirst, yearfirst, utc,
    format, exact, unit, infer_datetime_format, origin, cache):
    with numba.objmode(result='datetime_index'):
        result = pd.to_datetime(arr, errors=errors, dayfirst=dayfirst,
            yearfirst=yearfirst, utc=utc, format=format, exact=exact, unit=
            unit, infer_datetime_format=infer_datetime_format, origin=
            origin, cache=cache)
    return result


@numba.njit
def pandas_dict_string_array_to_datetime(arr, errors, dayfirst, yearfirst,
    utc, format, exact, unit, infer_datetime_format, origin, cache):
    hdr__gvtwg = len(arr)
    fml__qeq = np.empty(hdr__gvtwg, 'datetime64[ns]')
    lmiv__kubi = arr._indices
    eff__nsnl = pandas_string_array_to_datetime(arr._data, errors, dayfirst,
        yearfirst, utc, format, exact, unit, infer_datetime_format, origin,
        cache).values
    for gruxe__uuen in range(hdr__gvtwg):
        if bodo.libs.array_kernels.isna(lmiv__kubi, gruxe__uuen):
            bodo.libs.array_kernels.setna(fml__qeq, gruxe__uuen)
            continue
        fml__qeq[gruxe__uuen] = eff__nsnl[lmiv__kubi[gruxe__uuen]]
    return fml__qeq


@overload(pd.to_datetime, inline='always', no_unliteral=True)
def overload_to_datetime(arg_a, errors='raise', dayfirst=False, yearfirst=
    False, utc=None, format=None, exact=True, unit=None,
    infer_datetime_format=False, origin='unix', cache=True):
    if arg_a == bodo.string_type or is_overload_constant_str(arg_a
        ) or is_overload_constant_int(arg_a) or isinstance(arg_a, types.Integer
        ):

        def pd_to_datetime_impl(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return to_datetime_scalar(arg_a, errors=errors, dayfirst=
                dayfirst, yearfirst=yearfirst, utc=utc, format=format,
                exact=exact, unit=unit, infer_datetime_format=
                infer_datetime_format, origin=origin, cache=cache)
        return pd_to_datetime_impl
    if isinstance(arg_a, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            zgbot__atxqx = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            tjk__xva = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            xdxtt__lkv = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_datetime(arr, errors=errors, dayfirst=dayfirst,
                yearfirst=yearfirst, utc=utc, format=format, exact=exact,
                unit=unit, infer_datetime_format=infer_datetime_format,
                origin=origin, cache=cache))
            return bodo.hiframes.pd_series_ext.init_series(xdxtt__lkv,
                zgbot__atxqx, tjk__xva)
        return impl_series
    if arg_a == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        dplnv__ygl = np.dtype('datetime64[ns]')
        iNaT = pd._libs.tslibs.iNaT

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            hdr__gvtwg = len(arg_a)
            fml__qeq = np.empty(hdr__gvtwg, dplnv__ygl)
            for gruxe__uuen in numba.parfors.parfor.internal_prange(hdr__gvtwg
                ):
                val = iNaT
                if not bodo.libs.array_kernels.isna(arg_a, gruxe__uuen):
                    data = arg_a[gruxe__uuen]
                    val = (bodo.hiframes.pd_timestamp_ext.
                        npy_datetimestruct_to_datetime(data.year, data.
                        month, data.day, 0, 0, 0, 0))
                fml__qeq[gruxe__uuen
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(fml__qeq,
                None)
        return impl_date_arr
    if arg_a == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return (lambda arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True: bodo.
            hiframes.pd_index_ext.init_datetime_index(arg_a, None))
    if arg_a == string_array_type:

        def impl_string_array(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return pandas_string_array_to_datetime(arg_a, errors, dayfirst,
                yearfirst, utc, format, exact, unit, infer_datetime_format,
                origin, cache)
        return impl_string_array
    if isinstance(arg_a, types.Array) and isinstance(arg_a.dtype, types.Integer
        ):
        dplnv__ygl = np.dtype('datetime64[ns]')

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            hdr__gvtwg = len(arg_a)
            fml__qeq = np.empty(hdr__gvtwg, dplnv__ygl)
            for gruxe__uuen in numba.parfors.parfor.internal_prange(hdr__gvtwg
                ):
                data = arg_a[gruxe__uuen]
                val = to_datetime_scalar(data, errors=errors, dayfirst=
                    dayfirst, yearfirst=yearfirst, utc=utc, format=format,
                    exact=exact, unit=unit, infer_datetime_format=
                    infer_datetime_format, origin=origin, cache=cache)
                fml__qeq[gruxe__uuen
                    ] = bodo.hiframes.pd_timestamp_ext.datetime_datetime_to_dt64(
                    val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(fml__qeq,
                None)
        return impl_date_arr
    if isinstance(arg_a, CategoricalArrayType
        ) and arg_a.dtype.elem_type == bodo.string_type:
        dplnv__ygl = np.dtype('datetime64[ns]')

        def impl_cat_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            hdr__gvtwg = len(arg_a)
            fml__qeq = np.empty(hdr__gvtwg, dplnv__ygl)
            mwxe__ueuvq = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arg_a))
            eff__nsnl = pandas_string_array_to_datetime(arg_a.dtype.
                categories.values, errors, dayfirst, yearfirst, utc, format,
                exact, unit, infer_datetime_format, origin, cache).values
            for gruxe__uuen in numba.parfors.parfor.internal_prange(hdr__gvtwg
                ):
                c = mwxe__ueuvq[gruxe__uuen]
                if c == -1:
                    bodo.libs.array_kernels.setna(fml__qeq, gruxe__uuen)
                    continue
                fml__qeq[gruxe__uuen] = eff__nsnl[c]
            return bodo.hiframes.pd_index_ext.init_datetime_index(fml__qeq,
                None)
        return impl_cat_arr
    if arg_a == bodo.dict_str_arr_type:

        def impl_dict_str_arr(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            fml__qeq = pandas_dict_string_array_to_datetime(arg_a, errors,
                dayfirst, yearfirst, utc, format, exact, unit,
                infer_datetime_format, origin, cache)
            return bodo.hiframes.pd_index_ext.init_datetime_index(fml__qeq,
                None)
        return impl_dict_str_arr
    if isinstance(arg_a, PandasTimestampType):

        def impl_timestamp(arg_a, errors='raise', dayfirst=False, yearfirst
            =False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            return arg_a
        return impl_timestamp
    raise_bodo_error(f'pd.to_datetime(): cannot convert date type {arg_a}')


@overload(pd.to_timedelta, inline='always', no_unliteral=True)
def overload_to_timedelta(arg_a, unit='ns', errors='raise'):
    if not is_overload_constant_str(unit):
        raise BodoError(
            'pandas.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    if isinstance(arg_a, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(arg_a, unit='ns', errors='raise'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            zgbot__atxqx = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            tjk__xva = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            xdxtt__lkv = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_timedelta(arr, unit, errors))
            return bodo.hiframes.pd_series_ext.init_series(xdxtt__lkv,
                zgbot__atxqx, tjk__xva)
        return impl_series
    if is_overload_constant_str(arg_a) or arg_a in (pd_timedelta_type,
        datetime_timedelta_type, bodo.string_type):

        def impl_string(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a)
        return impl_string
    if isinstance(arg_a, types.Float):
        m, lulda__adhew = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_float_scalar(arg_a, unit='ns', errors='raise'):
            val = float_to_timedelta_val(arg_a, lulda__adhew, m)
            return pd.Timedelta(val)
        return impl_float_scalar
    if isinstance(arg_a, types.Integer):
        m, fxnoj__gvre = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_integer_scalar(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a * m)
        return impl_integer_scalar
    if is_iterable_type(arg_a) and not isinstance(arg_a, types.BaseTuple):
        m, lulda__adhew = pd._libs.tslibs.conversion.precision_from_unit(unit)
        iwfe__hof = np.dtype('timedelta64[ns]')
        if isinstance(arg_a.dtype, types.Float):

            def impl_float(arg_a, unit='ns', errors='raise'):
                hdr__gvtwg = len(arg_a)
                fml__qeq = np.empty(hdr__gvtwg, iwfe__hof)
                for gruxe__uuen in numba.parfors.parfor.internal_prange(
                    hdr__gvtwg):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, gruxe__uuen):
                        val = float_to_timedelta_val(arg_a[gruxe__uuen],
                            lulda__adhew, m)
                    fml__qeq[gruxe__uuen
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(fml__qeq
                    , None)
            return impl_float
        if isinstance(arg_a.dtype, types.Integer):

            def impl_int(arg_a, unit='ns', errors='raise'):
                hdr__gvtwg = len(arg_a)
                fml__qeq = np.empty(hdr__gvtwg, iwfe__hof)
                for gruxe__uuen in numba.parfors.parfor.internal_prange(
                    hdr__gvtwg):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, gruxe__uuen):
                        val = arg_a[gruxe__uuen] * m
                    fml__qeq[gruxe__uuen
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(fml__qeq
                    , None)
            return impl_int
        if arg_a.dtype == bodo.timedelta64ns:

            def impl_td64(arg_a, unit='ns', errors='raise'):
                arr = bodo.utils.conversion.coerce_to_ndarray(arg_a)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(arr,
                    None)
            return impl_td64
        if arg_a.dtype == bodo.string_type or isinstance(arg_a.dtype, types
            .UnicodeCharSeq):

            def impl_str(arg_a, unit='ns', errors='raise'):
                return pandas_string_array_to_timedelta(arg_a, unit, errors)
            return impl_str
        if arg_a.dtype == datetime_timedelta_type:

            def impl_datetime_timedelta(arg_a, unit='ns', errors='raise'):
                hdr__gvtwg = len(arg_a)
                fml__qeq = np.empty(hdr__gvtwg, iwfe__hof)
                for gruxe__uuen in numba.parfors.parfor.internal_prange(
                    hdr__gvtwg):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, gruxe__uuen):
                        mfvu__yyipn = arg_a[gruxe__uuen]
                        val = (mfvu__yyipn.microseconds + 1000 * 1000 * (
                            mfvu__yyipn.seconds + 24 * 60 * 60 *
                            mfvu__yyipn.days)) * 1000
                    fml__qeq[gruxe__uuen
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(fml__qeq
                    , None)
            return impl_datetime_timedelta
    raise_bodo_error(
        f'pd.to_timedelta(): cannot convert date type {arg_a.dtype}')


@register_jitable
def float_to_timedelta_val(data, precision, multiplier):
    gknsy__ewia = np.int64(data)
    lrsf__tobh = data - gknsy__ewia
    if precision:
        lrsf__tobh = np.round(lrsf__tobh, precision)
    return gknsy__ewia * multiplier + np.int64(lrsf__tobh * multiplier)


@numba.njit
def pandas_string_array_to_timedelta(arg_a, unit='ns', errors='raise'):
    with numba.objmode(result='timedelta_index'):
        result = pd.to_timedelta(arg_a, errors=errors)
    return result


def create_timestamp_cmp_op_overload(op):

    def overload_date_timestamp_cmp(lhs, rhs):
        if (lhs == pd_timestamp_type and rhs == bodo.hiframes.
            datetime_date_ext.datetime_date_type):
            return lambda lhs, rhs: op(lhs.value, bodo.hiframes.
                pd_timestamp_ext.npy_datetimestruct_to_datetime(rhs.year,
                rhs.month, rhs.day, 0, 0, 0, 0))
        if (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and 
            rhs == pd_timestamp_type):
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                npy_datetimestruct_to_datetime(lhs.year, lhs.month, lhs.day,
                0, 0, 0, 0), rhs.value)
        if lhs == pd_timestamp_type and rhs == pd_timestamp_type:
            return lambda lhs, rhs: op(lhs.value, rhs.value)
        if lhs == pd_timestamp_type and rhs == bodo.datetime64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_dt64(lhs.value), rhs)
        if lhs == bodo.datetime64ns and rhs == pd_timestamp_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_dt64(rhs.value))
    return overload_date_timestamp_cmp


@overload_method(PandasTimestampType, 'toordinal', no_unliteral=True)
def toordinal(date):

    def impl(date):
        return _ymd2ord(date.year, date.month, date.day)
    return impl


def overload_freq_methods(method):

    def freq_overload(td, freq, ambiguous='raise', nonexistent='raise'):
        check_tz_aware_unsupported(td, f'Timestamp.{method}()')
        slrsh__ppu = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        yoc__dfp = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Timestamp.{method}', slrsh__ppu, yoc__dfp,
            package_name='pandas', module_name='Timestamp')
        ublzv__uyl = ["freq == 'D'", "freq == 'H'",
            "freq == 'min' or freq == 'T'", "freq == 'S'",
            "freq == 'ms' or freq == 'L'", "freq == 'U' or freq == 'us'",
            "freq == 'N'"]
        trvk__tdpee = [24 * 60 * 60 * 1000000 * 1000, 60 * 60 * 1000000 * 
            1000, 60 * 1000000 * 1000, 1000000 * 1000, 1000 * 1000, 1000, 1]
        zlpw__zbvw = (
            "def impl(td, freq, ambiguous='raise', nonexistent='raise'):\n")
        for gruxe__uuen, sdcj__ozgf in enumerate(ublzv__uyl):
            degeo__vnc = 'if' if gruxe__uuen == 0 else 'elif'
            zlpw__zbvw += '    {} {}:\n'.format(degeo__vnc, sdcj__ozgf)
            zlpw__zbvw += '        unit_value = {}\n'.format(trvk__tdpee[
                gruxe__uuen])
        zlpw__zbvw += '    else:\n'
        zlpw__zbvw += (
            "        raise ValueError('Incorrect Frequency specification')\n")
        if td == pd_timedelta_type:
            zlpw__zbvw += (
                """    return pd.Timedelta(unit_value * np.int64(np.{}(td.value / unit_value)))
"""
                .format(method))
        elif td == pd_timestamp_type:
            if method == 'ceil':
                zlpw__zbvw += (
                    '    value = td.value + np.remainder(-td.value, unit_value)\n'
                    )
            if method == 'floor':
                zlpw__zbvw += (
                    '    value = td.value - np.remainder(td.value, unit_value)\n'
                    )
            if method == 'round':
                zlpw__zbvw += '    if unit_value == 1:\n'
                zlpw__zbvw += '        value = td.value\n'
                zlpw__zbvw += '    else:\n'
                zlpw__zbvw += (
                    '        quotient, remainder = np.divmod(td.value, unit_value)\n'
                    )
                zlpw__zbvw += """        mask = np.logical_or(remainder > (unit_value // 2), np.logical_and(remainder == (unit_value // 2), quotient % 2))
"""
                zlpw__zbvw += '        if mask:\n'
                zlpw__zbvw += '            quotient = quotient + 1\n'
                zlpw__zbvw += '        value = quotient * unit_value\n'
            zlpw__zbvw += '    return pd.Timestamp(value)\n'
        pqoa__awiu = {}
        exec(zlpw__zbvw, {'np': np, 'pd': pd}, pqoa__awiu)
        impl = pqoa__awiu['impl']
        return impl
    return freq_overload


def _install_freq_methods():
    cpov__pdqxi = ['ceil', 'floor', 'round']
    for method in cpov__pdqxi:
        accsa__brht = overload_freq_methods(method)
        overload_method(PDTimeDeltaType, method, no_unliteral=True)(accsa__brht
            )
        overload_method(PandasTimestampType, method, no_unliteral=True)(
            accsa__brht)


_install_freq_methods()


@register_jitable
def compute_pd_timestamp(totmicrosec, nanosecond):
    microsecond = totmicrosec % 1000000
    lhtrc__thd = totmicrosec // 1000000
    second = lhtrc__thd % 60
    fgi__nnz = lhtrc__thd // 60
    minute = fgi__nnz % 60
    xibb__yswc = fgi__nnz // 60
    hour = xibb__yswc % 24
    pimat__jkqd = xibb__yswc // 24
    year, month, day = _ord2ymd(pimat__jkqd)
    value = npy_datetimestruct_to_datetime(year, month, day, hour, minute,
        second, microsecond)
    value += zero_if_none(nanosecond)
    return init_timestamp(year, month, day, hour, minute, second,
        microsecond, nanosecond, value, None)


def overload_sub_operator_timestamp(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            zveko__xoc = lhs.toordinal()
            zcvlp__ybiis = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ksb__rymg = lhs.microsecond
            nanosecond = lhs.nanosecond
            itx__mhqbm = rhs.days
            pmtg__zlp = rhs.seconds
            cis__mntqe = rhs.microseconds
            vzbs__alsk = zveko__xoc - itx__mhqbm
            eco__ybi = zcvlp__ybiis - pmtg__zlp
            ewpm__dpxs = ksb__rymg - cis__mntqe
            totmicrosec = 1000000 * (vzbs__alsk * 86400 + eco__ybi
                ) + ewpm__dpxs
            return compute_pd_timestamp(totmicrosec, nanosecond)
        return impl
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl_timestamp(lhs, rhs):
            return convert_numpy_timedelta64_to_pd_timedelta(lhs.value -
                rhs.value)
        return impl_timestamp
    if lhs == pd_timestamp_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


def overload_add_operator_timestamp(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            zveko__xoc = lhs.toordinal()
            zcvlp__ybiis = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ksb__rymg = lhs.microsecond
            nanosecond = lhs.nanosecond
            itx__mhqbm = rhs.days
            pmtg__zlp = rhs.seconds
            cis__mntqe = rhs.microseconds
            vzbs__alsk = zveko__xoc + itx__mhqbm
            eco__ybi = zcvlp__ybiis + pmtg__zlp
            ewpm__dpxs = ksb__rymg + cis__mntqe
            totmicrosec = 1000000 * (vzbs__alsk * 86400 + eco__ybi
                ) + ewpm__dpxs
            return compute_pd_timestamp(totmicrosec, nanosecond)
        return impl
    if lhs == pd_timestamp_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            zveko__xoc = lhs.toordinal()
            zcvlp__ybiis = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ksb__rymg = lhs.microsecond
            wvh__oedvo = lhs.nanosecond
            cis__mntqe = rhs.value // 1000
            sos__nccc = rhs.nanoseconds
            ewpm__dpxs = ksb__rymg + cis__mntqe
            totmicrosec = 1000000 * (zveko__xoc * 86400 + zcvlp__ybiis
                ) + ewpm__dpxs
            wpj__vgojx = wvh__oedvo + sos__nccc
            return compute_pd_timestamp(totmicrosec, wpj__vgojx)
        return impl
    if (lhs == pd_timedelta_type and rhs == pd_timestamp_type or lhs ==
        datetime_timedelta_type and rhs == pd_timestamp_type):

        def impl(lhs, rhs):
            return rhs + lhs
        return impl


@overload(min, no_unliteral=True)
def timestamp_min(lhs, rhs):
    check_tz_aware_unsupported(lhs, f'Timestamp.min()')
    check_tz_aware_unsupported(rhs, f'Timestamp.min()')
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@overload(max, no_unliteral=True)
def timestamp_max(lhs, rhs):
    check_tz_aware_unsupported(lhs, f'Timestamp.max()')
    check_tz_aware_unsupported(rhs, f'Timestamp.max()')
    if lhs == pd_timestamp_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload_method(DatetimeDateType, 'strftime')
@overload_method(PandasTimestampType, 'strftime')
def strftime(ts, format):
    if isinstance(ts, DatetimeDateType):
        kal__bqgwk = 'datetime.date'
    else:
        kal__bqgwk = 'pandas.Timestamp'
    if types.unliteral(format) != types.unicode_type:
        raise BodoError(
            f"{kal__bqgwk}.strftime(): 'strftime' argument must be a string")

    def impl(ts, format):
        with numba.objmode(res='unicode_type'):
            res = ts.strftime(format)
        return res
    return impl


@overload_method(PandasTimestampType, 'to_datetime64')
def to_datetime64(ts):

    def impl(ts):
        return integer_to_dt64(ts.value)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='pd_timestamp_type'):
        d = pd.Timestamp.now()
    return d


class CompDT64(ConcreteTemplate):
    cases = [signature(types.boolean, types.NPDatetime('ns'), types.
        NPDatetime('ns'))]


@infer_global(operator.lt)
class CmpOpLt(CompDT64):
    key = operator.lt


@infer_global(operator.le)
class CmpOpLe(CompDT64):
    key = operator.le


@infer_global(operator.gt)
class CmpOpGt(CompDT64):
    key = operator.gt


@infer_global(operator.ge)
class CmpOpGe(CompDT64):
    key = operator.ge


@infer_global(operator.eq)
class CmpOpEq(CompDT64):
    key = operator.eq


@infer_global(operator.ne)
class CmpOpNe(CompDT64):
    key = operator.ne


@typeof_impl.register(calendar._localized_month)
def typeof_python_calendar(val, c):
    return types.Tuple([types.StringLiteral(cqdav__sfusf) for cqdav__sfusf in
        val])


@overload(str)
def overload_datetime64_str(val):
    if val == bodo.datetime64ns:

        def impl(val):
            return (bodo.hiframes.pd_timestamp_ext.
                convert_datetime64_to_timestamp(val).isoformat('T'))
        return impl


timestamp_unsupported_attrs = ['asm8', 'components', 'freqstr', 'tz',
    'fold', 'tzinfo', 'freq']
timestamp_unsupported_methods = ['astimezone', 'ctime', 'dst', 'isoweekday',
    'replace', 'strptime', 'time', 'timestamp', 'timetuple', 'timetz',
    'to_julian_date', 'to_numpy', 'to_period', 'to_pydatetime', 'tzname',
    'utcoffset', 'utctimetuple']


def _install_pd_timestamp_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for rwd__yqiyp in timestamp_unsupported_attrs:
        qpgo__xje = 'pandas.Timestamp.' + rwd__yqiyp
        overload_attribute(PandasTimestampType, rwd__yqiyp)(
            create_unsupported_overload(qpgo__xje))
    for yhf__fryw in timestamp_unsupported_methods:
        qpgo__xje = 'pandas.Timestamp.' + yhf__fryw
        overload_method(PandasTimestampType, yhf__fryw)(
            create_unsupported_overload(qpgo__xje + '()'))


_install_pd_timestamp_unsupported()


@lower_builtin(numba.core.types.functions.NumberClass, pd_timestamp_type,
    types.StringLiteral)
def datetime64_constructor(context, builder, sig, args):

    def datetime64_constructor_impl(a, b):
        return integer_to_dt64(a.value)
    return context.compile_internal(builder, datetime64_constructor_impl,
        sig, args)
