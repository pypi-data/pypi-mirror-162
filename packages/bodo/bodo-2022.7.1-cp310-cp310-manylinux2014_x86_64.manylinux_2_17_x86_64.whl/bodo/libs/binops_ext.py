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
        hun__nyg = lhs.data if isinstance(lhs, SeriesType) else lhs
        nozo__gjobi = rhs.data if isinstance(rhs, SeriesType) else rhs
        if hun__nyg in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and nozo__gjobi.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            hun__nyg = nozo__gjobi.dtype
        elif nozo__gjobi in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and hun__nyg.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            nozo__gjobi = hun__nyg.dtype
        nnah__csksb = hun__nyg, nozo__gjobi
        fhwb__ajfue = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            lgoj__skx = self.context.resolve_function_type(self.key,
                nnah__csksb, {}).return_type
        except Exception as ebjjt__ikkm:
            raise BodoError(fhwb__ajfue)
        if is_overload_bool(lgoj__skx):
            raise BodoError(fhwb__ajfue)
        qgzpd__ybfx = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        ftaxb__dtp = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        triln__qyx = types.bool_
        who__rsc = SeriesType(triln__qyx, lgoj__skx, qgzpd__ybfx, ftaxb__dtp)
        return who__rsc(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        zxo__ejoyn = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if zxo__ejoyn is None:
            zxo__ejoyn = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, zxo__ejoyn, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        hun__nyg = lhs.data if isinstance(lhs, SeriesType) else lhs
        nozo__gjobi = rhs.data if isinstance(rhs, SeriesType) else rhs
        nnah__csksb = hun__nyg, nozo__gjobi
        fhwb__ajfue = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            lgoj__skx = self.context.resolve_function_type(self.key,
                nnah__csksb, {}).return_type
        except Exception as vmbf__crqdn:
            raise BodoError(fhwb__ajfue)
        qgzpd__ybfx = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        ftaxb__dtp = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        triln__qyx = lgoj__skx.dtype
        who__rsc = SeriesType(triln__qyx, lgoj__skx, qgzpd__ybfx, ftaxb__dtp)
        return who__rsc(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        zxo__ejoyn = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if zxo__ejoyn is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                zxo__ejoyn = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, zxo__ejoyn, sig, args)
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
            zxo__ejoyn = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return zxo__ejoyn(lhs, rhs)
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
            zxo__ejoyn = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return zxo__ejoyn(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    ejou__kocgj = lhs == datetime_timedelta_type and rhs == datetime_date_type
    dod__gtuq = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return ejou__kocgj or dod__gtuq


def add_timestamp(lhs, rhs):
    hvr__kil = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    npvrd__dxlg = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return hvr__kil or npvrd__dxlg


def add_datetime_and_timedeltas(lhs, rhs):
    qbgcr__xufns = [datetime_timedelta_type, pd_timedelta_type]
    tnj__nxpj = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    orfq__npd = lhs in qbgcr__xufns and rhs in qbgcr__xufns
    vtt__egah = (lhs == datetime_datetime_type and rhs in qbgcr__xufns or 
        rhs == datetime_datetime_type and lhs in qbgcr__xufns)
    return orfq__npd or vtt__egah


def mul_string_arr_and_int(lhs, rhs):
    nozo__gjobi = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    hun__nyg = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return nozo__gjobi or hun__nyg


def mul_timedelta_and_int(lhs, rhs):
    ejou__kocgj = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    dod__gtuq = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return ejou__kocgj or dod__gtuq


def mul_date_offset_and_int(lhs, rhs):
    jlfg__pbv = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    oxjf__dps = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return jlfg__pbv or oxjf__dps


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    qxd__olp = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    avzn__psmk = [date_offset_type, month_begin_type, month_end_type, week_type
        ]
    return rhs in avzn__psmk and lhs in qxd__olp


def sub_dt_index_and_timestamp(lhs, rhs):
    bci__opdl = isinstance(lhs, DatetimeIndexType) and rhs == pd_timestamp_type
    doy__ikir = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return bci__opdl or doy__ikir


def sub_dt_or_td(lhs, rhs):
    fiy__mfa = lhs == datetime_date_type and rhs == datetime_timedelta_type
    szlg__owf = lhs == datetime_date_type and rhs == datetime_date_type
    tgaxv__xof = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return fiy__mfa or szlg__owf or tgaxv__xof


def sub_datetime_and_timedeltas(lhs, rhs):
    qzvbq__yihee = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    inyiq__scdw = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return qzvbq__yihee or inyiq__scdw


def div_timedelta_and_int(lhs, rhs):
    orfq__npd = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    xvzr__gfekz = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return orfq__npd or xvzr__gfekz


def div_datetime_timedelta(lhs, rhs):
    orfq__npd = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    xvzr__gfekz = lhs == datetime_timedelta_type and rhs == types.int64
    return orfq__npd or xvzr__gfekz


def mod_timedeltas(lhs, rhs):
    zdrc__kph = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    tha__kdr = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return zdrc__kph or tha__kdr


def cmp_dt_index_to_string(lhs, rhs):
    bci__opdl = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    doy__ikir = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return bci__opdl or doy__ikir


def cmp_timestamp_or_date(lhs, rhs):
    ncmz__nwjs = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    kzw__rhwis = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    xryd__esrny = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    nhrjq__jrt = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    uvw__ngeig = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return ncmz__nwjs or kzw__rhwis or xryd__esrny or nhrjq__jrt or uvw__ngeig


def cmp_timeseries(lhs, rhs):
    tfga__wgvla = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    grwe__zvme = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    fbuu__pamde = tfga__wgvla or grwe__zvme
    gqor__dwpwk = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    gtdyp__sug = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    nnczi__pflq = gqor__dwpwk or gtdyp__sug
    return fbuu__pamde or nnczi__pflq


def cmp_timedeltas(lhs, rhs):
    orfq__npd = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in orfq__npd and rhs in orfq__npd


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    ipqnv__ctl = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return ipqnv__ctl


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    lpiz__tvefm = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    llz__wouw = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    muo__bgii = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    gjng__csj = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return lpiz__tvefm or llz__wouw or muo__bgii or gjng__csj


def args_td_and_int_array(lhs, rhs):
    bdzn__hlgzd = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    ncum__vzzr = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return bdzn__hlgzd and ncum__vzzr


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        dod__gtuq = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        ejou__kocgj = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        zvaj__eae = dod__gtuq or ejou__kocgj
        yxuwu__bvt = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        bft__eolwi = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        kqu__dddz = yxuwu__bvt or bft__eolwi
        upajj__cpaj = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        sgnmb__mrz = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        drr__jsaf = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ybnr__tldcp = upajj__cpaj or sgnmb__mrz or drr__jsaf
        wzne__vbd = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        wlnl__pok = isinstance(lhs, tys) or isinstance(rhs, tys)
        fxf__wzvrd = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (zvaj__eae or kqu__dddz or ybnr__tldcp or wzne__vbd or
            wlnl__pok or fxf__wzvrd)
    if op == operator.pow:
        qoy__hjl = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        jfm__xatx = isinstance(lhs, types.Float) and isinstance(rhs, (types
            .IntegerLiteral, types.Float, types.Integer) or rhs in types.
            unsigned_domain or rhs in types.signed_domain)
        drr__jsaf = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        fxf__wzvrd = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return qoy__hjl or jfm__xatx or drr__jsaf or fxf__wzvrd
    if op == operator.floordiv:
        sgnmb__mrz = lhs in types.real_domain and rhs in types.real_domain
        upajj__cpaj = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        aidd__ili = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        orfq__npd = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        fxf__wzvrd = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (sgnmb__mrz or upajj__cpaj or aidd__ili or orfq__npd or
            fxf__wzvrd)
    if op == operator.truediv:
        vyk__gsmut = lhs in machine_ints and rhs in machine_ints
        sgnmb__mrz = lhs in types.real_domain and rhs in types.real_domain
        drr__jsaf = lhs in types.complex_domain and rhs in types.complex_domain
        upajj__cpaj = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        aidd__ili = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        qmli__bumio = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        orfq__npd = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            (types.Integer, types.Float, types.NPTimedelta))
        fxf__wzvrd = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (vyk__gsmut or sgnmb__mrz or drr__jsaf or upajj__cpaj or
            aidd__ili or qmli__bumio or orfq__npd or fxf__wzvrd)
    if op == operator.mod:
        vyk__gsmut = lhs in machine_ints and rhs in machine_ints
        sgnmb__mrz = lhs in types.real_domain and rhs in types.real_domain
        upajj__cpaj = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        aidd__ili = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        fxf__wzvrd = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        return (vyk__gsmut or sgnmb__mrz or upajj__cpaj or aidd__ili or
            fxf__wzvrd)
    if op == operator.add or op == operator.sub:
        zvaj__eae = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        aybik__odmou = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        tfm__imcqj = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        xry__fdi = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
        upajj__cpaj = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        sgnmb__mrz = isinstance(lhs, types.Float) and isinstance(rhs, types
            .Float)
        drr__jsaf = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        ybnr__tldcp = upajj__cpaj or sgnmb__mrz or drr__jsaf
        fxf__wzvrd = isinstance(lhs, types.Array) or isinstance(rhs, types.
            Array)
        gqar__qbcwo = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        wzne__vbd = isinstance(lhs, types.List) and isinstance(rhs, types.List)
        qpcu__gygnq = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        xnks__cqgmk = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        gdsqd__vpg = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        wkxon__pbi = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        beyp__fqfmk = qpcu__gygnq or xnks__cqgmk or gdsqd__vpg or wkxon__pbi
        kqu__dddz = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        eypz__ewolz = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        wbq__fjbkv = kqu__dddz or eypz__ewolz
        gtf__jnxjn = lhs == types.NPTimedelta and rhs == types.NPDatetime
        zmv__bxoh = (gqar__qbcwo or wzne__vbd or beyp__fqfmk or wbq__fjbkv or
            gtf__jnxjn)
        jtns__mrla = op == operator.add and zmv__bxoh
        return (zvaj__eae or aybik__odmou or tfm__imcqj or xry__fdi or
            ybnr__tldcp or fxf__wzvrd or jtns__mrla)


def cmp_op_supported_by_numba(lhs, rhs):
    fxf__wzvrd = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    wzne__vbd = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    zvaj__eae = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    cnvbr__zmj = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    kqu__dddz = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    gqar__qbcwo = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
        types.BaseTuple)
    xry__fdi = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    ybnr__tldcp = isinstance(lhs, types.Number) and isinstance(rhs, types.
        Number)
    zabf__dwfb = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    qtgy__oktc = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    fomze__rvg = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    islaw__nqxy = isinstance(lhs, types.EnumMember) and isinstance(rhs,
        types.EnumMember)
    vrbe__ynpoi = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (wzne__vbd or zvaj__eae or cnvbr__zmj or kqu__dddz or
        gqar__qbcwo or xry__fdi or ybnr__tldcp or zabf__dwfb or qtgy__oktc or
        fomze__rvg or fxf__wzvrd or islaw__nqxy or vrbe__ynpoi)


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
        kofvm__snqxj = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(kofvm__snqxj)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        kofvm__snqxj = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(kofvm__snqxj)


install_arith_ops()
