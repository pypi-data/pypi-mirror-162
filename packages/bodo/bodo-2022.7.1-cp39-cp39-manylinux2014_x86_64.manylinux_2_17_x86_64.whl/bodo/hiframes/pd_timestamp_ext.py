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
            tbn__tuou = 'PandasTimestampType()'
        else:
            tbn__tuou = f'PandasTimestampType({tz_val})'
        super(PandasTimestampType, self).__init__(name=tbn__tuou)


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
        for lknut__iqyp in val.data:
            if isinstance(lknut__iqyp, bodo.DatetimeArrayType):
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
        oek__vjqyu = [('year', ts_field_typ), ('month', ts_field_typ), (
            'day', ts_field_typ), ('hour', ts_field_typ), ('minute',
            ts_field_typ), ('second', ts_field_typ), ('microsecond',
            ts_field_typ), ('nanosecond', ts_field_typ), ('value',
            ts_field_typ)]
        models.StructModel.__init__(self, dmm, fe_type, oek__vjqyu)


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
    cai__sjxef = c.pyapi.object_getattr_string(val, 'year')
    fkuj__xdjwm = c.pyapi.object_getattr_string(val, 'month')
    pjn__bxcg = c.pyapi.object_getattr_string(val, 'day')
    huix__dhx = c.pyapi.object_getattr_string(val, 'hour')
    keha__jfa = c.pyapi.object_getattr_string(val, 'minute')
    uilt__hzhxi = c.pyapi.object_getattr_string(val, 'second')
    szz__joeky = c.pyapi.object_getattr_string(val, 'microsecond')
    tdjvd__txcac = c.pyapi.object_getattr_string(val, 'nanosecond')
    wvp__myl = c.pyapi.object_getattr_string(val, 'value')
    ptcbo__nks = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ptcbo__nks.year = c.pyapi.long_as_longlong(cai__sjxef)
    ptcbo__nks.month = c.pyapi.long_as_longlong(fkuj__xdjwm)
    ptcbo__nks.day = c.pyapi.long_as_longlong(pjn__bxcg)
    ptcbo__nks.hour = c.pyapi.long_as_longlong(huix__dhx)
    ptcbo__nks.minute = c.pyapi.long_as_longlong(keha__jfa)
    ptcbo__nks.second = c.pyapi.long_as_longlong(uilt__hzhxi)
    ptcbo__nks.microsecond = c.pyapi.long_as_longlong(szz__joeky)
    ptcbo__nks.nanosecond = c.pyapi.long_as_longlong(tdjvd__txcac)
    ptcbo__nks.value = c.pyapi.long_as_longlong(wvp__myl)
    c.pyapi.decref(cai__sjxef)
    c.pyapi.decref(fkuj__xdjwm)
    c.pyapi.decref(pjn__bxcg)
    c.pyapi.decref(huix__dhx)
    c.pyapi.decref(keha__jfa)
    c.pyapi.decref(uilt__hzhxi)
    c.pyapi.decref(szz__joeky)
    c.pyapi.decref(tdjvd__txcac)
    c.pyapi.decref(wvp__myl)
    mzrx__skean = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ptcbo__nks._getvalue(), is_error=mzrx__skean)


@box(PandasTimestampType)
def box_pandas_timestamp(typ, val, c):
    xxn__tbyxh = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    cai__sjxef = c.pyapi.long_from_longlong(xxn__tbyxh.year)
    fkuj__xdjwm = c.pyapi.long_from_longlong(xxn__tbyxh.month)
    pjn__bxcg = c.pyapi.long_from_longlong(xxn__tbyxh.day)
    huix__dhx = c.pyapi.long_from_longlong(xxn__tbyxh.hour)
    keha__jfa = c.pyapi.long_from_longlong(xxn__tbyxh.minute)
    uilt__hzhxi = c.pyapi.long_from_longlong(xxn__tbyxh.second)
    cbf__ufc = c.pyapi.long_from_longlong(xxn__tbyxh.microsecond)
    kvqt__weax = c.pyapi.long_from_longlong(xxn__tbyxh.nanosecond)
    iirbi__ntrhb = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timestamp))
    if typ.tz is None:
        res = c.pyapi.call_function_objargs(iirbi__ntrhb, (cai__sjxef,
            fkuj__xdjwm, pjn__bxcg, huix__dhx, keha__jfa, uilt__hzhxi,
            cbf__ufc, kvqt__weax))
    else:
        if isinstance(typ.tz, int):
            rgvnp__nxnn = c.pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), typ.tz))
        else:
            qirxn__ncpcs = c.context.insert_const_string(c.builder.module,
                str(typ.tz))
            rgvnp__nxnn = c.pyapi.string_from_string(qirxn__ncpcs)
        args = c.pyapi.tuple_pack(())
        kwargs = c.pyapi.dict_pack([('year', cai__sjxef), ('month',
            fkuj__xdjwm), ('day', pjn__bxcg), ('hour', huix__dhx), (
            'minute', keha__jfa), ('second', uilt__hzhxi), ('microsecond',
            cbf__ufc), ('nanosecond', kvqt__weax), ('tz', rgvnp__nxnn)])
        res = c.pyapi.call(iirbi__ntrhb, args, kwargs)
        c.pyapi.decref(args)
        c.pyapi.decref(kwargs)
        c.pyapi.decref(rgvnp__nxnn)
    c.pyapi.decref(cai__sjxef)
    c.pyapi.decref(fkuj__xdjwm)
    c.pyapi.decref(pjn__bxcg)
    c.pyapi.decref(huix__dhx)
    c.pyapi.decref(keha__jfa)
    c.pyapi.decref(uilt__hzhxi)
    c.pyapi.decref(cbf__ufc)
    c.pyapi.decref(kvqt__weax)
    return res


@intrinsic
def init_timestamp(typingctx, year, month, day, hour, minute, second,
    microsecond, nanosecond, value, tz):

    def codegen(context, builder, sig, args):
        (year, month, day, hour, minute, second, kkmc__axto, emzug__rhgqd,
            value, fyo__mztpt) = args
        ts = cgutils.create_struct_proxy(sig.return_type)(context, builder)
        ts.year = year
        ts.month = month
        ts.day = day
        ts.hour = hour
        ts.minute = minute
        ts.second = second
        ts.microsecond = kkmc__axto
        ts.nanosecond = emzug__rhgqd
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
        ufmf__piz, precision = pd._libs.tslibs.conversion.precision_from_unit(
            unit)
        if isinstance(ts_input, types.Integer):

            def impl_int(ts_input=_no_input, freq=None, tz=None, unit=None,
                year=None, month=None, day=None, hour=None, minute=None,
                second=None, microsecond=None, nanosecond=None, tzinfo=None):
                value = ts_input * ufmf__piz
                return convert_val_to_timestamp(value, tz)
            return impl_int

        def impl_float(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            bmfb__nkbrq = np.int64(ts_input)
            cyu__llo = ts_input - bmfb__nkbrq
            if precision:
                cyu__llo = np.round(cyu__llo, precision)
            value = bmfb__nkbrq * ufmf__piz + np.int64(cyu__llo * ufmf__piz)
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
        ufmf__piz, precision = pd._libs.tslibs.conversion.precision_from_unit(
            ts_input.unit)

        def impl_date(ts_input=_no_input, freq=None, tz=None, unit=None,
            year=None, month=None, day=None, hour=None, minute=None, second
            =None, microsecond=None, nanosecond=None, tzinfo=None):
            value = np.int64(ts_input) * ufmf__piz
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
        fyo__mztpt, yrihm__rqfue, fyo__mztpt = get_isocalendar(ptt.year,
            ptt.month, ptt.day)
        return yrihm__rqfue
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
        year, yrihm__rqfue, wcgnq__aam = get_isocalendar(ptt.year, ptt.
            month, ptt.day)
        return year, yrihm__rqfue, wcgnq__aam
    return impl


@overload_method(PandasTimestampType, 'isoformat', no_unliteral=True)
def overload_pd_timestamp_isoformat(ts, sep=None):
    if is_overload_none(sep):

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            ced__lhgh = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + 'T' + ced__lhgh
            return res
        return timestamp_isoformat_impl
    else:

        def timestamp_isoformat_impl(ts, sep=None):
            assert ts.nanosecond == 0
            ced__lhgh = str_2d(ts.hour) + ':' + str_2d(ts.minute
                ) + ':' + str_2d(ts.second)
            res = str(ts.year) + '-' + str_2d(ts.month) + '-' + str_2d(ts.day
                ) + sep + ced__lhgh
            return res
    return timestamp_isoformat_impl


@overload_method(PandasTimestampType, 'normalize', no_unliteral=True)
def overload_pd_timestamp_normalize(ptt):

    def impl(ptt):
        return pd.Timestamp(year=ptt.year, month=ptt.month, day=ptt.day)
    return impl


@overload_method(PandasTimestampType, 'day_name', no_unliteral=True)
def overload_pd_timestamp_day_name(ptt, locale=None):
    oavc__qgw = dict(locale=locale)
    pyq__bwbyj = dict(locale=None)
    check_unsupported_args('Timestamp.day_name', oavc__qgw, pyq__bwbyj,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        bjh__apk = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'Saturday', 'Sunday')
        fyo__mztpt, fyo__mztpt, uty__vfemb = ptt.isocalendar()
        return bjh__apk[uty__vfemb - 1]
    return impl


@overload_method(PandasTimestampType, 'month_name', no_unliteral=True)
def overload_pd_timestamp_month_name(ptt, locale=None):
    oavc__qgw = dict(locale=locale)
    pyq__bwbyj = dict(locale=None)
    check_unsupported_args('Timestamp.month_name', oavc__qgw, pyq__bwbyj,
        package_name='pandas', module_name='Timestamp')

    def impl(ptt, locale=None):
        uvl__cih = ('January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December')
        return uvl__cih[ptt.month - 1]
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
    oavc__qgw = dict(ambiguous=ambiguous, nonexistent=nonexistent)
    eywck__crwnx = dict(ambiguous='raise', nonexistent='raise')
    check_unsupported_args('Timestamp.tz_localize', oavc__qgw, eywck__crwnx,
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
        bvjvw__mpb = cgutils.alloca_once(builder, lir.IntType(64))
        builder.store(args[0], bvjvw__mpb)
        year = cgutils.alloca_once(builder, lir.IntType(64))
        szc__zecx = cgutils.alloca_once(builder, lir.IntType(64))
        muz__qkad = lir.FunctionType(lir.VoidType(), [lir.IntType(64).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        wgwjm__cud = cgutils.get_or_insert_function(builder.module,
            muz__qkad, name='extract_year_days')
        builder.call(wgwjm__cud, [bvjvw__mpb, year, szc__zecx])
        return cgutils.pack_array(builder, [builder.load(bvjvw__mpb),
            builder.load(year), builder.load(szc__zecx)])
    return types.Tuple([types.int64, types.int64, types.int64])(dt64_t
        ), codegen


@intrinsic
def get_month_day(typingctx, year_t, days_t=None):
    assert year_t == types.int64
    assert days_t == types.int64

    def codegen(context, builder, sig, args):
        month = cgutils.alloca_once(builder, lir.IntType(64))
        day = cgutils.alloca_once(builder, lir.IntType(64))
        muz__qkad = lir.FunctionType(lir.VoidType(), [lir.IntType(64), lir.
            IntType(64), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer()])
        wgwjm__cud = cgutils.get_or_insert_function(builder.module,
            muz__qkad, name='get_month_day')
        builder.call(wgwjm__cud, [args[0], args[1], month, day])
        return cgutils.pack_array(builder, [builder.load(month), builder.
            load(day)])
    return types.Tuple([types.int64, types.int64])(types.int64, types.int64
        ), codegen


@register_jitable
def get_day_of_year(year, month, day):
    iubfv__tlnrc = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 
        365, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
    piklt__btr = is_leap_year(year)
    yeuhn__ggrbj = iubfv__tlnrc[piklt__btr * 13 + month - 1]
    uqjov__otmoc = yeuhn__ggrbj + day
    return uqjov__otmoc


@register_jitable
def get_day_of_week(y, m, d):
    hkmqq__pmxrl = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    y -= m < 3
    day = (y + y // 4 - y // 100 + y // 400 + hkmqq__pmxrl[m - 1] + d) % 7
    return (day + 6) % 7


@register_jitable
def get_days_in_month(year, month):
    is_leap_year = year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)
    qen__qyt = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 29, 31,
        30, 31, 30, 31, 31, 30, 31, 30, 31]
    return qen__qyt[12 * is_leap_year + month - 1]


@register_jitable
def is_leap_year(year):
    return year & 3 == 0 and (year % 100 != 0 or year % 400 == 0)


@numba.generated_jit(nopython=True)
def convert_val_to_timestamp(ts_input, tz=None, is_convert=True):
    hmes__qncea = awktd__kbzmu = np.array([])
    atks__uozk = '0'
    if is_overload_constant_str(tz):
        qirxn__ncpcs = get_overload_const_str(tz)
        rgvnp__nxnn = pytz.timezone(qirxn__ncpcs)
        if isinstance(rgvnp__nxnn, pytz.tzinfo.DstTzInfo):
            hmes__qncea = np.array(rgvnp__nxnn._utc_transition_times, dtype
                ='M8[ns]').view('i8')
            awktd__kbzmu = np.array(rgvnp__nxnn._transition_info)[:, 0]
            awktd__kbzmu = (pd.Series(awktd__kbzmu).dt.total_seconds() * 
                1000000000).astype(np.int64).values
            atks__uozk = (
                "deltas[np.searchsorted(trans, ts_input, side='right') - 1]")
        else:
            awktd__kbzmu = np.int64(rgvnp__nxnn._utcoffset.total_seconds() *
                1000000000)
            atks__uozk = 'deltas'
    elif is_overload_constant_int(tz):
        wjso__qnkqt = get_overload_const_int(tz)
        atks__uozk = str(wjso__qnkqt)
    elif not is_overload_none(tz):
        raise_bodo_error(
            'convert_val_to_timestamp(): tz value must be a constant string or None'
            )
    is_convert = get_overload_const_bool(is_convert)
    if is_convert:
        duw__chvor = 'tz_ts_input'
        iaegp__oej = 'ts_input'
    else:
        duw__chvor = 'ts_input'
        iaegp__oej = 'tz_ts_input'
    zkgr__ynjd = 'def impl(ts_input, tz=None, is_convert=True):\n'
    zkgr__ynjd += f'  tz_ts_input = ts_input + {atks__uozk}\n'
    zkgr__ynjd += (
        f'  dt, year, days = extract_year_days(integer_to_dt64({duw__chvor}))\n'
        )
    zkgr__ynjd += '  month, day = get_month_day(year, days)\n'
    zkgr__ynjd += '  return init_timestamp(\n'
    zkgr__ynjd += '    year=year,\n'
    zkgr__ynjd += '    month=month,\n'
    zkgr__ynjd += '    day=day,\n'
    zkgr__ynjd += '    hour=dt // (60 * 60 * 1_000_000_000),\n'
    zkgr__ynjd += '    minute=(dt // (60 * 1_000_000_000)) % 60,\n'
    zkgr__ynjd += '    second=(dt // 1_000_000_000) % 60,\n'
    zkgr__ynjd += '    microsecond=(dt // 1000) % 1_000_000,\n'
    zkgr__ynjd += '    nanosecond=dt % 1000,\n'
    zkgr__ynjd += f'    value={iaegp__oej},\n'
    zkgr__ynjd += '    tz=tz,\n'
    zkgr__ynjd += '  )\n'
    udu__jrui = {}
    exec(zkgr__ynjd, {'np': np, 'pd': pd, 'trans': hmes__qncea, 'deltas':
        awktd__kbzmu, 'integer_to_dt64': integer_to_dt64,
        'extract_year_days': extract_year_days, 'get_month_day':
        get_month_day, 'init_timestamp': init_timestamp, 'zero_if_none':
        zero_if_none}, udu__jrui)
    impl = udu__jrui['impl']
    return impl


@numba.njit(no_cpython_wrapper=True)
def convert_datetime64_to_timestamp(dt64):
    bvjvw__mpb, year, szc__zecx = extract_year_days(dt64)
    month, day = get_month_day(year, szc__zecx)
    return init_timestamp(year=year, month=month, day=day, hour=bvjvw__mpb //
        (60 * 60 * 1000000000), minute=bvjvw__mpb // (60 * 1000000000) % 60,
        second=bvjvw__mpb // 1000000000 % 60, microsecond=bvjvw__mpb // 
        1000 % 1000000, nanosecond=bvjvw__mpb % 1000, value=dt64, tz=None)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_datetime_timedelta(dt64):
    mihew__fbnnw = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    gdva__ymgqp = mihew__fbnnw // (86400 * 1000000000)
    mawe__sytaa = mihew__fbnnw - gdva__ymgqp * 86400 * 1000000000
    oaclj__eyho = mawe__sytaa // 1000000000
    xer__qzg = mawe__sytaa - oaclj__eyho * 1000000000
    apc__jrf = xer__qzg // 1000
    return datetime.timedelta(gdva__ymgqp, oaclj__eyho, apc__jrf)


@numba.njit(no_cpython_wrapper=True)
def convert_numpy_timedelta64_to_pd_timedelta(dt64):
    mihew__fbnnw = (bodo.hiframes.datetime_timedelta_ext.
        cast_numpy_timedelta_to_int(dt64))
    return pd.Timedelta(mihew__fbnnw)


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
    tuio__rofo = len(arr)
    vsaqr__qod = np.empty(tuio__rofo, 'datetime64[ns]')
    orvk__dgc = arr._indices
    zyg__abmy = pandas_string_array_to_datetime(arr._data, errors, dayfirst,
        yearfirst, utc, format, exact, unit, infer_datetime_format, origin,
        cache).values
    for rgfc__ysx in range(tuio__rofo):
        if bodo.libs.array_kernels.isna(orvk__dgc, rgfc__ysx):
            bodo.libs.array_kernels.setna(vsaqr__qod, rgfc__ysx)
            continue
        vsaqr__qod[rgfc__ysx] = zyg__abmy[orvk__dgc[rgfc__ysx]]
    return vsaqr__qod


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
            taw__lmtez = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            tbn__tuou = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            pwlw__rsl = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_datetime(arr, errors=errors, dayfirst=dayfirst,
                yearfirst=yearfirst, utc=utc, format=format, exact=exact,
                unit=unit, infer_datetime_format=infer_datetime_format,
                origin=origin, cache=cache))
            return bodo.hiframes.pd_series_ext.init_series(pwlw__rsl,
                taw__lmtez, tbn__tuou)
        return impl_series
    if arg_a == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        bfydu__gqone = np.dtype('datetime64[ns]')
        iNaT = pd._libs.tslibs.iNaT

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            tuio__rofo = len(arg_a)
            vsaqr__qod = np.empty(tuio__rofo, bfydu__gqone)
            for rgfc__ysx in numba.parfors.parfor.internal_prange(tuio__rofo):
                val = iNaT
                if not bodo.libs.array_kernels.isna(arg_a, rgfc__ysx):
                    data = arg_a[rgfc__ysx]
                    val = (bodo.hiframes.pd_timestamp_ext.
                        npy_datetimestruct_to_datetime(data.year, data.
                        month, data.day, 0, 0, 0, 0))
                vsaqr__qod[rgfc__ysx
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(vsaqr__qod,
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
        bfydu__gqone = np.dtype('datetime64[ns]')

        def impl_date_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            tuio__rofo = len(arg_a)
            vsaqr__qod = np.empty(tuio__rofo, bfydu__gqone)
            for rgfc__ysx in numba.parfors.parfor.internal_prange(tuio__rofo):
                data = arg_a[rgfc__ysx]
                val = to_datetime_scalar(data, errors=errors, dayfirst=
                    dayfirst, yearfirst=yearfirst, utc=utc, format=format,
                    exact=exact, unit=unit, infer_datetime_format=
                    infer_datetime_format, origin=origin, cache=cache)
                vsaqr__qod[rgfc__ysx
                    ] = bodo.hiframes.pd_timestamp_ext.datetime_datetime_to_dt64(
                    val)
            return bodo.hiframes.pd_index_ext.init_datetime_index(vsaqr__qod,
                None)
        return impl_date_arr
    if isinstance(arg_a, CategoricalArrayType
        ) and arg_a.dtype.elem_type == bodo.string_type:
        bfydu__gqone = np.dtype('datetime64[ns]')

        def impl_cat_arr(arg_a, errors='raise', dayfirst=False, yearfirst=
            False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            tuio__rofo = len(arg_a)
            vsaqr__qod = np.empty(tuio__rofo, bfydu__gqone)
            zceeq__ehu = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arg_a))
            zyg__abmy = pandas_string_array_to_datetime(arg_a.dtype.
                categories.values, errors, dayfirst, yearfirst, utc, format,
                exact, unit, infer_datetime_format, origin, cache).values
            for rgfc__ysx in numba.parfors.parfor.internal_prange(tuio__rofo):
                c = zceeq__ehu[rgfc__ysx]
                if c == -1:
                    bodo.libs.array_kernels.setna(vsaqr__qod, rgfc__ysx)
                    continue
                vsaqr__qod[rgfc__ysx] = zyg__abmy[c]
            return bodo.hiframes.pd_index_ext.init_datetime_index(vsaqr__qod,
                None)
        return impl_cat_arr
    if arg_a == bodo.dict_str_arr_type:

        def impl_dict_str_arr(arg_a, errors='raise', dayfirst=False,
            yearfirst=False, utc=None, format=None, exact=True, unit=None,
            infer_datetime_format=False, origin='unix', cache=True):
            vsaqr__qod = pandas_dict_string_array_to_datetime(arg_a, errors,
                dayfirst, yearfirst, utc, format, exact, unit,
                infer_datetime_format, origin, cache)
            return bodo.hiframes.pd_index_ext.init_datetime_index(vsaqr__qod,
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
            taw__lmtez = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            tbn__tuou = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            pwlw__rsl = bodo.utils.conversion.coerce_to_ndarray(pd.
                to_timedelta(arr, unit, errors))
            return bodo.hiframes.pd_series_ext.init_series(pwlw__rsl,
                taw__lmtez, tbn__tuou)
        return impl_series
    if is_overload_constant_str(arg_a) or arg_a in (pd_timedelta_type,
        datetime_timedelta_type, bodo.string_type):

        def impl_string(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a)
        return impl_string
    if isinstance(arg_a, types.Float):
        m, gevwo__aqebj = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_float_scalar(arg_a, unit='ns', errors='raise'):
            val = float_to_timedelta_val(arg_a, gevwo__aqebj, m)
            return pd.Timedelta(val)
        return impl_float_scalar
    if isinstance(arg_a, types.Integer):
        m, fyo__mztpt = pd._libs.tslibs.conversion.precision_from_unit(unit)

        def impl_integer_scalar(arg_a, unit='ns', errors='raise'):
            return pd.Timedelta(arg_a * m)
        return impl_integer_scalar
    if is_iterable_type(arg_a) and not isinstance(arg_a, types.BaseTuple):
        m, gevwo__aqebj = pd._libs.tslibs.conversion.precision_from_unit(unit)
        bxizq__fig = np.dtype('timedelta64[ns]')
        if isinstance(arg_a.dtype, types.Float):

            def impl_float(arg_a, unit='ns', errors='raise'):
                tuio__rofo = len(arg_a)
                vsaqr__qod = np.empty(tuio__rofo, bxizq__fig)
                for rgfc__ysx in numba.parfors.parfor.internal_prange(
                    tuio__rofo):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, rgfc__ysx):
                        val = float_to_timedelta_val(arg_a[rgfc__ysx],
                            gevwo__aqebj, m)
                    vsaqr__qod[rgfc__ysx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    vsaqr__qod, None)
            return impl_float
        if isinstance(arg_a.dtype, types.Integer):

            def impl_int(arg_a, unit='ns', errors='raise'):
                tuio__rofo = len(arg_a)
                vsaqr__qod = np.empty(tuio__rofo, bxizq__fig)
                for rgfc__ysx in numba.parfors.parfor.internal_prange(
                    tuio__rofo):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, rgfc__ysx):
                        val = arg_a[rgfc__ysx] * m
                    vsaqr__qod[rgfc__ysx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    vsaqr__qod, None)
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
                tuio__rofo = len(arg_a)
                vsaqr__qod = np.empty(tuio__rofo, bxizq__fig)
                for rgfc__ysx in numba.parfors.parfor.internal_prange(
                    tuio__rofo):
                    val = iNaT
                    if not bodo.libs.array_kernels.isna(arg_a, rgfc__ysx):
                        ibrno__mzl = arg_a[rgfc__ysx]
                        val = (ibrno__mzl.microseconds + 1000 * 1000 * (
                            ibrno__mzl.seconds + 24 * 60 * 60 * ibrno__mzl.
                            days)) * 1000
                    vsaqr__qod[rgfc__ysx
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        val)
                return bodo.hiframes.pd_index_ext.init_timedelta_index(
                    vsaqr__qod, None)
            return impl_datetime_timedelta
    raise_bodo_error(
        f'pd.to_timedelta(): cannot convert date type {arg_a.dtype}')


@register_jitable
def float_to_timedelta_val(data, precision, multiplier):
    bmfb__nkbrq = np.int64(data)
    cyu__llo = data - bmfb__nkbrq
    if precision:
        cyu__llo = np.round(cyu__llo, precision)
    return bmfb__nkbrq * multiplier + np.int64(cyu__llo * multiplier)


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
        oavc__qgw = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        ysiwd__nsiqi = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Timestamp.{method}', oavc__qgw,
            ysiwd__nsiqi, package_name='pandas', module_name='Timestamp')
        bzj__wqqpm = ["freq == 'D'", "freq == 'H'",
            "freq == 'min' or freq == 'T'", "freq == 'S'",
            "freq == 'ms' or freq == 'L'", "freq == 'U' or freq == 'us'",
            "freq == 'N'"]
        yorhq__qhpfq = [24 * 60 * 60 * 1000000 * 1000, 60 * 60 * 1000000 * 
            1000, 60 * 1000000 * 1000, 1000000 * 1000, 1000 * 1000, 1000, 1]
        zkgr__ynjd = (
            "def impl(td, freq, ambiguous='raise', nonexistent='raise'):\n")
        for rgfc__ysx, omhn__ohvr in enumerate(bzj__wqqpm):
            moe__ofapa = 'if' if rgfc__ysx == 0 else 'elif'
            zkgr__ynjd += '    {} {}:\n'.format(moe__ofapa, omhn__ohvr)
            zkgr__ynjd += '        unit_value = {}\n'.format(yorhq__qhpfq[
                rgfc__ysx])
        zkgr__ynjd += '    else:\n'
        zkgr__ynjd += (
            "        raise ValueError('Incorrect Frequency specification')\n")
        if td == pd_timedelta_type:
            zkgr__ynjd += (
                """    return pd.Timedelta(unit_value * np.int64(np.{}(td.value / unit_value)))
"""
                .format(method))
        elif td == pd_timestamp_type:
            if method == 'ceil':
                zkgr__ynjd += (
                    '    value = td.value + np.remainder(-td.value, unit_value)\n'
                    )
            if method == 'floor':
                zkgr__ynjd += (
                    '    value = td.value - np.remainder(td.value, unit_value)\n'
                    )
            if method == 'round':
                zkgr__ynjd += '    if unit_value == 1:\n'
                zkgr__ynjd += '        value = td.value\n'
                zkgr__ynjd += '    else:\n'
                zkgr__ynjd += (
                    '        quotient, remainder = np.divmod(td.value, unit_value)\n'
                    )
                zkgr__ynjd += """        mask = np.logical_or(remainder > (unit_value // 2), np.logical_and(remainder == (unit_value // 2), quotient % 2))
"""
                zkgr__ynjd += '        if mask:\n'
                zkgr__ynjd += '            quotient = quotient + 1\n'
                zkgr__ynjd += '        value = quotient * unit_value\n'
            zkgr__ynjd += '    return pd.Timestamp(value)\n'
        udu__jrui = {}
        exec(zkgr__ynjd, {'np': np, 'pd': pd}, udu__jrui)
        impl = udu__jrui['impl']
        return impl
    return freq_overload


def _install_freq_methods():
    zmlt__iubw = ['ceil', 'floor', 'round']
    for method in zmlt__iubw:
        gbn__udfcy = overload_freq_methods(method)
        overload_method(PDTimeDeltaType, method, no_unliteral=True)(gbn__udfcy)
        overload_method(PandasTimestampType, method, no_unliteral=True)(
            gbn__udfcy)


_install_freq_methods()


@register_jitable
def compute_pd_timestamp(totmicrosec, nanosecond):
    microsecond = totmicrosec % 1000000
    puyi__cetyj = totmicrosec // 1000000
    second = puyi__cetyj % 60
    nhu__mvyo = puyi__cetyj // 60
    minute = nhu__mvyo % 60
    aigb__utr = nhu__mvyo // 60
    hour = aigb__utr % 24
    bofhw__jbto = aigb__utr // 24
    year, month, day = _ord2ymd(bofhw__jbto)
    value = npy_datetimestruct_to_datetime(year, month, day, hour, minute,
        second, microsecond)
    value += zero_if_none(nanosecond)
    return init_timestamp(year, month, day, hour, minute, second,
        microsecond, nanosecond, value, None)


def overload_sub_operator_timestamp(lhs, rhs):
    if lhs == pd_timestamp_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            jtfsi__dyef = lhs.toordinal()
            rbz__qxhd = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            pte__cqcc = lhs.microsecond
            nanosecond = lhs.nanosecond
            eux__ulps = rhs.days
            rhzl__kfm = rhs.seconds
            pvu__pezev = rhs.microseconds
            rjzac__xekwt = jtfsi__dyef - eux__ulps
            ukz__qssg = rbz__qxhd - rhzl__kfm
            qpot__xmlk = pte__cqcc - pvu__pezev
            totmicrosec = 1000000 * (rjzac__xekwt * 86400 + ukz__qssg
                ) + qpot__xmlk
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
            jtfsi__dyef = lhs.toordinal()
            rbz__qxhd = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            pte__cqcc = lhs.microsecond
            nanosecond = lhs.nanosecond
            eux__ulps = rhs.days
            rhzl__kfm = rhs.seconds
            pvu__pezev = rhs.microseconds
            rjzac__xekwt = jtfsi__dyef + eux__ulps
            ukz__qssg = rbz__qxhd + rhzl__kfm
            qpot__xmlk = pte__cqcc + pvu__pezev
            totmicrosec = 1000000 * (rjzac__xekwt * 86400 + ukz__qssg
                ) + qpot__xmlk
            return compute_pd_timestamp(totmicrosec, nanosecond)
        return impl
    if lhs == pd_timestamp_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            jtfsi__dyef = lhs.toordinal()
            rbz__qxhd = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            pte__cqcc = lhs.microsecond
            jjtp__zxvyr = lhs.nanosecond
            pvu__pezev = rhs.value // 1000
            xycf__xqfo = rhs.nanoseconds
            qpot__xmlk = pte__cqcc + pvu__pezev
            totmicrosec = 1000000 * (jtfsi__dyef * 86400 + rbz__qxhd
                ) + qpot__xmlk
            msvl__ihyp = jjtp__zxvyr + xycf__xqfo
            return compute_pd_timestamp(totmicrosec, msvl__ihyp)
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
        ijmtc__gfhw = 'datetime.date'
    else:
        ijmtc__gfhw = 'pandas.Timestamp'
    if types.unliteral(format) != types.unicode_type:
        raise BodoError(
            f"{ijmtc__gfhw}.strftime(): 'strftime' argument must be a string")

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
    return types.Tuple([types.StringLiteral(tup__zkxu) for tup__zkxu in val])


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
    for ruey__dbali in timestamp_unsupported_attrs:
        agybm__krdem = 'pandas.Timestamp.' + ruey__dbali
        overload_attribute(PandasTimestampType, ruey__dbali)(
            create_unsupported_overload(agybm__krdem))
    for cmpo__qpyx in timestamp_unsupported_methods:
        agybm__krdem = 'pandas.Timestamp.' + cmpo__qpyx
        overload_method(PandasTimestampType, cmpo__qpyx)(
            create_unsupported_overload(agybm__krdem + '()'))


_install_pd_timestamp_unsupported()


@lower_builtin(numba.core.types.functions.NumberClass, pd_timestamp_type,
    types.StringLiteral)
def datetime64_constructor(context, builder, sig, args):

    def datetime64_constructor_impl(a, b):
        return integer_to_dt64(a.value)
    return context.compile_internal(builder, datetime64_constructor_impl,
        sig, args)
