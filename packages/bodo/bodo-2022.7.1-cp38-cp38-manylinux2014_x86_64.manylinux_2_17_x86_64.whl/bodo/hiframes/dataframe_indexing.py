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
            scf__vsci = idx
            tuzr__zlsyo = df.data
            jsxvl__oqsa = df.columns
            rlgk__dux = self.replace_range_with_numeric_idx_if_needed(df,
                scf__vsci)
            ttf__wfti = DataFrameType(tuzr__zlsyo, rlgk__dux, jsxvl__oqsa,
                is_table_format=df.is_table_format)
            return ttf__wfti(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            itdq__umea = idx.types[0]
            piaw__muhjq = idx.types[1]
            if isinstance(itdq__umea, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(piaw__muhjq):
                    srgr__ske = get_overload_const_str(piaw__muhjq)
                    if srgr__ske not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, srgr__ske))
                    lkt__ircar = df.columns.index(srgr__ske)
                    return df.data[lkt__ircar].dtype(*args)
                if isinstance(piaw__muhjq, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(itdq__umea
                ) and itdq__umea.dtype == types.bool_ or isinstance(itdq__umea,
                types.SliceType):
                rlgk__dux = self.replace_range_with_numeric_idx_if_needed(df,
                    itdq__umea)
                if is_overload_constant_str(piaw__muhjq):
                    svhw__zbjx = get_overload_const_str(piaw__muhjq)
                    if svhw__zbjx not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {svhw__zbjx}'
                            )
                    lkt__ircar = df.columns.index(svhw__zbjx)
                    yiai__ssdt = df.data[lkt__ircar]
                    yfatf__dtukk = yiai__ssdt.dtype
                    zfgs__drp = types.literal(df.columns[lkt__ircar])
                    ttf__wfti = bodo.SeriesType(yfatf__dtukk, yiai__ssdt,
                        rlgk__dux, zfgs__drp)
                    return ttf__wfti(*args)
                if isinstance(piaw__muhjq, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(piaw__muhjq):
                    lowyy__hhbia = get_overload_const_list(piaw__muhjq)
                    rqh__jhr = types.unliteral(piaw__muhjq)
                    if rqh__jhr.dtype == types.bool_:
                        if len(df.columns) != len(lowyy__hhbia):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {lowyy__hhbia} has {len(lowyy__hhbia)} values'
                                )
                        soh__oytzy = []
                        iohwz__sngz = []
                        for hjef__nbp in range(len(lowyy__hhbia)):
                            if lowyy__hhbia[hjef__nbp]:
                                soh__oytzy.append(df.columns[hjef__nbp])
                                iohwz__sngz.append(df.data[hjef__nbp])
                        msw__mbk = tuple()
                        ehjxh__zod = df.is_table_format and len(soh__oytzy
                            ) > 0 and len(soh__oytzy
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        ttf__wfti = DataFrameType(tuple(iohwz__sngz),
                            rlgk__dux, tuple(soh__oytzy), is_table_format=
                            ehjxh__zod)
                        return ttf__wfti(*args)
                    elif rqh__jhr.dtype == bodo.string_type:
                        msw__mbk, iohwz__sngz = (
                            get_df_getitem_kept_cols_and_data(df, lowyy__hhbia)
                            )
                        ehjxh__zod = df.is_table_format and len(lowyy__hhbia
                            ) > 0 and len(lowyy__hhbia
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        ttf__wfti = DataFrameType(iohwz__sngz, rlgk__dux,
                            msw__mbk, is_table_format=ehjxh__zod)
                        return ttf__wfti(*args)
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
                soh__oytzy = []
                iohwz__sngz = []
                for hjef__nbp, ssj__tjs in enumerate(df.columns):
                    if ssj__tjs[0] != ind_val:
                        continue
                    soh__oytzy.append(ssj__tjs[1] if len(ssj__tjs) == 2 else
                        ssj__tjs[1:])
                    iohwz__sngz.append(df.data[hjef__nbp])
                yiai__ssdt = tuple(iohwz__sngz)
                tfiz__dqzcc = df.index
                mumhs__vkwlz = tuple(soh__oytzy)
                ttf__wfti = DataFrameType(yiai__ssdt, tfiz__dqzcc, mumhs__vkwlz
                    )
                return ttf__wfti(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                lkt__ircar = df.columns.index(ind_val)
                yiai__ssdt = df.data[lkt__ircar]
                yfatf__dtukk = yiai__ssdt.dtype
                tfiz__dqzcc = df.index
                zfgs__drp = types.literal(df.columns[lkt__ircar])
                ttf__wfti = bodo.SeriesType(yfatf__dtukk, yiai__ssdt,
                    tfiz__dqzcc, zfgs__drp)
                return ttf__wfti(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            yiai__ssdt = df.data
            tfiz__dqzcc = self.replace_range_with_numeric_idx_if_needed(df, ind
                )
            mumhs__vkwlz = df.columns
            ttf__wfti = DataFrameType(yiai__ssdt, tfiz__dqzcc, mumhs__vkwlz,
                is_table_format=df.is_table_format)
            return ttf__wfti(*args)
        elif is_overload_constant_list(ind):
            nqpz__cdpx = get_overload_const_list(ind)
            mumhs__vkwlz, yiai__ssdt = get_df_getitem_kept_cols_and_data(df,
                nqpz__cdpx)
            tfiz__dqzcc = df.index
            ehjxh__zod = df.is_table_format and len(nqpz__cdpx) > 0 and len(
                nqpz__cdpx) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            ttf__wfti = DataFrameType(yiai__ssdt, tfiz__dqzcc, mumhs__vkwlz,
                is_table_format=ehjxh__zod)
            return ttf__wfti(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        rlgk__dux = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64,
            df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return rlgk__dux


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for pghnw__yadt in cols_to_keep_list:
        if pghnw__yadt not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(pghnw__yadt, df.columns))
    mumhs__vkwlz = tuple(cols_to_keep_list)
    yiai__ssdt = tuple(df.data[df.column_index[ufng__ggjhy]] for
        ufng__ggjhy in mumhs__vkwlz)
    return mumhs__vkwlz, yiai__ssdt


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
            soh__oytzy = []
            iohwz__sngz = []
            for hjef__nbp, ssj__tjs in enumerate(df.columns):
                if ssj__tjs[0] != ind_val:
                    continue
                soh__oytzy.append(ssj__tjs[1] if len(ssj__tjs) == 2 else
                    ssj__tjs[1:])
                iohwz__sngz.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(hjef__nbp))
            wpg__hxoxg = 'def impl(df, ind):\n'
            srzw__icwiu = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(wpg__hxoxg,
                soh__oytzy, ', '.join(iohwz__sngz), srzw__icwiu)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        nqpz__cdpx = get_overload_const_list(ind)
        for pghnw__yadt in nqpz__cdpx:
            if pghnw__yadt not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(pghnw__yadt, df.columns))
        xpc__unuuc = None
        if df.is_table_format and len(nqpz__cdpx) > 0 and len(nqpz__cdpx
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            fcg__ytxr = [df.column_index[pghnw__yadt] for pghnw__yadt in
                nqpz__cdpx]
            xpc__unuuc = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (fcg__ytxr))}
            iohwz__sngz = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            iohwz__sngz = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pghnw__yadt]}).copy()'
                 for pghnw__yadt in nqpz__cdpx)
        wpg__hxoxg = 'def impl(df, ind):\n'
        srzw__icwiu = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(wpg__hxoxg,
            nqpz__cdpx, iohwz__sngz, srzw__icwiu, extra_globals=xpc__unuuc)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        wpg__hxoxg = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            wpg__hxoxg += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        srzw__icwiu = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            iohwz__sngz = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            iohwz__sngz = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pghnw__yadt]})[ind]'
                 for pghnw__yadt in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(wpg__hxoxg, df.
            columns, iohwz__sngz, srzw__icwiu)
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
        ufng__ggjhy = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(ufng__ggjhy)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pix__grji = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, pix__grji)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        idkv__evp, = args
        fqbw__eklh = signature.return_type
        qqrn__xjrb = cgutils.create_struct_proxy(fqbw__eklh)(context, builder)
        qqrn__xjrb.obj = idkv__evp
        context.nrt.incref(builder, signature.args[0], idkv__evp)
        return qqrn__xjrb._getvalue()
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
        wrpe__albm = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            kvc__kyisx = get_overload_const_int(idx.types[1])
            if kvc__kyisx < 0 or kvc__kyisx >= wrpe__albm:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            fqfmc__fjra = [kvc__kyisx]
        else:
            is_out_series = False
            fqfmc__fjra = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= wrpe__albm for
                ind in fqfmc__fjra):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[fqfmc__fjra])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                kvc__kyisx = fqfmc__fjra[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, kvc__kyisx)
                        [idx[0]])
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
    wpg__hxoxg = 'def impl(I, idx):\n'
    wpg__hxoxg += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        wpg__hxoxg += f'  idx_t = {idx}\n'
    else:
        wpg__hxoxg += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    srzw__icwiu = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    xpc__unuuc = None
    if df.is_table_format and not is_out_series:
        fcg__ytxr = [df.column_index[pghnw__yadt] for pghnw__yadt in col_names]
        xpc__unuuc = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            fcg__ytxr))}
        iohwz__sngz = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        iohwz__sngz = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pghnw__yadt]})[idx_t]'
             for pghnw__yadt in col_names)
    if is_out_series:
        mxvvr__suaoi = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        wpg__hxoxg += f"""  return bodo.hiframes.pd_series_ext.init_series({iohwz__sngz}, {srzw__icwiu}, {mxvvr__suaoi})
"""
        zch__yahyl = {}
        exec(wpg__hxoxg, {'bodo': bodo}, zch__yahyl)
        return zch__yahyl['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(wpg__hxoxg, col_names,
        iohwz__sngz, srzw__icwiu, extra_globals=xpc__unuuc)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    wpg__hxoxg = 'def impl(I, idx):\n'
    wpg__hxoxg += '  df = I._obj\n'
    xvaz__ixfng = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pghnw__yadt]})[{idx}]'
         for pghnw__yadt in col_names)
    wpg__hxoxg += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    wpg__hxoxg += f"""  return bodo.hiframes.pd_series_ext.init_series(({xvaz__ixfng},), row_idx, None)
"""
    zch__yahyl = {}
    exec(wpg__hxoxg, {'bodo': bodo}, zch__yahyl)
    impl = zch__yahyl['impl']
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
        ufng__ggjhy = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(ufng__ggjhy)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pix__grji = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, pix__grji)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        idkv__evp, = args
        fmu__rqs = signature.return_type
        uwt__bjmbe = cgutils.create_struct_proxy(fmu__rqs)(context, builder)
        uwt__bjmbe.obj = idkv__evp
        context.nrt.incref(builder, signature.args[0], idkv__evp)
        return uwt__bjmbe._getvalue()
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
        wpg__hxoxg = 'def impl(I, idx):\n'
        wpg__hxoxg += '  df = I._obj\n'
        wpg__hxoxg += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        srzw__icwiu = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            iohwz__sngz = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            iohwz__sngz = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[pghnw__yadt]})[idx_t]'
                 for pghnw__yadt in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(wpg__hxoxg, df.
            columns, iohwz__sngz, srzw__icwiu)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        gye__qns = idx.types[1]
        if is_overload_constant_str(gye__qns):
            zbpqh__vkcsn = get_overload_const_str(gye__qns)
            kvc__kyisx = df.columns.index(zbpqh__vkcsn)

            def impl_col_name(I, idx):
                df = I._obj
                srzw__icwiu = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                oemw__xgtzd = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_data(df, kvc__kyisx))
                return bodo.hiframes.pd_series_ext.init_series(oemw__xgtzd,
                    srzw__icwiu, zbpqh__vkcsn).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(gye__qns):
            col_idx_list = get_overload_const_list(gye__qns)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(pghnw__yadt in df.column_index for
                pghnw__yadt in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    fqfmc__fjra = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for hjef__nbp, lsnvu__quy in enumerate(col_idx_list):
            if lsnvu__quy:
                fqfmc__fjra.append(hjef__nbp)
                col_names.append(df.columns[hjef__nbp])
    else:
        col_names = col_idx_list
        fqfmc__fjra = [df.column_index[pghnw__yadt] for pghnw__yadt in
            col_idx_list]
    xpc__unuuc = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        xpc__unuuc = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            fqfmc__fjra))}
        iohwz__sngz = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        iohwz__sngz = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in fqfmc__fjra)
    srzw__icwiu = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    wpg__hxoxg = 'def impl(I, idx):\n'
    wpg__hxoxg += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(wpg__hxoxg, col_names,
        iohwz__sngz, srzw__icwiu, extra_globals=xpc__unuuc)


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
        ufng__ggjhy = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(ufng__ggjhy)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        pix__grji = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, pix__grji)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        idkv__evp, = args
        bktz__guwul = signature.return_type
        lqvi__lwuo = cgutils.create_struct_proxy(bktz__guwul)(context, builder)
        lqvi__lwuo.obj = idkv__evp
        context.nrt.incref(builder, signature.args[0], idkv__evp)
        return lqvi__lwuo._getvalue()
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
        kvc__kyisx = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            oemw__xgtzd = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                kvc__kyisx)
            return bodo.utils.conversion.box_if_dt64(oemw__xgtzd[idx[0]])
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
        kvc__kyisx = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[kvc__kyisx]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            oemw__xgtzd = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                kvc__kyisx)
            oemw__xgtzd[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    lqvi__lwuo = cgutils.create_struct_proxy(fromty)(context, builder, val)
    aec__camo = context.cast(builder, lqvi__lwuo.obj, fromty.df_type, toty.
        df_type)
    lch__ktbk = cgutils.create_struct_proxy(toty)(context, builder)
    lch__ktbk.obj = aec__camo
    return lch__ktbk._getvalue()
