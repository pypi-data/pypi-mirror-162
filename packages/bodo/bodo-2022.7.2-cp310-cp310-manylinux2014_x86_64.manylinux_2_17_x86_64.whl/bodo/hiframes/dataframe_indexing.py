"""
Indexing support for pd.DataFrame type.
"""
import operator
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.utils.transform import gen_const_tup
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_list, get_overload_const_str, is_immutable_array, is_list_like_index_type, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, raise_bodo_error


@infer_global(operator.getitem)
class DataFrameGetItemTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        check_runtime_cols_unsupported(args[0], 'DataFrame getitem (df[])')
        if isinstance(args[0], DataFrameType):
            return self.typecheck_df_getitem(args)
        elif isinstance(args[0], DataFrameLocType):
            return self.typecheck_loc_getitem(args)
        else:
            return

    def typecheck_loc_getitem(self, args):
        I = args[0]
        idx = args[1]
        df = I.df_type
        if isinstance(df.columns[0], tuple):
            raise_bodo_error(
                'DataFrame.loc[] getitem (location-based indexing) with multi-indexed columns not supported yet'
                )
        if is_list_like_index_type(idx) and idx.dtype == types.bool_:
            vwknl__ngecz = idx
            mhpyk__zwi = df.data
            kub__ygdgm = df.columns
            gvgss__lpyp = self.replace_range_with_numeric_idx_if_needed(df,
                vwknl__ngecz)
            nutnl__vdxrb = DataFrameType(mhpyk__zwi, gvgss__lpyp,
                kub__ygdgm, is_table_format=df.is_table_format)
            return nutnl__vdxrb(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            rpcak__ulghm = idx.types[0]
            zfs__gpqf = idx.types[1]
            if isinstance(rpcak__ulghm, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(zfs__gpqf):
                    rmybh__jol = get_overload_const_str(zfs__gpqf)
                    if rmybh__jol not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, rmybh__jol))
                    epvr__adjg = df.columns.index(rmybh__jol)
                    return df.data[epvr__adjg].dtype(*args)
                if isinstance(zfs__gpqf, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(rpcak__ulghm
                ) and rpcak__ulghm.dtype == types.bool_ or isinstance(
                rpcak__ulghm, types.SliceType):
                gvgss__lpyp = self.replace_range_with_numeric_idx_if_needed(df,
                    rpcak__ulghm)
                if is_overload_constant_str(zfs__gpqf):
                    ygydr__didy = get_overload_const_str(zfs__gpqf)
                    if ygydr__didy not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {ygydr__didy}'
                            )
                    epvr__adjg = df.columns.index(ygydr__didy)
                    rzuyi__kcds = df.data[epvr__adjg]
                    hydg__kfov = rzuyi__kcds.dtype
                    xzh__dzav = types.literal(df.columns[epvr__adjg])
                    nutnl__vdxrb = bodo.SeriesType(hydg__kfov, rzuyi__kcds,
                        gvgss__lpyp, xzh__dzav)
                    return nutnl__vdxrb(*args)
                if isinstance(zfs__gpqf, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(zfs__gpqf):
                    qkdt__vmvk = get_overload_const_list(zfs__gpqf)
                    izr__yuat = types.unliteral(zfs__gpqf)
                    if izr__yuat.dtype == types.bool_:
                        if len(df.columns) != len(qkdt__vmvk):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {qkdt__vmvk} has {len(qkdt__vmvk)} values'
                                )
                        tlo__yro = []
                        jgpz__uxmg = []
                        for pgo__cuq in range(len(qkdt__vmvk)):
                            if qkdt__vmvk[pgo__cuq]:
                                tlo__yro.append(df.columns[pgo__cuq])
                                jgpz__uxmg.append(df.data[pgo__cuq])
                        acre__neo = tuple()
                        rzts__jxpu = df.is_table_format and len(tlo__yro
                            ) > 0 and len(tlo__yro
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        nutnl__vdxrb = DataFrameType(tuple(jgpz__uxmg),
                            gvgss__lpyp, tuple(tlo__yro), is_table_format=
                            rzts__jxpu)
                        return nutnl__vdxrb(*args)
                    elif izr__yuat.dtype == bodo.string_type:
                        acre__neo, jgpz__uxmg = (
                            get_df_getitem_kept_cols_and_data(df, qkdt__vmvk))
                        rzts__jxpu = df.is_table_format and len(qkdt__vmvk
                            ) > 0 and len(qkdt__vmvk
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        nutnl__vdxrb = DataFrameType(jgpz__uxmg,
                            gvgss__lpyp, acre__neo, is_table_format=rzts__jxpu)
                        return nutnl__vdxrb(*args)
        raise_bodo_error(
            f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet. If you are trying to select a subset of the columns by passing a list of column names, that list must be a compile time constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def typecheck_df_getitem(self, args):
        df = args[0]
        ind = args[1]
        if is_overload_constant_str(ind) or is_overload_constant_int(ind):
            ind_val = get_overload_const_str(ind) if is_overload_constant_str(
                ind) else get_overload_const_int(ind)
            if isinstance(df.columns[0], tuple):
                tlo__yro = []
                jgpz__uxmg = []
                for pgo__cuq, qav__wrghl in enumerate(df.columns):
                    if qav__wrghl[0] != ind_val:
                        continue
                    tlo__yro.append(qav__wrghl[1] if len(qav__wrghl) == 2 else
                        qav__wrghl[1:])
                    jgpz__uxmg.append(df.data[pgo__cuq])
                rzuyi__kcds = tuple(jgpz__uxmg)
                vql__becmp = df.index
                gin__cbdwa = tuple(tlo__yro)
                nutnl__vdxrb = DataFrameType(rzuyi__kcds, vql__becmp,
                    gin__cbdwa)
                return nutnl__vdxrb(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                epvr__adjg = df.columns.index(ind_val)
                rzuyi__kcds = df.data[epvr__adjg]
                hydg__kfov = rzuyi__kcds.dtype
                vql__becmp = df.index
                xzh__dzav = types.literal(df.columns[epvr__adjg])
                nutnl__vdxrb = bodo.SeriesType(hydg__kfov, rzuyi__kcds,
                    vql__becmp, xzh__dzav)
                return nutnl__vdxrb(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            rzuyi__kcds = df.data
            vql__becmp = self.replace_range_with_numeric_idx_if_needed(df, ind)
            gin__cbdwa = df.columns
            nutnl__vdxrb = DataFrameType(rzuyi__kcds, vql__becmp,
                gin__cbdwa, is_table_format=df.is_table_format)
            return nutnl__vdxrb(*args)
        elif is_overload_constant_list(ind):
            uqcz__wyjk = get_overload_const_list(ind)
            gin__cbdwa, rzuyi__kcds = get_df_getitem_kept_cols_and_data(df,
                uqcz__wyjk)
            vql__becmp = df.index
            rzts__jxpu = df.is_table_format and len(uqcz__wyjk) > 0 and len(
                uqcz__wyjk) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            nutnl__vdxrb = DataFrameType(rzuyi__kcds, vql__becmp,
                gin__cbdwa, is_table_format=rzts__jxpu)
            return nutnl__vdxrb(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        gvgss__lpyp = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return gvgss__lpyp


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for jyw__bcvtd in cols_to_keep_list:
        if jyw__bcvtd not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(jyw__bcvtd, df.columns))
    gin__cbdwa = tuple(cols_to_keep_list)
    rzuyi__kcds = tuple(df.data[df.column_index[wqcna__fuso]] for
        wqcna__fuso in gin__cbdwa)
    return gin__cbdwa, rzuyi__kcds


@lower_builtin(operator.getitem, DataFrameType, types.Any)
def getitem_df_lower(context, builder, sig, args):
    impl = df_getitem_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_getitem_overload(df, ind):
    if not isinstance(df, DataFrameType):
        return
    if is_overload_constant_str(ind) or is_overload_constant_int(ind):
        ind_val = get_overload_const_str(ind) if is_overload_constant_str(ind
            ) else get_overload_const_int(ind)
        if isinstance(df.columns[0], tuple):
            tlo__yro = []
            jgpz__uxmg = []
            for pgo__cuq, qav__wrghl in enumerate(df.columns):
                if qav__wrghl[0] != ind_val:
                    continue
                tlo__yro.append(qav__wrghl[1] if len(qav__wrghl) == 2 else
                    qav__wrghl[1:])
                jgpz__uxmg.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(pgo__cuq))
            lcp__cwckf = 'def impl(df, ind):\n'
            kyf__brpfb = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(lcp__cwckf,
                tlo__yro, ', '.join(jgpz__uxmg), kyf__brpfb)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        uqcz__wyjk = get_overload_const_list(ind)
        for jyw__bcvtd in uqcz__wyjk:
            if jyw__bcvtd not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(jyw__bcvtd, df.columns))
        pmhhi__xaw = None
        if df.is_table_format and len(uqcz__wyjk) > 0 and len(uqcz__wyjk
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            zjqz__ieh = [df.column_index[jyw__bcvtd] for jyw__bcvtd in
                uqcz__wyjk]
            pmhhi__xaw = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (zjqz__ieh))}
            jgpz__uxmg = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            jgpz__uxmg = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[jyw__bcvtd]}).copy()'
                 for jyw__bcvtd in uqcz__wyjk)
        lcp__cwckf = 'def impl(df, ind):\n'
        kyf__brpfb = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(lcp__cwckf,
            uqcz__wyjk, jgpz__uxmg, kyf__brpfb, extra_globals=pmhhi__xaw)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        lcp__cwckf = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            lcp__cwckf += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        kyf__brpfb = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            jgpz__uxmg = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            jgpz__uxmg = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[jyw__bcvtd]})[ind]'
                 for jyw__bcvtd in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(lcp__cwckf, df.
            columns, jgpz__uxmg, kyf__brpfb)
    raise_bodo_error('df[] getitem using {} not supported'.format(ind))


@overload(operator.setitem, no_unliteral=True)
def df_setitem_overload(df, idx, val):
    check_runtime_cols_unsupported(df, 'DataFrame setitem (df[])')
    if not isinstance(df, DataFrameType):
        return
    raise_bodo_error('DataFrame setitem: transform necessary')


class DataFrameILocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        wqcna__fuso = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(wqcna__fuso)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xeub__rhlws = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, xeub__rhlws)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        zfb__ejh, = args
        ujf__lphab = signature.return_type
        disvc__hesze = cgutils.create_struct_proxy(ujf__lphab)(context, builder
            )
        disvc__hesze.obj = zfb__ejh
        context.nrt.incref(builder, signature.args[0], zfb__ejh)
        return disvc__hesze._getvalue()
    return DataFrameILocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iloc')
def overload_dataframe_iloc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iloc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iloc(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iloc_getitem(I, idx):
    if not isinstance(I, DataFrameILocType):
        return
    df = I.df_type
    if isinstance(idx, types.Integer):
        return _gen_iloc_getitem_row_impl(df, df.columns, 'idx')
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and not isinstance(
        idx[1], types.SliceType):
        if not (is_overload_constant_list(idx.types[1]) or
            is_overload_constant_int(idx.types[1])):
            raise_bodo_error(
                'idx2 in df.iloc[idx1, idx2] should be a constant integer or constant list of integers. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        cgowr__hbr = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            smg__yib = get_overload_const_int(idx.types[1])
            if smg__yib < 0 or smg__yib >= cgowr__hbr:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            vrv__ysqq = [smg__yib]
        else:
            is_out_series = False
            vrv__ysqq = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= cgowr__hbr for
                ind in vrv__ysqq):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[vrv__ysqq])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                smg__yib = vrv__ysqq[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, smg__yib)[
                        idx[0]])
                return impl
            return _gen_iloc_getitem_row_impl(df, col_names, 'idx[0]')
        if is_list_like_index_type(idx.types[0]) and isinstance(idx.types[0
            ].dtype, (types.Integer, types.Boolean)) or isinstance(idx.
            types[0], types.SliceType):
            return _gen_iloc_getitem_bool_slice_impl(df, col_names, idx.
                types[0], 'idx[0]', is_out_series)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, (types.
        Integer, types.Boolean)) or isinstance(idx, types.SliceType):
        return _gen_iloc_getitem_bool_slice_impl(df, df.columns, idx, 'idx',
            False)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):
        raise_bodo_error(
            'slice2 in df.iloc[slice1,slice2] should be constant. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )
    raise_bodo_error(f'df.iloc[] getitem using {idx} not supported')


def _gen_iloc_getitem_bool_slice_impl(df, col_names, idx_typ, idx,
    is_out_series):
    lcp__cwckf = 'def impl(I, idx):\n'
    lcp__cwckf += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        lcp__cwckf += f'  idx_t = {idx}\n'
    else:
        lcp__cwckf += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    kyf__brpfb = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    pmhhi__xaw = None
    if df.is_table_format and not is_out_series:
        zjqz__ieh = [df.column_index[jyw__bcvtd] for jyw__bcvtd in col_names]
        pmhhi__xaw = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            zjqz__ieh))}
        jgpz__uxmg = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        jgpz__uxmg = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[jyw__bcvtd]})[idx_t]'
             for jyw__bcvtd in col_names)
    if is_out_series:
        jestw__jypdq = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        lcp__cwckf += f"""  return bodo.hiframes.pd_series_ext.init_series({jgpz__uxmg}, {kyf__brpfb}, {jestw__jypdq})
"""
        rgb__tcz = {}
        exec(lcp__cwckf, {'bodo': bodo}, rgb__tcz)
        return rgb__tcz['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(lcp__cwckf, col_names,
        jgpz__uxmg, kyf__brpfb, extra_globals=pmhhi__xaw)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    lcp__cwckf = 'def impl(I, idx):\n'
    lcp__cwckf += '  df = I._obj\n'
    wvmui__ckrvr = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[jyw__bcvtd]})[{idx}]'
         for jyw__bcvtd in col_names)
    lcp__cwckf += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    lcp__cwckf += f"""  return bodo.hiframes.pd_series_ext.init_series(({wvmui__ckrvr},), row_idx, None)
"""
    rgb__tcz = {}
    exec(lcp__cwckf, {'bodo': bodo}, rgb__tcz)
    impl = rgb__tcz['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def df_iloc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameILocType):
        return
    raise_bodo_error(
        f'DataFrame.iloc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameLocType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        wqcna__fuso = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(wqcna__fuso)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xeub__rhlws = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, xeub__rhlws)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        zfb__ejh, = args
        zgcz__ithk = signature.return_type
        onybl__ipags = cgutils.create_struct_proxy(zgcz__ithk)(context, builder
            )
        onybl__ipags.obj = zfb__ejh
        context.nrt.incref(builder, signature.args[0], zfb__ejh)
        return onybl__ipags._getvalue()
    return DataFrameLocType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'loc')
def overload_dataframe_loc(df):
    check_runtime_cols_unsupported(df, 'DataFrame.loc')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_loc(df)


@lower_builtin(operator.getitem, DataFrameLocType, types.Any)
def loc_getitem_lower(context, builder, sig, args):
    impl = overload_loc_getitem(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def overload_loc_getitem(I, idx):
    if not isinstance(I, DataFrameLocType):
        return
    df = I.df_type
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        lcp__cwckf = 'def impl(I, idx):\n'
        lcp__cwckf += '  df = I._obj\n'
        lcp__cwckf += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        kyf__brpfb = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            jgpz__uxmg = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            jgpz__uxmg = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[jyw__bcvtd]})[idx_t]'
                 for jyw__bcvtd in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(lcp__cwckf, df.
            columns, jgpz__uxmg, kyf__brpfb)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        twa__gbuoq = idx.types[1]
        if is_overload_constant_str(twa__gbuoq):
            exehl__aunp = get_overload_const_str(twa__gbuoq)
            smg__yib = df.columns.index(exehl__aunp)

            def impl_col_name(I, idx):
                df = I._obj
                kyf__brpfb = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                gkejt__bcbbc = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_data(df, smg__yib))
                return bodo.hiframes.pd_series_ext.init_series(gkejt__bcbbc,
                    kyf__brpfb, exehl__aunp).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(twa__gbuoq):
            col_idx_list = get_overload_const_list(twa__gbuoq)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(jyw__bcvtd in df.column_index for
                jyw__bcvtd in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    vrv__ysqq = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for pgo__cuq, uqz__cax in enumerate(col_idx_list):
            if uqz__cax:
                vrv__ysqq.append(pgo__cuq)
                col_names.append(df.columns[pgo__cuq])
    else:
        col_names = col_idx_list
        vrv__ysqq = [df.column_index[jyw__bcvtd] for jyw__bcvtd in col_idx_list
            ]
    pmhhi__xaw = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        pmhhi__xaw = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            vrv__ysqq))}
        jgpz__uxmg = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        jgpz__uxmg = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in vrv__ysqq)
    kyf__brpfb = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    lcp__cwckf = 'def impl(I, idx):\n'
    lcp__cwckf += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(lcp__cwckf, col_names,
        jgpz__uxmg, kyf__brpfb, extra_globals=pmhhi__xaw)


@overload(operator.setitem, no_unliteral=True)
def df_loc_setitem_overload(df, idx, val):
    if not isinstance(df, DataFrameLocType):
        return
    raise_bodo_error(
        f'DataFrame.loc setitem unsupported for dataframe {df.df_type}, index {idx}, value {val}'
        )


class DataFrameIatType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        wqcna__fuso = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(wqcna__fuso)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xeub__rhlws = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, xeub__rhlws)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        zfb__ejh, = args
        nhigb__pzfw = signature.return_type
        myyl__fsyn = cgutils.create_struct_proxy(nhigb__pzfw)(context, builder)
        myyl__fsyn.obj = zfb__ejh
        context.nrt.incref(builder, signature.args[0], zfb__ejh)
        return myyl__fsyn._getvalue()
    return DataFrameIatType(obj)(obj), codegen


@overload_attribute(DataFrameType, 'iat')
def overload_dataframe_iat(df):
    check_runtime_cols_unsupported(df, 'DataFrame.iat')
    return lambda df: bodo.hiframes.dataframe_indexing.init_dataframe_iat(df)


@overload(operator.getitem, no_unliteral=True)
def overload_iat_getitem(I, idx):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat getitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        smg__yib = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            gkejt__bcbbc = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df
                , smg__yib)
            return bodo.utils.conversion.box_if_dt64(gkejt__bcbbc[idx[0]])
        return impl_col_ind
    raise BodoError('df.iat[] getitem using {} not supported'.format(idx))


@overload(operator.setitem, no_unliteral=True)
def overload_iat_setitem(I, idx, val):
    if not isinstance(I, DataFrameIatType):
        return
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        if not isinstance(idx.types[0], types.Integer):
            raise BodoError(
                'DataFrame.iat: iAt based indexing can only have integer indexers'
                )
        if not is_overload_constant_int(idx.types[1]):
            raise_bodo_error(
                'DataFrame.iat setitem: column index must be a constant integer. For more informaton, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        smg__yib = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[smg__yib]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            gkejt__bcbbc = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df
                , smg__yib)
            gkejt__bcbbc[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val
                )
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    myyl__fsyn = cgutils.create_struct_proxy(fromty)(context, builder, val)
    zltr__jla = context.cast(builder, myyl__fsyn.obj, fromty.df_type, toty.
        df_type)
    jgqi__fzvxm = cgutils.create_struct_proxy(toty)(context, builder)
    jgqi__fzvxm.obj = zltr__jla
    return jgqi__fzvxm._getvalue()
