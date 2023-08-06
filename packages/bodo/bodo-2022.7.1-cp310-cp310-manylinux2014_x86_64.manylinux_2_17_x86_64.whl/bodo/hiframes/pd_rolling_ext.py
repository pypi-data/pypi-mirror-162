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
            dljw__cbt = 'Series'
        else:
            dljw__cbt = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{dljw__cbt}.rolling()')
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
        gzjgc__jxmrw = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, gzjgc__jxmrw)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    mvlv__jnu = dict(win_type=win_type, axis=axis, closed=closed)
    wda__abcp = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', mvlv__jnu, wda__abcp,
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
    mvlv__jnu = dict(win_type=win_type, axis=axis, closed=closed)
    wda__abcp = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', mvlv__jnu, wda__abcp,
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
        grct__ecw, ore__eajpe, rofxa__lvytw, uyy__sbhd, bkqp__fwdt = args
        ofbk__yphkw = signature.return_type
        ojoe__vny = cgutils.create_struct_proxy(ofbk__yphkw)(context, builder)
        ojoe__vny.obj = grct__ecw
        ojoe__vny.window = ore__eajpe
        ojoe__vny.min_periods = rofxa__lvytw
        ojoe__vny.center = uyy__sbhd
        context.nrt.incref(builder, signature.args[0], grct__ecw)
        context.nrt.incref(builder, signature.args[1], ore__eajpe)
        context.nrt.incref(builder, signature.args[2], rofxa__lvytw)
        context.nrt.incref(builder, signature.args[3], uyy__sbhd)
        return ojoe__vny._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    ofbk__yphkw = RollingType(obj_type, window_type, on, selection, False)
    return ofbk__yphkw(obj_type, window_type, min_periods_type, center_type,
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
    wpu__lhspf = not isinstance(rolling.window_type, types.Integer)
    djmrb__vcq = 'variable' if wpu__lhspf else 'fixed'
    ylhvk__cvwel = 'None'
    if wpu__lhspf:
        ylhvk__cvwel = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    nhu__gxupz = []
    dlpl__zdeu = 'on_arr, ' if wpu__lhspf else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{djmrb__vcq}(bodo.hiframes.pd_series_ext.get_series_data(df), {dlpl__zdeu}index_arr, window, minp, center, func, raw)'
            , ylhvk__cvwel, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    hwyh__nwh = rolling.obj_type.data
    out_cols = []
    for jdumn__fcz in rolling.selection:
        vhpey__pok = rolling.obj_type.columns.index(jdumn__fcz)
        if jdumn__fcz == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            qtjbc__gcjd = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {vhpey__pok})'
                )
            out_cols.append(jdumn__fcz)
        else:
            if not isinstance(hwyh__nwh[vhpey__pok].dtype, (types.Boolean,
                types.Number)):
                continue
            qtjbc__gcjd = (
                f'bodo.hiframes.rolling.rolling_{djmrb__vcq}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {vhpey__pok}), {dlpl__zdeu}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(jdumn__fcz)
        nhu__gxupz.append(qtjbc__gcjd)
    return ', '.join(nhu__gxupz), ylhvk__cvwel, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    mvlv__jnu = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    wda__abcp = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', mvlv__jnu, wda__abcp,
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
    mvlv__jnu = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    wda__abcp = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', mvlv__jnu, wda__abcp,
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
        noou__obyk = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        mjdv__ugpr = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{lpicz__yntpn}'" if
                isinstance(lpicz__yntpn, str) else f'{lpicz__yntpn}' for
                lpicz__yntpn in rolling.selection if lpicz__yntpn !=
                rolling.on))
        yrjuz__gnexf = qhh__gej = ''
        if fname == 'apply':
            yrjuz__gnexf = 'func, raw, args, kwargs'
            qhh__gej = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            yrjuz__gnexf = qhh__gej = 'other, pairwise'
        if fname == 'cov':
            yrjuz__gnexf = qhh__gej = 'other, pairwise, ddof'
        abmb__ywez = (
            f'lambda df, window, minp, center, {yrjuz__gnexf}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {mjdv__ugpr}){selection}.{fname}({qhh__gej})'
            )
        noou__obyk += f"""  return rolling.obj.apply({abmb__ywez}, rolling.window, rolling.min_periods, rolling.center, {yrjuz__gnexf})
"""
        zgpl__ogklc = {}
        exec(noou__obyk, {'bodo': bodo}, zgpl__ogklc)
        impl = zgpl__ogklc['impl']
        return impl
    wnmfd__ane = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if wnmfd__ane else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if wnmfd__ane else rolling.obj_type.columns
        other_cols = None if wnmfd__ane else other.columns
        nhu__gxupz, ylhvk__cvwel = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        nhu__gxupz, ylhvk__cvwel, out_cols = _gen_df_rolling_out_data(rolling)
    xjxo__djcez = wnmfd__ane or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    kqjj__rxx = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    kqjj__rxx += '  df = rolling.obj\n'
    kqjj__rxx += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if wnmfd__ane else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    dljw__cbt = 'None'
    if wnmfd__ane:
        dljw__cbt = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif xjxo__djcez:
        jdumn__fcz = (set(out_cols) - set([rolling.on])).pop()
        dljw__cbt = f"'{jdumn__fcz}'" if isinstance(jdumn__fcz, str) else str(
            jdumn__fcz)
    kqjj__rxx += f'  name = {dljw__cbt}\n'
    kqjj__rxx += '  window = rolling.window\n'
    kqjj__rxx += '  center = rolling.center\n'
    kqjj__rxx += '  minp = rolling.min_periods\n'
    kqjj__rxx += f'  on_arr = {ylhvk__cvwel}\n'
    if fname == 'apply':
        kqjj__rxx += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        kqjj__rxx += f"  func = '{fname}'\n"
        kqjj__rxx += f'  index_arr = None\n'
        kqjj__rxx += f'  raw = False\n'
    if xjxo__djcez:
        kqjj__rxx += (
            f'  return bodo.hiframes.pd_series_ext.init_series({nhu__gxupz}, index, name)'
            )
        zgpl__ogklc = {}
        yfw__ogkw = {'bodo': bodo}
        exec(kqjj__rxx, yfw__ogkw, zgpl__ogklc)
        impl = zgpl__ogklc['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(kqjj__rxx, out_cols,
        nhu__gxupz)


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
        cme__gamzk = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(cme__gamzk)


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
    cimt__urem = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(cimt__urem) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    wpu__lhspf = not isinstance(window_type, types.Integer)
    ylhvk__cvwel = 'None'
    if wpu__lhspf:
        ylhvk__cvwel = 'bodo.utils.conversion.index_to_array(index)'
    dlpl__zdeu = 'on_arr, ' if wpu__lhspf else ''
    nhu__gxupz = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {dlpl__zdeu}window, minp, center)'
            , ylhvk__cvwel)
    for jdumn__fcz in out_cols:
        if jdumn__fcz in df_cols and jdumn__fcz in other_cols:
            yild__nzdba = df_cols.index(jdumn__fcz)
            pbtz__vufcy = other_cols.index(jdumn__fcz)
            qtjbc__gcjd = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {yild__nzdba}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {pbtz__vufcy}), {dlpl__zdeu}window, minp, center)'
                )
        else:
            qtjbc__gcjd = 'np.full(len(df), np.nan)'
        nhu__gxupz.append(qtjbc__gcjd)
    return ', '.join(nhu__gxupz), ylhvk__cvwel


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    zvno__pjx = {'pairwise': pairwise, 'ddof': ddof}
    cssnr__jzzz = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        zvno__pjx, cssnr__jzzz, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    zvno__pjx = {'ddof': ddof, 'pairwise': pairwise}
    cssnr__jzzz = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        zvno__pjx, cssnr__jzzz, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, abqy__givtu = args
        if isinstance(rolling, RollingType):
            cimt__urem = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(abqy__givtu, (tuple, list)):
                if len(set(abqy__givtu).difference(set(cimt__urem))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(abqy__givtu).difference(set(cimt__urem))))
                selection = list(abqy__givtu)
            else:
                if abqy__givtu not in cimt__urem:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(abqy__givtu))
                selection = [abqy__givtu]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            bmx__alpu = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(bmx__alpu, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        cimt__urem = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            cimt__urem = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            cimt__urem = rolling.obj_type.columns
        if attr in cimt__urem:
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
    tfc__vgf = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    hwyh__nwh = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in tfc__vgf):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        vqwl__aiul = hwyh__nwh[tfc__vgf.index(get_literal_value(on))]
        if not isinstance(vqwl__aiul, types.Array
            ) or vqwl__aiul.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(msjev__rmonh.dtype, (types.Boolean, types.Number)
        ) for msjev__rmonh in hwyh__nwh):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
