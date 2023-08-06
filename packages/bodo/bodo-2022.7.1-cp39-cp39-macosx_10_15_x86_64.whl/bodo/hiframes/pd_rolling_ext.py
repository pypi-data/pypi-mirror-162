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
            oyl__iny = 'Series'
        else:
            oyl__iny = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{oyl__iny}.rolling()')
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
        udtl__uqgw = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, udtl__uqgw)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    nwa__wtr = dict(win_type=win_type, axis=axis, closed=closed)
    oqhh__hhve = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', nwa__wtr, oqhh__hhve,
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
    nwa__wtr = dict(win_type=win_type, axis=axis, closed=closed)
    oqhh__hhve = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', nwa__wtr, oqhh__hhve,
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
        mdya__wkxhw, dvmrf__nsk, vvuz__jmmjx, qjwd__bvnks, qdp__gdw = args
        anwv__cbq = signature.return_type
        oppwf__qlyu = cgutils.create_struct_proxy(anwv__cbq)(context, builder)
        oppwf__qlyu.obj = mdya__wkxhw
        oppwf__qlyu.window = dvmrf__nsk
        oppwf__qlyu.min_periods = vvuz__jmmjx
        oppwf__qlyu.center = qjwd__bvnks
        context.nrt.incref(builder, signature.args[0], mdya__wkxhw)
        context.nrt.incref(builder, signature.args[1], dvmrf__nsk)
        context.nrt.incref(builder, signature.args[2], vvuz__jmmjx)
        context.nrt.incref(builder, signature.args[3], qjwd__bvnks)
        return oppwf__qlyu._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    anwv__cbq = RollingType(obj_type, window_type, on, selection, False)
    return anwv__cbq(obj_type, window_type, min_periods_type, center_type,
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
    xkacz__zjob = not isinstance(rolling.window_type, types.Integer)
    vtlho__snndb = 'variable' if xkacz__zjob else 'fixed'
    xitm__yjwz = 'None'
    if xkacz__zjob:
        xitm__yjwz = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    ksdm__ckp = []
    tqvr__lvndn = 'on_arr, ' if xkacz__zjob else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{vtlho__snndb}(bodo.hiframes.pd_series_ext.get_series_data(df), {tqvr__lvndn}index_arr, window, minp, center, func, raw)'
            , xitm__yjwz, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    utxk__xfufs = rolling.obj_type.data
    out_cols = []
    for xpu__woa in rolling.selection:
        uka__mkr = rolling.obj_type.columns.index(xpu__woa)
        if xpu__woa == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            cat__xgpzo = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {uka__mkr})'
                )
            out_cols.append(xpu__woa)
        else:
            if not isinstance(utxk__xfufs[uka__mkr].dtype, (types.Boolean,
                types.Number)):
                continue
            cat__xgpzo = (
                f'bodo.hiframes.rolling.rolling_{vtlho__snndb}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {uka__mkr}), {tqvr__lvndn}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(xpu__woa)
        ksdm__ckp.append(cat__xgpzo)
    return ', '.join(ksdm__ckp), xitm__yjwz, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    nwa__wtr = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    oqhh__hhve = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', nwa__wtr, oqhh__hhve,
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
    nwa__wtr = dict(win_type=win_type, axis=axis, closed=closed, method=method)
    oqhh__hhve = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', nwa__wtr, oqhh__hhve,
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
        xuenw__hbwj = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        yvjxb__ntnsn = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{sss__pkn}'" if
                isinstance(sss__pkn, str) else f'{sss__pkn}' for sss__pkn in
                rolling.selection if sss__pkn != rolling.on))
        wnhm__olo = edwa__slpo = ''
        if fname == 'apply':
            wnhm__olo = 'func, raw, args, kwargs'
            edwa__slpo = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            wnhm__olo = edwa__slpo = 'other, pairwise'
        if fname == 'cov':
            wnhm__olo = edwa__slpo = 'other, pairwise, ddof'
        jlov__ggga = (
            f'lambda df, window, minp, center, {wnhm__olo}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {yvjxb__ntnsn}){selection}.{fname}({edwa__slpo})'
            )
        xuenw__hbwj += f"""  return rolling.obj.apply({jlov__ggga}, rolling.window, rolling.min_periods, rolling.center, {wnhm__olo})
"""
        rhr__tfq = {}
        exec(xuenw__hbwj, {'bodo': bodo}, rhr__tfq)
        impl = rhr__tfq['impl']
        return impl
    shw__asc = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if shw__asc else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if shw__asc else rolling.obj_type.columns
        other_cols = None if shw__asc else other.columns
        ksdm__ckp, xitm__yjwz = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        ksdm__ckp, xitm__yjwz, out_cols = _gen_df_rolling_out_data(rolling)
    uhq__kcq = shw__asc or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    ckwol__zmtup = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    ckwol__zmtup += '  df = rolling.obj\n'
    ckwol__zmtup += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if shw__asc else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    oyl__iny = 'None'
    if shw__asc:
        oyl__iny = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif uhq__kcq:
        xpu__woa = (set(out_cols) - set([rolling.on])).pop()
        oyl__iny = f"'{xpu__woa}'" if isinstance(xpu__woa, str) else str(
            xpu__woa)
    ckwol__zmtup += f'  name = {oyl__iny}\n'
    ckwol__zmtup += '  window = rolling.window\n'
    ckwol__zmtup += '  center = rolling.center\n'
    ckwol__zmtup += '  minp = rolling.min_periods\n'
    ckwol__zmtup += f'  on_arr = {xitm__yjwz}\n'
    if fname == 'apply':
        ckwol__zmtup += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        ckwol__zmtup += f"  func = '{fname}'\n"
        ckwol__zmtup += f'  index_arr = None\n'
        ckwol__zmtup += f'  raw = False\n'
    if uhq__kcq:
        ckwol__zmtup += (
            f'  return bodo.hiframes.pd_series_ext.init_series({ksdm__ckp}, index, name)'
            )
        rhr__tfq = {}
        jpdyk__yce = {'bodo': bodo}
        exec(ckwol__zmtup, jpdyk__yce, rhr__tfq)
        impl = rhr__tfq['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(ckwol__zmtup, out_cols,
        ksdm__ckp)


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
        atb__shbc = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(atb__shbc)


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
    mht__mouq = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(mht__mouq) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    xkacz__zjob = not isinstance(window_type, types.Integer)
    xitm__yjwz = 'None'
    if xkacz__zjob:
        xitm__yjwz = 'bodo.utils.conversion.index_to_array(index)'
    tqvr__lvndn = 'on_arr, ' if xkacz__zjob else ''
    ksdm__ckp = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {tqvr__lvndn}window, minp, center)'
            , xitm__yjwz)
    for xpu__woa in out_cols:
        if xpu__woa in df_cols and xpu__woa in other_cols:
            rhan__jqb = df_cols.index(xpu__woa)
            bfrwg__zuc = other_cols.index(xpu__woa)
            cat__xgpzo = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rhan__jqb}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {bfrwg__zuc}), {tqvr__lvndn}window, minp, center)'
                )
        else:
            cat__xgpzo = 'np.full(len(df), np.nan)'
        ksdm__ckp.append(cat__xgpzo)
    return ', '.join(ksdm__ckp), xitm__yjwz


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    urhy__qbj = {'pairwise': pairwise, 'ddof': ddof}
    belgm__vbtgw = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        urhy__qbj, belgm__vbtgw, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    urhy__qbj = {'ddof': ddof, 'pairwise': pairwise}
    belgm__vbtgw = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        urhy__qbj, belgm__vbtgw, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, nxj__dfcu = args
        if isinstance(rolling, RollingType):
            mht__mouq = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(nxj__dfcu, (tuple, list)):
                if len(set(nxj__dfcu).difference(set(mht__mouq))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(nxj__dfcu).difference(set(mht__mouq))))
                selection = list(nxj__dfcu)
            else:
                if nxj__dfcu not in mht__mouq:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(nxj__dfcu))
                selection = [nxj__dfcu]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            tinhh__cabb = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(tinhh__cabb, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        mht__mouq = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            mht__mouq = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            mht__mouq = rolling.obj_type.columns
        if attr in mht__mouq:
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
    nvq__eka = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    utxk__xfufs = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in nvq__eka):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        grbok__eynma = utxk__xfufs[nvq__eka.index(get_literal_value(on))]
        if not isinstance(grbok__eynma, types.Array
            ) or grbok__eynma.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(poc__jdog.dtype, (types.Boolean, types.Number)) for
        poc__jdog in utxk__xfufs):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
