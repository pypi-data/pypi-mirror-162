""" Implementation of binary operators for the different types.
    Currently implemented operators:
        arith: add, sub, mul, truediv, floordiv, mod, pow
        cmp: lt, le, eq, ne, ge, gt
"""
import operator
import numba
from numba.core import types
from numba.core.imputils import lower_builtin
from numba.core.typing.builtins import machine_ints
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type, datetime_timedelta_type
from bodo.hiframes.datetime_timedelta_ext import datetime_datetime_type, datetime_timedelta_array_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import DatetimeIndexType, HeterogeneousIndexType, is_index_type
from bodo.hiframes.pd_offsets_ext import date_offset_type, month_begin_type, month_end_type, week_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.series_impl import SeriesType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.typing import BodoError, is_overload_bool, is_str_arr_type, is_timedelta_type


class SeriesCmpOpTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        lhs, rhs = args
        if cmp_timeseries(lhs, rhs) or (isinstance(lhs, DataFrameType) or
            isinstance(rhs, DataFrameType)) or not (isinstance(lhs,
            SeriesType) or isinstance(rhs, SeriesType)):
            return
        mtal__ybicy = lhs.data if isinstance(lhs, SeriesType) else lhs
        hepgp__lkyj = rhs.data if isinstance(rhs, SeriesType) else rhs
        if mtal__ybicy in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and hepgp__lkyj.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            mtal__ybicy = hepgp__lkyj.dtype
        elif hepgp__lkyj in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and mtal__ybicy.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            hepgp__lkyj = mtal__ybicy.dtype
        ewqxx__cdjgt = mtal__ybicy, hepgp__lkyj
        oumc__qnat = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            rip__gkms = self.context.resolve_function_type(self.key,
                ewqxx__cdjgt, {}).return_type
        except Exception as wgaw__iwrm:
            raise BodoError(oumc__qnat)
        if is_overload_bool(rip__gkms):
            raise BodoError(oumc__qnat)
        jwwvp__jzib = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        kiz__yzsa = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        ylbmj__rehe = types.bool_
        zvtp__hxkl = SeriesType(ylbmj__rehe, rip__gkms, jwwvp__jzib, kiz__yzsa)
        return zvtp__hxkl(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        ldv__lfnvw = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if ldv__lfnvw is None:
            ldv__lfnvw = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, ldv__lfnvw, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        mtal__ybicy = lhs.data if isinstance(lhs, SeriesType) else lhs
        hepgp__lkyj = rhs.data if isinstance(rhs, SeriesType) else rhs
        ewqxx__cdjgt = mtal__ybicy, hepgp__lkyj
        oumc__qnat = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            rip__gkms = self.context.resolve_function_type(self.key,
                ewqxx__cdjgt, {}).return_type
        except Exception as xdcj__vsm:
            raise BodoError(oumc__qnat)
        jwwvp__jzib = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        kiz__yzsa = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        ylbmj__rehe = rip__gkms.dtype
        zvtp__hxkl = SeriesType(ylbmj__rehe, rip__gkms, jwwvp__jzib, kiz__yzsa)
        return zvtp__hxkl(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        ldv__lfnvw = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if ldv__lfnvw is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                ldv__lfnvw = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, ldv__lfnvw, sig, args)
    return lower_and_or_impl


def overload_add_operator_scalars(lhs, rhs):
    if lhs == week_type or rhs == week_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_week_offset_type(lhs, rhs))
    if lhs == month_begin_type or rhs == month_begin_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_begin_offset_type(lhs, rhs))
    if lhs == month_end_type or rhs == month_end_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_month_end_offset_type(lhs, rhs))
    if lhs == date_offset_type or rhs == date_offset_type:
        return (bodo.hiframes.pd_offsets_ext.
            overload_add_operator_date_offset_type(lhs, rhs))
    if add_timestamp(lhs, rhs):
        return bodo.hiframes.pd_timestamp_ext.overload_add_operator_timestamp(
            lhs, rhs)
    if add_dt_td_and_dt_date(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_add_operator_datetime_date(lhs, rhs))
    if add_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_add_operator_datetime_timedelta(lhs, rhs))
    raise_error_if_not_numba_supported(operator.add, lhs, rhs)


def overload_sub_operator_scalars(lhs, rhs):
    if sub_offset_to_datetime_or_timestamp(lhs, rhs):
        return bodo.hiframes.pd_offsets_ext.overload_sub_operator_offsets(lhs,
            rhs)
    if lhs == pd_timestamp_type and rhs in [pd_timestamp_type,
        datetime_timedelta_type, pd_timedelta_type]:
        return bodo.hiframes.pd_timestamp_ext.overload_sub_operator_timestamp(
            lhs, rhs)
    if sub_dt_or_td(lhs, rhs):
        return (bodo.hiframes.datetime_date_ext.
            overload_sub_operator_datetime_date(lhs, rhs))
    if sub_datetime_and_timedeltas(lhs, rhs):
        return (bodo.hiframes.datetime_timedelta_ext.
            overload_sub_operator_datetime_timedelta(lhs, rhs))
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
        return (bodo.hiframes.datetime_datetime_ext.
            overload_sub_operator_datetime_datetime(lhs, rhs))
    raise_error_if_not_numba_supported(operator.sub, lhs, rhs)


def create_overload_arith_op(op):

    def overload_arith_operator(lhs, rhs):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if time_series_operation(lhs, rhs) and op in [operator.add,
            operator.sub]:
            return bodo.hiframes.series_dt_impl.create_bin_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return bodo.hiframes.series_impl.create_binary_op_overload(op)(lhs,
                rhs)
        if sub_dt_index_and_timestamp(lhs, rhs) and op == operator.sub:
            return (bodo.hiframes.pd_index_ext.
                overload_sub_operator_datetime_index(lhs, rhs))
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if args_td_and_int_array(lhs, rhs):
            return bodo.libs.int_arr_ext.get_int_array_op_pd_td(op)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if op == operator.add and (is_str_arr_type(lhs) or types.unliteral(
            lhs) == string_type):
            return bodo.libs.str_arr_ext.overload_add_operator_string_array(lhs
                , rhs)
        if op == operator.add:
            return overload_add_operator_scalars(lhs, rhs)
        if op == operator.sub:
            return overload_sub_operator_scalars(lhs, rhs)
        if op == operator.mul:
            if mul_timedelta_and_int(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mul_operator_timedelta(lhs, rhs))
            if mul_string_arr_and_int(lhs, rhs):
                return bodo.libs.str_arr_ext.overload_mul_operator_str_arr(lhs,
                    rhs)
            if mul_date_offset_and_int(lhs, rhs):
                return (bodo.hiframes.pd_offsets_ext.
                    overload_mul_date_offset_types(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op in [operator.truediv, operator.floordiv]:
            if div_timedelta_and_int(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_pd_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_pd_timedelta(lhs, rhs))
            if div_datetime_timedelta(lhs, rhs):
                if op == operator.truediv:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_truediv_operator_dt_timedelta(lhs, rhs))
                else:
                    return (bodo.hiframes.datetime_timedelta_ext.
                        overload_floordiv_operator_dt_timedelta(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.mod:
            if mod_timedeltas(lhs, rhs):
                return (bodo.hiframes.datetime_timedelta_ext.
                    overload_mod_operator_timedeltas(lhs, rhs))
            raise_error_if_not_numba_supported(op, lhs, rhs)
        if op == operator.pow:
            raise_error_if_not_numba_supported(op, lhs, rhs)
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_arith_operator


def create_overload_cmp_operator(op):

    def overload_cmp_operator(lhs, rhs):
        if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
                f'{op} operator')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
                f'{op} operator')
            return bodo.hiframes.dataframe_impl.create_binary_op_overload(op)(
                lhs, rhs)
        if cmp_timeseries(lhs, rhs):
            return bodo.hiframes.series_dt_impl.create_cmp_op_overload(op)(lhs,
                rhs)
        if isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(lhs,
            f'{op} operator')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rhs,
            f'{op} operator')
        if lhs == datetime_date_array_type or rhs == datetime_date_array_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload_arr(
                op)(lhs, rhs)
        if (lhs == datetime_timedelta_array_type or rhs ==
            datetime_timedelta_array_type):
            ldv__lfnvw = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return ldv__lfnvw(lhs, rhs)
        if is_str_arr_type(lhs) or is_str_arr_type(rhs):
            return bodo.libs.str_arr_ext.create_binary_op_overload(op)(lhs, rhs
                )
        if isinstance(lhs, Decimal128Type) and isinstance(rhs, Decimal128Type):
            return bodo.libs.decimal_arr_ext.decimal_create_cmp_op_overload(op
                )(lhs, rhs)
        if lhs == boolean_array or rhs == boolean_array:
            return bodo.libs.bool_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
            IntegerArrayType):
            return bodo.libs.int_arr_ext.create_op_overload(op, 2)(lhs, rhs)
        if binary_array_cmp(lhs, rhs):
            return bodo.libs.binary_arr_ext.create_binary_cmp_op_overload(op)(
                lhs, rhs)
        if cmp_dt_index_to_string(lhs, rhs):
            return bodo.hiframes.pd_index_ext.overload_binop_dti_str(op)(lhs,
                rhs)
        if operand_is_index(lhs) or operand_is_index(rhs):
            return bodo.hiframes.pd_index_ext.create_binary_op_overload(op)(lhs
                , rhs)
        if lhs == datetime_date_type and rhs == datetime_date_type:
            return bodo.hiframes.datetime_date_ext.create_cmp_op_overload(op)(
                lhs, rhs)
        if can_cmp_date_datetime(lhs, rhs, op):
            return (bodo.hiframes.datetime_date_ext.
                create_datetime_date_cmp_op_overload(op)(lhs, rhs))
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:
            return bodo.hiframes.datetime_datetime_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:
            return bodo.hiframes.datetime_timedelta_ext.create_cmp_op_overload(
                op)(lhs, rhs)
        if cmp_timedeltas(lhs, rhs):
            ldv__lfnvw = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return ldv__lfnvw(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    pde__ibic = lhs == datetime_timedelta_type and rhs == datetime_date_type
    exlvg__piap = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return pde__ibic or exlvg__piap


def add_timestamp(lhs, rhs):
    baizn__fzzge = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    clp__ydilb = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return baizn__fzzge or clp__ydilb


def add_datetime_and_timedeltas(lhs, rhs):
    hnhb__etumb = [datetime_timedelta_type, pd_timedelta_type]
    hdlsk__ffs = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    pst__xvy = lhs in hnhb__etumb and rhs in hnhb__etumb
    tduqa__flkr = (lhs == datetime_datetime_type and rhs in hnhb__etumb or 
        rhs == datetime_datetime_type and lhs in hnhb__etumb)
    return pst__xvy or tduqa__flkr


def mul_string_arr_and_int(lhs, rhs):
    hepgp__lkyj = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    mtal__ybicy = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return hepgp__lkyj or mtal__ybicy


def mul_timedelta_and_int(lhs, rhs):
    pde__ibic = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    exlvg__piap = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return pde__ibic or exlvg__piap


def mul_date_offset_and_int(lhs, rhs):
    jaxt__pzko = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    nwh__gidxq = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return jaxt__pzko or nwh__gidxq


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    ouh__sngrf = [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ]
    eeeac__qee = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in eeeac__qee and lhs in ouh__sngrf


def sub_dt_index_and_timestamp(lhs, rhs):
    heyt__yixmw = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    koak__cdtn = isinstance(rhs, DatetimeIndexType
        ) and lhs == pd_timestamp_type
    return heyt__yixmw or koak__cdtn


def sub_dt_or_td(lhs, rhs):
    rurw__hwggy = lhs == datetime_date_type and rhs == datetime_timedelta_type
    fdjea__zbwi = lhs == datetime_date_type and rhs == datetime_date_type
    cdzhs__dqki = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return rurw__hwggy or fdjea__zbwi or cdzhs__dqki


def sub_datetime_and_timedeltas(lhs, rhs):
    tqlep__anb = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    bob__wztkn = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return tqlep__anb or bob__wztkn


def div_timedelta_and_int(lhs, rhs):
    pst__xvy = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    xobg__leef = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return pst__xvy or xobg__leef


def div_datetime_timedelta(lhs, rhs):
    pst__xvy = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    xobg__leef = lhs == datetime_timedelta_type and rhs == types.int64
    return pst__xvy or xobg__leef


def mod_timedeltas(lhs, rhs):
    sese__rarp = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    lcfjp__cydxk = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return sese__rarp or lcfjp__cydxk


def cmp_dt_index_to_string(lhs, rhs):
    heyt__yixmw = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    koak__cdtn = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return heyt__yixmw or koak__cdtn


def cmp_timestamp_or_date(lhs, rhs):
    prhxm__pnihc = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    iap__sdpbq = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    enob__kgjq = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    bened__wxbq = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    xeocj__qwrq = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return (prhxm__pnihc or iap__sdpbq or enob__kgjq or bened__wxbq or
        xeocj__qwrq)


def cmp_timeseries(lhs, rhs):
    lub__sviq = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    cfnvs__ccnpi = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (
        bodo.utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs
        .str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    nxpzs__bku = lub__sviq or cfnvs__ccnpi
    ybot__laoeo = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    erb__sktsc = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    binq__ufemi = ybot__laoeo or erb__sktsc
    return nxpzs__bku or binq__ufemi


def cmp_timedeltas(lhs, rhs):
    pst__xvy = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in pst__xvy and rhs in pst__xvy


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    ijc__lkbpw = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return ijc__lkbpw


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    dffy__bah = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    sads__lkd = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    gurd__lgi = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    phzrg__wqce = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return dffy__bah or sads__lkd or gurd__lgi or phzrg__wqce


def args_td_and_int_array(lhs, rhs):
    flny__ilwim = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    abo__zsq = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return flny__ilwim and abo__zsq


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        exlvg__piap = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        pde__ibic = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        gtam__rjixm = exlvg__piap or pde__ibic
        hsg__ewp = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        yonah__czjo = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        phe__dwdu = hsg__ewp or yonah__czjo
        ovwd__sjxr = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        hsqso__waqw = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        pqmua__xqbk = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ohs__cos = ovwd__sjxr or hsqso__waqw or pqmua__xqbk
        llr__zvch = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        pcd__fhigp = isinstance(lhs, tys) or isinstance(rhs, tys)
        hxhb__pbrez = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (gtam__rjixm or phe__dwdu or ohs__cos or llr__zvch or
            pcd__fhigp or hxhb__pbrez)
    if op == operator.pow:
        wvyqz__tagq = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        rfp__ysri = isinstance(lhs, types.Float) and isinstance(rhs, (types
            .IntegerLiteral, types.Float, types.Integer) or rhs in types.
            unsigned_domain or rhs in types.signed_domain)
        pqmua__xqbk = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        hxhb__pbrez = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return wvyqz__tagq or rfp__ysri or pqmua__xqbk or hxhb__pbrez
    if op == operator.floordiv:
        hsqso__waqw = lhs in types.real_domain and rhs in types.real_domain
        ovwd__sjxr = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        svsw__vmh = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        pst__xvy = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, (
            types.Integer, types.Float, types.NPTimedelta))
        hxhb__pbrez = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (hsqso__waqw or ovwd__sjxr or svsw__vmh or pst__xvy or
            hxhb__pbrez)
    if op == operator.truediv:
        tgteg__utd = lhs in machine_ints and rhs in machine_ints
        hsqso__waqw = lhs in types.real_domain and rhs in types.real_domain
        pqmua__xqbk = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        ovwd__sjxr = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        svsw__vmh = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        jhmqu__hkhe = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        pst__xvy = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, (
            types.Integer, types.Float, types.NPTimedelta))
        hxhb__pbrez = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (tgteg__utd or hsqso__waqw or pqmua__xqbk or ovwd__sjxr or
            svsw__vmh or jhmqu__hkhe or pst__xvy or hxhb__pbrez)
    if op == operator.mod:
        tgteg__utd = lhs in machine_ints and rhs in machine_ints
        hsqso__waqw = lhs in types.real_domain and rhs in types.real_domain
        ovwd__sjxr = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        svsw__vmh = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        hxhb__pbrez = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        return (tgteg__utd or hsqso__waqw or ovwd__sjxr or svsw__vmh or
            hxhb__pbrez)
    if op == operator.add or op == operator.sub:
        gtam__rjixm = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        xpij__ryix = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        aekb__tedj = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        lzlp__ahf = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        ovwd__sjxr = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        hsqso__waqw = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        pqmua__xqbk = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ohs__cos = ovwd__sjxr or hsqso__waqw or pqmua__xqbk
        hxhb__pbrez = isinstance(lhs, types.Array) or isinstance(rhs, types
            .Array)
        nxyec__pgh = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        llr__zvch = isinstance(lhs, types.List) and isinstance(rhs, types.List)
        mnpsc__rkuig = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs
            , types.UnicodeType)
        vlqx__iqn = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        agdpx__ixqu = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        gys__cdy = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        paexi__myo = mnpsc__rkuig or vlqx__iqn or agdpx__ixqu or gys__cdy
        phe__dwdu = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        nrip__inq = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        ops__quc = phe__dwdu or nrip__inq
        xjle__qzk = lhs == types.NPTimedelta and rhs == types.NPDatetime
        adaoa__udx = (nxyec__pgh or llr__zvch or paexi__myo or ops__quc or
            xjle__qzk)
        yqfm__fsfs = op == operator.add and adaoa__udx
        return (gtam__rjixm or xpij__ryix or aekb__tedj or lzlp__ahf or
            ohs__cos or hxhb__pbrez or yqfm__fsfs)


def cmp_op_supported_by_numba(lhs, rhs):
    hxhb__pbrez = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    llr__zvch = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    gtam__rjixm = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    rlbxr__grwu = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    phe__dwdu = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    nxyec__pgh = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types
        .BaseTuple)
    lzlp__ahf = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    ohs__cos = isinstance(lhs, types.Number) and isinstance(rhs, types.Number)
    eft__bki = isinstance(lhs, types.Boolean) and isinstance(rhs, types.Boolean
        )
    mjk__piexn = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    uwms__bzaho = isinstance(lhs, types.DictType) and isinstance(rhs, types
        .DictType)
    fgdix__swjma = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    jvvl__oove = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (llr__zvch or gtam__rjixm or rlbxr__grwu or phe__dwdu or
        nxyec__pgh or lzlp__ahf or ohs__cos or eft__bki or mjk__piexn or
        uwms__bzaho or hxhb__pbrez or fgdix__swjma or jvvl__oove)


def raise_error_if_not_numba_supported(op, lhs, rhs):
    if arith_op_supported_by_numba(op, lhs, rhs):
        return
    raise BodoError(
        f'{op} operator not supported for data types {lhs} and {rhs}.')


def _install_series_and_or():
    for op in (operator.or_, operator.and_):
        infer_global(op)(SeriesAndOrTyper)
        lower_impl = lower_series_and_or(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)


_install_series_and_or()


def _install_cmp_ops():
    for op in (operator.lt, operator.eq, operator.ne, operator.ge, operator
        .gt, operator.le):
        infer_global(op)(SeriesCmpOpTemplate)
        lower_impl = series_cmp_op_lower(op)
        lower_builtin(op, SeriesType, SeriesType)(lower_impl)
        lower_builtin(op, SeriesType, types.Any)(lower_impl)
        lower_builtin(op, types.Any, SeriesType)(lower_impl)
        jhlr__ugf = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(jhlr__ugf)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        jhlr__ugf = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(jhlr__ugf)


install_arith_ops()
