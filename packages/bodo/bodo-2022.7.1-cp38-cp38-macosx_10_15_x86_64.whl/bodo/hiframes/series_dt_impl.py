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
        rlz__cae = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(rlz__cae)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        omko__izw = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, omko__izw)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        mquhd__fwkdw, = args
        fubz__htf = signature.return_type
        eeb__iugod = cgutils.create_struct_proxy(fubz__htf)(context, builder)
        eeb__iugod.obj = mquhd__fwkdw
        context.nrt.incref(builder, signature.args[0], mquhd__fwkdw)
        return eeb__iugod._getvalue()
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
        tmyy__grt = 'def impl(S_dt):\n'
        tmyy__grt += '    S = S_dt._obj\n'
        tmyy__grt += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        tmyy__grt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tmyy__grt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tmyy__grt += '    numba.parfors.parfor.init_prange()\n'
        tmyy__grt += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            tmyy__grt += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            tmyy__grt += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        tmyy__grt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        tmyy__grt += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        tmyy__grt += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        tmyy__grt += '            continue\n'
        tmyy__grt += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            tmyy__grt += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                tmyy__grt += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            tmyy__grt += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            jrmck__rija = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            tmyy__grt += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            tmyy__grt += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            tmyy__grt += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(jrmck__rija[field]))
        elif field == 'is_leap_year':
            tmyy__grt += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            tmyy__grt += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)\n'
                )
        elif field in ('daysinmonth', 'days_in_month'):
            jrmck__rija = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            tmyy__grt += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            tmyy__grt += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            tmyy__grt += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(jrmck__rija[field]))
        else:
            tmyy__grt += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            tmyy__grt += '        out_arr[i] = ts.' + field + '\n'
        tmyy__grt += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        kycw__azraj = {}
        exec(tmyy__grt, {'bodo': bodo, 'numba': numba, 'np': np}, kycw__azraj)
        impl = kycw__azraj['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        gsz__zcno = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(gsz__zcno)


_install_date_fields()


def create_date_method_overload(method):
    gpinj__ypily = method in ['day_name', 'month_name']
    if gpinj__ypily:
        tmyy__grt = 'def overload_method(S_dt, locale=None):\n'
        tmyy__grt += '    unsupported_args = dict(locale=locale)\n'
        tmyy__grt += '    arg_defaults = dict(locale=None)\n'
        tmyy__grt += '    bodo.utils.typing.check_unsupported_args(\n'
        tmyy__grt += f"        'Series.dt.{method}',\n"
        tmyy__grt += '        unsupported_args,\n'
        tmyy__grt += '        arg_defaults,\n'
        tmyy__grt += "        package_name='pandas',\n"
        tmyy__grt += "        module_name='Series',\n"
        tmyy__grt += '    )\n'
    else:
        tmyy__grt = 'def overload_method(S_dt):\n'
        tmyy__grt += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    tmyy__grt += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    tmyy__grt += '        return\n'
    if gpinj__ypily:
        tmyy__grt += '    def impl(S_dt, locale=None):\n'
    else:
        tmyy__grt += '    def impl(S_dt):\n'
    tmyy__grt += '        S = S_dt._obj\n'
    tmyy__grt += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    tmyy__grt += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    tmyy__grt += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    tmyy__grt += '        numba.parfors.parfor.init_prange()\n'
    tmyy__grt += '        n = len(arr)\n'
    if gpinj__ypily:
        tmyy__grt += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        tmyy__grt += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    tmyy__grt += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    tmyy__grt += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    tmyy__grt += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    tmyy__grt += '                continue\n'
    tmyy__grt += '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n'
    tmyy__grt += f'            method_val = ts.{method}()\n'
    if gpinj__ypily:
        tmyy__grt += '            out_arr[i] = method_val\n'
    else:
        tmyy__grt += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    tmyy__grt += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    tmyy__grt += '    return impl\n'
    kycw__azraj = {}
    exec(tmyy__grt, {'bodo': bodo, 'numba': numba, 'np': np}, kycw__azraj)
    overload_method = kycw__azraj['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        gsz__zcno = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            gsz__zcno)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        vayxd__qsjq = S_dt._obj
        yrgyp__kwsd = bodo.hiframes.pd_series_ext.get_series_data(vayxd__qsjq)
        iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(vayxd__qsjq)
        rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(vayxd__qsjq)
        numba.parfors.parfor.init_prange()
        nsp__wzrpo = len(yrgyp__kwsd)
        gvl__kzkj = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            nsp__wzrpo)
        for szjrk__oibme in numba.parfors.parfor.internal_prange(nsp__wzrpo):
            vaq__aqig = yrgyp__kwsd[szjrk__oibme]
            jua__nlc = bodo.utils.conversion.box_if_dt64(vaq__aqig)
            gvl__kzkj[szjrk__oibme] = datetime.date(jua__nlc.year, jua__nlc
                .month, jua__nlc.day)
        return bodo.hiframes.pd_series_ext.init_series(gvl__kzkj,
            iswd__qiunl, rlz__cae)
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
            igv__gabz = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            lhz__vbz = 'convert_numpy_timedelta64_to_pd_timedelta'
            bul__moqsh = 'np.empty(n, np.int64)'
            zjqq__wqnst = attr
        elif attr == 'isocalendar':
            igv__gabz = ['year', 'week', 'day']
            lhz__vbz = 'convert_datetime64_to_timestamp'
            bul__moqsh = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            zjqq__wqnst = attr + '()'
        tmyy__grt = 'def impl(S_dt):\n'
        tmyy__grt += '    S = S_dt._obj\n'
        tmyy__grt += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        tmyy__grt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tmyy__grt += '    numba.parfors.parfor.init_prange()\n'
        tmyy__grt += '    n = len(arr)\n'
        for field in igv__gabz:
            tmyy__grt += '    {} = {}\n'.format(field, bul__moqsh)
        tmyy__grt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        tmyy__grt += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in igv__gabz:
            tmyy__grt += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        tmyy__grt += '            continue\n'
        yldq__amkhg = '(' + '[i], '.join(igv__gabz) + '[i])'
        tmyy__grt += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(yldq__amkhg, lhz__vbz, zjqq__wqnst))
        mfq__kyqn = '(' + ', '.join(igv__gabz) + ')'
        tmyy__grt += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(mfq__kyqn))
        kycw__azraj = {}
        exec(tmyy__grt, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(igv__gabz))}, kycw__azraj)
        impl = kycw__azraj['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    wfmz__uup = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, ybihg__xyejz in wfmz__uup:
        gsz__zcno = create_series_dt_df_output_overload(attr)
        ybihg__xyejz(SeriesDatetimePropertiesType, attr, inline='always')(
            gsz__zcno)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        tmyy__grt = 'def impl(S_dt):\n'
        tmyy__grt += '    S = S_dt._obj\n'
        tmyy__grt += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        tmyy__grt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tmyy__grt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tmyy__grt += '    numba.parfors.parfor.init_prange()\n'
        tmyy__grt += '    n = len(A)\n'
        tmyy__grt += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        tmyy__grt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        tmyy__grt += '        if bodo.libs.array_kernels.isna(A, i):\n'
        tmyy__grt += '            bodo.libs.array_kernels.setna(B, i)\n'
        tmyy__grt += '            continue\n'
        tmyy__grt += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if field == 'nanoseconds':
            tmyy__grt += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            tmyy__grt += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            tmyy__grt += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            tmyy__grt += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        tmyy__grt += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        kycw__azraj = {}
        exec(tmyy__grt, {'numba': numba, 'np': np, 'bodo': bodo}, kycw__azraj)
        impl = kycw__azraj['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        tmyy__grt = 'def impl(S_dt):\n'
        tmyy__grt += '    S = S_dt._obj\n'
        tmyy__grt += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        tmyy__grt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tmyy__grt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tmyy__grt += '    numba.parfors.parfor.init_prange()\n'
        tmyy__grt += '    n = len(A)\n'
        if method == 'total_seconds':
            tmyy__grt += '    B = np.empty(n, np.float64)\n'
        else:
            tmyy__grt += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        tmyy__grt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        tmyy__grt += '        if bodo.libs.array_kernels.isna(A, i):\n'
        tmyy__grt += '            bodo.libs.array_kernels.setna(B, i)\n'
        tmyy__grt += '            continue\n'
        tmyy__grt += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if method == 'total_seconds':
            tmyy__grt += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            tmyy__grt += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            tmyy__grt += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            tmyy__grt += '    return B\n'
        kycw__azraj = {}
        exec(tmyy__grt, {'numba': numba, 'np': np, 'bodo': bodo, 'datetime':
            datetime}, kycw__azraj)
        impl = kycw__azraj['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        gsz__zcno = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(gsz__zcno)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        gsz__zcno = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            gsz__zcno)


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
        vayxd__qsjq = S_dt._obj
        afeq__sqpd = bodo.hiframes.pd_series_ext.get_series_data(vayxd__qsjq)
        iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(vayxd__qsjq)
        rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(vayxd__qsjq)
        numba.parfors.parfor.init_prange()
        nsp__wzrpo = len(afeq__sqpd)
        qrpxl__lff = bodo.libs.str_arr_ext.pre_alloc_string_array(nsp__wzrpo,
            -1)
        for jeryi__cdqbv in numba.parfors.parfor.internal_prange(nsp__wzrpo):
            if bodo.libs.array_kernels.isna(afeq__sqpd, jeryi__cdqbv):
                bodo.libs.array_kernels.setna(qrpxl__lff, jeryi__cdqbv)
                continue
            qrpxl__lff[jeryi__cdqbv] = bodo.utils.conversion.box_if_dt64(
                afeq__sqpd[jeryi__cdqbv]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(qrpxl__lff,
            iswd__qiunl, rlz__cae)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        vayxd__qsjq = S_dt._obj
        nixv__pcb = get_series_data(vayxd__qsjq).tz_convert(tz)
        iswd__qiunl = get_series_index(vayxd__qsjq)
        rlz__cae = get_series_name(vayxd__qsjq)
        return init_series(nixv__pcb, iswd__qiunl, rlz__cae)
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
        wjr__yij = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        xsyr__znvyr = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', wjr__yij, xsyr__znvyr,
            package_name='pandas', module_name='Series')
        tmyy__grt = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        tmyy__grt += '    S = S_dt._obj\n'
        tmyy__grt += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        tmyy__grt += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        tmyy__grt += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        tmyy__grt += '    numba.parfors.parfor.init_prange()\n'
        tmyy__grt += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            tmyy__grt += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            tmyy__grt += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        tmyy__grt += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        tmyy__grt += '        if bodo.libs.array_kernels.isna(A, i):\n'
        tmyy__grt += '            bodo.libs.array_kernels.setna(B, i)\n'
        tmyy__grt += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            vnol__urq = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            agvh__mwe = 'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64'
        else:
            vnol__urq = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            agvh__mwe = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        tmyy__grt += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            agvh__mwe, vnol__urq, method)
        tmyy__grt += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        kycw__azraj = {}
        exec(tmyy__grt, {'numba': numba, 'np': np, 'bodo': bodo}, kycw__azraj)
        impl = kycw__azraj['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    lrtt__lrnm = ['ceil', 'floor', 'round']
    for method in lrtt__lrnm:
        gsz__zcno = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            gsz__zcno)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                hru__ivpwh = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                apr__vpnee = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    hru__ivpwh)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                hhki__aaarz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pcrr__rxh = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    hhki__aaarz)
                nsp__wzrpo = len(apr__vpnee)
                vayxd__qsjq = np.empty(nsp__wzrpo, timedelta64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    yoab__fssue = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(apr__vpnee[szjrk__oibme]))
                    yht__ejjlm = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(pcrr__rxh[szjrk__oibme]))
                    if yoab__fssue == enhdw__vyod or yht__ejjlm == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(yoab__fssue, yht__ejjlm)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                pcrr__rxh = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, dt64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    cop__umivh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    ubc__hzpfq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(pcrr__rxh[szjrk__oibme]))
                    if cop__umivh == enhdw__vyod or ubc__hzpfq == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(cop__umivh, ubc__hzpfq)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                pcrr__rxh = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, dt64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    cop__umivh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    ubc__hzpfq = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(pcrr__rxh[szjrk__oibme]))
                    if cop__umivh == enhdw__vyod or ubc__hzpfq == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(cop__umivh, ubc__hzpfq)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, timedelta64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                cna__dsp = rhs.value
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    cop__umivh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if cop__umivh == enhdw__vyod or cna__dsp == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(cop__umivh, cna__dsp)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, timedelta64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                cna__dsp = lhs.value
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    cop__umivh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if cna__dsp == enhdw__vyod or cop__umivh == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(cna__dsp, cop__umivh)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, dt64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                prh__ppagw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                ubc__hzpfq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(prh__ppagw))
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    cop__umivh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if cop__umivh == enhdw__vyod or ubc__hzpfq == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(cop__umivh, ubc__hzpfq)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, dt64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                prh__ppagw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                ubc__hzpfq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(prh__ppagw))
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    cop__umivh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if cop__umivh == enhdw__vyod or ubc__hzpfq == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(cop__umivh, ubc__hzpfq)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, timedelta64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                ifowc__mie = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                cop__umivh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ifowc__mie)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    gzsc__ohrzu = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if gzsc__ohrzu == enhdw__vyod or cop__umivh == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(gzsc__ohrzu, cop__umivh)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, timedelta64_dtype)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                ifowc__mie = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                cop__umivh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ifowc__mie)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    gzsc__ohrzu = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if cop__umivh == enhdw__vyod or gzsc__ohrzu == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(cop__umivh, gzsc__ohrzu)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ssdqd__tnjy = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yrgyp__kwsd = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, timedelta64_dtype)
                enhdw__vyod = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ssdqd__tnjy))
                prh__ppagw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                ubc__hzpfq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(prh__ppagw))
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    wzyyz__yrj = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if ubc__hzpfq == enhdw__vyod or wzyyz__yrj == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(wzyyz__yrj, ubc__hzpfq)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ssdqd__tnjy = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yrgyp__kwsd = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                vayxd__qsjq = np.empty(nsp__wzrpo, timedelta64_dtype)
                enhdw__vyod = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ssdqd__tnjy))
                prh__ppagw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                ubc__hzpfq = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(prh__ppagw))
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    wzyyz__yrj = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if ubc__hzpfq == enhdw__vyod or wzyyz__yrj == enhdw__vyod:
                        uox__cutm = enhdw__vyod
                    else:
                        uox__cutm = op(ubc__hzpfq, wzyyz__yrj)
                    vayxd__qsjq[szjrk__oibme
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        uox__cutm)
                return bodo.hiframes.pd_series_ext.init_series(vayxd__qsjq,
                    iswd__qiunl, rlz__cae)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            hrdt__hgk = True
        else:
            hrdt__hgk = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ssdqd__tnjy = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yrgyp__kwsd = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                gvl__kzkj = bodo.libs.bool_arr_ext.alloc_bool_array(nsp__wzrpo)
                enhdw__vyod = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ssdqd__tnjy))
                afqw__yhue = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                lhkon__gmyu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(afqw__yhue))
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    spdzy__qrzf = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if (spdzy__qrzf == enhdw__vyod or lhkon__gmyu ==
                        enhdw__vyod):
                        uox__cutm = hrdt__hgk
                    else:
                        uox__cutm = op(spdzy__qrzf, lhkon__gmyu)
                    gvl__kzkj[szjrk__oibme] = uox__cutm
                return bodo.hiframes.pd_series_ext.init_series(gvl__kzkj,
                    iswd__qiunl, rlz__cae)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            ssdqd__tnjy = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yrgyp__kwsd = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                gvl__kzkj = bodo.libs.bool_arr_ext.alloc_bool_array(nsp__wzrpo)
                enhdw__vyod = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ssdqd__tnjy))
                qub__ilnp = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                spdzy__qrzf = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(qub__ilnp))
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    lhkon__gmyu = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if (spdzy__qrzf == enhdw__vyod or lhkon__gmyu ==
                        enhdw__vyod):
                        uox__cutm = hrdt__hgk
                    else:
                        uox__cutm = op(spdzy__qrzf, lhkon__gmyu)
                    gvl__kzkj[szjrk__oibme] = uox__cutm
                return bodo.hiframes.pd_series_ext.init_series(gvl__kzkj,
                    iswd__qiunl, rlz__cae)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                gvl__kzkj = bodo.libs.bool_arr_ext.alloc_bool_array(nsp__wzrpo)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    spdzy__qrzf = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if spdzy__qrzf == enhdw__vyod or rhs.value == enhdw__vyod:
                        uox__cutm = hrdt__hgk
                    else:
                        uox__cutm = op(spdzy__qrzf, rhs.value)
                    gvl__kzkj[szjrk__oibme] = uox__cutm
                return bodo.hiframes.pd_series_ext.init_series(gvl__kzkj,
                    iswd__qiunl, rlz__cae)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                nsp__wzrpo = len(yrgyp__kwsd)
                gvl__kzkj = bodo.libs.bool_arr_ext.alloc_bool_array(nsp__wzrpo)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    lhkon__gmyu = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if lhkon__gmyu == enhdw__vyod or lhs.value == enhdw__vyod:
                        uox__cutm = hrdt__hgk
                    else:
                        uox__cutm = op(lhs.value, lhkon__gmyu)
                    gvl__kzkj[szjrk__oibme] = uox__cutm
                return bodo.hiframes.pd_series_ext.init_series(gvl__kzkj,
                    iswd__qiunl, rlz__cae)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                nsp__wzrpo = len(yrgyp__kwsd)
                gvl__kzkj = bodo.libs.bool_arr_ext.alloc_bool_array(nsp__wzrpo)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                ryj__zjk = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                vxuys__wqlh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ryj__zjk)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    spdzy__qrzf = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if (spdzy__qrzf == enhdw__vyod or vxuys__wqlh ==
                        enhdw__vyod):
                        uox__cutm = hrdt__hgk
                    else:
                        uox__cutm = op(spdzy__qrzf, vxuys__wqlh)
                    gvl__kzkj[szjrk__oibme] = uox__cutm
                return bodo.hiframes.pd_series_ext.init_series(gvl__kzkj,
                    iswd__qiunl, rlz__cae)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            ssdqd__tnjy = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                uyb__sqp = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yrgyp__kwsd = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    uyb__sqp)
                iswd__qiunl = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                rlz__cae = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                nsp__wzrpo = len(yrgyp__kwsd)
                gvl__kzkj = bodo.libs.bool_arr_ext.alloc_bool_array(nsp__wzrpo)
                enhdw__vyod = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ssdqd__tnjy)
                ryj__zjk = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                vxuys__wqlh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    ryj__zjk)
                for szjrk__oibme in numba.parfors.parfor.internal_prange(
                    nsp__wzrpo):
                    ifowc__mie = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yrgyp__kwsd[szjrk__oibme]))
                    if ifowc__mie == enhdw__vyod or vxuys__wqlh == enhdw__vyod:
                        uox__cutm = hrdt__hgk
                    else:
                        uox__cutm = op(vxuys__wqlh, ifowc__mie)
                    gvl__kzkj[szjrk__oibme] = uox__cutm
                return bodo.hiframes.pd_series_ext.init_series(gvl__kzkj,
                    iswd__qiunl, rlz__cae)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for owyav__pksvw in series_dt_unsupported_attrs:
        pexu__ugldo = 'Series.dt.' + owyav__pksvw
        overload_attribute(SeriesDatetimePropertiesType, owyav__pksvw)(
            create_unsupported_overload(pexu__ugldo))
    for dsfbp__thiwo in series_dt_unsupported_methods:
        pexu__ugldo = 'Series.dt.' + dsfbp__thiwo
        overload_method(SeriesDatetimePropertiesType, dsfbp__thiwo,
            no_unliteral=True)(create_unsupported_overload(pexu__ugldo))


_install_series_dt_unsupported()
