"""Numba extension support for datetime.timedelta objects and their arrays.
"""
import datetime
import operator
from collections import namedtuple
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import get_new_null_mask_bool_index, get_new_null_mask_int_index, get_new_null_mask_slice_index, setitem_slice_index_null_bits
from bodo.utils.typing import BodoError, get_overload_const_str, is_iterable_type, is_list_like_index_type, is_overload_constant_str
ll.add_symbol('box_datetime_timedelta_array', hdatetime_ext.
    box_datetime_timedelta_array)
ll.add_symbol('unbox_datetime_timedelta_array', hdatetime_ext.
    unbox_datetime_timedelta_array)


class NoInput:
    pass


_no_input = NoInput()


class NoInputType(types.Type):

    def __init__(self):
        super(NoInputType, self).__init__(name='NoInput')


register_model(NoInputType)(models.OpaqueModel)


@typeof_impl.register(NoInput)
def _typ_no_input(val, c):
    return NoInputType()


@lower_constant(NoInputType)
def constant_no_input(context, builder, ty, pyval):
    return context.get_dummy_value()


class PDTimeDeltaType(types.Type):

    def __init__(self):
        super(PDTimeDeltaType, self).__init__(name='PDTimeDeltaType()')


pd_timedelta_type = PDTimeDeltaType()
types.pd_timedelta_type = pd_timedelta_type


@typeof_impl.register(pd.Timedelta)
def typeof_pd_timedelta(val, c):
    return pd_timedelta_type


@register_model(PDTimeDeltaType)
class PDTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dvyf__vqie = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, dvyf__vqie)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    pecnh__cfz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    shyg__znefj = c.pyapi.long_from_longlong(pecnh__cfz.value)
    vnrq__dtk = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(vnrq__dtk, (shyg__znefj,))
    c.pyapi.decref(shyg__znefj)
    c.pyapi.decref(vnrq__dtk)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    shyg__znefj = c.pyapi.object_getattr_string(val, 'value')
    jlodp__syssl = c.pyapi.long_as_longlong(shyg__znefj)
    pecnh__cfz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pecnh__cfz.value = jlodp__syssl
    c.pyapi.decref(shyg__znefj)
    nblxb__xtee = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pecnh__cfz._getvalue(), is_error=nblxb__xtee)


@lower_constant(PDTimeDeltaType)
def lower_constant_pd_timedelta(context, builder, ty, pyval):
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct([value])


@overload(pd.Timedelta, no_unliteral=True)
def pd_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
    microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    if value == _no_input:

        def impl_timedelta_kw(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            days += weeks * 7
            hours += days * 24
            minutes += 60 * hours
            seconds += 60 * minutes
            milliseconds += 1000 * seconds
            microseconds += 1000 * milliseconds
            kwm__tjnya = 1000 * microseconds
            return init_pd_timedelta(kwm__tjnya)
        return impl_timedelta_kw
    if value == bodo.string_type or is_overload_constant_str(value):

        def impl_str(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            with numba.objmode(res='pd_timedelta_type'):
                res = pd.Timedelta(value)
            return res
        return impl_str
    if value == pd_timedelta_type:
        return (lambda value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0: value)
    if value == datetime_timedelta_type:

        def impl_timedelta_datetime(value=_no_input, unit='ns', days=0,
            seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0,
            weeks=0):
            days = value.days
            seconds = 60 * 60 * 24 * days + value.seconds
            microseconds = 1000 * 1000 * seconds + value.microseconds
            kwm__tjnya = 1000 * microseconds
            return init_pd_timedelta(kwm__tjnya)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    hjx__syp, apfsf__dtz = pd._libs.tslibs.conversion.precision_from_unit(unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * hjx__syp)
    return impl_timedelta


@intrinsic
def init_pd_timedelta(typingctx, value):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.value = args[0]
        return timedelta._getvalue()
    return PDTimeDeltaType()(value), codegen


make_attribute_wrapper(PDTimeDeltaType, 'value', '_value')


@overload_attribute(PDTimeDeltaType, 'value')
@overload_attribute(PDTimeDeltaType, 'delta')
def pd_timedelta_get_value(td):

    def impl(td):
        return td._value
    return impl


@overload_attribute(PDTimeDeltaType, 'days')
def pd_timedelta_get_days(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000 * 60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'seconds')
def pd_timedelta_get_seconds(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000) % (60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'microseconds')
def pd_timedelta_get_microseconds(td):

    def impl(td):
        return td._value // 1000 % 1000000
    return impl


@overload_attribute(PDTimeDeltaType, 'nanoseconds')
def pd_timedelta_get_nanoseconds(td):

    def impl(td):
        return td._value % 1000
    return impl


@register_jitable
def _to_hours_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60 * 60) % 24


@register_jitable
def _to_minutes_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60) % 60


@register_jitable
def _to_seconds_pd_td(td):
    return td._value // (1000 * 1000 * 1000) % 60


@register_jitable
def _to_milliseconds_pd_td(td):
    return td._value // (1000 * 1000) % 1000


@register_jitable
def _to_microseconds_pd_td(td):
    return td._value // 1000 % 1000


Components = namedtuple('Components', ['days', 'hours', 'minutes',
    'seconds', 'milliseconds', 'microseconds', 'nanoseconds'], defaults=[0,
    0, 0, 0, 0, 0, 0])


@overload_attribute(PDTimeDeltaType, 'components', no_unliteral=True)
def pd_timedelta_get_components(td):

    def impl(td):
        a = Components(td.days, _to_hours_pd_td(td), _to_minutes_pd_td(td),
            _to_seconds_pd_td(td), _to_milliseconds_pd_td(td),
            _to_microseconds_pd_td(td), td.nanoseconds)
        return a
    return impl


@overload_method(PDTimeDeltaType, '__hash__', no_unliteral=True)
def pd_td___hash__(td):

    def impl(td):
        return hash(td._value)
    return impl


@overload_method(PDTimeDeltaType, 'to_numpy', no_unliteral=True)
@overload_method(PDTimeDeltaType, 'to_timedelta64', no_unliteral=True)
def pd_td_to_numpy(td):
    from bodo.hiframes.pd_timestamp_ext import integer_to_timedelta64

    def impl(td):
        return integer_to_timedelta64(td.value)
    return impl


@overload_method(PDTimeDeltaType, 'to_pytimedelta', no_unliteral=True)
def pd_td_to_pytimedelta(td):

    def impl(td):
        return datetime.timedelta(microseconds=np.int64(td._value / 1000))
    return impl


@overload_method(PDTimeDeltaType, 'total_seconds', no_unliteral=True)
def pd_td_total_seconds(td):

    def impl(td):
        return td._value // 1000 / 10 ** 6
    return impl


def overload_add_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            val = lhs.value + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            oktv__tkq = (rhs.microseconds + (rhs.seconds + rhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + oktv__tkq
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            myz__hnm = (lhs.microseconds + (lhs.seconds + lhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = myz__hnm + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            dgd__zmv = rhs.toordinal()
            ona__qwl = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            ddzn__vzy = rhs.microsecond
            hixcy__lpgmm = lhs.value // 1000
            ffg__ivk = lhs.nanoseconds
            etg__zdmfj = ddzn__vzy + hixcy__lpgmm
            ncxtt__ssih = 1000000 * (dgd__zmv * 86400 + ona__qwl) + etg__zdmfj
            nlusb__seno = ffg__ivk
            return compute_pd_timestamp(ncxtt__ssih, nlusb__seno)
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + rhs.to_pytimedelta()
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days + rhs.days
            s = lhs.seconds + rhs.seconds
            us = lhs.microseconds + rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            xnw__fdoj = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            xnw__fdoj = xnw__fdoj + lhs
            ccpsl__iois, bztb__xmwb = divmod(xnw__fdoj.seconds, 3600)
            yndp__jxcq, cwap__wxgy = divmod(bztb__xmwb, 60)
            if 0 < xnw__fdoj.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(xnw__fdoj
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    ccpsl__iois, yndp__jxcq, cwap__wxgy, xnw__fdoj.microseconds
                    )
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            xnw__fdoj = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            xnw__fdoj = xnw__fdoj + rhs
            ccpsl__iois, bztb__xmwb = divmod(xnw__fdoj.seconds, 3600)
            yndp__jxcq, cwap__wxgy = divmod(bztb__xmwb, 60)
            if 0 < xnw__fdoj.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(xnw__fdoj
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    ccpsl__iois, yndp__jxcq, cwap__wxgy, xnw__fdoj.microseconds
                    )
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            onmjh__oll = lhs.value - rhs.value
            return pd.Timedelta(onmjh__oll)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days - rhs.days
            s = lhs.seconds - rhs.seconds
            us = lhs.microseconds - rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            kvjt__ltdv = lhs
            numba.parfors.parfor.init_prange()
            n = len(kvjt__ltdv)
            A = alloc_datetime_timedelta_array(n)
            for ceiiv__rkk in numba.parfors.parfor.internal_prange(n):
                A[ceiiv__rkk] = kvjt__ltdv[ceiiv__rkk] - rhs
            return A
        return impl


def overload_mul_operator_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value * rhs)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(rhs.value * lhs)
        return impl
    if lhs == datetime_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            d = lhs.days * rhs
            s = lhs.seconds * rhs
            us = lhs.microseconds * rhs
            return datetime.timedelta(d, s, us)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs * rhs.days
            s = lhs * rhs.seconds
            us = lhs * rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl


def overload_floordiv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value // rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value // rhs)
        return impl


def overload_truediv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value / rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(int(lhs.value / rhs))
        return impl


def overload_mod_operator_timedeltas(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value % rhs.value)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            aubf__engkk = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, aubf__engkk)
        return impl


def pd_create_cmp_op_overload(op):

    def overload_pd_timedelta_cmp(lhs, rhs):
        if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

            def impl(lhs, rhs):
                return op(lhs.value, rhs.value)
            return impl
        if lhs == pd_timedelta_type and rhs == bodo.timedelta64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(lhs.value), rhs)
        if lhs == bodo.timedelta64ns and rhs == pd_timedelta_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(rhs.value))
    return overload_pd_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def pd_timedelta_neg(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return pd.Timedelta(-lhs.value)
        return impl


@overload(operator.pos, no_unliteral=True)
def pd_timedelta_pos(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def pd_timedelta_divmod(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            czaup__bjee, aubf__engkk = divmod(lhs.value, rhs.value)
            return czaup__bjee, pd.Timedelta(aubf__engkk)
        return impl


@overload(abs, no_unliteral=True)
def pd_timedelta_abs(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            if lhs.value < 0:
                return -lhs
            else:
                return lhs
        return impl


class DatetimeTimeDeltaType(types.Type):

    def __init__(self):
        super(DatetimeTimeDeltaType, self).__init__(name=
            'DatetimeTimeDeltaType()')


datetime_timedelta_type = DatetimeTimeDeltaType()


@typeof_impl.register(datetime.timedelta)
def typeof_datetime_timedelta(val, c):
    return datetime_timedelta_type


@register_model(DatetimeTimeDeltaType)
class DatetimeTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dvyf__vqie = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, dvyf__vqie)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    pecnh__cfz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    yue__idjon = c.pyapi.long_from_longlong(pecnh__cfz.days)
    gza__pij = c.pyapi.long_from_longlong(pecnh__cfz.seconds)
    viwz__xix = c.pyapi.long_from_longlong(pecnh__cfz.microseconds)
    vnrq__dtk = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(vnrq__dtk, (yue__idjon, gza__pij,
        viwz__xix))
    c.pyapi.decref(yue__idjon)
    c.pyapi.decref(gza__pij)
    c.pyapi.decref(viwz__xix)
    c.pyapi.decref(vnrq__dtk)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    yue__idjon = c.pyapi.object_getattr_string(val, 'days')
    gza__pij = c.pyapi.object_getattr_string(val, 'seconds')
    viwz__xix = c.pyapi.object_getattr_string(val, 'microseconds')
    tvj__hzul = c.pyapi.long_as_longlong(yue__idjon)
    geap__tih = c.pyapi.long_as_longlong(gza__pij)
    hepkn__csafg = c.pyapi.long_as_longlong(viwz__xix)
    pecnh__cfz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pecnh__cfz.days = tvj__hzul
    pecnh__cfz.seconds = geap__tih
    pecnh__cfz.microseconds = hepkn__csafg
    c.pyapi.decref(yue__idjon)
    c.pyapi.decref(gza__pij)
    c.pyapi.decref(viwz__xix)
    nblxb__xtee = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pecnh__cfz._getvalue(), is_error=nblxb__xtee)


@lower_constant(DatetimeTimeDeltaType)
def lower_constant_datetime_timedelta(context, builder, ty, pyval):
    days = context.get_constant(types.int64, pyval.days)
    seconds = context.get_constant(types.int64, pyval.seconds)
    microseconds = context.get_constant(types.int64, pyval.microseconds)
    return lir.Constant.literal_struct([days, seconds, microseconds])


@overload(datetime.timedelta, no_unliteral=True)
def datetime_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
    minutes=0, hours=0, weeks=0):

    def impl_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
        minutes=0, hours=0, weeks=0):
        d = s = us = 0
        days += weeks * 7
        seconds += minutes * 60 + hours * 3600
        microseconds += milliseconds * 1000
        d = days
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += int(seconds)
        seconds, us = divmod(microseconds, 1000000)
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += seconds
        return init_timedelta(d, s, us)
    return impl_timedelta


@intrinsic
def init_timedelta(typingctx, d, s, us):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.days = args[0]
        timedelta.seconds = args[1]
        timedelta.microseconds = args[2]
        return timedelta._getvalue()
    return DatetimeTimeDeltaType()(d, s, us), codegen


make_attribute_wrapper(DatetimeTimeDeltaType, 'days', '_days')
make_attribute_wrapper(DatetimeTimeDeltaType, 'seconds', '_seconds')
make_attribute_wrapper(DatetimeTimeDeltaType, 'microseconds', '_microseconds')


@overload_attribute(DatetimeTimeDeltaType, 'days')
def timedelta_get_days(td):

    def impl(td):
        return td._days
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'seconds')
def timedelta_get_seconds(td):

    def impl(td):
        return td._seconds
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'microseconds')
def timedelta_get_microseconds(td):

    def impl(td):
        return td._microseconds
    return impl


@overload_method(DatetimeTimeDeltaType, 'total_seconds', no_unliteral=True)
def total_seconds(td):

    def impl(td):
        return ((td._days * 86400 + td._seconds) * 10 ** 6 + td._microseconds
            ) / 10 ** 6
    return impl


@overload_method(DatetimeTimeDeltaType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        return hash((td._days, td._seconds, td._microseconds))
    return impl


@register_jitable
def _to_nanoseconds(td):
    return np.int64(((td._days * 86400 + td._seconds) * 1000000 + td.
        _microseconds) * 1000)


@register_jitable
def _to_microseconds(td):
    return (td._days * (24 * 3600) + td._seconds) * 1000000 + td._microseconds


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@register_jitable
def _getstate(td):
    return td._days, td._seconds, td._microseconds


@register_jitable
def _divide_and_round(a, b):
    czaup__bjee, aubf__engkk = divmod(a, b)
    aubf__engkk *= 2
    aez__qxjj = aubf__engkk > b if b > 0 else aubf__engkk < b
    if aez__qxjj or aubf__engkk == b and czaup__bjee % 2 == 1:
        czaup__bjee += 1
    return czaup__bjee


_MAXORDINAL = 3652059


def overload_floordiv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us // _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, us // rhs)
        return impl


def overload_truediv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us / _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, _divide_and_round(us, rhs))
        return impl


def create_cmp_op_overload(op):

    def overload_timedelta_cmp(lhs, rhs):
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

            def impl(lhs, rhs):
                dsvk__eryoe = _cmp(_getstate(lhs), _getstate(rhs))
                return op(dsvk__eryoe, 0)
            return impl
    return overload_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def timedelta_neg(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return datetime.timedelta(-lhs.days, -lhs.seconds, -lhs.
                microseconds)
        return impl


@overload(operator.pos, no_unliteral=True)
def timedelta_pos(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def timedelta_divmod(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            czaup__bjee, aubf__engkk = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return czaup__bjee, datetime.timedelta(0, 0, aubf__engkk)
        return impl


@overload(abs, no_unliteral=True)
def timedelta_abs(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            if lhs.days < 0:
                return -lhs
            else:
                return lhs
        return impl


@intrinsic
def cast_numpy_timedelta_to_int(typingctx, val=None):
    assert val in (types.NPTimedelta('ns'), types.int64)

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(val), codegen


@overload(bool, no_unliteral=True)
def timedelta_to_bool(timedelta):
    if timedelta != datetime_timedelta_type:
        return
    rtit__ldl = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != rtit__ldl
    return impl


class DatetimeTimeDeltaArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeTimeDeltaArrayType, self).__init__(name=
            'DatetimeTimeDeltaArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_timedelta_type

    def copy(self):
        return DatetimeTimeDeltaArrayType()


datetime_timedelta_array_type = DatetimeTimeDeltaArrayType()
types.datetime_timedelta_array_type = datetime_timedelta_array_type
days_data_type = types.Array(types.int64, 1, 'C')
seconds_data_type = types.Array(types.int64, 1, 'C')
microseconds_data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeTimeDeltaArrayType)
class DatetimeTimeDeltaArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dvyf__vqie = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, dvyf__vqie)


make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'days_data', '_days_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'seconds_data',
    '_seconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'microseconds_data',
    '_microseconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'null_bitmap',
    '_null_bitmap')


@overload_method(DatetimeTimeDeltaArrayType, 'copy', no_unliteral=True)
def overload_datetime_timedelta_arr_copy(A):
    return (lambda A: bodo.hiframes.datetime_timedelta_ext.
        init_datetime_timedelta_array(A._days_data.copy(), A._seconds_data.
        copy(), A._microseconds_data.copy(), A._null_bitmap.copy()))


@unbox(DatetimeTimeDeltaArrayType)
def unbox_datetime_timedelta_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    tcopf__ojl = types.Array(types.intp, 1, 'C')
    zuht__eapv = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        tcopf__ojl, [n])
    jynd__znec = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        tcopf__ojl, [n])
    dps__xgp = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        tcopf__ojl, [n])
    uqm__wcqs = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    ynjr__cilpw = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [uqm__wcqs])
    ukyu__wezpf = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    ppcox__gzpkw = cgutils.get_or_insert_function(c.builder.module,
        ukyu__wezpf, name='unbox_datetime_timedelta_array')
    c.builder.call(ppcox__gzpkw, [val, n, zuht__eapv.data, jynd__znec.data,
        dps__xgp.data, ynjr__cilpw.data])
    eqevy__xubjy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    eqevy__xubjy.days_data = zuht__eapv._getvalue()
    eqevy__xubjy.seconds_data = jynd__znec._getvalue()
    eqevy__xubjy.microseconds_data = dps__xgp._getvalue()
    eqevy__xubjy.null_bitmap = ynjr__cilpw._getvalue()
    nblxb__xtee = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(eqevy__xubjy._getvalue(), is_error=nblxb__xtee)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    kvjt__ltdv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    zuht__eapv = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, kvjt__ltdv.days_data)
    jynd__znec = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, kvjt__ltdv.seconds_data).data
    dps__xgp = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, kvjt__ltdv.microseconds_data).data
    vhoqk__kilms = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, kvjt__ltdv.null_bitmap).data
    n = c.builder.extract_value(zuht__eapv.shape, 0)
    ukyu__wezpf = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    eyriz__xph = cgutils.get_or_insert_function(c.builder.module,
        ukyu__wezpf, name='box_datetime_timedelta_array')
    fmvz__ugfft = c.builder.call(eyriz__xph, [n, zuht__eapv.data,
        jynd__znec, dps__xgp, vhoqk__kilms])
    c.context.nrt.decref(c.builder, typ, val)
    return fmvz__ugfft


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        zhapl__dclxq, ajwh__tjyx, gkr__lsgu, jcod__ygkx = args
        hrxc__zwwmn = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        hrxc__zwwmn.days_data = zhapl__dclxq
        hrxc__zwwmn.seconds_data = ajwh__tjyx
        hrxc__zwwmn.microseconds_data = gkr__lsgu
        hrxc__zwwmn.null_bitmap = jcod__ygkx
        context.nrt.incref(builder, signature.args[0], zhapl__dclxq)
        context.nrt.incref(builder, signature.args[1], ajwh__tjyx)
        context.nrt.incref(builder, signature.args[2], gkr__lsgu)
        context.nrt.incref(builder, signature.args[3], jcod__ygkx)
        return hrxc__zwwmn._getvalue()
    eir__rrb = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return eir__rrb, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    zuht__eapv = np.empty(n, np.int64)
    jynd__znec = np.empty(n, np.int64)
    dps__xgp = np.empty(n, np.int64)
    mpvi__tlntj = np.empty(n + 7 >> 3, np.uint8)
    for ceiiv__rkk, s in enumerate(pyval):
        zej__sswhk = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(mpvi__tlntj, ceiiv__rkk, int(
            not zej__sswhk))
        if not zej__sswhk:
            zuht__eapv[ceiiv__rkk] = s.days
            jynd__znec[ceiiv__rkk] = s.seconds
            dps__xgp[ceiiv__rkk] = s.microseconds
    pjad__aceac = context.get_constant_generic(builder, days_data_type,
        zuht__eapv)
    ihhw__mmko = context.get_constant_generic(builder, seconds_data_type,
        jynd__znec)
    rdsbv__zeta = context.get_constant_generic(builder,
        microseconds_data_type, dps__xgp)
    ijpt__yslr = context.get_constant_generic(builder, nulls_type, mpvi__tlntj)
    return lir.Constant.literal_struct([pjad__aceac, ihhw__mmko,
        rdsbv__zeta, ijpt__yslr])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    zuht__eapv = np.empty(n, dtype=np.int64)
    jynd__znec = np.empty(n, dtype=np.int64)
    dps__xgp = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(zuht__eapv, jynd__znec, dps__xgp,
        nulls)


def alloc_datetime_timedelta_array_equiv(self, scope, equiv_set, loc, args, kws
    ):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_timedelta_ext_alloc_datetime_timedelta_array
    ) = alloc_datetime_timedelta_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_timedelta_arr_getitem(A, ind):
    if A != datetime_timedelta_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl_int(A, ind):
            return datetime.timedelta(days=A._days_data[ind], seconds=A.
                _seconds_data[ind], microseconds=A._microseconds_data[ind])
        return impl_int
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            qpd__lxsh = bodo.utils.conversion.coerce_to_ndarray(ind)
            aah__pqnx = A._null_bitmap
            iyevr__nglrt = A._days_data[qpd__lxsh]
            zmz__wue = A._seconds_data[qpd__lxsh]
            onyy__bcvor = A._microseconds_data[qpd__lxsh]
            n = len(iyevr__nglrt)
            qknc__xpp = get_new_null_mask_bool_index(aah__pqnx, ind, n)
            return init_datetime_timedelta_array(iyevr__nglrt, zmz__wue,
                onyy__bcvor, qknc__xpp)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            qpd__lxsh = bodo.utils.conversion.coerce_to_ndarray(ind)
            aah__pqnx = A._null_bitmap
            iyevr__nglrt = A._days_data[qpd__lxsh]
            zmz__wue = A._seconds_data[qpd__lxsh]
            onyy__bcvor = A._microseconds_data[qpd__lxsh]
            n = len(iyevr__nglrt)
            qknc__xpp = get_new_null_mask_int_index(aah__pqnx, qpd__lxsh, n)
            return init_datetime_timedelta_array(iyevr__nglrt, zmz__wue,
                onyy__bcvor, qknc__xpp)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            aah__pqnx = A._null_bitmap
            iyevr__nglrt = np.ascontiguousarray(A._days_data[ind])
            zmz__wue = np.ascontiguousarray(A._seconds_data[ind])
            onyy__bcvor = np.ascontiguousarray(A._microseconds_data[ind])
            qknc__xpp = get_new_null_mask_slice_index(aah__pqnx, ind, n)
            return init_datetime_timedelta_array(iyevr__nglrt, zmz__wue,
                onyy__bcvor, qknc__xpp)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_timedelta_arr_setitem(A, ind, val):
    if A != datetime_timedelta_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    fga__jgkub = (
        f"setitem for DatetimeTimedeltaArray with indexing type {ind} received an incorrect 'value' type {val}."
        )
    if isinstance(ind, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl(A, ind, val):
                A._days_data[ind] = val._days
                A._seconds_data[ind] = val._seconds
                A._microseconds_data[ind] = val._microseconds
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, ind, 1)
            return impl
        else:
            raise BodoError(fga__jgkub)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(fga__jgkub)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for ceiiv__rkk in range(n):
                    A._days_data[ind[ceiiv__rkk]] = val._days
                    A._seconds_data[ind[ceiiv__rkk]] = val._seconds
                    A._microseconds_data[ind[ceiiv__rkk]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ceiiv__rkk], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for ceiiv__rkk in range(n):
                    A._days_data[ind[ceiiv__rkk]] = val._days_data[ceiiv__rkk]
                    A._seconds_data[ind[ceiiv__rkk]] = val._seconds_data[
                        ceiiv__rkk]
                    A._microseconds_data[ind[ceiiv__rkk]
                        ] = val._microseconds_data[ceiiv__rkk]
                    voahj__bgpdm = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, ceiiv__rkk)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ceiiv__rkk], voahj__bgpdm)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for ceiiv__rkk in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ceiiv__rkk
                        ) and ind[ceiiv__rkk]:
                        A._days_data[ceiiv__rkk] = val._days
                        A._seconds_data[ceiiv__rkk] = val._seconds
                        A._microseconds_data[ceiiv__rkk] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ceiiv__rkk, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                iem__ljz = 0
                for ceiiv__rkk in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ceiiv__rkk
                        ) and ind[ceiiv__rkk]:
                        A._days_data[ceiiv__rkk] = val._days_data[iem__ljz]
                        A._seconds_data[ceiiv__rkk] = val._seconds_data[
                            iem__ljz]
                        A._microseconds_data[ceiiv__rkk
                            ] = val._microseconds_data[iem__ljz]
                        voahj__bgpdm = (bodo.libs.int_arr_ext.
                            get_bit_bitmap_arr(val._null_bitmap, iem__ljz))
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ceiiv__rkk, voahj__bgpdm)
                        iem__ljz += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                gbdzv__occbg = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for ceiiv__rkk in range(gbdzv__occbg.start, gbdzv__occbg.
                    stop, gbdzv__occbg.step):
                    A._days_data[ceiiv__rkk] = val._days
                    A._seconds_data[ceiiv__rkk] = val._seconds
                    A._microseconds_data[ceiiv__rkk] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ceiiv__rkk, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                uqjfi__cst = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, uqjfi__cst,
                    ind, n)
            return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_timedelta_arr(A):
    if A == datetime_timedelta_array_type:
        return lambda A: len(A._days_data)


@overload_attribute(DatetimeTimeDeltaArrayType, 'shape')
def overload_datetime_timedelta_arr_shape(A):
    return lambda A: (len(A._days_data),)


@overload_attribute(DatetimeTimeDeltaArrayType, 'nbytes')
def timedelta_arr_nbytes_overload(A):
    return (lambda A: A._days_data.nbytes + A._seconds_data.nbytes + A.
        _microseconds_data.nbytes + A._null_bitmap.nbytes)


def overload_datetime_timedelta_arr_sub(arg1, arg2):
    if (arg1 == datetime_timedelta_array_type and arg2 ==
        datetime_timedelta_type):

        def impl(arg1, arg2):
            kvjt__ltdv = arg1
            numba.parfors.parfor.init_prange()
            n = len(kvjt__ltdv)
            A = alloc_datetime_timedelta_array(n)
            for ceiiv__rkk in numba.parfors.parfor.internal_prange(n):
                A[ceiiv__rkk] = kvjt__ltdv[ceiiv__rkk] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            cxvjj__btbnx = True
        else:
            cxvjj__btbnx = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                kiu__xykgx = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ceiiv__rkk in numba.parfors.parfor.internal_prange(n):
                    ntzt__mpz = bodo.libs.array_kernels.isna(lhs, ceiiv__rkk)
                    yvn__aqys = bodo.libs.array_kernels.isna(rhs, ceiiv__rkk)
                    if ntzt__mpz or yvn__aqys:
                        mppkk__czol = cxvjj__btbnx
                    else:
                        mppkk__czol = op(lhs[ceiiv__rkk], rhs[ceiiv__rkk])
                    kiu__xykgx[ceiiv__rkk] = mppkk__czol
                return kiu__xykgx
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                kiu__xykgx = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ceiiv__rkk in numba.parfors.parfor.internal_prange(n):
                    voahj__bgpdm = bodo.libs.array_kernels.isna(lhs, ceiiv__rkk
                        )
                    if voahj__bgpdm:
                        mppkk__czol = cxvjj__btbnx
                    else:
                        mppkk__czol = op(lhs[ceiiv__rkk], rhs)
                    kiu__xykgx[ceiiv__rkk] = mppkk__czol
                return kiu__xykgx
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                kiu__xykgx = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ceiiv__rkk in numba.parfors.parfor.internal_prange(n):
                    voahj__bgpdm = bodo.libs.array_kernels.isna(rhs, ceiiv__rkk
                        )
                    if voahj__bgpdm:
                        mppkk__czol = cxvjj__btbnx
                    else:
                        mppkk__czol = op(lhs, rhs[ceiiv__rkk])
                    kiu__xykgx[ceiiv__rkk] = mppkk__czol
                return kiu__xykgx
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for yswb__kub in timedelta_unsupported_attrs:
        tqnzf__xcm = 'pandas.Timedelta.' + yswb__kub
        overload_attribute(PDTimeDeltaType, yswb__kub)(
            create_unsupported_overload(tqnzf__xcm))
    for mfzb__qrnht in timedelta_unsupported_methods:
        tqnzf__xcm = 'pandas.Timedelta.' + mfzb__qrnht
        overload_method(PDTimeDeltaType, mfzb__qrnht)(
            create_unsupported_overload(tqnzf__xcm + '()'))


_intstall_pd_timedelta_unsupported()
