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
        nrxjf__pbxb = lhs.data if isinstance(lhs, SeriesType) else lhs
        ojupj__hosv = rhs.data if isinstance(rhs, SeriesType) else rhs
        if nrxjf__pbxb in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and ojupj__hosv.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            nrxjf__pbxb = ojupj__hosv.dtype
        elif ojupj__hosv in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and nrxjf__pbxb.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            ojupj__hosv = nrxjf__pbxb.dtype
        fxirs__hbty = nrxjf__pbxb, ojupj__hosv
        fkgxg__gqmtv = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            nehd__iqc = self.context.resolve_function_type(self.key,
                fxirs__hbty, {}).return_type
        except Exception as pxsem__vpqv:
            raise BodoError(fkgxg__gqmtv)
        if is_overload_bool(nehd__iqc):
            raise BodoError(fkgxg__gqmtv)
        tjj__jya = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        liykm__sao = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        gjgxh__wwnh = types.bool_
        uwer__vhrz = SeriesType(gjgxh__wwnh, nehd__iqc, tjj__jya, liykm__sao)
        return uwer__vhrz(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        vxxgq__sop = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if vxxgq__sop is None:
            vxxgq__sop = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, vxxgq__sop, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        nrxjf__pbxb = lhs.data if isinstance(lhs, SeriesType) else lhs
        ojupj__hosv = rhs.data if isinstance(rhs, SeriesType) else rhs
        fxirs__hbty = nrxjf__pbxb, ojupj__hosv
        fkgxg__gqmtv = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            nehd__iqc = self.context.resolve_function_type(self.key,
                fxirs__hbty, {}).return_type
        except Exception as wal__fygk:
            raise BodoError(fkgxg__gqmtv)
        tjj__jya = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        liykm__sao = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        gjgxh__wwnh = nehd__iqc.dtype
        uwer__vhrz = SeriesType(gjgxh__wwnh, nehd__iqc, tjj__jya, liykm__sao)
        return uwer__vhrz(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        vxxgq__sop = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if vxxgq__sop is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                vxxgq__sop = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, vxxgq__sop, sig, args)
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
            vxxgq__sop = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return vxxgq__sop(lhs, rhs)
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
            vxxgq__sop = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return vxxgq__sop(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    hjff__zeje = lhs == datetime_timedelta_type and rhs == datetime_date_type
    glmm__qoq = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return hjff__zeje or glmm__qoq


def add_timestamp(lhs, rhs):
    yudj__cviw = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    ctus__rbfe = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return yudj__cviw or ctus__rbfe


def add_datetime_and_timedeltas(lhs, rhs):
    blfyw__jmro = [datetime_timedelta_type, pd_timedelta_type]
    tnjf__lisg = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    jnnc__gmuf = lhs in blfyw__jmro and rhs in blfyw__jmro
    vnedt__npuct = (lhs == datetime_datetime_type and rhs in blfyw__jmro or
        rhs == datetime_datetime_type and lhs in blfyw__jmro)
    return jnnc__gmuf or vnedt__npuct


def mul_string_arr_and_int(lhs, rhs):
    ojupj__hosv = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    nrxjf__pbxb = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return ojupj__hosv or nrxjf__pbxb


def mul_timedelta_and_int(lhs, rhs):
    hjff__zeje = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    glmm__qoq = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return hjff__zeje or glmm__qoq


def mul_date_offset_and_int(lhs, rhs):
    aqwii__mchg = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    eleny__iojoz = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return aqwii__mchg or eleny__iojoz


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    kxk__fgb = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    oecr__eaexo = [date_offset_type, month_begin_type, month_end_type,
        week_type]
    return rhs in oecr__eaexo and lhs in kxk__fgb


def sub_dt_index_and_timestamp(lhs, rhs):
    hhr__jfrpi = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    fvc__rvub = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return hhr__jfrpi or fvc__rvub


def sub_dt_or_td(lhs, rhs):
    keq__xhcqa = lhs == datetime_date_type and rhs == datetime_timedelta_type
    ayvxy__kxl = lhs == datetime_date_type and rhs == datetime_date_type
    dhe__yusnz = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return keq__xhcqa or ayvxy__kxl or dhe__yusnz


def sub_datetime_and_timedeltas(lhs, rhs):
    xocwi__hhek = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    zxslz__kuyww = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return xocwi__hhek or zxslz__kuyww


def div_timedelta_and_int(lhs, rhs):
    jnnc__gmuf = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    gqeqp__scq = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return jnnc__gmuf or gqeqp__scq


def div_datetime_timedelta(lhs, rhs):
    jnnc__gmuf = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    gqeqp__scq = lhs == datetime_timedelta_type and rhs == types.int64
    return jnnc__gmuf or gqeqp__scq


def mod_timedeltas(lhs, rhs):
    cjlmx__hiinu = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    rjhq__tppg = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return cjlmx__hiinu or rjhq__tppg


def cmp_dt_index_to_string(lhs, rhs):
    hhr__jfrpi = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    fvc__rvub = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return hhr__jfrpi or fvc__rvub


def cmp_timestamp_or_date(lhs, rhs):
    omzbg__usfm = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    wpoq__ggbm = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    xsojv__cosl = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    jnc__bkpr = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    fvhjp__mnwri = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return (omzbg__usfm or wpoq__ggbm or xsojv__cosl or jnc__bkpr or
        fvhjp__mnwri)


def cmp_timeseries(lhs, rhs):
    vwggt__wsxno = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (
        bodo.utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs
        .str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    cod__pvz = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    zqmvn__zsbbr = vwggt__wsxno or cod__pvz
    yhlcy__czv = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    pfotn__nawu = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    ldze__hpl = yhlcy__czv or pfotn__nawu
    return zqmvn__zsbbr or ldze__hpl


def cmp_timedeltas(lhs, rhs):
    jnnc__gmuf = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in jnnc__gmuf and rhs in jnnc__gmuf


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    owmr__gog = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return owmr__gog


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    vdd__qplm = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    ifd__tcaoo = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    ijjby__aoo = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    oqsf__wdgqd = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return vdd__qplm or ifd__tcaoo or ijjby__aoo or oqsf__wdgqd


def args_td_and_int_array(lhs, rhs):
    cill__fgk = (isinstance(lhs, IntegerArrayType) or isinstance(lhs, types
        .Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance(
        rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    zuu__bukc = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return cill__fgk and zuu__bukc


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        glmm__qoq = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        hjff__zeje = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        hlx__ylz = glmm__qoq or hjff__zeje
        ueviz__kgt = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        calb__qhezt = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        bhp__gfmi = ueviz__kgt or calb__qhezt
        cout__cfowk = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        maib__zur = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        wxe__xyf = isinstance(lhs, types.Complex) and isinstance(rhs, types
            .Complex)
        imczu__lpyt = cout__cfowk or maib__zur or wxe__xyf
        emxd__secw = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        kiq__ulgyb = isinstance(lhs, tys) or isinstance(rhs, tys)
        iqd__sbkre = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (hlx__ylz or bhp__gfmi or imczu__lpyt or emxd__secw or
            kiq__ulgyb or iqd__sbkre)
    if op == operator.pow:
        pmyg__oja = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        kozsq__heiae = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        wxe__xyf = isinstance(lhs, types.Complex) and isinstance(rhs, types
            .Complex)
        iqd__sbkre = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return pmyg__oja or kozsq__heiae or wxe__xyf or iqd__sbkre
    if op == operator.floordiv:
        maib__zur = lhs in types.real_domain and rhs in types.real_domain
        cout__cfowk = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        irjdb__kwujb = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        jnnc__gmuf = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        iqd__sbkre = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (maib__zur or cout__cfowk or irjdb__kwujb or jnnc__gmuf or
            iqd__sbkre)
    if op == operator.truediv:
        rcx__qja = lhs in machine_ints and rhs in machine_ints
        maib__zur = lhs in types.real_domain and rhs in types.real_domain
        wxe__xyf = lhs in types.complex_domain and rhs in types.complex_domain
        cout__cfowk = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        irjdb__kwujb = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        cqp__lar = isinstance(lhs, types.Complex) and isinstance(rhs, types
            .Complex)
        jnnc__gmuf = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        iqd__sbkre = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (rcx__qja or maib__zur or wxe__xyf or cout__cfowk or
            irjdb__kwujb or cqp__lar or jnnc__gmuf or iqd__sbkre)
    if op == operator.mod:
        rcx__qja = lhs in machine_ints and rhs in machine_ints
        maib__zur = lhs in types.real_domain and rhs in types.real_domain
        cout__cfowk = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        irjdb__kwujb = isinstance(lhs, types.Float) and isinstance(rhs,
            types.Float)
        iqd__sbkre = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (rcx__qja or maib__zur or cout__cfowk or irjdb__kwujb or
            iqd__sbkre)
    if op == operator.add or op == operator.sub:
        hlx__ylz = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        ximoq__ubiek = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        pxyuw__wzw = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        yrw__xnutm = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        cout__cfowk = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        maib__zur = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        wxe__xyf = isinstance(lhs, types.Complex) and isinstance(rhs, types
            .Complex)
        imczu__lpyt = cout__cfowk or maib__zur or wxe__xyf
        iqd__sbkre = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        ipqn__xkcj = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        emxd__secw = isinstance(lhs, types.List) and isinstance(rhs, types.List
            )
        vna__xirem = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        baysb__dxpk = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        dbl__eeo = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        ukr__qeav = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        ekm__warrj = vna__xirem or baysb__dxpk or dbl__eeo or ukr__qeav
        bhp__gfmi = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        qicf__vpqjf = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        wake__mkkb = bhp__gfmi or qicf__vpqjf
        njnw__mbcz = lhs == types.NPTimedelta and rhs == types.NPDatetime
        vrzmc__kej = (ipqn__xkcj or emxd__secw or ekm__warrj or wake__mkkb or
            njnw__mbcz)
        qjks__qilag = op == operator.add and vrzmc__kej
        return (hlx__ylz or ximoq__ubiek or pxyuw__wzw or yrw__xnutm or
            imczu__lpyt or iqd__sbkre or qjks__qilag)


def cmp_op_supported_by_numba(lhs, rhs):
    iqd__sbkre = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    emxd__secw = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    hlx__ylz = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, types
        .NPTimedelta)
    mojh__xzy = isinstance(lhs, types.NPDatetime) and isinstance(rhs, types
        .NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    bhp__gfmi = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    ipqn__xkcj = isinstance(lhs, types.BaseTuple) and isinstance(rhs, types
        .BaseTuple)
    yrw__xnutm = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    imczu__lpyt = isinstance(lhs, types.Number) and isinstance(rhs, types.
        Number)
    tvqs__tmtn = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    hxgy__spbt = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    whv__nlkf = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    cwxbu__ygtt = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    fbg__wjeyi = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (emxd__secw or hlx__ylz or mojh__xzy or bhp__gfmi or ipqn__xkcj or
        yrw__xnutm or imczu__lpyt or tvqs__tmtn or hxgy__spbt or whv__nlkf or
        iqd__sbkre or cwxbu__ygtt or fbg__wjeyi)


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
        vzsr__eli = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(vzsr__eli)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        vzsr__eli = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(vzsr__eli)


install_arith_ops()
