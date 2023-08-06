import datetime
import numba
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
"""
Implementation is based on
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""


class DatetimeDatetimeType(types.Type):

    def __init__(self):
        super(DatetimeDatetimeType, self).__init__(name=
            'DatetimeDatetimeType()')


datetime_datetime_type = DatetimeDatetimeType()
types.datetime_datetime_type = datetime_datetime_type


@typeof_impl.register(datetime.datetime)
def typeof_datetime_datetime(val, c):
    return datetime_datetime_type


@register_model(DatetimeDatetimeType)
class DatetimeDateTimeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        odwvh__kjgg = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, odwvh__kjgg)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    gjgu__yktks = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    hqip__qrt = c.pyapi.long_from_longlong(gjgu__yktks.year)
    nau__qtsp = c.pyapi.long_from_longlong(gjgu__yktks.month)
    dogih__dub = c.pyapi.long_from_longlong(gjgu__yktks.day)
    xxh__dvxh = c.pyapi.long_from_longlong(gjgu__yktks.hour)
    mrqx__wdgp = c.pyapi.long_from_longlong(gjgu__yktks.minute)
    fxy__zevfg = c.pyapi.long_from_longlong(gjgu__yktks.second)
    dzgj__ulmgt = c.pyapi.long_from_longlong(gjgu__yktks.microsecond)
    fvybf__fgumi = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    esg__oyzbo = c.pyapi.call_function_objargs(fvybf__fgumi, (hqip__qrt,
        nau__qtsp, dogih__dub, xxh__dvxh, mrqx__wdgp, fxy__zevfg, dzgj__ulmgt))
    c.pyapi.decref(hqip__qrt)
    c.pyapi.decref(nau__qtsp)
    c.pyapi.decref(dogih__dub)
    c.pyapi.decref(xxh__dvxh)
    c.pyapi.decref(mrqx__wdgp)
    c.pyapi.decref(fxy__zevfg)
    c.pyapi.decref(dzgj__ulmgt)
    c.pyapi.decref(fvybf__fgumi)
    return esg__oyzbo


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    hqip__qrt = c.pyapi.object_getattr_string(val, 'year')
    nau__qtsp = c.pyapi.object_getattr_string(val, 'month')
    dogih__dub = c.pyapi.object_getattr_string(val, 'day')
    xxh__dvxh = c.pyapi.object_getattr_string(val, 'hour')
    mrqx__wdgp = c.pyapi.object_getattr_string(val, 'minute')
    fxy__zevfg = c.pyapi.object_getattr_string(val, 'second')
    dzgj__ulmgt = c.pyapi.object_getattr_string(val, 'microsecond')
    gjgu__yktks = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gjgu__yktks.year = c.pyapi.long_as_longlong(hqip__qrt)
    gjgu__yktks.month = c.pyapi.long_as_longlong(nau__qtsp)
    gjgu__yktks.day = c.pyapi.long_as_longlong(dogih__dub)
    gjgu__yktks.hour = c.pyapi.long_as_longlong(xxh__dvxh)
    gjgu__yktks.minute = c.pyapi.long_as_longlong(mrqx__wdgp)
    gjgu__yktks.second = c.pyapi.long_as_longlong(fxy__zevfg)
    gjgu__yktks.microsecond = c.pyapi.long_as_longlong(dzgj__ulmgt)
    c.pyapi.decref(hqip__qrt)
    c.pyapi.decref(nau__qtsp)
    c.pyapi.decref(dogih__dub)
    c.pyapi.decref(xxh__dvxh)
    c.pyapi.decref(mrqx__wdgp)
    c.pyapi.decref(fxy__zevfg)
    c.pyapi.decref(dzgj__ulmgt)
    zdb__ulgyf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gjgu__yktks._getvalue(), is_error=zdb__ulgyf)


@lower_constant(DatetimeDatetimeType)
def constant_datetime(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    return lir.Constant.literal_struct([year, month, day, hour, minute,
        second, microsecond])


@overload(datetime.datetime, no_unliteral=True)
def datetime_datetime(year, month, day, hour=0, minute=0, second=0,
    microsecond=0):

    def impl_datetime(year, month, day, hour=0, minute=0, second=0,
        microsecond=0):
        return init_datetime(year, month, day, hour, minute, second,
            microsecond)
    return impl_datetime


@intrinsic
def init_datetime(typingctx, year, month, day, hour, minute, second,
    microsecond):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        gjgu__yktks = cgutils.create_struct_proxy(typ)(context, builder)
        gjgu__yktks.year = args[0]
        gjgu__yktks.month = args[1]
        gjgu__yktks.day = args[2]
        gjgu__yktks.hour = args[3]
        gjgu__yktks.minute = args[4]
        gjgu__yktks.second = args[5]
        gjgu__yktks.microsecond = args[6]
        return gjgu__yktks._getvalue()
    return DatetimeDatetimeType()(year, month, day, hour, minute, second,
        microsecond), codegen


make_attribute_wrapper(DatetimeDatetimeType, 'year', '_year')
make_attribute_wrapper(DatetimeDatetimeType, 'month', '_month')
make_attribute_wrapper(DatetimeDatetimeType, 'day', '_day')
make_attribute_wrapper(DatetimeDatetimeType, 'hour', '_hour')
make_attribute_wrapper(DatetimeDatetimeType, 'minute', '_minute')
make_attribute_wrapper(DatetimeDatetimeType, 'second', '_second')
make_attribute_wrapper(DatetimeDatetimeType, 'microsecond', '_microsecond')


@overload_attribute(DatetimeDatetimeType, 'year')
def datetime_get_year(dt):

    def impl(dt):
        return dt._year
    return impl


@overload_attribute(DatetimeDatetimeType, 'month')
def datetime_get_month(dt):

    def impl(dt):
        return dt._month
    return impl


@overload_attribute(DatetimeDatetimeType, 'day')
def datetime_get_day(dt):

    def impl(dt):
        return dt._day
    return impl


@overload_attribute(DatetimeDatetimeType, 'hour')
def datetime_get_hour(dt):

    def impl(dt):
        return dt._hour
    return impl


@overload_attribute(DatetimeDatetimeType, 'minute')
def datetime_get_minute(dt):

    def impl(dt):
        return dt._minute
    return impl


@overload_attribute(DatetimeDatetimeType, 'second')
def datetime_get_second(dt):

    def impl(dt):
        return dt._second
    return impl


@overload_attribute(DatetimeDatetimeType, 'microsecond')
def datetime_get_microsecond(dt):

    def impl(dt):
        return dt._microsecond
    return impl


@overload_method(DatetimeDatetimeType, 'date', no_unliteral=True)
def date(dt):

    def impl(dt):
        return datetime.date(dt.year, dt.month, dt.day)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.now()
    return d


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.today()
    return d


@register_jitable
def strptime_impl(date_string, dtformat):
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.strptime(date_string, dtformat)
    return d


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def create_cmp_op_overload(op):

    def overload_datetime_cmp(lhs, rhs):
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

            def impl(lhs, rhs):
                y, sakq__rdw = lhs.year, rhs.year
                dbb__gwcp, umzq__keox = lhs.month, rhs.month
                d, wde__ign = lhs.day, rhs.day
                yiv__mrq, oxtm__guvyg = lhs.hour, rhs.hour
                aihwb__oxl, rlwh__urcdj = lhs.minute, rhs.minute
                dnc__wkx, pqxj__hwuj = lhs.second, rhs.second
                coh__mlxvr, yvmqt__fzip = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, dbb__gwcp, d, yiv__mrq, aihwb__oxl,
                    dnc__wkx, coh__mlxvr), (sakq__rdw, umzq__keox, wde__ign,
                    oxtm__guvyg, rlwh__urcdj, pqxj__hwuj, yvmqt__fzip)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            khv__lqlq = lhs.toordinal()
            pibmi__ikjct = rhs.toordinal()
            wvqav__xhf = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ldzgf__lhh = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            cvijg__odsx = datetime.timedelta(khv__lqlq - pibmi__ikjct, 
                wvqav__xhf - ldzgf__lhh, lhs.microsecond - rhs.microsecond)
            return cvijg__odsx
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    law__vki = context.make_helper(builder, fromty, value=val)
    vreq__heaj = cgutils.as_bool_bit(builder, law__vki.valid)
    with builder.if_else(vreq__heaj) as (ilqsj__dipwf, xsq__xhqm):
        with ilqsj__dipwf:
            siy__qbby = context.cast(builder, law__vki.data, fromty.type, toty)
            xwx__wwrc = builder.block
        with xsq__xhqm:
            rzob__rgxgf = numba.np.npdatetime.NAT
            thuek__johh = builder.block
    esg__oyzbo = builder.phi(siy__qbby.type)
    esg__oyzbo.add_incoming(siy__qbby, xwx__wwrc)
    esg__oyzbo.add_incoming(rzob__rgxgf, thuek__johh)
    return esg__oyzbo
