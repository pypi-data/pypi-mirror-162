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
        nxjx__ozfbd = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, nxjx__ozfbd)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    tupj__hpjt = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    ccwhx__zde = c.pyapi.long_from_longlong(tupj__hpjt.value)
    poau__wabo = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(poau__wabo, (ccwhx__zde,))
    c.pyapi.decref(ccwhx__zde)
    c.pyapi.decref(poau__wabo)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    ccwhx__zde = c.pyapi.object_getattr_string(val, 'value')
    ljqje__aomk = c.pyapi.long_as_longlong(ccwhx__zde)
    tupj__hpjt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tupj__hpjt.value = ljqje__aomk
    c.pyapi.decref(ccwhx__zde)
    vnw__eea = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tupj__hpjt._getvalue(), is_error=vnw__eea)


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
            kdks__dgfwl = 1000 * microseconds
            return init_pd_timedelta(kdks__dgfwl)
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
            kdks__dgfwl = 1000 * microseconds
            return init_pd_timedelta(kdks__dgfwl)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    clko__rhive, lfyp__jjve = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * clko__rhive)
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
            srok__qtyq = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + srok__qtyq
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            onc__gewmk = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = onc__gewmk + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            pcf__gat = rhs.toordinal()
            stz__felea = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            gbufh__vfrr = rhs.microsecond
            kij__fdo = lhs.value // 1000
            bap__huu = lhs.nanoseconds
            yfsdo__vggml = gbufh__vfrr + kij__fdo
            ldo__wwot = 1000000 * (pcf__gat * 86400 + stz__felea
                ) + yfsdo__vggml
            pdn__tgia = bap__huu
            return compute_pd_timestamp(ldo__wwot, pdn__tgia)
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
            fnle__ycrn = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            fnle__ycrn = fnle__ycrn + lhs
            idoh__pvvj, amv__xrzy = divmod(fnle__ycrn.seconds, 3600)
            ymw__rgdc, evkr__rfptq = divmod(amv__xrzy, 60)
            if 0 < fnle__ycrn.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(fnle__ycrn
                    .days)
                return datetime.datetime(d.year, d.month, d.day, idoh__pvvj,
                    ymw__rgdc, evkr__rfptq, fnle__ycrn.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            fnle__ycrn = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            fnle__ycrn = fnle__ycrn + rhs
            idoh__pvvj, amv__xrzy = divmod(fnle__ycrn.seconds, 3600)
            ymw__rgdc, evkr__rfptq = divmod(amv__xrzy, 60)
            if 0 < fnle__ycrn.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(fnle__ycrn
                    .days)
                return datetime.datetime(d.year, d.month, d.day, idoh__pvvj,
                    ymw__rgdc, evkr__rfptq, fnle__ycrn.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            xzb__eeu = lhs.value - rhs.value
            return pd.Timedelta(xzb__eeu)
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
            afg__ertun = lhs
            numba.parfors.parfor.init_prange()
            n = len(afg__ertun)
            A = alloc_datetime_timedelta_array(n)
            for fpc__eat in numba.parfors.parfor.internal_prange(n):
                A[fpc__eat] = afg__ertun[fpc__eat] - rhs
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
            eay__uikon = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, eay__uikon)
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
            cur__giib, eay__uikon = divmod(lhs.value, rhs.value)
            return cur__giib, pd.Timedelta(eay__uikon)
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
        nxjx__ozfbd = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, nxjx__ozfbd)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    tupj__hpjt = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    awgte__jye = c.pyapi.long_from_longlong(tupj__hpjt.days)
    vcue__jpfwh = c.pyapi.long_from_longlong(tupj__hpjt.seconds)
    sak__nkn = c.pyapi.long_from_longlong(tupj__hpjt.microseconds)
    poau__wabo = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(poau__wabo, (awgte__jye,
        vcue__jpfwh, sak__nkn))
    c.pyapi.decref(awgte__jye)
    c.pyapi.decref(vcue__jpfwh)
    c.pyapi.decref(sak__nkn)
    c.pyapi.decref(poau__wabo)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    awgte__jye = c.pyapi.object_getattr_string(val, 'days')
    vcue__jpfwh = c.pyapi.object_getattr_string(val, 'seconds')
    sak__nkn = c.pyapi.object_getattr_string(val, 'microseconds')
    qvcf__tdvft = c.pyapi.long_as_longlong(awgte__jye)
    ymyl__hzmg = c.pyapi.long_as_longlong(vcue__jpfwh)
    yrkya__shs = c.pyapi.long_as_longlong(sak__nkn)
    tupj__hpjt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tupj__hpjt.days = qvcf__tdvft
    tupj__hpjt.seconds = ymyl__hzmg
    tupj__hpjt.microseconds = yrkya__shs
    c.pyapi.decref(awgte__jye)
    c.pyapi.decref(vcue__jpfwh)
    c.pyapi.decref(sak__nkn)
    vnw__eea = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tupj__hpjt._getvalue(), is_error=vnw__eea)


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
    cur__giib, eay__uikon = divmod(a, b)
    eay__uikon *= 2
    ceazf__hlwq = eay__uikon > b if b > 0 else eay__uikon < b
    if ceazf__hlwq or eay__uikon == b and cur__giib % 2 == 1:
        cur__giib += 1
    return cur__giib


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
                wekw__bih = _cmp(_getstate(lhs), _getstate(rhs))
                return op(wekw__bih, 0)
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
            cur__giib, eay__uikon = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return cur__giib, datetime.timedelta(0, 0, eay__uikon)
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
    obwkl__wjo = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != obwkl__wjo
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
        nxjx__ozfbd = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, nxjx__ozfbd)


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
    viow__shdhj = types.Array(types.intp, 1, 'C')
    wvppz__zpc = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        viow__shdhj, [n])
    zma__byte = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        viow__shdhj, [n])
    emtus__bvc = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        viow__shdhj, [n])
    xyx__nrpqb = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    yqkv__wyxgb = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [xyx__nrpqb])
    ngfe__xndk = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    vis__nmnm = cgutils.get_or_insert_function(c.builder.module, ngfe__xndk,
        name='unbox_datetime_timedelta_array')
    c.builder.call(vis__nmnm, [val, n, wvppz__zpc.data, zma__byte.data,
        emtus__bvc.data, yqkv__wyxgb.data])
    pmmv__cfau = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pmmv__cfau.days_data = wvppz__zpc._getvalue()
    pmmv__cfau.seconds_data = zma__byte._getvalue()
    pmmv__cfau.microseconds_data = emtus__bvc._getvalue()
    pmmv__cfau.null_bitmap = yqkv__wyxgb._getvalue()
    vnw__eea = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pmmv__cfau._getvalue(), is_error=vnw__eea)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    afg__ertun = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    wvppz__zpc = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, afg__ertun.days_data)
    zma__byte = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, afg__ertun.seconds_data).data
    emtus__bvc = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, afg__ertun.microseconds_data).data
    etxb__peaaw = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, afg__ertun.null_bitmap).data
    n = c.builder.extract_value(wvppz__zpc.shape, 0)
    ngfe__xndk = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    toek__uyr = cgutils.get_or_insert_function(c.builder.module, ngfe__xndk,
        name='box_datetime_timedelta_array')
    iae__dupu = c.builder.call(toek__uyr, [n, wvppz__zpc.data, zma__byte,
        emtus__bvc, etxb__peaaw])
    c.context.nrt.decref(c.builder, typ, val)
    return iae__dupu


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        jdu__snoal, lvag__kat, sjq__dpfzi, ktmfh__zgal = args
        seh__vzao = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        seh__vzao.days_data = jdu__snoal
        seh__vzao.seconds_data = lvag__kat
        seh__vzao.microseconds_data = sjq__dpfzi
        seh__vzao.null_bitmap = ktmfh__zgal
        context.nrt.incref(builder, signature.args[0], jdu__snoal)
        context.nrt.incref(builder, signature.args[1], lvag__kat)
        context.nrt.incref(builder, signature.args[2], sjq__dpfzi)
        context.nrt.incref(builder, signature.args[3], ktmfh__zgal)
        return seh__vzao._getvalue()
    wrgd__mrynd = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return wrgd__mrynd, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    wvppz__zpc = np.empty(n, np.int64)
    zma__byte = np.empty(n, np.int64)
    emtus__bvc = np.empty(n, np.int64)
    opwu__orvoo = np.empty(n + 7 >> 3, np.uint8)
    for fpc__eat, s in enumerate(pyval):
        kwc__wwxr = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(opwu__orvoo, fpc__eat, int(not
            kwc__wwxr))
        if not kwc__wwxr:
            wvppz__zpc[fpc__eat] = s.days
            zma__byte[fpc__eat] = s.seconds
            emtus__bvc[fpc__eat] = s.microseconds
    upae__tze = context.get_constant_generic(builder, days_data_type,
        wvppz__zpc)
    bjkw__cweaa = context.get_constant_generic(builder, seconds_data_type,
        zma__byte)
    mxl__lpswr = context.get_constant_generic(builder,
        microseconds_data_type, emtus__bvc)
    jozf__zbub = context.get_constant_generic(builder, nulls_type, opwu__orvoo)
    return lir.Constant.literal_struct([upae__tze, bjkw__cweaa, mxl__lpswr,
        jozf__zbub])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    wvppz__zpc = np.empty(n, dtype=np.int64)
    zma__byte = np.empty(n, dtype=np.int64)
    emtus__bvc = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(wvppz__zpc, zma__byte, emtus__bvc,
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
            gsnb__uswvx = bodo.utils.conversion.coerce_to_ndarray(ind)
            nbetk__lpvtj = A._null_bitmap
            cdnfn__xefgt = A._days_data[gsnb__uswvx]
            kzbk__bolvt = A._seconds_data[gsnb__uswvx]
            ditkz__upp = A._microseconds_data[gsnb__uswvx]
            n = len(cdnfn__xefgt)
            iyk__sgf = get_new_null_mask_bool_index(nbetk__lpvtj, ind, n)
            return init_datetime_timedelta_array(cdnfn__xefgt, kzbk__bolvt,
                ditkz__upp, iyk__sgf)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            gsnb__uswvx = bodo.utils.conversion.coerce_to_ndarray(ind)
            nbetk__lpvtj = A._null_bitmap
            cdnfn__xefgt = A._days_data[gsnb__uswvx]
            kzbk__bolvt = A._seconds_data[gsnb__uswvx]
            ditkz__upp = A._microseconds_data[gsnb__uswvx]
            n = len(cdnfn__xefgt)
            iyk__sgf = get_new_null_mask_int_index(nbetk__lpvtj, gsnb__uswvx, n
                )
            return init_datetime_timedelta_array(cdnfn__xefgt, kzbk__bolvt,
                ditkz__upp, iyk__sgf)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            nbetk__lpvtj = A._null_bitmap
            cdnfn__xefgt = np.ascontiguousarray(A._days_data[ind])
            kzbk__bolvt = np.ascontiguousarray(A._seconds_data[ind])
            ditkz__upp = np.ascontiguousarray(A._microseconds_data[ind])
            iyk__sgf = get_new_null_mask_slice_index(nbetk__lpvtj, ind, n)
            return init_datetime_timedelta_array(cdnfn__xefgt, kzbk__bolvt,
                ditkz__upp, iyk__sgf)
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
    lzk__bxbfr = (
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
            raise BodoError(lzk__bxbfr)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(lzk__bxbfr)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for fpc__eat in range(n):
                    A._days_data[ind[fpc__eat]] = val._days
                    A._seconds_data[ind[fpc__eat]] = val._seconds
                    A._microseconds_data[ind[fpc__eat]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[fpc__eat], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for fpc__eat in range(n):
                    A._days_data[ind[fpc__eat]] = val._days_data[fpc__eat]
                    A._seconds_data[ind[fpc__eat]] = val._seconds_data[fpc__eat
                        ]
                    A._microseconds_data[ind[fpc__eat]
                        ] = val._microseconds_data[fpc__eat]
                    eezzz__btq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, fpc__eat)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[fpc__eat], eezzz__btq)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for fpc__eat in range(n):
                    if not bodo.libs.array_kernels.isna(ind, fpc__eat) and ind[
                        fpc__eat]:
                        A._days_data[fpc__eat] = val._days
                        A._seconds_data[fpc__eat] = val._seconds
                        A._microseconds_data[fpc__eat] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            fpc__eat, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                kqz__zsgyb = 0
                for fpc__eat in range(n):
                    if not bodo.libs.array_kernels.isna(ind, fpc__eat) and ind[
                        fpc__eat]:
                        A._days_data[fpc__eat] = val._days_data[kqz__zsgyb]
                        A._seconds_data[fpc__eat] = val._seconds_data[
                            kqz__zsgyb]
                        A._microseconds_data[fpc__eat
                            ] = val._microseconds_data[kqz__zsgyb]
                        eezzz__btq = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, kqz__zsgyb)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            fpc__eat, eezzz__btq)
                        kqz__zsgyb += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                vusf__gzzvo = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for fpc__eat in range(vusf__gzzvo.start, vusf__gzzvo.stop,
                    vusf__gzzvo.step):
                    A._days_data[fpc__eat] = val._days
                    A._seconds_data[fpc__eat] = val._seconds
                    A._microseconds_data[fpc__eat] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        fpc__eat, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                grg__qcrel = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, grg__qcrel,
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
            afg__ertun = arg1
            numba.parfors.parfor.init_prange()
            n = len(afg__ertun)
            A = alloc_datetime_timedelta_array(n)
            for fpc__eat in numba.parfors.parfor.internal_prange(n):
                A[fpc__eat] = afg__ertun[fpc__eat] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            vkd__ompff = True
        else:
            vkd__ompff = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                hzmqr__tliz = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for fpc__eat in numba.parfors.parfor.internal_prange(n):
                    bvn__oqopk = bodo.libs.array_kernels.isna(lhs, fpc__eat)
                    ksovl__blq = bodo.libs.array_kernels.isna(rhs, fpc__eat)
                    if bvn__oqopk or ksovl__blq:
                        awh__jfjam = vkd__ompff
                    else:
                        awh__jfjam = op(lhs[fpc__eat], rhs[fpc__eat])
                    hzmqr__tliz[fpc__eat] = awh__jfjam
                return hzmqr__tliz
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                hzmqr__tliz = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for fpc__eat in numba.parfors.parfor.internal_prange(n):
                    eezzz__btq = bodo.libs.array_kernels.isna(lhs, fpc__eat)
                    if eezzz__btq:
                        awh__jfjam = vkd__ompff
                    else:
                        awh__jfjam = op(lhs[fpc__eat], rhs)
                    hzmqr__tliz[fpc__eat] = awh__jfjam
                return hzmqr__tliz
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                hzmqr__tliz = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for fpc__eat in numba.parfors.parfor.internal_prange(n):
                    eezzz__btq = bodo.libs.array_kernels.isna(rhs, fpc__eat)
                    if eezzz__btq:
                        awh__jfjam = vkd__ompff
                    else:
                        awh__jfjam = op(lhs, rhs[fpc__eat])
                    hzmqr__tliz[fpc__eat] = awh__jfjam
                return hzmqr__tliz
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for jct__wfvr in timedelta_unsupported_attrs:
        cqs__fcrdo = 'pandas.Timedelta.' + jct__wfvr
        overload_attribute(PDTimeDeltaType, jct__wfvr)(
            create_unsupported_overload(cqs__fcrdo))
    for mah__lhoh in timedelta_unsupported_methods:
        cqs__fcrdo = 'pandas.Timedelta.' + mah__lhoh
        overload_method(PDTimeDeltaType, mah__lhoh)(create_unsupported_overload
            (cqs__fcrdo + '()'))


_intstall_pd_timedelta_unsupported()
