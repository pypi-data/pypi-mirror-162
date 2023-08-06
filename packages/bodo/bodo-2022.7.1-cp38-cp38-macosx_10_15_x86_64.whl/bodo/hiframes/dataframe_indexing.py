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
            dwqfl__qgxiq = idx
            qxkuj__qpylo = df.data
            saan__isog = df.columns
            cbt__bhnv = self.replace_range_with_numeric_idx_if_needed(df,
                dwqfl__qgxiq)
            zyv__qkwav = DataFrameType(qxkuj__qpylo, cbt__bhnv, saan__isog,
                is_table_format=df.is_table_format)
            return zyv__qkwav(*args)
        if isinstance(idx, types.BaseTuple) and len(idx) == 2:
            qdqk__rte = idx.types[0]
            cekjv__bpmme = idx.types[1]
            if isinstance(qdqk__rte, types.Integer):
                if not isinstance(df.index, bodo.hiframes.pd_index_ext.
                    RangeIndexType):
                    raise_bodo_error(
                        'Dataframe.loc[int, col_ind] getitem only supported for dataframes with RangeIndexes'
                        )
                if is_overload_constant_str(cekjv__bpmme):
                    ivs__rhpd = get_overload_const_str(cekjv__bpmme)
                    if ivs__rhpd not in df.columns:
                        raise_bodo_error(
                            'dataframe {} does not include column {}'.
                            format(df, ivs__rhpd))
                    nfzn__kvv = df.columns.index(ivs__rhpd)
                    return df.data[nfzn__kvv].dtype(*args)
                if isinstance(cekjv__bpmme, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                else:
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
                        )
            if is_list_like_index_type(qdqk__rte
                ) and qdqk__rte.dtype == types.bool_ or isinstance(qdqk__rte,
                types.SliceType):
                cbt__bhnv = self.replace_range_with_numeric_idx_if_needed(df,
                    qdqk__rte)
                if is_overload_constant_str(cekjv__bpmme):
                    pns__bxttr = get_overload_const_str(cekjv__bpmme)
                    if pns__bxttr not in df.columns:
                        raise_bodo_error(
                            f'dataframe {df} does not include column {pns__bxttr}'
                            )
                    nfzn__kvv = df.columns.index(pns__bxttr)
                    ejc__wers = df.data[nfzn__kvv]
                    amc__phb = ejc__wers.dtype
                    txxu__jpzz = types.literal(df.columns[nfzn__kvv])
                    zyv__qkwav = bodo.SeriesType(amc__phb, ejc__wers,
                        cbt__bhnv, txxu__jpzz)
                    return zyv__qkwav(*args)
                if isinstance(cekjv__bpmme, types.UnicodeType):
                    raise_bodo_error(
                        f'DataFrame.loc[] getitem (location-based indexing) requires constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                        )
                elif is_overload_constant_list(cekjv__bpmme):
                    clb__yra = get_overload_const_list(cekjv__bpmme)
                    vbo__kaksu = types.unliteral(cekjv__bpmme)
                    if vbo__kaksu.dtype == types.bool_:
                        if len(df.columns) != len(clb__yra):
                            raise_bodo_error(
                                f'dataframe {df} has {len(df.columns)} columns, but boolean array used with DataFrame.loc[] {clb__yra} has {len(clb__yra)} values'
                                )
                        qzg__rchdm = []
                        evoe__obmn = []
                        for cjsp__ipmt in range(len(clb__yra)):
                            if clb__yra[cjsp__ipmt]:
                                qzg__rchdm.append(df.columns[cjsp__ipmt])
                                evoe__obmn.append(df.data[cjsp__ipmt])
                        nxfo__iom = tuple()
                        uxdzu__ygdms = df.is_table_format and len(qzg__rchdm
                            ) > 0 and len(qzg__rchdm
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        zyv__qkwav = DataFrameType(tuple(evoe__obmn),
                            cbt__bhnv, tuple(qzg__rchdm), is_table_format=
                            uxdzu__ygdms)
                        return zyv__qkwav(*args)
                    elif vbo__kaksu.dtype == bodo.string_type:
                        nxfo__iom, evoe__obmn = (
                            get_df_getitem_kept_cols_and_data(df, clb__yra))
                        uxdzu__ygdms = df.is_table_format and len(clb__yra
                            ) > 0 and len(clb__yra
                            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
                        zyv__qkwav = DataFrameType(evoe__obmn, cbt__bhnv,
                            nxfo__iom, is_table_format=uxdzu__ygdms)
                        return zyv__qkwav(*args)
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
                qzg__rchdm = []
                evoe__obmn = []
                for cjsp__ipmt, ewy__olw in enumerate(df.columns):
                    if ewy__olw[0] != ind_val:
                        continue
                    qzg__rchdm.append(ewy__olw[1] if len(ewy__olw) == 2 else
                        ewy__olw[1:])
                    evoe__obmn.append(df.data[cjsp__ipmt])
                ejc__wers = tuple(evoe__obmn)
                uxmc__qahss = df.index
                xqqwy__miuo = tuple(qzg__rchdm)
                zyv__qkwav = DataFrameType(ejc__wers, uxmc__qahss, xqqwy__miuo)
                return zyv__qkwav(*args)
            else:
                if ind_val not in df.columns:
                    raise_bodo_error('dataframe {} does not include column {}'
                        .format(df, ind_val))
                nfzn__kvv = df.columns.index(ind_val)
                ejc__wers = df.data[nfzn__kvv]
                amc__phb = ejc__wers.dtype
                uxmc__qahss = df.index
                txxu__jpzz = types.literal(df.columns[nfzn__kvv])
                zyv__qkwav = bodo.SeriesType(amc__phb, ejc__wers,
                    uxmc__qahss, txxu__jpzz)
                return zyv__qkwav(*args)
        if isinstance(ind, types.Integer) or isinstance(ind, types.UnicodeType
            ):
            raise_bodo_error(
                'df[] getitem selecting a subset of columns requires providing constant column names. For more information, see https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
                )
        if is_list_like_index_type(ind
            ) and ind.dtype == types.bool_ or isinstance(ind, types.SliceType):
            ejc__wers = df.data
            uxmc__qahss = self.replace_range_with_numeric_idx_if_needed(df, ind
                )
            xqqwy__miuo = df.columns
            zyv__qkwav = DataFrameType(ejc__wers, uxmc__qahss, xqqwy__miuo,
                is_table_format=df.is_table_format)
            return zyv__qkwav(*args)
        elif is_overload_constant_list(ind):
            ohf__eef = get_overload_const_list(ind)
            xqqwy__miuo, ejc__wers = get_df_getitem_kept_cols_and_data(df,
                ohf__eef)
            uxmc__qahss = df.index
            uxdzu__ygdms = df.is_table_format and len(ohf__eef) > 0 and len(
                ohf__eef) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD
            zyv__qkwav = DataFrameType(ejc__wers, uxmc__qahss, xqqwy__miuo,
                is_table_format=uxdzu__ygdms)
            return zyv__qkwav(*args)
        raise_bodo_error(
            f'df[] getitem using {ind} not supported. If you are trying to select a subset of the columns, you must provide the column names you are selecting as a constant. See https://docs.bodo.ai/latest/bodo_parallelism/typing_considerations/#require_constants.'
            )

    def replace_range_with_numeric_idx_if_needed(self, df, ind):
        cbt__bhnv = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64,
            df.index.name_typ) if not isinstance(ind, types.SliceType
            ) and isinstance(df.index, bodo.hiframes.pd_index_ext.
            RangeIndexType) else df.index
        return cbt__bhnv


DataFrameGetItemTemplate._no_unliteral = True


def get_df_getitem_kept_cols_and_data(df, cols_to_keep_list):
    for fqq__saci in cols_to_keep_list:
        if fqq__saci not in df.column_index:
            raise_bodo_error('Column {} not found in dataframe columns {}'.
                format(fqq__saci, df.columns))
    xqqwy__miuo = tuple(cols_to_keep_list)
    ejc__wers = tuple(df.data[df.column_index[gktcl__maz]] for gktcl__maz in
        xqqwy__miuo)
    return xqqwy__miuo, ejc__wers


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
            qzg__rchdm = []
            evoe__obmn = []
            for cjsp__ipmt, ewy__olw in enumerate(df.columns):
                if ewy__olw[0] != ind_val:
                    continue
                qzg__rchdm.append(ewy__olw[1] if len(ewy__olw) == 2 else
                    ewy__olw[1:])
                evoe__obmn.append(
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'
                    .format(cjsp__ipmt))
            ilkp__spj = 'def impl(df, ind):\n'
            lylb__hlw = (
                'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
            return bodo.hiframes.dataframe_impl._gen_init_df(ilkp__spj,
                qzg__rchdm, ', '.join(evoe__obmn), lylb__hlw)
        if ind_val not in df.columns:
            raise_bodo_error('dataframe {} does not include column {}'.
                format(df, ind_val))
        col_no = df.columns.index(ind_val)
        return lambda df, ind: bodo.hiframes.pd_series_ext.init_series(bodo
            .hiframes.pd_dataframe_ext.get_dataframe_data(df, col_no), bodo
            .hiframes.pd_dataframe_ext.get_dataframe_index(df), ind_val)
    if is_overload_constant_list(ind):
        ohf__eef = get_overload_const_list(ind)
        for fqq__saci in ohf__eef:
            if fqq__saci not in df.column_index:
                raise_bodo_error('Column {} not found in dataframe columns {}'
                    .format(fqq__saci, df.columns))
        zdbzl__qwf = None
        if df.is_table_format and len(ohf__eef) > 0 and len(ohf__eef
            ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
            ivw__muy = [df.column_index[fqq__saci] for fqq__saci in ohf__eef]
            zdbzl__qwf = {'col_nums_meta': bodo.utils.typing.MetaType(tuple
                (ivw__muy))}
            evoe__obmn = (
                f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, True)'
                )
        else:
            evoe__obmn = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[fqq__saci]}).copy()'
                 for fqq__saci in ohf__eef)
        ilkp__spj = 'def impl(df, ind):\n'
        lylb__hlw = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
        return bodo.hiframes.dataframe_impl._gen_init_df(ilkp__spj,
            ohf__eef, evoe__obmn, lylb__hlw, extra_globals=zdbzl__qwf)
    if is_list_like_index_type(ind) and ind.dtype == types.bool_ or isinstance(
        ind, types.SliceType):
        ilkp__spj = 'def impl(df, ind):\n'
        if not isinstance(ind, types.SliceType):
            ilkp__spj += (
                '  ind = bodo.utils.conversion.coerce_to_ndarray(ind)\n')
        lylb__hlw = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[ind]')
        if df.is_table_format:
            evoe__obmn = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[ind]')
        else:
            evoe__obmn = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[fqq__saci]})[ind]'
                 for fqq__saci in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(ilkp__spj, df.
            columns, evoe__obmn, lylb__hlw)
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
        gktcl__maz = 'DataFrameILocType({})'.format(df_type)
        super(DataFrameILocType, self).__init__(gktcl__maz)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameILocType)
class DataFrameILocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nhp__kliw = [('obj', fe_type.df_type)]
        super(DataFrameILocModel, self).__init__(dmm, fe_type, nhp__kliw)


make_attribute_wrapper(DataFrameILocType, 'obj', '_obj')


@intrinsic
def init_dataframe_iloc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        kkvtf__fwkp, = args
        sokh__rfzdk = signature.return_type
        zkp__nfrym = cgutils.create_struct_proxy(sokh__rfzdk)(context, builder)
        zkp__nfrym.obj = kkvtf__fwkp
        context.nrt.incref(builder, signature.args[0], kkvtf__fwkp)
        return zkp__nfrym._getvalue()
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
        pdl__xvby = len(df.data)
        if is_overload_constant_int(idx.types[1]):
            is_out_series = True
            lkw__aurm = get_overload_const_int(idx.types[1])
            if lkw__aurm < 0 or lkw__aurm >= pdl__xvby:
                raise BodoError(
                    'df.iloc: column integer must refer to a valid column number'
                    )
            ydhv__xwvd = [lkw__aurm]
        else:
            is_out_series = False
            ydhv__xwvd = get_overload_const_list(idx.types[1])
            if any(not isinstance(ind, int) or ind < 0 or ind >= pdl__xvby for
                ind in ydhv__xwvd):
                raise BodoError(
                    'df.iloc: column list must be integers referring to a valid column number'
                    )
        col_names = tuple(pd.Series(df.columns, dtype=object)[ydhv__xwvd])
        if isinstance(idx.types[0], types.Integer):
            if isinstance(idx.types[1], types.Integer):
                lkw__aurm = ydhv__xwvd[0]

                def impl(I, idx):
                    df = I._obj
                    return bodo.utils.conversion.box_if_dt64(bodo.hiframes.
                        pd_dataframe_ext.get_dataframe_data(df, lkw__aurm)[
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
    ilkp__spj = 'def impl(I, idx):\n'
    ilkp__spj += '  df = I._obj\n'
    if isinstance(idx_typ, types.SliceType):
        ilkp__spj += f'  idx_t = {idx}\n'
    else:
        ilkp__spj += (
            f'  idx_t = bodo.utils.conversion.coerce_to_ndarray({idx})\n')
    lylb__hlw = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]'
    zdbzl__qwf = None
    if df.is_table_format and not is_out_series:
        ivw__muy = [df.column_index[fqq__saci] for fqq__saci in col_names]
        zdbzl__qwf = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            ivw__muy))}
        evoe__obmn = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx_t]'
            )
    else:
        evoe__obmn = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[fqq__saci]})[idx_t]'
             for fqq__saci in col_names)
    if is_out_series:
        dwst__hpooe = f"'{col_names[0]}'" if isinstance(col_names[0], str
            ) else f'{col_names[0]}'
        ilkp__spj += f"""  return bodo.hiframes.pd_series_ext.init_series({evoe__obmn}, {lylb__hlw}, {dwst__hpooe})
"""
        aar__lwap = {}
        exec(ilkp__spj, {'bodo': bodo}, aar__lwap)
        return aar__lwap['impl']
    return bodo.hiframes.dataframe_impl._gen_init_df(ilkp__spj, col_names,
        evoe__obmn, lylb__hlw, extra_globals=zdbzl__qwf)


def _gen_iloc_getitem_row_impl(df, col_names, idx):
    ilkp__spj = 'def impl(I, idx):\n'
    ilkp__spj += '  df = I._obj\n'
    okqgs__lztlt = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[fqq__saci]})[{idx}]'
         for fqq__saci in col_names)
    ilkp__spj += f"""  row_idx = bodo.hiframes.pd_index_ext.init_heter_index({gen_const_tup(col_names)}, None)
"""
    ilkp__spj += f"""  return bodo.hiframes.pd_series_ext.init_series(({okqgs__lztlt},), row_idx, None)
"""
    aar__lwap = {}
    exec(ilkp__spj, {'bodo': bodo}, aar__lwap)
    impl = aar__lwap['impl']
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
        gktcl__maz = 'DataFrameLocType({})'.format(df_type)
        super(DataFrameLocType, self).__init__(gktcl__maz)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameLocType)
class DataFrameLocModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nhp__kliw = [('obj', fe_type.df_type)]
        super(DataFrameLocModel, self).__init__(dmm, fe_type, nhp__kliw)


make_attribute_wrapper(DataFrameLocType, 'obj', '_obj')


@intrinsic
def init_dataframe_loc(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        kkvtf__fwkp, = args
        wag__zkqc = signature.return_type
        xdydm__pxacc = cgutils.create_struct_proxy(wag__zkqc)(context, builder)
        xdydm__pxacc.obj = kkvtf__fwkp
        context.nrt.incref(builder, signature.args[0], kkvtf__fwkp)
        return xdydm__pxacc._getvalue()
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
        ilkp__spj = 'def impl(I, idx):\n'
        ilkp__spj += '  df = I._obj\n'
        ilkp__spj += '  idx_t = bodo.utils.conversion.coerce_to_ndarray(idx)\n'
        lylb__hlw = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx_t]')
        if df.is_table_format:
            evoe__obmn = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[idx_t]'
                )
        else:
            evoe__obmn = ', '.join(
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[fqq__saci]})[idx_t]'
                 for fqq__saci in df.columns)
        return bodo.hiframes.dataframe_impl._gen_init_df(ilkp__spj, df.
            columns, evoe__obmn, lylb__hlw)
    if isinstance(idx, types.BaseTuple) and len(idx) == 2:
        fbx__rkj = idx.types[1]
        if is_overload_constant_str(fbx__rkj):
            kumf__qeml = get_overload_const_str(fbx__rkj)
            lkw__aurm = df.columns.index(kumf__qeml)

            def impl_col_name(I, idx):
                df = I._obj
                lylb__hlw = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
                    df)
                jmud__eswl = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
                    df, lkw__aurm)
                return bodo.hiframes.pd_series_ext.init_series(jmud__eswl,
                    lylb__hlw, kumf__qeml).loc[idx[0]]
            return impl_col_name
        if is_overload_constant_list(fbx__rkj):
            col_idx_list = get_overload_const_list(fbx__rkj)
            if len(col_idx_list) > 0 and not isinstance(col_idx_list[0], (
                bool, np.bool_)) and not all(fqq__saci in df.column_index for
                fqq__saci in col_idx_list):
                raise_bodo_error(
                    f'DataFrame.loc[]: invalid column list {col_idx_list}; not all in dataframe columns {df.columns}'
                    )
            return gen_df_loc_col_select_impl(df, col_idx_list)
    raise_bodo_error(
        f'DataFrame.loc[] getitem (location-based indexing) using {idx} not supported yet.'
        )


def gen_df_loc_col_select_impl(df, col_idx_list):
    col_names = []
    ydhv__xwvd = []
    if len(col_idx_list) > 0 and isinstance(col_idx_list[0], (bool, np.bool_)):
        for cjsp__ipmt, amrmo__ouo in enumerate(col_idx_list):
            if amrmo__ouo:
                ydhv__xwvd.append(cjsp__ipmt)
                col_names.append(df.columns[cjsp__ipmt])
    else:
        col_names = col_idx_list
        ydhv__xwvd = [df.column_index[fqq__saci] for fqq__saci in col_idx_list]
    zdbzl__qwf = None
    if df.is_table_format and len(col_idx_list) > 0 and len(col_idx_list
        ) >= bodo.hiframes.boxing.TABLE_FORMAT_THRESHOLD:
        zdbzl__qwf = {'col_nums_meta': bodo.utils.typing.MetaType(tuple(
            ydhv__xwvd))}
        evoe__obmn = (
            f'bodo.hiframes.table.table_subset(bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), col_nums_meta, False)[idx[0]]'
            )
    else:
        evoe__obmn = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ind})[idx[0]]'
             for ind in ydhv__xwvd)
    lylb__hlw = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[idx[0]]')
    ilkp__spj = 'def impl(I, idx):\n'
    ilkp__spj += '  df = I._obj\n'
    return bodo.hiframes.dataframe_impl._gen_init_df(ilkp__spj, col_names,
        evoe__obmn, lylb__hlw, extra_globals=zdbzl__qwf)


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
        gktcl__maz = 'DataFrameIatType({})'.format(df_type)
        super(DataFrameIatType, self).__init__(gktcl__maz)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)
    ndim = 2


@register_model(DataFrameIatType)
class DataFrameIatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        nhp__kliw = [('obj', fe_type.df_type)]
        super(DataFrameIatModel, self).__init__(dmm, fe_type, nhp__kliw)


make_attribute_wrapper(DataFrameIatType, 'obj', '_obj')


@intrinsic
def init_dataframe_iat(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        kkvtf__fwkp, = args
        qfatl__yicu = signature.return_type
        gmhwk__jtfq = cgutils.create_struct_proxy(qfatl__yicu)(context, builder
            )
        gmhwk__jtfq.obj = kkvtf__fwkp
        context.nrt.incref(builder, signature.args[0], kkvtf__fwkp)
        return gmhwk__jtfq._getvalue()
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
        lkw__aurm = get_overload_const_int(idx.types[1])

        def impl_col_ind(I, idx):
            df = I._obj
            jmud__eswl = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                lkw__aurm)
            return bodo.utils.conversion.box_if_dt64(jmud__eswl[idx[0]])
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
        lkw__aurm = get_overload_const_int(idx.types[1])
        if is_immutable_array(I.df_type.data[lkw__aurm]):
            raise BodoError(
                f'DataFrame setitem not supported for column with immutable array type {I.df_type.data}'
                )

        def impl_col_ind(I, idx, val):
            df = I._obj
            jmud__eswl = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df,
                lkw__aurm)
            jmud__eswl[idx[0]] = bodo.utils.conversion.unbox_if_timestamp(val)
        return impl_col_ind
    raise BodoError('df.iat[] setitem using {} not supported'.format(idx))


@lower_cast(DataFrameIatType, DataFrameIatType)
@lower_cast(DataFrameILocType, DataFrameILocType)
@lower_cast(DataFrameLocType, DataFrameLocType)
def cast_series_iat(context, builder, fromty, toty, val):
    gmhwk__jtfq = cgutils.create_struct_proxy(fromty)(context, builder, val)
    wcvm__jfr = context.cast(builder, gmhwk__jtfq.obj, fromty.df_type, toty
        .df_type)
    lpdc__zdri = cgutils.create_struct_proxy(toty)(context, builder)
    lpdc__zdri.obj = wcvm__jfr
    return lpdc__zdri._getvalue()
