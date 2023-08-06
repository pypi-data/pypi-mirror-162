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
        zwjk__lgts = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, zwjk__lgts)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    tgjw__tkudz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ifhmc__uqc = c.pyapi.long_from_longlong(tgjw__tkudz.n)
    wqt__cxow = c.pyapi.from_native_value(types.boolean, tgjw__tkudz.
        normalize, c.env_manager)
    dqoor__bmkg = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    oqnmn__avpe = c.pyapi.call_function_objargs(dqoor__bmkg, (ifhmc__uqc,
        wqt__cxow))
    c.pyapi.decref(ifhmc__uqc)
    c.pyapi.decref(wqt__cxow)
    c.pyapi.decref(dqoor__bmkg)
    return oqnmn__avpe


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    ifhmc__uqc = c.pyapi.object_getattr_string(val, 'n')
    wqt__cxow = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ifhmc__uqc)
    normalize = c.pyapi.to_native_value(types.bool_, wqt__cxow).value
    tgjw__tkudz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tgjw__tkudz.n = n
    tgjw__tkudz.normalize = normalize
    c.pyapi.decref(ifhmc__uqc)
    c.pyapi.decref(wqt__cxow)
    rvsj__rwwh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tgjw__tkudz._getvalue(), is_error=rvsj__rwwh)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        tgjw__tkudz = cgutils.create_struct_proxy(typ)(context, builder)
        tgjw__tkudz.n = args[0]
        tgjw__tkudz.normalize = args[1]
        return tgjw__tkudz._getvalue()
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
        zwjk__lgts = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, zwjk__lgts)


@box(MonthEndType)
def box_month_end(typ, val, c):
    thvnp__gjml = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ifhmc__uqc = c.pyapi.long_from_longlong(thvnp__gjml.n)
    wqt__cxow = c.pyapi.from_native_value(types.boolean, thvnp__gjml.
        normalize, c.env_manager)
    ibev__gyyv = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    oqnmn__avpe = c.pyapi.call_function_objargs(ibev__gyyv, (ifhmc__uqc,
        wqt__cxow))
    c.pyapi.decref(ifhmc__uqc)
    c.pyapi.decref(wqt__cxow)
    c.pyapi.decref(ibev__gyyv)
    return oqnmn__avpe


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    ifhmc__uqc = c.pyapi.object_getattr_string(val, 'n')
    wqt__cxow = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ifhmc__uqc)
    normalize = c.pyapi.to_native_value(types.bool_, wqt__cxow).value
    thvnp__gjml = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    thvnp__gjml.n = n
    thvnp__gjml.normalize = normalize
    c.pyapi.decref(ifhmc__uqc)
    c.pyapi.decref(wqt__cxow)
    rvsj__rwwh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(thvnp__gjml._getvalue(), is_error=rvsj__rwwh)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        thvnp__gjml = cgutils.create_struct_proxy(typ)(context, builder)
        thvnp__gjml.n = args[0]
        thvnp__gjml.normalize = args[1]
        return thvnp__gjml._getvalue()
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
        thvnp__gjml = get_days_in_month(year, month)
        if thvnp__gjml > day:
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
        zwjk__lgts = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, zwjk__lgts)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    vdp__xdlj = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bbgta__tqqm = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for efed__lks, jrn__glhja in enumerate(date_offset_fields):
        c.builder.store(getattr(vdp__xdlj, jrn__glhja), c.builder.inttoptr(
            c.builder.add(c.builder.ptrtoint(bbgta__tqqm, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * efed__lks)), lir.IntType(64).
            as_pointer()))
    vze__wlla = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    tyzcm__dpflf = cgutils.get_or_insert_function(c.builder.module,
        vze__wlla, name='box_date_offset')
    gvoq__igpk = c.builder.call(tyzcm__dpflf, [vdp__xdlj.n, vdp__xdlj.
        normalize, bbgta__tqqm, vdp__xdlj.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return gvoq__igpk


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    ifhmc__uqc = c.pyapi.object_getattr_string(val, 'n')
    wqt__cxow = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(ifhmc__uqc)
    normalize = c.pyapi.to_native_value(types.bool_, wqt__cxow).value
    bbgta__tqqm = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    vze__wlla = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer()])
    oalmh__kizhx = cgutils.get_or_insert_function(c.builder.module,
        vze__wlla, name='unbox_date_offset')
    has_kws = c.builder.call(oalmh__kizhx, [val, bbgta__tqqm])
    vdp__xdlj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vdp__xdlj.n = n
    vdp__xdlj.normalize = normalize
    for efed__lks, jrn__glhja in enumerate(date_offset_fields):
        setattr(vdp__xdlj, jrn__glhja, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(bbgta__tqqm, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * efed__lks)), lir.IntType(64).
            as_pointer())))
    vdp__xdlj.has_kws = has_kws
    c.pyapi.decref(ifhmc__uqc)
    c.pyapi.decref(wqt__cxow)
    rvsj__rwwh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vdp__xdlj._getvalue(), is_error=rvsj__rwwh)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    yoc__xrb = [n, normalize]
    has_kws = False
    bhegv__ienrn = [0] * 9 + [-1] * 9
    for efed__lks, jrn__glhja in enumerate(date_offset_fields):
        if hasattr(pyval, jrn__glhja):
            ixoaj__tpdg = context.get_constant(types.int64, getattr(pyval,
                jrn__glhja))
            has_kws = True
        else:
            ixoaj__tpdg = context.get_constant(types.int64, bhegv__ienrn[
                efed__lks])
        yoc__xrb.append(ixoaj__tpdg)
    has_kws = context.get_constant(types.boolean, has_kws)
    yoc__xrb.append(has_kws)
    return lir.Constant.literal_struct(yoc__xrb)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    bnew__nsq = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for jxg__ubo in bnew__nsq:
        if not is_overload_none(jxg__ubo):
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
        vdp__xdlj = cgutils.create_struct_proxy(typ)(context, builder)
        vdp__xdlj.n = args[0]
        vdp__xdlj.normalize = args[1]
        vdp__xdlj.years = args[2]
        vdp__xdlj.months = args[3]
        vdp__xdlj.weeks = args[4]
        vdp__xdlj.days = args[5]
        vdp__xdlj.hours = args[6]
        vdp__xdlj.minutes = args[7]
        vdp__xdlj.seconds = args[8]
        vdp__xdlj.microseconds = args[9]
        vdp__xdlj.nanoseconds = args[10]
        vdp__xdlj.year = args[11]
        vdp__xdlj.month = args[12]
        vdp__xdlj.day = args[13]
        vdp__xdlj.weekday = args[14]
        vdp__xdlj.hour = args[15]
        vdp__xdlj.minute = args[16]
        vdp__xdlj.second = args[17]
        vdp__xdlj.microsecond = args[18]
        vdp__xdlj.nanosecond = args[19]
        vdp__xdlj.has_kws = args[20]
        return vdp__xdlj._getvalue()
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
        rowq__yasn = -1 if dateoffset.n < 0 else 1
        for byybd__mitqu in range(np.abs(dateoffset.n)):
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
            year += rowq__yasn * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += rowq__yasn * dateoffset._months
            year, month, ofg__zhmsf = calculate_month_end_date(year, month,
                day, 0)
            if day > ofg__zhmsf:
                day = ofg__zhmsf
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
            ibe__augs = pd.Timedelta(days=dateoffset._days + 7 * dateoffset
                ._weeks, hours=dateoffset._hours, minutes=dateoffset.
                _minutes, seconds=dateoffset._seconds, microseconds=
                dateoffset._microseconds)
            ibe__augs = ibe__augs + pd.Timedelta(dateoffset._nanoseconds,
                unit='ns')
            if rowq__yasn == -1:
                ibe__augs = -ibe__augs
            ts = ts + ibe__augs
            if dateoffset._weekday != -1:
                ldnyf__rdd = ts.weekday()
                rala__iwri = (dateoffset._weekday - ldnyf__rdd) % 7
                ts = ts + pd.Timedelta(days=rala__iwri)
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
        zwjk__lgts = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, zwjk__lgts)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        amu__nfw = -1 if weekday is None else weekday
        return init_week(n, normalize, amu__nfw)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        qeq__naki = cgutils.create_struct_proxy(typ)(context, builder)
        qeq__naki.n = args[0]
        qeq__naki.normalize = args[1]
        qeq__naki.weekday = args[2]
        return qeq__naki._getvalue()
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
    qeq__naki = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ifhmc__uqc = c.pyapi.long_from_longlong(qeq__naki.n)
    wqt__cxow = c.pyapi.from_native_value(types.boolean, qeq__naki.
        normalize, c.env_manager)
    iwoh__mjyp = c.pyapi.long_from_longlong(qeq__naki.weekday)
    kknx__mrj = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    syla__tzvr = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), 
        -1), qeq__naki.weekday)
    with c.builder.if_else(syla__tzvr) as (yzie__nujl, tmjya__mmud):
        with yzie__nujl:
            zesh__eqy = c.pyapi.call_function_objargs(kknx__mrj, (
                ifhmc__uqc, wqt__cxow, iwoh__mjyp))
            egsoa__hqo = c.builder.block
        with tmjya__mmud:
            avcp__nmi = c.pyapi.call_function_objargs(kknx__mrj, (
                ifhmc__uqc, wqt__cxow))
            ixdit__ehyn = c.builder.block
    oqnmn__avpe = c.builder.phi(zesh__eqy.type)
    oqnmn__avpe.add_incoming(zesh__eqy, egsoa__hqo)
    oqnmn__avpe.add_incoming(avcp__nmi, ixdit__ehyn)
    c.pyapi.decref(iwoh__mjyp)
    c.pyapi.decref(ifhmc__uqc)
    c.pyapi.decref(wqt__cxow)
    c.pyapi.decref(kknx__mrj)
    return oqnmn__avpe


@unbox(WeekType)
def unbox_week(typ, val, c):
    ifhmc__uqc = c.pyapi.object_getattr_string(val, 'n')
    wqt__cxow = c.pyapi.object_getattr_string(val, 'normalize')
    iwoh__mjyp = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(ifhmc__uqc)
    normalize = c.pyapi.to_native_value(types.bool_, wqt__cxow).value
    hbvhj__zgce = c.pyapi.make_none()
    wruio__wja = c.builder.icmp_unsigned('==', iwoh__mjyp, hbvhj__zgce)
    with c.builder.if_else(wruio__wja) as (tmjya__mmud, yzie__nujl):
        with yzie__nujl:
            zesh__eqy = c.pyapi.long_as_longlong(iwoh__mjyp)
            egsoa__hqo = c.builder.block
        with tmjya__mmud:
            avcp__nmi = lir.Constant(lir.IntType(64), -1)
            ixdit__ehyn = c.builder.block
    oqnmn__avpe = c.builder.phi(zesh__eqy.type)
    oqnmn__avpe.add_incoming(zesh__eqy, egsoa__hqo)
    oqnmn__avpe.add_incoming(avcp__nmi, ixdit__ehyn)
    qeq__naki = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qeq__naki.n = n
    qeq__naki.normalize = normalize
    qeq__naki.weekday = oqnmn__avpe
    c.pyapi.decref(ifhmc__uqc)
    c.pyapi.decref(wqt__cxow)
    c.pyapi.decref(iwoh__mjyp)
    rvsj__rwwh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qeq__naki._getvalue(), is_error=rvsj__rwwh)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            xhzvz__xmvhl = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            if lhs.normalize:
                seal__kck = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                seal__kck = rhs
            return seal__kck + xhzvz__xmvhl
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            xhzvz__xmvhl = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            if lhs.normalize:
                seal__kck = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                seal__kck = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return seal__kck + xhzvz__xmvhl
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            xhzvz__xmvhl = calculate_week_date(lhs.n, lhs.weekday, rhs.
                weekday())
            return rhs + xhzvz__xmvhl
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
        cksi__rzh = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=cksi__rzh)


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
    for efcu__tmgfg in date_offset_unsupported_attrs:
        flo__obsg = 'pandas.tseries.offsets.DateOffset.' + efcu__tmgfg
        overload_attribute(DateOffsetType, efcu__tmgfg)(
            create_unsupported_overload(flo__obsg))
    for efcu__tmgfg in date_offset_unsupported:
        flo__obsg = 'pandas.tseries.offsets.DateOffset.' + efcu__tmgfg
        overload_method(DateOffsetType, efcu__tmgfg)(
            create_unsupported_overload(flo__obsg))


def _install_month_begin_unsupported():
    for efcu__tmgfg in month_begin_unsupported_attrs:
        flo__obsg = 'pandas.tseries.offsets.MonthBegin.' + efcu__tmgfg
        overload_attribute(MonthBeginType, efcu__tmgfg)(
            create_unsupported_overload(flo__obsg))
    for efcu__tmgfg in month_begin_unsupported:
        flo__obsg = 'pandas.tseries.offsets.MonthBegin.' + efcu__tmgfg
        overload_method(MonthBeginType, efcu__tmgfg)(
            create_unsupported_overload(flo__obsg))


def _install_month_end_unsupported():
    for efcu__tmgfg in date_offset_unsupported_attrs:
        flo__obsg = 'pandas.tseries.offsets.MonthEnd.' + efcu__tmgfg
        overload_attribute(MonthEndType, efcu__tmgfg)(
            create_unsupported_overload(flo__obsg))
    for efcu__tmgfg in date_offset_unsupported:
        flo__obsg = 'pandas.tseries.offsets.MonthEnd.' + efcu__tmgfg
        overload_method(MonthEndType, efcu__tmgfg)(create_unsupported_overload
            (flo__obsg))


def _install_week_unsupported():
    for efcu__tmgfg in week_unsupported_attrs:
        flo__obsg = 'pandas.tseries.offsets.Week.' + efcu__tmgfg
        overload_attribute(WeekType, efcu__tmgfg)(create_unsupported_overload
            (flo__obsg))
    for efcu__tmgfg in week_unsupported:
        flo__obsg = 'pandas.tseries.offsets.Week.' + efcu__tmgfg
        overload_method(WeekType, efcu__tmgfg)(create_unsupported_overload(
            flo__obsg))


def _install_offsets_unsupported():
    for ixoaj__tpdg in offsets_unsupported:
        flo__obsg = 'pandas.tseries.offsets.' + ixoaj__tpdg.__name__
        overload(ixoaj__tpdg)(create_unsupported_overload(flo__obsg))


def _install_frequencies_unsupported():
    for ixoaj__tpdg in frequencies_unsupported:
        flo__obsg = 'pandas.tseries.frequencies.' + ixoaj__tpdg.__name__
        overload(ixoaj__tpdg)(create_unsupported_overload(flo__obsg))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
