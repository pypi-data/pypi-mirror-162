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
            emv__aal = idx
            xfo__vzdg = df.data
            aaarj__cxg = df.columns
            uayrk__kevtz = self.replace_range_with_numeric_idx_if_needed(df,
                emv__aal)
            icoi__utps = DataFrameType(xfo__vzdg, uayrk__kevtz, aaarj__cxg,
                is_table_format=df.is_table_format)
            return icoi__utps(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            lsn__jlx = idx.types[0]
            elaw__nxvv = idx.types[1]
            if isinstance(lsn__jlx, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(elaw__nxvv):
                    tyw__cfni = get_overload_const_str(elaw__nxvv)
                    if tyw__cfni not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, tyw__cfni))
                    msfto__axt = df.columns.index(tyw__cfni)
                    return df.data[msfto__axt].dtype(*args)
                if isinstance(elaw__nxvv, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(lsn__jlx
                ) and lsn__jlx.dtype == types.bool_ or isinstance(lsn__jlx,
                types.SliceType):
                uayrk__kevtz = self.replace_range_with_numeric_idx_if_needed(df
                    , lsn__jlx)
                if is_overload_constant_str(elaw__nxvv):
                    yhcat__joho = get_overload_const_str(elaw__nxvv)
                    if yhcat__joho not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {yhcat__joho}'
                            )
                    msfto__axt = df.columns.index(yhcat__joho)
                    qiwxv__vqnlt = df.data[msfto__axt]
                    pbc__mln = qiwxv__vqnlt.dtype
                    jekoi__zllaj = types.literal(df.columns[msfto__axt])
                    icoi__utps = bodo.SeriesType(pbc__mln, qiwxv__vqnlt,
                        uayrk__kevtz, jekoi__zllaj)
                    return icoi__utps(*args)
                if isinstance(elaw__nxvv, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(elaw__nxvv):
                    qjxg__ivlxa = get_overload_const_list(elaw__nxvv)
                    tap__cswn = types.unliteral(elaw__nxvv)
                    if tap__cswn.dtype == types.bool_:
                        if len(df.columns) != len(qjxg__ivlxa):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {qjxg__ivlxa} has {len(qjxg__ivlxa)} values'
                                )
                        ikbpt__urp = []
                        ztii__fhui = []
                        for hthxk__vrlt in range(len(qjxg__ivlxa)):
                            if qjxg__ivlxa[hthxk__vrlt]:
                                ikbpt__urp.append(df.columns[hthxk__vrlt])
                                ztii__fhui.append(df.data[hthxk__vrlt])
                        sdva__edir = tuple()
                        glxb__jqo = df.is_table_format and len(ikbpt__urp
                            ) > 0 and len(ikbpt__urp
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        icoi__utps = DataFrameType(tuple(ztii__fhui),
                            uayrk__kevtz, tuple(ikbpt__urp),
                            is_table_format=glxb__jqo)
                        return icoi__utps(*args)
                    elif tap__cswn.dtype == bodo.string_type:
                        sdva__edir, ztii__fhui = (
                            get_df_getitem_kept_cols_and_data(df, qjxg__ivlxa))
                        glxb__jqo = df.is_table_format and len(qjxg__ivlxa
                            ) > 0 and len(qjxg__ivlxa
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        icoi__utps = DataFrameType(ztii__fhui, uayrk__kevtz,
                            sdva__edir, is_table_format=glxb__jqo)
                        return icoi__utps(*args)
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
                ikbpt__urp = []
                ztii__fhui = []
                for hthxk__vrlt, wdjg__vdo in enumerate(df.columns):
                    if wdjg__vdo[0] != ind_val:
                        continue
                    ikbpt__urp.append(wdjg__vdo[1] if len(wdjg__vdo) == 2 else
                        wdjg__vdo[1:])
                    ztii__fhui.append(df.data[hthxk__vrlt])
                qiwxv__vqnlt = tuple(ztii__fhui)
                prpf__rvtp = df.index
                nuiy__sgrt = tuple(ikbpt__urp)
                icoi__utps = DataFrameType(qiwxv__vqnlt, prpf__rvtp, nuiy__sgrt
                    )
                return icoi__utps(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                msfto__axt = df.columns.index(ind_val)
                qiwxv__vqnlt = df.data[msfto__axt]
                pbc__mln = qiwxv__vqnlt.dtype
                prpf__rvtp = df.index
                jekoi__zllaj = types.literal(df.columns[msfto__axt])
                icoi__utps = bodo.SeriesType(pbc__mln, qiwxv__vqnlt,
                    prpf__rvtp, jekoi__zllaj)
                return icoi__utps(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            qiwxv__vqnlt = df.data
            prpf__rvtp = self.replace_range_with_numeric_idx_if_needed(df, ind)
            nuiy__sgrt = df.columns
            icoi__utps = DataFrameType(qiwxv__vqnlt, prpf__rvtp, nuiy__sgrt,
                is_table_format=df.is_table_format)
            return icoi__utps(*args)
        elif is_overload_constant_list(ind):
            egomn__aje = get_overload_const_list(ind)
            nuiy__sgrt, qiwxv__vqnlt = get_df_getitem_kept_cols_and_data(df,
                egomn__aje)
            prpf__rvtp = df.index
            glxb__jqo = df.is_table_format and len(egomn__aje) > 0 and len(
                egomn__aje) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            icoi__utps = DataFrameType(qiwxv__vqnlt, prpf__rvtp, nuiy__sgrt,
                is_table_format=glxb__jqo)
            return icoi__utps(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        uayrk__kevtz = bodo.hiframes.pd_index_ext.NumericIndexType(types.
            int64, df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return uayrk__kevtz


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for gzv__rvok in cols_to_keep_list:
        if gzv__rvok not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(gzv__rvok, df.columns))
    nuiy__sgrt = tuple(cols_to_keep_list)
    qiwxv__vqnlt = tuple(df.data[df.column_index[vhvw__pze]] for vhvw__pze in
        nuiy__sgrt)
    return nuiy__sgrt, qiwxv__vqnlt


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
            ikbpt__urp = []
            ztii__fhui = []
            for hthxk__vrlt, wdjg__vdo in enumerate(df.columns):
                if wdjg__vdo[0] != ind_val:
                    continue
                ikbpt__urp.append(wdjg__vdo[1] if len(wdjg__vdo) == 2 else
                    wdjg__vdo[1:])
                ztii__fhui.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(hthxk__vrlt))
            txpl__ghfb = 'def impl(df, ind):\n'
            psrl__uhvly = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(txpl__ghfb,
                ikbpt__urp, ', '.join(ztii__fhui), psrl__uhvly)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        egomn__aje = get_overload_const_list(ind)
        for gzv__rvok in egomn__aje:
            if gzv__rvok not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(gzv__rvok, df.columns))
        orptc__ule = None
        if df.is_table_format and len(egomn__aje) > 0 and len(egomn__aje
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            permv__pbmft = [df.column_index[gzv__rvok] for gzv__rvok in
                egomn__aje]
            orptc__ule = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (permv__pbmft))}
            ztii__fhui = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            ztii__fhui = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[gzv__rvok]}).copy()'
                 for gzv__rvok in egomn__aje)
        txpl__ghfb = 'def impl(df, ind):\n'
        psrl__uhvly = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(txpl__ghfb,
            egomn__aje, ztii__fhui, psrl__uhvly, extra_globals=orptc__ule)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        txpl__ghfb = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            txpl__ghfb += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        psrl__uhvly = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            ztii__fhui = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            ztii__fhui = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[gzv__rvok]})[ind]'
                 for gzv__rvok in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(txpl__ghfb, df.
            columns, ztii__fhui, psrl__uhvly)
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
        vhvw__pze = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(vhvw__pze)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qwisu__zrvrq = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, qwisu__zrvrq)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        jjtav__oaj, = args
        mitk__xcyii = signature.return_type
        okk__qighu = cgutils.create_struct_proxy(mitk__xcyii)(context, builder)
        okk__qighu.obj = jjtav__oaj
        context.nrt.incref(builder, signature.args[0], jjtav__oaj)
        return okk__qighu._getvalue()
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
        dej__vffz = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            fvx__kcq = get_overload_const_int(idx.types[1])
            if fvx__kcq < 0 or fvx__kcq >= dej__vffz:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            mbs__flgm = [fvx__kcq]
        else:
            is_out_series = False
            mbs__flgm = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= dej__vffz for
                ind in mbs__flgm):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[mbs__flgm])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                fvx__kcq = mbs__flgm[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, fvx__kcq)[
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
    txpl__ghfb = 'def impl(I, idx):\n'
    txpl__ghfb += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        txpl__ghfb += f'  idx_t = {idx}\n'
    else:
        txpl__ghfb += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    psrl__uhvly = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
    orptc__ule = None
    if df.is_table_format and not is_out_series:
        permv__pbmft = [df.column_index[gzv__rvok] for gzv__rvok in col_names]
        orptc__ule = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            permv__pbmft))}
        ztii__fhui = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        ztii__fhui = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[gzv__rvok]})[idx_t]'
             for gzv__rvok in col_names)
    if is_out_series:
        lomfz__uvri = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        txpl__ghfb += f"""  return bodo.hiframes.pd_series_ext.init_series({ztii__fhui}, {psrl__uhvly}, {lomfz__uvri})
"""
        soh__nan = {}
        exec(txpl__ghfb, {'bodo': bodo}, soh__nan)
        return soh__nan['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(txpl__ghfb, col_names,
        ztii__fhui, psrl__uhvly, extra_globals=orptc__ule)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    txpl__ghfb = 'def impl(I, idx):\n'
    txpl__ghfb += '  df = I._obj\n'
    ggjd__ihzhh = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[gzv__rvok]})[{idx}]'
         for gzv__rvok in col_names)
    txpl__ghfb += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    txpl__ghfb += f"""  return bodo.hiframes.pd_series_ext.init_series(({ggjd__ihzhh},), row_idx, None)
"""
    soh__nan = {}
    exec(txpl__ghfb, {'bodo': bodo}, soh__nan)
    impl = soh__nan['impl']
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
        vhvw__pze = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(vhvw__pze)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qwisu__zrvrq = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, qwisu__zrvrq)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        jjtav__oaj, = args
        ijbcf__rpd = signature.return_type
        vrvky__ymsz = cgutils.create_struct_proxy(ijbcf__rpd)(context, builder)
        vrvky__ymsz.obj = jjtav__oaj
        context.nrt.incref(builder, signature.args[0], jjtav__oaj)
        return vrvky__ymsz._getvalue()
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
        txpl__ghfb = 'def impl(I, idx):\n'
        txpl__ghfb += '  df = I._obj\n'
        txpl__ghfb += (
            '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n')
        psrl__uhvly = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            ztii__fhui = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            ztii__fhui = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[gzv__rvok]})[idx_t]'
                 for gzv__rvok in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(txpl__ghfb, df.
            columns, ztii__fhui, psrl__uhvly)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        qmvc__vop = idx.types[1]
        if is_overload_constant_str(qmvc__vop):
            mghx__ijuje = get_overload_const_str(qmvc__vop)
            fvx__kcq = df.columns.index(mghx__ijuje)

            def impl_col_name(I, idx):
                df = I._obj
                psrl__uhvly = (bodo.hiframes.pd_dataframe_ext.
                    get_dataframe_index(df))
                ajolt__ecz = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, fvx__kcq)
                return bodo.hiframes.pd_series_ext.init_series(ajolt__ecz,
                    psrl__uhvly, mghx__ijuje).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(qmvc__vop):
            col_idx_list = get_overload_const_list(qmvc__vop)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(gzv__rvok in df.column_index for
                gzv__rvok in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    mbs__flgm = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for hthxk__vrlt, wps__suev in enumerate(col_idx_list):
            if wps__suev:
                mbs__flgm.append(hthxk__vrlt)
                col_names.append(df.columns[hthxk__vrlt])
    else:
        col_names = col_idx_list
        mbs__flgm = [df.column_index[gzv__rvok] for gzv__rvok in col_idx_list]
    orptc__ule = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        orptc__ule = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            mbs__flgm))}
        ztii__fhui = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        ztii__fhui = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in mbs__flgm)
    psrl__uhvly = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    txpl__ghfb = 'def impl(I, idx):\n'
    txpl__ghfb += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(txpl__ghfb, col_names,
        ztii__fhui, psrl__uhvly, extra_globals=orptc__ule)


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
        vhvw__pze = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(vhvw__pze)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qwisu__zrvrq = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, qwisu__zrvrq)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        jjtav__oaj, = args
        bbd__yqg = signature.return_type
        sqx__njlft = cgutils.create_struct_proxy(bbd__yqg)(context, builder)
        sqx__njlft.obj = jjtav__oaj
        context.nrt.incref(builder, signature.args[0], jjtav__oaj)
        return sqx__njlft._getvalue()
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
        fvx__kcq = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            ajolt__ecz = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                fvx__kcq)
            return bodo.utils.conversion.box_if_dt64(ajolt__ecz[idx[0]])
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
        fvx__kcq = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[fvx__kcq]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            ajolt__ecz = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                fvx__kcq)
            ajolt__ecz[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    sqx__njlft = cgutils.create_struct_proxy(fromty)(context, builder, val)
    ddl__pxx = context.cast(builder, sqx__njlft.obj, fromty.df_type, toty.
        df_type)
    sggbp__ieyf = cgutils.create_struct_proxy(toty)(context, builder)
    sggbp__ieyf.obj = ddl__pxx
    return sggbp__ieyf._getvalue()
