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
            ttzj__ipave = 'Series'
        else:
            ttzj__ipave = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{ttzj__ipave}.rolling()')
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
        bimuw__pflgv = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, bimuw__pflgv)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    klz__vpnx = dict(win_type=win_type, axis=axis, closed=closed)
    lmnae__bbwg = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', klz__vpnx, lmnae__bbwg,
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
    klz__vpnx = dict(win_type=win_type, axis=axis, closed=closed)
    lmnae__bbwg = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', klz__vpnx, lmnae__bbwg,
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
        bii__zyfqd, iecaf__iazsk, aoe__qklcg, qoh__lzjh, thgz__dii = args
        npz__igkx = signature.return_type
        vfv__hwom = cgutils.create_struct_proxy(npz__igkx)(context, builder)
        vfv__hwom.obj = bii__zyfqd
        vfv__hwom.window = iecaf__iazsk
        vfv__hwom.min_periods = aoe__qklcg
        vfv__hwom.center = qoh__lzjh
        context.nrt.incref(builder, signature.args[0], bii__zyfqd)
        context.nrt.incref(builder, signature.args[1], iecaf__iazsk)
        context.nrt.incref(builder, signature.args[2], aoe__qklcg)
        context.nrt.incref(builder, signature.args[3], qoh__lzjh)
        return vfv__hwom._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    npz__igkx = RollingType(obj_type, window_type, on, selection, False)
    return npz__igkx(obj_type, window_type, min_periods_type, center_type,
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
    fvb__khgip = not isinstance(rolling.window_type, types.Integer)
    zhl__adox = 'variable' if fvb__khgip else 'fixed'
    tfyau__ieqdi = 'None'
    if fvb__khgip:
        tfyau__ieqdi = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    miixf__lrk = []
    itvf__mliu = 'on_arr, ' if fvb__khgip else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{zhl__adox}(bodo.hiframes.pd_series_ext.get_series_data(df), {itvf__mliu}index_arr, window, minp, center, func, raw)'
            , tfyau__ieqdi, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    hukcm__ohu = rolling.obj_type.data
    out_cols = []
    for oism__fgl in rolling.selection:
        nvm__sgj = rolling.obj_type.columns.index(oism__fgl)
        if oism__fgl == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            zvm__pqmqq = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {nvm__sgj})'
                )
            out_cols.append(oism__fgl)
        else:
            if not isinstance(hukcm__ohu[nvm__sgj].dtype, (types.Boolean,
                types.Number)):
                continue
            zvm__pqmqq = (
                f'bodo.hiframes.rolling.rolling_{zhl__adox}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {nvm__sgj}), {itvf__mliu}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(oism__fgl)
        miixf__lrk.append(zvm__pqmqq)
    return ', '.join(miixf__lrk), tfyau__ieqdi, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    klz__vpnx = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    lmnae__bbwg = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', klz__vpnx, lmnae__bbwg,
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
    klz__vpnx = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    lmnae__bbwg = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', klz__vpnx, lmnae__bbwg,
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
        vxdd__tet = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        xhqd__ide = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{rrdwa__xok}'" if
                isinstance(rrdwa__xok, str) else f'{rrdwa__xok}' for
                rrdwa__xok in rolling.selection if rrdwa__xok != rolling.on))
        dseb__uew = xwru__twaw = ''
        if fname == 'apply':
            dseb__uew = 'func, raw, args, kwargs'
            xwru__twaw = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            dseb__uew = xwru__twaw = 'other, pairwise'
        if fname == 'cov':
            dseb__uew = xwru__twaw = 'other, pairwise, ddof'
        hws__mblpg = (
            f'lambda df, window, minp, center, {dseb__uew}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {xhqd__ide}){selection}.{fname}({xwru__twaw})'
            )
        vxdd__tet += f"""  return rolling.obj.apply({hws__mblpg}, rolling.window, rolling.min_periods, rolling.center, {dseb__uew})
"""
        qki__qlpg = {}
        exec(vxdd__tet, {'bodo': bodo}, qki__qlpg)
        impl = qki__qlpg['impl']
        return impl
    bpnf__vubd = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if bpnf__vubd else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if bpnf__vubd else rolling.obj_type.columns
        other_cols = None if bpnf__vubd else other.columns
        miixf__lrk, tfyau__ieqdi = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        miixf__lrk, tfyau__ieqdi, out_cols = _gen_df_rolling_out_data(rolling)
    ehl__mftt = bpnf__vubd or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    ntrc__pdine = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    ntrc__pdine += '  df = rolling.obj\n'
    ntrc__pdine += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if bpnf__vubd else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    ttzj__ipave = 'None'
    if bpnf__vubd:
        ttzj__ipave = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif ehl__mftt:
        oism__fgl = (set(out_cols) - set([rolling.on])).pop()
        ttzj__ipave = f"'{oism__fgl}'" if isinstance(oism__fgl, str) else str(
            oism__fgl)
    ntrc__pdine += f'  name = {ttzj__ipave}\n'
    ntrc__pdine += '  window = rolling.window\n'
    ntrc__pdine += '  center = rolling.center\n'
    ntrc__pdine += '  minp = rolling.min_periods\n'
    ntrc__pdine += f'  on_arr = {tfyau__ieqdi}\n'
    if fname == 'apply':
        ntrc__pdine += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        ntrc__pdine += f"  func = '{fname}'\n"
        ntrc__pdine += f'  index_arr = None\n'
        ntrc__pdine += f'  raw = False\n'
    if ehl__mftt:
        ntrc__pdine += (
            f'  return bodo.hiframes.pd_series_ext.init_series({miixf__lrk}, index, name)'
            )
        qki__qlpg = {}
        hlw__vec = {'bodo': bodo}
        exec(ntrc__pdine, hlw__vec, qki__qlpg)
        impl = qki__qlpg['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(ntrc__pdine, out_cols,
        miixf__lrk)


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
        nne__wpu = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(nne__wpu)


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
    ibzee__dijab = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(ibzee__dijab) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    fvb__khgip = not isinstance(window_type, types.Integer)
    tfyau__ieqdi = 'None'
    if fvb__khgip:
        tfyau__ieqdi = 'bodo.utils.conversion.index_to_array(index)'
    itvf__mliu = 'on_arr, ' if fvb__khgip else ''
    miixf__lrk = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {itvf__mliu}window, minp, center)'
            , tfyau__ieqdi)
    for oism__fgl in out_cols:
        if oism__fgl in df_cols and oism__fgl in other_cols:
            gsnoy__sps = df_cols.index(oism__fgl)
            nans__wyo = other_cols.index(oism__fgl)
            zvm__pqmqq = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {gsnoy__sps}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {nans__wyo}), {itvf__mliu}window, minp, center)'
                )
        else:
            zvm__pqmqq = 'np.full(len(df), np.nan)'
        miixf__lrk.append(zvm__pqmqq)
    return ', '.join(miixf__lrk), tfyau__ieqdi


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    ezdd__nimyr = {'pairwise': pairwise, 'ddof': ddof}
    mjds__wwlyj = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        ezdd__nimyr, mjds__wwlyj, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    ezdd__nimyr = {'ddof': ddof, 'pairwise': pairwise}
    mjds__wwlyj = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        ezdd__nimyr, mjds__wwlyj, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, xdnlt__fohm = args
        if isinstance(rolling, RollingType):
            ibzee__dijab = rolling.obj_type.selection if isinstance(rolling
                .obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(xdnlt__fohm, (tuple, list)):
                if len(set(xdnlt__fohm).difference(set(ibzee__dijab))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(xdnlt__fohm).difference(set(ibzee__dijab)))
                        )
                selection = list(xdnlt__fohm)
            else:
                if xdnlt__fohm not in ibzee__dijab:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(xdnlt__fohm))
                selection = [xdnlt__fohm]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            pkg__izuz = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(pkg__izuz, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        ibzee__dijab = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            ibzee__dijab = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            ibzee__dijab = rolling.obj_type.columns
        if attr in ibzee__dijab:
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
    pwho__jyog = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    hukcm__ohu = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in pwho__jyog):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        nxt__hujhz = hukcm__ohu[pwho__jyog.index(get_literal_value(on))]
        if not isinstance(nxt__hujhz, types.Array
            ) or nxt__hujhz.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(kwdej__jmo.dtype, (types.Boolean, types.Number)) for
        kwdej__jmo in hukcm__ohu):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
