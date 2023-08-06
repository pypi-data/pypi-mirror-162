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
        aco__nls = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, aco__nls)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    ukik__imh = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    fva__offu = c.pyapi.long_from_longlong(ukik__imh.value)
    spl__sfpur = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(spl__sfpur, (fva__offu,))
    c.pyapi.decref(fva__offu)
    c.pyapi.decref(spl__sfpur)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    fva__offu = c.pyapi.object_getattr_string(val, 'value')
    bjcfm__lyb = c.pyapi.long_as_longlong(fva__offu)
    ukik__imh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ukik__imh.value = bjcfm__lyb
    c.pyapi.decref(fva__offu)
    vuh__skvjn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ukik__imh._getvalue(), is_error=vuh__skvjn)


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
            ixmde__fwusb = 1000 * microseconds
            return init_pd_timedelta(ixmde__fwusb)
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
            ixmde__fwusb = 1000 * microseconds
            return init_pd_timedelta(ixmde__fwusb)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    zyve__yttqc, wqf__gno = pd._libs.tslibs.conversion.precision_from_unit(unit
        )

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * zyve__yttqc)
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
            smdm__kjrbz = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + smdm__kjrbz
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            yevvw__jvwy = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = yevvw__jvwy + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            rkpj__picmp = rhs.toordinal()
            vamj__ufw = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            dxx__fqht = rhs.microsecond
            rrl__jleo = lhs.value // 1000
            bytqz__cotnq = lhs.nanoseconds
            xsyc__sqhhd = dxx__fqht + rrl__jleo
            rvh__ozym = 1000000 * (rkpj__picmp * 86400 + vamj__ufw
                ) + xsyc__sqhhd
            dei__deyo = bytqz__cotnq
            return compute_pd_timestamp(rvh__ozym, dei__deyo)
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
            wrn__ljli = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            wrn__ljli = wrn__ljli + lhs
            yje__qjqb, reg__kisyc = divmod(wrn__ljli.seconds, 3600)
            euux__uvnod, jpron__jmok = divmod(reg__kisyc, 60)
            if 0 < wrn__ljli.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(wrn__ljli
                    .days)
                return datetime.datetime(d.year, d.month, d.day, yje__qjqb,
                    euux__uvnod, jpron__jmok, wrn__ljli.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            wrn__ljli = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            wrn__ljli = wrn__ljli + rhs
            yje__qjqb, reg__kisyc = divmod(wrn__ljli.seconds, 3600)
            euux__uvnod, jpron__jmok = divmod(reg__kisyc, 60)
            if 0 < wrn__ljli.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(wrn__ljli
                    .days)
                return datetime.datetime(d.year, d.month, d.day, yje__qjqb,
                    euux__uvnod, jpron__jmok, wrn__ljli.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            azdxr__vem = lhs.value - rhs.value
            return pd.Timedelta(azdxr__vem)
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
            ecq__pmtyh = lhs
            numba.parfors.parfor.init_prange()
            n = len(ecq__pmtyh)
            A = alloc_datetime_timedelta_array(n)
            for rora__bclwo in numba.parfors.parfor.internal_prange(n):
                A[rora__bclwo] = ecq__pmtyh[rora__bclwo] - rhs
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
            ksajq__fokvd = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, ksajq__fokvd)
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
            jejib__ztumn, ksajq__fokvd = divmod(lhs.value, rhs.value)
            return jejib__ztumn, pd.Timedelta(ksajq__fokvd)
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
        aco__nls = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, aco__nls)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    ukik__imh = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    trc__cgll = c.pyapi.long_from_longlong(ukik__imh.days)
    myh__zcgrl = c.pyapi.long_from_longlong(ukik__imh.seconds)
    mbp__blbmu = c.pyapi.long_from_longlong(ukik__imh.microseconds)
    spl__sfpur = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(spl__sfpur, (trc__cgll, myh__zcgrl,
        mbp__blbmu))
    c.pyapi.decref(trc__cgll)
    c.pyapi.decref(myh__zcgrl)
    c.pyapi.decref(mbp__blbmu)
    c.pyapi.decref(spl__sfpur)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    trc__cgll = c.pyapi.object_getattr_string(val, 'days')
    myh__zcgrl = c.pyapi.object_getattr_string(val, 'seconds')
    mbp__blbmu = c.pyapi.object_getattr_string(val, 'microseconds')
    jnov__iwmb = c.pyapi.long_as_longlong(trc__cgll)
    ksdf__uosu = c.pyapi.long_as_longlong(myh__zcgrl)
    dfpev__bfw = c.pyapi.long_as_longlong(mbp__blbmu)
    ukik__imh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ukik__imh.days = jnov__iwmb
    ukik__imh.seconds = ksdf__uosu
    ukik__imh.microseconds = dfpev__bfw
    c.pyapi.decref(trc__cgll)
    c.pyapi.decref(myh__zcgrl)
    c.pyapi.decref(mbp__blbmu)
    vuh__skvjn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ukik__imh._getvalue(), is_error=vuh__skvjn)


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
    jejib__ztumn, ksajq__fokvd = divmod(a, b)
    ksajq__fokvd *= 2
    yyu__vrnpf = ksajq__fokvd > b if b > 0 else ksajq__fokvd < b
    if yyu__vrnpf or ksajq__fokvd == b and jejib__ztumn % 2 == 1:
        jejib__ztumn += 1
    return jejib__ztumn


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
                mnts__dad = _cmp(_getstate(lhs), _getstate(rhs))
                return op(mnts__dad, 0)
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
            jejib__ztumn, ksajq__fokvd = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return jejib__ztumn, datetime.timedelta(0, 0, ksajq__fokvd)
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
    esc__tdaoq = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != esc__tdaoq
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
        aco__nls = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, aco__nls)


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
    mrmqr__euipi = types.Array(types.intp, 1, 'C')
    reb__ksfa = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        mrmqr__euipi, [n])
    udaa__vmnvw = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        mrmqr__euipi, [n])
    yoxkc__redp = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        mrmqr__euipi, [n])
    mrf__ssb = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64),
        7)), lir.Constant(lir.IntType(64), 8))
    mec__pupcx = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [mrf__ssb])
    bisnd__sbiu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    ipne__hjnv = cgutils.get_or_insert_function(c.builder.module,
        bisnd__sbiu, name='unbox_datetime_timedelta_array')
    c.builder.call(ipne__hjnv, [val, n, reb__ksfa.data, udaa__vmnvw.data,
        yoxkc__redp.data, mec__pupcx.data])
    xbon__pucp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xbon__pucp.days_data = reb__ksfa._getvalue()
    xbon__pucp.seconds_data = udaa__vmnvw._getvalue()
    xbon__pucp.microseconds_data = yoxkc__redp._getvalue()
    xbon__pucp.null_bitmap = mec__pupcx._getvalue()
    vuh__skvjn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xbon__pucp._getvalue(), is_error=vuh__skvjn)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    ecq__pmtyh = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    reb__ksfa = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, ecq__pmtyh.days_data)
    udaa__vmnvw = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, ecq__pmtyh.seconds_data).data
    yoxkc__redp = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, ecq__pmtyh.microseconds_data).data
    yjcr__sdz = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, ecq__pmtyh.null_bitmap).data
    n = c.builder.extract_value(reb__ksfa.shape, 0)
    bisnd__sbiu = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    ixqgo__ygcxh = cgutils.get_or_insert_function(c.builder.module,
        bisnd__sbiu, name='box_datetime_timedelta_array')
    txlm__hhrwg = c.builder.call(ixqgo__ygcxh, [n, reb__ksfa.data,
        udaa__vmnvw, yoxkc__redp, yjcr__sdz])
    c.context.nrt.decref(c.builder, typ, val)
    return txlm__hhrwg


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        fglw__ksnrb, efn__adrt, rsuk__pzajk, mtrr__vwkx = args
        bjlxl__rntxj = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        bjlxl__rntxj.days_data = fglw__ksnrb
        bjlxl__rntxj.seconds_data = efn__adrt
        bjlxl__rntxj.microseconds_data = rsuk__pzajk
        bjlxl__rntxj.null_bitmap = mtrr__vwkx
        context.nrt.incref(builder, signature.args[0], fglw__ksnrb)
        context.nrt.incref(builder, signature.args[1], efn__adrt)
        context.nrt.incref(builder, signature.args[2], rsuk__pzajk)
        context.nrt.incref(builder, signature.args[3], mtrr__vwkx)
        return bjlxl__rntxj._getvalue()
    gtt__awgo = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return gtt__awgo, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    reb__ksfa = np.empty(n, np.int64)
    udaa__vmnvw = np.empty(n, np.int64)
    yoxkc__redp = np.empty(n, np.int64)
    baok__iwm = np.empty(n + 7 >> 3, np.uint8)
    for rora__bclwo, s in enumerate(pyval):
        fio__vjyu = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(baok__iwm, rora__bclwo, int(
            not fio__vjyu))
        if not fio__vjyu:
            reb__ksfa[rora__bclwo] = s.days
            udaa__vmnvw[rora__bclwo] = s.seconds
            yoxkc__redp[rora__bclwo] = s.microseconds
    ounbo__rjc = context.get_constant_generic(builder, days_data_type,
        reb__ksfa)
    nnwc__ahrz = context.get_constant_generic(builder, seconds_data_type,
        udaa__vmnvw)
    jik__vyt = context.get_constant_generic(builder, microseconds_data_type,
        yoxkc__redp)
    abic__sitwm = context.get_constant_generic(builder, nulls_type, baok__iwm)
    return lir.Constant.literal_struct([ounbo__rjc, nnwc__ahrz, jik__vyt,
        abic__sitwm])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    reb__ksfa = np.empty(n, dtype=np.int64)
    udaa__vmnvw = np.empty(n, dtype=np.int64)
    yoxkc__redp = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(reb__ksfa, udaa__vmnvw,
        yoxkc__redp, nulls)


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
            qjl__jmfk = bodo.utils.conversion.coerce_to_ndarray(ind)
            vulnv__hlbzz = A._null_bitmap
            izc__dis = A._days_data[qjl__jmfk]
            cvs__xeqtf = A._seconds_data[qjl__jmfk]
            iuwf__prat = A._microseconds_data[qjl__jmfk]
            n = len(izc__dis)
            trd__sdbi = get_new_null_mask_bool_index(vulnv__hlbzz, ind, n)
            return init_datetime_timedelta_array(izc__dis, cvs__xeqtf,
                iuwf__prat, trd__sdbi)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            qjl__jmfk = bodo.utils.conversion.coerce_to_ndarray(ind)
            vulnv__hlbzz = A._null_bitmap
            izc__dis = A._days_data[qjl__jmfk]
            cvs__xeqtf = A._seconds_data[qjl__jmfk]
            iuwf__prat = A._microseconds_data[qjl__jmfk]
            n = len(izc__dis)
            trd__sdbi = get_new_null_mask_int_index(vulnv__hlbzz, qjl__jmfk, n)
            return init_datetime_timedelta_array(izc__dis, cvs__xeqtf,
                iuwf__prat, trd__sdbi)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            vulnv__hlbzz = A._null_bitmap
            izc__dis = np.ascontiguousarray(A._days_data[ind])
            cvs__xeqtf = np.ascontiguousarray(A._seconds_data[ind])
            iuwf__prat = np.ascontiguousarray(A._microseconds_data[ind])
            trd__sdbi = get_new_null_mask_slice_index(vulnv__hlbzz, ind, n)
            return init_datetime_timedelta_array(izc__dis, cvs__xeqtf,
                iuwf__prat, trd__sdbi)
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
    vdz__crt = (
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
            raise BodoError(vdz__crt)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(vdz__crt)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for rora__bclwo in range(n):
                    A._days_data[ind[rora__bclwo]] = val._days
                    A._seconds_data[ind[rora__bclwo]] = val._seconds
                    A._microseconds_data[ind[rora__bclwo]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[rora__bclwo], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for rora__bclwo in range(n):
                    A._days_data[ind[rora__bclwo]] = val._days_data[rora__bclwo
                        ]
                    A._seconds_data[ind[rora__bclwo]] = val._seconds_data[
                        rora__bclwo]
                    A._microseconds_data[ind[rora__bclwo]
                        ] = val._microseconds_data[rora__bclwo]
                    wvrl__ejib = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, rora__bclwo)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[rora__bclwo], wvrl__ejib)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for rora__bclwo in range(n):
                    if not bodo.libs.array_kernels.isna(ind, rora__bclwo
                        ) and ind[rora__bclwo]:
                        A._days_data[rora__bclwo] = val._days
                        A._seconds_data[rora__bclwo] = val._seconds
                        A._microseconds_data[rora__bclwo] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            rora__bclwo, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                smv__tjmw = 0
                for rora__bclwo in range(n):
                    if not bodo.libs.array_kernels.isna(ind, rora__bclwo
                        ) and ind[rora__bclwo]:
                        A._days_data[rora__bclwo] = val._days_data[smv__tjmw]
                        A._seconds_data[rora__bclwo] = val._seconds_data[
                            smv__tjmw]
                        A._microseconds_data[rora__bclwo
                            ] = val._microseconds_data[smv__tjmw]
                        wvrl__ejib = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, smv__tjmw)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            rora__bclwo, wvrl__ejib)
                        smv__tjmw += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                hdkxw__ony = numba.cpython.unicode._normalize_slice(ind, len(A)
                    )
                for rora__bclwo in range(hdkxw__ony.start, hdkxw__ony.stop,
                    hdkxw__ony.step):
                    A._days_data[rora__bclwo] = val._days
                    A._seconds_data[rora__bclwo] = val._seconds
                    A._microseconds_data[rora__bclwo] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        rora__bclwo, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                cix__ajqlx = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, cix__ajqlx,
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
            ecq__pmtyh = arg1
            numba.parfors.parfor.init_prange()
            n = len(ecq__pmtyh)
            A = alloc_datetime_timedelta_array(n)
            for rora__bclwo in numba.parfors.parfor.internal_prange(n):
                A[rora__bclwo] = ecq__pmtyh[rora__bclwo] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            uyb__jkcu = True
        else:
            uyb__jkcu = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                mjpjv__kthms = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for rora__bclwo in numba.parfors.parfor.internal_prange(n):
                    rhy__wdygi = bodo.libs.array_kernels.isna(lhs, rora__bclwo)
                    yxyjo__qdj = bodo.libs.array_kernels.isna(rhs, rora__bclwo)
                    if rhy__wdygi or yxyjo__qdj:
                        tnf__jqgn = uyb__jkcu
                    else:
                        tnf__jqgn = op(lhs[rora__bclwo], rhs[rora__bclwo])
                    mjpjv__kthms[rora__bclwo] = tnf__jqgn
                return mjpjv__kthms
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                mjpjv__kthms = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for rora__bclwo in numba.parfors.parfor.internal_prange(n):
                    wvrl__ejib = bodo.libs.array_kernels.isna(lhs, rora__bclwo)
                    if wvrl__ejib:
                        tnf__jqgn = uyb__jkcu
                    else:
                        tnf__jqgn = op(lhs[rora__bclwo], rhs)
                    mjpjv__kthms[rora__bclwo] = tnf__jqgn
                return mjpjv__kthms
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                mjpjv__kthms = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for rora__bclwo in numba.parfors.parfor.internal_prange(n):
                    wvrl__ejib = bodo.libs.array_kernels.isna(rhs, rora__bclwo)
                    if wvrl__ejib:
                        tnf__jqgn = uyb__jkcu
                    else:
                        tnf__jqgn = op(lhs, rhs[rora__bclwo])
                    mjpjv__kthms[rora__bclwo] = tnf__jqgn
                return mjpjv__kthms
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for elzgb__sdflt in timedelta_unsupported_attrs:
        ntlab__utmr = 'pandas.Timedelta.' + elzgb__sdflt
        overload_attribute(PDTimeDeltaType, elzgb__sdflt)(
            create_unsupported_overload(ntlab__utmr))
    for roks__wtpux in timedelta_unsupported_methods:
        ntlab__utmr = 'pandas.Timedelta.' + roks__wtpux
        overload_method(PDTimeDeltaType, roks__wtpux)(
            create_unsupported_overload(ntlab__utmr + '()'))


_intstall_pd_timedelta_unsupported()
