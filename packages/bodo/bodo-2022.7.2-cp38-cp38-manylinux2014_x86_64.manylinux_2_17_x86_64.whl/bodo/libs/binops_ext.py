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
        udwjl__syv = lhs.data if isinstance(lhs, SeriesType) else lhs
        gies__fjbb = rhs.data if isinstance(rhs, SeriesType) else rhs
        if udwjl__syv in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and gies__fjbb.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            udwjl__syv = gies__fjbb.dtype
        elif gies__fjbb in (bodo.pd_timestamp_type, bodo.pd_timedelta_type
            ) and udwjl__syv.dtype in (bodo.datetime64ns, bodo.timedelta64ns):
            gies__fjbb = udwjl__syv.dtype
        uudi__ueb = udwjl__syv, gies__fjbb
        arla__taj = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            jxbpi__nsvix = self.context.resolve_function_type(self.key,
                uudi__ueb, {}).return_type
        except Exception as fjos__ozwhv:
            raise BodoError(arla__taj)
        if is_overload_bool(jxbpi__nsvix):
            raise BodoError(arla__taj)
        ekkry__dnqv = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        udu__ssslc = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        vuw__cad = types.bool_
        bti__dxcs = SeriesType(vuw__cad, jxbpi__nsvix, ekkry__dnqv, udu__ssslc)
        return bti__dxcs(*args)


def series_cmp_op_lower(op):

    def lower_impl(context, builder, sig, args):
        aih__clsf = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if aih__clsf is None:
            aih__clsf = create_overload_cmp_operator(op)(*sig.args)
        return context.compile_internal(builder, aih__clsf, sig, args)
    return lower_impl


class SeriesAndOrTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        lhs, rhs = args
        if not (isinstance(lhs, SeriesType) or isinstance(rhs, SeriesType)):
            return
        udwjl__syv = lhs.data if isinstance(lhs, SeriesType) else lhs
        gies__fjbb = rhs.data if isinstance(rhs, SeriesType) else rhs
        uudi__ueb = udwjl__syv, gies__fjbb
        arla__taj = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[self.key]} {rhs} not supported'
            )
        try:
            jxbpi__nsvix = self.context.resolve_function_type(self.key,
                uudi__ueb, {}).return_type
        except Exception as uamfq__kmdt:
            raise BodoError(arla__taj)
        ekkry__dnqv = lhs.index if isinstance(lhs, SeriesType) else rhs.index
        udu__ssslc = lhs.name_typ if isinstance(lhs, SeriesType
            ) else rhs.name_typ
        vuw__cad = jxbpi__nsvix.dtype
        bti__dxcs = SeriesType(vuw__cad, jxbpi__nsvix, ekkry__dnqv, udu__ssslc)
        return bti__dxcs(*args)


def lower_series_and_or(op):

    def lower_and_or_impl(context, builder, sig, args):
        aih__clsf = bodo.hiframes.series_impl.create_binary_op_overload(op)(*
            sig.args)
        if aih__clsf is None:
            lhs, rhs = sig.args
            if isinstance(lhs, DataFrameType) or isinstance(rhs, DataFrameType
                ):
                aih__clsf = (bodo.hiframes.dataframe_impl.
                    create_binary_op_overload(op)(*sig.args))
        return context.compile_internal(builder, aih__clsf, sig, args)
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
            aih__clsf = (bodo.hiframes.datetime_timedelta_ext.
                create_cmp_op_overload(op))
            return aih__clsf(lhs, rhs)
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
            aih__clsf = (bodo.hiframes.datetime_timedelta_ext.
                pd_create_cmp_op_overload(op))
            return aih__clsf(lhs, rhs)
        if cmp_timestamp_or_date(lhs, rhs):
            return (bodo.hiframes.pd_timestamp_ext.
                create_timestamp_cmp_op_overload(op)(lhs, rhs))
        if cmp_op_supported_by_numba(lhs, rhs):
            return
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_cmp_operator


def add_dt_td_and_dt_date(lhs, rhs):
    cbzzr__jhclb = lhs == datetime_timedelta_type and rhs == datetime_date_type
    pli__udacq = rhs == datetime_timedelta_type and lhs == datetime_date_type
    return cbzzr__jhclb or pli__udacq


def add_timestamp(lhs, rhs):
    lrqpf__akfm = lhs == pd_timestamp_type and is_timedelta_type(rhs)
    xpxff__mdgd = is_timedelta_type(lhs) and rhs == pd_timestamp_type
    return lrqpf__akfm or xpxff__mdgd


def add_datetime_and_timedeltas(lhs, rhs):
    rer__xvh = [datetime_timedelta_type, pd_timedelta_type]
    vyco__mkpcz = [datetime_timedelta_type, pd_timedelta_type,
        datetime_datetime_type]
    lpw__awm = lhs in rer__xvh and rhs in rer__xvh
    ogtj__jaw = (lhs == datetime_datetime_type and rhs in rer__xvh or rhs ==
        datetime_datetime_type and lhs in rer__xvh)
    return lpw__awm or ogtj__jaw


def mul_string_arr_and_int(lhs, rhs):
    gies__fjbb = isinstance(lhs, types.Integer) and is_str_arr_type(rhs)
    udwjl__syv = is_str_arr_type(lhs) and isinstance(rhs, types.Integer)
    return gies__fjbb or udwjl__syv


def mul_timedelta_and_int(lhs, rhs):
    cbzzr__jhclb = lhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(rhs, types.Integer)
    pli__udacq = rhs in [pd_timedelta_type, datetime_timedelta_type
        ] and isinstance(lhs, types.Integer)
    return cbzzr__jhclb or pli__udacq


def mul_date_offset_and_int(lhs, rhs):
    rcufx__kdvm = lhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(rhs, types.Integer)
    zhj__gyxlj = rhs in [week_type, month_end_type, month_begin_type,
        date_offset_type] and isinstance(lhs, types.Integer)
    return rcufx__kdvm or zhj__gyxlj


def sub_offset_to_datetime_or_timestamp(lhs, rhs):
    aon__yriz = [datetime_datetime_type, pd_timestamp_type, datetime_date_type]
    fpbjt__aexv = [date_offset_type, month_begin_type, month_end_type,
        week_type]
    return rhs in fpbjt__aexv and lhs in aon__yriz


def sub_dt_index_and_timestamp(lhs, rhs):
    mwsiw__hqvb = isinstance(lhs, DatetimeIndexType
        ) and rhs == pd_timestamp_type
    hdpp__iln = isinstance(rhs, DatetimeIndexType) and lhs == pd_timestamp_type
    return mwsiw__hqvb or hdpp__iln


def sub_dt_or_td(lhs, rhs):
    rotx__pojw = lhs == datetime_date_type and rhs == datetime_timedelta_type
    bfwv__cdpc = lhs == datetime_date_type and rhs == datetime_date_type
    iek__fbcy = (lhs == datetime_date_array_type and rhs ==
        datetime_timedelta_type)
    return rotx__pojw or bfwv__cdpc or iek__fbcy


def sub_datetime_and_timedeltas(lhs, rhs):
    sbgz__syo = (is_timedelta_type(lhs) or lhs == datetime_datetime_type
        ) and is_timedelta_type(rhs)
    bzxz__ledg = (lhs == datetime_timedelta_array_type and rhs ==
        datetime_timedelta_type)
    return sbgz__syo or bzxz__ledg


def div_timedelta_and_int(lhs, rhs):
    lpw__awm = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    fkdl__nsu = lhs == pd_timedelta_type and isinstance(rhs, types.Integer)
    return lpw__awm or fkdl__nsu


def div_datetime_timedelta(lhs, rhs):
    lpw__awm = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    fkdl__nsu = lhs == datetime_timedelta_type and rhs == types.int64
    return lpw__awm or fkdl__nsu


def mod_timedeltas(lhs, rhs):
    fplxn__bok = lhs == pd_timedelta_type and rhs == pd_timedelta_type
    gcpn__nuea = (lhs == datetime_timedelta_type and rhs ==
        datetime_timedelta_type)
    return fplxn__bok or gcpn__nuea


def cmp_dt_index_to_string(lhs, rhs):
    mwsiw__hqvb = isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
        ) == string_type
    hdpp__iln = isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
        ) == string_type
    return mwsiw__hqvb or hdpp__iln


def cmp_timestamp_or_date(lhs, rhs):
    iunvw__nrcur = (lhs == pd_timestamp_type and rhs == bodo.hiframes.
        datetime_date_ext.datetime_date_type)
    mby__eyyom = (lhs == bodo.hiframes.datetime_date_ext.datetime_date_type and
        rhs == pd_timestamp_type)
    iymgd__omwr = lhs == pd_timestamp_type and rhs == pd_timestamp_type
    jigan__bjbr = lhs == pd_timestamp_type and rhs == bodo.datetime64ns
    avdtl__iniv = rhs == pd_timestamp_type and lhs == bodo.datetime64ns
    return (iunvw__nrcur or mby__eyyom or iymgd__omwr or jigan__bjbr or
        avdtl__iniv)


def cmp_timeseries(lhs, rhs):
    cgkzd__hqtt = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (bodo
        .utils.typing.is_overload_constant_str(lhs) or lhs == bodo.libs.
        str_ext.string_type or lhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    opon__epzch = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (bodo
        .utils.typing.is_overload_constant_str(rhs) or rhs == bodo.libs.
        str_ext.string_type or rhs == bodo.hiframes.pd_timestamp_ext.
        pd_timestamp_type)
    lgcob__awvbd = cgkzd__hqtt or opon__epzch
    gumq__fevw = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    wlxt__avas = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
    ajh__xkkk = gumq__fevw or wlxt__avas
    return lgcob__awvbd or ajh__xkkk


def cmp_timedeltas(lhs, rhs):
    lpw__awm = [pd_timedelta_type, bodo.timedelta64ns]
    return lhs in lpw__awm and rhs in lpw__awm


def operand_is_index(operand):
    return is_index_type(operand) or isinstance(operand, HeterogeneousIndexType
        )


def helper_time_series_checks(operand):
    gqlzn__gqkhi = bodo.hiframes.pd_series_ext.is_dt64_series_typ(operand
        ) or bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(operand
        ) or operand in [datetime_timedelta_type, datetime_datetime_type,
        pd_timestamp_type]
    return gqlzn__gqkhi


def binary_array_cmp(lhs, rhs):
    return lhs == binary_array_type and rhs in [bytes_type, binary_array_type
        ] or lhs in [bytes_type, binary_array_type
        ] and rhs == binary_array_type


def can_cmp_date_datetime(lhs, rhs, op):
    return op in (operator.eq, operator.ne) and (lhs == datetime_date_type and
        rhs == datetime_datetime_type or lhs == datetime_datetime_type and 
        rhs == datetime_date_type)


def time_series_operation(lhs, rhs):
    quar__whh = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs
        ) and rhs == datetime_timedelta_type
    mpfr__zohjn = bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs
        ) and lhs == datetime_timedelta_type
    svdkx__rpr = bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
        ) and helper_time_series_checks(rhs)
    ynvqm__kzvuf = bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
        ) and helper_time_series_checks(lhs)
    return quar__whh or mpfr__zohjn or svdkx__rpr or ynvqm__kzvuf


def args_td_and_int_array(lhs, rhs):
    ameua__ekyqn = (isinstance(lhs, IntegerArrayType) or isinstance(lhs,
        types.Array) and isinstance(lhs.dtype, types.Integer)) or (isinstance
        (rhs, IntegerArrayType) or isinstance(rhs, types.Array) and
        isinstance(rhs.dtype, types.Integer))
    aaid__ikdyx = lhs in [pd_timedelta_type] or rhs in [pd_timedelta_type]
    return ameua__ekyqn and aaid__ikdyx


def arith_op_supported_by_numba(op, lhs, rhs):
    if op == operator.mul:
        pli__udacq = isinstance(lhs, (types.Integer, types.Float)
            ) and isinstance(rhs, types.NPTimedelta)
        cbzzr__jhclb = isinstance(rhs, (types.Integer, types.Float)
            ) and isinstance(lhs, types.NPTimedelta)
        vogkn__turd = pli__udacq or cbzzr__jhclb
        vjqvu__swjz = isinstance(rhs, types.UnicodeType) and isinstance(lhs,
            types.Integer)
        yuwim__ipzdq = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.Integer)
        diq__nsla = vjqvu__swjz or yuwim__ipzdq
        ovfgn__xpu = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        fkd__jpr = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        osqgf__afy = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        czu__wjvu = ovfgn__xpu or fkd__jpr or osqgf__afy
        zmrtu__xrx = isinstance(lhs, types.List) and isinstance(rhs, types.
            Integer) or isinstance(lhs, types.Integer) and isinstance(rhs,
            types.List)
        tys = types.UnicodeCharSeq, types.CharSeq, types.Bytes
        qzyhl__bmtn = isinstance(lhs, tys) or isinstance(rhs, tys)
        tgm__tocn = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (vogkn__turd or diq__nsla or czu__wjvu or zmrtu__xrx or
            qzyhl__bmtn or tgm__tocn)
    if op == operator.pow:
        lxvd__ckygk = isinstance(lhs, types.Integer) and isinstance(rhs, (
            types.IntegerLiteral, types.Integer))
        ymv__sgtma = isinstance(lhs, types.Float) and isinstance(rhs, (
            types.IntegerLiteral, types.Float, types.Integer) or rhs in
            types.unsigned_domain or rhs in types.signed_domain)
        osqgf__afy = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        tgm__tocn = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return lxvd__ckygk or ymv__sgtma or osqgf__afy or tgm__tocn
    if op == operator.floordiv:
        fkd__jpr = lhs in types.real_domain and rhs in types.real_domain
        ovfgn__xpu = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        sgk__vebc = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        lpw__awm = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, (
            types.Integer, types.Float, types.NPTimedelta))
        tgm__tocn = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return fkd__jpr or ovfgn__xpu or sgk__vebc or lpw__awm or tgm__tocn
    if op == operator.truediv:
        msbcn__qyz = lhs in machine_ints and rhs in machine_ints
        fkd__jpr = lhs in types.real_domain and rhs in types.real_domain
        osqgf__afy = (lhs in types.complex_domain and rhs in types.
            complex_domain)
        ovfgn__xpu = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        sgk__vebc = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        xlmy__sor = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        lpw__awm = isinstance(lhs, types.NPTimedelta) and isinstance(rhs, (
            types.Integer, types.Float, types.NPTimedelta))
        tgm__tocn = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return (msbcn__qyz or fkd__jpr or osqgf__afy or ovfgn__xpu or
            sgk__vebc or xlmy__sor or lpw__awm or tgm__tocn)
    if op == operator.mod:
        msbcn__qyz = lhs in machine_ints and rhs in machine_ints
        fkd__jpr = lhs in types.real_domain and rhs in types.real_domain
        ovfgn__xpu = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        sgk__vebc = isinstance(lhs, types.Float) and isinstance(rhs, types.
            Float)
        tgm__tocn = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        return msbcn__qyz or fkd__jpr or ovfgn__xpu or sgk__vebc or tgm__tocn
    if op == operator.add or op == operator.sub:
        vogkn__turd = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
            types.NPTimedelta)
        sctm__ucbz = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPDatetime)
        zrzp__uuc = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
            types.NPTimedelta)
        vtblr__rychc = isinstance(lhs, types.Set) and isinstance(rhs, types.Set
            )
        ovfgn__xpu = isinstance(lhs, types.Integer) and isinstance(rhs,
            types.Integer)
        fkd__jpr = isinstance(lhs, types.Float) and isinstance(rhs, types.Float
            )
        osqgf__afy = isinstance(lhs, types.Complex) and isinstance(rhs,
            types.Complex)
        czu__wjvu = ovfgn__xpu or fkd__jpr or osqgf__afy
        tgm__tocn = isinstance(lhs, types.Array) or isinstance(rhs, types.Array
            )
        fttaz__tstk = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
            types.BaseTuple)
        zmrtu__xrx = isinstance(lhs, types.List) and isinstance(rhs, types.List
            )
        wscvy__skwy = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeType)
        ffih__bfsce = isinstance(rhs, types.UnicodeCharSeq) and isinstance(lhs,
            types.UnicodeType)
        ludk__jgaf = isinstance(lhs, types.UnicodeCharSeq) and isinstance(rhs,
            types.UnicodeCharSeq)
        aoa__fef = isinstance(lhs, (types.CharSeq, types.Bytes)
            ) and isinstance(rhs, (types.CharSeq, types.Bytes))
        wpj__eqa = wscvy__skwy or ffih__bfsce or ludk__jgaf or aoa__fef
        diq__nsla = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeType)
        pqgbb__liz = isinstance(lhs, types.UnicodeType) and isinstance(rhs,
            types.UnicodeCharSeq)
        djh__laiy = diq__nsla or pqgbb__liz
        pfpjk__aeb = lhs == types.NPTimedelta and rhs == types.NPDatetime
        ebyhi__fih = (fttaz__tstk or zmrtu__xrx or wpj__eqa or djh__laiy or
            pfpjk__aeb)
        kjjj__ynz = op == operator.add and ebyhi__fih
        return (vogkn__turd or sctm__ucbz or zrzp__uuc or vtblr__rychc or
            czu__wjvu or tgm__tocn or kjjj__ynz)


def cmp_op_supported_by_numba(lhs, rhs):
    tgm__tocn = isinstance(lhs, types.Array) or isinstance(rhs, types.Array)
    zmrtu__xrx = isinstance(lhs, types.ListType) and isinstance(rhs, types.
        ListType)
    vogkn__turd = isinstance(lhs, types.NPTimedelta) and isinstance(rhs,
        types.NPTimedelta)
    mqukm__cnrh = isinstance(lhs, types.NPDatetime) and isinstance(rhs,
        types.NPDatetime)
    unicode_types = (types.UnicodeType, types.StringLiteral, types.CharSeq,
        types.Bytes, types.UnicodeCharSeq)
    diq__nsla = isinstance(lhs, unicode_types) and isinstance(rhs,
        unicode_types)
    fttaz__tstk = isinstance(lhs, types.BaseTuple) and isinstance(rhs,
        types.BaseTuple)
    vtblr__rychc = isinstance(lhs, types.Set) and isinstance(rhs, types.Set)
    czu__wjvu = isinstance(lhs, types.Number) and isinstance(rhs, types.Number)
    frmll__qaz = isinstance(lhs, types.Boolean) and isinstance(rhs, types.
        Boolean)
    uwe__ealik = isinstance(lhs, types.NoneType) or isinstance(rhs, types.
        NoneType)
    ikrgp__tvj = isinstance(lhs, types.DictType) and isinstance(rhs, types.
        DictType)
    cbq__pxq = isinstance(lhs, types.EnumMember) and isinstance(rhs, types.
        EnumMember)
    qlcu__mohtf = isinstance(lhs, types.Literal) and isinstance(rhs, types.
        Literal)
    return (zmrtu__xrx or vogkn__turd or mqukm__cnrh or diq__nsla or
        fttaz__tstk or vtblr__rychc or czu__wjvu or frmll__qaz or
        uwe__ealik or ikrgp__tvj or tgm__tocn or cbq__pxq or qlcu__mohtf)


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
        zhex__okscq = create_overload_cmp_operator(op)
        overload(op, no_unliteral=True)(zhex__okscq)


_install_cmp_ops()


def install_arith_ops():
    for op in (operator.add, operator.sub, operator.mul, operator.truediv,
        operator.floordiv, operator.mod, operator.pow):
        zhex__okscq = create_overload_arith_op(op)
        overload(op, no_unliteral=True)(zhex__okscq)


install_arith_ops()
