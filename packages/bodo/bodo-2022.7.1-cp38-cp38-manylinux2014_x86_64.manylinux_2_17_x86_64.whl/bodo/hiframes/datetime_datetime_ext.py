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
        nnzb__dwoya = [('year', types.int64), ('month', types.int64), (
            'day', types.int64), ('hour', types.int64), ('minute', types.
            int64), ('second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, nnzb__dwoya)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    mhsaz__pmw = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    uccb__llwi = c.pyapi.long_from_longlong(mhsaz__pmw.year)
    cucb__iyflw = c.pyapi.long_from_longlong(mhsaz__pmw.month)
    bbl__buxs = c.pyapi.long_from_longlong(mhsaz__pmw.day)
    tpsow__hhid = c.pyapi.long_from_longlong(mhsaz__pmw.hour)
    xofg__ksvo = c.pyapi.long_from_longlong(mhsaz__pmw.minute)
    gugg__acua = c.pyapi.long_from_longlong(mhsaz__pmw.second)
    hqya__yhdzo = c.pyapi.long_from_longlong(mhsaz__pmw.microsecond)
    yfqtq__mseb = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    hhu__dnbdu = c.pyapi.call_function_objargs(yfqtq__mseb, (uccb__llwi,
        cucb__iyflw, bbl__buxs, tpsow__hhid, xofg__ksvo, gugg__acua,
        hqya__yhdzo))
    c.pyapi.decref(uccb__llwi)
    c.pyapi.decref(cucb__iyflw)
    c.pyapi.decref(bbl__buxs)
    c.pyapi.decref(tpsow__hhid)
    c.pyapi.decref(xofg__ksvo)
    c.pyapi.decref(gugg__acua)
    c.pyapi.decref(hqya__yhdzo)
    c.pyapi.decref(yfqtq__mseb)
    return hhu__dnbdu


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    uccb__llwi = c.pyapi.object_getattr_string(val, 'year')
    cucb__iyflw = c.pyapi.object_getattr_string(val, 'month')
    bbl__buxs = c.pyapi.object_getattr_string(val, 'day')
    tpsow__hhid = c.pyapi.object_getattr_string(val, 'hour')
    xofg__ksvo = c.pyapi.object_getattr_string(val, 'minute')
    gugg__acua = c.pyapi.object_getattr_string(val, 'second')
    hqya__yhdzo = c.pyapi.object_getattr_string(val, 'microsecond')
    mhsaz__pmw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mhsaz__pmw.year = c.pyapi.long_as_longlong(uccb__llwi)
    mhsaz__pmw.month = c.pyapi.long_as_longlong(cucb__iyflw)
    mhsaz__pmw.day = c.pyapi.long_as_longlong(bbl__buxs)
    mhsaz__pmw.hour = c.pyapi.long_as_longlong(tpsow__hhid)
    mhsaz__pmw.minute = c.pyapi.long_as_longlong(xofg__ksvo)
    mhsaz__pmw.second = c.pyapi.long_as_longlong(gugg__acua)
    mhsaz__pmw.microsecond = c.pyapi.long_as_longlong(hqya__yhdzo)
    c.pyapi.decref(uccb__llwi)
    c.pyapi.decref(cucb__iyflw)
    c.pyapi.decref(bbl__buxs)
    c.pyapi.decref(tpsow__hhid)
    c.pyapi.decref(xofg__ksvo)
    c.pyapi.decref(gugg__acua)
    c.pyapi.decref(hqya__yhdzo)
    exc__zsf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mhsaz__pmw._getvalue(), is_error=exc__zsf)


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
        mhsaz__pmw = cgutils.create_struct_proxy(typ)(context, builder)
        mhsaz__pmw.year = args[0]
        mhsaz__pmw.month = args[1]
        mhsaz__pmw.day = args[2]
        mhsaz__pmw.hour = args[3]
        mhsaz__pmw.minute = args[4]
        mhsaz__pmw.second = args[5]
        mhsaz__pmw.microsecond = args[6]
        return mhsaz__pmw._getvalue()
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
                y, rnlp__nplv = lhs.year, rhs.year
                ueas__vifr, zxve__lcok = lhs.month, rhs.month
                d, gtvpx__sxstb = lhs.day, rhs.day
                aikx__lutj, ftyox__pkyx = lhs.hour, rhs.hour
                bss__rrzj, enwv__ztmoz = lhs.minute, rhs.minute
                aiyz__tjad, wqrhi__gehs = lhs.second, rhs.second
                dgx__lyra, jqnt__ely = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, ueas__vifr, d, aikx__lutj, bss__rrzj,
                    aiyz__tjad, dgx__lyra), (rnlp__nplv, zxve__lcok,
                    gtvpx__sxstb, ftyox__pkyx, enwv__ztmoz, wqrhi__gehs,
                    jqnt__ely)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            veh__xlppw = lhs.toordinal()
            iddec__oyfiz = rhs.toordinal()
            norq__duqd = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            konh__pypk = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            kmb__ata = datetime.timedelta(veh__xlppw - iddec__oyfiz, 
                norq__duqd - konh__pypk, lhs.microsecond - rhs.microsecond)
            return kmb__ata
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    ykp__bssh = context.make_helper(builder, fromty, value=val)
    nvgky__zmoi = cgutils.as_bool_bit(builder, ykp__bssh.valid)
    with builder.if_else(nvgky__zmoi) as (mxc__zypy, fgk__bwnkg):
        with mxc__zypy:
            bbb__tnadz = context.cast(builder, ykp__bssh.data, fromty.type,
                toty)
            cexbo__uba = builder.block
        with fgk__bwnkg:
            cukiq__cpux = numba.np.npdatetime.NAT
            onqqg__vkhyh = builder.block
    hhu__dnbdu = builder.phi(bbb__tnadz.type)
    hhu__dnbdu.add_incoming(bbb__tnadz, cexbo__uba)
    hhu__dnbdu.add_incoming(cukiq__cpux, onqqg__vkhyh)
    return hhu__dnbdu
