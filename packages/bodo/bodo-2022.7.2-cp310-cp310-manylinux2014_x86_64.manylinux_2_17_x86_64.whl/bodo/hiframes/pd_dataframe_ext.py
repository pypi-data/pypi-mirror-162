"""
Implement pd.DataFrame typing and data model handling.
"""
import json
import operator
from functools import cached_property
from urllib.parse import quote
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.cpython.listobj import ListInstance
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_index_ext import HeterogeneousIndexType, NumericIndexType, RangeIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.series_indexing import SeriesIlocType
from bodo.hiframes.table import Table, TableType, decode_if_dict_table, get_table_data, set_table_data_codegen
from bodo.io import json_cpp
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_table_to_cpp_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_from_sequence
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils import tracing
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.conversion import fix_arr_dtype, index_to_array
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, decode_if_dict_array, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_iterable_type, is_literal_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_str_arr_type, is_tuple_like_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
from bodo.utils.utils import is_null_pointer
_json_write = types.ExternalFunction('json_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.bool_,
    types.voidptr, types.voidptr))
ll.add_symbol('json_write', json_cpp.json_write)


class DataFrameType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, data=None, index=None, columns=None, dist=None,
        is_table_format=False):
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        if index is None:
            index = RangeIndexType(types.none)
        self.index = index
        self.columns = columns
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        self.is_table_format = is_table_format
        if columns is None:
            assert is_table_format, 'Determining columns at runtime is only supported for DataFrame with table format'
            self.table_type = TableType(tuple(data[:-1]), True)
        else:
            self.table_type = TableType(data) if is_table_format else None
        super(DataFrameType, self).__init__(name=
            f'dataframe({data}, {index}, {columns}, {dist}, {is_table_format}, {self.has_runtime_cols})'
            )

    def __str__(self):
        if not self.has_runtime_cols and len(self.columns) > 20:
            bew__uivfx = f'{len(self.data)} columns of types {set(self.data)}'
            yczl__ibm = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({bew__uivfx}, {self.index}, {yczl__ibm}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
                )
        return super().__str__()

    def copy(self, data=None, index=None, columns=None, dist=None,
        is_table_format=None):
        if data is None:
            data = self.data
        if columns is None:
            columns = self.columns
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if is_table_format is None:
            is_table_format = self.is_table_format
        return DataFrameType(data, index, columns, dist, is_table_format)

    @property
    def has_runtime_cols(self):
        return self.columns is None

    @cached_property
    def column_index(self):
        return {yzsr__duzs: i for i, yzsr__duzs in enumerate(self.columns)}

    @property
    def runtime_colname_typ(self):
        return self.data[-1] if self.has_runtime_cols else None

    @property
    def runtime_data_types(self):
        return self.data[:-1] if self.has_runtime_cols else self.data

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return (self.data, self.index, self.columns, self.dist, self.
            is_table_format)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if (isinstance(other, DataFrameType) and len(other.data) == len(
            self.data) and other.columns == self.columns and other.
            has_runtime_cols == self.has_runtime_cols):
            llt__eedj = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            data = tuple(usv__jytj.unify(typingctx, arh__xmzsd) if 
                usv__jytj != arh__xmzsd else usv__jytj for usv__jytj,
                arh__xmzsd in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if llt__eedj is not None and None not in data:
                return DataFrameType(data, llt__eedj, self.columns, dist,
                    self.is_table_format)
        if isinstance(other, DataFrameType) and len(self.data
            ) == 0 and not self.has_runtime_cols:
            return other

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, DataFrameType) and self.data == other.data and
            self.index == other.index and self.columns == other.columns and
            self.dist != other.dist and self.has_runtime_cols == other.
            has_runtime_cols):
            return Conversion.safe

    def is_precise(self):
        return all(usv__jytj.is_precise() for usv__jytj in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        yyj__jst = self.columns.index(col_name)
        evkw__nxglz = tuple(list(self.data[:yyj__jst]) + [new_type] + list(
            self.data[yyj__jst + 1:]))
        return DataFrameType(evkw__nxglz, self.index, self.columns, self.
            dist, self.is_table_format)


def check_runtime_cols_unsupported(df, func_name):
    if isinstance(df, DataFrameType) and df.has_runtime_cols:
        raise BodoError(
            f'{func_name} on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information.'
            )


class DataFramePayloadType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        super(DataFramePayloadType, self).__init__(name=
            f'DataFramePayloadType({df_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFramePayloadType)
class DataFramePayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        data_typ = types.Tuple(fe_type.df_type.data)
        if fe_type.df_type.is_table_format:
            data_typ = types.Tuple([fe_type.df_type.table_type])
        kzby__xbz = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            kzby__xbz.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, kzby__xbz)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        kzby__xbz = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, kzby__xbz)


make_attribute_wrapper(DataFrameType, 'meminfo', '_meminfo')


@infer_getattr
class DataFrameAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])

    @bound_function('df.head')
    def resolve_head(self, df, args, kws):
        func_name = 'DataFrame.head'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        kzhg__yle = 'n',
        gdr__sdd = {'n': 5}
        phylv__tej, tgbp__ztkqr = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, kzhg__yle, gdr__sdd)
        jhnqk__futvu = tgbp__ztkqr[0]
        if not is_overload_int(jhnqk__futvu):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        pmaay__pkpns = df.copy()
        return pmaay__pkpns(*tgbp__ztkqr).replace(pysig=phylv__tej)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        wtou__hzzk = (df,) + args
        kzhg__yle = 'df', 'method', 'min_periods'
        gdr__sdd = {'method': 'pearson', 'min_periods': 1}
        ubsuj__lqxw = 'method',
        phylv__tej, tgbp__ztkqr = bodo.utils.typing.fold_typing_args(func_name,
            wtou__hzzk, kws, kzhg__yle, gdr__sdd, ubsuj__lqxw)
        smp__mot = tgbp__ztkqr[2]
        if not is_overload_int(smp__mot):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        zqbr__slh = []
        itr__hwocn = []
        for yzsr__duzs, ifwo__exfls in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(ifwo__exfls.dtype):
                zqbr__slh.append(yzsr__duzs)
                itr__hwocn.append(types.Array(types.float64, 1, 'A'))
        if len(zqbr__slh) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        itr__hwocn = tuple(itr__hwocn)
        zqbr__slh = tuple(zqbr__slh)
        index_typ = bodo.utils.typing.type_col_to_index(zqbr__slh)
        pmaay__pkpns = DataFrameType(itr__hwocn, index_typ, zqbr__slh)
        return pmaay__pkpns(*tgbp__ztkqr).replace(pysig=phylv__tej)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        ibarp__unnpv = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        xbhdg__wep = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        xgjz__orpa = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        iwcig__nyn = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        nimni__pxww = dict(raw=xbhdg__wep, result_type=xgjz__orpa)
        xkatk__hiyn = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', nimni__pxww, xkatk__hiyn,
            package_name='pandas', module_name='DataFrame')
        syla__bqn = True
        if types.unliteral(ibarp__unnpv) == types.unicode_type:
            if not is_overload_constant_str(ibarp__unnpv):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            syla__bqn = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        dfbz__jljia = get_overload_const_int(axis)
        if syla__bqn and dfbz__jljia != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif dfbz__jljia not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        lpmc__qzf = []
        for arr_typ in df.data:
            blvex__txz = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            hmrxg__rxcl = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(blvex__txz), types.int64), {}
                ).return_type
            lpmc__qzf.append(hmrxg__rxcl)
        rmup__sts = types.none
        hniaf__zjxyl = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(yzsr__duzs) for yzsr__duzs in df.columns)),
            None)
        kioo__ruhbd = types.BaseTuple.from_types(lpmc__qzf)
        vrp__dyeix = types.Tuple([types.bool_] * len(kioo__ruhbd))
        bhf__edxag = bodo.NullableTupleType(kioo__ruhbd, vrp__dyeix)
        xzm__qoj = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if xzm__qoj == types.NPDatetime('ns'):
            xzm__qoj = bodo.pd_timestamp_type
        if xzm__qoj == types.NPTimedelta('ns'):
            xzm__qoj = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(kioo__ruhbd):
            kocma__ptys = HeterogeneousSeriesType(bhf__edxag, hniaf__zjxyl,
                xzm__qoj)
        else:
            kocma__ptys = SeriesType(kioo__ruhbd.dtype, bhf__edxag,
                hniaf__zjxyl, xzm__qoj)
        ary__yfbxx = kocma__ptys,
        if iwcig__nyn is not None:
            ary__yfbxx += tuple(iwcig__nyn.types)
        try:
            if not syla__bqn:
                oggtw__lbfnh = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(ibarp__unnpv), self.context,
                    'DataFrame.apply', axis if dfbz__jljia == 1 else None)
            else:
                oggtw__lbfnh = get_const_func_output_type(ibarp__unnpv,
                    ary__yfbxx, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as qdg__nhr:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', qdg__nhr))
        if syla__bqn:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(oggtw__lbfnh, (SeriesType, HeterogeneousSeriesType)
                ) and oggtw__lbfnh.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(oggtw__lbfnh, HeterogeneousSeriesType):
                xcr__ntui, yncc__uhv = oggtw__lbfnh.const_info
                if isinstance(oggtw__lbfnh.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    vsfsu__msh = oggtw__lbfnh.data.tuple_typ.types
                elif isinstance(oggtw__lbfnh.data, types.Tuple):
                    vsfsu__msh = oggtw__lbfnh.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                xjozd__xkplt = tuple(to_nullable_type(dtype_to_array_type(
                    zorp__vzovj)) for zorp__vzovj in vsfsu__msh)
                epj__ksx = DataFrameType(xjozd__xkplt, df.index, yncc__uhv)
            elif isinstance(oggtw__lbfnh, SeriesType):
                jof__lzo, yncc__uhv = oggtw__lbfnh.const_info
                xjozd__xkplt = tuple(to_nullable_type(dtype_to_array_type(
                    oggtw__lbfnh.dtype)) for xcr__ntui in range(jof__lzo))
                epj__ksx = DataFrameType(xjozd__xkplt, df.index, yncc__uhv)
            else:
                nbe__ngn = get_udf_out_arr_type(oggtw__lbfnh)
                epj__ksx = SeriesType(nbe__ngn.dtype, nbe__ngn, df.index, None)
        else:
            epj__ksx = oggtw__lbfnh
        pmocx__fha = ', '.join("{} = ''".format(usv__jytj) for usv__jytj in
            kws.keys())
        phi__ykp = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {pmocx__fha}):
"""
        phi__ykp += '    pass\n'
        allr__ezp = {}
        exec(phi__ykp, {}, allr__ezp)
        kwy__sgxo = allr__ezp['apply_stub']
        phylv__tej = numba.core.utils.pysignature(kwy__sgxo)
        vpxk__hjzt = (ibarp__unnpv, axis, xbhdg__wep, xgjz__orpa, iwcig__nyn
            ) + tuple(kws.values())
        return signature(epj__ksx, *vpxk__hjzt).replace(pysig=phylv__tej)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        kzhg__yle = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        gdr__sdd = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        ubsuj__lqxw = ('subplots', 'sharex', 'sharey', 'layout',
            'use_index', 'grid', 'style', 'logx', 'logy', 'loglog', 'xlim',
            'ylim', 'rot', 'colormap', 'table', 'yerr', 'xerr',
            'sort_columns', 'secondary_y', 'colorbar', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        phylv__tej, tgbp__ztkqr = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, kzhg__yle, gdr__sdd, ubsuj__lqxw)
        logpp__awmd = tgbp__ztkqr[2]
        if not is_overload_constant_str(logpp__awmd):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        nhk__fcyh = tgbp__ztkqr[0]
        if not is_overload_none(nhk__fcyh) and not (is_overload_int(
            nhk__fcyh) or is_overload_constant_str(nhk__fcyh)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(nhk__fcyh):
            cago__pcth = get_overload_const_str(nhk__fcyh)
            if cago__pcth not in df.columns:
                raise BodoError(f'{func_name}: {cago__pcth} column not found.')
        elif is_overload_int(nhk__fcyh):
            css__iel = get_overload_const_int(nhk__fcyh)
            if css__iel > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {css__iel} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            nhk__fcyh = df.columns[nhk__fcyh]
        jwd__bhjn = tgbp__ztkqr[1]
        if not is_overload_none(jwd__bhjn) and not (is_overload_int(
            jwd__bhjn) or is_overload_constant_str(jwd__bhjn)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(jwd__bhjn):
            bhzss__khlo = get_overload_const_str(jwd__bhjn)
            if bhzss__khlo not in df.columns:
                raise BodoError(f'{func_name}: {bhzss__khlo} column not found.'
                    )
        elif is_overload_int(jwd__bhjn):
            cyxr__fah = get_overload_const_int(jwd__bhjn)
            if cyxr__fah > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {cyxr__fah} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            jwd__bhjn = df.columns[jwd__bhjn]
        rqmxx__yxhiy = tgbp__ztkqr[3]
        if not is_overload_none(rqmxx__yxhiy) and not is_tuple_like_type(
            rqmxx__yxhiy):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        ocq__zznjl = tgbp__ztkqr[10]
        if not is_overload_none(ocq__zznjl) and not is_overload_constant_str(
            ocq__zznjl):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        kxkb__bmlbc = tgbp__ztkqr[12]
        if not is_overload_bool(kxkb__bmlbc):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        xzx__gad = tgbp__ztkqr[17]
        if not is_overload_none(xzx__gad) and not is_tuple_like_type(xzx__gad):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        yaurl__cbc = tgbp__ztkqr[18]
        if not is_overload_none(yaurl__cbc) and not is_tuple_like_type(
            yaurl__cbc):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        vuuyr__yvewe = tgbp__ztkqr[22]
        if not is_overload_none(vuuyr__yvewe) and not is_overload_int(
            vuuyr__yvewe):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        ryu__hcnvy = tgbp__ztkqr[29]
        if not is_overload_none(ryu__hcnvy) and not is_overload_constant_str(
            ryu__hcnvy):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        rtwdg__mgxi = tgbp__ztkqr[30]
        if not is_overload_none(rtwdg__mgxi) and not is_overload_constant_str(
            rtwdg__mgxi):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        pxgh__ims = types.List(types.mpl_line_2d_type)
        logpp__awmd = get_overload_const_str(logpp__awmd)
        if logpp__awmd == 'scatter':
            if is_overload_none(nhk__fcyh) and is_overload_none(jwd__bhjn):
                raise BodoError(
                    f'{func_name}: {logpp__awmd} requires an x and y column.')
            elif is_overload_none(nhk__fcyh):
                raise BodoError(
                    f'{func_name}: {logpp__awmd} x column is missing.')
            elif is_overload_none(jwd__bhjn):
                raise BodoError(
                    f'{func_name}: {logpp__awmd} y column is missing.')
            pxgh__ims = types.mpl_path_collection_type
        elif logpp__awmd != 'line':
            raise BodoError(
                f'{func_name}: {logpp__awmd} plot is not supported.')
        return signature(pxgh__ims, *tgbp__ztkqr).replace(pysig=phylv__tej)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            pxbag__ntjvz = df.columns.index(attr)
            arr_typ = df.data[pxbag__ntjvz]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            xxwhs__mrbbp = []
            evkw__nxglz = []
            vrgh__dqz = False
            for i, tklis__hxjha in enumerate(df.columns):
                if tklis__hxjha[0] != attr:
                    continue
                vrgh__dqz = True
                xxwhs__mrbbp.append(tklis__hxjha[1] if len(tklis__hxjha) ==
                    2 else tklis__hxjha[1:])
                evkw__nxglz.append(df.data[i])
            if vrgh__dqz:
                return DataFrameType(tuple(evkw__nxglz), df.index, tuple(
                    xxwhs__mrbbp))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        hlxqw__tid = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(hlxqw__tid)
        return lambda tup, idx: tup[val_ind]


def decref_df_data(context, builder, payload, df_type):
    if df_type.is_table_format:
        context.nrt.decref(builder, df_type.table_type, builder.
            extract_value(payload.data, 0))
        context.nrt.decref(builder, df_type.index, payload.index)
        if df_type.has_runtime_cols:
            context.nrt.decref(builder, df_type.data[-1], payload.columns)
        return
    for i in range(len(df_type.data)):
        blerc__fze = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], blerc__fze)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    uzljp__ytzvc = builder.module
    tbnw__xkfrn = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gucth__pqsuf = cgutils.get_or_insert_function(uzljp__ytzvc, tbnw__xkfrn,
        name='.dtor.df.{}'.format(df_type))
    if not gucth__pqsuf.is_declaration:
        return gucth__pqsuf
    gucth__pqsuf.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gucth__pqsuf.append_basic_block())
    naok__uwmt = gucth__pqsuf.args[0]
    wuwll__bxmf = context.get_value_type(payload_type).as_pointer()
    yot__vre = builder.bitcast(naok__uwmt, wuwll__bxmf)
    payload = context.make_helper(builder, payload_type, ref=yot__vre)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        skvue__toa = context.get_python_api(builder)
        nvex__bllp = skvue__toa.gil_ensure()
        skvue__toa.decref(payload.parent)
        skvue__toa.gil_release(nvex__bllp)
    builder.ret_void()
    return gucth__pqsuf


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    mkbiz__tqbg = cgutils.create_struct_proxy(payload_type)(context, builder)
    mkbiz__tqbg.data = data_tup
    mkbiz__tqbg.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        mkbiz__tqbg.columns = colnames
    uuth__ewb = context.get_value_type(payload_type)
    vgwb__chswj = context.get_abi_sizeof(uuth__ewb)
    nwyr__tdt = define_df_dtor(context, builder, df_type, payload_type)
    amn__uiuvg = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, vgwb__chswj), nwyr__tdt)
    kprr__ccoy = context.nrt.meminfo_data(builder, amn__uiuvg)
    pvtef__unxm = builder.bitcast(kprr__ccoy, uuth__ewb.as_pointer())
    ockid__pxb = cgutils.create_struct_proxy(df_type)(context, builder)
    ockid__pxb.meminfo = amn__uiuvg
    if parent is None:
        ockid__pxb.parent = cgutils.get_null_value(ockid__pxb.parent.type)
    else:
        ockid__pxb.parent = parent
        mkbiz__tqbg.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            skvue__toa = context.get_python_api(builder)
            nvex__bllp = skvue__toa.gil_ensure()
            skvue__toa.incref(parent)
            skvue__toa.gil_release(nvex__bllp)
    builder.store(mkbiz__tqbg._getvalue(), pvtef__unxm)
    return ockid__pxb._getvalue()


@intrinsic
def init_runtime_cols_dataframe(typingctx, data_typ, index_typ,
    colnames_index_typ=None):
    assert isinstance(data_typ, types.BaseTuple) and isinstance(data_typ.
        dtype, TableType
        ) and data_typ.dtype.has_runtime_cols, 'init_runtime_cols_dataframe must be called with a table that determines columns at runtime.'
    assert bodo.hiframes.pd_index_ext.is_pd_index_type(colnames_index_typ
        ) or isinstance(colnames_index_typ, bodo.hiframes.
        pd_multi_index_ext.MultiIndexType), 'Column names must be an index'
    if isinstance(data_typ.dtype.arr_types, types.UniTuple):
        olj__mycz = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        olj__mycz = [zorp__vzovj for zorp__vzovj in data_typ.dtype.arr_types]
    sto__kxg = DataFrameType(tuple(olj__mycz + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        lpxex__ocq = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return lpxex__ocq
    sig = signature(sto__kxg, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    jof__lzo = len(data_tup_typ.types)
    if jof__lzo == 0:
        column_names = ()
    lflxo__kto = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(lflxo__kto, ColNamesMetaType) and isinstance(lflxo__kto
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = lflxo__kto.meta
    if jof__lzo == 1 and isinstance(data_tup_typ.types[0], TableType):
        jof__lzo = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == jof__lzo, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    mmx__odpnm = data_tup_typ.types
    if jof__lzo != 0 and isinstance(data_tup_typ.types[0], TableType):
        mmx__odpnm = data_tup_typ.types[0].arr_types
        is_table_format = True
    sto__kxg = DataFrameType(mmx__odpnm, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            ixbkv__cky = cgutils.create_struct_proxy(sto__kxg.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = ixbkv__cky.parent
        lpxex__ocq = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return lpxex__ocq
    sig = signature(sto__kxg, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        ockid__pxb = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, ockid__pxb.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        mkbiz__tqbg = get_dataframe_payload(context, builder, df_typ, args[0])
        abfy__onsma = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[abfy__onsma]
        if df_typ.is_table_format:
            ixbkv__cky = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(mkbiz__tqbg.data, 0))
            hxcr__cihzh = df_typ.table_type.type_to_blk[arr_typ]
            kbboj__wzba = getattr(ixbkv__cky, f'block_{hxcr__cihzh}')
            opb__xej = ListInstance(context, builder, types.List(arr_typ),
                kbboj__wzba)
            bquqm__zke = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[abfy__onsma])
            blerc__fze = opb__xej.getitem(bquqm__zke)
        else:
            blerc__fze = builder.extract_value(mkbiz__tqbg.data, abfy__onsma)
        mwt__xxdq = cgutils.alloca_once_value(builder, blerc__fze)
        utg__opqwo = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, mwt__xxdq, utg__opqwo)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    amn__uiuvg = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, amn__uiuvg)
    wuwll__bxmf = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, wuwll__bxmf)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    sto__kxg = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        sto__kxg = types.Tuple([TableType(df_typ.data)])
    sig = signature(sto__kxg, df_typ)

    def codegen(context, builder, signature, args):
        mkbiz__tqbg = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            mkbiz__tqbg.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        mkbiz__tqbg = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index,
            mkbiz__tqbg.index)
    sto__kxg = df_typ.index
    sig = signature(sto__kxg, df_typ)
    return sig, codegen


def get_dataframe_data(df, i):
    return df[i]


@infer_global(get_dataframe_data)
class GetDataFrameDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        if not is_overload_constant_int(args[1]):
            raise_bodo_error(
                'Selecting a DataFrame column requires a constant column label'
                )
        df = args[0]
        check_runtime_cols_unsupported(df, 'get_dataframe_data')
        i = get_overload_const_int(args[1])
        pmaay__pkpns = df.data[i]
        return pmaay__pkpns(*args)


GetDataFrameDataInfer.prefer_literal = True


def get_dataframe_data_impl(df, i):
    if df.is_table_format:

        def _impl(df, i):
            if has_parent(df) and _column_needs_unboxing(df, i):
                bodo.hiframes.boxing.unbox_dataframe_column(df, i)
            return get_table_data(_get_dataframe_data(df)[0], i)
        return _impl

    def _impl(df, i):
        if has_parent(df) and _column_needs_unboxing(df, i):
            bodo.hiframes.boxing.unbox_dataframe_column(df, i)
        return _get_dataframe_data(df)[i]
    return _impl


@intrinsic
def get_dataframe_table(typingctx, df_typ=None):
    assert df_typ.is_table_format, 'get_dataframe_table() expects table format'

    def codegen(context, builder, signature, args):
        mkbiz__tqbg = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(mkbiz__tqbg.data, 0))
    return df_typ.table_type(df_typ), codegen


def get_dataframe_all_data(df):
    return df.data


def get_dataframe_all_data_impl(df):
    if df.is_table_format:

        def _impl(df):
            return get_dataframe_table(df)
        return _impl
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for i in
        range(len(df.columns)))
    bty__ftq = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{bty__ftq})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        pmaay__pkpns = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return pmaay__pkpns(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        mkbiz__tqbg = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, mkbiz__tqbg.columns)
    return df_typ.runtime_colname_typ(df_typ), codegen


@lower_builtin(get_dataframe_data, DataFrameType, types.IntegerLiteral)
def lower_get_dataframe_data(context, builder, sig, args):
    impl = get_dataframe_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_dataframe_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_index',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_table',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_all_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func


def alias_ext_init_dataframe(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 3
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_dataframe',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_init_dataframe


def init_dataframe_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 3 and not kws
    data_tup = args[0]
    index = args[1]
    kioo__ruhbd = self.typemap[data_tup.name]
    if any(is_tuple_like_type(zorp__vzovj) for zorp__vzovj in kioo__ruhbd.types
        ):
        return None
    if equiv_set.has_shape(data_tup):
        hfq__qijt = equiv_set.get_shape(data_tup)
        if len(hfq__qijt) > 1:
            equiv_set.insert_equiv(*hfq__qijt)
        if len(hfq__qijt) > 0:
            hniaf__zjxyl = self.typemap[index.name]
            if not isinstance(hniaf__zjxyl, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(hfq__qijt[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(hfq__qijt[0], len(
                hfq__qijt)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    wey__xag = args[0]
    data_types = self.typemap[wey__xag.name].data
    if any(is_tuple_like_type(zorp__vzovj) for zorp__vzovj in data_types):
        return None
    if equiv_set.has_shape(wey__xag):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wey__xag)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    wey__xag = args[0]
    hniaf__zjxyl = self.typemap[wey__xag.name].index
    if isinstance(hniaf__zjxyl, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(wey__xag):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wey__xag)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    wey__xag = args[0]
    if equiv_set.has_shape(wey__xag):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wey__xag), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    wey__xag = args[0]
    if equiv_set.has_shape(wey__xag):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wey__xag)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    abfy__onsma = get_overload_const_int(c_ind_typ)
    if df_typ.data[abfy__onsma] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        nsqq__fazeo, xcr__ntui, ftxu__koa = args
        mkbiz__tqbg = get_dataframe_payload(context, builder, df_typ,
            nsqq__fazeo)
        if df_typ.is_table_format:
            ixbkv__cky = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(mkbiz__tqbg.data, 0))
            hxcr__cihzh = df_typ.table_type.type_to_blk[arr_typ]
            kbboj__wzba = getattr(ixbkv__cky, f'block_{hxcr__cihzh}')
            opb__xej = ListInstance(context, builder, types.List(arr_typ),
                kbboj__wzba)
            bquqm__zke = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[abfy__onsma])
            opb__xej.setitem(bquqm__zke, ftxu__koa, True)
        else:
            blerc__fze = builder.extract_value(mkbiz__tqbg.data, abfy__onsma)
            context.nrt.decref(builder, df_typ.data[abfy__onsma], blerc__fze)
            mkbiz__tqbg.data = builder.insert_value(mkbiz__tqbg.data,
                ftxu__koa, abfy__onsma)
            context.nrt.incref(builder, arr_typ, ftxu__koa)
        ockid__pxb = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=nsqq__fazeo)
        payload_type = DataFramePayloadType(df_typ)
        yot__vre = context.nrt.meminfo_data(builder, ockid__pxb.meminfo)
        wuwll__bxmf = context.get_value_type(payload_type).as_pointer()
        yot__vre = builder.bitcast(yot__vre, wuwll__bxmf)
        builder.store(mkbiz__tqbg._getvalue(), yot__vre)
        return impl_ret_borrowed(context, builder, df_typ, nsqq__fazeo)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        umwf__jumbj = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        rykf__qgj = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=umwf__jumbj)
        vkg__suuz = get_dataframe_payload(context, builder, df_typ, umwf__jumbj
            )
        ockid__pxb = construct_dataframe(context, builder, signature.
            return_type, vkg__suuz.data, index_val, rykf__qgj.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), vkg__suuz.data)
        return ockid__pxb
    sto__kxg = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(sto__kxg, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    jof__lzo = len(df_type.columns)
    dujel__nudk = jof__lzo
    qitp__jwgl = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    stl__lohg = col_name not in df_type.columns
    abfy__onsma = jof__lzo
    if stl__lohg:
        qitp__jwgl += arr_type,
        column_names += col_name,
        dujel__nudk += 1
    else:
        abfy__onsma = df_type.columns.index(col_name)
        qitp__jwgl = tuple(arr_type if i == abfy__onsma else qitp__jwgl[i] for
            i in range(jof__lzo))

    def codegen(context, builder, signature, args):
        nsqq__fazeo, xcr__ntui, ftxu__koa = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, nsqq__fazeo)
        jmyq__gdfg = cgutils.create_struct_proxy(df_type)(context, builder,
            value=nsqq__fazeo)
        if df_type.is_table_format:
            jeik__elwhp = df_type.table_type
            szxgp__xyod = builder.extract_value(in_dataframe_payload.data, 0)
            mrch__gql = TableType(qitp__jwgl)
            jxpva__kob = set_table_data_codegen(context, builder,
                jeik__elwhp, szxgp__xyod, mrch__gql, arr_type, ftxu__koa,
                abfy__onsma, stl__lohg)
            data_tup = context.make_tuple(builder, types.Tuple([mrch__gql]),
                [jxpva__kob])
        else:
            mmx__odpnm = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != abfy__onsma else ftxu__koa) for i in range(jof__lzo)
                ]
            if stl__lohg:
                mmx__odpnm.append(ftxu__koa)
            for wey__xag, qnkpk__olci in zip(mmx__odpnm, qitp__jwgl):
                context.nrt.incref(builder, qnkpk__olci, wey__xag)
            data_tup = context.make_tuple(builder, types.Tuple(qitp__jwgl),
                mmx__odpnm)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        jmzkq__saww = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, jmyq__gdfg.parent, None)
        if not stl__lohg and arr_type == df_type.data[abfy__onsma]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            yot__vre = context.nrt.meminfo_data(builder, jmyq__gdfg.meminfo)
            wuwll__bxmf = context.get_value_type(payload_type).as_pointer()
            yot__vre = builder.bitcast(yot__vre, wuwll__bxmf)
            ijb__cive = get_dataframe_payload(context, builder, df_type,
                jmzkq__saww)
            builder.store(ijb__cive._getvalue(), yot__vre)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, mrch__gql, builder.
                    extract_value(data_tup, 0))
            else:
                for wey__xag, qnkpk__olci in zip(mmx__odpnm, qitp__jwgl):
                    context.nrt.incref(builder, qnkpk__olci, wey__xag)
        has_parent = cgutils.is_not_null(builder, jmyq__gdfg.parent)
        with builder.if_then(has_parent):
            skvue__toa = context.get_python_api(builder)
            nvex__bllp = skvue__toa.gil_ensure()
            tlm__jhz = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, ftxu__koa)
            yzsr__duzs = numba.core.pythonapi._BoxContext(context, builder,
                skvue__toa, tlm__jhz)
            xfxxy__duwv = yzsr__duzs.pyapi.from_native_value(arr_type,
                ftxu__koa, yzsr__duzs.env_manager)
            if isinstance(col_name, str):
                xjvtw__bcc = context.insert_const_string(builder.module,
                    col_name)
                riae__qqfpp = skvue__toa.string_from_string(xjvtw__bcc)
            else:
                assert isinstance(col_name, int)
                riae__qqfpp = skvue__toa.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            skvue__toa.object_setitem(jmyq__gdfg.parent, riae__qqfpp,
                xfxxy__duwv)
            skvue__toa.decref(xfxxy__duwv)
            skvue__toa.decref(riae__qqfpp)
            skvue__toa.gil_release(nvex__bllp)
        return jmzkq__saww
    sto__kxg = DataFrameType(qitp__jwgl, index_typ, column_names, df_type.
        dist, df_type.is_table_format)
    sig = signature(sto__kxg, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    jof__lzo = len(pyval.columns)
    mmx__odpnm = []
    for i in range(jof__lzo):
        jos__aizy = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            xfxxy__duwv = jos__aizy.array
        else:
            xfxxy__duwv = jos__aizy.values
        mmx__odpnm.append(xfxxy__duwv)
    mmx__odpnm = tuple(mmx__odpnm)
    if df_type.is_table_format:
        ixbkv__cky = context.get_constant_generic(builder, df_type.
            table_type, Table(mmx__odpnm))
        data_tup = lir.Constant.literal_struct([ixbkv__cky])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], tklis__hxjha) for
            i, tklis__hxjha in enumerate(mmx__odpnm)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    xorua__giu = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, xorua__giu])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    marpp__axu = context.get_constant(types.int64, -1)
    apba__bhdj = context.get_constant_null(types.voidptr)
    amn__uiuvg = lir.Constant.literal_struct([marpp__axu, apba__bhdj,
        apba__bhdj, payload, marpp__axu])
    amn__uiuvg = cgutils.global_constant(builder, '.const.meminfo', amn__uiuvg
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([amn__uiuvg, xorua__giu])


@lower_cast(DataFrameType, DataFrameType)
def cast_df_to_df(context, builder, fromty, toty, val):
    if (fromty.data == toty.data and fromty.index == toty.index and fromty.
        columns == toty.columns and fromty.is_table_format == toty.
        is_table_format and fromty.dist != toty.dist and fromty.
        has_runtime_cols == toty.has_runtime_cols):
        return val
    if not fromty.has_runtime_cols and not toty.has_runtime_cols and len(fromty
        .data) == 0 and len(toty.columns):
        return _cast_empty_df(context, builder, toty)
    if len(fromty.data) != len(toty.data) or fromty.data != toty.data and any(
        context.typing_context.unify_pairs(fromty.data[i], toty.data[i]) is
        None for i in range(len(fromty.data))
        ) or fromty.has_runtime_cols != toty.has_runtime_cols:
        raise BodoError(f'Invalid dataframe cast from {fromty} to {toty}')
    in_dataframe_payload = get_dataframe_payload(context, builder, fromty, val)
    if isinstance(fromty.index, RangeIndexType) and isinstance(toty.index,
        NumericIndexType):
        llt__eedj = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        llt__eedj = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, llt__eedj)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        evkw__nxglz = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                evkw__nxglz)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), evkw__nxglz)
    elif not fromty.is_table_format and toty.is_table_format:
        evkw__nxglz = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        evkw__nxglz = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        evkw__nxglz = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        evkw__nxglz = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, evkw__nxglz,
        llt__eedj, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    iwfh__xlthf = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        hie__lsn = get_index_data_arr_types(toty.index)[0]
        usq__oku = bodo.utils.transform.get_type_alloc_counts(hie__lsn) - 1
        fex__ihxr = ', '.join('0' for xcr__ntui in range(usq__oku))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(fex__ihxr, ', ' if usq__oku == 1 else ''))
        iwfh__xlthf['index_arr_type'] = hie__lsn
    bnlnu__hng = []
    for i, arr_typ in enumerate(toty.data):
        usq__oku = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        fex__ihxr = ', '.join('0' for xcr__ntui in range(usq__oku))
        gjge__lzwy = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, fex__ihxr, ', ' if usq__oku == 1 else ''))
        bnlnu__hng.append(gjge__lzwy)
        iwfh__xlthf[f'arr_type{i}'] = arr_typ
    bnlnu__hng = ', '.join(bnlnu__hng)
    phi__ykp = 'def impl():\n'
    bhqfn__pai = bodo.hiframes.dataframe_impl._gen_init_df(phi__ykp, toty.
        columns, bnlnu__hng, index, iwfh__xlthf)
    df = context.compile_internal(builder, bhqfn__pai, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    lmf__cnpz = toty.table_type
    ixbkv__cky = cgutils.create_struct_proxy(lmf__cnpz)(context, builder)
    ixbkv__cky.parent = in_dataframe_payload.parent
    for zorp__vzovj, hxcr__cihzh in lmf__cnpz.type_to_blk.items():
        nuh__iupy = context.get_constant(types.int64, len(lmf__cnpz.
            block_to_arr_ind[hxcr__cihzh]))
        xcr__ntui, iptt__one = ListInstance.allocate_ex(context, builder,
            types.List(zorp__vzovj), nuh__iupy)
        iptt__one.size = nuh__iupy
        setattr(ixbkv__cky, f'block_{hxcr__cihzh}', iptt__one.value)
    for i, zorp__vzovj in enumerate(fromty.data):
        nbee__lyuo = toty.data[i]
        if zorp__vzovj != nbee__lyuo:
            qkwbq__ybabd = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qkwbq__ybabd)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        blerc__fze = builder.extract_value(in_dataframe_payload.data, i)
        if zorp__vzovj != nbee__lyuo:
            bzdwc__tye = context.cast(builder, blerc__fze, zorp__vzovj,
                nbee__lyuo)
            fhap__lco = False
        else:
            bzdwc__tye = blerc__fze
            fhap__lco = True
        hxcr__cihzh = lmf__cnpz.type_to_blk[zorp__vzovj]
        kbboj__wzba = getattr(ixbkv__cky, f'block_{hxcr__cihzh}')
        opb__xej = ListInstance(context, builder, types.List(zorp__vzovj),
            kbboj__wzba)
        bquqm__zke = context.get_constant(types.int64, lmf__cnpz.
            block_offsets[i])
        opb__xej.setitem(bquqm__zke, bzdwc__tye, fhap__lco)
    data_tup = context.make_tuple(builder, types.Tuple([lmf__cnpz]), [
        ixbkv__cky._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    mmx__odpnm = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            qkwbq__ybabd = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qkwbq__ybabd)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            blerc__fze = builder.extract_value(in_dataframe_payload.data, i)
            bzdwc__tye = context.cast(builder, blerc__fze, fromty.data[i],
                toty.data[i])
            fhap__lco = False
        else:
            bzdwc__tye = builder.extract_value(in_dataframe_payload.data, i)
            fhap__lco = True
        if fhap__lco:
            context.nrt.incref(builder, toty.data[i], bzdwc__tye)
        mmx__odpnm.append(bzdwc__tye)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), mmx__odpnm)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    jeik__elwhp = fromty.table_type
    szxgp__xyod = cgutils.create_struct_proxy(jeik__elwhp)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    mrch__gql = toty.table_type
    jxpva__kob = cgutils.create_struct_proxy(mrch__gql)(context, builder)
    jxpva__kob.parent = in_dataframe_payload.parent
    for zorp__vzovj, hxcr__cihzh in mrch__gql.type_to_blk.items():
        nuh__iupy = context.get_constant(types.int64, len(mrch__gql.
            block_to_arr_ind[hxcr__cihzh]))
        xcr__ntui, iptt__one = ListInstance.allocate_ex(context, builder,
            types.List(zorp__vzovj), nuh__iupy)
        iptt__one.size = nuh__iupy
        setattr(jxpva__kob, f'block_{hxcr__cihzh}', iptt__one.value)
    for i in range(len(fromty.data)):
        hfso__mwpbo = fromty.data[i]
        nbee__lyuo = toty.data[i]
        if hfso__mwpbo != nbee__lyuo:
            qkwbq__ybabd = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qkwbq__ybabd)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        pukj__vawxi = jeik__elwhp.type_to_blk[hfso__mwpbo]
        qgepq__rmt = getattr(szxgp__xyod, f'block_{pukj__vawxi}')
        xouq__qvv = ListInstance(context, builder, types.List(hfso__mwpbo),
            qgepq__rmt)
        skru__asepw = context.get_constant(types.int64, jeik__elwhp.
            block_offsets[i])
        blerc__fze = xouq__qvv.getitem(skru__asepw)
        if hfso__mwpbo != nbee__lyuo:
            bzdwc__tye = context.cast(builder, blerc__fze, hfso__mwpbo,
                nbee__lyuo)
            fhap__lco = False
        else:
            bzdwc__tye = blerc__fze
            fhap__lco = True
        jopfi__njdn = mrch__gql.type_to_blk[zorp__vzovj]
        iptt__one = getattr(jxpva__kob, f'block_{jopfi__njdn}')
        dvew__xtl = ListInstance(context, builder, types.List(nbee__lyuo),
            iptt__one)
        ydz__ttu = context.get_constant(types.int64, mrch__gql.block_offsets[i]
            )
        dvew__xtl.setitem(ydz__ttu, bzdwc__tye, fhap__lco)
    data_tup = context.make_tuple(builder, types.Tuple([mrch__gql]), [
        jxpva__kob._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    lmf__cnpz = fromty.table_type
    ixbkv__cky = cgutils.create_struct_proxy(lmf__cnpz)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    mmx__odpnm = []
    for i, zorp__vzovj in enumerate(toty.data):
        hfso__mwpbo = fromty.data[i]
        if zorp__vzovj != hfso__mwpbo:
            qkwbq__ybabd = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qkwbq__ybabd)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        hxcr__cihzh = lmf__cnpz.type_to_blk[zorp__vzovj]
        kbboj__wzba = getattr(ixbkv__cky, f'block_{hxcr__cihzh}')
        opb__xej = ListInstance(context, builder, types.List(zorp__vzovj),
            kbboj__wzba)
        bquqm__zke = context.get_constant(types.int64, lmf__cnpz.
            block_offsets[i])
        blerc__fze = opb__xej.getitem(bquqm__zke)
        if zorp__vzovj != hfso__mwpbo:
            bzdwc__tye = context.cast(builder, blerc__fze, hfso__mwpbo,
                zorp__vzovj)
            fhap__lco = False
        else:
            bzdwc__tye = blerc__fze
            fhap__lco = True
        if fhap__lco:
            context.nrt.incref(builder, zorp__vzovj, bzdwc__tye)
        mmx__odpnm.append(bzdwc__tye)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), mmx__odpnm)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    xkkui__hwr, bnlnu__hng, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    ubc__yngh = ColNamesMetaType(tuple(xkkui__hwr))
    phi__ykp = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    phi__ykp += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(bnlnu__hng, index_arg))
    allr__ezp = {}
    exec(phi__ykp, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': ubc__yngh}, allr__ezp)
    mbr__hsbsv = allr__ezp['_init_df']
    return mbr__hsbsv


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    sto__kxg = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ.
        index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(sto__kxg, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    sto__kxg = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ.
        index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(sto__kxg, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    cjkn__zog = ''
    if not is_overload_none(dtype):
        cjkn__zog = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        jof__lzo = (len(data.types) - 1) // 2
        ulrhz__dna = [zorp__vzovj.literal_value for zorp__vzovj in data.
            types[1:jof__lzo + 1]]
        data_val_types = dict(zip(ulrhz__dna, data.types[jof__lzo + 1:]))
        mmx__odpnm = ['data[{}]'.format(i) for i in range(jof__lzo + 1, 2 *
            jof__lzo + 1)]
        data_dict = dict(zip(ulrhz__dna, mmx__odpnm))
        if is_overload_none(index):
            for i, zorp__vzovj in enumerate(data.types[jof__lzo + 1:]):
                if isinstance(zorp__vzovj, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(jof__lzo + 1 + i))
                    index_is_none = False
                    break
    elif is_overload_none(data):
        data_dict = {}
        data_val_types = {}
    else:
        if not (isinstance(data, types.Array) and data.ndim == 2):
            raise BodoError(
                'pd.DataFrame() only supports constant dictionary and array input'
                )
        if is_overload_none(columns):
            raise BodoError(
                "pd.DataFrame() 'columns' argument is required when an array is passed as data"
                )
        afre__uia = '.copy()' if copy else ''
        jcpv__djdr = get_overload_const_list(columns)
        jof__lzo = len(jcpv__djdr)
        data_val_types = {yzsr__duzs: data.copy(ndim=1) for yzsr__duzs in
            jcpv__djdr}
        mmx__odpnm = ['data[:,{}]{}'.format(i, afre__uia) for i in range(
            jof__lzo)]
        data_dict = dict(zip(jcpv__djdr, mmx__odpnm))
    if is_overload_none(columns):
        col_names = data_dict.keys()
    else:
        col_names = get_overload_const_list(columns)
    df_len = _get_df_len_from_info(data_dict, data_val_types, col_names,
        index_is_none, index_arg)
    _fill_null_arrays(data_dict, col_names, df_len, dtype)
    if index_is_none:
        if is_overload_none(data):
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_binary_str_index(bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0))'
                )
        else:
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, {}, 1, None)'
                .format(df_len))
    bnlnu__hng = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[yzsr__duzs], df_len, cjkn__zog) for yzsr__duzs in
        col_names))
    if len(col_names) == 0:
        bnlnu__hng = '()'
    return col_names, bnlnu__hng, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for yzsr__duzs in col_names:
        if yzsr__duzs in data_dict and is_iterable_type(data_val_types[
            yzsr__duzs]):
            df_len = 'len({})'.format(data_dict[yzsr__duzs])
            break
    if df_len == '0':
        if not index_is_none:
            df_len = f'len({index_arg})'
        elif data_dict:
            raise BodoError(
                'Internal Error: Unable to determine length of DataFrame Index. If this is unexpected, please try passing an index value.'
                )
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(yzsr__duzs in data_dict for yzsr__duzs in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    usc__ywn = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for yzsr__duzs in col_names:
        if yzsr__duzs not in data_dict:
            data_dict[yzsr__duzs] = usc__ywn


@infer_global(len)
class LenTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        if isinstance(args[0], (DataFrameType, bodo.TableType)):
            return types.int64(*args)


@lower_builtin(len, DataFrameType)
def table_len_lower(context, builder, sig, args):
    impl = df_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_len_overload(df):
    if not isinstance(df, DataFrameType):
        return
    if df.has_runtime_cols:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            zorp__vzovj = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df
                )
            return len(zorp__vzovj)
        return impl
    if len(df.columns) == 0:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
        return impl

    def impl(df):
        if is_null_pointer(df._meminfo):
            return 0
        return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 0))
    return impl


@infer_global(operator.getitem)
class GetItemTuple(AbstractTemplate):
    key = operator.getitem

    def generic(self, args, kws):
        tup, idx = args
        if not isinstance(tup, types.BaseTuple) or not isinstance(idx,
            types.IntegerLiteral):
            return
        tkvo__wkmyk = idx.literal_value
        if isinstance(tkvo__wkmyk, int):
            pmaay__pkpns = tup.types[tkvo__wkmyk]
        elif isinstance(tkvo__wkmyk, slice):
            pmaay__pkpns = types.BaseTuple.from_types(tup.types[tkvo__wkmyk])
        return signature(pmaay__pkpns, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    pos__ubu, idx = sig.args
    idx = idx.literal_value
    tup, xcr__ntui = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(pos__ubu)
        if not 0 <= idx < len(pos__ubu):
            raise IndexError('cannot index at %d in %s' % (idx, pos__ubu))
        unsm__tkcu = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        lubk__zrhk = cgutils.unpack_tuple(builder, tup)[idx]
        unsm__tkcu = context.make_tuple(builder, sig.return_type, lubk__zrhk)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, unsm__tkcu)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, lceo__hvj, suffix_x,
            suffix_y, is_join, indicator, xcr__ntui, xcr__ntui) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        fmp__xsyny = {yzsr__duzs: i for i, yzsr__duzs in enumerate(left_on)}
        yeotl__tmf = {yzsr__duzs: i for i, yzsr__duzs in enumerate(right_on)}
        uwwfg__mfev = set(left_on) & set(right_on)
        tzqx__injz = set(left_df.columns) & set(right_df.columns)
        hbr__imzu = tzqx__injz - uwwfg__mfev
        gds__ardc = '$_bodo_index_' in left_on
        eui__fbqap = '$_bodo_index_' in right_on
        how = get_overload_const_str(lceo__hvj)
        vrs__nky = how in {'left', 'outer'}
        lmtt__sggqn = how in {'right', 'outer'}
        columns = []
        data = []
        if gds__ardc:
            vjfu__oylh = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            vjfu__oylh = left_df.data[left_df.column_index[left_on[0]]]
        if eui__fbqap:
            mpqgb__zkhmh = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            mpqgb__zkhmh = right_df.data[right_df.column_index[right_on[0]]]
        if gds__ardc and not eui__fbqap and not is_join.literal_value:
            cogf__qbt = right_on[0]
            if cogf__qbt in left_df.column_index:
                columns.append(cogf__qbt)
                if (mpqgb__zkhmh == bodo.dict_str_arr_type and vjfu__oylh ==
                    bodo.string_array_type):
                    ygcm__uvia = bodo.string_array_type
                else:
                    ygcm__uvia = mpqgb__zkhmh
                data.append(ygcm__uvia)
        if eui__fbqap and not gds__ardc and not is_join.literal_value:
            ldubu__foxqb = left_on[0]
            if ldubu__foxqb in right_df.column_index:
                columns.append(ldubu__foxqb)
                if (vjfu__oylh == bodo.dict_str_arr_type and mpqgb__zkhmh ==
                    bodo.string_array_type):
                    ygcm__uvia = bodo.string_array_type
                else:
                    ygcm__uvia = vjfu__oylh
                data.append(ygcm__uvia)
        for hfso__mwpbo, jos__aizy in zip(left_df.data, left_df.columns):
            columns.append(str(jos__aizy) + suffix_x.literal_value if 
                jos__aizy in hbr__imzu else jos__aizy)
            if jos__aizy in uwwfg__mfev:
                if hfso__mwpbo == bodo.dict_str_arr_type:
                    hfso__mwpbo = right_df.data[right_df.column_index[
                        jos__aizy]]
                data.append(hfso__mwpbo)
            else:
                if (hfso__mwpbo == bodo.dict_str_arr_type and jos__aizy in
                    fmp__xsyny):
                    if eui__fbqap:
                        hfso__mwpbo = mpqgb__zkhmh
                    else:
                        zazf__rjh = fmp__xsyny[jos__aizy]
                        vulvh__ilfd = right_on[zazf__rjh]
                        hfso__mwpbo = right_df.data[right_df.column_index[
                            vulvh__ilfd]]
                if lmtt__sggqn:
                    hfso__mwpbo = to_nullable_type(hfso__mwpbo)
                data.append(hfso__mwpbo)
        for hfso__mwpbo, jos__aizy in zip(right_df.data, right_df.columns):
            if jos__aizy not in uwwfg__mfev:
                columns.append(str(jos__aizy) + suffix_y.literal_value if 
                    jos__aizy in hbr__imzu else jos__aizy)
                if (hfso__mwpbo == bodo.dict_str_arr_type and jos__aizy in
                    yeotl__tmf):
                    if gds__ardc:
                        hfso__mwpbo = vjfu__oylh
                    else:
                        zazf__rjh = yeotl__tmf[jos__aizy]
                        osew__mkth = left_on[zazf__rjh]
                        hfso__mwpbo = left_df.data[left_df.column_index[
                            osew__mkth]]
                if vrs__nky:
                    hfso__mwpbo = to_nullable_type(hfso__mwpbo)
                data.append(hfso__mwpbo)
        ufrja__jjvq = get_overload_const_bool(indicator)
        if ufrja__jjvq:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        wrg__vxp = False
        if gds__ardc and eui__fbqap and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            wrg__vxp = True
        elif gds__ardc and not eui__fbqap:
            index_typ = right_df.index
            wrg__vxp = True
        elif eui__fbqap and not gds__ardc:
            index_typ = left_df.index
            wrg__vxp = True
        if wrg__vxp and isinstance(index_typ, bodo.hiframes.pd_index_ext.
            RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        ouc__umk = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(ouc__umk, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    ockid__pxb = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ockid__pxb._getvalue()


@overload(pd.concat, inline='always', no_unliteral=True)
def concat_overload(objs, axis=0, join='outer', join_axes=None,
    ignore_index=False, keys=None, levels=None, names=None,
    verify_integrity=False, sort=None, copy=True):
    if not is_overload_constant_int(axis):
        raise BodoError("pd.concat(): 'axis' should be a constant integer")
    if not is_overload_constant_bool(ignore_index):
        raise BodoError(
            "pd.concat(): 'ignore_index' should be a constant boolean")
    axis = get_overload_const_int(axis)
    ignore_index = is_overload_true(ignore_index)
    nimni__pxww = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    gdr__sdd = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', nimni__pxww, gdr__sdd,
        package_name='pandas', module_name='General')
    phi__ykp = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        hozu__rrya = 0
        bnlnu__hng = []
        names = []
        for i, ntgv__dow in enumerate(objs.types):
            assert isinstance(ntgv__dow, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(ntgv__dow, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ntgv__dow
                , 'pandas.concat()')
            if isinstance(ntgv__dow, SeriesType):
                names.append(str(hozu__rrya))
                hozu__rrya += 1
                bnlnu__hng.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(ntgv__dow.columns)
                for iext__mqmg in range(len(ntgv__dow.data)):
                    bnlnu__hng.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, iext__mqmg))
        return bodo.hiframes.dataframe_impl._gen_init_df(phi__ykp, names,
            ', '.join(bnlnu__hng), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(zorp__vzovj, DataFrameType) for zorp__vzovj in
            objs.types)
        czr__zjz = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            czr__zjz.extend(df.columns)
        czr__zjz = list(dict.fromkeys(czr__zjz).keys())
        olj__mycz = {}
        for hozu__rrya, yzsr__duzs in enumerate(czr__zjz):
            for i, df in enumerate(objs.types):
                if yzsr__duzs in df.column_index:
                    olj__mycz[f'arr_typ{hozu__rrya}'] = df.data[df.
                        column_index[yzsr__duzs]]
                    break
        assert len(olj__mycz) == len(czr__zjz)
        xprm__hips = []
        for hozu__rrya, yzsr__duzs in enumerate(czr__zjz):
            args = []
            for i, df in enumerate(objs.types):
                if yzsr__duzs in df.column_index:
                    abfy__onsma = df.column_index[yzsr__duzs]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, abfy__onsma))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, hozu__rrya))
            phi__ykp += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'.
                format(hozu__rrya, ', '.join(args)))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(A0), 1, None)'
                )
        else:
            index = (
                """bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)) if len(objs[i].
                columns) > 0)))
        return bodo.hiframes.dataframe_impl._gen_init_df(phi__ykp, czr__zjz,
            ', '.join('A{}'.format(i) for i in range(len(czr__zjz))), index,
            olj__mycz)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(zorp__vzovj, SeriesType) for zorp__vzovj in
            objs.types)
        phi__ykp += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'.
            format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            phi__ykp += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            phi__ykp += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        phi__ykp += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        allr__ezp = {}
        exec(phi__ykp, {'bodo': bodo, 'np': np, 'numba': numba}, allr__ezp)
        return allr__ezp['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for hozu__rrya, yzsr__duzs in enumerate(df_type.columns):
            phi__ykp += '  arrs{} = []\n'.format(hozu__rrya)
            phi__ykp += '  for i in range(len(objs)):\n'
            phi__ykp += '    df = objs[i]\n'
            phi__ykp += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(hozu__rrya))
            phi__ykp += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(hozu__rrya))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            phi__ykp += '  arrs_index = []\n'
            phi__ykp += '  for i in range(len(objs)):\n'
            phi__ykp += '    df = objs[i]\n'
            phi__ykp += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(phi__ykp, df_type.
            columns, ', '.join('out_arr{}'.format(i) for i in range(len(
            df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        phi__ykp += '  arrs = []\n'
        phi__ykp += '  for i in range(len(objs)):\n'
        phi__ykp += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        phi__ykp += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            phi__ykp += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            phi__ykp += '  arrs_index = []\n'
            phi__ykp += '  for i in range(len(objs)):\n'
            phi__ykp += '    S = objs[i]\n'
            phi__ykp += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            phi__ykp += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        phi__ykp += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        allr__ezp = {}
        exec(phi__ykp, {'bodo': bodo, 'np': np, 'numba': numba}, allr__ezp)
        return allr__ezp['impl']
    raise BodoError('pd.concat(): input type {} not supported yet'.format(objs)
        )


def sort_values_dummy(df, by, ascending, inplace, na_position):
    return df.sort_values(by, ascending=ascending, inplace=inplace,
        na_position=na_position)


@infer_global(sort_values_dummy)
class SortDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, by, ascending, inplace, na_position = args
        index = df.index
        if isinstance(index, bodo.hiframes.pd_index_ext.RangeIndexType):
            index = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64)
        sto__kxg = df.copy(index=index)
        return signature(sto__kxg, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    xgfcn__bscnz = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return xgfcn__bscnz._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    nimni__pxww = dict(index=index, name=name)
    gdr__sdd = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', nimni__pxww, gdr__sdd,
        package_name='pandas', module_name='DataFrame')

    def _impl(df, index=True, name='Pandas'):
        return bodo.hiframes.pd_dataframe_ext.itertuples_dummy(df)
    return _impl


def itertuples_dummy(df):
    return df


@infer_global(itertuples_dummy)
class ItertuplesDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, = args
        assert 'Index' not in df.columns
        columns = ('Index',) + df.columns
        olj__mycz = (types.Array(types.int64, 1, 'C'),) + df.data
        rpa__dfbvk = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, olj__mycz)
        return signature(rpa__dfbvk, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    xgfcn__bscnz = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return xgfcn__bscnz._getvalue()


def query_dummy(df, expr):
    return df.eval(expr)


@infer_global(query_dummy)
class QueryDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=RangeIndexType(types
            .none)), *args)


@lower_builtin(query_dummy, types.VarArg(types.Any))
def lower_query_dummy(context, builder, sig, args):
    xgfcn__bscnz = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return xgfcn__bscnz._getvalue()


def val_isin_dummy(S, vals):
    return S in vals


def val_notin_dummy(S, vals):
    return S not in vals


@infer_global(val_isin_dummy)
@infer_global(val_notin_dummy)
class ValIsinTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=args[0].index), *args)


@lower_builtin(val_isin_dummy, types.VarArg(types.Any))
@lower_builtin(val_notin_dummy, types.VarArg(types.Any))
def lower_val_isin_dummy(context, builder, sig, args):
    xgfcn__bscnz = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return xgfcn__bscnz._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    is_already_shuffled=False, _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    ypa__ova = get_overload_const_bool(check_duplicates)
    pqa__jon = not get_overload_const_bool(is_already_shuffled)
    aly__vvw = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    dbq__iwi = len(value_names) > 1
    oks__vlzkl = None
    qkn__rys = None
    hxcoc__fvha = None
    xyyzl__jlnne = None
    yvw__liskt = isinstance(values_tup, types.UniTuple)
    if yvw__liskt:
        jkekx__jmuz = [to_str_arr_if_dict_array(to_nullable_type(values_tup
            .dtype))]
    else:
        jkekx__jmuz = [to_str_arr_if_dict_array(to_nullable_type(
            qnkpk__olci)) for qnkpk__olci in values_tup]
    phi__ykp = 'def impl(\n'
    phi__ykp += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, is_already_shuffled=False, _constant_pivot_values=None, parallel=False
"""
    phi__ykp += '):\n'
    phi__ykp += "    ev = tracing.Event('pivot_impl', is_parallel=parallel)\n"
    if pqa__jon:
        phi__ykp += '    if parallel:\n'
        phi__ykp += (
            "        ev_shuffle = tracing.Event('shuffle_pivot_index')\n")
        myod__hje = ', '.join([f'array_to_info(index_tup[{i}])' for i in
            range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for
            i in range(len(columns_tup))] + [
            f'array_to_info(values_tup[{i}])' for i in range(len(values_tup))])
        phi__ykp += f'        info_list = [{myod__hje}]\n'
        phi__ykp += '        cpp_table = arr_info_list_to_table(info_list)\n'
        phi__ykp += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
        ruf__mpits = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
             for i in range(len(index_tup))])
        eoia__olwja = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
             for i in range(len(columns_tup))])
        aaw__fmsyq = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
             for i in range(len(values_tup))])
        phi__ykp += f'        index_tup = ({ruf__mpits},)\n'
        phi__ykp += f'        columns_tup = ({eoia__olwja},)\n'
        phi__ykp += f'        values_tup = ({aaw__fmsyq},)\n'
        phi__ykp += '        delete_table(cpp_table)\n'
        phi__ykp += '        delete_table(out_cpp_table)\n'
        phi__ykp += '        ev_shuffle.finalize()\n'
    phi__ykp += '    columns_arr = columns_tup[0]\n'
    if yvw__liskt:
        phi__ykp += '    values_arrs = [arr for arr in values_tup]\n'
    phi__ykp += (
        "    ev_unique = tracing.Event('pivot_unique_index_map', is_parallel=parallel)\n"
        )
    phi__ykp += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    phi__ykp += '        index_tup\n'
    phi__ykp += '    )\n'
    phi__ykp += '    n_rows = len(unique_index_arr_tup[0])\n'
    phi__ykp += '    num_values_arrays = len(values_tup)\n'
    phi__ykp += '    n_unique_pivots = len(pivot_values)\n'
    if yvw__liskt:
        phi__ykp += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        phi__ykp += '    n_cols = n_unique_pivots\n'
    phi__ykp += '    col_map = {}\n'
    phi__ykp += '    for i in range(n_unique_pivots):\n'
    phi__ykp += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    phi__ykp += '            raise ValueError(\n'
    phi__ykp += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    phi__ykp += '            )\n'
    phi__ykp += '        col_map[pivot_values[i]] = i\n'
    phi__ykp += '    ev_unique.finalize()\n'
    phi__ykp += (
        "    ev_alloc = tracing.Event('pivot_alloc', is_parallel=parallel)\n")
    rnaws__obv = False
    for i, cbk__ggxl in enumerate(jkekx__jmuz):
        if is_str_arr_type(cbk__ggxl):
            rnaws__obv = True
            phi__ykp += (
                f'    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]\n'
                )
            phi__ykp += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if rnaws__obv:
        if ypa__ova:
            phi__ykp += '    nbytes = (n_rows + 7) >> 3\n'
            phi__ykp += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        phi__ykp += '    for i in range(len(columns_arr)):\n'
        phi__ykp += '        col_name = columns_arr[i]\n'
        phi__ykp += '        pivot_idx = col_map[col_name]\n'
        phi__ykp += '        row_idx = row_vector[i]\n'
        if ypa__ova:
            phi__ykp += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            phi__ykp += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            phi__ykp += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            phi__ykp += '        else:\n'
            phi__ykp += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if yvw__liskt:
            phi__ykp += '        for j in range(num_values_arrays):\n'
            phi__ykp += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            phi__ykp += '            len_arr = len_arrs_0[col_idx]\n'
            phi__ykp += '            values_arr = values_arrs[j]\n'
            phi__ykp += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            phi__ykp += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            phi__ykp += '                len_arr[row_idx] = str_val_len\n'
            phi__ykp += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, cbk__ggxl in enumerate(jkekx__jmuz):
                if is_str_arr_type(cbk__ggxl):
                    phi__ykp += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    phi__ykp += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    phi__ykp += (
                        f'            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}\n'
                        )
                    phi__ykp += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    phi__ykp += f"    ev_alloc.add_attribute('num_rows', n_rows)\n"
    for i, cbk__ggxl in enumerate(jkekx__jmuz):
        if is_str_arr_type(cbk__ggxl):
            phi__ykp += f'    data_arrs_{i} = [\n'
            phi__ykp += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            phi__ykp += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            phi__ykp += '        )\n'
            phi__ykp += '        for i in range(n_cols)\n'
            phi__ykp += '    ]\n'
            phi__ykp += f'    if tracing.is_tracing():\n'
            phi__ykp += '         for i in range(n_cols):'
            phi__ykp += f"""            ev_alloc.add_attribute('total_str_chars_out_column_{i}_' + str(i), total_lens_{i}[i])
"""
        else:
            phi__ykp += f'    data_arrs_{i} = [\n'
            phi__ykp += (
                f'        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})\n'
                )
            phi__ykp += '        for _ in range(n_cols)\n'
            phi__ykp += '    ]\n'
    if not rnaws__obv and ypa__ova:
        phi__ykp += '    nbytes = (n_rows + 7) >> 3\n'
        phi__ykp += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    phi__ykp += '    ev_alloc.finalize()\n'
    phi__ykp += (
        "    ev_fill = tracing.Event('pivot_fill_data', is_parallel=parallel)\n"
        )
    phi__ykp += '    for i in range(len(columns_arr)):\n'
    phi__ykp += '        col_name = columns_arr[i]\n'
    phi__ykp += '        pivot_idx = col_map[col_name]\n'
    phi__ykp += '        row_idx = row_vector[i]\n'
    if not rnaws__obv and ypa__ova:
        phi__ykp += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        phi__ykp += (
            '        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):\n'
            )
        phi__ykp += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        phi__ykp += '        else:\n'
        phi__ykp += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if yvw__liskt:
        phi__ykp += '        for j in range(num_values_arrays):\n'
        phi__ykp += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        phi__ykp += '            col_arr = data_arrs_0[col_idx]\n'
        phi__ykp += '            values_arr = values_arrs[j]\n'
        phi__ykp += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        phi__ykp += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        phi__ykp += '            else:\n'
        phi__ykp += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, cbk__ggxl in enumerate(jkekx__jmuz):
            phi__ykp += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            phi__ykp += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            phi__ykp += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            phi__ykp += f'        else:\n'
            phi__ykp += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        phi__ykp += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        oks__vlzkl = index_names.meta[0]
    else:
        phi__ykp += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        oks__vlzkl = tuple(index_names.meta)
    phi__ykp += f'    if tracing.is_tracing():\n'
    phi__ykp += f'        index_nbytes = index.nbytes\n'
    phi__ykp += f"        ev.add_attribute('index_nbytes', index_nbytes)\n"
    if not aly__vvw:
        hxcoc__fvha = columns_name.meta[0]
        if dbq__iwi:
            phi__ykp += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            qkn__rys = value_names.meta
            if all(isinstance(yzsr__duzs, str) for yzsr__duzs in qkn__rys):
                qkn__rys = pd.array(qkn__rys, 'string')
            elif all(isinstance(yzsr__duzs, int) for yzsr__duzs in qkn__rys):
                qkn__rys = np.array(qkn__rys, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(qkn__rys.dtype, pd.StringDtype):
                phi__ykp += '    total_chars = 0\n'
                phi__ykp += f'    for i in range({len(value_names)}):\n'
                phi__ykp += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                phi__ykp += '        total_chars += value_name_str_len\n'
                phi__ykp += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                phi__ykp += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                phi__ykp += '    total_chars = 0\n'
                phi__ykp += '    for i in range(len(pivot_values)):\n'
                phi__ykp += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                phi__ykp += '        total_chars += pivot_val_str_len\n'
                phi__ykp += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                phi__ykp += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            phi__ykp += f'    for i in range({len(value_names)}):\n'
            phi__ykp += '        for j in range(len(pivot_values)):\n'
            phi__ykp += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            phi__ykp += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            phi__ykp += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            phi__ykp += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    phi__ykp += '    ev_fill.finalize()\n'
    lmf__cnpz = None
    if aly__vvw:
        if dbq__iwi:
            vldj__lzpc = []
            for vwgra__xjm in _constant_pivot_values.meta:
                for lzcf__svw in value_names.meta:
                    vldj__lzpc.append((vwgra__xjm, lzcf__svw))
            column_names = tuple(vldj__lzpc)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        xyyzl__jlnne = ColNamesMetaType(column_names)
        ong__kyzwf = []
        for qnkpk__olci in jkekx__jmuz:
            ong__kyzwf.extend([qnkpk__olci] * len(_constant_pivot_values))
        eqe__vlouy = tuple(ong__kyzwf)
        lmf__cnpz = TableType(eqe__vlouy)
        phi__ykp += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        phi__ykp += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, qnkpk__olci in enumerate(jkekx__jmuz):
            phi__ykp += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {lmf__cnpz.type_to_blk[qnkpk__olci]})
"""
        phi__ykp += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        phi__ykp += '        (table,), index, columns_typ\n'
        phi__ykp += '    )\n'
    else:
        kxzy__iryl = ', '.join(f'data_arrs_{i}' for i in range(len(
            jkekx__jmuz)))
        phi__ykp += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({kxzy__iryl},), n_rows)
"""
        phi__ykp += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        phi__ykp += '        (table,), index, column_index\n'
        phi__ykp += '    )\n'
    phi__ykp += '    ev.finalize()\n'
    phi__ykp += '    return result\n'
    allr__ezp = {}
    poyfh__pczq = {f'data_arr_typ_{i}': cbk__ggxl for i, cbk__ggxl in
        enumerate(jkekx__jmuz)}
    prjrz__etta = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        lmf__cnpz, 'columns_typ': xyyzl__jlnne, 'index_names_lit':
        oks__vlzkl, 'value_names_lit': qkn__rys, 'columns_name_lit':
        hxcoc__fvha, **poyfh__pczq, 'tracing': tracing}
    exec(phi__ykp, prjrz__etta, allr__ezp)
    impl = allr__ezp['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    syws__jskd = {}
    syws__jskd['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, gvu__tmz in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        vrqq__cqxm = None
        if isinstance(gvu__tmz, bodo.DatetimeArrayType):
            yrdcx__ulsjt = 'datetimetz'
            qztu__wcf = 'datetime64[ns]'
            if isinstance(gvu__tmz.tz, int):
                phkhv__odnic = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(gvu__tmz.tz))
            else:
                phkhv__odnic = pd.DatetimeTZDtype(tz=gvu__tmz.tz).tz
            vrqq__cqxm = {'timezone': pa.lib.tzinfo_to_string(phkhv__odnic)}
        elif isinstance(gvu__tmz, types.Array) or gvu__tmz == boolean_array:
            yrdcx__ulsjt = qztu__wcf = gvu__tmz.dtype.name
            if qztu__wcf.startswith('datetime'):
                yrdcx__ulsjt = 'datetime'
        elif is_str_arr_type(gvu__tmz):
            yrdcx__ulsjt = 'unicode'
            qztu__wcf = 'object'
        elif gvu__tmz == binary_array_type:
            yrdcx__ulsjt = 'bytes'
            qztu__wcf = 'object'
        elif isinstance(gvu__tmz, DecimalArrayType):
            yrdcx__ulsjt = qztu__wcf = 'object'
        elif isinstance(gvu__tmz, IntegerArrayType):
            tzvpj__ipiz = gvu__tmz.dtype.name
            if tzvpj__ipiz.startswith('int'):
                yrdcx__ulsjt = 'Int' + tzvpj__ipiz[3:]
            elif tzvpj__ipiz.startswith('uint'):
                yrdcx__ulsjt = 'UInt' + tzvpj__ipiz[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, gvu__tmz))
            qztu__wcf = gvu__tmz.dtype.name
        elif gvu__tmz == datetime_date_array_type:
            yrdcx__ulsjt = 'datetime'
            qztu__wcf = 'object'
        elif isinstance(gvu__tmz, (StructArrayType, ArrayItemArrayType)):
            yrdcx__ulsjt = 'object'
            qztu__wcf = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, gvu__tmz))
        cbp__zpui = {'name': col_name, 'field_name': col_name,
            'pandas_type': yrdcx__ulsjt, 'numpy_type': qztu__wcf,
            'metadata': vrqq__cqxm}
        syws__jskd['columns'].append(cbp__zpui)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            tlyeh__bqxd = '__index_level_0__'
            fqm__axtf = None
        else:
            tlyeh__bqxd = '%s'
            fqm__axtf = '%s'
        syws__jskd['index_columns'] = [tlyeh__bqxd]
        syws__jskd['columns'].append({'name': fqm__axtf, 'field_name':
            tlyeh__bqxd, 'pandas_type': index.pandas_type_name,
            'numpy_type': index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        syws__jskd['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        syws__jskd['index_columns'] = []
    syws__jskd['pandas_version'] = pd.__version__
    return syws__jskd


@overload_method(DataFrameType, 'to_parquet', no_unliteral=True)
def to_parquet_overload(df, path, engine='auto', compression='snappy',
    index=None, partition_cols=None, storage_options=None, row_group_size=-
    1, _bodo_file_prefix='part-', _is_parallel=False):
    check_unsupported_args('DataFrame.to_parquet', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if df.has_runtime_cols and not is_overload_none(partition_cols):
        raise BodoError(
            f"DataFrame.to_parquet(): Providing 'partition_cols' on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information."
            )
    if not is_overload_none(engine) and get_overload_const_str(engine) not in (
        'auto', 'pyarrow'):
        raise BodoError('DataFrame.to_parquet(): only pyarrow engine supported'
            )
    if not is_overload_none(compression) and get_overload_const_str(compression
        ) not in {'snappy', 'gzip', 'brotli'}:
        raise BodoError('to_parquet(): Unsupported compression: ' + str(
            get_overload_const_str(compression)))
    if not is_overload_none(partition_cols):
        partition_cols = get_overload_const_list(partition_cols)
        ein__kywv = []
        for hweyq__iyxdv in partition_cols:
            try:
                idx = df.columns.index(hweyq__iyxdv)
            except ValueError as qaw__dcsdu:
                raise BodoError(
                    f'Partition column {hweyq__iyxdv} is not in dataframe')
            ein__kywv.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    wdvk__mjt = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType)
    aiu__owb = df.index is not None and (is_overload_true(_is_parallel) or 
        not is_overload_true(_is_parallel) and not wdvk__mjt)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not wdvk__mjt or is_overload_true
        (_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and wdvk__mjt and not is_overload_true(_is_parallel)
    if df.has_runtime_cols:
        if isinstance(df.runtime_colname_typ, MultiIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): Not supported with MultiIndex runtime column names. Please return the DataFrame to regular Python to update typing information.'
                )
        if not isinstance(df.runtime_colname_typ, bodo.hiframes.
            pd_index_ext.StringIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): parquet must have string column names. Please return the DataFrame with runtime column names to regular Python to modify column names.'
                )
        zop__pjl = df.runtime_data_types
        bji__gzf = len(zop__pjl)
        vrqq__cqxm = gen_pandas_parquet_metadata([''] * bji__gzf, zop__pjl,
            df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        ynq__wcsb = vrqq__cqxm['columns'][:bji__gzf]
        vrqq__cqxm['columns'] = vrqq__cqxm['columns'][bji__gzf:]
        ynq__wcsb = [json.dumps(nhk__fcyh).replace('""', '{0}') for
            nhk__fcyh in ynq__wcsb]
        eujm__duebc = json.dumps(vrqq__cqxm)
        kytoy__glt = '"columns": ['
        yvtic__clhnr = eujm__duebc.find(kytoy__glt)
        if yvtic__clhnr == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        pppy__vlxm = yvtic__clhnr + len(kytoy__glt)
        taj__wwohu = eujm__duebc[:pppy__vlxm]
        eujm__duebc = eujm__duebc[pppy__vlxm:]
        kmom__kfp = len(vrqq__cqxm['columns'])
    else:
        eujm__duebc = json.dumps(gen_pandas_parquet_metadata(df.columns, df
            .data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and wdvk__mjt:
        eujm__duebc = eujm__duebc.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            eujm__duebc = eujm__duebc.replace('"%s"', '%s')
    if not df.is_table_format:
        bnlnu__hng = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    phi__ykp = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        phi__ykp += '    py_table = get_dataframe_table(df)\n'
        phi__ykp += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        phi__ykp += '    info_list = [{}]\n'.format(bnlnu__hng)
        phi__ykp += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        phi__ykp += '    columns_index = get_dataframe_column_names(df)\n'
        phi__ykp += '    names_arr = index_to_array(columns_index)\n'
        phi__ykp += '    col_names = array_to_info(names_arr)\n'
    else:
        phi__ykp += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and aiu__owb:
        phi__ykp += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        eqn__zzvg = True
    else:
        phi__ykp += '    index_col = array_to_info(np.empty(0))\n'
        eqn__zzvg = False
    if df.has_runtime_cols:
        phi__ykp += '    columns_lst = []\n'
        phi__ykp += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            phi__ykp += f'    for _ in range(len(py_table.block_{i})):\n'
            phi__ykp += f"""        columns_lst.append({ynq__wcsb[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            phi__ykp += '        num_cols += 1\n'
        if kmom__kfp:
            phi__ykp += "    columns_lst.append('')\n"
        phi__ykp += '    columns_str = ", ".join(columns_lst)\n'
        phi__ykp += ('    metadata = """' + taj__wwohu +
            '""" + columns_str + """' + eujm__duebc + '"""\n')
    else:
        phi__ykp += '    metadata = """' + eujm__duebc + '"""\n'
    phi__ykp += '    if compression is None:\n'
    phi__ykp += "        compression = 'none'\n"
    phi__ykp += '    if df.index.name is not None:\n'
    phi__ykp += '        name_ptr = df.index.name\n'
    phi__ykp += '    else:\n'
    phi__ykp += "        name_ptr = 'null'\n"
    phi__ykp += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    xkto__qph = None
    if partition_cols:
        xkto__qph = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        lfi__ghc = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in ein__kywv)
        if lfi__ghc:
            phi__ykp += '    cat_info_list = [{}]\n'.format(lfi__ghc)
            phi__ykp += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            phi__ykp += '    cat_table = table\n'
        phi__ykp += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        phi__ykp += (
            f'    part_cols_idxs = np.array({ein__kywv}, dtype=np.int32)\n')
        phi__ykp += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        phi__ykp += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        phi__ykp += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        phi__ykp += (
            '                            unicode_to_utf8(compression),\n')
        phi__ykp += '                            _is_parallel,\n'
        phi__ykp += (
            '                            unicode_to_utf8(bucket_region),\n')
        phi__ykp += '                            row_group_size,\n'
        phi__ykp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        phi__ykp += '    delete_table_decref_arrays(table)\n'
        phi__ykp += '    delete_info_decref_array(index_col)\n'
        phi__ykp += '    delete_info_decref_array(col_names_no_partitions)\n'
        phi__ykp += '    delete_info_decref_array(col_names)\n'
        if lfi__ghc:
            phi__ykp += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        phi__ykp += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        phi__ykp += (
            '                            table, col_names, index_col,\n')
        phi__ykp += '                            ' + str(eqn__zzvg) + ',\n'
        phi__ykp += '                            unicode_to_utf8(metadata),\n'
        phi__ykp += (
            '                            unicode_to_utf8(compression),\n')
        phi__ykp += (
            '                            _is_parallel, 1, df.index.start,\n')
        phi__ykp += (
            '                            df.index.stop, df.index.step,\n')
        phi__ykp += '                            unicode_to_utf8(name_ptr),\n'
        phi__ykp += (
            '                            unicode_to_utf8(bucket_region),\n')
        phi__ykp += '                            row_group_size,\n'
        phi__ykp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        phi__ykp += '    delete_table_decref_arrays(table)\n'
        phi__ykp += '    delete_info_decref_array(index_col)\n'
        phi__ykp += '    delete_info_decref_array(col_names)\n'
    else:
        phi__ykp += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        phi__ykp += (
            '                            table, col_names, index_col,\n')
        phi__ykp += '                            ' + str(eqn__zzvg) + ',\n'
        phi__ykp += '                            unicode_to_utf8(metadata),\n'
        phi__ykp += (
            '                            unicode_to_utf8(compression),\n')
        phi__ykp += '                            _is_parallel, 0, 0, 0, 0,\n'
        phi__ykp += '                            unicode_to_utf8(name_ptr),\n'
        phi__ykp += (
            '                            unicode_to_utf8(bucket_region),\n')
        phi__ykp += '                            row_group_size,\n'
        phi__ykp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        phi__ykp += '    delete_table_decref_arrays(table)\n'
        phi__ykp += '    delete_info_decref_array(index_col)\n'
        phi__ykp += '    delete_info_decref_array(col_names)\n'
    allr__ezp = {}
    if df.has_runtime_cols:
        cgwrz__ypy = None
    else:
        for jos__aizy in df.columns:
            if not isinstance(jos__aizy, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        cgwrz__ypy = pd.array(df.columns)
    exec(phi__ykp, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': cgwrz__ypy,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': xkto__qph, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, allr__ezp)
    pzifr__rrkr = allr__ezp['df_to_parquet']
    return pzifr__rrkr


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    qtl__reeu = 'all_ok'
    nxwo__yeyrr, sdnx__lnxms = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        ouw__nwx = 100
        if chunksize is None:
            nae__ocl = ouw__nwx
        else:
            nae__ocl = min(chunksize, ouw__nwx)
        if _is_table_create:
            df = df.iloc[:nae__ocl, :]
        else:
            df = df.iloc[nae__ocl:, :]
            if len(df) == 0:
                return qtl__reeu
    ejk__jmu = df.columns
    try:
        if nxwo__yeyrr == 'snowflake':
            if sdnx__lnxms and con.count(sdnx__lnxms) == 1:
                con = con.replace(sdnx__lnxms, quote(sdnx__lnxms))
            try:
                from snowflake.connector.pandas_tools import pd_writer
                from bodo import snowflake_sqlalchemy_compat
                if method is not None and _is_table_create and bodo.get_rank(
                    ) == 0:
                    import warnings
                    from bodo.utils.typing import BodoWarning
                    warnings.warn(BodoWarning(
                        'DataFrame.to_sql(): method argument is not supported with Snowflake. Bodo always uses snowflake.connector.pandas_tools.pd_writer to write data.'
                        ))
                method = pd_writer
                df.columns = [(yzsr__duzs.upper() if yzsr__duzs.islower() else
                    yzsr__duzs) for yzsr__duzs in df.columns]
            except ImportError as qaw__dcsdu:
                qtl__reeu = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return qtl__reeu
        if nxwo__yeyrr == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            wjmj__ncl = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            umb__nekfj = bodo.typeof(df)
            xqq__ezxkp = {}
            for yzsr__duzs, sqd__vcld in zip(umb__nekfj.columns, umb__nekfj
                .data):
                if df[yzsr__duzs].dtype == 'object':
                    if sqd__vcld == datetime_date_array_type:
                        xqq__ezxkp[yzsr__duzs] = sa.types.Date
                    elif sqd__vcld in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not wjmj__ncl or wjmj__ncl ==
                        '0'):
                        xqq__ezxkp[yzsr__duzs] = VARCHAR2(4000)
            dtype = xqq__ezxkp
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as qdg__nhr:
            qtl__reeu = qdg__nhr.args[0]
            if nxwo__yeyrr == 'oracle' and 'ORA-12899' in qtl__reeu:
                qtl__reeu += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return qtl__reeu
    finally:
        df.columns = ejk__jmu


@numba.njit
def to_sql_exception_guard_encaps(df, name, con, schema=None, if_exists=
    'fail', index=True, index_label=None, chunksize=None, dtype=None,
    method=None, _is_table_create=False, _is_parallel=False):
    with numba.objmode(out='unicode_type'):
        out = to_sql_exception_guard(df, name, con, schema, if_exists,
            index, index_label, chunksize, dtype, method, _is_table_create,
            _is_parallel)
    return out


@overload_method(DataFrameType, 'to_sql')
def to_sql_overload(df, name, con, schema=None, if_exists='fail', index=
    True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_parallel=False):
    import warnings
    check_runtime_cols_unsupported(df, 'DataFrame.to_sql()')
    df: DataFrameType = df
    if is_overload_none(schema):
        if bodo.get_rank() == 0:
            import warnings
            warnings.warn(BodoWarning(
                f'DataFrame.to_sql(): schema argument is recommended to avoid permission issues when writing the table.'
                ))
    if not (is_overload_none(chunksize) or isinstance(chunksize, types.Integer)
        ):
        raise BodoError(
            "DataFrame.to_sql(): 'chunksize' argument must be an integer if provided."
            )
    phi__ykp = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    phi__ykp += f"    if con.startswith('iceberg'):\n"
    phi__ykp += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    phi__ykp += f'        if schema is None:\n'
    phi__ykp += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    phi__ykp += f'        if chunksize is not None:\n'
    phi__ykp += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    phi__ykp += f'        if index and bodo.get_rank() == 0:\n'
    phi__ykp += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    phi__ykp += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    phi__ykp += (
        f"            warnings.warn('index_label is not supported for Iceberg tables.')\n"
        )
    if df.is_table_format:
        phi__ykp += f'        py_table = get_dataframe_table(df)\n'
        phi__ykp += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        bnlnu__hng = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        phi__ykp += f'        info_list = [{bnlnu__hng}]\n'
        phi__ykp += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        phi__ykp += f'        columns_index = get_dataframe_column_names(df)\n'
        phi__ykp += f'        names_arr = index_to_array(columns_index)\n'
        phi__ykp += f'        col_names = array_to_info(names_arr)\n'
    else:
        phi__ykp += f'        col_names = array_to_info(col_names_arr)\n'
    phi__ykp += """        bodo.io.iceberg.iceberg_write(
            name,
            con_str,
            schema,
            table,
            col_names,
            if_exists,
            _is_parallel,
            pyarrow_table_schema,
        )
"""
    phi__ykp += f'        delete_table_decref_arrays(table)\n'
    phi__ykp += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        cgwrz__ypy = None
    else:
        for jos__aizy in df.columns:
            if not isinstance(jos__aizy, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        cgwrz__ypy = pd.array(df.columns)
    phi__ykp += f'    else:\n'
    phi__ykp += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    phi__ykp += f"        err_msg = 'unset'\n"
    phi__ykp += f'        if rank != 0:\n'
    phi__ykp += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    phi__ykp += f'        elif rank == 0:\n'
    phi__ykp += f'            err_msg = to_sql_exception_guard_encaps(\n'
    phi__ykp += (
        f'                          df, name, con, schema, if_exists, index, index_label,\n'
        )
    phi__ykp += f'                          chunksize, dtype, method,\n'
    phi__ykp += f'                          True, _is_parallel,\n'
    phi__ykp += f'                      )\n'
    phi__ykp += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    phi__ykp += f"        if_exists = 'append'\n"
    phi__ykp += f"        if _is_parallel and err_msg == 'all_ok':\n"
    phi__ykp += f'            err_msg = to_sql_exception_guard_encaps(\n'
    phi__ykp += (
        f'                          df, name, con, schema, if_exists, index, index_label,\n'
        )
    phi__ykp += f'                          chunksize, dtype, method,\n'
    phi__ykp += f'                          False, _is_parallel,\n'
    phi__ykp += f'                      )\n'
    phi__ykp += f"        if err_msg != 'all_ok':\n"
    phi__ykp += f"            print('err_msg=', err_msg)\n"
    phi__ykp += (
        f"            raise ValueError('error in to_sql() operation')\n")
    allr__ezp = {}
    exec(phi__ykp, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_to_cpp_table':
        py_table_to_cpp_table, 'py_table_typ': df.table_type,
        'col_names_arr': cgwrz__ypy, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'delete_info_decref_array':
        delete_info_decref_array, 'arr_info_list_to_table':
        arr_info_list_to_table, 'index_to_array': index_to_array,
        'pyarrow_table_schema': bodo.io.iceberg.pyarrow_schema(df),
        'to_sql_exception_guard_encaps': to_sql_exception_guard_encaps,
        'warnings': warnings}, allr__ezp)
    _impl = allr__ezp['df_to_sql']
    return _impl


@overload_method(DataFrameType, 'to_csv', no_unliteral=True)
def to_csv_overload(df, path_or_buf=None, sep=',', na_rep='', float_format=
    None, columns=None, header=True, index=True, index_label=None, mode='w',
    encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator=None, chunksize=None, date_format=None, doublequote=
    True, escapechar=None, decimal='.', errors='strict', storage_options=
    None, _bodo_file_prefix='part-'):
    check_runtime_cols_unsupported(df, 'DataFrame.to_csv()')
    check_unsupported_args('DataFrame.to_csv', {'encoding': encoding,
        'mode': mode, 'errors': errors, 'storage_options': storage_options},
        {'encoding': None, 'mode': 'w', 'errors': 'strict',
        'storage_options': None}, package_name='pandas', module_name='IO')
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "DataFrame.to_csv(): 'path_or_buf' argument should be None or string"
            )
    if not is_overload_none(compression):
        raise BodoError(
            "DataFrame.to_csv(): 'compression' argument supports only None, which is the default in JIT code."
            )
    if is_overload_constant_str(path_or_buf):
        ezkce__uuvs = get_overload_const_str(path_or_buf)
        if ezkce__uuvs.endswith(('.gz', '.bz2', '.zip', '.xz')):
            import warnings
            from bodo.utils.typing import BodoWarning
            warnings.warn(BodoWarning(
                "DataFrame.to_csv(): 'compression' argument defaults to None in JIT code, which is the only supported value."
                ))
    if not (is_overload_none(columns) or isinstance(columns, (types.List,
        types.Tuple))):
        raise BodoError(
            "DataFrame.to_csv(): 'columns' argument must be list a or tuple type."
            )
    if is_overload_none(path_or_buf):

        def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=
            None, columns=None, header=True, index=True, index_label=None,
            mode='w', encoding=None, compression=None, quoting=None,
            quotechar='"', line_terminator=None, chunksize=None,
            date_format=None, doublequote=True, escapechar=None, decimal=
            '.', errors='strict', storage_options=None, _bodo_file_prefix=
            'part-'):
            with numba.objmode(D='unicode_type'):
                D = df.to_csv(path_or_buf, sep, na_rep, float_format,
                    columns, header, index, index_label, mode, encoding,
                    compression, quoting, quotechar, line_terminator,
                    chunksize, date_format, doublequote, escapechar,
                    decimal, errors, storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=None,
        columns=None, header=True, index=True, index_label=None, mode='w',
        encoding=None, compression=None, quoting=None, quotechar='"',
        line_terminator=None, chunksize=None, date_format=None, doublequote
        =True, escapechar=None, decimal='.', errors='strict',
        storage_options=None, _bodo_file_prefix='part-'):
        with numba.objmode(D='unicode_type'):
            D = df.to_csv(None, sep, na_rep, float_format, columns, header,
                index, index_label, mode, encoding, compression, quoting,
                quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors, storage_options)
        bodo.io.fs_io.csv_write(path_or_buf, D, _bodo_file_prefix)
    return _impl


@overload_method(DataFrameType, 'to_json', no_unliteral=True)
def to_json_overload(df, path_or_buf=None, orient='records', date_format=
    None, double_precision=10, force_ascii=True, date_unit='ms',
    default_handler=None, lines=True, compression='infer', index=True,
    indent=None, storage_options=None, _bodo_file_prefix='part-'):
    check_runtime_cols_unsupported(df, 'DataFrame.to_json()')
    check_unsupported_args('DataFrame.to_json', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if path_or_buf is None or path_or_buf == types.none:

        def _impl(df, path_or_buf=None, orient='records', date_format=None,
            double_precision=10, force_ascii=True, date_unit='ms',
            default_handler=None, lines=True, compression='infer', index=
            True, indent=None, storage_options=None, _bodo_file_prefix='part-'
            ):
            with numba.objmode(D='unicode_type'):
                D = df.to_json(path_or_buf, orient, date_format,
                    double_precision, force_ascii, date_unit,
                    default_handler, lines, compression, index, indent,
                    storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, orient='records', date_format=None,
        double_precision=10, force_ascii=True, date_unit='ms',
        default_handler=None, lines=True, compression='infer', index=True,
        indent=None, storage_options=None, _bodo_file_prefix='part-'):
        with numba.objmode(D='unicode_type'):
            D = df.to_json(None, orient, date_format, double_precision,
                force_ascii, date_unit, default_handler, lines, compression,
                index, indent, storage_options)
        gjx__xkv = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(gjx__xkv), unicode_to_utf8(_bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(gjx__xkv), unicode_to_utf8(_bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    bnob__uhl = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    wcb__rcb = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', bnob__uhl, wcb__rcb,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    phi__ykp = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        xbta__ilmxr = data.data.dtype.categories
        phi__ykp += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        xbta__ilmxr = data.dtype.categories
        phi__ykp += '  data_values = data\n'
    jof__lzo = len(xbta__ilmxr)
    phi__ykp += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    phi__ykp += '  numba.parfors.parfor.init_prange()\n'
    phi__ykp += '  n = len(data_values)\n'
    for i in range(jof__lzo):
        phi__ykp += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    phi__ykp += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    phi__ykp += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for iext__mqmg in range(jof__lzo):
        phi__ykp += '          data_arr_{}[i] = 0\n'.format(iext__mqmg)
    phi__ykp += '      else:\n'
    for tor__qds in range(jof__lzo):
        phi__ykp += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            tor__qds)
    bnlnu__hng = ', '.join(f'data_arr_{i}' for i in range(jof__lzo))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(xbta__ilmxr[0], np.datetime64):
        xbta__ilmxr = tuple(pd.Timestamp(yzsr__duzs) for yzsr__duzs in
            xbta__ilmxr)
    elif isinstance(xbta__ilmxr[0], np.timedelta64):
        xbta__ilmxr = tuple(pd.Timedelta(yzsr__duzs) for yzsr__duzs in
            xbta__ilmxr)
    return bodo.hiframes.dataframe_impl._gen_init_df(phi__ykp, xbta__ilmxr,
        bnlnu__hng, index)


def categorical_can_construct_dataframe(val):
    if isinstance(val, CategoricalArrayType):
        return val.dtype.categories is not None
    elif isinstance(val, SeriesType) and isinstance(val.data,
        CategoricalArrayType):
        return val.data.dtype.categories is not None
    return False


def handle_inplace_df_type_change(inplace, _bodo_transformed, func_name):
    if is_overload_false(_bodo_transformed
        ) and bodo.transforms.typing_pass.in_partial_typing and (
        is_overload_true(inplace) or not is_overload_constant_bool(inplace)):
        bodo.transforms.typing_pass.typing_transform_required = True
        raise Exception('DataFrame.{}(): transform necessary for inplace'.
            format(func_name))


pd_unsupported = (pd.read_pickle, pd.read_table, pd.read_fwf, pd.
    read_clipboard, pd.ExcelFile, pd.read_html, pd.read_xml, pd.read_hdf,
    pd.read_feather, pd.read_orc, pd.read_sas, pd.read_spss, pd.
    read_sql_query, pd.read_gbq, pd.read_stata, pd.ExcelWriter, pd.
    json_normalize, pd.merge_ordered, pd.factorize, pd.wide_to_long, pd.
    bdate_range, pd.period_range, pd.infer_freq, pd.interval_range, pd.eval,
    pd.test, pd.Grouper)
pd_util_unsupported = pd.util.hash_array, pd.util.hash_pandas_object
dataframe_unsupported = ['set_flags', 'convert_dtypes', 'bool', '__iter__',
    'items', 'iteritems', 'keys', 'iterrows', 'lookup', 'pop', 'xs', 'get',
    'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow', 'dot',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'lt', 'gt', 'le', 'ge', 'ne', 'eq', 'combine', 'combine_first',
    'subtract', 'divide', 'multiply', 'applymap', 'agg', 'aggregate',
    'transform', 'expanding', 'ewm', 'all', 'any', 'clip', 'corrwith',
    'cummax', 'cummin', 'eval', 'kurt', 'kurtosis', 'mad', 'mode', 'round',
    'sem', 'skew', 'value_counts', 'add_prefix', 'add_suffix', 'align',
    'at_time', 'between_time', 'equals', 'reindex', 'reindex_like',
    'rename_axis', 'set_axis', 'truncate', 'backfill', 'bfill', 'ffill',
    'interpolate', 'pad', 'droplevel', 'reorder_levels', 'nlargest',
    'nsmallest', 'swaplevel', 'stack', 'unstack', 'swapaxes', 'squeeze',
    'to_xarray', 'T', 'transpose', 'compare', 'update', 'asfreq', 'asof',
    'slice_shift', 'tshift', 'first_valid_index', 'last_valid_index',
    'resample', 'to_period', 'to_timestamp', 'tz_convert', 'tz_localize',
    'boxplot', 'hist', 'from_dict', 'from_records', 'to_pickle', 'to_hdf',
    'to_dict', 'to_excel', 'to_html', 'to_feather', 'to_latex', 'to_stata',
    'to_gbq', 'to_records', 'to_clipboard', 'to_markdown', 'to_xml']
dataframe_unsupported_attrs = ['at', 'attrs', 'axes', 'flags', 'style',
    'sparse']


def _install_pd_unsupported(mod_name, pd_unsupported):
    for spq__pttg in pd_unsupported:
        wesev__fle = mod_name + '.' + spq__pttg.__name__
        overload(spq__pttg, no_unliteral=True)(create_unsupported_overload(
            wesev__fle))


def _install_dataframe_unsupported():
    for khbd__shzee in dataframe_unsupported_attrs:
        snmu__iymcr = 'DataFrame.' + khbd__shzee
        overload_attribute(DataFrameType, khbd__shzee)(
            create_unsupported_overload(snmu__iymcr))
    for wesev__fle in dataframe_unsupported:
        snmu__iymcr = 'DataFrame.' + wesev__fle + '()'
        overload_method(DataFrameType, wesev__fle)(create_unsupported_overload
            (snmu__iymcr))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
