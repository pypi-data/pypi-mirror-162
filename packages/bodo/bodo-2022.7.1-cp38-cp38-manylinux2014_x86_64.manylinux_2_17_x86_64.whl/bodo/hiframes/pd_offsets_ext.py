"""
Implement support for the various classes in pd.tseries.offsets.
"""
import operator
import llvmlite.binding as ll
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.pd_timestamp_ext import get_days_in_month, pd_timestamp_type
from bodo.libs import hdatetime_ext
from bodo.utils.typing import BodoError, create_unsupported_overload, is_overload_none
ll.add_symbol('box_date_offset', hdatetime_ext.box_date_offset)
ll.add_symbol('unbox_date_offset', hdatetime_ext.unbox_date_offset)


class MonthBeginType(types.Type):

    def __init__(self):
        super(MonthBeginType, self).__init__(name='MonthBeginType()')


month_begin_type = MonthBeginType()


@typeof_impl.register(pd.tseries.offsets.MonthBegin)
def typeof_month_begin(val, c):
    return month_begin_type


@register_model(MonthBeginType)
class MonthBeginModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pwg__xndq = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, pwg__xndq)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    kdir__cfxc = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    whq__bgt = c.pyapi.long_from_longlong(kdir__cfxc.n)
    eah__yicyx = c.pyapi.from_native_value(types.boolean, kdir__cfxc.
        normalize, c.env_manager)
    mdkp__iew = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    ygu__bgt = c.pyapi.call_function_objargs(mdkp__iew, (whq__bgt, eah__yicyx))
    c.pyapi.decref(whq__bgt)
    c.pyapi.decref(eah__yicyx)
    c.pyapi.decref(mdkp__iew)
    return ygu__bgt


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    whq__bgt = c.pyapi.object_getattr_string(val, 'n')
    eah__yicyx = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(whq__bgt)
    normalize = c.pyapi.to_native_value(types.bool_, eah__yicyx).value
    kdir__cfxc = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kdir__cfxc.n = n
    kdir__cfxc.normalize = normalize
    c.pyapi.decref(whq__bgt)
    c.pyapi.decref(eah__yicyx)
    dwn__lnso = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kdir__cfxc._getvalue(), is_error=dwn__lnso)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        kdir__cfxc = cgutils.create_struct_proxy(typ)(context, builder)
        kdir__cfxc.n = args[0]
        kdir__cfxc.normalize = args[1]
        return kdir__cfxc._getvalue()
    return MonthBeginType()(n, normalize), codegen


make_attribute_wrapper(MonthBeginType, 'n', 'n')
make_attribute_wrapper(MonthBeginType, 'normalize', 'normalize')


@register_jitable
def calculate_month_begin_date(year, month, day, n):
    if n <= 0:
        if day > 1:
            n += 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = 1
    return year, month, day


def overload_add_operator_month_begin_offset_type(lhs, rhs):
    if lhs == month_begin_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_begin_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_begin_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_begin_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


class MonthEndType(types.Type):

    def __init__(self):
        super(MonthEndType, self).__init__(name='MonthEndType()')


month_end_type = MonthEndType()


@typeof_impl.register(pd.tseries.offsets.MonthEnd)
def typeof_month_end(val, c):
    return month_end_type


@register_model(MonthEndType)
class MonthEndModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pwg__xndq = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, pwg__xndq)


@box(MonthEndType)
def box_month_end(typ, val, c):
    kkuy__hft = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    whq__bgt = c.pyapi.long_from_longlong(kkuy__hft.n)
    eah__yicyx = c.pyapi.from_native_value(types.boolean, kkuy__hft.
        normalize, c.env_manager)
    tqhp__slt = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    ygu__bgt = c.pyapi.call_function_objargs(tqhp__slt, (whq__bgt, eah__yicyx))
    c.pyapi.decref(whq__bgt)
    c.pyapi.decref(eah__yicyx)
    c.pyapi.decref(tqhp__slt)
    return ygu__bgt


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    whq__bgt = c.pyapi.object_getattr_string(val, 'n')
    eah__yicyx = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(whq__bgt)
    normalize = c.pyapi.to_native_value(types.bool_, eah__yicyx).value
    kkuy__hft = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kkuy__hft.n = n
    kkuy__hft.normalize = normalize
    c.pyapi.decref(whq__bgt)
    c.pyapi.decref(eah__yicyx)
    dwn__lnso = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kkuy__hft._getvalue(), is_error=dwn__lnso)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        kkuy__hft = cgutils.create_struct_proxy(typ)(context, builder)
        kkuy__hft.n = args[0]
        kkuy__hft.normalize = args[1]
        return kkuy__hft._getvalue()
    return MonthEndType()(n, normalize), codegen


make_attribute_wrapper(MonthEndType, 'n', 'n')
make_attribute_wrapper(MonthEndType, 'normalize', 'normalize')


@lower_constant(MonthBeginType)
@lower_constant(MonthEndType)
def lower_constant_month_end(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    return lir.Constant.literal_struct([n, normalize])


@register_jitable
def calculate_month_end_date(year, month, day, n):
    if n > 0:
        kkuy__hft = get_days_in_month(year, month)
        if kkuy__hft > day:
            n -= 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = get_days_in_month(year, month)
    return year, month, day


def overload_add_operator_month_end_offset_type(lhs, rhs):
    if lhs == month_end_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_end_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_end_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_end_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_mul_date_offset_types(lhs, rhs):
    if lhs == month_begin_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthBegin(lhs.n * rhs, lhs.normalize)
    if lhs == month_end_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthEnd(lhs.n * rhs, lhs.normalize)
    if lhs == week_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.Week(lhs.n * rhs, lhs.normalize, lhs.
                weekday)
    if lhs == date_offset_type:

        def impl(lhs, rhs):
            n = lhs.n * rhs
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    if rhs in [week_type, month_end_type, month_begin_type, date_offset_type]:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl
    return impl


class DateOffsetType(types.Type):

    def __init__(self):
        super(DateOffsetType, self).__init__(name='DateOffsetType()')


date_offset_type = DateOffsetType()
date_offset_fields = ['years', 'months', 'weeks', 'days', 'hours',
    'minutes', 'seconds', 'microseconds', 'nanoseconds', 'year', 'month',
    'day', 'weekday', 'hour', 'minute', 'second', 'microsecond', 'nanosecond']


@typeof_impl.register(pd.tseries.offsets.DateOffset)
def type_of_date_offset(val, c):
    return date_offset_type


@register_model(DateOffsetType)
class DateOffsetModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pwg__xndq = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, pwg__xndq)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    unpx__ffvuu = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    fxkw__wxont = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for vbeas__rjtix, qphi__rvcav in enumerate(date_offset_fields):
        c.builder.store(getattr(unpx__ffvuu, qphi__rvcav), c.builder.
            inttoptr(c.builder.add(c.builder.ptrtoint(fxkw__wxont, lir.
            IntType(64)), lir.Constant(lir.IntType(64), 8 * vbeas__rjtix)),
            lir.IntType(64).as_pointer()))
    yvb__lhgiy = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    tjvk__nem = cgutils.get_or_insert_function(c.builder.module, yvb__lhgiy,
        name='box_date_offset')
    eawn__npda = c.builder.call(tjvk__nem, [unpx__ffvuu.n, unpx__ffvuu.
        normalize, fxkw__wxont, unpx__ffvuu.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return eawn__npda


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    whq__bgt = c.pyapi.object_getattr_string(val, 'n')
    eah__yicyx = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(whq__bgt)
    normalize = c.pyapi.to_native_value(types.bool_, eah__yicyx).value
    fxkw__wxont = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    yvb__lhgiy = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    lcluk__wjgv = cgutils.get_or_insert_function(c.builder.module,
        yvb__lhgiy, name='unbox_date_offset')
    has_kws = c.builder.call(lcluk__wjgv, [val, fxkw__wxont])
    unpx__ffvuu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    unpx__ffvuu.n = n
    unpx__ffvuu.normalize = normalize
    for vbeas__rjtix, qphi__rvcav in enumerate(date_offset_fields):
        setattr(unpx__ffvuu, qphi__rvcav, c.builder.load(c.builder.inttoptr
            (c.builder.add(c.builder.ptrtoint(fxkw__wxont, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * vbeas__rjtix)), lir.IntType(
            64).as_pointer())))
    unpx__ffvuu.has_kws = has_kws
    c.pyapi.decref(whq__bgt)
    c.pyapi.decref(eah__yicyx)
    dwn__lnso = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(unpx__ffvuu._getvalue(), is_error=dwn__lnso)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    gonm__iuc = [n, normalize]
    has_kws = False
    wrhsq__nwrif = [0] * 9 + [-1] * 9
    for vbeas__rjtix, qphi__rvcav in enumerate(date_offset_fields):
        if hasattr(pyval, qphi__rvcav):
            nnc__hik = context.get_constant(types.int64, getattr(pyval,
                qphi__rvcav))
            has_kws = True
        else:
            nnc__hik = context.get_constant(types.int64, wrhsq__nwrif[
                vbeas__rjtix])
        gonm__iuc.append(nnc__hik)
    has_kws = context.get_constant(types.boolean, has_kws)
    gonm__iuc.append(has_kws)
    return lir.Constant.literal_struct(gonm__iuc)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    ypazc__enk = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for yky__byh in ypazc__enk:
        if not is_overload_none(yky__byh):
            has_kws = True
            break

    def impl(n=1, normalize=False, years=None, months=None, weeks=None,
        days=None, hours=None, minutes=None, seconds=None, microseconds=
        None, nanoseconds=None, year=None, month=None, day=None, weekday=
        None, hour=None, minute=None, second=None, microsecond=None,
        nanosecond=None):
        years = 0 if years is None else years
        months = 0 if months is None else months
        weeks = 0 if weeks is None else weeks
        days = 0 if days is None else days
        hours = 0 if hours is None else hours
        minutes = 0 if minutes is None else minutes
        seconds = 0 if seconds is None else seconds
        microseconds = 0 if microseconds is None else microseconds
        nanoseconds = 0 if nanoseconds is None else nanoseconds
        year = -1 if year is None else year
        month = -1 if month is None else month
        weekday = -1 if weekday is None else weekday
        day = -1 if day is None else day
        hour = -1 if hour is None else hour
        minute = -1 if minute is None else minute
        second = -1 if second is None else second
        microsecond = -1 if microsecond is None else microsecond
        nanosecond = -1 if nanosecond is None else nanosecond
        return init_date_offset(n, normalize, years, months, weeks, days,
            hours, minutes, seconds, microseconds, nanoseconds, year, month,
            day, weekday, hour, minute, second, microsecond, nanosecond,
            has_kws)
    return impl


@intrinsic
def init_date_offset(typingctx, n, normalize, years, months, weeks, days,
    hours, minutes, seconds, microseconds, nanoseconds, year, month, day,
    weekday, hour, minute, second, microsecond, nanosecond, has_kws):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        unpx__ffvuu = cgutils.create_struct_proxy(typ)(context, builder)
        unpx__ffvuu.n = args[0]
        unpx__ffvuu.normalize = args[1]
        unpx__ffvuu.years = args[2]
        unpx__ffvuu.months = args[3]
        unpx__ffvuu.weeks = args[4]
        unpx__ffvuu.days = args[5]
        unpx__ffvuu.hours = args[6]
        unpx__ffvuu.minutes = args[7]
        unpx__ffvuu.seconds = args[8]
        unpx__ffvuu.microseconds = args[9]
        unpx__ffvuu.nanoseconds = args[10]
        unpx__ffvuu.year = args[11]
        unpx__ffvuu.month = args[12]
        unpx__ffvuu.day = args[13]
        unpx__ffvuu.weekday = args[14]
        unpx__ffvuu.hour = args[15]
        unpx__ffvuu.minute = args[16]
        unpx__ffvuu.second = args[17]
        unpx__ffvuu.microsecond = args[18]
        unpx__ffvuu.nanosecond = args[19]
        unpx__ffvuu.has_kws = args[20]
        return unpx__ffvuu._getvalue()
    return DateOffsetType()(n, normalize, years, months, weeks, days, hours,
        minutes, seconds, microseconds, nanoseconds, year, month, day,
        weekday, hour, minute, second, microsecond, nanosecond, has_kws
        ), codegen


make_attribute_wrapper(DateOffsetType, 'n', 'n')
make_attribute_wrapper(DateOffsetType, 'normalize', 'normalize')
make_attribute_wrapper(DateOffsetType, 'years', '_years')
make_attribute_wrapper(DateOffsetType, 'months', '_months')
make_attribute_wrapper(DateOffsetType, 'weeks', '_weeks')
make_attribute_wrapper(DateOffsetType, 'days', '_days')
make_attribute_wrapper(DateOffsetType, 'hours', '_hours')
make_attribute_wrapper(DateOffsetType, 'minutes', '_minutes')
make_attribute_wrapper(DateOffsetType, 'seconds', '_seconds')
make_attribute_wrapper(DateOffsetType, 'microseconds', '_microseconds')
make_attribute_wrapper(DateOffsetType, 'nanoseconds', '_nanoseconds')
make_attribute_wrapper(DateOffsetType, 'year', '_year')
make_attribute_wrapper(DateOffsetType, 'month', '_month')
make_attribute_wrapper(DateOffsetType, 'weekday', '_weekday')
make_attribute_wrapper(DateOffsetType, 'day', '_day')
make_attribute_wrapper(DateOffsetType, 'hour', '_hour')
make_attribute_wrapper(DateOffsetType, 'minute', '_minute')
make_attribute_wrapper(DateOffsetType, 'second', '_second')
make_attribute_wrapper(DateOffsetType, 'microsecond', '_microsecond')
make_attribute_wrapper(DateOffsetType, 'nanosecond', '_nanosecond')
make_attribute_wrapper(DateOffsetType, 'has_kws', '_has_kws')


@register_jitable
def relative_delta_addition(dateoffset, ts):
    if dateoffset._has_kws:
        czmrz__sok = -1 if dateoffset.n < 0 else 1
        for mfvui__nwf in range(np.abs(dateoffset.n)):
            year = ts.year
            month = ts.month
            day = ts.day
            hour = ts.hour
            minute = ts.minute
            second = ts.second
            microsecond = ts.microsecond
            nanosecond = ts.nanosecond
            if dateoffset._year != -1:
                year = dateoffset._year
            year += czmrz__sok * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += czmrz__sok * dateoffset._months
            year, month, tbo__merpg = calculate_month_end_date(year, month,
                day, 0)
            if day > tbo__merpg:
                day = tbo__merpg
            if dateoffset._day != -1:
                day = dateoffset._day
            if dateoffset._hour != -1:
                hour = dateoffset._hour
            if dateoffset._minute != -1:
                minute = dateoffset._minute
            if dateoffset._second != -1:
                second = dateoffset._second
            if dateoffset._microsecond != -1:
                microsecond = dateoffset._microsecond
            if dateoffset._nanosecond != -1:
                nanosecond = dateoffset._nanosecond
            ts = pd.Timestamp(year=year, month=month, day=day, hour=hour,
                minute=minute, second=second, microsecond=microsecond,
                nanosecond=nanosecond)
            ujdcr__cfumq = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            ujdcr__cfumq = ujdcr__cfumq + pd.Timedelta(dateoffset.
                _nanoseconds, unit='ns')
            if czmrz__sok == -1:
                ujdcr__cfumq = -ujdcr__cfumq
            ts = ts + ujdcr__cfumq
            if dateoffset._weekday != -1:
                llhkw__ulmjo = ts.weekday()
                ghtc__nkgj = (dateoffset._weekday - llhkw__ulmjo) % 7
                ts = ts + pd.Timedelta(days=ghtc__nkgj)
        return ts
    else:
        return pd.Timedelta(days=dateoffset.n) + ts


def overload_add_operator_date_offset_type(lhs, rhs):
    if lhs == date_offset_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, rhs)
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs == date_offset_type and rhs in [datetime_date_type,
        datetime_datetime_type]:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, pd.Timestamp(rhs))
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == date_offset_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_sub_operator_offsets(lhs, rhs):
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs in [date_offset_type, month_begin_type, month_end_type,
        week_type]:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


@overload(operator.neg, no_unliteral=True)
def overload_neg(lhs):
    if lhs == month_begin_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthBegin(-lhs.n, lhs.normalize)
    elif lhs == month_end_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthEnd(-lhs.n, lhs.normalize)
    elif lhs == week_type:

        def impl(lhs):
            return pd.tseries.offsets.Week(-lhs.n, lhs.normalize, lhs.weekday)
    elif lhs == date_offset_type:

        def impl(lhs):
            n = -lhs.n
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    else:
        return
    return impl


def is_offsets_type(val):
    return val in [date_offset_type, month_begin_type, month_end_type,
        week_type]


class WeekType(types.Type):

    def __init__(self):
        super(WeekType, self).__init__(name='WeekType()')


week_type = WeekType()


@typeof_impl.register(pd.tseries.offsets.Week)
def typeof_week(val, c):
    return week_type


@register_model(WeekType)
class WeekModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pwg__xndq = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, pwg__xndq)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        cotq__akhx = -1 if weekday is None else weekday
        return init_week(n, normalize, cotq__akhx)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        irxpz__ziye = cgutils.create_struct_proxy(typ)(context, builder)
        irxpz__ziye.n = args[0]
        irxpz__ziye.normalize = args[1]
        irxpz__ziye.weekday = args[2]
        return irxpz__ziye._getvalue()
    return WeekType()(n, normalize, weekday), codegen


@lower_constant(WeekType)
def lower_constant_week(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    if pyval.weekday is not None:
        weekday = context.get_constant(types.int64, pyval.weekday)
    else:
        weekday = context.get_constant(types.int64, -1)
    return lir.Constant.literal_struct([n, normalize, weekday])


@box(WeekType)
def box_week(typ, val, c):
    irxpz__ziye = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    whq__bgt = c.pyapi.long_from_longlong(irxpz__ziye.n)
    eah__yicyx = c.pyapi.from_native_value(types.boolean, irxpz__ziye.
        normalize, c.env_manager)
    fjo__nje = c.pyapi.long_from_longlong(irxpz__ziye.weekday)
    vxib__ltr = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    zervl__nuwim = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64),
        -1), irxpz__ziye.weekday)
    with c.builder.if_else(zervl__nuwim) as (fbcq__iyg, unckf__dggox):
        with fbcq__iyg:
            nhgkx__vljj = c.pyapi.call_function_objargs(vxib__ltr, (
                whq__bgt, eah__yicyx, fjo__nje))
            dqu__kiphb = c.builder.block
        with unckf__dggox:
            flazp__bkvxr = c.pyapi.call_function_objargs(vxib__ltr, (
                whq__bgt, eah__yicyx))
            rvljm__aksel = c.builder.block
    ygu__bgt = c.builder.phi(nhgkx__vljj.type)
    ygu__bgt.add_incoming(nhgkx__vljj, dqu__kiphb)
    ygu__bgt.add_incoming(flazp__bkvxr, rvljm__aksel)
    c.pyapi.decref(fjo__nje)
    c.pyapi.decref(whq__bgt)
    c.pyapi.decref(eah__yicyx)
    c.pyapi.decref(vxib__ltr)
    return ygu__bgt


@unbox(WeekType)
def unbox_week(typ, val, c):
    whq__bgt = c.pyapi.object_getattr_string(val, 'n')
    eah__yicyx = c.pyapi.object_getattr_string(val, 'normalize')
    fjo__nje = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(whq__bgt)
    normalize = c.pyapi.to_native_value(types.bool_, eah__yicyx).value
    tglip__xfvdw = c.pyapi.make_none()
    amsdw__vktt = c.builder.icmp_unsigned('==', fjo__nje, tglip__xfvdw)
    with c.builder.if_else(amsdw__vktt) as (unckf__dggox, fbcq__iyg):
        with fbcq__iyg:
            nhgkx__vljj = c.pyapi.long_as_longlong(fjo__nje)
            dqu__kiphb = c.builder.block
        with unckf__dggox:
            flazp__bkvxr = lir.Constant(lir.IntType(64), -1)
            rvljm__aksel = c.builder.block
    ygu__bgt = c.builder.phi(nhgkx__vljj.type)
    ygu__bgt.add_incoming(nhgkx__vljj, dqu__kiphb)
    ygu__bgt.add_incoming(flazp__bkvxr, rvljm__aksel)
    irxpz__ziye = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    irxpz__ziye.n = n
    irxpz__ziye.normalize = normalize
    irxpz__ziye.weekday = ygu__bgt
    c.pyapi.decref(whq__bgt)
    c.pyapi.decref(eah__yicyx)
    c.pyapi.decref(fjo__nje)
    dwn__lnso = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(irxpz__ziye._getvalue(), is_error=dwn__lnso)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            fygjh__vrs = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                swv__pkqft = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                swv__pkqft = rhs
            return swv__pkqft + fygjh__vrs
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            fygjh__vrs = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                swv__pkqft = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                swv__pkqft = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return swv__pkqft + fygjh__vrs
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            fygjh__vrs = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + fygjh__vrs
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == week_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


@register_jitable
def calculate_week_date(n, weekday, other_weekday):
    if weekday == -1:
        return pd.Timedelta(weeks=n)
    if weekday != other_weekday:
        szf__zleu = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=szf__zleu)


date_offset_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
date_offset_unsupported = {'__call__', 'rollback', 'rollforward',
    'is_month_start', 'is_month_end', 'apply', 'apply_index', 'copy',
    'isAnchored', 'onOffset', 'is_anchored', 'is_on_offset',
    'is_quarter_start', 'is_quarter_end', 'is_year_start', 'is_year_end'}
month_end_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_end_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
month_begin_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_begin_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
week_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos', 'rule_code'}
week_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
offsets_unsupported = {pd.tseries.offsets.BusinessDay, pd.tseries.offsets.
    BDay, pd.tseries.offsets.BusinessHour, pd.tseries.offsets.
    CustomBusinessDay, pd.tseries.offsets.CDay, pd.tseries.offsets.
    CustomBusinessHour, pd.tseries.offsets.BusinessMonthEnd, pd.tseries.
    offsets.BMonthEnd, pd.tseries.offsets.BusinessMonthBegin, pd.tseries.
    offsets.BMonthBegin, pd.tseries.offsets.CustomBusinessMonthEnd, pd.
    tseries.offsets.CBMonthEnd, pd.tseries.offsets.CustomBusinessMonthBegin,
    pd.tseries.offsets.CBMonthBegin, pd.tseries.offsets.SemiMonthEnd, pd.
    tseries.offsets.SemiMonthBegin, pd.tseries.offsets.WeekOfMonth, pd.
    tseries.offsets.LastWeekOfMonth, pd.tseries.offsets.BQuarterEnd, pd.
    tseries.offsets.BQuarterBegin, pd.tseries.offsets.QuarterEnd, pd.
    tseries.offsets.QuarterBegin, pd.tseries.offsets.BYearEnd, pd.tseries.
    offsets.BYearBegin, pd.tseries.offsets.YearEnd, pd.tseries.offsets.
    YearBegin, pd.tseries.offsets.FY5253, pd.tseries.offsets.FY5253Quarter,
    pd.tseries.offsets.Easter, pd.tseries.offsets.Tick, pd.tseries.offsets.
    Day, pd.tseries.offsets.Hour, pd.tseries.offsets.Minute, pd.tseries.
    offsets.Second, pd.tseries.offsets.Milli, pd.tseries.offsets.Micro, pd.
    tseries.offsets.Nano}
frequencies_unsupported = {pd.tseries.frequencies.to_offset}


def _install_date_offsets_unsupported():
    for yum__vmkcy in date_offset_unsupported_attrs:
        qow__mugpj = 'pandas.tseries.offsets.DateOffset.' + yum__vmkcy
        overload_attribute(DateOffsetType, yum__vmkcy)(
            create_unsupported_overload(qow__mugpj))
    for yum__vmkcy in date_offset_unsupported:
        qow__mugpj = 'pandas.tseries.offsets.DateOffset.' + yum__vmkcy
        overload_method(DateOffsetType, yum__vmkcy)(create_unsupported_overload
            (qow__mugpj))


def _install_month_begin_unsupported():
    for yum__vmkcy in month_begin_unsupported_attrs:
        qow__mugpj = 'pandas.tseries.offsets.MonthBegin.' + yum__vmkcy
        overload_attribute(MonthBeginType, yum__vmkcy)(
            create_unsupported_overload(qow__mugpj))
    for yum__vmkcy in month_begin_unsupported:
        qow__mugpj = 'pandas.tseries.offsets.MonthBegin.' + yum__vmkcy
        overload_method(MonthBeginType, yum__vmkcy)(create_unsupported_overload
            (qow__mugpj))


def _install_month_end_unsupported():
    for yum__vmkcy in date_offset_unsupported_attrs:
        qow__mugpj = 'pandas.tseries.offsets.MonthEnd.' + yum__vmkcy
        overload_attribute(MonthEndType, yum__vmkcy)(
            create_unsupported_overload(qow__mugpj))
    for yum__vmkcy in date_offset_unsupported:
        qow__mugpj = 'pandas.tseries.offsets.MonthEnd.' + yum__vmkcy
        overload_method(MonthEndType, yum__vmkcy)(create_unsupported_overload
            (qow__mugpj))


def _install_week_unsupported():
    for yum__vmkcy in week_unsupported_attrs:
        qow__mugpj = 'pandas.tseries.offsets.Week.' + yum__vmkcy
        overload_attribute(WeekType, yum__vmkcy)(create_unsupported_overload
            (qow__mugpj))
    for yum__vmkcy in week_unsupported:
        qow__mugpj = 'pandas.tseries.offsets.Week.' + yum__vmkcy
        overload_method(WeekType, yum__vmkcy)(create_unsupported_overload(
            qow__mugpj))


def _install_offsets_unsupported():
    for nnc__hik in offsets_unsupported:
        qow__mugpj = 'pandas.tseries.offsets.' + nnc__hik.__name__
        overload(nnc__hik)(create_unsupported_overload(qow__mugpj))


def _install_frequencies_unsupported():
    for nnc__hik in frequencies_unsupported:
        qow__mugpj = 'pandas.tseries.frequencies.' + nnc__hik.__name__
        overload(nnc__hik)(create_unsupported_overload(qow__mugpj))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
