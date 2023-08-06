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
        qvv__izv = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(qvv__izv)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ecfon__hichy = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, ecfon__hichy)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        smw__tjb, = args
        yho__sddi = signature.return_type
        mmv__iye = cgutils.create_struct_proxy(yho__sddi)(context, builder)
        mmv__iye.obj = smw__tjb
        context.nrt.incref(builder, signature.args[0], smw__tjb)
        return mmv__iye._getvalue()
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
        iyszj__zwroa = 'def impl(S_dt):\n'
        iyszj__zwroa += '    S = S_dt._obj\n'
        iyszj__zwroa += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        iyszj__zwroa += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iyszj__zwroa += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        iyszj__zwroa += '    numba.parfors.parfor.init_prange()\n'
        iyszj__zwroa += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            iyszj__zwroa += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            iyszj__zwroa += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        iyszj__zwroa += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        iyszj__zwroa += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        iyszj__zwroa += (
            '            bodo.libs.array_kernels.setna(out_arr, i)\n')
        iyszj__zwroa += '            continue\n'
        iyszj__zwroa += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            iyszj__zwroa += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                iyszj__zwroa += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            iyszj__zwroa += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            ynnw__wqlse = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            iyszj__zwroa += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            iyszj__zwroa += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            iyszj__zwroa += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(ynnw__wqlse[field]))
        elif field == 'is_leap_year':
            iyszj__zwroa += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            iyszj__zwroa += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            ynnw__wqlse = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            iyszj__zwroa += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            iyszj__zwroa += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            iyszj__zwroa += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(ynnw__wqlse[field]))
        else:
            iyszj__zwroa += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            iyszj__zwroa += '        out_arr[i] = ts.' + field + '\n'
        iyszj__zwroa += """    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
        ukhaz__yys = {}
        exec(iyszj__zwroa, {'bodo': bodo, 'numba': numba, 'np': np}, ukhaz__yys
            )
        impl = ukhaz__yys['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        eod__pkjm = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(eod__pkjm)


_install_date_fields()


def create_date_method_overload(method):
    asrso__kmnoc = method in ['day_name', 'month_name']
    if asrso__kmnoc:
        iyszj__zwroa = 'def overload_method(S_dt, locale=None):\n'
        iyszj__zwroa += '    unsupported_args = dict(locale=locale)\n'
        iyszj__zwroa += '    arg_defaults = dict(locale=None)\n'
        iyszj__zwroa += '    bodo.utils.typing.check_unsupported_args(\n'
        iyszj__zwroa += f"        'Series.dt.{method}',\n"
        iyszj__zwroa += '        unsupported_args,\n'
        iyszj__zwroa += '        arg_defaults,\n'
        iyszj__zwroa += "        package_name='pandas',\n"
        iyszj__zwroa += "        module_name='Series',\n"
        iyszj__zwroa += '    )\n'
    else:
        iyszj__zwroa = 'def overload_method(S_dt):\n'
        iyszj__zwroa += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    iyszj__zwroa += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    iyszj__zwroa += '        return\n'
    if asrso__kmnoc:
        iyszj__zwroa += '    def impl(S_dt, locale=None):\n'
    else:
        iyszj__zwroa += '    def impl(S_dt):\n'
    iyszj__zwroa += '        S = S_dt._obj\n'
    iyszj__zwroa += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    iyszj__zwroa += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    iyszj__zwroa += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    iyszj__zwroa += '        numba.parfors.parfor.init_prange()\n'
    iyszj__zwroa += '        n = len(arr)\n'
    if asrso__kmnoc:
        iyszj__zwroa += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        iyszj__zwroa += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    iyszj__zwroa += (
        '        for i in numba.parfors.parfor.internal_prange(n):\n')
    iyszj__zwroa += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    iyszj__zwroa += (
        '                bodo.libs.array_kernels.setna(out_arr, i)\n')
    iyszj__zwroa += '                continue\n'
    iyszj__zwroa += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    iyszj__zwroa += f'            method_val = ts.{method}()\n'
    if asrso__kmnoc:
        iyszj__zwroa += '            out_arr[i] = method_val\n'
    else:
        iyszj__zwroa += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    iyszj__zwroa += """        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    iyszj__zwroa += '    return impl\n'
    ukhaz__yys = {}
    exec(iyszj__zwroa, {'bodo': bodo, 'numba': numba, 'np': np}, ukhaz__yys)
    overload_method = ukhaz__yys['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        eod__pkjm = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            eod__pkjm)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        bfdmi__izni = S_dt._obj
        obbc__obci = bodo.hiframes.pd_series_ext.get_series_data(bfdmi__izni)
        lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(bfdmi__izni)
        qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(bfdmi__izni)
        numba.parfors.parfor.init_prange()
        egzt__kxyg = len(obbc__obci)
        stci__venv = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            egzt__kxyg)
        for vgghc__bpve in numba.parfors.parfor.internal_prange(egzt__kxyg):
            bij__qfym = obbc__obci[vgghc__bpve]
            wgjk__ocw = bodo.utils.conversion.box_if_dt64(bij__qfym)
            stci__venv[vgghc__bpve] = datetime.date(wgjk__ocw.year,
                wgjk__ocw.month, wgjk__ocw.day)
        return bodo.hiframes.pd_series_ext.init_series(stci__venv,
            lrzux__fll, qvv__izv)
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
            dtbp__fiwy = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            xsyjh__phzmw = 'convert_numpy_timedelta64_to_pd_timedelta'
            gha__uygma = 'np.empty(n, np.int64)'
            ggio__ieu = attr
        elif attr == 'isocalendar':
            dtbp__fiwy = ['year', 'week', 'day']
            xsyjh__phzmw = 'convert_datetime64_to_timestamp'
            gha__uygma = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            ggio__ieu = attr + '()'
        iyszj__zwroa = 'def impl(S_dt):\n'
        iyszj__zwroa += '    S = S_dt._obj\n'
        iyszj__zwroa += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        iyszj__zwroa += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iyszj__zwroa += '    numba.parfors.parfor.init_prange()\n'
        iyszj__zwroa += '    n = len(arr)\n'
        for field in dtbp__fiwy:
            iyszj__zwroa += '    {} = {}\n'.format(field, gha__uygma)
        iyszj__zwroa += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        iyszj__zwroa += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in dtbp__fiwy:
            iyszj__zwroa += (
                '            bodo.libs.array_kernels.setna({}, i)\n'.format
                (field))
        iyszj__zwroa += '            continue\n'
        cjfd__ddq = '(' + '[i], '.join(dtbp__fiwy) + '[i])'
        iyszj__zwroa += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(cjfd__ddq, xsyjh__phzmw, ggio__ieu))
        ahu__pgh = '(' + ', '.join(dtbp__fiwy) + ')'
        iyszj__zwroa += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(ahu__pgh))
        ukhaz__yys = {}
        exec(iyszj__zwroa, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(dtbp__fiwy))}, ukhaz__yys)
        impl = ukhaz__yys['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    ofqny__fev = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, flv__mgl in ofqny__fev:
        eod__pkjm = create_series_dt_df_output_overload(attr)
        flv__mgl(SeriesDatetimePropertiesType, attr, inline='always')(eod__pkjm
            )


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        iyszj__zwroa = 'def impl(S_dt):\n'
        iyszj__zwroa += '    S = S_dt._obj\n'
        iyszj__zwroa += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        iyszj__zwroa += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iyszj__zwroa += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        iyszj__zwroa += '    numba.parfors.parfor.init_prange()\n'
        iyszj__zwroa += '    n = len(A)\n'
        iyszj__zwroa += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        iyszj__zwroa += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        iyszj__zwroa += '        if bodo.libs.array_kernels.isna(A, i):\n'
        iyszj__zwroa += '            bodo.libs.array_kernels.setna(B, i)\n'
        iyszj__zwroa += '            continue\n'
        iyszj__zwroa += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            iyszj__zwroa += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            iyszj__zwroa += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            iyszj__zwroa += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            iyszj__zwroa += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        iyszj__zwroa += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        ukhaz__yys = {}
        exec(iyszj__zwroa, {'numba': numba, 'np': np, 'bodo': bodo}, ukhaz__yys
            )
        impl = ukhaz__yys['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        iyszj__zwroa = 'def impl(S_dt):\n'
        iyszj__zwroa += '    S = S_dt._obj\n'
        iyszj__zwroa += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        iyszj__zwroa += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iyszj__zwroa += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        iyszj__zwroa += '    numba.parfors.parfor.init_prange()\n'
        iyszj__zwroa += '    n = len(A)\n'
        if method == 'total_seconds':
            iyszj__zwroa += '    B = np.empty(n, np.float64)\n'
        else:
            iyszj__zwroa += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        iyszj__zwroa += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        iyszj__zwroa += '        if bodo.libs.array_kernels.isna(A, i):\n'
        iyszj__zwroa += '            bodo.libs.array_kernels.setna(B, i)\n'
        iyszj__zwroa += '            continue\n'
        iyszj__zwroa += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            iyszj__zwroa += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            iyszj__zwroa += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            iyszj__zwroa += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            iyszj__zwroa += '    return B\n'
        ukhaz__yys = {}
        exec(iyszj__zwroa, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, ukhaz__yys)
        impl = ukhaz__yys['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        eod__pkjm = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(eod__pkjm)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        eod__pkjm = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            eod__pkjm)


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
        bfdmi__izni = S_dt._obj
        gqvgu__jhv = bodo.hiframes.pd_series_ext.get_series_data(bfdmi__izni)
        lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(bfdmi__izni)
        qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(bfdmi__izni)
        numba.parfors.parfor.init_prange()
        egzt__kxyg = len(gqvgu__jhv)
        ctx__zmk = bodo.libs.str_arr_ext.pre_alloc_string_array(egzt__kxyg, -1)
        for rhfo__mia in numba.parfors.parfor.internal_prange(egzt__kxyg):
            if bodo.libs.array_kernels.isna(gqvgu__jhv, rhfo__mia):
                bodo.libs.array_kernels.setna(ctx__zmk, rhfo__mia)
                continue
            ctx__zmk[rhfo__mia] = bodo.utils.conversion.box_if_dt64(gqvgu__jhv
                [rhfo__mia]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(ctx__zmk, lrzux__fll,
            qvv__izv)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        bfdmi__izni = S_dt._obj
        lmujv__sjeom = get_series_data(bfdmi__izni).tz_convert(tz)
        lrzux__fll = get_series_index(bfdmi__izni)
        qvv__izv = get_series_name(bfdmi__izni)
        return init_series(lmujv__sjeom, lrzux__fll, qvv__izv)
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
        myt__jllk = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        ycijt__pzubd = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', myt__jllk,
            ycijt__pzubd, package_name='pandas', module_name='Series')
        iyszj__zwroa = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        iyszj__zwroa += '    S = S_dt._obj\n'
        iyszj__zwroa += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        iyszj__zwroa += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iyszj__zwroa += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        iyszj__zwroa += '    numba.parfors.parfor.init_prange()\n'
        iyszj__zwroa += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            iyszj__zwroa += (
                "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n")
        else:
            iyszj__zwroa += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        iyszj__zwroa += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        iyszj__zwroa += '        if bodo.libs.array_kernels.isna(A, i):\n'
        iyszj__zwroa += '            bodo.libs.array_kernels.setna(B, i)\n'
        iyszj__zwroa += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            nnwnf__qrvh = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            clyg__rddyw = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            nnwnf__qrvh = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            clyg__rddyw = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        iyszj__zwroa += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            clyg__rddyw, nnwnf__qrvh, method)
        iyszj__zwroa += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        ukhaz__yys = {}
        exec(iyszj__zwroa, {'numba': numba, 'np': np, 'bodo': bodo}, ukhaz__yys
            )
        impl = ukhaz__yys['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    serkh__pdd = ['ceil', 'floor', 'round']
    for method in serkh__pdd:
        eod__pkjm = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            eod__pkjm)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                utm__cfn = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                gexj__nmvzd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    utm__cfn)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ftlw__wwyzu = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                aumlu__pgg = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ftlw__wwyzu)
                egzt__kxyg = len(gexj__nmvzd)
                bfdmi__izni = np.empty(egzt__kxyg, timedelta64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    vdtb__mhufp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(gexj__nmvzd[vgghc__bpve]))
                    ubjya__jma = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(aumlu__pgg[vgghc__bpve]))
                    if vdtb__mhufp == eeohq__nxnq or ubjya__jma == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(vdtb__mhufp, ubjya__jma)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                aumlu__pgg = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, dt64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    wth__yzpk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    bjak__uqwq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(aumlu__pgg[vgghc__bpve]))
                    if wth__yzpk == eeohq__nxnq or bjak__uqwq == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(wth__yzpk, bjak__uqwq)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                aumlu__pgg = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, dt64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    wth__yzpk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    bjak__uqwq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(aumlu__pgg[vgghc__bpve]))
                    if wth__yzpk == eeohq__nxnq or bjak__uqwq == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(wth__yzpk, bjak__uqwq)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, timedelta64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                weofc__mpsm = rhs.value
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    wth__yzpk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    if wth__yzpk == eeohq__nxnq or weofc__mpsm == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(wth__yzpk, weofc__mpsm)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, timedelta64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                weofc__mpsm = lhs.value
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    wth__yzpk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    if weofc__mpsm == eeohq__nxnq or wth__yzpk == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(weofc__mpsm, wth__yzpk)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, dt64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                mzbb__itvzp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                bjak__uqwq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mzbb__itvzp))
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    wth__yzpk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    if wth__yzpk == eeohq__nxnq or bjak__uqwq == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(wth__yzpk, bjak__uqwq)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, dt64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                mzbb__itvzp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                bjak__uqwq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mzbb__itvzp))
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    wth__yzpk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    if wth__yzpk == eeohq__nxnq or bjak__uqwq == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(wth__yzpk, bjak__uqwq)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, timedelta64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                vzx__ghe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                wth__yzpk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vzx__ghe)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    guk__oaz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    if guk__oaz == eeohq__nxnq or wth__yzpk == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(guk__oaz, wth__yzpk)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, timedelta64_dtype)
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                vzx__ghe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                wth__yzpk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    vzx__ghe)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    guk__oaz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    if wth__yzpk == eeohq__nxnq or guk__oaz == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(wth__yzpk, guk__oaz)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ctgj__bzlrh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                obbc__obci = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, timedelta64_dtype)
                eeohq__nxnq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ctgj__bzlrh))
                mzbb__itvzp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                bjak__uqwq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mzbb__itvzp))
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    ipao__ccg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(obbc__obci[vgghc__bpve]))
                    if bjak__uqwq == eeohq__nxnq or ipao__ccg == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(ipao__ccg, bjak__uqwq)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ctgj__bzlrh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                obbc__obci = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                egzt__kxyg = len(obbc__obci)
                bfdmi__izni = np.empty(egzt__kxyg, timedelta64_dtype)
                eeohq__nxnq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ctgj__bzlrh))
                mzbb__itvzp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                bjak__uqwq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mzbb__itvzp))
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    ipao__ccg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(obbc__obci[vgghc__bpve]))
                    if bjak__uqwq == eeohq__nxnq or ipao__ccg == eeohq__nxnq:
                        zjd__gqh = eeohq__nxnq
                    else:
                        zjd__gqh = op(bjak__uqwq, ipao__ccg)
                    bfdmi__izni[vgghc__bpve
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        zjd__gqh)
                return bodo.hiframes.pd_series_ext.init_series(bfdmi__izni,
                    lrzux__fll, qvv__izv)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            eudht__ocs = True
        else:
            eudht__ocs = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ctgj__bzlrh = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                obbc__obci = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                egzt__kxyg = len(obbc__obci)
                stci__venv = bodo.libs.bool_arr_ext.alloc_bool_array(egzt__kxyg
                    )
                eeohq__nxnq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ctgj__bzlrh))
                mkd__inya = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                cvw__cnvak = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mkd__inya))
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    lfj__fpqvp = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(obbc__obci[vgghc__bpve]))
                    if lfj__fpqvp == eeohq__nxnq or cvw__cnvak == eeohq__nxnq:
                        zjd__gqh = eudht__ocs
                    else:
                        zjd__gqh = op(lfj__fpqvp, cvw__cnvak)
                    stci__venv[vgghc__bpve] = zjd__gqh
                return bodo.hiframes.pd_series_ext.init_series(stci__venv,
                    lrzux__fll, qvv__izv)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ctgj__bzlrh = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                obbc__obci = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                egzt__kxyg = len(obbc__obci)
                stci__venv = bodo.libs.bool_arr_ext.alloc_bool_array(egzt__kxyg
                    )
                eeohq__nxnq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ctgj__bzlrh))
                agzkq__xqzku = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                lfj__fpqvp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(agzkq__xqzku))
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    cvw__cnvak = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(obbc__obci[vgghc__bpve]))
                    if lfj__fpqvp == eeohq__nxnq or cvw__cnvak == eeohq__nxnq:
                        zjd__gqh = eudht__ocs
                    else:
                        zjd__gqh = op(lfj__fpqvp, cvw__cnvak)
                    stci__venv[vgghc__bpve] = zjd__gqh
                return bodo.hiframes.pd_series_ext.init_series(stci__venv,
                    lrzux__fll, qvv__izv)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                egzt__kxyg = len(obbc__obci)
                stci__venv = bodo.libs.bool_arr_ext.alloc_bool_array(egzt__kxyg
                    )
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    lfj__fpqvp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(obbc__obci[vgghc__bpve]))
                    if lfj__fpqvp == eeohq__nxnq or rhs.value == eeohq__nxnq:
                        zjd__gqh = eudht__ocs
                    else:
                        zjd__gqh = op(lfj__fpqvp, rhs.value)
                    stci__venv[vgghc__bpve] = zjd__gqh
                return bodo.hiframes.pd_series_ext.init_series(stci__venv,
                    lrzux__fll, qvv__izv)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                egzt__kxyg = len(obbc__obci)
                stci__venv = bodo.libs.bool_arr_ext.alloc_bool_array(egzt__kxyg
                    )
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    cvw__cnvak = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(obbc__obci[vgghc__bpve]))
                    if cvw__cnvak == eeohq__nxnq or lhs.value == eeohq__nxnq:
                        zjd__gqh = eudht__ocs
                    else:
                        zjd__gqh = op(lhs.value, cvw__cnvak)
                    stci__venv[vgghc__bpve] = zjd__gqh
                return bodo.hiframes.pd_series_ext.init_series(stci__venv,
                    lrzux__fll, qvv__izv)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                egzt__kxyg = len(obbc__obci)
                stci__venv = bodo.libs.bool_arr_ext.alloc_bool_array(egzt__kxyg
                    )
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                ymum__gasqw = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(rhs))
                qhzup__akam = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ymum__gasqw)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    lfj__fpqvp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(obbc__obci[vgghc__bpve]))
                    if lfj__fpqvp == eeohq__nxnq or qhzup__akam == eeohq__nxnq:
                        zjd__gqh = eudht__ocs
                    else:
                        zjd__gqh = op(lfj__fpqvp, qhzup__akam)
                    stci__venv[vgghc__bpve] = zjd__gqh
                return bodo.hiframes.pd_series_ext.init_series(stci__venv,
                    lrzux__fll, qvv__izv)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            ctgj__bzlrh = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                fqt__ciq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                obbc__obci = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    fqt__ciq)
                lrzux__fll = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                qvv__izv = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                egzt__kxyg = len(obbc__obci)
                stci__venv = bodo.libs.bool_arr_ext.alloc_bool_array(egzt__kxyg
                    )
                eeohq__nxnq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ctgj__bzlrh)
                ymum__gasqw = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(lhs))
                qhzup__akam = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ymum__gasqw)
                for vgghc__bpve in numba.parfors.parfor.internal_prange(
                    egzt__kxyg):
                    vzx__ghe = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        obbc__obci[vgghc__bpve])
                    if vzx__ghe == eeohq__nxnq or qhzup__akam == eeohq__nxnq:
                        zjd__gqh = eudht__ocs
                    else:
                        zjd__gqh = op(qhzup__akam, vzx__ghe)
                    stci__venv[vgghc__bpve] = zjd__gqh
                return bodo.hiframes.pd_series_ext.init_series(stci__venv,
                    lrzux__fll, qvv__izv)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for zafsk__osfq in series_dt_unsupported_attrs:
        ugqj__veoh = 'Series.dt.' + zafsk__osfq
        overload_attribute(SeriesDatetimePropertiesType, zafsk__osfq)(
            create_unsupported_overload(ugqj__veoh))
    for hdjk__xox in series_dt_unsupported_methods:
        ugqj__veoh = 'Series.dt.' + hdjk__xox
        overload_method(SeriesDatetimePropertiesType, hdjk__xox,
            no_unliteral=True)(create_unsupported_overload(ugqj__veoh))


_install_series_dt_unsupported()
