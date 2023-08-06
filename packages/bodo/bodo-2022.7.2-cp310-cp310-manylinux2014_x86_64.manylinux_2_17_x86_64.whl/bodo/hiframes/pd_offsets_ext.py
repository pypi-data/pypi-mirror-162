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
        tzzg__rda = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, tzzg__rda)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    jmu__jezf = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    xmc__gakz = c.pyapi.long_from_longlong(jmu__jezf.n)
    axtmo__dmv = c.pyapi.from_native_value(types.boolean, jmu__jezf.
        normalize, c.env_manager)
    uux__ggzy = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    stxm__ekb = c.pyapi.call_function_objargs(uux__ggzy, (xmc__gakz,
        axtmo__dmv))
    c.pyapi.decref(xmc__gakz)
    c.pyapi.decref(axtmo__dmv)
    c.pyapi.decref(uux__ggzy)
    return stxm__ekb


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    xmc__gakz = c.pyapi.object_getattr_string(val, 'n')
    axtmo__dmv = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(xmc__gakz)
    normalize = c.pyapi.to_native_value(types.bool_, axtmo__dmv).value
    jmu__jezf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jmu__jezf.n = n
    jmu__jezf.normalize = normalize
    c.pyapi.decref(xmc__gakz)
    c.pyapi.decref(axtmo__dmv)
    clxc__iksl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jmu__jezf._getvalue(), is_error=clxc__iksl)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        jmu__jezf = cgutils.create_struct_proxy(typ)(context, builder)
        jmu__jezf.n = args[0]
        jmu__jezf.normalize = args[1]
        return jmu__jezf._getvalue()
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
        tzzg__rda = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, tzzg__rda)


@box(MonthEndType)
def box_month_end(typ, val, c):
    mijgy__zjwr = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    xmc__gakz = c.pyapi.long_from_longlong(mijgy__zjwr.n)
    axtmo__dmv = c.pyapi.from_native_value(types.boolean, mijgy__zjwr.
        normalize, c.env_manager)
    stjac__vmr = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    stxm__ekb = c.pyapi.call_function_objargs(stjac__vmr, (xmc__gakz,
        axtmo__dmv))
    c.pyapi.decref(xmc__gakz)
    c.pyapi.decref(axtmo__dmv)
    c.pyapi.decref(stjac__vmr)
    return stxm__ekb


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    xmc__gakz = c.pyapi.object_getattr_string(val, 'n')
    axtmo__dmv = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(xmc__gakz)
    normalize = c.pyapi.to_native_value(types.bool_, axtmo__dmv).value
    mijgy__zjwr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mijgy__zjwr.n = n
    mijgy__zjwr.normalize = normalize
    c.pyapi.decref(xmc__gakz)
    c.pyapi.decref(axtmo__dmv)
    clxc__iksl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mijgy__zjwr._getvalue(), is_error=clxc__iksl)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        mijgy__zjwr = cgutils.create_struct_proxy(typ)(context, builder)
        mijgy__zjwr.n = args[0]
        mijgy__zjwr.normalize = args[1]
        return mijgy__zjwr._getvalue()
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
        mijgy__zjwr = get_days_in_month(year, month)
        if mijgy__zjwr > day:
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
        tzzg__rda = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, tzzg__rda)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    nbzs__npn = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    afuo__bovxk = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for iuyme__dkakz, fgiun__ajc in enumerate(date_offset_fields):
        c.builder.store(getattr(nbzs__npn, fgiun__ajc), c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(afuo__bovxk, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * iuyme__dkakz)), lir.IntType(
            64).as_pointer()))
    cfas__bfz = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    dhsq__ionzn = cgutils.get_or_insert_function(c.builder.module,
        cfas__bfz, name='box_date_offset')
    xbi__jkrk = c.builder.call(dhsq__ionzn, [nbzs__npn.n, nbzs__npn.
        normalize, afuo__bovxk, nbzs__npn.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return xbi__jkrk


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    xmc__gakz = c.pyapi.object_getattr_string(val, 'n')
    axtmo__dmv = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(xmc__gakz)
    normalize = c.pyapi.to_native_value(types.bool_, axtmo__dmv).value
    afuo__bovxk = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    cfas__bfz = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer()])
    veqiv__gbsc = cgutils.get_or_insert_function(c.builder.module,
        cfas__bfz, name='unbox_date_offset')
    has_kws = c.builder.call(veqiv__gbsc, [val, afuo__bovxk])
    nbzs__npn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nbzs__npn.n = n
    nbzs__npn.normalize = normalize
    for iuyme__dkakz, fgiun__ajc in enumerate(date_offset_fields):
        setattr(nbzs__npn, fgiun__ajc, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(afuo__bovxk, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * iuyme__dkakz)), lir.IntType(
            64).as_pointer())))
    nbzs__npn.has_kws = has_kws
    c.pyapi.decref(xmc__gakz)
    c.pyapi.decref(axtmo__dmv)
    clxc__iksl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(nbzs__npn._getvalue(), is_error=clxc__iksl)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    dcp__vns = [n, normalize]
    has_kws = False
    sjq__fwyd = [0] * 9 + [-1] * 9
    for iuyme__dkakz, fgiun__ajc in enumerate(date_offset_fields):
        if hasattr(pyval, fgiun__ajc):
            gbj__sfur = context.get_constant(types.int64, getattr(pyval,
                fgiun__ajc))
            has_kws = True
        else:
            gbj__sfur = context.get_constant(types.int64, sjq__fwyd[
                iuyme__dkakz])
        dcp__vns.append(gbj__sfur)
    has_kws = context.get_constant(types.boolean, has_kws)
    dcp__vns.append(has_kws)
    return lir.Constant.literal_struct(dcp__vns)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    uwuoz__tescx = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for wftlc__pxw in uwuoz__tescx:
        if not is_overload_none(wftlc__pxw):
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
        nbzs__npn = cgutils.create_struct_proxy(typ)(context, builder)
        nbzs__npn.n = args[0]
        nbzs__npn.normalize = args[1]
        nbzs__npn.years = args[2]
        nbzs__npn.months = args[3]
        nbzs__npn.weeks = args[4]
        nbzs__npn.days = args[5]
        nbzs__npn.hours = args[6]
        nbzs__npn.minutes = args[7]
        nbzs__npn.seconds = args[8]
        nbzs__npn.microseconds = args[9]
        nbzs__npn.nanoseconds = args[10]
        nbzs__npn.year = args[11]
        nbzs__npn.month = args[12]
        nbzs__npn.day = args[13]
        nbzs__npn.weekday = args[14]
        nbzs__npn.hour = args[15]
        nbzs__npn.minute = args[16]
        nbzs__npn.second = args[17]
        nbzs__npn.microsecond = args[18]
        nbzs__npn.nanosecond = args[19]
        nbzs__npn.has_kws = args[20]
        return nbzs__npn._getvalue()
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
        ekowx__njcd = -1 if dateoffset.n < 0 else 1
        for fgfgi__acj in range(np.abs(dateoffset.n)):
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
            year += ekowx__njcd * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += ekowx__njcd * dateoffset._months
            year, month, wvu__phl = calculate_month_end_date(year, month,
                day, 0)
            if day > wvu__phl:
                day = wvu__phl
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
            eynnq__zgmbj = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            eynnq__zgmbj = eynnq__zgmbj + pd.Timedelta(dateoffset.
                _nanoseconds, unit='ns')
            if ekowx__njcd == -1:
                eynnq__zgmbj = -eynnq__zgmbj
            ts = ts + eynnq__zgmbj
            if dateoffset._weekday != -1:
                kukbd__modvm = ts.weekday()
                bqmi__fsrt = (dateoffset._weekday - kukbd__modvm) % 7
                ts = ts + pd.Timedelta(days=bqmi__fsrt)
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
        tzzg__rda = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, tzzg__rda)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        szgr__sllhz = -1 if weekday is None else weekday
        return init_week(n, normalize, szgr__sllhz)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        idfor__ribc = cgutils.create_struct_proxy(typ)(context, builder)
        idfor__ribc.n = args[0]
        idfor__ribc.normalize = args[1]
        idfor__ribc.weekday = args[2]
        return idfor__ribc._getvalue()
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
    idfor__ribc = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    xmc__gakz = c.pyapi.long_from_longlong(idfor__ribc.n)
    axtmo__dmv = c.pyapi.from_native_value(types.boolean, idfor__ribc.
        normalize, c.env_manager)
    bavb__autiq = c.pyapi.long_from_longlong(idfor__ribc.weekday)
    urw__vwmh = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    lzjxd__ahxp = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64),
        -1), idfor__ribc.weekday)
    with c.builder.if_else(lzjxd__ahxp) as (art__vcrdq, ibokl__rsaw):
        with art__vcrdq:
            kdr__gwiro = c.pyapi.call_function_objargs(urw__vwmh, (
                xmc__gakz, axtmo__dmv, bavb__autiq))
            mor__tbmuy = c.builder.block
        with ibokl__rsaw:
            sng__wvly = c.pyapi.call_function_objargs(urw__vwmh, (xmc__gakz,
                axtmo__dmv))
            ogick__fqo = c.builder.block
    stxm__ekb = c.builder.phi(kdr__gwiro.type)
    stxm__ekb.add_incoming(kdr__gwiro, mor__tbmuy)
    stxm__ekb.add_incoming(sng__wvly, ogick__fqo)
    c.pyapi.decref(bavb__autiq)
    c.pyapi.decref(xmc__gakz)
    c.pyapi.decref(axtmo__dmv)
    c.pyapi.decref(urw__vwmh)
    return stxm__ekb


@unbox(WeekType)
def unbox_week(typ, val, c):
    xmc__gakz = c.pyapi.object_getattr_string(val, 'n')
    axtmo__dmv = c.pyapi.object_getattr_string(val, 'normalize')
    bavb__autiq = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(xmc__gakz)
    normalize = c.pyapi.to_native_value(types.bool_, axtmo__dmv).value
    gxfbv__wcard = c.pyapi.make_none()
    mvpz__mmleh = c.builder.icmp_unsigned('==', bavb__autiq, gxfbv__wcard)
    with c.builder.if_else(mvpz__mmleh) as (ibokl__rsaw, art__vcrdq):
        with art__vcrdq:
            kdr__gwiro = c.pyapi.long_as_longlong(bavb__autiq)
            mor__tbmuy = c.builder.block
        with ibokl__rsaw:
            sng__wvly = lir.Constant(lir.IntType(64), -1)
            ogick__fqo = c.builder.block
    stxm__ekb = c.builder.phi(kdr__gwiro.type)
    stxm__ekb.add_incoming(kdr__gwiro, mor__tbmuy)
    stxm__ekb.add_incoming(sng__wvly, ogick__fqo)
    idfor__ribc = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    idfor__ribc.n = n
    idfor__ribc.normalize = normalize
    idfor__ribc.weekday = stxm__ekb
    c.pyapi.decref(xmc__gakz)
    c.pyapi.decref(axtmo__dmv)
    c.pyapi.decref(bavb__autiq)
    clxc__iksl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(idfor__ribc._getvalue(), is_error=clxc__iksl)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ghc__mayk = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                dmxvc__oclz = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                dmxvc__oclz = rhs
            return dmxvc__oclz + ghc__mayk
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            ghc__mayk = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                dmxvc__oclz = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                dmxvc__oclz = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return dmxvc__oclz + ghc__mayk
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            ghc__mayk = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + ghc__mayk
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
        vxms__cma = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=vxms__cma)


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
    for nyupz__ikj in date_offset_unsupported_attrs:
        xtbg__zbcn = 'pandas.tseries.offsets.DateOffset.' + nyupz__ikj
        overload_attribute(DateOffsetType, nyupz__ikj)(
            create_unsupported_overload(xtbg__zbcn))
    for nyupz__ikj in date_offset_unsupported:
        xtbg__zbcn = 'pandas.tseries.offsets.DateOffset.' + nyupz__ikj
        overload_method(DateOffsetType, nyupz__ikj)(create_unsupported_overload
            (xtbg__zbcn))


def _install_month_begin_unsupported():
    for nyupz__ikj in month_begin_unsupported_attrs:
        xtbg__zbcn = 'pandas.tseries.offsets.MonthBegin.' + nyupz__ikj
        overload_attribute(MonthBeginType, nyupz__ikj)(
            create_unsupported_overload(xtbg__zbcn))
    for nyupz__ikj in month_begin_unsupported:
        xtbg__zbcn = 'pandas.tseries.offsets.MonthBegin.' + nyupz__ikj
        overload_method(MonthBeginType, nyupz__ikj)(create_unsupported_overload
            (xtbg__zbcn))


def _install_month_end_unsupported():
    for nyupz__ikj in date_offset_unsupported_attrs:
        xtbg__zbcn = 'pandas.tseries.offsets.MonthEnd.' + nyupz__ikj
        overload_attribute(MonthEndType, nyupz__ikj)(
            create_unsupported_overload(xtbg__zbcn))
    for nyupz__ikj in date_offset_unsupported:
        xtbg__zbcn = 'pandas.tseries.offsets.MonthEnd.' + nyupz__ikj
        overload_method(MonthEndType, nyupz__ikj)(create_unsupported_overload
            (xtbg__zbcn))


def _install_week_unsupported():
    for nyupz__ikj in week_unsupported_attrs:
        xtbg__zbcn = 'pandas.tseries.offsets.Week.' + nyupz__ikj
        overload_attribute(WeekType, nyupz__ikj)(create_unsupported_overload
            (xtbg__zbcn))
    for nyupz__ikj in week_unsupported:
        xtbg__zbcn = 'pandas.tseries.offsets.Week.' + nyupz__ikj
        overload_method(WeekType, nyupz__ikj)(create_unsupported_overload(
            xtbg__zbcn))


def _install_offsets_unsupported():
    for gbj__sfur in offsets_unsupported:
        xtbg__zbcn = 'pandas.tseries.offsets.' + gbj__sfur.__name__
        overload(gbj__sfur)(create_unsupported_overload(xtbg__zbcn))


def _install_frequencies_unsupported():
    for gbj__sfur in frequencies_unsupported:
        xtbg__zbcn = 'pandas.tseries.frequencies.' + gbj__sfur.__name__
        overload(gbj__sfur)(create_unsupported_overload(xtbg__zbcn))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
