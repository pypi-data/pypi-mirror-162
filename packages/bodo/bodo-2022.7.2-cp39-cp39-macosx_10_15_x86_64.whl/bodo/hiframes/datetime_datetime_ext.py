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
        rmh__ymn = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, rmh__ymn)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    xvf__ipmf = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    wtvc__loex = c.pyapi.long_from_longlong(xvf__ipmf.year)
    zgppt__rluoh = c.pyapi.long_from_longlong(xvf__ipmf.month)
    udy__rxzk = c.pyapi.long_from_longlong(xvf__ipmf.day)
    kotn__vnbd = c.pyapi.long_from_longlong(xvf__ipmf.hour)
    glql__xui = c.pyapi.long_from_longlong(xvf__ipmf.minute)
    tujib__joohb = c.pyapi.long_from_longlong(xvf__ipmf.second)
    rnzlm__fyg = c.pyapi.long_from_longlong(xvf__ipmf.microsecond)
    huezg__pqb = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    mcos__bkoym = c.pyapi.call_function_objargs(huezg__pqb, (wtvc__loex,
        zgppt__rluoh, udy__rxzk, kotn__vnbd, glql__xui, tujib__joohb,
        rnzlm__fyg))
    c.pyapi.decref(wtvc__loex)
    c.pyapi.decref(zgppt__rluoh)
    c.pyapi.decref(udy__rxzk)
    c.pyapi.decref(kotn__vnbd)
    c.pyapi.decref(glql__xui)
    c.pyapi.decref(tujib__joohb)
    c.pyapi.decref(rnzlm__fyg)
    c.pyapi.decref(huezg__pqb)
    return mcos__bkoym


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    wtvc__loex = c.pyapi.object_getattr_string(val, 'year')
    zgppt__rluoh = c.pyapi.object_getattr_string(val, 'month')
    udy__rxzk = c.pyapi.object_getattr_string(val, 'day')
    kotn__vnbd = c.pyapi.object_getattr_string(val, 'hour')
    glql__xui = c.pyapi.object_getattr_string(val, 'minute')
    tujib__joohb = c.pyapi.object_getattr_string(val, 'second')
    rnzlm__fyg = c.pyapi.object_getattr_string(val, 'microsecond')
    xvf__ipmf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xvf__ipmf.year = c.pyapi.long_as_longlong(wtvc__loex)
    xvf__ipmf.month = c.pyapi.long_as_longlong(zgppt__rluoh)
    xvf__ipmf.day = c.pyapi.long_as_longlong(udy__rxzk)
    xvf__ipmf.hour = c.pyapi.long_as_longlong(kotn__vnbd)
    xvf__ipmf.minute = c.pyapi.long_as_longlong(glql__xui)
    xvf__ipmf.second = c.pyapi.long_as_longlong(tujib__joohb)
    xvf__ipmf.microsecond = c.pyapi.long_as_longlong(rnzlm__fyg)
    c.pyapi.decref(wtvc__loex)
    c.pyapi.decref(zgppt__rluoh)
    c.pyapi.decref(udy__rxzk)
    c.pyapi.decref(kotn__vnbd)
    c.pyapi.decref(glql__xui)
    c.pyapi.decref(tujib__joohb)
    c.pyapi.decref(rnzlm__fyg)
    znwa__pdwr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xvf__ipmf._getvalue(), is_error=znwa__pdwr)


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
        xvf__ipmf = cgutils.create_struct_proxy(typ)(context, builder)
        xvf__ipmf.year = args[0]
        xvf__ipmf.month = args[1]
        xvf__ipmf.day = args[2]
        xvf__ipmf.hour = args[3]
        xvf__ipmf.minute = args[4]
        xvf__ipmf.second = args[5]
        xvf__ipmf.microsecond = args[6]
        return xvf__ipmf._getvalue()
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
                y, ngey__wvfus = lhs.year, rhs.year
                hzxev__vikil, dvgq__zwnos = lhs.month, rhs.month
                d, jle__yip = lhs.day, rhs.day
                vmk__whzns, fak__pamu = lhs.hour, rhs.hour
                fny__wum, yygx__yget = lhs.minute, rhs.minute
                jyhrs__tphj, dvxml__fpw = lhs.second, rhs.second
                gjj__pxd, ldc__lxuof = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, hzxev__vikil, d, vmk__whzns, fny__wum,
                    jyhrs__tphj, gjj__pxd), (ngey__wvfus, dvgq__zwnos,
                    jle__yip, fak__pamu, yygx__yget, dvxml__fpw, ldc__lxuof
                    )), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            nka__kofcs = lhs.toordinal()
            jekw__evpj = rhs.toordinal()
            sphl__xqfa = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            ugdtd__cexn = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            mer__mey = datetime.timedelta(nka__kofcs - jekw__evpj, 
                sphl__xqfa - ugdtd__cexn, lhs.microsecond - rhs.microsecond)
            return mer__mey
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    dmj__sizkm = context.make_helper(builder, fromty, value=val)
    plme__dlyi = cgutils.as_bool_bit(builder, dmj__sizkm.valid)
    with builder.if_else(plme__dlyi) as (oyc__rop, ibmhq__powd):
        with oyc__rop:
            akg__nhft = context.cast(builder, dmj__sizkm.data, fromty.type,
                toty)
            xxgaa__irp = builder.block
        with ibmhq__powd:
            keh__ast = numba.np.npdatetime.NAT
            ulvnd__thx = builder.block
    mcos__bkoym = builder.phi(akg__nhft.type)
    mcos__bkoym.add_incoming(akg__nhft, xxgaa__irp)
    mcos__bkoym.add_incoming(keh__ast, ulvnd__thx)
    return mcos__bkoym
