"""typing for rolling window functions
"""
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model
import bodo
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.hiframes.pd_groupby_ext import DataFrameGroupByType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.rolling import supported_rolling_funcs, unsupported_rolling_methods
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, get_literal_value, is_const_func_type, is_literal_type, is_overload_bool, is_overload_constant_str, is_overload_int, is_overload_none, raise_bodo_error


class RollingType(types.Type):

    def __init__(self, obj_type, window_type, on, selection,
        explicit_select=False, series_select=False):
        if isinstance(obj_type, bodo.SeriesType):
            hscnr__uzvyh = 'Series'
        else:
            hscnr__uzvyh = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{hscnr__uzvyh}.rolling()')
        self.obj_type = obj_type
        self.window_type = window_type
        self.on = on
        self.selection = selection
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(RollingType, self).__init__(name=
            f'RollingType({obj_type}, {window_type}, {on}, {selection}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return RollingType(self.obj_type, self.window_type, self.on, self.
            selection, self.explicit_select, self.series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(RollingType)
class RollingModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ake__apaz = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, ake__apaz)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    wia__gmzu = dict(win_type=win_type, axis=axis, closed=closed)
    max__izh = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', wia__gmzu, max__izh,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(df, window, min_periods, center, on)

    def impl(df, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(df, window,
            min_periods, center, on)
    return impl


@overload_method(SeriesType, 'rolling', inline='always', no_unliteral=True)
def overload_series_rolling(S, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    wia__gmzu = dict(win_type=win_type, axis=axis, closed=closed)
    max__izh = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', wia__gmzu, max__izh,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(S, window, min_periods, center, on)

    def impl(S, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(S, window,
            min_periods, center, on)
    return impl


@intrinsic
def init_rolling(typingctx, obj_type, window_type, min_periods_type,
    center_type, on_type=None):

    def codegen(context, builder, signature, args):
        ipky__bcora, szna__lfbn, gmq__ayrjb, mdf__cbof, ffjfy__tbl = args
        pcweh__vcy = signature.return_type
        ejv__sowmb = cgutils.create_struct_proxy(pcweh__vcy)(context, builder)
        ejv__sowmb.obj = ipky__bcora
        ejv__sowmb.window = szna__lfbn
        ejv__sowmb.min_periods = gmq__ayrjb
        ejv__sowmb.center = mdf__cbof
        context.nrt.incref(builder, signature.args[0], ipky__bcora)
        context.nrt.incref(builder, signature.args[1], szna__lfbn)
        context.nrt.incref(builder, signature.args[2], gmq__ayrjb)
        context.nrt.incref(builder, signature.args[3], mdf__cbof)
        return ejv__sowmb._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    pcweh__vcy = RollingType(obj_type, window_type, on, selection, False)
    return pcweh__vcy(obj_type, window_type, min_periods_type, center_type,
        on_type), codegen


def _handle_default_min_periods(min_periods, window):
    return min_periods


@overload(_handle_default_min_periods)
def overload_handle_default_min_periods(min_periods, window):
    if is_overload_none(min_periods):
        if isinstance(window, types.Integer):
            return lambda min_periods, window: window
        else:
            return lambda min_periods, window: 1
    else:
        return lambda min_periods, window: min_periods


def _gen_df_rolling_out_data(rolling):
    spdp__tjvho = not isinstance(rolling.window_type, types.Integer)
    bjvcc__mmac = 'variable' if spdp__tjvho else 'fixed'
    whcg__fjnho = 'None'
    if spdp__tjvho:
        whcg__fjnho = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    qrt__afixm = []
    svkp__qfs = 'on_arr, ' if spdp__tjvho else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{bjvcc__mmac}(bodo.hiframes.pd_series_ext.get_series_data(df), {svkp__qfs}index_arr, window, minp, center, func, raw)'
            , whcg__fjnho, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    kmov__khw = rolling.obj_type.data
    out_cols = []
    for nvx__atgva in rolling.selection:
        bbw__stnz = rolling.obj_type.columns.index(nvx__atgva)
        if nvx__atgva == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            cxcut__wva = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {bbw__stnz})'
                )
            out_cols.append(nvx__atgva)
        else:
            if not isinstance(kmov__khw[bbw__stnz].dtype, (types.Boolean,
                types.Number)):
                continue
            cxcut__wva = (
                f'bodo.hiframes.rolling.rolling_{bjvcc__mmac}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {bbw__stnz}), {svkp__qfs}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(nvx__atgva)
        qrt__afixm.append(cxcut__wva)
    return ', '.join(qrt__afixm), whcg__fjnho, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    wia__gmzu = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    max__izh = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', wia__gmzu, max__izh,
        package_name='pandas', module_name='Window')
    if not is_const_func_type(func):
        raise BodoError(
            f"Rolling.apply(): 'func' parameter must be a function, not {func} (builtin functions not supported yet)."
            )
    if not is_overload_bool(raw):
        raise BodoError(
            f"Rolling.apply(): 'raw' parameter must be bool, not {raw}.")
    return _gen_rolling_impl(rolling, 'apply')


@overload_method(DataFrameGroupByType, 'rolling', inline='always',
    no_unliteral=True)
def groupby_rolling_overload(grp, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None, method='single'):
    wia__gmzu = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    max__izh = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', wia__gmzu, max__izh,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(grp, window, min_periods, center, on)

    def _impl(grp, window, min_periods=None, center=False, win_type=None,
        on=None, axis=0, closed=None, method='single'):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(grp, window,
            min_periods, center, on)
    return _impl


def _gen_rolling_impl(rolling, fname, other=None):
    if isinstance(rolling.obj_type, DataFrameGroupByType):
        eht__jdw = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        bhj__opq = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{mdmb__awlg}'" if
                isinstance(mdmb__awlg, str) else f'{mdmb__awlg}' for
                mdmb__awlg in rolling.selection if mdmb__awlg != rolling.on))
        ppkxd__lupge = xlr__vshah = ''
        if fname == 'apply':
            ppkxd__lupge = 'func, raw, args, kwargs'
            xlr__vshah = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            ppkxd__lupge = xlr__vshah = 'other, pairwise'
        if fname == 'cov':
            ppkxd__lupge = xlr__vshah = 'other, pairwise, ddof'
        orhj__csyeq = (
            f'lambda df, window, minp, center, {ppkxd__lupge}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {bhj__opq}){selection}.{fname}({xlr__vshah})'
            )
        eht__jdw += f"""  return rolling.obj.apply({orhj__csyeq}, rolling.window, rolling.min_periods, rolling.center, {ppkxd__lupge})
"""
        vxa__cmf = {}
        exec(eht__jdw, {'bodo': bodo}, vxa__cmf)
        impl = vxa__cmf['impl']
        return impl
    yjwnf__vxh = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if yjwnf__vxh else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if yjwnf__vxh else rolling.obj_type.columns
        other_cols = None if yjwnf__vxh else other.columns
        qrt__afixm, whcg__fjnho = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        qrt__afixm, whcg__fjnho, out_cols = _gen_df_rolling_out_data(rolling)
    hsmy__ptw = yjwnf__vxh or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    zxv__pel = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    zxv__pel += '  df = rolling.obj\n'
    zxv__pel += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if yjwnf__vxh else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    hscnr__uzvyh = 'None'
    if yjwnf__vxh:
        hscnr__uzvyh = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif hsmy__ptw:
        nvx__atgva = (set(out_cols) - set([rolling.on])).pop()
        hscnr__uzvyh = f"'{nvx__atgva}'" if isinstance(nvx__atgva, str
            ) else str(nvx__atgva)
    zxv__pel += f'  name = {hscnr__uzvyh}\n'
    zxv__pel += '  window = rolling.window\n'
    zxv__pel += '  center = rolling.center\n'
    zxv__pel += '  minp = rolling.min_periods\n'
    zxv__pel += f'  on_arr = {whcg__fjnho}\n'
    if fname == 'apply':
        zxv__pel += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        zxv__pel += f"  func = '{fname}'\n"
        zxv__pel += f'  index_arr = None\n'
        zxv__pel += f'  raw = False\n'
    if hsmy__ptw:
        zxv__pel += (
            f'  return bodo.hiframes.pd_series_ext.init_series({qrt__afixm}, index, name)'
            )
        vxa__cmf = {}
        ummbt__rntqq = {'bodo': bodo}
        exec(zxv__pel, ummbt__rntqq, vxa__cmf)
        impl = vxa__cmf['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(zxv__pel, out_cols,
        qrt__afixm)


def _get_rolling_func_args(fname):
    if fname == 'apply':
        return (
            'func, raw=False, engine=None, engine_kwargs=None, args=None, kwargs=None\n'
            )
    elif fname == 'corr':
        return 'other=None, pairwise=None, ddof=1\n'
    elif fname == 'cov':
        return 'other=None, pairwise=None, ddof=1\n'
    return ''


def create_rolling_overload(fname):

    def overload_rolling_func(rolling):
        return _gen_rolling_impl(rolling, fname)
    return overload_rolling_func


def _install_rolling_methods():
    for fname in supported_rolling_funcs:
        if fname in ('apply', 'corr', 'cov'):
            continue
        avxhu__ledf = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(avxhu__ledf)


def _install_rolling_unsupported_methods():
    for fname in unsupported_rolling_methods:
        overload_method(RollingType, fname, no_unliteral=True)(
            create_unsupported_overload(
            f'pandas.core.window.rolling.Rolling.{fname}()'))


_install_rolling_methods()
_install_rolling_unsupported_methods()


def _get_corr_cov_out_cols(rolling, other, func_name):
    if not isinstance(other, DataFrameType):
        raise_bodo_error(
            f"DataFrame.rolling.{func_name}(): requires providing a DataFrame for 'other'"
            )
    syf__wce = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(syf__wce) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    spdp__tjvho = not isinstance(window_type, types.Integer)
    whcg__fjnho = 'None'
    if spdp__tjvho:
        whcg__fjnho = 'bodo.utils.conversion.index_to_array(index)'
    svkp__qfs = 'on_arr, ' if spdp__tjvho else ''
    qrt__afixm = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {svkp__qfs}window, minp, center)'
            , whcg__fjnho)
    for nvx__atgva in out_cols:
        if nvx__atgva in df_cols and nvx__atgva in other_cols:
            wwd__odjx = df_cols.index(nvx__atgva)
            sskeu__peyiz = other_cols.index(nvx__atgva)
            cxcut__wva = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {wwd__odjx}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {sskeu__peyiz}), {svkp__qfs}window, minp, center)'
                )
        else:
            cxcut__wva = 'np.full(len(df), np.nan)'
        qrt__afixm.append(cxcut__wva)
    return ', '.join(qrt__afixm), whcg__fjnho


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    tod__wqso = {'pairwise': pairwise, 'ddof': ddof}
    uytw__ewmo = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        tod__wqso, uytw__ewmo, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    tod__wqso = {'ddof': ddof, 'pairwise': pairwise}
    uytw__ewmo = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        tod__wqso, uytw__ewmo, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, egyp__xol = args
        if isinstance(rolling, RollingType):
            syf__wce = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(egyp__xol, (tuple, list)):
                if len(set(egyp__xol).difference(set(syf__wce))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(egyp__xol).difference(set(syf__wce))))
                selection = list(egyp__xol)
            else:
                if egyp__xol not in syf__wce:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(egyp__xol))
                selection = [egyp__xol]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            hilkz__peom = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(hilkz__peom, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        syf__wce = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            syf__wce = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            syf__wce = rolling.obj_type.columns
        if attr in syf__wce:
            return RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, (attr,) if rolling.on is None else (attr,
                rolling.on), True, True)


def _validate_rolling_args(obj, window, min_periods, center, on):
    assert isinstance(obj, (SeriesType, DataFrameType, DataFrameGroupByType)
        ), 'invalid rolling obj'
    func_name = 'Series' if isinstance(obj, SeriesType
        ) else 'DataFrame' if isinstance(obj, DataFrameType
        ) else 'DataFrameGroupBy'
    if not (is_overload_int(window) or is_overload_constant_str(window) or 
        window == bodo.string_type or window in (pd_timedelta_type,
        datetime_timedelta_type)):
        raise BodoError(
            f"{func_name}.rolling(): 'window' should be int or time offset (str, pd.Timedelta, datetime.timedelta), not {window}"
            )
    if not is_overload_bool(center):
        raise BodoError(
            f'{func_name}.rolling(): center must be a boolean, not {center}')
    if not (is_overload_none(min_periods) or isinstance(min_periods, types.
        Integer)):
        raise BodoError(
            f'{func_name}.rolling(): min_periods must be an integer, not {min_periods}'
            )
    if isinstance(obj, SeriesType) and not is_overload_none(on):
        raise BodoError(
            f"{func_name}.rolling(): 'on' not supported for Series yet (can use a DataFrame instead)."
            )
    uvlsv__ogx = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    kmov__khw = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in uvlsv__ogx):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        zcfjh__jya = kmov__khw[uvlsv__ogx.index(get_literal_value(on))]
        if not isinstance(zcfjh__jya, types.Array
            ) or zcfjh__jya.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(vixvb__rxsy.dtype, (types.Boolean, types.Number)) for
        vixvb__rxsy in kmov__khw):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
