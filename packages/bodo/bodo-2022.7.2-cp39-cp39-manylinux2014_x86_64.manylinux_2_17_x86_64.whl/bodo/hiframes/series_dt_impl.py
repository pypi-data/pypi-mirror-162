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
        olh__tskrs = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(olh__tskrs)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gstn__kpb = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, gstn__kpb)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        ifuw__xidve, = args
        cusne__msfx = signature.return_type
        ccypf__fhfe = cgutils.create_struct_proxy(cusne__msfx)(context, builder
            )
        ccypf__fhfe.obj = ifuw__xidve
        context.nrt.incref(builder, signature.args[0], ifuw__xidve)
        return ccypf__fhfe._getvalue()
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
        qtqn__yxkrs = 'def impl(S_dt):\n'
        qtqn__yxkrs += '    S = S_dt._obj\n'
        qtqn__yxkrs += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        qtqn__yxkrs += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        qtqn__yxkrs += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        qtqn__yxkrs += '    numba.parfors.parfor.init_prange()\n'
        qtqn__yxkrs += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            qtqn__yxkrs += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            qtqn__yxkrs += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        qtqn__yxkrs += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        qtqn__yxkrs += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        qtqn__yxkrs += (
            '            bodo.libs.array_kernels.setna(out_arr, i)\n')
        qtqn__yxkrs += '            continue\n'
        qtqn__yxkrs += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            qtqn__yxkrs += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                qtqn__yxkrs += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            qtqn__yxkrs += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            mcaca__opxlf = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            qtqn__yxkrs += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            qtqn__yxkrs += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            qtqn__yxkrs += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(mcaca__opxlf[field]))
        elif field == 'is_leap_year':
            qtqn__yxkrs += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            qtqn__yxkrs += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            mcaca__opxlf = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            qtqn__yxkrs += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            qtqn__yxkrs += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            qtqn__yxkrs += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(mcaca__opxlf[field]))
        else:
            qtqn__yxkrs += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            qtqn__yxkrs += '        out_arr[i] = ts.' + field + '\n'
        qtqn__yxkrs += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        zph__jbtky = {}
        exec(qtqn__yxkrs, {'bodo': bodo, 'numba': numba, 'np': np}, zph__jbtky)
        impl = zph__jbtky['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        kvyet__onc = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(kvyet__onc)


_install_date_fields()


def create_date_method_overload(method):
    ean__zzgg = method in ['day_name', 'month_name']
    if ean__zzgg:
        qtqn__yxkrs = 'def overload_method(S_dt, locale=None):\n'
        qtqn__yxkrs += '    unsupported_args = dict(locale=locale)\n'
        qtqn__yxkrs += '    arg_defaults = dict(locale=None)\n'
        qtqn__yxkrs += '    bodo.utils.typing.check_unsupported_args(\n'
        qtqn__yxkrs += f"        'Series.dt.{method}',\n"
        qtqn__yxkrs += '        unsupported_args,\n'
        qtqn__yxkrs += '        arg_defaults,\n'
        qtqn__yxkrs += "        package_name='pandas',\n"
        qtqn__yxkrs += "        module_name='Series',\n"
        qtqn__yxkrs += '    )\n'
    else:
        qtqn__yxkrs = 'def overload_method(S_dt):\n'
        qtqn__yxkrs += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    qtqn__yxkrs += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    qtqn__yxkrs += '        return\n'
    if ean__zzgg:
        qtqn__yxkrs += '    def impl(S_dt, locale=None):\n'
    else:
        qtqn__yxkrs += '    def impl(S_dt):\n'
    qtqn__yxkrs += '        S = S_dt._obj\n'
    qtqn__yxkrs += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    qtqn__yxkrs += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    qtqn__yxkrs += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    qtqn__yxkrs += '        numba.parfors.parfor.init_prange()\n'
    qtqn__yxkrs += '        n = len(arr)\n'
    if ean__zzgg:
        qtqn__yxkrs += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        qtqn__yxkrs += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    qtqn__yxkrs += (
        '        for i in numba.parfors.parfor.internal_prange(n):\n')
    qtqn__yxkrs += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    qtqn__yxkrs += (
        '                bodo.libs.array_kernels.setna(out_arr, i)\n')
    qtqn__yxkrs += '                continue\n'
    qtqn__yxkrs += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    qtqn__yxkrs += f'            method_val = ts.{method}()\n'
    if ean__zzgg:
        qtqn__yxkrs += '            out_arr[i] = method_val\n'
    else:
        qtqn__yxkrs += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    qtqn__yxkrs += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    qtqn__yxkrs += '    return impl\n'
    zph__jbtky = {}
    exec(qtqn__yxkrs, {'bodo': bodo, 'numba': numba, 'np': np}, zph__jbtky)
    overload_method = zph__jbtky['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        kvyet__onc = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            kvyet__onc)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        rnve__sayzr = S_dt._obj
        fmlb__qob = bodo.hiframes.pd_series_ext.get_series_data(rnve__sayzr)
        mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rnve__sayzr)
        olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rnve__sayzr)
        numba.parfors.parfor.init_prange()
        sgbez__kyi = len(fmlb__qob)
        obx__nqmw = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            sgbez__kyi)
        for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi):
            utch__hypce = fmlb__qob[ruy__stt]
            wqc__oajn = bodo.utils.conversion.box_if_dt64(utch__hypce)
            obx__nqmw[ruy__stt] = datetime.date(wqc__oajn.year, wqc__oajn.
                month, wqc__oajn.day)
        return bodo.hiframes.pd_series_ext.init_series(obx__nqmw,
            mhx__cmokx, olh__tskrs)
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
            rqtd__ngerp = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            iyv__ruvv = 'convert_numpy_timedelta64_to_pd_timedelta'
            ozij__zzcng = 'np.empty(n, np.int64)'
            fnjn__hdi = attr
        elif attr == 'isocalendar':
            rqtd__ngerp = ['year', 'week', 'day']
            iyv__ruvv = 'convert_datetime64_to_timestamp'
            ozij__zzcng = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            fnjn__hdi = attr + '()'
        qtqn__yxkrs = 'def impl(S_dt):\n'
        qtqn__yxkrs += '    S = S_dt._obj\n'
        qtqn__yxkrs += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        qtqn__yxkrs += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        qtqn__yxkrs += '    numba.parfors.parfor.init_prange()\n'
        qtqn__yxkrs += '    n = len(arr)\n'
        for field in rqtd__ngerp:
            qtqn__yxkrs += '    {} = {}\n'.format(field, ozij__zzcng)
        qtqn__yxkrs += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        qtqn__yxkrs += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in rqtd__ngerp:
            qtqn__yxkrs += (
                '            bodo.libs.array_kernels.setna({}, i)\n'.format
                (field))
        qtqn__yxkrs += '            continue\n'
        ujpxf__caggp = '(' + '[i], '.join(rqtd__ngerp) + '[i])'
        qtqn__yxkrs += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(ujpxf__caggp, iyv__ruvv, fnjn__hdi))
        aeht__rszt = '(' + ', '.join(rqtd__ngerp) + ')'
        qtqn__yxkrs += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(aeht__rszt))
        zph__jbtky = {}
        exec(qtqn__yxkrs, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(rqtd__ngerp))}, zph__jbtky)
        impl = zph__jbtky['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    agmxw__tfwts = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, ocoe__legil in agmxw__tfwts:
        kvyet__onc = create_series_dt_df_output_overload(attr)
        ocoe__legil(SeriesDatetimePropertiesType, attr, inline='always')(
            kvyet__onc)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        qtqn__yxkrs = 'def impl(S_dt):\n'
        qtqn__yxkrs += '    S = S_dt._obj\n'
        qtqn__yxkrs += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        qtqn__yxkrs += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        qtqn__yxkrs += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        qtqn__yxkrs += '    numba.parfors.parfor.init_prange()\n'
        qtqn__yxkrs += '    n = len(A)\n'
        qtqn__yxkrs += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        qtqn__yxkrs += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        qtqn__yxkrs += '        if bodo.libs.array_kernels.isna(A, i):\n'
        qtqn__yxkrs += '            bodo.libs.array_kernels.setna(B, i)\n'
        qtqn__yxkrs += '            continue\n'
        qtqn__yxkrs += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            qtqn__yxkrs += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            qtqn__yxkrs += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            qtqn__yxkrs += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            qtqn__yxkrs += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        qtqn__yxkrs += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        zph__jbtky = {}
        exec(qtqn__yxkrs, {'numba': numba, 'np': np, 'bodo': bodo}, zph__jbtky)
        impl = zph__jbtky['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        qtqn__yxkrs = 'def impl(S_dt):\n'
        qtqn__yxkrs += '    S = S_dt._obj\n'
        qtqn__yxkrs += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        qtqn__yxkrs += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        qtqn__yxkrs += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        qtqn__yxkrs += '    numba.parfors.parfor.init_prange()\n'
        qtqn__yxkrs += '    n = len(A)\n'
        if method == 'total_seconds':
            qtqn__yxkrs += '    B = np.empty(n, np.float64)\n'
        else:
            qtqn__yxkrs += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        qtqn__yxkrs += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        qtqn__yxkrs += '        if bodo.libs.array_kernels.isna(A, i):\n'
        qtqn__yxkrs += '            bodo.libs.array_kernels.setna(B, i)\n'
        qtqn__yxkrs += '            continue\n'
        qtqn__yxkrs += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            qtqn__yxkrs += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            qtqn__yxkrs += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            qtqn__yxkrs += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            qtqn__yxkrs += '    return B\n'
        zph__jbtky = {}
        exec(qtqn__yxkrs, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, zph__jbtky)
        impl = zph__jbtky['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        kvyet__onc = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(kvyet__onc)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        kvyet__onc = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            kvyet__onc)


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
        rnve__sayzr = S_dt._obj
        vwf__kkaga = bodo.hiframes.pd_series_ext.get_series_data(rnve__sayzr)
        mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rnve__sayzr)
        olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rnve__sayzr)
        numba.parfors.parfor.init_prange()
        sgbez__kyi = len(vwf__kkaga)
        blvl__hhrpy = bodo.libs.str_arr_ext.pre_alloc_string_array(sgbez__kyi,
            -1)
        for jzj__uqp in numba.parfors.parfor.internal_prange(sgbez__kyi):
            if bodo.libs.array_kernels.isna(vwf__kkaga, jzj__uqp):
                bodo.libs.array_kernels.setna(blvl__hhrpy, jzj__uqp)
                continue
            blvl__hhrpy[jzj__uqp] = bodo.utils.conversion.box_if_dt64(
                vwf__kkaga[jzj__uqp]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(blvl__hhrpy,
            mhx__cmokx, olh__tskrs)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        rnve__sayzr = S_dt._obj
        ejno__tirp = get_series_data(rnve__sayzr).tz_convert(tz)
        mhx__cmokx = get_series_index(rnve__sayzr)
        olh__tskrs = get_series_name(rnve__sayzr)
        return init_series(ejno__tirp, mhx__cmokx, olh__tskrs)
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
        vwpa__lip = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        eyyl__ias = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', vwpa__lip, eyyl__ias,
            package_name='pandas', module_name='Series')
        qtqn__yxkrs = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        qtqn__yxkrs += '    S = S_dt._obj\n'
        qtqn__yxkrs += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        qtqn__yxkrs += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        qtqn__yxkrs += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        qtqn__yxkrs += '    numba.parfors.parfor.init_prange()\n'
        qtqn__yxkrs += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            qtqn__yxkrs += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            qtqn__yxkrs += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        qtqn__yxkrs += (
            '    for i in numba.parfors.parfor.internal_prange(n):\n')
        qtqn__yxkrs += '        if bodo.libs.array_kernels.isna(A, i):\n'
        qtqn__yxkrs += '            bodo.libs.array_kernels.setna(B, i)\n'
        qtqn__yxkrs += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            oyg__lvtbt = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            mzy__icthx = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            oyg__lvtbt = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            mzy__icthx = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        qtqn__yxkrs += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            mzy__icthx, oyg__lvtbt, method)
        qtqn__yxkrs += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        zph__jbtky = {}
        exec(qtqn__yxkrs, {'numba': numba, 'np': np, 'bodo': bodo}, zph__jbtky)
        impl = zph__jbtky['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    grovo__vxv = ['ceil', 'floor', 'round']
    for method in grovo__vxv:
        kvyet__onc = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            kvyet__onc)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                ifn__gthw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jlbg__fklr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    ifn__gthw)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                hpit__dplo = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                bassc__fvmqv = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    hpit__dplo)
                sgbez__kyi = len(jlbg__fklr)
                rnve__sayzr = np.empty(sgbez__kyi, timedelta64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    cxk__qso = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        jlbg__fklr[ruy__stt])
                    gjzo__ktz = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        bassc__fvmqv[ruy__stt])
                    if cxk__qso == cbpji__gkw or gjzo__ktz == cbpji__gkw:
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(cxk__qso, gjzo__ktz)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                bassc__fvmqv = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, dt64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    jjphd__cdrih = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(fmlb__qob[ruy__stt]))
                    rprfs__dfwxq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(bassc__fvmqv[ruy__stt]))
                    if (jjphd__cdrih == cbpji__gkw or rprfs__dfwxq ==
                        cbpji__gkw):
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(jjphd__cdrih, rprfs__dfwxq)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                bassc__fvmqv = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, dt64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    jjphd__cdrih = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(fmlb__qob[ruy__stt]))
                    rprfs__dfwxq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(bassc__fvmqv[ruy__stt]))
                    if (jjphd__cdrih == cbpji__gkw or rprfs__dfwxq ==
                        cbpji__gkw):
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(jjphd__cdrih, rprfs__dfwxq)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, timedelta64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                kobrt__xvy = rhs.value
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    jjphd__cdrih = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(fmlb__qob[ruy__stt]))
                    if jjphd__cdrih == cbpji__gkw or kobrt__xvy == cbpji__gkw:
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(jjphd__cdrih, kobrt__xvy)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, timedelta64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                kobrt__xvy = lhs.value
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    jjphd__cdrih = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(fmlb__qob[ruy__stt]))
                    if kobrt__xvy == cbpji__gkw or jjphd__cdrih == cbpji__gkw:
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(kobrt__xvy, jjphd__cdrih)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, dt64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                jyg__qheev = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                rprfs__dfwxq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jyg__qheev))
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    jjphd__cdrih = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(fmlb__qob[ruy__stt]))
                    if (jjphd__cdrih == cbpji__gkw or rprfs__dfwxq ==
                        cbpji__gkw):
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(jjphd__cdrih, rprfs__dfwxq)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, dt64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                jyg__qheev = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                rprfs__dfwxq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jyg__qheev))
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    jjphd__cdrih = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(fmlb__qob[ruy__stt]))
                    if (jjphd__cdrih == cbpji__gkw or rprfs__dfwxq ==
                        cbpji__gkw):
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(jjphd__cdrih, rprfs__dfwxq)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, timedelta64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                utk__gtai = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                jjphd__cdrih = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    utk__gtai)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    zhh__bwe = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        fmlb__qob[ruy__stt])
                    if zhh__bwe == cbpji__gkw or jjphd__cdrih == cbpji__gkw:
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(zhh__bwe, jjphd__cdrih)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, timedelta64_dtype)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                utk__gtai = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                jjphd__cdrih = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    utk__gtai)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    zhh__bwe = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        fmlb__qob[ruy__stt])
                    if jjphd__cdrih == cbpji__gkw or zhh__bwe == cbpji__gkw:
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(jjphd__cdrih, zhh__bwe)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            mjuf__nxpyz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fmlb__qob = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, timedelta64_dtype)
                cbpji__gkw = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mjuf__nxpyz))
                jyg__qheev = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                rprfs__dfwxq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jyg__qheev))
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    vwyov__ijcly = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(fmlb__qob[ruy__stt]))
                    if (rprfs__dfwxq == cbpji__gkw or vwyov__ijcly ==
                        cbpji__gkw):
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(vwyov__ijcly, rprfs__dfwxq)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            mjuf__nxpyz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fmlb__qob = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                sgbez__kyi = len(fmlb__qob)
                rnve__sayzr = np.empty(sgbez__kyi, timedelta64_dtype)
                cbpji__gkw = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mjuf__nxpyz))
                jyg__qheev = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                rprfs__dfwxq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jyg__qheev))
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    vwyov__ijcly = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(fmlb__qob[ruy__stt]))
                    if (rprfs__dfwxq == cbpji__gkw or vwyov__ijcly ==
                        cbpji__gkw):
                        penqz__tieby = cbpji__gkw
                    else:
                        penqz__tieby = op(rprfs__dfwxq, vwyov__ijcly)
                    rnve__sayzr[ruy__stt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        penqz__tieby)
                return bodo.hiframes.pd_series_ext.init_series(rnve__sayzr,
                    mhx__cmokx, olh__tskrs)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            aty__tfd = True
        else:
            aty__tfd = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            mjuf__nxpyz = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fmlb__qob = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                sgbez__kyi = len(fmlb__qob)
                obx__nqmw = bodo.libs.bool_arr_ext.alloc_bool_array(sgbez__kyi)
                cbpji__gkw = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mjuf__nxpyz))
                luxi__ahj = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                dec__qrh = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(luxi__ahj))
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    fqz__nwctg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(fmlb__qob[ruy__stt]))
                    if fqz__nwctg == cbpji__gkw or dec__qrh == cbpji__gkw:
                        penqz__tieby = aty__tfd
                    else:
                        penqz__tieby = op(fqz__nwctg, dec__qrh)
                    obx__nqmw[ruy__stt] = penqz__tieby
                return bodo.hiframes.pd_series_ext.init_series(obx__nqmw,
                    mhx__cmokx, olh__tskrs)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            mjuf__nxpyz = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fmlb__qob = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                sgbez__kyi = len(fmlb__qob)
                obx__nqmw = bodo.libs.bool_arr_ext.alloc_bool_array(sgbez__kyi)
                cbpji__gkw = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(mjuf__nxpyz))
                dujk__drtu = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                fqz__nwctg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dujk__drtu))
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    dec__qrh = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(fmlb__qob[ruy__stt]))
                    if fqz__nwctg == cbpji__gkw or dec__qrh == cbpji__gkw:
                        penqz__tieby = aty__tfd
                    else:
                        penqz__tieby = op(fqz__nwctg, dec__qrh)
                    obx__nqmw[ruy__stt] = penqz__tieby
                return bodo.hiframes.pd_series_ext.init_series(obx__nqmw,
                    mhx__cmokx, olh__tskrs)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                sgbez__kyi = len(fmlb__qob)
                obx__nqmw = bodo.libs.bool_arr_ext.alloc_bool_array(sgbez__kyi)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    fqz__nwctg = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(fmlb__qob[ruy__stt]))
                    if fqz__nwctg == cbpji__gkw or rhs.value == cbpji__gkw:
                        penqz__tieby = aty__tfd
                    else:
                        penqz__tieby = op(fqz__nwctg, rhs.value)
                    obx__nqmw[ruy__stt] = penqz__tieby
                return bodo.hiframes.pd_series_ext.init_series(obx__nqmw,
                    mhx__cmokx, olh__tskrs)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                sgbez__kyi = len(fmlb__qob)
                obx__nqmw = bodo.libs.bool_arr_ext.alloc_bool_array(sgbez__kyi)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    dec__qrh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        fmlb__qob[ruy__stt])
                    if dec__qrh == cbpji__gkw or lhs.value == cbpji__gkw:
                        penqz__tieby = aty__tfd
                    else:
                        penqz__tieby = op(lhs.value, dec__qrh)
                    obx__nqmw[ruy__stt] = penqz__tieby
                return bodo.hiframes.pd_series_ext.init_series(obx__nqmw,
                    mhx__cmokx, olh__tskrs)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                sgbez__kyi = len(fmlb__qob)
                obx__nqmw = bodo.libs.bool_arr_ext.alloc_bool_array(sgbez__kyi)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                evch__gcd = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                orkxd__jwi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    evch__gcd)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    fqz__nwctg = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(fmlb__qob[ruy__stt]))
                    if fqz__nwctg == cbpji__gkw or orkxd__jwi == cbpji__gkw:
                        penqz__tieby = aty__tfd
                    else:
                        penqz__tieby = op(fqz__nwctg, orkxd__jwi)
                    obx__nqmw[ruy__stt] = penqz__tieby
                return bodo.hiframes.pd_series_ext.init_series(obx__nqmw,
                    mhx__cmokx, olh__tskrs)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            mjuf__nxpyz = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                lpthr__zdf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                fmlb__qob = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    lpthr__zdf)
                mhx__cmokx = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                olh__tskrs = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                sgbez__kyi = len(fmlb__qob)
                obx__nqmw = bodo.libs.bool_arr_ext.alloc_bool_array(sgbez__kyi)
                cbpji__gkw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    mjuf__nxpyz)
                evch__gcd = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                orkxd__jwi = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    evch__gcd)
                for ruy__stt in numba.parfors.parfor.internal_prange(sgbez__kyi
                    ):
                    utk__gtai = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        fmlb__qob[ruy__stt])
                    if utk__gtai == cbpji__gkw or orkxd__jwi == cbpji__gkw:
                        penqz__tieby = aty__tfd
                    else:
                        penqz__tieby = op(orkxd__jwi, utk__gtai)
                    obx__nqmw[ruy__stt] = penqz__tieby
                return bodo.hiframes.pd_series_ext.init_series(obx__nqmw,
                    mhx__cmokx, olh__tskrs)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for awqam__uhyp in series_dt_unsupported_attrs:
        gyvi__idly = 'Series.dt.' + awqam__uhyp
        overload_attribute(SeriesDatetimePropertiesType, awqam__uhyp)(
            create_unsupported_overload(gyvi__idly))
    for vuqgg__doec in series_dt_unsupported_methods:
        gyvi__idly = 'Series.dt.' + vuqgg__doec
        overload_method(SeriesDatetimePropertiesType, vuqgg__doec,
            no_unliteral=True)(create_unsupported_overload(gyvi__idly))


_install_series_dt_unsupported()
