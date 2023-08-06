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
        ppuys__zwzq = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, ppuys__zwzq)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    cama__qadvt = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    jgedf__zbn = c.pyapi.long_from_longlong(cama__qadvt.n)
    kwt__fmnno = c.pyapi.from_native_value(types.boolean, cama__qadvt.
        normalize, c.env_manager)
    jomj__lam = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    lhl__zimnf = c.pyapi.call_function_objargs(jomj__lam, (jgedf__zbn,
        kwt__fmnno))
    c.pyapi.decref(jgedf__zbn)
    c.pyapi.decref(kwt__fmnno)
    c.pyapi.decref(jomj__lam)
    return lhl__zimnf


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    jgedf__zbn = c.pyapi.object_getattr_string(val, 'n')
    kwt__fmnno = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(jgedf__zbn)
    normalize = c.pyapi.to_native_value(types.bool_, kwt__fmnno).value
    cama__qadvt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cama__qadvt.n = n
    cama__qadvt.normalize = normalize
    c.pyapi.decref(jgedf__zbn)
    c.pyapi.decref(kwt__fmnno)
    dwsgq__dorj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cama__qadvt._getvalue(), is_error=dwsgq__dorj)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        cama__qadvt = cgutils.create_struct_proxy(typ)(context, builder)
        cama__qadvt.n = args[0]
        cama__qadvt.normalize = args[1]
        return cama__qadvt._getvalue()
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
        ppuys__zwzq = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, ppuys__zwzq)


@box(MonthEndType)
def box_month_end(typ, val, c):
    eun__hlsef = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    jgedf__zbn = c.pyapi.long_from_longlong(eun__hlsef.n)
    kwt__fmnno = c.pyapi.from_native_value(types.boolean, eun__hlsef.
        normalize, c.env_manager)
    rzyjk__psu = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    lhl__zimnf = c.pyapi.call_function_objargs(rzyjk__psu, (jgedf__zbn,
        kwt__fmnno))
    c.pyapi.decref(jgedf__zbn)
    c.pyapi.decref(kwt__fmnno)
    c.pyapi.decref(rzyjk__psu)
    return lhl__zimnf


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    jgedf__zbn = c.pyapi.object_getattr_string(val, 'n')
    kwt__fmnno = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(jgedf__zbn)
    normalize = c.pyapi.to_native_value(types.bool_, kwt__fmnno).value
    eun__hlsef = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    eun__hlsef.n = n
    eun__hlsef.normalize = normalize
    c.pyapi.decref(jgedf__zbn)
    c.pyapi.decref(kwt__fmnno)
    dwsgq__dorj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(eun__hlsef._getvalue(), is_error=dwsgq__dorj)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        eun__hlsef = cgutils.create_struct_proxy(typ)(context, builder)
        eun__hlsef.n = args[0]
        eun__hlsef.normalize = args[1]
        return eun__hlsef._getvalue()
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
        eun__hlsef = get_days_in_month(year, month)
        if eun__hlsef > day:
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
        ppuys__zwzq = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, ppuys__zwzq)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    liil__szls = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    awtk__igqra = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for xdvk__bgbdw, gzzm__ngu in enumerate(date_offset_fields):
        c.builder.store(getattr(liil__szls, gzzm__ngu), c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(awtk__igqra, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * xdvk__bgbdw)), lir.IntType(64
            ).as_pointer()))
    pxg__vcwn = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    sytq__bxrz = cgutils.get_or_insert_function(c.builder.module, pxg__vcwn,
        name='box_date_offset')
    wdeos__mim = c.builder.call(sytq__bxrz, [liil__szls.n, liil__szls.
        normalize, awtk__igqra, liil__szls.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return wdeos__mim


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    jgedf__zbn = c.pyapi.object_getattr_string(val, 'n')
    kwt__fmnno = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(jgedf__zbn)
    normalize = c.pyapi.to_native_value(types.bool_, kwt__fmnno).value
    awtk__igqra = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    pxg__vcwn = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer()])
    cext__mtkf = cgutils.get_or_insert_function(c.builder.module, pxg__vcwn,
        name='unbox_date_offset')
    has_kws = c.builder.call(cext__mtkf, [val, awtk__igqra])
    liil__szls = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    liil__szls.n = n
    liil__szls.normalize = normalize
    for xdvk__bgbdw, gzzm__ngu in enumerate(date_offset_fields):
        setattr(liil__szls, gzzm__ngu, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(awtk__igqra, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * xdvk__bgbdw)), lir.IntType(64
            ).as_pointer())))
    liil__szls.has_kws = has_kws
    c.pyapi.decref(jgedf__zbn)
    c.pyapi.decref(kwt__fmnno)
    dwsgq__dorj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(liil__szls._getvalue(), is_error=dwsgq__dorj)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    bems__dhh = [n, normalize]
    has_kws = False
    dde__drour = [0] * 9 + [-1] * 9
    for xdvk__bgbdw, gzzm__ngu in enumerate(date_offset_fields):
        if hasattr(pyval, gzzm__ngu):
            jpdt__ssku = context.get_constant(types.int64, getattr(pyval,
                gzzm__ngu))
            has_kws = True
        else:
            jpdt__ssku = context.get_constant(types.int64, dde__drour[
                xdvk__bgbdw])
        bems__dhh.append(jpdt__ssku)
    has_kws = context.get_constant(types.boolean, has_kws)
    bems__dhh.append(has_kws)
    return lir.Constant.literal_struct(bems__dhh)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    iqcjb__ndg = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for zaop__elvk in iqcjb__ndg:
        if not is_overload_none(zaop__elvk):
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
        liil__szls = cgutils.create_struct_proxy(typ)(context, builder)
        liil__szls.n = args[0]
        liil__szls.normalize = args[1]
        liil__szls.years = args[2]
        liil__szls.months = args[3]
        liil__szls.weeks = args[4]
        liil__szls.days = args[5]
        liil__szls.hours = args[6]
        liil__szls.minutes = args[7]
        liil__szls.seconds = args[8]
        liil__szls.microseconds = args[9]
        liil__szls.nanoseconds = args[10]
        liil__szls.year = args[11]
        liil__szls.month = args[12]
        liil__szls.day = args[13]
        liil__szls.weekday = args[14]
        liil__szls.hour = args[15]
        liil__szls.minute = args[16]
        liil__szls.second = args[17]
        liil__szls.microsecond = args[18]
        liil__szls.nanosecond = args[19]
        liil__szls.has_kws = args[20]
        return liil__szls._getvalue()
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
        charv__qifqg = -1 if dateoffset.n < 0 else 1
        for tre__swtgb in range(np.abs(dateoffset.n)):
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
            year += charv__qifqg * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += charv__qifqg * dateoffset._months
            year, month, ngy__rynja = calculate_month_end_date(year, month,
                day, 0)
            if day > ngy__rynja:
                day = ngy__rynja
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
            jbxf__cnr = pd.Timedelta(days=dateoffset._days + 7 * dateoffset
                ._weeks, hours=dateoffset._hours, minutes=dateoffset.
                _minutes, seconds=dateoffset._seconds, microseconds=
                dateoffset._microseconds)
            jbxf__cnr = jbxf__cnr + pd.Timedelta(dateoffset._nanoseconds,
                unit='ns')
            if charv__qifqg == -1:
                jbxf__cnr = -jbxf__cnr
            ts = ts + jbxf__cnr
            if dateoffset._weekday != -1:
                qufww__kxf = ts.weekday()
                rpj__ahvn = (dateoffset._weekday - qufww__kxf) % 7
                ts = ts + pd.Timedelta(days=rpj__ahvn)
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
        ppuys__zwzq = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, ppuys__zwzq)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        nvka__txlbr = -1 if weekday is None else weekday
        return init_week(n, normalize, nvka__txlbr)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        wfqsi__jvp = cgutils.create_struct_proxy(typ)(context, builder)
        wfqsi__jvp.n = args[0]
        wfqsi__jvp.normalize = args[1]
        wfqsi__jvp.weekday = args[2]
        return wfqsi__jvp._getvalue()
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
    wfqsi__jvp = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    jgedf__zbn = c.pyapi.long_from_longlong(wfqsi__jvp.n)
    kwt__fmnno = c.pyapi.from_native_value(types.boolean, wfqsi__jvp.
        normalize, c.env_manager)
    uqv__nke = c.pyapi.long_from_longlong(wfqsi__jvp.weekday)
    xib__bcuhe = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    tehls__kgbkw = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64),
        -1), wfqsi__jvp.weekday)
    with c.builder.if_else(tehls__kgbkw) as (edqd__lek, iaaey__svexa):
        with edqd__lek:
            syaiv__ypl = c.pyapi.call_function_objargs(xib__bcuhe, (
                jgedf__zbn, kwt__fmnno, uqv__nke))
            henb__ymrsp = c.builder.block
        with iaaey__svexa:
            iisyf__wdbv = c.pyapi.call_function_objargs(xib__bcuhe, (
                jgedf__zbn, kwt__fmnno))
            bapgx__wznc = c.builder.block
    lhl__zimnf = c.builder.phi(syaiv__ypl.type)
    lhl__zimnf.add_incoming(syaiv__ypl, henb__ymrsp)
    lhl__zimnf.add_incoming(iisyf__wdbv, bapgx__wznc)
    c.pyapi.decref(uqv__nke)
    c.pyapi.decref(jgedf__zbn)
    c.pyapi.decref(kwt__fmnno)
    c.pyapi.decref(xib__bcuhe)
    return lhl__zimnf


@unbox(WeekType)
def unbox_week(typ, val, c):
    jgedf__zbn = c.pyapi.object_getattr_string(val, 'n')
    kwt__fmnno = c.pyapi.object_getattr_string(val, 'normalize')
    uqv__nke = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(jgedf__zbn)
    normalize = c.pyapi.to_native_value(types.bool_, kwt__fmnno).value
    xjpl__vtqm = c.pyapi.make_none()
    knm__vwrb = c.builder.icmp_unsigned('==', uqv__nke, xjpl__vtqm)
    with c.builder.if_else(knm__vwrb) as (iaaey__svexa, edqd__lek):
        with edqd__lek:
            syaiv__ypl = c.pyapi.long_as_longlong(uqv__nke)
            henb__ymrsp = c.builder.block
        with iaaey__svexa:
            iisyf__wdbv = lir.Constant(lir.IntType(64), -1)
            bapgx__wznc = c.builder.block
    lhl__zimnf = c.builder.phi(syaiv__ypl.type)
    lhl__zimnf.add_incoming(syaiv__ypl, henb__ymrsp)
    lhl__zimnf.add_incoming(iisyf__wdbv, bapgx__wznc)
    wfqsi__jvp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wfqsi__jvp.n = n
    wfqsi__jvp.normalize = normalize
    wfqsi__jvp.weekday = lhl__zimnf
    c.pyapi.decref(jgedf__zbn)
    c.pyapi.decref(kwt__fmnno)
    c.pyapi.decref(uqv__nke)
    dwsgq__dorj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wfqsi__jvp._getvalue(), is_error=dwsgq__dorj)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            tbvwo__qxauu = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            if lhs.normalize:
                ctbu__jmvo = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                ctbu__jmvo = rhs
            return ctbu__jmvo + tbvwo__qxauu
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            tbvwo__qxauu = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            if lhs.normalize:
                ctbu__jmvo = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                ctbu__jmvo = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return ctbu__jmvo + tbvwo__qxauu
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            tbvwo__qxauu = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            return rhs + tbvwo__qxauu
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
        dcrx__yekcr = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=dcrx__yekcr)


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
    for aqy__wot in date_offset_unsupported_attrs:
        dgf__urcjh = 'pandas.tseries.offsets.DateOffset.' + aqy__wot
        overload_attribute(DateOffsetType, aqy__wot)(
            create_unsupported_overload(dgf__urcjh))
    for aqy__wot in date_offset_unsupported:
        dgf__urcjh = 'pandas.tseries.offsets.DateOffset.' + aqy__wot
        overload_method(DateOffsetType, aqy__wot)(create_unsupported_overload
            (dgf__urcjh))


def _install_month_begin_unsupported():
    for aqy__wot in month_begin_unsupported_attrs:
        dgf__urcjh = 'pandas.tseries.offsets.MonthBegin.' + aqy__wot
        overload_attribute(MonthBeginType, aqy__wot)(
            create_unsupported_overload(dgf__urcjh))
    for aqy__wot in month_begin_unsupported:
        dgf__urcjh = 'pandas.tseries.offsets.MonthBegin.' + aqy__wot
        overload_method(MonthBeginType, aqy__wot)(create_unsupported_overload
            (dgf__urcjh))


def _install_month_end_unsupported():
    for aqy__wot in date_offset_unsupported_attrs:
        dgf__urcjh = 'pandas.tseries.offsets.MonthEnd.' + aqy__wot
        overload_attribute(MonthEndType, aqy__wot)(create_unsupported_overload
            (dgf__urcjh))
    for aqy__wot in date_offset_unsupported:
        dgf__urcjh = 'pandas.tseries.offsets.MonthEnd.' + aqy__wot
        overload_method(MonthEndType, aqy__wot)(create_unsupported_overload
            (dgf__urcjh))


def _install_week_unsupported():
    for aqy__wot in week_unsupported_attrs:
        dgf__urcjh = 'pandas.tseries.offsets.Week.' + aqy__wot
        overload_attribute(WeekType, aqy__wot)(create_unsupported_overload(
            dgf__urcjh))
    for aqy__wot in week_unsupported:
        dgf__urcjh = 'pandas.tseries.offsets.Week.' + aqy__wot
        overload_method(WeekType, aqy__wot)(create_unsupported_overload(
            dgf__urcjh))


def _install_offsets_unsupported():
    for jpdt__ssku in offsets_unsupported:
        dgf__urcjh = 'pandas.tseries.offsets.' + jpdt__ssku.__name__
        overload(jpdt__ssku)(create_unsupported_overload(dgf__urcjh))


def _install_frequencies_unsupported():
    for jpdt__ssku in frequencies_unsupported:
        dgf__urcjh = 'pandas.tseries.frequencies.' + jpdt__ssku.__name__
        overload(jpdt__ssku)(create_unsupported_overload(dgf__urcjh))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
