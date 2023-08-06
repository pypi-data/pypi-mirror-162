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
        twc__worf = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, twc__worf)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    avdjx__qwi = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ytsib__wbg = c.pyapi.long_from_longlong(avdjx__qwi.year)
    bcyj__icdt = c.pyapi.long_from_longlong(avdjx__qwi.month)
    pntwr__gieq = c.pyapi.long_from_longlong(avdjx__qwi.day)
    epehq__vuacf = c.pyapi.long_from_longlong(avdjx__qwi.hour)
    jscfo__jrl = c.pyapi.long_from_longlong(avdjx__qwi.minute)
    snpzq__iel = c.pyapi.long_from_longlong(avdjx__qwi.second)
    yao__jygm = c.pyapi.long_from_longlong(avdjx__qwi.microsecond)
    gfkue__tee = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    vqf__owy = c.pyapi.call_function_objargs(gfkue__tee, (ytsib__wbg,
        bcyj__icdt, pntwr__gieq, epehq__vuacf, jscfo__jrl, snpzq__iel,
        yao__jygm))
    c.pyapi.decref(ytsib__wbg)
    c.pyapi.decref(bcyj__icdt)
    c.pyapi.decref(pntwr__gieq)
    c.pyapi.decref(epehq__vuacf)
    c.pyapi.decref(jscfo__jrl)
    c.pyapi.decref(snpzq__iel)
    c.pyapi.decref(yao__jygm)
    c.pyapi.decref(gfkue__tee)
    return vqf__owy


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    ytsib__wbg = c.pyapi.object_getattr_string(val, 'year')
    bcyj__icdt = c.pyapi.object_getattr_string(val, 'month')
    pntwr__gieq = c.pyapi.object_getattr_string(val, 'day')
    epehq__vuacf = c.pyapi.object_getattr_string(val, 'hour')
    jscfo__jrl = c.pyapi.object_getattr_string(val, 'minute')
    snpzq__iel = c.pyapi.object_getattr_string(val, 'second')
    yao__jygm = c.pyapi.object_getattr_string(val, 'microsecond')
    avdjx__qwi = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    avdjx__qwi.year = c.pyapi.long_as_longlong(ytsib__wbg)
    avdjx__qwi.month = c.pyapi.long_as_longlong(bcyj__icdt)
    avdjx__qwi.day = c.pyapi.long_as_longlong(pntwr__gieq)
    avdjx__qwi.hour = c.pyapi.long_as_longlong(epehq__vuacf)
    avdjx__qwi.minute = c.pyapi.long_as_longlong(jscfo__jrl)
    avdjx__qwi.second = c.pyapi.long_as_longlong(snpzq__iel)
    avdjx__qwi.microsecond = c.pyapi.long_as_longlong(yao__jygm)
    c.pyapi.decref(ytsib__wbg)
    c.pyapi.decref(bcyj__icdt)
    c.pyapi.decref(pntwr__gieq)
    c.pyapi.decref(epehq__vuacf)
    c.pyapi.decref(jscfo__jrl)
    c.pyapi.decref(snpzq__iel)
    c.pyapi.decref(yao__jygm)
    kda__znsn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(avdjx__qwi._getvalue(), is_error=kda__znsn)


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
        avdjx__qwi = cgutils.create_struct_proxy(typ)(context, builder)
        avdjx__qwi.year = args[0]
        avdjx__qwi.month = args[1]
        avdjx__qwi.day = args[2]
        avdjx__qwi.hour = args[3]
        avdjx__qwi.minute = args[4]
        avdjx__qwi.second = args[5]
        avdjx__qwi.microsecond = args[6]
        return avdjx__qwi._getvalue()
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
                y, ljav__nlhg = lhs.year, rhs.year
                tfh__hyta, dkp__cpc = lhs.month, rhs.month
                d, hiuwf__lcp = lhs.day, rhs.day
                wyah__fpn, rsm__xbjm = lhs.hour, rhs.hour
                iyfbj__sizc, ovzw__ymyqw = lhs.minute, rhs.minute
                ond__jmdl, ntxgw__vkgr = lhs.second, rhs.second
                iae__dxip, cfh__jyuj = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, tfh__hyta, d, wyah__fpn, iyfbj__sizc,
                    ond__jmdl, iae__dxip), (ljav__nlhg, dkp__cpc,
                    hiuwf__lcp, rsm__xbjm, ovzw__ymyqw, ntxgw__vkgr,
                    cfh__jyuj)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            vzhhf__dvar = lhs.toordinal()
            wgpec__ugiux = rhs.toordinal()
            eatmz__yeui = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            nedx__puoi = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            kekf__ykuf = datetime.timedelta(vzhhf__dvar - wgpec__ugiux, 
                eatmz__yeui - nedx__puoi, lhs.microsecond - rhs.microsecond)
            return kekf__ykuf
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    gws__kxvc = context.make_helper(builder, fromty, value=val)
    tkkl__citw = cgutils.as_bool_bit(builder, gws__kxvc.valid)
    with builder.if_else(tkkl__citw) as (tyx__vsev, qdq__zlm):
        with tyx__vsev:
            jftl__zvja = context.cast(builder, gws__kxvc.data, fromty.type,
                toty)
            zvb__kmftl = builder.block
        with qdq__zlm:
            vph__wmp = numba.np.npdatetime.NAT
            kjudy__ppczj = builder.block
    vqf__owy = builder.phi(jftl__zvja.type)
    vqf__owy.add_incoming(jftl__zvja, zvb__kmftl)
    vqf__owy.add_incoming(vph__wmp, kjudy__ppczj)
    return vqf__owy
