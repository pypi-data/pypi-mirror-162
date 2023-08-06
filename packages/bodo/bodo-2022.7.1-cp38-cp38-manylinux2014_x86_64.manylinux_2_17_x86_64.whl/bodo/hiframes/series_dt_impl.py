"""
Support for Series.dt attributes and methods
"""
import datetime
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_series_ext import SeriesType, get_series_data, get_series_index, get_series_name, init_series
from bodo.libs.pd_datetime_arr_ext import PandasDatetimeTZDtype
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, raise_bodo_error
dt64_dtype = np.dtype('datetime64[ns]')
timedelta64_dtype = np.dtype('timedelta64[ns]')


class SeriesDatetimePropertiesType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        aupjz__ccua = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(aupjz__ccua)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hwpx__klzar = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, hwpx__klzar)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        qot__tjjgj, = args
        ppaod__ikpm = signature.return_type
        dti__ubn = cgutils.create_struct_proxy(ppaod__ikpm)(context, builder)
        dti__ubn.obj = qot__tjjgj
        context.nrt.incref(builder, signature.args[0], qot__tjjgj)
        return dti__ubn._getvalue()
    return SeriesDatetimePropertiesType(obj)(obj), codegen


@overload_attribute(SeriesType, 'dt')
def overload_series_dt(s):
    if not (bodo.hiframes.pd_series_ext.is_dt64_series_typ(s) or bodo.
        hiframes.pd_series_ext.is_timedelta64_series_typ(s)):
        raise_bodo_error('Can only use .dt accessor with datetimelike values.')
    return lambda s: bodo.hiframes.series_dt_impl.init_series_dt_properties(s)


def create_date_field_overload(field):

    def overload_field(S_dt):
        if S_dt.stype.dtype != types.NPDatetime('ns') and not isinstance(S_dt
            .stype.dtype, PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{field}')
        opnlw__tko = 'def impl(S_dt):\n'
        opnlw__tko += '    S = S_dt._obj\n'
        opnlw__tko += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        opnlw__tko += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        opnlw__tko += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        opnlw__tko += '    numba.parfors.parfor.init_prange()\n'
        opnlw__tko += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            opnlw__tko += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            opnlw__tko += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        opnlw__tko += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        opnlw__tko += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        opnlw__tko += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        opnlw__tko += '            continue\n'
        opnlw__tko += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            opnlw__tko += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                opnlw__tko += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            opnlw__tko += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            ixowo__sgfri = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            opnlw__tko += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            opnlw__tko += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            opnlw__tko += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(ixowo__sgfri[field]))
        elif field == 'is_leap_year':
            opnlw__tko += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            opnlw__tko += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            ixowo__sgfri = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            opnlw__tko += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            opnlw__tko += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            opnlw__tko += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(ixowo__sgfri[field]))
        else:
            opnlw__tko += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            opnlw__tko += '        out_arr[i] = ts.' + field + '\n'
        opnlw__tko += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        amjo__xfma = {}
        exec(opnlw__tko, {'bodo': bodo, 'numba': numba, 'np': np}, amjo__xfma)
        impl = amjo__xfma['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        vbf__awk = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(vbf__awk)


_install_date_fields()


def create_date_method_overload(method):
    wcqjr__keat = method in ['day_name', 'month_name']
    if wcqjr__keat:
        opnlw__tko = 'def overload_method(S_dt, locale=None):\n'
        opnlw__tko += '    unsupported_args = dict(locale=locale)\n'
        opnlw__tko += '    arg_defaults = dict(locale=None)\n'
        opnlw__tko += '    bodo.utils.typing.check_unsupported_args(\n'
        opnlw__tko += f"        'Series.dt.{method}',\n"
        opnlw__tko += '        unsupported_args,\n'
        opnlw__tko += '        arg_defaults,\n'
        opnlw__tko += "        package_name='pandas',\n"
        opnlw__tko += "        module_name='Series',\n"
        opnlw__tko += '    )\n'
    else:
        opnlw__tko = 'def overload_method(S_dt):\n'
        opnlw__tko += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    opnlw__tko += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    opnlw__tko += '        return\n'
    if wcqjr__keat:
        opnlw__tko += '    def impl(S_dt, locale=None):\n'
    else:
        opnlw__tko += '    def impl(S_dt):\n'
    opnlw__tko += '        S = S_dt._obj\n'
    opnlw__tko += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    opnlw__tko += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    opnlw__tko += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    opnlw__tko += '        numba.parfors.parfor.init_prange()\n'
    opnlw__tko += '        n = len(arr)\n'
    if wcqjr__keat:
        opnlw__tko += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        opnlw__tko += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    opnlw__tko += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    opnlw__tko += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    opnlw__tko += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    opnlw__tko += '                continue\n'
    opnlw__tko += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    opnlw__tko += f'            method_val = ts.{method}()\n'
    if wcqjr__keat:
        opnlw__tko += '            out_arr[i] = method_val\n'
    else:
        opnlw__tko += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    opnlw__tko += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    opnlw__tko += '    return impl\n'
    amjo__xfma = {}
    exec(opnlw__tko, {'bodo': bodo, 'numba': numba, 'np': np}, amjo__xfma)
    overload_method = amjo__xfma['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        vbf__awk = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vbf__awk)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        mqxq__vzieq = S_dt._obj
        yog__dkmoz = bodo.hiframes.pd_series_ext.get_series_data(mqxq__vzieq)
        ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(mqxq__vzieq)
        aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(mqxq__vzieq)
        numba.parfors.parfor.init_prange()
        nkn__jnic = len(yog__dkmoz)
        aiz__lyctn = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            nkn__jnic)
        for osyvm__zrtu in numba.parfors.parfor.internal_prange(nkn__jnic):
            sftq__weaqb = yog__dkmoz[osyvm__zrtu]
            dmavg__wvug = bodo.utils.conversion.box_if_dt64(sftq__weaqb)
            aiz__lyctn[osyvm__zrtu] = datetime.date(dmavg__wvug.year,
                dmavg__wvug.month, dmavg__wvug.day)
        return bodo.hiframes.pd_series_ext.init_series(aiz__lyctn,
            ljau__atti, aupjz__ccua)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and (S_dt.stype.
            dtype == types.NPDatetime('ns') or isinstance(S_dt.stype.dtype,
            PandasDatetimeTZDtype))):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{attr}')
        if attr == 'components':
            yvyf__ztit = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            jdcej__qwzaz = 'convert_numpy_timedelta64_to_pd_timedelta'
            ttcmc__iphty = 'np.empty(n, np.int64)'
            xmhbg__ebjpk = attr
        elif attr == 'isocalendar':
            yvyf__ztit = ['year', 'week', 'day']
            jdcej__qwzaz = 'convert_datetime64_to_timestamp'
            ttcmc__iphty = (
                'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)')
            xmhbg__ebjpk = attr + '()'
        opnlw__tko = 'def impl(S_dt):\n'
        opnlw__tko += '    S = S_dt._obj\n'
        opnlw__tko += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        opnlw__tko += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        opnlw__tko += '    numba.parfors.parfor.init_prange()\n'
        opnlw__tko += '    n = len(arr)\n'
        for field in yvyf__ztit:
            opnlw__tko += '    {} = {}\n'.format(field, ttcmc__iphty)
        opnlw__tko += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        opnlw__tko += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in yvyf__ztit:
            opnlw__tko += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        opnlw__tko += '            continue\n'
        tii__ptj = '(' + '[i], '.join(yvyf__ztit) + '[i])'
        opnlw__tko += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(tii__ptj, jdcej__qwzaz, xmhbg__ebjpk))
        udz__qva = '(' + ', '.join(yvyf__ztit) + ')'
        opnlw__tko += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(udz__qva))
        amjo__xfma = {}
        exec(opnlw__tko, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(yvyf__ztit))}, amjo__xfma)
        impl = amjo__xfma['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    nevfz__agnib = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, xvota__eeyzc in nevfz__agnib:
        vbf__awk = create_series_dt_df_output_overload(attr)
        xvota__eeyzc(SeriesDatetimePropertiesType, attr, inline='always')(
            vbf__awk)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        opnlw__tko = 'def impl(S_dt):\n'
        opnlw__tko += '    S = S_dt._obj\n'
        opnlw__tko += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        opnlw__tko += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        opnlw__tko += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        opnlw__tko += '    numba.parfors.parfor.init_prange()\n'
        opnlw__tko += '    n = len(A)\n'
        opnlw__tko += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        opnlw__tko += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        opnlw__tko += '        if bodo.libs.array_kernels.isna(A, i):\n'
        opnlw__tko += '            bodo.libs.array_kernels.setna(B, i)\n'
        opnlw__tko += '            continue\n'
        opnlw__tko += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            opnlw__tko += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            opnlw__tko += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            opnlw__tko += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            opnlw__tko += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        opnlw__tko += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        amjo__xfma = {}
        exec(opnlw__tko, {'numba': numba, 'np': np, 'bodo': bodo}, amjo__xfma)
        impl = amjo__xfma['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        opnlw__tko = 'def impl(S_dt):\n'
        opnlw__tko += '    S = S_dt._obj\n'
        opnlw__tko += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        opnlw__tko += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        opnlw__tko += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        opnlw__tko += '    numba.parfors.parfor.init_prange()\n'
        opnlw__tko += '    n = len(A)\n'
        if method == 'total_seconds':
            opnlw__tko += '    B = np.empty(n, np.float64)\n'
        else:
            opnlw__tko += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        opnlw__tko += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        opnlw__tko += '        if bodo.libs.array_kernels.isna(A, i):\n'
        opnlw__tko += '            bodo.libs.array_kernels.setna(B, i)\n'
        opnlw__tko += '            continue\n'
        opnlw__tko += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            opnlw__tko += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            opnlw__tko += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            opnlw__tko += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            opnlw__tko += '    return B\n'
        amjo__xfma = {}
        exec(opnlw__tko, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, amjo__xfma)
        impl = amjo__xfma['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        vbf__awk = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(vbf__awk)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        vbf__awk = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vbf__awk)


_install_S_dt_timedelta_methods()


@overload_method(SeriesDatetimePropertiesType, 'strftime', inline='always',
    no_unliteral=True)
def dt_strftime(S_dt, date_format):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return
    if types.unliteral(date_format) != types.unicode_type:
        raise BodoError(
            "Series.str.strftime(): 'date_format' argument must be a string")

    def impl(S_dt, date_format):
        mqxq__vzieq = S_dt._obj
        easy__bksfg = bodo.hiframes.pd_series_ext.get_series_data(mqxq__vzieq)
        ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(mqxq__vzieq)
        aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(mqxq__vzieq)
        numba.parfors.parfor.init_prange()
        nkn__jnic = len(easy__bksfg)
        jly__nnkx = bodo.libs.str_arr_ext.pre_alloc_string_array(nkn__jnic, -1)
        for urgyv__fhoo in numba.parfors.parfor.internal_prange(nkn__jnic):
            if bodo.libs.array_kernels.isna(easy__bksfg, urgyv__fhoo):
                bodo.libs.array_kernels.setna(jly__nnkx, urgyv__fhoo)
                continue
            jly__nnkx[urgyv__fhoo] = bodo.utils.conversion.box_if_dt64(
                easy__bksfg[urgyv__fhoo]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(jly__nnkx,
            ljau__atti, aupjz__ccua)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        mqxq__vzieq = S_dt._obj
        npa__kot = get_series_data(mqxq__vzieq).tz_convert(tz)
        ljau__atti = get_series_index(mqxq__vzieq)
        aupjz__ccua = get_series_name(mqxq__vzieq)
        return init_series(npa__kot, ljau__atti, aupjz__ccua)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'
            ) and not isinstance(S_dt.stype.dtype, bodo.libs.
            pd_datetime_arr_ext.PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{method}()')
        zfeiq__tnt = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        btj__yeps = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', zfeiq__tnt, btj__yeps,
            package_name='pandas', module_name='Series')
        opnlw__tko = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        opnlw__tko += '    S = S_dt._obj\n'
        opnlw__tko += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        opnlw__tko += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        opnlw__tko += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        opnlw__tko += '    numba.parfors.parfor.init_prange()\n'
        opnlw__tko += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            opnlw__tko += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            opnlw__tko += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        opnlw__tko += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        opnlw__tko += '        if bodo.libs.array_kernels.isna(A, i):\n'
        opnlw__tko += '            bodo.libs.array_kernels.setna(B, i)\n'
        opnlw__tko += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            fhs__quxzt = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            jnb__jqn = 'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64'
        else:
            fhs__quxzt = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            jnb__jqn = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        opnlw__tko += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            jnb__jqn, fhs__quxzt, method)
        opnlw__tko += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        amjo__xfma = {}
        exec(opnlw__tko, {'numba': numba, 'np': np, 'bodo': bodo}, amjo__xfma)
        impl = amjo__xfma['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    bxq__zzkx = ['ceil', 'floor', 'round']
    for method in bxq__zzkx:
        vbf__awk = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            vbf__awk)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lhz__uah = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                nyjzc__ukg = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lhz__uah)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                led__vbpfv = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                azaxx__vwhxu = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    led__vbpfv)
                nkn__jnic = len(nyjzc__ukg)
                mqxq__vzieq = np.empty(nkn__jnic, timedelta64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    tfiam__kazsh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(nyjzc__ukg[osyvm__zrtu]))
                    upbj__xuu = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        azaxx__vwhxu[osyvm__zrtu])
                    if tfiam__kazsh == ukg__uta or upbj__xuu == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(tfiam__kazsh, upbj__xuu)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                azaxx__vwhxu = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, dt64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    yci__wuxz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    anlw__fmnz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(azaxx__vwhxu[osyvm__zrtu]))
                    if yci__wuxz == ukg__uta or anlw__fmnz == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(yci__wuxz, anlw__fmnz)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                azaxx__vwhxu = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, dt64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    yci__wuxz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    anlw__fmnz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(azaxx__vwhxu[osyvm__zrtu]))
                    if yci__wuxz == ukg__uta or anlw__fmnz == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(yci__wuxz, anlw__fmnz)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, timedelta64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                vwjzd__aln = rhs.value
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    yci__wuxz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    if yci__wuxz == ukg__uta or vwjzd__aln == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(yci__wuxz, vwjzd__aln)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, timedelta64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                vwjzd__aln = lhs.value
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    yci__wuxz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    if vwjzd__aln == ukg__uta or yci__wuxz == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(vwjzd__aln, yci__wuxz)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, dt64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                pze__cabb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                anlw__fmnz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pze__cabb))
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    yci__wuxz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    if yci__wuxz == ukg__uta or anlw__fmnz == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(yci__wuxz, anlw__fmnz)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, dt64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                pze__cabb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                anlw__fmnz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pze__cabb))
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    yci__wuxz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    if yci__wuxz == ukg__uta or anlw__fmnz == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(yci__wuxz, anlw__fmnz)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, timedelta64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                xdh__vlad = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                yci__wuxz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    xdh__vlad)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    tyvqr__evg = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yog__dkmoz[osyvm__zrtu]))
                    if tyvqr__evg == ukg__uta or yci__wuxz == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(tyvqr__evg, yci__wuxz)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, timedelta64_dtype)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                xdh__vlad = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                yci__wuxz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    xdh__vlad)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    tyvqr__evg = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yog__dkmoz[osyvm__zrtu]))
                    if yci__wuxz == ukg__uta or tyvqr__evg == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(yci__wuxz, tyvqr__evg)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tvlh__fssj = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yog__dkmoz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, timedelta64_dtype)
                ukg__uta = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tvlh__fssj))
                pze__cabb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                anlw__fmnz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pze__cabb))
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    jxkqv__fnvr = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yog__dkmoz[osyvm__zrtu]))
                    if anlw__fmnz == ukg__uta or jxkqv__fnvr == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(jxkqv__fnvr, anlw__fmnz)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tvlh__fssj = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yog__dkmoz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nkn__jnic = len(yog__dkmoz)
                mqxq__vzieq = np.empty(nkn__jnic, timedelta64_dtype)
                ukg__uta = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tvlh__fssj))
                pze__cabb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                anlw__fmnz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pze__cabb))
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    jxkqv__fnvr = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yog__dkmoz[osyvm__zrtu]))
                    if anlw__fmnz == ukg__uta or jxkqv__fnvr == ukg__uta:
                        yghg__cfmgv = ukg__uta
                    else:
                        yghg__cfmgv = op(anlw__fmnz, jxkqv__fnvr)
                    mqxq__vzieq[osyvm__zrtu
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        yghg__cfmgv)
                return bodo.hiframes.pd_series_ext.init_series(mqxq__vzieq,
                    ljau__atti, aupjz__ccua)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            jyr__cvsae = True
        else:
            jyr__cvsae = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tvlh__fssj = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yog__dkmoz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nkn__jnic = len(yog__dkmoz)
                aiz__lyctn = bodo.libs.bool_arr_ext.alloc_bool_array(nkn__jnic)
                ukg__uta = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tvlh__fssj))
                jpug__fbghd = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                ddxjs__ile = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jpug__fbghd))
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    ibki__cbl = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yog__dkmoz[osyvm__zrtu]))
                    if ibki__cbl == ukg__uta or ddxjs__ile == ukg__uta:
                        yghg__cfmgv = jyr__cvsae
                    else:
                        yghg__cfmgv = op(ibki__cbl, ddxjs__ile)
                    aiz__lyctn[osyvm__zrtu] = yghg__cfmgv
                return bodo.hiframes.pd_series_ext.init_series(aiz__lyctn,
                    ljau__atti, aupjz__ccua)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tvlh__fssj = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yog__dkmoz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nkn__jnic = len(yog__dkmoz)
                aiz__lyctn = bodo.libs.bool_arr_ext.alloc_bool_array(nkn__jnic)
                ukg__uta = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tvlh__fssj))
                rayb__csu = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                ibki__cbl = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rayb__csu))
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    ddxjs__ile = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yog__dkmoz[osyvm__zrtu]))
                    if ibki__cbl == ukg__uta or ddxjs__ile == ukg__uta:
                        yghg__cfmgv = jyr__cvsae
                    else:
                        yghg__cfmgv = op(ibki__cbl, ddxjs__ile)
                    aiz__lyctn[osyvm__zrtu] = yghg__cfmgv
                return bodo.hiframes.pd_series_ext.init_series(aiz__lyctn,
                    ljau__atti, aupjz__ccua)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nkn__jnic = len(yog__dkmoz)
                aiz__lyctn = bodo.libs.bool_arr_ext.alloc_bool_array(nkn__jnic)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    ibki__cbl = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    if ibki__cbl == ukg__uta or rhs.value == ukg__uta:
                        yghg__cfmgv = jyr__cvsae
                    else:
                        yghg__cfmgv = op(ibki__cbl, rhs.value)
                    aiz__lyctn[osyvm__zrtu] = yghg__cfmgv
                return bodo.hiframes.pd_series_ext.init_series(aiz__lyctn,
                    ljau__atti, aupjz__ccua)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nkn__jnic = len(yog__dkmoz)
                aiz__lyctn = bodo.libs.bool_arr_ext.alloc_bool_array(nkn__jnic)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    ddxjs__ile = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yog__dkmoz[osyvm__zrtu]))
                    if ddxjs__ile == ukg__uta or lhs.value == ukg__uta:
                        yghg__cfmgv = jyr__cvsae
                    else:
                        yghg__cfmgv = op(lhs.value, ddxjs__ile)
                    aiz__lyctn[osyvm__zrtu] = yghg__cfmgv
                return bodo.hiframes.pd_series_ext.init_series(aiz__lyctn,
                    ljau__atti, aupjz__ccua)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                nkn__jnic = len(yog__dkmoz)
                aiz__lyctn = bodo.libs.bool_arr_ext.alloc_bool_array(nkn__jnic)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                xsi__mddse = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                xqqp__yyprt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    xsi__mddse)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    ibki__cbl = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    if ibki__cbl == ukg__uta or xqqp__yyprt == ukg__uta:
                        yghg__cfmgv = jyr__cvsae
                    else:
                        yghg__cfmgv = op(ibki__cbl, xqqp__yyprt)
                    aiz__lyctn[osyvm__zrtu] = yghg__cfmgv
                return bodo.hiframes.pd_series_ext.init_series(aiz__lyctn,
                    ljau__atti, aupjz__ccua)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            tvlh__fssj = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                dvr__ojlw = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yog__dkmoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    dvr__ojlw)
                ljau__atti = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                aupjz__ccua = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                nkn__jnic = len(yog__dkmoz)
                aiz__lyctn = bodo.libs.bool_arr_ext.alloc_bool_array(nkn__jnic)
                ukg__uta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tvlh__fssj)
                xsi__mddse = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                xqqp__yyprt = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    xsi__mddse)
                for osyvm__zrtu in numba.parfors.parfor.internal_prange(
                    nkn__jnic):
                    xdh__vlad = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        yog__dkmoz[osyvm__zrtu])
                    if xdh__vlad == ukg__uta or xqqp__yyprt == ukg__uta:
                        yghg__cfmgv = jyr__cvsae
                    else:
                        yghg__cfmgv = op(xqqp__yyprt, xdh__vlad)
                    aiz__lyctn[osyvm__zrtu] = yghg__cfmgv
                return bodo.hiframes.pd_series_ext.init_series(aiz__lyctn,
                    ljau__atti, aupjz__ccua)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for vzz__ztafn in series_dt_unsupported_attrs:
        cipl__wzvur = 'Series.dt.' + vzz__ztafn
        overload_attribute(SeriesDatetimePropertiesType, vzz__ztafn)(
            create_unsupported_overload(cipl__wzvur))
    for zraxa__aie in series_dt_unsupported_methods:
        cipl__wzvur = 'Series.dt.' + zraxa__aie
        overload_method(SeriesDatetimePropertiesType, zraxa__aie,
            no_unliteral=True)(create_unsupported_overload(cipl__wzvur))


_install_series_dt_unsupported()
