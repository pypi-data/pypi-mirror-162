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
        phk__taldt = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, phk__taldt)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    tajw__dyosa = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    cbkd__bodib = c.pyapi.long_from_longlong(tajw__dyosa.value)
    tnmu__astsm = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(tnmu__astsm, (cbkd__bodib,))
    c.pyapi.decref(cbkd__bodib)
    c.pyapi.decref(tnmu__astsm)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    cbkd__bodib = c.pyapi.object_getattr_string(val, 'value')
    btdux__xfba = c.pyapi.long_as_longlong(cbkd__bodib)
    tajw__dyosa = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tajw__dyosa.value = btdux__xfba
    c.pyapi.decref(cbkd__bodib)
    xiii__sehve = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tajw__dyosa._getvalue(), is_error=xiii__sehve)


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
            cchj__gtry = 1000 * microseconds
            return init_pd_timedelta(cchj__gtry)
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
            cchj__gtry = 1000 * microseconds
            return init_pd_timedelta(cchj__gtry)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    qqbvt__ijv, cdyh__lgfnb = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * qqbvt__ijv)
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
            wijt__jeap = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + wijt__jeap
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ydz__akvmr = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = ydz__akvmr + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            gywh__xrdo = rhs.toordinal()
            yds__hthkc = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            yoqq__oqy = rhs.microsecond
            snwm__mlq = lhs.value // 1000
            lrkl__lxpl = lhs.nanoseconds
            kxm__irci = yoqq__oqy + snwm__mlq
            imxt__krsh = 1000000 * (gywh__xrdo * 86400 + yds__hthkc
                ) + kxm__irci
            anqp__gkgx = lrkl__lxpl
            return compute_pd_timestamp(imxt__krsh, anqp__gkgx)
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
            jec__haw = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            jec__haw = jec__haw + lhs
            dtosa__fwmg, zwyb__zqvk = divmod(jec__haw.seconds, 3600)
            gcyl__ged, dclw__wuco = divmod(zwyb__zqvk, 60)
            if 0 < jec__haw.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(jec__haw
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    dtosa__fwmg, gcyl__ged, dclw__wuco, jec__haw.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            jec__haw = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            jec__haw = jec__haw + rhs
            dtosa__fwmg, zwyb__zqvk = divmod(jec__haw.seconds, 3600)
            gcyl__ged, dclw__wuco = divmod(zwyb__zqvk, 60)
            if 0 < jec__haw.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(jec__haw
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    dtosa__fwmg, gcyl__ged, dclw__wuco, jec__haw.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            wekd__dmoco = lhs.value - rhs.value
            return pd.Timedelta(wekd__dmoco)
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
            zsv__lcz = lhs
            numba.parfors.parfor.init_prange()
            n = len(zsv__lcz)
            A = alloc_datetime_timedelta_array(n)
            for ydhzd__qcb in numba.parfors.parfor.internal_prange(n):
                A[ydhzd__qcb] = zsv__lcz[ydhzd__qcb] - rhs
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
            dub__bpbr = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, dub__bpbr)
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
            omt__hoq, dub__bpbr = divmod(lhs.value, rhs.value)
            return omt__hoq, pd.Timedelta(dub__bpbr)
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
        phk__taldt = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, phk__taldt)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    tajw__dyosa = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    czi__msmj = c.pyapi.long_from_longlong(tajw__dyosa.days)
    lkfhk__dbtcg = c.pyapi.long_from_longlong(tajw__dyosa.seconds)
    nqs__qjnd = c.pyapi.long_from_longlong(tajw__dyosa.microseconds)
    tnmu__astsm = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(tnmu__astsm, (czi__msmj,
        lkfhk__dbtcg, nqs__qjnd))
    c.pyapi.decref(czi__msmj)
    c.pyapi.decref(lkfhk__dbtcg)
    c.pyapi.decref(nqs__qjnd)
    c.pyapi.decref(tnmu__astsm)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    czi__msmj = c.pyapi.object_getattr_string(val, 'days')
    lkfhk__dbtcg = c.pyapi.object_getattr_string(val, 'seconds')
    nqs__qjnd = c.pyapi.object_getattr_string(val, 'microseconds')
    ndza__ujnl = c.pyapi.long_as_longlong(czi__msmj)
    xds__xoz = c.pyapi.long_as_longlong(lkfhk__dbtcg)
    uyww__qwpuv = c.pyapi.long_as_longlong(nqs__qjnd)
    tajw__dyosa = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tajw__dyosa.days = ndza__ujnl
    tajw__dyosa.seconds = xds__xoz
    tajw__dyosa.microseconds = uyww__qwpuv
    c.pyapi.decref(czi__msmj)
    c.pyapi.decref(lkfhk__dbtcg)
    c.pyapi.decref(nqs__qjnd)
    xiii__sehve = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tajw__dyosa._getvalue(), is_error=xiii__sehve)


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
    omt__hoq, dub__bpbr = divmod(a, b)
    dub__bpbr *= 2
    tvaho__zkkej = dub__bpbr > b if b > 0 else dub__bpbr < b
    if tvaho__zkkej or dub__bpbr == b and omt__hoq % 2 == 1:
        omt__hoq += 1
    return omt__hoq


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
                kyf__ejx = _cmp(_getstate(lhs), _getstate(rhs))
                return op(kyf__ejx, 0)
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
            omt__hoq, dub__bpbr = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return omt__hoq, datetime.timedelta(0, 0, dub__bpbr)
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
    wyu__owxan = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != wyu__owxan
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
        phk__taldt = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, phk__taldt)


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
    slys__imio = types.Array(types.intp, 1, 'C')
    axwrh__avz = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        slys__imio, [n])
    cdkm__tkg = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        slys__imio, [n])
    jnoj__zhwku = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        slys__imio, [n])
    rak__ilke = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    mzchs__ppf = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [rak__ilke])
    vauu__fyjjc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    fqzs__vjm = cgutils.get_or_insert_function(c.builder.module,
        vauu__fyjjc, name='unbox_datetime_timedelta_array')
    c.builder.call(fqzs__vjm, [val, n, axwrh__avz.data, cdkm__tkg.data,
        jnoj__zhwku.data, mzchs__ppf.data])
    bazj__spskd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bazj__spskd.days_data = axwrh__avz._getvalue()
    bazj__spskd.seconds_data = cdkm__tkg._getvalue()
    bazj__spskd.microseconds_data = jnoj__zhwku._getvalue()
    bazj__spskd.null_bitmap = mzchs__ppf._getvalue()
    xiii__sehve = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bazj__spskd._getvalue(), is_error=xiii__sehve)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    zsv__lcz = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    axwrh__avz = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, zsv__lcz.days_data)
    cdkm__tkg = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, zsv__lcz.seconds_data).data
    jnoj__zhwku = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, zsv__lcz.microseconds_data).data
    ifi__wsxbc = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, zsv__lcz.null_bitmap).data
    n = c.builder.extract_value(axwrh__avz.shape, 0)
    vauu__fyjjc = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    qwosa__auux = cgutils.get_or_insert_function(c.builder.module,
        vauu__fyjjc, name='box_datetime_timedelta_array')
    nkk__fhse = c.builder.call(qwosa__auux, [n, axwrh__avz.data, cdkm__tkg,
        jnoj__zhwku, ifi__wsxbc])
    c.context.nrt.decref(c.builder, typ, val)
    return nkk__fhse


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        jxryv__txh, zyjp__bdiv, xivhu__zsndp, xlzp__vwzhk = args
        nimi__zqfkd = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        nimi__zqfkd.days_data = jxryv__txh
        nimi__zqfkd.seconds_data = zyjp__bdiv
        nimi__zqfkd.microseconds_data = xivhu__zsndp
        nimi__zqfkd.null_bitmap = xlzp__vwzhk
        context.nrt.incref(builder, signature.args[0], jxryv__txh)
        context.nrt.incref(builder, signature.args[1], zyjp__bdiv)
        context.nrt.incref(builder, signature.args[2], xivhu__zsndp)
        context.nrt.incref(builder, signature.args[3], xlzp__vwzhk)
        return nimi__zqfkd._getvalue()
    ypdwa__nayoj = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return ypdwa__nayoj, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    axwrh__avz = np.empty(n, np.int64)
    cdkm__tkg = np.empty(n, np.int64)
    jnoj__zhwku = np.empty(n, np.int64)
    dgcv__gbb = np.empty(n + 7 >> 3, np.uint8)
    for ydhzd__qcb, s in enumerate(pyval):
        ydv__cmxwk = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(dgcv__gbb, ydhzd__qcb, int(not
            ydv__cmxwk))
        if not ydv__cmxwk:
            axwrh__avz[ydhzd__qcb] = s.days
            cdkm__tkg[ydhzd__qcb] = s.seconds
            jnoj__zhwku[ydhzd__qcb] = s.microseconds
    fzww__ejs = context.get_constant_generic(builder, days_data_type,
        axwrh__avz)
    lnyra__ebew = context.get_constant_generic(builder, seconds_data_type,
        cdkm__tkg)
    jlk__hnol = context.get_constant_generic(builder,
        microseconds_data_type, jnoj__zhwku)
    zgi__zranm = context.get_constant_generic(builder, nulls_type, dgcv__gbb)
    return lir.Constant.literal_struct([fzww__ejs, lnyra__ebew, jlk__hnol,
        zgi__zranm])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    axwrh__avz = np.empty(n, dtype=np.int64)
    cdkm__tkg = np.empty(n, dtype=np.int64)
    jnoj__zhwku = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(axwrh__avz, cdkm__tkg, jnoj__zhwku,
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
            hzk__sdivd = bodo.utils.conversion.coerce_to_ndarray(ind)
            dtdcf__bxk = A._null_bitmap
            wqazc__oeezn = A._days_data[hzk__sdivd]
            rkeo__zwsvs = A._seconds_data[hzk__sdivd]
            abaj__rox = A._microseconds_data[hzk__sdivd]
            n = len(wqazc__oeezn)
            bgq__gvwjj = get_new_null_mask_bool_index(dtdcf__bxk, ind, n)
            return init_datetime_timedelta_array(wqazc__oeezn, rkeo__zwsvs,
                abaj__rox, bgq__gvwjj)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            hzk__sdivd = bodo.utils.conversion.coerce_to_ndarray(ind)
            dtdcf__bxk = A._null_bitmap
            wqazc__oeezn = A._days_data[hzk__sdivd]
            rkeo__zwsvs = A._seconds_data[hzk__sdivd]
            abaj__rox = A._microseconds_data[hzk__sdivd]
            n = len(wqazc__oeezn)
            bgq__gvwjj = get_new_null_mask_int_index(dtdcf__bxk, hzk__sdivd, n)
            return init_datetime_timedelta_array(wqazc__oeezn, rkeo__zwsvs,
                abaj__rox, bgq__gvwjj)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            dtdcf__bxk = A._null_bitmap
            wqazc__oeezn = np.ascontiguousarray(A._days_data[ind])
            rkeo__zwsvs = np.ascontiguousarray(A._seconds_data[ind])
            abaj__rox = np.ascontiguousarray(A._microseconds_data[ind])
            bgq__gvwjj = get_new_null_mask_slice_index(dtdcf__bxk, ind, n)
            return init_datetime_timedelta_array(wqazc__oeezn, rkeo__zwsvs,
                abaj__rox, bgq__gvwjj)
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
    gpf__xak = (
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
            raise BodoError(gpf__xak)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(gpf__xak)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for ydhzd__qcb in range(n):
                    A._days_data[ind[ydhzd__qcb]] = val._days
                    A._seconds_data[ind[ydhzd__qcb]] = val._seconds
                    A._microseconds_data[ind[ydhzd__qcb]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ydhzd__qcb], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for ydhzd__qcb in range(n):
                    A._days_data[ind[ydhzd__qcb]] = val._days_data[ydhzd__qcb]
                    A._seconds_data[ind[ydhzd__qcb]] = val._seconds_data[
                        ydhzd__qcb]
                    A._microseconds_data[ind[ydhzd__qcb]
                        ] = val._microseconds_data[ydhzd__qcb]
                    vseht__pog = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, ydhzd__qcb)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ydhzd__qcb], vseht__pog)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for ydhzd__qcb in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ydhzd__qcb
                        ) and ind[ydhzd__qcb]:
                        A._days_data[ydhzd__qcb] = val._days
                        A._seconds_data[ydhzd__qcb] = val._seconds
                        A._microseconds_data[ydhzd__qcb] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ydhzd__qcb, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                yqiua__jqvgk = 0
                for ydhzd__qcb in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ydhzd__qcb
                        ) and ind[ydhzd__qcb]:
                        A._days_data[ydhzd__qcb] = val._days_data[yqiua__jqvgk]
                        A._seconds_data[ydhzd__qcb] = val._seconds_data[
                            yqiua__jqvgk]
                        A._microseconds_data[ydhzd__qcb
                            ] = val._microseconds_data[yqiua__jqvgk]
                        vseht__pog = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, yqiua__jqvgk)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ydhzd__qcb, vseht__pog)
                        yqiua__jqvgk += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                hfxdz__rgwxb = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for ydhzd__qcb in range(hfxdz__rgwxb.start, hfxdz__rgwxb.
                    stop, hfxdz__rgwxb.step):
                    A._days_data[ydhzd__qcb] = val._days
                    A._seconds_data[ydhzd__qcb] = val._seconds
                    A._microseconds_data[ydhzd__qcb] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ydhzd__qcb, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                kba__zukd = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, kba__zukd, ind, n
                    )
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
            zsv__lcz = arg1
            numba.parfors.parfor.init_prange()
            n = len(zsv__lcz)
            A = alloc_datetime_timedelta_array(n)
            for ydhzd__qcb in numba.parfors.parfor.internal_prange(n):
                A[ydhzd__qcb] = zsv__lcz[ydhzd__qcb] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            mcn__jok = True
        else:
            mcn__jok = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                iessr__ocvwz = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ydhzd__qcb in numba.parfors.parfor.internal_prange(n):
                    mvx__pixlm = bodo.libs.array_kernels.isna(lhs, ydhzd__qcb)
                    zdlf__nev = bodo.libs.array_kernels.isna(rhs, ydhzd__qcb)
                    if mvx__pixlm or zdlf__nev:
                        qyozi__iubn = mcn__jok
                    else:
                        qyozi__iubn = op(lhs[ydhzd__qcb], rhs[ydhzd__qcb])
                    iessr__ocvwz[ydhzd__qcb] = qyozi__iubn
                return iessr__ocvwz
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                iessr__ocvwz = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ydhzd__qcb in numba.parfors.parfor.internal_prange(n):
                    vseht__pog = bodo.libs.array_kernels.isna(lhs, ydhzd__qcb)
                    if vseht__pog:
                        qyozi__iubn = mcn__jok
                    else:
                        qyozi__iubn = op(lhs[ydhzd__qcb], rhs)
                    iessr__ocvwz[ydhzd__qcb] = qyozi__iubn
                return iessr__ocvwz
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                iessr__ocvwz = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ydhzd__qcb in numba.parfors.parfor.internal_prange(n):
                    vseht__pog = bodo.libs.array_kernels.isna(rhs, ydhzd__qcb)
                    if vseht__pog:
                        qyozi__iubn = mcn__jok
                    else:
                        qyozi__iubn = op(lhs, rhs[ydhzd__qcb])
                    iessr__ocvwz[ydhzd__qcb] = qyozi__iubn
                return iessr__ocvwz
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for kza__iylo in timedelta_unsupported_attrs:
        lcea__ubfh = 'pandas.Timedelta.' + kza__iylo
        overload_attribute(PDTimeDeltaType, kza__iylo)(
            create_unsupported_overload(lcea__ubfh))
    for btq__pbte in timedelta_unsupported_methods:
        lcea__ubfh = 'pandas.Timedelta.' + btq__pbte
        overload_method(PDTimeDeltaType, btq__pbte)(create_unsupported_overload
            (lcea__ubfh + '()'))


_intstall_pd_timedelta_unsupported()
