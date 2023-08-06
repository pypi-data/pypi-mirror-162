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
            tzjlt__rwp = f'{len(self.data)} columns of types {set(self.data)}'
            cqhf__foji = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({tzjlt__rwp}, {self.index}, {cqhf__foji}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {jvf__ufjq: i for i, jvf__ufjq in enumerate(self.columns)}

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
            hgk__hps = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            data = tuple(sejv__qgduu.unify(typingctx, dnzf__taqbb) if 
                sejv__qgduu != dnzf__taqbb else sejv__qgduu for sejv__qgduu,
                dnzf__taqbb in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if hgk__hps is not None and None not in data:
                return DataFrameType(data, hgk__hps, self.columns, dist,
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
        return all(sejv__qgduu.is_precise() for sejv__qgduu in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        ipqlx__owqp = self.columns.index(col_name)
        mmkoi__yjpl = tuple(list(self.data[:ipqlx__owqp]) + [new_type] +
            list(self.data[ipqlx__owqp + 1:]))
        return DataFrameType(mmkoi__yjpl, self.index, self.columns, self.
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
        uzov__qwir = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            uzov__qwir.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, uzov__qwir)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        uzov__qwir = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, uzov__qwir)


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
        cntrh__xjhhm = 'n',
        escq__hmmt = {'n': 5}
        rcz__ahhbp, szb__zojxv = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, cntrh__xjhhm, escq__hmmt)
        jtruj__fkt = szb__zojxv[0]
        if not is_overload_int(jtruj__fkt):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        pat__pqicc = df.copy()
        return pat__pqicc(*szb__zojxv).replace(pysig=rcz__ahhbp)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        yst__iax = (df,) + args
        cntrh__xjhhm = 'df', 'method', 'min_periods'
        escq__hmmt = {'method': 'pearson', 'min_periods': 1}
        oowt__ckqx = 'method',
        rcz__ahhbp, szb__zojxv = bodo.utils.typing.fold_typing_args(func_name,
            yst__iax, kws, cntrh__xjhhm, escq__hmmt, oowt__ckqx)
        ozv__ltoog = szb__zojxv[2]
        if not is_overload_int(ozv__ltoog):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        qyl__eqtc = []
        ppiue__dclo = []
        for jvf__ufjq, fcwi__outyj in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(fcwi__outyj.dtype):
                qyl__eqtc.append(jvf__ufjq)
                ppiue__dclo.append(types.Array(types.float64, 1, 'A'))
        if len(qyl__eqtc) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        ppiue__dclo = tuple(ppiue__dclo)
        qyl__eqtc = tuple(qyl__eqtc)
        index_typ = bodo.utils.typing.type_col_to_index(qyl__eqtc)
        pat__pqicc = DataFrameType(ppiue__dclo, index_typ, qyl__eqtc)
        return pat__pqicc(*szb__zojxv).replace(pysig=rcz__ahhbp)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        pkltg__nxtk = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        uwg__xwaaw = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        jpj__gkp = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        jqyev__wel = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        cwplt__rkffq = dict(raw=uwg__xwaaw, result_type=jpj__gkp)
        ngdly__mciuh = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', cwplt__rkffq,
            ngdly__mciuh, package_name='pandas', module_name='DataFrame')
        xhfit__apc = True
        if types.unliteral(pkltg__nxtk) == types.unicode_type:
            if not is_overload_constant_str(pkltg__nxtk):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            xhfit__apc = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        aswdd__joqre = get_overload_const_int(axis)
        if xhfit__apc and aswdd__joqre != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif aswdd__joqre not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        xacyy__yrdb = []
        for arr_typ in df.data:
            wmoxn__lva = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            dqpa__xvldx = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(wmoxn__lva), types.int64), {}
                ).return_type
            xacyy__yrdb.append(dqpa__xvldx)
        qunn__qgoi = types.none
        wfgy__nkelc = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(jvf__ufjq) for jvf__ufjq in df.columns)), None)
        zmhc__qhk = types.BaseTuple.from_types(xacyy__yrdb)
        nntk__inho = types.Tuple([types.bool_] * len(zmhc__qhk))
        azw__wxtkz = bodo.NullableTupleType(zmhc__qhk, nntk__inho)
        cblpe__qoh = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if cblpe__qoh == types.NPDatetime('ns'):
            cblpe__qoh = bodo.pd_timestamp_type
        if cblpe__qoh == types.NPTimedelta('ns'):
            cblpe__qoh = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(zmhc__qhk):
            kkoik__qfpxe = HeterogeneousSeriesType(azw__wxtkz, wfgy__nkelc,
                cblpe__qoh)
        else:
            kkoik__qfpxe = SeriesType(zmhc__qhk.dtype, azw__wxtkz,
                wfgy__nkelc, cblpe__qoh)
        pkdcp__rzuxq = kkoik__qfpxe,
        if jqyev__wel is not None:
            pkdcp__rzuxq += tuple(jqyev__wel.types)
        try:
            if not xhfit__apc:
                rdrbg__xhky = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(pkltg__nxtk), self.context,
                    'DataFrame.apply', axis if aswdd__joqre == 1 else None)
            else:
                rdrbg__xhky = get_const_func_output_type(pkltg__nxtk,
                    pkdcp__rzuxq, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as fxqk__hyudm:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                fxqk__hyudm))
        if xhfit__apc:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(rdrbg__xhky, (SeriesType, HeterogeneousSeriesType)
                ) and rdrbg__xhky.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(rdrbg__xhky, HeterogeneousSeriesType):
                colqq__qwl, vjie__yuq = rdrbg__xhky.const_info
                if isinstance(rdrbg__xhky.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    bxj__gnor = rdrbg__xhky.data.tuple_typ.types
                elif isinstance(rdrbg__xhky.data, types.Tuple):
                    bxj__gnor = rdrbg__xhky.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                ekezl__emtm = tuple(to_nullable_type(dtype_to_array_type(
                    biwfn__omip)) for biwfn__omip in bxj__gnor)
                hmw__vhaw = DataFrameType(ekezl__emtm, df.index, vjie__yuq)
            elif isinstance(rdrbg__xhky, SeriesType):
                mjk__mpww, vjie__yuq = rdrbg__xhky.const_info
                ekezl__emtm = tuple(to_nullable_type(dtype_to_array_type(
                    rdrbg__xhky.dtype)) for colqq__qwl in range(mjk__mpww))
                hmw__vhaw = DataFrameType(ekezl__emtm, df.index, vjie__yuq)
            else:
                sdba__iuuhk = get_udf_out_arr_type(rdrbg__xhky)
                hmw__vhaw = SeriesType(sdba__iuuhk.dtype, sdba__iuuhk, df.
                    index, None)
        else:
            hmw__vhaw = rdrbg__xhky
        ngxu__bnuu = ', '.join("{} = ''".format(sejv__qgduu) for
            sejv__qgduu in kws.keys())
        aexk__ghssp = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {ngxu__bnuu}):
"""
        aexk__ghssp += '    pass\n'
        hqh__jubq = {}
        exec(aexk__ghssp, {}, hqh__jubq)
        dmwod__dyftx = hqh__jubq['apply_stub']
        rcz__ahhbp = numba.core.utils.pysignature(dmwod__dyftx)
        nub__cazl = (pkltg__nxtk, axis, uwg__xwaaw, jpj__gkp, jqyev__wel
            ) + tuple(kws.values())
        return signature(hmw__vhaw, *nub__cazl).replace(pysig=rcz__ahhbp)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        cntrh__xjhhm = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        escq__hmmt = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        oowt__ckqx = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        rcz__ahhbp, szb__zojxv = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, cntrh__xjhhm, escq__hmmt, oowt__ckqx)
        rjr__phm = szb__zojxv[2]
        if not is_overload_constant_str(rjr__phm):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        nzsp__hto = szb__zojxv[0]
        if not is_overload_none(nzsp__hto) and not (is_overload_int(
            nzsp__hto) or is_overload_constant_str(nzsp__hto)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(nzsp__hto):
            ivd__ugs = get_overload_const_str(nzsp__hto)
            if ivd__ugs not in df.columns:
                raise BodoError(f'{func_name}: {ivd__ugs} column not found.')
        elif is_overload_int(nzsp__hto):
            zpzg__spuw = get_overload_const_int(nzsp__hto)
            if zpzg__spuw > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {zpzg__spuw} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            nzsp__hto = df.columns[nzsp__hto]
        jsyh__livc = szb__zojxv[1]
        if not is_overload_none(jsyh__livc) and not (is_overload_int(
            jsyh__livc) or is_overload_constant_str(jsyh__livc)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(jsyh__livc):
            yvrf__tbj = get_overload_const_str(jsyh__livc)
            if yvrf__tbj not in df.columns:
                raise BodoError(f'{func_name}: {yvrf__tbj} column not found.')
        elif is_overload_int(jsyh__livc):
            vvy__hdsj = get_overload_const_int(jsyh__livc)
            if vvy__hdsj > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {vvy__hdsj} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            jsyh__livc = df.columns[jsyh__livc]
        bsqg__oig = szb__zojxv[3]
        if not is_overload_none(bsqg__oig) and not is_tuple_like_type(bsqg__oig
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        jkkbw__nalr = szb__zojxv[10]
        if not is_overload_none(jkkbw__nalr) and not is_overload_constant_str(
            jkkbw__nalr):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        zkul__xvmd = szb__zojxv[12]
        if not is_overload_bool(zkul__xvmd):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        ylsew__cecik = szb__zojxv[17]
        if not is_overload_none(ylsew__cecik) and not is_tuple_like_type(
            ylsew__cecik):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        awrvq__xkivw = szb__zojxv[18]
        if not is_overload_none(awrvq__xkivw) and not is_tuple_like_type(
            awrvq__xkivw):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        mdsdd__gibl = szb__zojxv[22]
        if not is_overload_none(mdsdd__gibl) and not is_overload_int(
            mdsdd__gibl):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        gyval__ignmo = szb__zojxv[29]
        if not is_overload_none(gyval__ignmo) and not is_overload_constant_str(
            gyval__ignmo):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        dmbr__sdyj = szb__zojxv[30]
        if not is_overload_none(dmbr__sdyj) and not is_overload_constant_str(
            dmbr__sdyj):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        wcy__nyxx = types.List(types.mpl_line_2d_type)
        rjr__phm = get_overload_const_str(rjr__phm)
        if rjr__phm == 'scatter':
            if is_overload_none(nzsp__hto) and is_overload_none(jsyh__livc):
                raise BodoError(
                    f'{func_name}: {rjr__phm} requires an x and y column.')
            elif is_overload_none(nzsp__hto):
                raise BodoError(f'{func_name}: {rjr__phm} x column is missing.'
                    )
            elif is_overload_none(jsyh__livc):
                raise BodoError(f'{func_name}: {rjr__phm} y column is missing.'
                    )
            wcy__nyxx = types.mpl_path_collection_type
        elif rjr__phm != 'line':
            raise BodoError(f'{func_name}: {rjr__phm} plot is not supported.')
        return signature(wcy__nyxx, *szb__zojxv).replace(pysig=rcz__ahhbp)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            swbmg__hhc = df.columns.index(attr)
            arr_typ = df.data[swbmg__hhc]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            vws__eht = []
            mmkoi__yjpl = []
            ncp__ozsoa = False
            for i, bvo__rbku in enumerate(df.columns):
                if bvo__rbku[0] != attr:
                    continue
                ncp__ozsoa = True
                vws__eht.append(bvo__rbku[1] if len(bvo__rbku) == 2 else
                    bvo__rbku[1:])
                mmkoi__yjpl.append(df.data[i])
            if ncp__ozsoa:
                return DataFrameType(tuple(mmkoi__yjpl), df.index, tuple(
                    vws__eht))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        dim__oxxj = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(dim__oxxj)
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
        xonr__thml = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], xonr__thml)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    jcycw__bim = builder.module
    hffyz__pvc = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gtp__nvhk = cgutils.get_or_insert_function(jcycw__bim, hffyz__pvc, name
        ='.dtor.df.{}'.format(df_type))
    if not gtp__nvhk.is_declaration:
        return gtp__nvhk
    gtp__nvhk.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gtp__nvhk.append_basic_block())
    mcl__amaon = gtp__nvhk.args[0]
    cir__eyehy = context.get_value_type(payload_type).as_pointer()
    llzz__zeb = builder.bitcast(mcl__amaon, cir__eyehy)
    payload = context.make_helper(builder, payload_type, ref=llzz__zeb)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        vczi__qhwmk = context.get_python_api(builder)
        wodkb__fsm = vczi__qhwmk.gil_ensure()
        vczi__qhwmk.decref(payload.parent)
        vczi__qhwmk.gil_release(wodkb__fsm)
    builder.ret_void()
    return gtp__nvhk


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    hzf__mxy = cgutils.create_struct_proxy(payload_type)(context, builder)
    hzf__mxy.data = data_tup
    hzf__mxy.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        hzf__mxy.columns = colnames
    tnzm__tjct = context.get_value_type(payload_type)
    ibfxe__ehe = context.get_abi_sizeof(tnzm__tjct)
    ogrk__oxw = define_df_dtor(context, builder, df_type, payload_type)
    dpb__slj = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, ibfxe__ehe), ogrk__oxw)
    ivlxz__hlxiv = context.nrt.meminfo_data(builder, dpb__slj)
    lyavp__lrms = builder.bitcast(ivlxz__hlxiv, tnzm__tjct.as_pointer())
    vcnin__atvv = cgutils.create_struct_proxy(df_type)(context, builder)
    vcnin__atvv.meminfo = dpb__slj
    if parent is None:
        vcnin__atvv.parent = cgutils.get_null_value(vcnin__atvv.parent.type)
    else:
        vcnin__atvv.parent = parent
        hzf__mxy.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            vczi__qhwmk = context.get_python_api(builder)
            wodkb__fsm = vczi__qhwmk.gil_ensure()
            vczi__qhwmk.incref(parent)
            vczi__qhwmk.gil_release(wodkb__fsm)
    builder.store(hzf__mxy._getvalue(), lyavp__lrms)
    return vcnin__atvv._getvalue()


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
        obz__otm = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        obz__otm = [biwfn__omip for biwfn__omip in data_typ.dtype.arr_types]
    hcme__lms = DataFrameType(tuple(obz__otm + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        reali__frhgk = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return reali__frhgk
    sig = signature(hcme__lms, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    mjk__mpww = len(data_tup_typ.types)
    if mjk__mpww == 0:
        column_names = ()
    azyw__dsumb = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(azyw__dsumb, ColNamesMetaType) and isinstance(azyw__dsumb
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = azyw__dsumb.meta
    if mjk__mpww == 1 and isinstance(data_tup_typ.types[0], TableType):
        mjk__mpww = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == mjk__mpww, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    blok__dmp = data_tup_typ.types
    if mjk__mpww != 0 and isinstance(data_tup_typ.types[0], TableType):
        blok__dmp = data_tup_typ.types[0].arr_types
        is_table_format = True
    hcme__lms = DataFrameType(blok__dmp, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            hua__qik = cgutils.create_struct_proxy(hcme__lms.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = hua__qik.parent
        reali__frhgk = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return reali__frhgk
    sig = signature(hcme__lms, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        vcnin__atvv = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, vcnin__atvv.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        hzf__mxy = get_dataframe_payload(context, builder, df_typ, args[0])
        dxizs__liplp = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[dxizs__liplp]
        if df_typ.is_table_format:
            hua__qik = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(hzf__mxy.data, 0))
            ukc__oiz = df_typ.table_type.type_to_blk[arr_typ]
            nnknv__kgut = getattr(hua__qik, f'block_{ukc__oiz}')
            jrlv__qolzd = ListInstance(context, builder, types.List(arr_typ
                ), nnknv__kgut)
            wmcrj__gpifh = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[dxizs__liplp])
            xonr__thml = jrlv__qolzd.getitem(wmcrj__gpifh)
        else:
            xonr__thml = builder.extract_value(hzf__mxy.data, dxizs__liplp)
        wei__hrw = cgutils.alloca_once_value(builder, xonr__thml)
        ubk__laff = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, wei__hrw, ubk__laff)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    dpb__slj = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, dpb__slj)
    cir__eyehy = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, cir__eyehy)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    hcme__lms = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        hcme__lms = types.Tuple([TableType(df_typ.data)])
    sig = signature(hcme__lms, df_typ)

    def codegen(context, builder, signature, args):
        hzf__mxy = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            hzf__mxy.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        hzf__mxy = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, hzf__mxy.index
            )
    hcme__lms = df_typ.index
    sig = signature(hcme__lms, df_typ)
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
        pat__pqicc = df.data[i]
        return pat__pqicc(*args)


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
        hzf__mxy = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(hzf__mxy.data, 0))
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
    xob__nxysz = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{xob__nxysz})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        pat__pqicc = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return pat__pqicc(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        hzf__mxy = get_dataframe_payload(context, builder, signature.args[0
            ], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, hzf__mxy.columns)
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
    zmhc__qhk = self.typemap[data_tup.name]
    if any(is_tuple_like_type(biwfn__omip) for biwfn__omip in zmhc__qhk.types):
        return None
    if equiv_set.has_shape(data_tup):
        dagzu__vpskz = equiv_set.get_shape(data_tup)
        if len(dagzu__vpskz) > 1:
            equiv_set.insert_equiv(*dagzu__vpskz)
        if len(dagzu__vpskz) > 0:
            wfgy__nkelc = self.typemap[index.name]
            if not isinstance(wfgy__nkelc, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(dagzu__vpskz[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(dagzu__vpskz[0], len(
                dagzu__vpskz)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ixvv__mgrmp = args[0]
    data_types = self.typemap[ixvv__mgrmp.name].data
    if any(is_tuple_like_type(biwfn__omip) for biwfn__omip in data_types):
        return None
    if equiv_set.has_shape(ixvv__mgrmp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ixvv__mgrmp)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    ixvv__mgrmp = args[0]
    wfgy__nkelc = self.typemap[ixvv__mgrmp.name].index
    if isinstance(wfgy__nkelc, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(ixvv__mgrmp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ixvv__mgrmp)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ixvv__mgrmp = args[0]
    if equiv_set.has_shape(ixvv__mgrmp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ixvv__mgrmp), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ixvv__mgrmp = args[0]
    if equiv_set.has_shape(ixvv__mgrmp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            ixvv__mgrmp)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    dxizs__liplp = get_overload_const_int(c_ind_typ)
    if df_typ.data[dxizs__liplp] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        xis__sen, colqq__qwl, acw__jlde = args
        hzf__mxy = get_dataframe_payload(context, builder, df_typ, xis__sen)
        if df_typ.is_table_format:
            hua__qik = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(hzf__mxy.data, 0))
            ukc__oiz = df_typ.table_type.type_to_blk[arr_typ]
            nnknv__kgut = getattr(hua__qik, f'block_{ukc__oiz}')
            jrlv__qolzd = ListInstance(context, builder, types.List(arr_typ
                ), nnknv__kgut)
            wmcrj__gpifh = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[dxizs__liplp])
            jrlv__qolzd.setitem(wmcrj__gpifh, acw__jlde, True)
        else:
            xonr__thml = builder.extract_value(hzf__mxy.data, dxizs__liplp)
            context.nrt.decref(builder, df_typ.data[dxizs__liplp], xonr__thml)
            hzf__mxy.data = builder.insert_value(hzf__mxy.data, acw__jlde,
                dxizs__liplp)
            context.nrt.incref(builder, arr_typ, acw__jlde)
        vcnin__atvv = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=xis__sen)
        payload_type = DataFramePayloadType(df_typ)
        llzz__zeb = context.nrt.meminfo_data(builder, vcnin__atvv.meminfo)
        cir__eyehy = context.get_value_type(payload_type).as_pointer()
        llzz__zeb = builder.bitcast(llzz__zeb, cir__eyehy)
        builder.store(hzf__mxy._getvalue(), llzz__zeb)
        return impl_ret_borrowed(context, builder, df_typ, xis__sen)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        smluh__irr = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        fbj__wao = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=smluh__irr)
        edtuh__alxz = get_dataframe_payload(context, builder, df_typ,
            smluh__irr)
        vcnin__atvv = construct_dataframe(context, builder, signature.
            return_type, edtuh__alxz.data, index_val, fbj__wao.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), edtuh__alxz.data)
        return vcnin__atvv
    hcme__lms = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(hcme__lms, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    mjk__mpww = len(df_type.columns)
    eduiz__tglw = mjk__mpww
    csqc__dhwbr = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    ibuzl__vpc = col_name not in df_type.columns
    dxizs__liplp = mjk__mpww
    if ibuzl__vpc:
        csqc__dhwbr += arr_type,
        column_names += col_name,
        eduiz__tglw += 1
    else:
        dxizs__liplp = df_type.columns.index(col_name)
        csqc__dhwbr = tuple(arr_type if i == dxizs__liplp else csqc__dhwbr[
            i] for i in range(mjk__mpww))

    def codegen(context, builder, signature, args):
        xis__sen, colqq__qwl, acw__jlde = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, xis__sen)
        yshbe__fquti = cgutils.create_struct_proxy(df_type)(context,
            builder, value=xis__sen)
        if df_type.is_table_format:
            rlss__qirib = df_type.table_type
            pxwam__qdv = builder.extract_value(in_dataframe_payload.data, 0)
            sxvwm__jfydu = TableType(csqc__dhwbr)
            uhqu__wtq = set_table_data_codegen(context, builder,
                rlss__qirib, pxwam__qdv, sxvwm__jfydu, arr_type, acw__jlde,
                dxizs__liplp, ibuzl__vpc)
            data_tup = context.make_tuple(builder, types.Tuple([
                sxvwm__jfydu]), [uhqu__wtq])
        else:
            blok__dmp = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != dxizs__liplp else acw__jlde) for i in range(
                mjk__mpww)]
            if ibuzl__vpc:
                blok__dmp.append(acw__jlde)
            for ixvv__mgrmp, uinuo__cpfpq in zip(blok__dmp, csqc__dhwbr):
                context.nrt.incref(builder, uinuo__cpfpq, ixvv__mgrmp)
            data_tup = context.make_tuple(builder, types.Tuple(csqc__dhwbr),
                blok__dmp)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        vyzk__eyl = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, yshbe__fquti.parent, None)
        if not ibuzl__vpc and arr_type == df_type.data[dxizs__liplp]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            llzz__zeb = context.nrt.meminfo_data(builder, yshbe__fquti.meminfo)
            cir__eyehy = context.get_value_type(payload_type).as_pointer()
            llzz__zeb = builder.bitcast(llzz__zeb, cir__eyehy)
            lsjm__wqqz = get_dataframe_payload(context, builder, df_type,
                vyzk__eyl)
            builder.store(lsjm__wqqz._getvalue(), llzz__zeb)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, sxvwm__jfydu, builder.
                    extract_value(data_tup, 0))
            else:
                for ixvv__mgrmp, uinuo__cpfpq in zip(blok__dmp, csqc__dhwbr):
                    context.nrt.incref(builder, uinuo__cpfpq, ixvv__mgrmp)
        has_parent = cgutils.is_not_null(builder, yshbe__fquti.parent)
        with builder.if_then(has_parent):
            vczi__qhwmk = context.get_python_api(builder)
            wodkb__fsm = vczi__qhwmk.gil_ensure()
            jboa__uyjt = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, acw__jlde)
            jvf__ufjq = numba.core.pythonapi._BoxContext(context, builder,
                vczi__qhwmk, jboa__uyjt)
            apya__qqo = jvf__ufjq.pyapi.from_native_value(arr_type,
                acw__jlde, jvf__ufjq.env_manager)
            if isinstance(col_name, str):
                idog__eto = context.insert_const_string(builder.module,
                    col_name)
                oula__spu = vczi__qhwmk.string_from_string(idog__eto)
            else:
                assert isinstance(col_name, int)
                oula__spu = vczi__qhwmk.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            vczi__qhwmk.object_setitem(yshbe__fquti.parent, oula__spu,
                apya__qqo)
            vczi__qhwmk.decref(apya__qqo)
            vczi__qhwmk.decref(oula__spu)
            vczi__qhwmk.gil_release(wodkb__fsm)
        return vyzk__eyl
    hcme__lms = DataFrameType(csqc__dhwbr, index_typ, column_names, df_type
        .dist, df_type.is_table_format)
    sig = signature(hcme__lms, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    mjk__mpww = len(pyval.columns)
    blok__dmp = []
    for i in range(mjk__mpww):
        pgrpn__ugij = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            apya__qqo = pgrpn__ugij.array
        else:
            apya__qqo = pgrpn__ugij.values
        blok__dmp.append(apya__qqo)
    blok__dmp = tuple(blok__dmp)
    if df_type.is_table_format:
        hua__qik = context.get_constant_generic(builder, df_type.table_type,
            Table(blok__dmp))
        data_tup = lir.Constant.literal_struct([hua__qik])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], bvo__rbku) for i,
            bvo__rbku in enumerate(blok__dmp)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    njhkm__yckbw = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, njhkm__yckbw])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    dcmtk__lgt = context.get_constant(types.int64, -1)
    htdng__gthac = context.get_constant_null(types.voidptr)
    dpb__slj = lir.Constant.literal_struct([dcmtk__lgt, htdng__gthac,
        htdng__gthac, payload, dcmtk__lgt])
    dpb__slj = cgutils.global_constant(builder, '.const.meminfo', dpb__slj
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([dpb__slj, njhkm__yckbw])


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
        hgk__hps = context.cast(builder, in_dataframe_payload.index, fromty
            .index, toty.index)
    else:
        hgk__hps = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, hgk__hps)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        mmkoi__yjpl = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                mmkoi__yjpl)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), mmkoi__yjpl)
    elif not fromty.is_table_format and toty.is_table_format:
        mmkoi__yjpl = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        mmkoi__yjpl = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        mmkoi__yjpl = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        mmkoi__yjpl = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, mmkoi__yjpl,
        hgk__hps, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    ocspe__grtdx = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        klkrx__brnz = get_index_data_arr_types(toty.index)[0]
        ybg__adl = bodo.utils.transform.get_type_alloc_counts(klkrx__brnz) - 1
        aet__qmn = ', '.join('0' for colqq__qwl in range(ybg__adl))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(aet__qmn, ', ' if ybg__adl == 1 else ''))
        ocspe__grtdx['index_arr_type'] = klkrx__brnz
    dhas__kolb = []
    for i, arr_typ in enumerate(toty.data):
        ybg__adl = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        aet__qmn = ', '.join('0' for colqq__qwl in range(ybg__adl))
        xmutf__hil = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, aet__qmn, ', ' if ybg__adl == 1 else ''))
        dhas__kolb.append(xmutf__hil)
        ocspe__grtdx[f'arr_type{i}'] = arr_typ
    dhas__kolb = ', '.join(dhas__kolb)
    aexk__ghssp = 'def impl():\n'
    krsv__klpbq = bodo.hiframes.dataframe_impl._gen_init_df(aexk__ghssp,
        toty.columns, dhas__kolb, index, ocspe__grtdx)
    df = context.compile_internal(builder, krsv__klpbq, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    gfy__sgjqy = toty.table_type
    hua__qik = cgutils.create_struct_proxy(gfy__sgjqy)(context, builder)
    hua__qik.parent = in_dataframe_payload.parent
    for biwfn__omip, ukc__oiz in gfy__sgjqy.type_to_blk.items():
        tbdxk__ltja = context.get_constant(types.int64, len(gfy__sgjqy.
            block_to_arr_ind[ukc__oiz]))
        colqq__qwl, djto__hvp = ListInstance.allocate_ex(context, builder,
            types.List(biwfn__omip), tbdxk__ltja)
        djto__hvp.size = tbdxk__ltja
        setattr(hua__qik, f'block_{ukc__oiz}', djto__hvp.value)
    for i, biwfn__omip in enumerate(fromty.data):
        afbu__jcos = toty.data[i]
        if biwfn__omip != afbu__jcos:
            ttck__kzir = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ttck__kzir)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        xonr__thml = builder.extract_value(in_dataframe_payload.data, i)
        if biwfn__omip != afbu__jcos:
            qbo__heogw = context.cast(builder, xonr__thml, biwfn__omip,
                afbu__jcos)
            tupsp__dei = False
        else:
            qbo__heogw = xonr__thml
            tupsp__dei = True
        ukc__oiz = gfy__sgjqy.type_to_blk[biwfn__omip]
        nnknv__kgut = getattr(hua__qik, f'block_{ukc__oiz}')
        jrlv__qolzd = ListInstance(context, builder, types.List(biwfn__omip
            ), nnknv__kgut)
        wmcrj__gpifh = context.get_constant(types.int64, gfy__sgjqy.
            block_offsets[i])
        jrlv__qolzd.setitem(wmcrj__gpifh, qbo__heogw, tupsp__dei)
    data_tup = context.make_tuple(builder, types.Tuple([gfy__sgjqy]), [
        hua__qik._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    blok__dmp = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            ttck__kzir = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ttck__kzir)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            xonr__thml = builder.extract_value(in_dataframe_payload.data, i)
            qbo__heogw = context.cast(builder, xonr__thml, fromty.data[i],
                toty.data[i])
            tupsp__dei = False
        else:
            qbo__heogw = builder.extract_value(in_dataframe_payload.data, i)
            tupsp__dei = True
        if tupsp__dei:
            context.nrt.incref(builder, toty.data[i], qbo__heogw)
        blok__dmp.append(qbo__heogw)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), blok__dmp)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    rlss__qirib = fromty.table_type
    pxwam__qdv = cgutils.create_struct_proxy(rlss__qirib)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    sxvwm__jfydu = toty.table_type
    uhqu__wtq = cgutils.create_struct_proxy(sxvwm__jfydu)(context, builder)
    uhqu__wtq.parent = in_dataframe_payload.parent
    for biwfn__omip, ukc__oiz in sxvwm__jfydu.type_to_blk.items():
        tbdxk__ltja = context.get_constant(types.int64, len(sxvwm__jfydu.
            block_to_arr_ind[ukc__oiz]))
        colqq__qwl, djto__hvp = ListInstance.allocate_ex(context, builder,
            types.List(biwfn__omip), tbdxk__ltja)
        djto__hvp.size = tbdxk__ltja
        setattr(uhqu__wtq, f'block_{ukc__oiz}', djto__hvp.value)
    for i in range(len(fromty.data)):
        ybz__qala = fromty.data[i]
        afbu__jcos = toty.data[i]
        if ybz__qala != afbu__jcos:
            ttck__kzir = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ttck__kzir)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        ekcqa__ofcc = rlss__qirib.type_to_blk[ybz__qala]
        kzwxr__jirki = getattr(pxwam__qdv, f'block_{ekcqa__ofcc}')
        avddy__stad = ListInstance(context, builder, types.List(ybz__qala),
            kzwxr__jirki)
        ckzdi__rdzjl = context.get_constant(types.int64, rlss__qirib.
            block_offsets[i])
        xonr__thml = avddy__stad.getitem(ckzdi__rdzjl)
        if ybz__qala != afbu__jcos:
            qbo__heogw = context.cast(builder, xonr__thml, ybz__qala,
                afbu__jcos)
            tupsp__dei = False
        else:
            qbo__heogw = xonr__thml
            tupsp__dei = True
        bjwwh__epum = sxvwm__jfydu.type_to_blk[biwfn__omip]
        djto__hvp = getattr(uhqu__wtq, f'block_{bjwwh__epum}')
        bcgp__lkp = ListInstance(context, builder, types.List(afbu__jcos),
            djto__hvp)
        gkurl__bqv = context.get_constant(types.int64, sxvwm__jfydu.
            block_offsets[i])
        bcgp__lkp.setitem(gkurl__bqv, qbo__heogw, tupsp__dei)
    data_tup = context.make_tuple(builder, types.Tuple([sxvwm__jfydu]), [
        uhqu__wtq._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    gfy__sgjqy = fromty.table_type
    hua__qik = cgutils.create_struct_proxy(gfy__sgjqy)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    blok__dmp = []
    for i, biwfn__omip in enumerate(toty.data):
        ybz__qala = fromty.data[i]
        if biwfn__omip != ybz__qala:
            ttck__kzir = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ttck__kzir)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        ukc__oiz = gfy__sgjqy.type_to_blk[biwfn__omip]
        nnknv__kgut = getattr(hua__qik, f'block_{ukc__oiz}')
        jrlv__qolzd = ListInstance(context, builder, types.List(biwfn__omip
            ), nnknv__kgut)
        wmcrj__gpifh = context.get_constant(types.int64, gfy__sgjqy.
            block_offsets[i])
        xonr__thml = jrlv__qolzd.getitem(wmcrj__gpifh)
        if biwfn__omip != ybz__qala:
            qbo__heogw = context.cast(builder, xonr__thml, ybz__qala,
                biwfn__omip)
            tupsp__dei = False
        else:
            qbo__heogw = xonr__thml
            tupsp__dei = True
        if tupsp__dei:
            context.nrt.incref(builder, biwfn__omip, qbo__heogw)
        blok__dmp.append(qbo__heogw)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), blok__dmp)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    ehx__hun, dhas__kolb, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    rgd__mug = ColNamesMetaType(tuple(ehx__hun))
    aexk__ghssp = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    aexk__ghssp += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(dhas__kolb, index_arg))
    hqh__jubq = {}
    exec(aexk__ghssp, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': rgd__mug}, hqh__jubq)
    tem__nuys = hqh__jubq['_init_df']
    return tem__nuys


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    hcme__lms = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ
        .index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(hcme__lms, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    hcme__lms = DataFrameType(to_str_arr_if_dict_array(df_typ.data), df_typ
        .index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(hcme__lms, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    vnxh__plb = ''
    if not is_overload_none(dtype):
        vnxh__plb = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        mjk__mpww = (len(data.types) - 1) // 2
        fukg__fnsch = [biwfn__omip.literal_value for biwfn__omip in data.
            types[1:mjk__mpww + 1]]
        data_val_types = dict(zip(fukg__fnsch, data.types[mjk__mpww + 1:]))
        blok__dmp = ['data[{}]'.format(i) for i in range(mjk__mpww + 1, 2 *
            mjk__mpww + 1)]
        data_dict = dict(zip(fukg__fnsch, blok__dmp))
        if is_overload_none(index):
            for i, biwfn__omip in enumerate(data.types[mjk__mpww + 1:]):
                if isinstance(biwfn__omip, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(mjk__mpww + 1 + i))
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
        lwkah__cwrek = '.copy()' if copy else ''
        gxikd__mjevb = get_overload_const_list(columns)
        mjk__mpww = len(gxikd__mjevb)
        data_val_types = {jvf__ufjq: data.copy(ndim=1) for jvf__ufjq in
            gxikd__mjevb}
        blok__dmp = ['data[:,{}]{}'.format(i, lwkah__cwrek) for i in range(
            mjk__mpww)]
        data_dict = dict(zip(gxikd__mjevb, blok__dmp))
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
    dhas__kolb = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[jvf__ufjq], df_len, vnxh__plb) for jvf__ufjq in
        col_names))
    if len(col_names) == 0:
        dhas__kolb = '()'
    return col_names, dhas__kolb, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for jvf__ufjq in col_names:
        if jvf__ufjq in data_dict and is_iterable_type(data_val_types[
            jvf__ufjq]):
            df_len = 'len({})'.format(data_dict[jvf__ufjq])
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
    if all(jvf__ufjq in data_dict for jvf__ufjq in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    hxe__jqlnc = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for jvf__ufjq in col_names:
        if jvf__ufjq not in data_dict:
            data_dict[jvf__ufjq] = hxe__jqlnc


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
            biwfn__omip = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df
                )
            return len(biwfn__omip)
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
        khec__vvazq = idx.literal_value
        if isinstance(khec__vvazq, int):
            pat__pqicc = tup.types[khec__vvazq]
        elif isinstance(khec__vvazq, slice):
            pat__pqicc = types.BaseTuple.from_types(tup.types[khec__vvazq])
        return signature(pat__pqicc, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    abbn__wwkah, idx = sig.args
    idx = idx.literal_value
    tup, colqq__qwl = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(abbn__wwkah)
        if not 0 <= idx < len(abbn__wwkah):
            raise IndexError('cannot index at %d in %s' % (idx, abbn__wwkah))
        nvv__cvzgq = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        jiqrn__mjfl = cgutils.unpack_tuple(builder, tup)[idx]
        nvv__cvzgq = context.make_tuple(builder, sig.return_type, jiqrn__mjfl)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, nvv__cvzgq)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, uhsn__tclet, suffix_x,
            suffix_y, is_join, indicator, colqq__qwl, colqq__qwl) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        icr__ashly = {jvf__ufjq: i for i, jvf__ufjq in enumerate(left_on)}
        pqjqu__ulacy = {jvf__ufjq: i for i, jvf__ufjq in enumerate(right_on)}
        onj__vpacl = set(left_on) & set(right_on)
        mox__kfk = set(left_df.columns) & set(right_df.columns)
        fca__yes = mox__kfk - onj__vpacl
        tdu__dcani = '$_bodo_index_' in left_on
        uxech__ubsl = '$_bodo_index_' in right_on
        how = get_overload_const_str(uhsn__tclet)
        zqyly__sqd = how in {'left', 'outer'}
        xblf__aqdc = how in {'right', 'outer'}
        columns = []
        data = []
        if tdu__dcani:
            jcifr__ijqg = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            jcifr__ijqg = left_df.data[left_df.column_index[left_on[0]]]
        if uxech__ubsl:
            gtryz__olzzt = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            gtryz__olzzt = right_df.data[right_df.column_index[right_on[0]]]
        if tdu__dcani and not uxech__ubsl and not is_join.literal_value:
            lfgqd__jctwt = right_on[0]
            if lfgqd__jctwt in left_df.column_index:
                columns.append(lfgqd__jctwt)
                if (gtryz__olzzt == bodo.dict_str_arr_type and jcifr__ijqg ==
                    bodo.string_array_type):
                    zfi__qspx = bodo.string_array_type
                else:
                    zfi__qspx = gtryz__olzzt
                data.append(zfi__qspx)
        if uxech__ubsl and not tdu__dcani and not is_join.literal_value:
            ktyys__nwzj = left_on[0]
            if ktyys__nwzj in right_df.column_index:
                columns.append(ktyys__nwzj)
                if (jcifr__ijqg == bodo.dict_str_arr_type and gtryz__olzzt ==
                    bodo.string_array_type):
                    zfi__qspx = bodo.string_array_type
                else:
                    zfi__qspx = jcifr__ijqg
                data.append(zfi__qspx)
        for ybz__qala, pgrpn__ugij in zip(left_df.data, left_df.columns):
            columns.append(str(pgrpn__ugij) + suffix_x.literal_value if 
                pgrpn__ugij in fca__yes else pgrpn__ugij)
            if pgrpn__ugij in onj__vpacl:
                if ybz__qala == bodo.dict_str_arr_type:
                    ybz__qala = right_df.data[right_df.column_index[
                        pgrpn__ugij]]
                data.append(ybz__qala)
            else:
                if (ybz__qala == bodo.dict_str_arr_type and pgrpn__ugij in
                    icr__ashly):
                    if uxech__ubsl:
                        ybz__qala = gtryz__olzzt
                    else:
                        nffs__qgjxv = icr__ashly[pgrpn__ugij]
                        pzufg__qevkl = right_on[nffs__qgjxv]
                        ybz__qala = right_df.data[right_df.column_index[
                            pzufg__qevkl]]
                if xblf__aqdc:
                    ybz__qala = to_nullable_type(ybz__qala)
                data.append(ybz__qala)
        for ybz__qala, pgrpn__ugij in zip(right_df.data, right_df.columns):
            if pgrpn__ugij not in onj__vpacl:
                columns.append(str(pgrpn__ugij) + suffix_y.literal_value if
                    pgrpn__ugij in fca__yes else pgrpn__ugij)
                if (ybz__qala == bodo.dict_str_arr_type and pgrpn__ugij in
                    pqjqu__ulacy):
                    if tdu__dcani:
                        ybz__qala = jcifr__ijqg
                    else:
                        nffs__qgjxv = pqjqu__ulacy[pgrpn__ugij]
                        unqee__afxt = left_on[nffs__qgjxv]
                        ybz__qala = left_df.data[left_df.column_index[
                            unqee__afxt]]
                if zqyly__sqd:
                    ybz__qala = to_nullable_type(ybz__qala)
                data.append(ybz__qala)
        guomq__qziyt = get_overload_const_bool(indicator)
        if guomq__qziyt:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        jffm__wrwzw = False
        if tdu__dcani and uxech__ubsl and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            jffm__wrwzw = True
        elif tdu__dcani and not uxech__ubsl:
            index_typ = right_df.index
            jffm__wrwzw = True
        elif uxech__ubsl and not tdu__dcani:
            index_typ = left_df.index
            jffm__wrwzw = True
        if jffm__wrwzw and isinstance(index_typ, bodo.hiframes.pd_index_ext
            .RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        tuhw__ezcf = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(tuhw__ezcf, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    vcnin__atvv = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return vcnin__atvv._getvalue()


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
    cwplt__rkffq = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    escq__hmmt = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', cwplt__rkffq, escq__hmmt,
        package_name='pandas', module_name='General')
    aexk__ghssp = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        mfuli__qmc = 0
        dhas__kolb = []
        names = []
        for i, aib__wnqr in enumerate(objs.types):
            assert isinstance(aib__wnqr, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(aib__wnqr, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(aib__wnqr
                , 'pandas.concat()')
            if isinstance(aib__wnqr, SeriesType):
                names.append(str(mfuli__qmc))
                mfuli__qmc += 1
                dhas__kolb.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(aib__wnqr.columns)
                for awni__dgbh in range(len(aib__wnqr.data)):
                    dhas__kolb.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, awni__dgbh))
        return bodo.hiframes.dataframe_impl._gen_init_df(aexk__ghssp, names,
            ', '.join(dhas__kolb), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(biwfn__omip, DataFrameType) for biwfn__omip in
            objs.types)
        lzb__bdf = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            lzb__bdf.extend(df.columns)
        lzb__bdf = list(dict.fromkeys(lzb__bdf).keys())
        obz__otm = {}
        for mfuli__qmc, jvf__ufjq in enumerate(lzb__bdf):
            for i, df in enumerate(objs.types):
                if jvf__ufjq in df.column_index:
                    obz__otm[f'arr_typ{mfuli__qmc}'] = df.data[df.
                        column_index[jvf__ufjq]]
                    break
        assert len(obz__otm) == len(lzb__bdf)
        iur__rvn = []
        for mfuli__qmc, jvf__ufjq in enumerate(lzb__bdf):
            args = []
            for i, df in enumerate(objs.types):
                if jvf__ufjq in df.column_index:
                    dxizs__liplp = df.column_index[jvf__ufjq]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, dxizs__liplp))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, mfuli__qmc))
            aexk__ghssp += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(mfuli__qmc, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(aexk__ghssp,
            lzb__bdf, ', '.join('A{}'.format(i) for i in range(len(lzb__bdf
            ))), index, obz__otm)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(biwfn__omip, SeriesType) for biwfn__omip in
            objs.types)
        aexk__ghssp += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            aexk__ghssp += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            aexk__ghssp += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        aexk__ghssp += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        hqh__jubq = {}
        exec(aexk__ghssp, {'bodo': bodo, 'np': np, 'numba': numba}, hqh__jubq)
        return hqh__jubq['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for mfuli__qmc, jvf__ufjq in enumerate(df_type.columns):
            aexk__ghssp += '  arrs{} = []\n'.format(mfuli__qmc)
            aexk__ghssp += '  for i in range(len(objs)):\n'
            aexk__ghssp += '    df = objs[i]\n'
            aexk__ghssp += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(mfuli__qmc))
            aexk__ghssp += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(mfuli__qmc))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            aexk__ghssp += '  arrs_index = []\n'
            aexk__ghssp += '  for i in range(len(objs)):\n'
            aexk__ghssp += '    df = objs[i]\n'
            aexk__ghssp += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(aexk__ghssp,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        aexk__ghssp += '  arrs = []\n'
        aexk__ghssp += '  for i in range(len(objs)):\n'
        aexk__ghssp += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        aexk__ghssp += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            aexk__ghssp += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            aexk__ghssp += '  arrs_index = []\n'
            aexk__ghssp += '  for i in range(len(objs)):\n'
            aexk__ghssp += '    S = objs[i]\n'
            aexk__ghssp += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            aexk__ghssp += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        aexk__ghssp += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        hqh__jubq = {}
        exec(aexk__ghssp, {'bodo': bodo, 'np': np, 'numba': numba}, hqh__jubq)
        return hqh__jubq['impl']
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
        hcme__lms = df.copy(index=index)
        return signature(hcme__lms, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    obux__enu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return obux__enu._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    cwplt__rkffq = dict(index=index, name=name)
    escq__hmmt = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', cwplt__rkffq, escq__hmmt,
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
        obz__otm = (types.Array(types.int64, 1, 'C'),) + df.data
        gyeot__qxo = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, obz__otm)
        return signature(gyeot__qxo, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    obux__enu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return obux__enu._getvalue()


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
    obux__enu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return obux__enu._getvalue()


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
    obux__enu = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return obux__enu._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    is_already_shuffled=False, _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    lnc__nugwn = get_overload_const_bool(check_duplicates)
    lsfbd__httqg = not get_overload_const_bool(is_already_shuffled)
    fxyte__dmbh = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    dera__deg = len(value_names) > 1
    mjah__kzwv = None
    crn__edyxd = None
    brfnt__xgl = None
    npw__cigr = None
    ayw__nuwv = isinstance(values_tup, types.UniTuple)
    if ayw__nuwv:
        hcu__tnsoi = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        hcu__tnsoi = [to_str_arr_if_dict_array(to_nullable_type(
            uinuo__cpfpq)) for uinuo__cpfpq in values_tup]
    aexk__ghssp = 'def impl(\n'
    aexk__ghssp += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, is_already_shuffled=False, _constant_pivot_values=None, parallel=False
"""
    aexk__ghssp += '):\n'
    aexk__ghssp += (
        "    ev = tracing.Event('pivot_impl', is_parallel=parallel)\n")
    if lsfbd__httqg:
        aexk__ghssp += '    if parallel:\n'
        aexk__ghssp += (
            "        ev_shuffle = tracing.Event('shuffle_pivot_index')\n")
        odqh__hdx = ', '.join([f'array_to_info(index_tup[{i}])' for i in
            range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for
            i in range(len(columns_tup))] + [
            f'array_to_info(values_tup[{i}])' for i in range(len(values_tup))])
        aexk__ghssp += f'        info_list = [{odqh__hdx}]\n'
        aexk__ghssp += (
            '        cpp_table = arr_info_list_to_table(info_list)\n')
        aexk__ghssp += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
        psx__bxdv = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
             for i in range(len(index_tup))])
        yclbm__okaba = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
             for i in range(len(columns_tup))])
        ncac__yqtt = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
             for i in range(len(values_tup))])
        aexk__ghssp += f'        index_tup = ({psx__bxdv},)\n'
        aexk__ghssp += f'        columns_tup = ({yclbm__okaba},)\n'
        aexk__ghssp += f'        values_tup = ({ncac__yqtt},)\n'
        aexk__ghssp += '        delete_table(cpp_table)\n'
        aexk__ghssp += '        delete_table(out_cpp_table)\n'
        aexk__ghssp += '        ev_shuffle.finalize()\n'
    aexk__ghssp += '    columns_arr = columns_tup[0]\n'
    if ayw__nuwv:
        aexk__ghssp += '    values_arrs = [arr for arr in values_tup]\n'
    rrz__dwnw = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    aexk__ghssp += f'    new_index_tup = ({rrz__dwnw},)\n'
    aexk__ghssp += """    ev_unique = tracing.Event('pivot_unique_index_map', is_parallel=parallel)
"""
    aexk__ghssp += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    aexk__ghssp += '        new_index_tup\n'
    aexk__ghssp += '    )\n'
    aexk__ghssp += '    n_rows = len(unique_index_arr_tup[0])\n'
    aexk__ghssp += '    num_values_arrays = len(values_tup)\n'
    aexk__ghssp += '    n_unique_pivots = len(pivot_values)\n'
    if ayw__nuwv:
        aexk__ghssp += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        aexk__ghssp += '    n_cols = n_unique_pivots\n'
    aexk__ghssp += '    col_map = {}\n'
    aexk__ghssp += '    for i in range(n_unique_pivots):\n'
    aexk__ghssp += (
        '        if bodo.libs.array_kernels.isna(pivot_values, i):\n')
    aexk__ghssp += '            raise ValueError(\n'
    aexk__ghssp += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    aexk__ghssp += '            )\n'
    aexk__ghssp += '        col_map[pivot_values[i]] = i\n'
    aexk__ghssp += '    ev_unique.finalize()\n'
    aexk__ghssp += (
        "    ev_alloc = tracing.Event('pivot_alloc', is_parallel=parallel)\n")
    zasw__sel = False
    for i, urk__jep in enumerate(hcu__tnsoi):
        if is_str_arr_type(urk__jep):
            zasw__sel = True
            aexk__ghssp += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            aexk__ghssp += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if zasw__sel:
        if lnc__nugwn:
            aexk__ghssp += '    nbytes = (n_rows + 7) >> 3\n'
            aexk__ghssp += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        aexk__ghssp += '    for i in range(len(columns_arr)):\n'
        aexk__ghssp += '        col_name = columns_arr[i]\n'
        aexk__ghssp += '        pivot_idx = col_map[col_name]\n'
        aexk__ghssp += '        row_idx = row_vector[i]\n'
        if lnc__nugwn:
            aexk__ghssp += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            aexk__ghssp += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            aexk__ghssp += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            aexk__ghssp += '        else:\n'
            aexk__ghssp += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if ayw__nuwv:
            aexk__ghssp += '        for j in range(num_values_arrays):\n'
            aexk__ghssp += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            aexk__ghssp += '            len_arr = len_arrs_0[col_idx]\n'
            aexk__ghssp += '            values_arr = values_arrs[j]\n'
            aexk__ghssp += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            aexk__ghssp += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            aexk__ghssp += '                len_arr[row_idx] = str_val_len\n'
            aexk__ghssp += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, urk__jep in enumerate(hcu__tnsoi):
                if is_str_arr_type(urk__jep):
                    aexk__ghssp += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    aexk__ghssp += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    aexk__ghssp += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    aexk__ghssp += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    aexk__ghssp += f"    ev_alloc.add_attribute('num_rows', n_rows)\n"
    for i, urk__jep in enumerate(hcu__tnsoi):
        if is_str_arr_type(urk__jep):
            aexk__ghssp += f'    data_arrs_{i} = [\n'
            aexk__ghssp += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            aexk__ghssp += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            aexk__ghssp += '        )\n'
            aexk__ghssp += '        for i in range(n_cols)\n'
            aexk__ghssp += '    ]\n'
            aexk__ghssp += f'    if tracing.is_tracing():\n'
            aexk__ghssp += '         for i in range(n_cols):'
            aexk__ghssp += f"""            ev_alloc.add_attribute('total_str_chars_out_column_{i}_' + str(i), total_lens_{i}[i])
"""
        else:
            aexk__ghssp += f'    data_arrs_{i} = [\n'
            aexk__ghssp += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            aexk__ghssp += '        for _ in range(n_cols)\n'
            aexk__ghssp += '    ]\n'
    if not zasw__sel and lnc__nugwn:
        aexk__ghssp += '    nbytes = (n_rows + 7) >> 3\n'
        aexk__ghssp += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    aexk__ghssp += '    ev_alloc.finalize()\n'
    aexk__ghssp += (
        "    ev_fill = tracing.Event('pivot_fill_data', is_parallel=parallel)\n"
        )
    aexk__ghssp += '    for i in range(len(columns_arr)):\n'
    aexk__ghssp += '        col_name = columns_arr[i]\n'
    aexk__ghssp += '        pivot_idx = col_map[col_name]\n'
    aexk__ghssp += '        row_idx = row_vector[i]\n'
    if not zasw__sel and lnc__nugwn:
        aexk__ghssp += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        aexk__ghssp += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        aexk__ghssp += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        aexk__ghssp += '        else:\n'
        aexk__ghssp += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
    if ayw__nuwv:
        aexk__ghssp += '        for j in range(num_values_arrays):\n'
        aexk__ghssp += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        aexk__ghssp += '            col_arr = data_arrs_0[col_idx]\n'
        aexk__ghssp += '            values_arr = values_arrs[j]\n'
        aexk__ghssp += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        aexk__ghssp += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        aexk__ghssp += '            else:\n'
        aexk__ghssp += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, urk__jep in enumerate(hcu__tnsoi):
            aexk__ghssp += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            aexk__ghssp += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            aexk__ghssp += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            aexk__ghssp += f'        else:\n'
            aexk__ghssp += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        aexk__ghssp += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        mjah__kzwv = index_names.meta[0]
    else:
        aexk__ghssp += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        mjah__kzwv = tuple(index_names.meta)
    aexk__ghssp += f'    if tracing.is_tracing():\n'
    aexk__ghssp += f'        index_nbytes = index.nbytes\n'
    aexk__ghssp += f"        ev.add_attribute('index_nbytes', index_nbytes)\n"
    if not fxyte__dmbh:
        brfnt__xgl = columns_name.meta[0]
        if dera__deg:
            aexk__ghssp += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            crn__edyxd = value_names.meta
            if all(isinstance(jvf__ufjq, str) for jvf__ufjq in crn__edyxd):
                crn__edyxd = pd.array(crn__edyxd, 'string')
            elif all(isinstance(jvf__ufjq, int) for jvf__ufjq in crn__edyxd):
                crn__edyxd = np.array(crn__edyxd, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(crn__edyxd.dtype, pd.StringDtype):
                aexk__ghssp += '    total_chars = 0\n'
                aexk__ghssp += f'    for i in range({len(value_names)}):\n'
                aexk__ghssp += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                aexk__ghssp += '        total_chars += value_name_str_len\n'
                aexk__ghssp += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                aexk__ghssp += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                aexk__ghssp += '    total_chars = 0\n'
                aexk__ghssp += '    for i in range(len(pivot_values)):\n'
                aexk__ghssp += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                aexk__ghssp += '        total_chars += pivot_val_str_len\n'
                aexk__ghssp += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                aexk__ghssp += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            aexk__ghssp += f'    for i in range({len(value_names)}):\n'
            aexk__ghssp += '        for j in range(len(pivot_values)):\n'
            aexk__ghssp += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            aexk__ghssp += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            aexk__ghssp += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            aexk__ghssp += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    aexk__ghssp += '    ev_fill.finalize()\n'
    gfy__sgjqy = None
    if fxyte__dmbh:
        if dera__deg:
            hpzxd__viu = []
            for wkh__kmlo in _constant_pivot_values.meta:
                for pchxx__jlmat in value_names.meta:
                    hpzxd__viu.append((wkh__kmlo, pchxx__jlmat))
            column_names = tuple(hpzxd__viu)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        npw__cigr = ColNamesMetaType(column_names)
        ccftx__bmdv = []
        for uinuo__cpfpq in hcu__tnsoi:
            ccftx__bmdv.extend([uinuo__cpfpq] * len(_constant_pivot_values))
        ymj__efkrc = tuple(ccftx__bmdv)
        gfy__sgjqy = TableType(ymj__efkrc)
        aexk__ghssp += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        aexk__ghssp += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, uinuo__cpfpq in enumerate(hcu__tnsoi):
            aexk__ghssp += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {gfy__sgjqy.type_to_blk[uinuo__cpfpq]})
"""
        aexk__ghssp += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        aexk__ghssp += '        (table,), index, columns_typ\n'
        aexk__ghssp += '    )\n'
    else:
        bekqs__mlyi = ', '.join(f'data_arrs_{i}' for i in range(len(
            hcu__tnsoi)))
        aexk__ghssp += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({bekqs__mlyi},), n_rows)
"""
        aexk__ghssp += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        aexk__ghssp += '        (table,), index, column_index\n'
        aexk__ghssp += '    )\n'
    aexk__ghssp += '    ev.finalize()\n'
    aexk__ghssp += '    return result\n'
    hqh__jubq = {}
    bat__vvasw = {f'data_arr_typ_{i}': urk__jep for i, urk__jep in
        enumerate(hcu__tnsoi)}
    vtai__mhcxh = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        gfy__sgjqy, 'columns_typ': npw__cigr, 'index_names_lit': mjah__kzwv,
        'value_names_lit': crn__edyxd, 'columns_name_lit': brfnt__xgl, **
        bat__vvasw, 'tracing': tracing}
    exec(aexk__ghssp, vtai__mhcxh, hqh__jubq)
    impl = hqh__jubq['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    wpik__qlcni = {}
    wpik__qlcni['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, bxucw__nkpbe in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        jej__scg = None
        if isinstance(bxucw__nkpbe, bodo.DatetimeArrayType):
            fba__fipjo = 'datetimetz'
            lbx__aqym = 'datetime64[ns]'
            if isinstance(bxucw__nkpbe.tz, int):
                pqpgy__muhw = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(bxucw__nkpbe.tz))
            else:
                pqpgy__muhw = pd.DatetimeTZDtype(tz=bxucw__nkpbe.tz).tz
            jej__scg = {'timezone': pa.lib.tzinfo_to_string(pqpgy__muhw)}
        elif isinstance(bxucw__nkpbe, types.Array
            ) or bxucw__nkpbe == boolean_array:
            fba__fipjo = lbx__aqym = bxucw__nkpbe.dtype.name
            if lbx__aqym.startswith('datetime'):
                fba__fipjo = 'datetime'
        elif is_str_arr_type(bxucw__nkpbe):
            fba__fipjo = 'unicode'
            lbx__aqym = 'object'
        elif bxucw__nkpbe == binary_array_type:
            fba__fipjo = 'bytes'
            lbx__aqym = 'object'
        elif isinstance(bxucw__nkpbe, DecimalArrayType):
            fba__fipjo = lbx__aqym = 'object'
        elif isinstance(bxucw__nkpbe, IntegerArrayType):
            srczc__khscv = bxucw__nkpbe.dtype.name
            if srczc__khscv.startswith('int'):
                fba__fipjo = 'Int' + srczc__khscv[3:]
            elif srczc__khscv.startswith('uint'):
                fba__fipjo = 'UInt' + srczc__khscv[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, bxucw__nkpbe))
            lbx__aqym = bxucw__nkpbe.dtype.name
        elif bxucw__nkpbe == datetime_date_array_type:
            fba__fipjo = 'datetime'
            lbx__aqym = 'object'
        elif isinstance(bxucw__nkpbe, (StructArrayType, ArrayItemArrayType)):
            fba__fipjo = 'object'
            lbx__aqym = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, bxucw__nkpbe))
        pkf__lznk = {'name': col_name, 'field_name': col_name,
            'pandas_type': fba__fipjo, 'numpy_type': lbx__aqym, 'metadata':
            jej__scg}
        wpik__qlcni['columns'].append(pkf__lznk)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            rvvg__dedxn = '__index_level_0__'
            jfo__petwl = None
        else:
            rvvg__dedxn = '%s'
            jfo__petwl = '%s'
        wpik__qlcni['index_columns'] = [rvvg__dedxn]
        wpik__qlcni['columns'].append({'name': jfo__petwl, 'field_name':
            rvvg__dedxn, 'pandas_type': index.pandas_type_name,
            'numpy_type': index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        wpik__qlcni['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        wpik__qlcni['index_columns'] = []
    wpik__qlcni['pandas_version'] = pd.__version__
    return wpik__qlcni


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
        kdzkl__lju = []
        for avyb__kmiyz in partition_cols:
            try:
                idx = df.columns.index(avyb__kmiyz)
            except ValueError as bjlnr__uxn:
                raise BodoError(
                    f'Partition column {avyb__kmiyz} is not in dataframe')
            kdzkl__lju.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    kwqtj__vvzod = isinstance(df.index, bodo.hiframes.pd_index_ext.
        RangeIndexType)
    sojp__jxn = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not kwqtj__vvzod)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not kwqtj__vvzod or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and kwqtj__vvzod and not is_overload_true(_is_parallel)
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
        qyxt__pyw = df.runtime_data_types
        jdf__yusw = len(qyxt__pyw)
        jej__scg = gen_pandas_parquet_metadata([''] * jdf__yusw, qyxt__pyw,
            df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        vhvv__utv = jej__scg['columns'][:jdf__yusw]
        jej__scg['columns'] = jej__scg['columns'][jdf__yusw:]
        vhvv__utv = [json.dumps(nzsp__hto).replace('""', '{0}') for
            nzsp__hto in vhvv__utv]
        ogr__mfol = json.dumps(jej__scg)
        opus__oau = '"columns": ['
        ykdg__dts = ogr__mfol.find(opus__oau)
        if ykdg__dts == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        nziy__saz = ykdg__dts + len(opus__oau)
        skl__spbny = ogr__mfol[:nziy__saz]
        ogr__mfol = ogr__mfol[nziy__saz:]
        gnbkj__wmvz = len(jej__scg['columns'])
    else:
        ogr__mfol = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and kwqtj__vvzod:
        ogr__mfol = ogr__mfol.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            ogr__mfol = ogr__mfol.replace('"%s"', '%s')
    if not df.is_table_format:
        dhas__kolb = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    aexk__ghssp = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        aexk__ghssp += '    py_table = get_dataframe_table(df)\n'
        aexk__ghssp += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        aexk__ghssp += '    info_list = [{}]\n'.format(dhas__kolb)
        aexk__ghssp += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        aexk__ghssp += '    columns_index = get_dataframe_column_names(df)\n'
        aexk__ghssp += '    names_arr = index_to_array(columns_index)\n'
        aexk__ghssp += '    col_names = array_to_info(names_arr)\n'
    else:
        aexk__ghssp += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and sojp__jxn:
        aexk__ghssp += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        hhp__yewbs = True
    else:
        aexk__ghssp += '    index_col = array_to_info(np.empty(0))\n'
        hhp__yewbs = False
    if df.has_runtime_cols:
        aexk__ghssp += '    columns_lst = []\n'
        aexk__ghssp += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            aexk__ghssp += f'    for _ in range(len(py_table.block_{i})):\n'
            aexk__ghssp += f"""        columns_lst.append({vhvv__utv[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            aexk__ghssp += '        num_cols += 1\n'
        if gnbkj__wmvz:
            aexk__ghssp += "    columns_lst.append('')\n"
        aexk__ghssp += '    columns_str = ", ".join(columns_lst)\n'
        aexk__ghssp += ('    metadata = """' + skl__spbny +
            '""" + columns_str + """' + ogr__mfol + '"""\n')
    else:
        aexk__ghssp += '    metadata = """' + ogr__mfol + '"""\n'
    aexk__ghssp += '    if compression is None:\n'
    aexk__ghssp += "        compression = 'none'\n"
    aexk__ghssp += '    if df.index.name is not None:\n'
    aexk__ghssp += '        name_ptr = df.index.name\n'
    aexk__ghssp += '    else:\n'
    aexk__ghssp += "        name_ptr = 'null'\n"
    aexk__ghssp += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    graaa__zfrfy = None
    if partition_cols:
        graaa__zfrfy = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        dkp__mpuiz = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in kdzkl__lju)
        if dkp__mpuiz:
            aexk__ghssp += '    cat_info_list = [{}]\n'.format(dkp__mpuiz)
            aexk__ghssp += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            aexk__ghssp += '    cat_table = table\n'
        aexk__ghssp += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        aexk__ghssp += (
            f'    part_cols_idxs = np.array({kdzkl__lju}, dtype=np.int32)\n')
        aexk__ghssp += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        aexk__ghssp += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        aexk__ghssp += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        aexk__ghssp += (
            '                            unicode_to_utf8(compression),\n')
        aexk__ghssp += '                            _is_parallel,\n'
        aexk__ghssp += (
            '                            unicode_to_utf8(bucket_region),\n')
        aexk__ghssp += '                            row_group_size,\n'
        aexk__ghssp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        aexk__ghssp += '    delete_table_decref_arrays(table)\n'
        aexk__ghssp += '    delete_info_decref_array(index_col)\n'
        aexk__ghssp += (
            '    delete_info_decref_array(col_names_no_partitions)\n')
        aexk__ghssp += '    delete_info_decref_array(col_names)\n'
        if dkp__mpuiz:
            aexk__ghssp += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        aexk__ghssp += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        aexk__ghssp += (
            '                            table, col_names, index_col,\n')
        aexk__ghssp += '                            ' + str(hhp__yewbs) + ',\n'
        aexk__ghssp += (
            '                            unicode_to_utf8(metadata),\n')
        aexk__ghssp += (
            '                            unicode_to_utf8(compression),\n')
        aexk__ghssp += (
            '                            _is_parallel, 1, df.index.start,\n')
        aexk__ghssp += (
            '                            df.index.stop, df.index.step,\n')
        aexk__ghssp += (
            '                            unicode_to_utf8(name_ptr),\n')
        aexk__ghssp += (
            '                            unicode_to_utf8(bucket_region),\n')
        aexk__ghssp += '                            row_group_size,\n'
        aexk__ghssp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        aexk__ghssp += '    delete_table_decref_arrays(table)\n'
        aexk__ghssp += '    delete_info_decref_array(index_col)\n'
        aexk__ghssp += '    delete_info_decref_array(col_names)\n'
    else:
        aexk__ghssp += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        aexk__ghssp += (
            '                            table, col_names, index_col,\n')
        aexk__ghssp += '                            ' + str(hhp__yewbs) + ',\n'
        aexk__ghssp += (
            '                            unicode_to_utf8(metadata),\n')
        aexk__ghssp += (
            '                            unicode_to_utf8(compression),\n')
        aexk__ghssp += (
            '                            _is_parallel, 0, 0, 0, 0,\n')
        aexk__ghssp += (
            '                            unicode_to_utf8(name_ptr),\n')
        aexk__ghssp += (
            '                            unicode_to_utf8(bucket_region),\n')
        aexk__ghssp += '                            row_group_size,\n'
        aexk__ghssp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        aexk__ghssp += '    delete_table_decref_arrays(table)\n'
        aexk__ghssp += '    delete_info_decref_array(index_col)\n'
        aexk__ghssp += '    delete_info_decref_array(col_names)\n'
    hqh__jubq = {}
    if df.has_runtime_cols:
        vmv__mpczp = None
    else:
        for pgrpn__ugij in df.columns:
            if not isinstance(pgrpn__ugij, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        vmv__mpczp = pd.array(df.columns)
    exec(aexk__ghssp, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': vmv__mpczp,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': graaa__zfrfy,
        'get_dataframe_column_names': get_dataframe_column_names,
        'fix_arr_dtype': fix_arr_dtype, 'decode_if_dict_array':
        decode_if_dict_array, 'decode_if_dict_table': decode_if_dict_table},
        hqh__jubq)
    lrylf__gmrz = hqh__jubq['df_to_parquet']
    return lrylf__gmrz


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    zfta__wqzm = 'all_ok'
    csezp__fra, jzg__nnrq = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        efn__rzf = 100
        if chunksize is None:
            zcpij__daczy = efn__rzf
        else:
            zcpij__daczy = min(chunksize, efn__rzf)
        if _is_table_create:
            df = df.iloc[:zcpij__daczy, :]
        else:
            df = df.iloc[zcpij__daczy:, :]
            if len(df) == 0:
                return zfta__wqzm
    ktb__mtwcd = df.columns
    try:
        if csezp__fra == 'snowflake':
            if jzg__nnrq and con.count(jzg__nnrq) == 1:
                con = con.replace(jzg__nnrq, quote(jzg__nnrq))
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
                df.columns = [(jvf__ufjq.upper() if jvf__ufjq.islower() else
                    jvf__ufjq) for jvf__ufjq in df.columns]
            except ImportError as bjlnr__uxn:
                zfta__wqzm = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return zfta__wqzm
        if csezp__fra == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            zlnb__kdif = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            ggg__rhjku = bodo.typeof(df)
            tnxgh__bupv = {}
            for jvf__ufjq, ybey__wrec in zip(ggg__rhjku.columns, ggg__rhjku
                .data):
                if df[jvf__ufjq].dtype == 'object':
                    if ybey__wrec == datetime_date_array_type:
                        tnxgh__bupv[jvf__ufjq] = sa.types.Date
                    elif ybey__wrec in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not zlnb__kdif or 
                        zlnb__kdif == '0'):
                        tnxgh__bupv[jvf__ufjq] = VARCHAR2(4000)
            dtype = tnxgh__bupv
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as fxqk__hyudm:
            zfta__wqzm = fxqk__hyudm.args[0]
            if csezp__fra == 'oracle' and 'ORA-12899' in zfta__wqzm:
                zfta__wqzm += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return zfta__wqzm
    finally:
        df.columns = ktb__mtwcd


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
    aexk__ghssp = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    aexk__ghssp += f"    if con.startswith('iceberg'):\n"
    aexk__ghssp += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    aexk__ghssp += f'        if schema is None:\n'
    aexk__ghssp += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    aexk__ghssp += f'        if chunksize is not None:\n'
    aexk__ghssp += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    aexk__ghssp += f'        if index and bodo.get_rank() == 0:\n'
    aexk__ghssp += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    aexk__ghssp += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    aexk__ghssp += f"""            warnings.warn('index_label is not supported for Iceberg tables.')
"""
    if df.is_table_format:
        aexk__ghssp += f'        py_table = get_dataframe_table(df)\n'
        aexk__ghssp += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        dhas__kolb = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        aexk__ghssp += f'        info_list = [{dhas__kolb}]\n'
        aexk__ghssp += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        aexk__ghssp += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        aexk__ghssp += f'        names_arr = index_to_array(columns_index)\n'
        aexk__ghssp += f'        col_names = array_to_info(names_arr)\n'
    else:
        aexk__ghssp += f'        col_names = array_to_info(col_names_arr)\n'
    aexk__ghssp += """        bodo.io.iceberg.iceberg_write(
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
    aexk__ghssp += f'        delete_table_decref_arrays(table)\n'
    aexk__ghssp += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        vmv__mpczp = None
    else:
        for pgrpn__ugij in df.columns:
            if not isinstance(pgrpn__ugij, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        vmv__mpczp = pd.array(df.columns)
    aexk__ghssp += f'    else:\n'
    aexk__ghssp += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    aexk__ghssp += f"        err_msg = 'unset'\n"
    aexk__ghssp += f'        if rank != 0:\n'
    aexk__ghssp += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    aexk__ghssp += f'        elif rank == 0:\n'
    aexk__ghssp += f'            err_msg = to_sql_exception_guard_encaps(\n'
    aexk__ghssp += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    aexk__ghssp += f'                          chunksize, dtype, method,\n'
    aexk__ghssp += f'                          True, _is_parallel,\n'
    aexk__ghssp += f'                      )\n'
    aexk__ghssp += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    aexk__ghssp += f"        if_exists = 'append'\n"
    aexk__ghssp += f"        if _is_parallel and err_msg == 'all_ok':\n"
    aexk__ghssp += f'            err_msg = to_sql_exception_guard_encaps(\n'
    aexk__ghssp += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    aexk__ghssp += f'                          chunksize, dtype, method,\n'
    aexk__ghssp += f'                          False, _is_parallel,\n'
    aexk__ghssp += f'                      )\n'
    aexk__ghssp += f"        if err_msg != 'all_ok':\n"
    aexk__ghssp += f"            print('err_msg=', err_msg)\n"
    aexk__ghssp += (
        f"            raise ValueError('error in to_sql() operation')\n")
    hqh__jubq = {}
    exec(aexk__ghssp, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_to_cpp_table':
        py_table_to_cpp_table, 'py_table_typ': df.table_type,
        'col_names_arr': vmv__mpczp, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'delete_info_decref_array':
        delete_info_decref_array, 'arr_info_list_to_table':
        arr_info_list_to_table, 'index_to_array': index_to_array,
        'pyarrow_table_schema': bodo.io.iceberg.pyarrow_schema(df),
        'to_sql_exception_guard_encaps': to_sql_exception_guard_encaps,
        'warnings': warnings}, hqh__jubq)
    _impl = hqh__jubq['df_to_sql']
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
        aqqi__nke = get_overload_const_str(path_or_buf)
        if aqqi__nke.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        pvyvr__nzf = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(pvyvr__nzf), unicode_to_utf8(_bodo_file_prefix)
                )
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(pvyvr__nzf), unicode_to_utf8(_bodo_file_prefix)
                )
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    yfb__ugi = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    grgnl__ywmkg = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', yfb__ugi, grgnl__ywmkg,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    aexk__ghssp = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        icb__sqq = data.data.dtype.categories
        aexk__ghssp += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        icb__sqq = data.dtype.categories
        aexk__ghssp += '  data_values = data\n'
    mjk__mpww = len(icb__sqq)
    aexk__ghssp += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    aexk__ghssp += '  numba.parfors.parfor.init_prange()\n'
    aexk__ghssp += '  n = len(data_values)\n'
    for i in range(mjk__mpww):
        aexk__ghssp += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    aexk__ghssp += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    aexk__ghssp += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for awni__dgbh in range(mjk__mpww):
        aexk__ghssp += '          data_arr_{}[i] = 0\n'.format(awni__dgbh)
    aexk__ghssp += '      else:\n'
    for ugshy__hsmv in range(mjk__mpww):
        aexk__ghssp += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            ugshy__hsmv)
    dhas__kolb = ', '.join(f'data_arr_{i}' for i in range(mjk__mpww))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(icb__sqq[0], np.datetime64):
        icb__sqq = tuple(pd.Timestamp(jvf__ufjq) for jvf__ufjq in icb__sqq)
    elif isinstance(icb__sqq[0], np.timedelta64):
        icb__sqq = tuple(pd.Timedelta(jvf__ufjq) for jvf__ufjq in icb__sqq)
    return bodo.hiframes.dataframe_impl._gen_init_df(aexk__ghssp, icb__sqq,
        dhas__kolb, index)


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
    for xwnst__cai in pd_unsupported:
        imue__pymp = mod_name + '.' + xwnst__cai.__name__
        overload(xwnst__cai, no_unliteral=True)(create_unsupported_overload
            (imue__pymp))


def _install_dataframe_unsupported():
    for mpi__oksi in dataframe_unsupported_attrs:
        wqd__gmjg = 'DataFrame.' + mpi__oksi
        overload_attribute(DataFrameType, mpi__oksi)(
            create_unsupported_overload(wqd__gmjg))
    for imue__pymp in dataframe_unsupported:
        wqd__gmjg = 'DataFrame.' + imue__pymp + '()'
        overload_method(DataFrameType, imue__pymp)(create_unsupported_overload
            (wqd__gmjg))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
