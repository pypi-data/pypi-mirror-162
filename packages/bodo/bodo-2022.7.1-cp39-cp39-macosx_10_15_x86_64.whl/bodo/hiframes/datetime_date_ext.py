"""Numba extension support for datetime.date objects and their arrays.
"""
import datetime
import operator
import warnings
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_builtin, lower_constant
from numba.core.typing.templates import AttributeTemplate, infer_getattr
from numba.core.utils import PYVERSION
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import DatetimeDatetimeType
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type, is_overload_int, is_overload_none
ll.add_symbol('box_datetime_date_array', hdatetime_ext.box_datetime_date_array)
ll.add_symbol('unbox_datetime_date_array', hdatetime_ext.
    unbox_datetime_date_array)
ll.add_symbol('get_isocalendar', hdatetime_ext.get_isocalendar)


class DatetimeDateType(types.Type):

    def __init__(self):
        super(DatetimeDateType, self).__init__(name='DatetimeDateType()')
        self.bitwidth = 64


datetime_date_type = DatetimeDateType()


@typeof_impl.register(datetime.date)
def typeof_datetime_date(val, c):
    return datetime_date_type


register_model(DatetimeDateType)(models.IntegerModel)


@infer_getattr
class DatetimeAttribute(AttributeTemplate):
    key = DatetimeDateType

    def resolve_year(self, typ):
        return types.int64

    def resolve_month(self, typ):
        return types.int64

    def resolve_day(self, typ):
        return types.int64


@lower_getattr(DatetimeDateType, 'year')
def datetime_get_year(context, builder, typ, val):
    return builder.lshr(val, lir.Constant(lir.IntType(64), 32))


@lower_getattr(DatetimeDateType, 'month')
def datetime_get_month(context, builder, typ, val):
    return builder.and_(builder.lshr(val, lir.Constant(lir.IntType(64), 16)
        ), lir.Constant(lir.IntType(64), 65535))


@lower_getattr(DatetimeDateType, 'day')
def datetime_get_day(context, builder, typ, val):
    return builder.and_(val, lir.Constant(lir.IntType(64), 65535))


@unbox(DatetimeDateType)
def unbox_datetime_date(typ, val, c):
    wyxfh__fdif = c.pyapi.object_getattr_string(val, 'year')
    lyxb__bkie = c.pyapi.object_getattr_string(val, 'month')
    bjtk__alev = c.pyapi.object_getattr_string(val, 'day')
    micp__pfsx = c.pyapi.long_as_longlong(wyxfh__fdif)
    syiuc__ylt = c.pyapi.long_as_longlong(lyxb__bkie)
    vckn__ksydz = c.pyapi.long_as_longlong(bjtk__alev)
    rqzx__plbtf = c.builder.add(vckn__ksydz, c.builder.add(c.builder.shl(
        micp__pfsx, lir.Constant(lir.IntType(64), 32)), c.builder.shl(
        syiuc__ylt, lir.Constant(lir.IntType(64), 16))))
    c.pyapi.decref(wyxfh__fdif)
    c.pyapi.decref(lyxb__bkie)
    c.pyapi.decref(bjtk__alev)
    yivn__ffhl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rqzx__plbtf, is_error=yivn__ffhl)


@lower_constant(DatetimeDateType)
def lower_constant_datetime_date(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    rqzx__plbtf = builder.add(day, builder.add(builder.shl(year, lir.
        Constant(lir.IntType(64), 32)), builder.shl(month, lir.Constant(lir
        .IntType(64), 16))))
    return rqzx__plbtf


@box(DatetimeDateType)
def box_datetime_date(typ, val, c):
    wyxfh__fdif = c.pyapi.long_from_longlong(c.builder.lshr(val, lir.
        Constant(lir.IntType(64), 32)))
    lyxb__bkie = c.pyapi.long_from_longlong(c.builder.and_(c.builder.lshr(
        val, lir.Constant(lir.IntType(64), 16)), lir.Constant(lir.IntType(
        64), 65535)))
    bjtk__alev = c.pyapi.long_from_longlong(c.builder.and_(val, lir.
        Constant(lir.IntType(64), 65535)))
    seonj__gfyc = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.date))
    wqh__bwoom = c.pyapi.call_function_objargs(seonj__gfyc, (wyxfh__fdif,
        lyxb__bkie, bjtk__alev))
    c.pyapi.decref(wyxfh__fdif)
    c.pyapi.decref(lyxb__bkie)
    c.pyapi.decref(bjtk__alev)
    c.pyapi.decref(seonj__gfyc)
    return wqh__bwoom


@type_callable(datetime.date)
def type_datetime_date(context):

    def typer(year, month, day):
        return datetime_date_type
    return typer


@lower_builtin(datetime.date, types.IntegerLiteral, types.IntegerLiteral,
    types.IntegerLiteral)
@lower_builtin(datetime.date, types.int64, types.int64, types.int64)
def impl_ctor_datetime_date(context, builder, sig, args):
    year, month, day = args
    rqzx__plbtf = builder.add(day, builder.add(builder.shl(year, lir.
        Constant(lir.IntType(64), 32)), builder.shl(month, lir.Constant(lir
        .IntType(64), 16))))
    return rqzx__plbtf


@intrinsic
def cast_int_to_datetime_date(typingctx, val=None):
    assert val == types.int64

    def codegen(context, builder, signature, args):
        return args[0]
    return datetime_date_type(types.int64), codegen


@intrinsic
def cast_datetime_date_to_int(typingctx, val=None):
    assert val == datetime_date_type

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(datetime_date_type), codegen


"""
Following codes are copied from
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""
_MAXORDINAL = 3652059
_DAYS_IN_MONTH = np.array([-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 
    31], dtype=np.int64)
_DAYS_BEFORE_MONTH = np.array([-1, 0, 31, 59, 90, 120, 151, 181, 212, 243, 
    273, 304, 334], dtype=np.int64)


@register_jitable
def _is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


@register_jitable
def _days_before_year(year):
    y = year - 1
    return y * 365 + y // 4 - y // 100 + y // 400


@register_jitable
def _days_in_month(year, month):
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month]


@register_jitable
def _days_before_month(year, month):
    return _DAYS_BEFORE_MONTH[month] + (month > 2 and _is_leap(year))


_DI400Y = _days_before_year(401)
_DI100Y = _days_before_year(101)
_DI4Y = _days_before_year(5)


@register_jitable
def _ymd2ord(year, month, day):
    dhudh__snq = _days_in_month(year, month)
    return _days_before_year(year) + _days_before_month(year, month) + day


@register_jitable
def _ord2ymd(n):
    n -= 1
    tvlli__zjom, n = divmod(n, _DI400Y)
    year = tvlli__zjom * 400 + 1
    hqipt__wno, n = divmod(n, _DI100Y)
    hhzr__daxat, n = divmod(n, _DI4Y)
    hyhl__vja, n = divmod(n, 365)
    year += hqipt__wno * 100 + hhzr__daxat * 4 + hyhl__vja
    if hyhl__vja == 4 or hqipt__wno == 4:
        return year - 1, 12, 31
    loms__qpd = hyhl__vja == 3 and (hhzr__daxat != 24 or hqipt__wno == 3)
    month = n + 50 >> 5
    qzmn__ddqbt = _DAYS_BEFORE_MONTH[month] + (month > 2 and loms__qpd)
    if qzmn__ddqbt > n:
        month -= 1
        qzmn__ddqbt -= _DAYS_IN_MONTH[month] + (month == 2 and loms__qpd)
    n -= qzmn__ddqbt
    return year, month, n + 1


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@intrinsic
def get_isocalendar(typingctx, dt_year, dt_month, dt_day):

    def codegen(context, builder, sig, args):
        year = cgutils.alloca_once(builder, lir.IntType(64))
        lgwz__ourbg = cgutils.alloca_once(builder, lir.IntType(64))
        idjk__znc = cgutils.alloca_once(builder, lir.IntType(64))
        pdwqq__dcjh = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
            lir.IntType(64), lir.IntType(64), lir.IntType(64).as_pointer(),
            lir.IntType(64).as_pointer(), lir.IntType(64).as_pointer()])
        sifhp__jsz = cgutils.get_or_insert_function(builder.module,
            pdwqq__dcjh, name='get_isocalendar')
        builder.call(sifhp__jsz, [args[0], args[1], args[2], year,
            lgwz__ourbg, idjk__znc])
        return cgutils.pack_array(builder, [builder.load(year), builder.
            load(lgwz__ourbg), builder.load(idjk__znc)])
    wqh__bwoom = types.Tuple([types.int64, types.int64, types.int64])(types
        .int64, types.int64, types.int64), codegen
    return wqh__bwoom


types.datetime_date_type = datetime_date_type


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_date_type'):
        d = datetime.date.today()
    return d


@register_jitable
def fromordinal_impl(n):
    y, ghdg__uovj, d = _ord2ymd(n)
    return datetime.date(y, ghdg__uovj, d)


@overload_method(DatetimeDateType, 'replace')
def replace_overload(date, year=None, month=None, day=None):
    if not is_overload_none(year) and not is_overload_int(year):
        raise BodoError('date.replace(): year must be an integer')
    elif not is_overload_none(month) and not is_overload_int(month):
        raise BodoError('date.replace(): month must be an integer')
    elif not is_overload_none(day) and not is_overload_int(day):
        raise BodoError('date.replace(): day must be an integer')

    def impl(date, year=None, month=None, day=None):
        jpgf__fvp = date.year if year is None else year
        swb__rspmj = date.month if month is None else month
        lzvpu__pzztq = date.day if day is None else day
        return datetime.date(jpgf__fvp, swb__rspmj, lzvpu__pzztq)
    return impl


@overload_method(DatetimeDatetimeType, 'toordinal', no_unliteral=True)
@overload_method(DatetimeDateType, 'toordinal', no_unliteral=True)
def toordinal(date):

    def impl(date):
        return _ymd2ord(date.year, date.month, date.day)
    return impl


@overload_method(DatetimeDatetimeType, 'weekday', no_unliteral=True)
@overload_method(DatetimeDateType, 'weekday', no_unliteral=True)
def weekday(date):

    def impl(date):
        return (date.toordinal() + 6) % 7
    return impl


@overload_method(DatetimeDateType, 'isocalendar', no_unliteral=True)
def overload_pd_timestamp_isocalendar(date):

    def impl(date):
        year, lgwz__ourbg, npr__fjsch = get_isocalendar(date.year, date.
            month, date.day)
        return year, lgwz__ourbg, npr__fjsch
    return impl


def overload_add_operator_datetime_date(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            wke__sxpi = lhs.toordinal() + rhs.days
            if 0 < wke__sxpi <= _MAXORDINAL:
                return fromordinal_impl(wke__sxpi)
            raise OverflowError('result out of range')
        return impl
    elif lhs == datetime_timedelta_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            wke__sxpi = lhs.days + rhs.toordinal()
            if 0 < wke__sxpi <= _MAXORDINAL:
                return fromordinal_impl(wke__sxpi)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_date(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + datetime.timedelta(-rhs.days)
        return impl
    elif lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            nsknc__slk = lhs.toordinal()
            hca__oidwn = rhs.toordinal()
            return datetime.timedelta(nsknc__slk - hca__oidwn)
        return impl
    if lhs == datetime_date_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            mysld__wcoj = lhs
            numba.parfors.parfor.init_prange()
            n = len(mysld__wcoj)
            A = alloc_datetime_date_array(n)
            for dwml__nejy in numba.parfors.parfor.internal_prange(n):
                A[dwml__nejy] = mysld__wcoj[dwml__nejy] - rhs
            return A
        return impl


@overload(min, no_unliteral=True)
def date_min(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@overload(max, no_unliteral=True)
def date_max(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload_method(DatetimeDateType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        yeb__the = np.uint8(td.year // 256)
        lorqg__ggtcj = np.uint8(td.year % 256)
        month = np.uint8(td.month)
        day = np.uint8(td.day)
        exgud__ggobk = yeb__the, lorqg__ggtcj, month, day
        return hash(exgud__ggobk)
    return impl


@overload(bool, inline='always', no_unliteral=True)
def date_to_bool(date):
    if date != datetime_date_type:
        return

    def impl(date):
        return True
    return impl


if PYVERSION >= (3, 9):
    IsoCalendarDate = datetime.date(2011, 1, 1).isocalendar().__class__


    class IsoCalendarDateType(types.Type):

        def __init__(self):
            super(IsoCalendarDateType, self).__init__(name=
                'IsoCalendarDateType()')
    iso_calendar_date_type = DatetimeDateType()

    @typeof_impl.register(IsoCalendarDate)
    def typeof_datetime_date(val, c):
        return iso_calendar_date_type


class DatetimeDateArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeDateArrayType, self).__init__(name=
            'DatetimeDateArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_date_type

    def copy(self):
        return DatetimeDateArrayType()


datetime_date_array_type = DatetimeDateArrayType()
types.datetime_date_array_type = datetime_date_array_type
data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeDateArrayType)
class DatetimeDateArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dict__ops = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, dict__ops)


make_attribute_wrapper(DatetimeDateArrayType, 'data', '_data')
make_attribute_wrapper(DatetimeDateArrayType, 'null_bitmap', '_null_bitmap')


@overload_method(DatetimeDateArrayType, 'copy', no_unliteral=True)
def overload_datetime_date_arr_copy(A):
    return lambda A: bodo.hiframes.datetime_date_ext.init_datetime_date_array(A
        ._data.copy(), A._null_bitmap.copy())


@overload_attribute(DatetimeDateArrayType, 'dtype')
def overload_datetime_date_arr_dtype(A):
    return lambda A: np.object_


@unbox(DatetimeDateArrayType)
def unbox_datetime_date_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    fhq__yxits = types.Array(types.intp, 1, 'C')
    qsvho__sktl = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        fhq__yxits, [n])
    swspl__kxe = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    dps__gfbwh = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [swspl__kxe])
    pdwqq__dcjh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(8).as_pointer()])
    skiqe__tgemw = cgutils.get_or_insert_function(c.builder.module,
        pdwqq__dcjh, name='unbox_datetime_date_array')
    c.builder.call(skiqe__tgemw, [val, n, qsvho__sktl.data, dps__gfbwh.data])
    gbe__yjfvu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gbe__yjfvu.data = qsvho__sktl._getvalue()
    gbe__yjfvu.null_bitmap = dps__gfbwh._getvalue()
    yivn__ffhl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gbe__yjfvu._getvalue(), is_error=yivn__ffhl)


def int_to_datetime_date_python(ia):
    return datetime.date(ia >> 32, ia >> 16 & 65535, ia & 65535)


def int_array_to_datetime_date(ia):
    return np.vectorize(int_to_datetime_date_python, otypes=[object])(ia)


@box(DatetimeDateArrayType)
def box_datetime_date_array(typ, val, c):
    mysld__wcoj = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    qsvho__sktl = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, mysld__wcoj.data)
    iwe__fwc = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, mysld__wcoj.null_bitmap).data
    n = c.builder.extract_value(qsvho__sktl.shape, 0)
    pdwqq__dcjh = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(8).as_pointer()])
    moftf__fulib = cgutils.get_or_insert_function(c.builder.module,
        pdwqq__dcjh, name='box_datetime_date_array')
    lekoz__pqy = c.builder.call(moftf__fulib, [n, qsvho__sktl.data, iwe__fwc])
    c.context.nrt.decref(c.builder, typ, val)
    return lekoz__pqy


@intrinsic
def init_datetime_date_array(typingctx, data, nulls=None):
    assert data == types.Array(types.int64, 1, 'C') or data == types.Array(
        types.NPDatetime('ns'), 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        ndbx__ikt, qfr__pnhe = args
        qoxiv__vqa = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        qoxiv__vqa.data = ndbx__ikt
        qoxiv__vqa.null_bitmap = qfr__pnhe
        context.nrt.incref(builder, signature.args[0], ndbx__ikt)
        context.nrt.incref(builder, signature.args[1], qfr__pnhe)
        return qoxiv__vqa._getvalue()
    sig = datetime_date_array_type(data, nulls)
    return sig, codegen


@lower_constant(DatetimeDateArrayType)
def lower_constant_datetime_date_arr(context, builder, typ, pyval):
    n = len(pyval)
    azcy__qizml = (1970 << 32) + (1 << 16) + 1
    qsvho__sktl = np.full(n, azcy__qizml, np.int64)
    syshc__bvl = np.empty(n + 7 >> 3, np.uint8)
    for dwml__nejy, ufkwv__ibqrq in enumerate(pyval):
        mcbz__sua = pd.isna(ufkwv__ibqrq)
        bodo.libs.int_arr_ext.set_bit_to_arr(syshc__bvl, dwml__nejy, int(
            not mcbz__sua))
        if not mcbz__sua:
            qsvho__sktl[dwml__nejy] = (ufkwv__ibqrq.year << 32) + (ufkwv__ibqrq
                .month << 16) + ufkwv__ibqrq.day
    qmyf__hpt = context.get_constant_generic(builder, data_type, qsvho__sktl)
    buo__abwg = context.get_constant_generic(builder, nulls_type, syshc__bvl)
    return lir.Constant.literal_struct([qmyf__hpt, buo__abwg])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_date_array(n):
    qsvho__sktl = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_date_array(qsvho__sktl, nulls)


def alloc_datetime_date_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_date_ext_alloc_datetime_date_array
    ) = alloc_datetime_date_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_date_arr_getitem(A, ind):
    if A != datetime_date_array_type:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: cast_int_to_datetime_date(A._data[ind])
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            npnyh__pynw, msgg__frl = array_getitem_bool_index(A, ind)
            return init_datetime_date_array(npnyh__pynw, msgg__frl)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            npnyh__pynw, msgg__frl = array_getitem_int_index(A, ind)
            return init_datetime_date_array(npnyh__pynw, msgg__frl)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            npnyh__pynw, msgg__frl = array_getitem_slice_index(A, ind)
            return init_datetime_date_array(npnyh__pynw, msgg__frl)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeDateArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_date_arr_setitem(A, idx, val):
    if A != datetime_date_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    htm__izto = (
        f"setitem for DatetimeDateArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == datetime_date_type:

            def impl(A, idx, val):
                A._data[idx] = cast_datetime_date_to_int(val)
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl
        else:
            raise BodoError(htm__izto)
    if not (is_iterable_type(val) and val.dtype == bodo.datetime_date_type or
        types.unliteral(val) == datetime_date_type):
        raise BodoError(htm__izto)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_int_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_arr_ind(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_bool_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_slice_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeDateArray with indexing type {idx} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_date_arr(A):
    if A == datetime_date_array_type:
        return lambda A: len(A._data)


@overload_attribute(DatetimeDateArrayType, 'shape')
def overload_datetime_date_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(DatetimeDateArrayType, 'nbytes')
def datetime_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


def create_cmp_op_overload(op):

    def overload_date_cmp(lhs, rhs):
        if lhs == datetime_date_type and rhs == datetime_date_type:

            def impl(lhs, rhs):
                y, yrwz__ahi = lhs.year, rhs.year
                ghdg__uovj, nyinn__cjh = lhs.month, rhs.month
                d, pujt__nsr = lhs.day, rhs.day
                return op(_cmp((y, ghdg__uovj, d), (yrwz__ahi, nyinn__cjh,
                    pujt__nsr)), 0)
            return impl
    return overload_date_cmp


def create_datetime_date_cmp_op_overload(op):

    def overload_cmp(lhs, rhs):
        brw__kar = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[op]} {rhs} is always {op == operator.ne} in Python. If this is unexpected there may be a bug in your code.'
            )
        warnings.warn(brw__kar, bodo.utils.typing.BodoWarning)
        if op == operator.eq:
            return lambda lhs, rhs: False
        elif op == operator.ne:
            return lambda lhs, rhs: True
    return overload_cmp


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            whpp__fxbl = True
        else:
            whpp__fxbl = False
        if lhs == datetime_date_array_type and rhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                xshks__vkpu = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for dwml__nejy in numba.parfors.parfor.internal_prange(n):
                    bajd__ajzty = bodo.libs.array_kernels.isna(lhs, dwml__nejy)
                    bsqu__amy = bodo.libs.array_kernels.isna(rhs, dwml__nejy)
                    if bajd__ajzty or bsqu__amy:
                        kpf__mes = whpp__fxbl
                    else:
                        kpf__mes = op(lhs[dwml__nejy], rhs[dwml__nejy])
                    xshks__vkpu[dwml__nejy] = kpf__mes
                return xshks__vkpu
            return impl
        elif lhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                xshks__vkpu = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for dwml__nejy in numba.parfors.parfor.internal_prange(n):
                    mmeg__qphz = bodo.libs.array_kernels.isna(lhs, dwml__nejy)
                    if mmeg__qphz:
                        kpf__mes = whpp__fxbl
                    else:
                        kpf__mes = op(lhs[dwml__nejy], rhs)
                    xshks__vkpu[dwml__nejy] = kpf__mes
                return xshks__vkpu
            return impl
        elif rhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                xshks__vkpu = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for dwml__nejy in numba.parfors.parfor.internal_prange(n):
                    mmeg__qphz = bodo.libs.array_kernels.isna(rhs, dwml__nejy)
                    if mmeg__qphz:
                        kpf__mes = whpp__fxbl
                    else:
                        kpf__mes = op(lhs, rhs[dwml__nejy])
                    xshks__vkpu[dwml__nejy] = kpf__mes
                return xshks__vkpu
            return impl
    return overload_date_arr_cmp
