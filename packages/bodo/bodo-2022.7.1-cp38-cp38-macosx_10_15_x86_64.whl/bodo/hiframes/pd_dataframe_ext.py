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
            ihky__aga = f'{len(self.data)} columns of types {set(self.data)}'
            kxv__vjtwt = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({ihky__aga}, {self.index}, {kxv__vjtwt}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {qhe__zac: i for i, qhe__zac in enumerate(self.columns)}

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
            dmwu__yka = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            data = tuple(ptfn__aox.unify(typingctx, kkck__pos) if ptfn__aox !=
                kkck__pos else ptfn__aox for ptfn__aox, kkck__pos in zip(
                self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if dmwu__yka is not None and None not in data:
                return DataFrameType(data, dmwu__yka, self.columns, dist,
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
        return all(ptfn__aox.is_precise() for ptfn__aox in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        khw__oegqr = self.columns.index(col_name)
        wchdm__tkood = tuple(list(self.data[:khw__oegqr]) + [new_type] +
            list(self.data[khw__oegqr + 1:]))
        return DataFrameType(wchdm__tkood, self.index, self.columns, self.
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
        cgbcs__yidpr = [('data', data_typ), ('index', fe_type.df_type.index
            ), ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            cgbcs__yidpr.append(('columns', fe_type.df_type.
                runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, cgbcs__yidpr)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        cgbcs__yidpr = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, cgbcs__yidpr)


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
        nlu__wpv = 'n',
        ddpi__izbbu = {'n': 5}
        mrue__qtaj, iuf__ufm = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, nlu__wpv, ddpi__izbbu)
        bdbxe__mmdmz = iuf__ufm[0]
        if not is_overload_int(bdbxe__mmdmz):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        vca__ihapa = df.copy()
        return vca__ihapa(*iuf__ufm).replace(pysig=mrue__qtaj)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        affld__axr = (df,) + args
        nlu__wpv = 'df', 'method', 'min_periods'
        ddpi__izbbu = {'method': 'pearson', 'min_periods': 1}
        btrss__siysy = 'method',
        mrue__qtaj, iuf__ufm = bodo.utils.typing.fold_typing_args(func_name,
            affld__axr, kws, nlu__wpv, ddpi__izbbu, btrss__siysy)
        slp__enfzc = iuf__ufm[2]
        if not is_overload_int(slp__enfzc):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        djvzk__zng = []
        iitz__gpuqk = []
        for qhe__zac, ebw__jqx in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(ebw__jqx.dtype):
                djvzk__zng.append(qhe__zac)
                iitz__gpuqk.append(types.Array(types.float64, 1, 'A'))
        if len(djvzk__zng) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        iitz__gpuqk = tuple(iitz__gpuqk)
        djvzk__zng = tuple(djvzk__zng)
        index_typ = bodo.utils.typing.type_col_to_index(djvzk__zng)
        vca__ihapa = DataFrameType(iitz__gpuqk, index_typ, djvzk__zng)
        return vca__ihapa(*iuf__ufm).replace(pysig=mrue__qtaj)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        ckcle__zsw = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        blg__pwi = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        xohgj__iog = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        htcgs__mkbtr = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        emjdu__csz = dict(raw=blg__pwi, result_type=xohgj__iog)
        lhciw__oaww = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', emjdu__csz, lhciw__oaww,
            package_name='pandas', module_name='DataFrame')
        lik__ciyt = True
        if types.unliteral(ckcle__zsw) == types.unicode_type:
            if not is_overload_constant_str(ckcle__zsw):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            lik__ciyt = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        hqxdc__biky = get_overload_const_int(axis)
        if lik__ciyt and hqxdc__biky != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif hqxdc__biky not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        ubebb__axi = []
        for arr_typ in df.data:
            mhiex__mddnw = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            pkny__fdan = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(mhiex__mddnw), types.int64), {}
                ).return_type
            ubebb__axi.append(pkny__fdan)
        xgwzr__ltnrz = types.none
        dlr__lyx = HeterogeneousIndexType(types.BaseTuple.from_types(tuple(
            types.literal(qhe__zac) for qhe__zac in df.columns)), None)
        ukd__vnews = types.BaseTuple.from_types(ubebb__axi)
        mjfx__oelc = types.Tuple([types.bool_] * len(ukd__vnews))
        bfn__tudu = bodo.NullableTupleType(ukd__vnews, mjfx__oelc)
        hzrs__srznl = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if hzrs__srznl == types.NPDatetime('ns'):
            hzrs__srznl = bodo.pd_timestamp_type
        if hzrs__srznl == types.NPTimedelta('ns'):
            hzrs__srznl = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(ukd__vnews):
            ximln__ugggd = HeterogeneousSeriesType(bfn__tudu, dlr__lyx,
                hzrs__srznl)
        else:
            ximln__ugggd = SeriesType(ukd__vnews.dtype, bfn__tudu, dlr__lyx,
                hzrs__srznl)
        fwpfb__acfo = ximln__ugggd,
        if htcgs__mkbtr is not None:
            fwpfb__acfo += tuple(htcgs__mkbtr.types)
        try:
            if not lik__ciyt:
                rkgrv__ajh = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(ckcle__zsw), self.context,
                    'DataFrame.apply', axis if hqxdc__biky == 1 else None)
            else:
                rkgrv__ajh = get_const_func_output_type(ckcle__zsw,
                    fwpfb__acfo, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as gjrs__piade:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                gjrs__piade))
        if lik__ciyt:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(rkgrv__ajh, (SeriesType, HeterogeneousSeriesType)
                ) and rkgrv__ajh.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(rkgrv__ajh, HeterogeneousSeriesType):
                qez__ckz, wyxhz__dzi = rkgrv__ajh.const_info
                if isinstance(rkgrv__ajh.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    req__kqeo = rkgrv__ajh.data.tuple_typ.types
                elif isinstance(rkgrv__ajh.data, types.Tuple):
                    req__kqeo = rkgrv__ajh.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                jeeuq__pyyx = tuple(to_nullable_type(dtype_to_array_type(
                    kxtlw__tbri)) for kxtlw__tbri in req__kqeo)
                vjzgy__ctdiv = DataFrameType(jeeuq__pyyx, df.index, wyxhz__dzi)
            elif isinstance(rkgrv__ajh, SeriesType):
                gvgp__xjf, wyxhz__dzi = rkgrv__ajh.const_info
                jeeuq__pyyx = tuple(to_nullable_type(dtype_to_array_type(
                    rkgrv__ajh.dtype)) for qez__ckz in range(gvgp__xjf))
                vjzgy__ctdiv = DataFrameType(jeeuq__pyyx, df.index, wyxhz__dzi)
            else:
                nlu__laij = get_udf_out_arr_type(rkgrv__ajh)
                vjzgy__ctdiv = SeriesType(nlu__laij.dtype, nlu__laij, df.
                    index, None)
        else:
            vjzgy__ctdiv = rkgrv__ajh
        ekcj__cpky = ', '.join("{} = ''".format(ptfn__aox) for ptfn__aox in
            kws.keys())
        wvjqf__mfws = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {ekcj__cpky}):
"""
        wvjqf__mfws += '    pass\n'
        sbrgr__wvi = {}
        exec(wvjqf__mfws, {}, sbrgr__wvi)
        qtoqu__fzi = sbrgr__wvi['apply_stub']
        mrue__qtaj = numba.core.utils.pysignature(qtoqu__fzi)
        rhkve__pxg = (ckcle__zsw, axis, blg__pwi, xohgj__iog, htcgs__mkbtr
            ) + tuple(kws.values())
        return signature(vjzgy__ctdiv, *rhkve__pxg).replace(pysig=mrue__qtaj)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        nlu__wpv = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots', 'sharex',
            'sharey', 'layout', 'use_index', 'title', 'grid', 'legend',
            'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks', 'xlim',
            'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr', 'xerr',
            'secondary_y', 'sort_columns', 'xlabel', 'ylabel', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        ddpi__izbbu = {'x': None, 'y': None, 'kind': 'line', 'figsize':
            None, 'ax': None, 'subplots': False, 'sharex': None, 'sharey': 
            False, 'layout': None, 'use_index': True, 'title': None, 'grid':
            None, 'legend': True, 'style': None, 'logx': False, 'logy': 
            False, 'loglog': False, 'xticks': None, 'yticks': None, 'xlim':
            None, 'ylim': None, 'rot': None, 'fontsize': None, 'colormap':
            None, 'table': False, 'yerr': None, 'xerr': None, 'secondary_y':
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        btrss__siysy = ('subplots', 'sharex', 'sharey', 'layout',
            'use_index', 'grid', 'style', 'logx', 'logy', 'loglog', 'xlim',
            'ylim', 'rot', 'colormap', 'table', 'yerr', 'xerr',
            'sort_columns', 'secondary_y', 'colorbar', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        mrue__qtaj, iuf__ufm = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, nlu__wpv, ddpi__izbbu, btrss__siysy)
        wnc__urubn = iuf__ufm[2]
        if not is_overload_constant_str(wnc__urubn):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        eej__iqud = iuf__ufm[0]
        if not is_overload_none(eej__iqud) and not (is_overload_int(
            eej__iqud) or is_overload_constant_str(eej__iqud)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(eej__iqud):
            mbkkn__gwyxj = get_overload_const_str(eej__iqud)
            if mbkkn__gwyxj not in df.columns:
                raise BodoError(
                    f'{func_name}: {mbkkn__gwyxj} column not found.')
        elif is_overload_int(eej__iqud):
            iuqds__roq = get_overload_const_int(eej__iqud)
            if iuqds__roq > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {iuqds__roq} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            eej__iqud = df.columns[eej__iqud]
        txwu__hcjgk = iuf__ufm[1]
        if not is_overload_none(txwu__hcjgk) and not (is_overload_int(
            txwu__hcjgk) or is_overload_constant_str(txwu__hcjgk)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(txwu__hcjgk):
            drki__tdus = get_overload_const_str(txwu__hcjgk)
            if drki__tdus not in df.columns:
                raise BodoError(f'{func_name}: {drki__tdus} column not found.')
        elif is_overload_int(txwu__hcjgk):
            xtapb__xotb = get_overload_const_int(txwu__hcjgk)
            if xtapb__xotb > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {xtapb__xotb} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            txwu__hcjgk = df.columns[txwu__hcjgk]
        wywly__aeoh = iuf__ufm[3]
        if not is_overload_none(wywly__aeoh) and not is_tuple_like_type(
            wywly__aeoh):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        zleh__znh = iuf__ufm[10]
        if not is_overload_none(zleh__znh) and not is_overload_constant_str(
            zleh__znh):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        jxt__pam = iuf__ufm[12]
        if not is_overload_bool(jxt__pam):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        blgc__lfca = iuf__ufm[17]
        if not is_overload_none(blgc__lfca) and not is_tuple_like_type(
            blgc__lfca):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        qnu__brse = iuf__ufm[18]
        if not is_overload_none(qnu__brse) and not is_tuple_like_type(qnu__brse
            ):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        jks__jhaee = iuf__ufm[22]
        if not is_overload_none(jks__jhaee) and not is_overload_int(jks__jhaee
            ):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        ybril__kcxo = iuf__ufm[29]
        if not is_overload_none(ybril__kcxo) and not is_overload_constant_str(
            ybril__kcxo):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        pfhbf__vyka = iuf__ufm[30]
        if not is_overload_none(pfhbf__vyka) and not is_overload_constant_str(
            pfhbf__vyka):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        vbqqp__gynfu = types.List(types.mpl_line_2d_type)
        wnc__urubn = get_overload_const_str(wnc__urubn)
        if wnc__urubn == 'scatter':
            if is_overload_none(eej__iqud) and is_overload_none(txwu__hcjgk):
                raise BodoError(
                    f'{func_name}: {wnc__urubn} requires an x and y column.')
            elif is_overload_none(eej__iqud):
                raise BodoError(
                    f'{func_name}: {wnc__urubn} x column is missing.')
            elif is_overload_none(txwu__hcjgk):
                raise BodoError(
                    f'{func_name}: {wnc__urubn} y column is missing.')
            vbqqp__gynfu = types.mpl_path_collection_type
        elif wnc__urubn != 'line':
            raise BodoError(f'{func_name}: {wnc__urubn} plot is not supported.'
                )
        return signature(vbqqp__gynfu, *iuf__ufm).replace(pysig=mrue__qtaj)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            oep__qpqhc = df.columns.index(attr)
            arr_typ = df.data[oep__qpqhc]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            bgtut__sji = []
            wchdm__tkood = []
            owe__qnk = False
            for i, wuqcl__ufdck in enumerate(df.columns):
                if wuqcl__ufdck[0] != attr:
                    continue
                owe__qnk = True
                bgtut__sji.append(wuqcl__ufdck[1] if len(wuqcl__ufdck) == 2
                     else wuqcl__ufdck[1:])
                wchdm__tkood.append(df.data[i])
            if owe__qnk:
                return DataFrameType(tuple(wchdm__tkood), df.index, tuple(
                    bgtut__sji))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        hbutq__mju = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(hbutq__mju)
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
        rrx__mwvgl = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], rrx__mwvgl)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    qjpiw__jaya = builder.module
    wxv__kdxkb = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    kmuh__bom = cgutils.get_or_insert_function(qjpiw__jaya, wxv__kdxkb,
        name='.dtor.df.{}'.format(df_type))
    if not kmuh__bom.is_declaration:
        return kmuh__bom
    kmuh__bom.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(kmuh__bom.append_basic_block())
    kmvgm__vhg = kmuh__bom.args[0]
    atw__unsqp = context.get_value_type(payload_type).as_pointer()
    zoyfh__imoz = builder.bitcast(kmvgm__vhg, atw__unsqp)
    payload = context.make_helper(builder, payload_type, ref=zoyfh__imoz)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        prur__lkhi = context.get_python_api(builder)
        igd__jtw = prur__lkhi.gil_ensure()
        prur__lkhi.decref(payload.parent)
        prur__lkhi.gil_release(igd__jtw)
    builder.ret_void()
    return kmuh__bom


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    bcvv__rtq = cgutils.create_struct_proxy(payload_type)(context, builder)
    bcvv__rtq.data = data_tup
    bcvv__rtq.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        bcvv__rtq.columns = colnames
    uejb__voy = context.get_value_type(payload_type)
    brc__ynsle = context.get_abi_sizeof(uejb__voy)
    nebhy__lmjx = define_df_dtor(context, builder, df_type, payload_type)
    prx__qtc = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, brc__ynsle), nebhy__lmjx)
    xszvy__czng = context.nrt.meminfo_data(builder, prx__qtc)
    hig__lglip = builder.bitcast(xszvy__czng, uejb__voy.as_pointer())
    bersy__wkwjs = cgutils.create_struct_proxy(df_type)(context, builder)
    bersy__wkwjs.meminfo = prx__qtc
    if parent is None:
        bersy__wkwjs.parent = cgutils.get_null_value(bersy__wkwjs.parent.type)
    else:
        bersy__wkwjs.parent = parent
        bcvv__rtq.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            prur__lkhi = context.get_python_api(builder)
            igd__jtw = prur__lkhi.gil_ensure()
            prur__lkhi.incref(parent)
            prur__lkhi.gil_release(igd__jtw)
    builder.store(bcvv__rtq._getvalue(), hig__lglip)
    return bersy__wkwjs._getvalue()


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
        syr__krlw = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        syr__krlw = [kxtlw__tbri for kxtlw__tbri in data_typ.dtype.arr_types]
    jqcga__rfbdo = DataFrameType(tuple(syr__krlw + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        imbt__xvh = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return imbt__xvh
    sig = signature(jqcga__rfbdo, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    gvgp__xjf = len(data_tup_typ.types)
    if gvgp__xjf == 0:
        column_names = ()
    bnmwi__vvpq = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(bnmwi__vvpq, ColNamesMetaType) and isinstance(bnmwi__vvpq
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = bnmwi__vvpq.meta
    if gvgp__xjf == 1 and isinstance(data_tup_typ.types[0], TableType):
        gvgp__xjf = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == gvgp__xjf, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    hrac__ozidd = data_tup_typ.types
    if gvgp__xjf != 0 and isinstance(data_tup_typ.types[0], TableType):
        hrac__ozidd = data_tup_typ.types[0].arr_types
        is_table_format = True
    jqcga__rfbdo = DataFrameType(hrac__ozidd, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            xoi__qewli = cgutils.create_struct_proxy(jqcga__rfbdo.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = xoi__qewli.parent
        imbt__xvh = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return imbt__xvh
    sig = signature(jqcga__rfbdo, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        bersy__wkwjs = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, bersy__wkwjs.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        bcvv__rtq = get_dataframe_payload(context, builder, df_typ, args[0])
        ifnl__kpjl = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[ifnl__kpjl]
        if df_typ.is_table_format:
            xoi__qewli = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(bcvv__rtq.data, 0))
            lvfzn__txcbi = df_typ.table_type.type_to_blk[arr_typ]
            rrzdi__ophew = getattr(xoi__qewli, f'block_{lvfzn__txcbi}')
            kni__smf = ListInstance(context, builder, types.List(arr_typ),
                rrzdi__ophew)
            ntcd__hdqo = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[ifnl__kpjl])
            rrx__mwvgl = kni__smf.getitem(ntcd__hdqo)
        else:
            rrx__mwvgl = builder.extract_value(bcvv__rtq.data, ifnl__kpjl)
        olqy__sdn = cgutils.alloca_once_value(builder, rrx__mwvgl)
        hlnvq__bdnp = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, olqy__sdn, hlnvq__bdnp)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    prx__qtc = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, prx__qtc)
    atw__unsqp = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, atw__unsqp)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    jqcga__rfbdo = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        jqcga__rfbdo = types.Tuple([TableType(df_typ.data)])
    sig = signature(jqcga__rfbdo, df_typ)

    def codegen(context, builder, signature, args):
        bcvv__rtq = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            bcvv__rtq.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        bcvv__rtq = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, bcvv__rtq.
            index)
    jqcga__rfbdo = df_typ.index
    sig = signature(jqcga__rfbdo, df_typ)
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
        vca__ihapa = df.data[i]
        return vca__ihapa(*args)


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
        bcvv__rtq = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(bcvv__rtq.data, 0))
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
    duhz__bjqa = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{duhz__bjqa})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        vca__ihapa = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return vca__ihapa(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        bcvv__rtq = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, bcvv__rtq.columns)
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
    ukd__vnews = self.typemap[data_tup.name]
    if any(is_tuple_like_type(kxtlw__tbri) for kxtlw__tbri in ukd__vnews.types
        ):
        return None
    if equiv_set.has_shape(data_tup):
        ysl__ensb = equiv_set.get_shape(data_tup)
        if len(ysl__ensb) > 1:
            equiv_set.insert_equiv(*ysl__ensb)
        if len(ysl__ensb) > 0:
            dlr__lyx = self.typemap[index.name]
            if not isinstance(dlr__lyx, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(ysl__ensb[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(ysl__ensb[0], len(
                ysl__ensb)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    bmp__jkqnb = args[0]
    data_types = self.typemap[bmp__jkqnb.name].data
    if any(is_tuple_like_type(kxtlw__tbri) for kxtlw__tbri in data_types):
        return None
    if equiv_set.has_shape(bmp__jkqnb):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            bmp__jkqnb)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    bmp__jkqnb = args[0]
    dlr__lyx = self.typemap[bmp__jkqnb.name].index
    if isinstance(dlr__lyx, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(bmp__jkqnb):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            bmp__jkqnb)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    bmp__jkqnb = args[0]
    if equiv_set.has_shape(bmp__jkqnb):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            bmp__jkqnb), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    bmp__jkqnb = args[0]
    if equiv_set.has_shape(bmp__jkqnb):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            bmp__jkqnb)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    ifnl__kpjl = get_overload_const_int(c_ind_typ)
    if df_typ.data[ifnl__kpjl] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        qsr__eadw, qez__ckz, dxtc__soh = args
        bcvv__rtq = get_dataframe_payload(context, builder, df_typ, qsr__eadw)
        if df_typ.is_table_format:
            xoi__qewli = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(bcvv__rtq.data, 0))
            lvfzn__txcbi = df_typ.table_type.type_to_blk[arr_typ]
            rrzdi__ophew = getattr(xoi__qewli, f'block_{lvfzn__txcbi}')
            kni__smf = ListInstance(context, builder, types.List(arr_typ),
                rrzdi__ophew)
            ntcd__hdqo = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[ifnl__kpjl])
            kni__smf.setitem(ntcd__hdqo, dxtc__soh, True)
        else:
            rrx__mwvgl = builder.extract_value(bcvv__rtq.data, ifnl__kpjl)
            context.nrt.decref(builder, df_typ.data[ifnl__kpjl], rrx__mwvgl)
            bcvv__rtq.data = builder.insert_value(bcvv__rtq.data, dxtc__soh,
                ifnl__kpjl)
            context.nrt.incref(builder, arr_typ, dxtc__soh)
        bersy__wkwjs = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=qsr__eadw)
        payload_type = DataFramePayloadType(df_typ)
        zoyfh__imoz = context.nrt.meminfo_data(builder, bersy__wkwjs.meminfo)
        atw__unsqp = context.get_value_type(payload_type).as_pointer()
        zoyfh__imoz = builder.bitcast(zoyfh__imoz, atw__unsqp)
        builder.store(bcvv__rtq._getvalue(), zoyfh__imoz)
        return impl_ret_borrowed(context, builder, df_typ, qsr__eadw)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        dataa__zoqu = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        btmv__dzcu = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=dataa__zoqu)
        nfw__zjvh = get_dataframe_payload(context, builder, df_typ, dataa__zoqu
            )
        bersy__wkwjs = construct_dataframe(context, builder, signature.
            return_type, nfw__zjvh.data, index_val, btmv__dzcu.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), nfw__zjvh.data)
        return bersy__wkwjs
    jqcga__rfbdo = DataFrameType(df_t.data, index_t, df_t.columns, df_t.
        dist, df_t.is_table_format)
    sig = signature(jqcga__rfbdo, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    gvgp__xjf = len(df_type.columns)
    svxc__wuejo = gvgp__xjf
    xfox__wpyyk = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    lnsf__yqnoj = col_name not in df_type.columns
    ifnl__kpjl = gvgp__xjf
    if lnsf__yqnoj:
        xfox__wpyyk += arr_type,
        column_names += col_name,
        svxc__wuejo += 1
    else:
        ifnl__kpjl = df_type.columns.index(col_name)
        xfox__wpyyk = tuple(arr_type if i == ifnl__kpjl else xfox__wpyyk[i] for
            i in range(gvgp__xjf))

    def codegen(context, builder, signature, args):
        qsr__eadw, qez__ckz, dxtc__soh = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, qsr__eadw)
        yyq__jfir = cgutils.create_struct_proxy(df_type)(context, builder,
            value=qsr__eadw)
        if df_type.is_table_format:
            dbj__msl = df_type.table_type
            rbl__gsk = builder.extract_value(in_dataframe_payload.data, 0)
            wwuc__rhh = TableType(xfox__wpyyk)
            hlyw__iqo = set_table_data_codegen(context, builder, dbj__msl,
                rbl__gsk, wwuc__rhh, arr_type, dxtc__soh, ifnl__kpjl,
                lnsf__yqnoj)
            data_tup = context.make_tuple(builder, types.Tuple([wwuc__rhh]),
                [hlyw__iqo])
        else:
            hrac__ozidd = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != ifnl__kpjl else dxtc__soh) for i in range(gvgp__xjf)
                ]
            if lnsf__yqnoj:
                hrac__ozidd.append(dxtc__soh)
            for bmp__jkqnb, sfkpy__fhq in zip(hrac__ozidd, xfox__wpyyk):
                context.nrt.incref(builder, sfkpy__fhq, bmp__jkqnb)
            data_tup = context.make_tuple(builder, types.Tuple(xfox__wpyyk),
                hrac__ozidd)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        jjy__vvehw = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, yyq__jfir.parent, None)
        if not lnsf__yqnoj and arr_type == df_type.data[ifnl__kpjl]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            zoyfh__imoz = context.nrt.meminfo_data(builder, yyq__jfir.meminfo)
            atw__unsqp = context.get_value_type(payload_type).as_pointer()
            zoyfh__imoz = builder.bitcast(zoyfh__imoz, atw__unsqp)
            miau__dhq = get_dataframe_payload(context, builder, df_type,
                jjy__vvehw)
            builder.store(miau__dhq._getvalue(), zoyfh__imoz)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, wwuc__rhh, builder.
                    extract_value(data_tup, 0))
            else:
                for bmp__jkqnb, sfkpy__fhq in zip(hrac__ozidd, xfox__wpyyk):
                    context.nrt.incref(builder, sfkpy__fhq, bmp__jkqnb)
        has_parent = cgutils.is_not_null(builder, yyq__jfir.parent)
        with builder.if_then(has_parent):
            prur__lkhi = context.get_python_api(builder)
            igd__jtw = prur__lkhi.gil_ensure()
            gofj__nxjz = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, dxtc__soh)
            qhe__zac = numba.core.pythonapi._BoxContext(context, builder,
                prur__lkhi, gofj__nxjz)
            vlf__sjm = qhe__zac.pyapi.from_native_value(arr_type, dxtc__soh,
                qhe__zac.env_manager)
            if isinstance(col_name, str):
                hhe__ztii = context.insert_const_string(builder.module,
                    col_name)
                zlzd__cztzt = prur__lkhi.string_from_string(hhe__ztii)
            else:
                assert isinstance(col_name, int)
                zlzd__cztzt = prur__lkhi.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            prur__lkhi.object_setitem(yyq__jfir.parent, zlzd__cztzt, vlf__sjm)
            prur__lkhi.decref(vlf__sjm)
            prur__lkhi.decref(zlzd__cztzt)
            prur__lkhi.gil_release(igd__jtw)
        return jjy__vvehw
    jqcga__rfbdo = DataFrameType(xfox__wpyyk, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(jqcga__rfbdo, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    gvgp__xjf = len(pyval.columns)
    hrac__ozidd = []
    for i in range(gvgp__xjf):
        mqufn__tsml = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            vlf__sjm = mqufn__tsml.array
        else:
            vlf__sjm = mqufn__tsml.values
        hrac__ozidd.append(vlf__sjm)
    hrac__ozidd = tuple(hrac__ozidd)
    if df_type.is_table_format:
        xoi__qewli = context.get_constant_generic(builder, df_type.
            table_type, Table(hrac__ozidd))
        data_tup = lir.Constant.literal_struct([xoi__qewli])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], wuqcl__ufdck) for
            i, wuqcl__ufdck in enumerate(hrac__ozidd)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    fzuj__umicf = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, fzuj__umicf])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    ciw__fxmyk = context.get_constant(types.int64, -1)
    vag__cokz = context.get_constant_null(types.voidptr)
    prx__qtc = lir.Constant.literal_struct([ciw__fxmyk, vag__cokz,
        vag__cokz, payload, ciw__fxmyk])
    prx__qtc = cgutils.global_constant(builder, '.const.meminfo', prx__qtc
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([prx__qtc, fzuj__umicf])


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
        dmwu__yka = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        dmwu__yka = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, dmwu__yka)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        wchdm__tkood = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                wchdm__tkood)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), wchdm__tkood)
    elif not fromty.is_table_format and toty.is_table_format:
        wchdm__tkood = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        wchdm__tkood = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        wchdm__tkood = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        wchdm__tkood = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, wchdm__tkood,
        dmwu__yka, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    ikyx__lcdxu = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        pzk__tmpp = get_index_data_arr_types(toty.index)[0]
        okx__lkct = bodo.utils.transform.get_type_alloc_counts(pzk__tmpp) - 1
        eaf__trlj = ', '.join('0' for qez__ckz in range(okx__lkct))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(eaf__trlj, ', ' if okx__lkct == 1 else ''))
        ikyx__lcdxu['index_arr_type'] = pzk__tmpp
    hal__baq = []
    for i, arr_typ in enumerate(toty.data):
        okx__lkct = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        eaf__trlj = ', '.join('0' for qez__ckz in range(okx__lkct))
        skse__yaqjc = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'
            .format(i, eaf__trlj, ', ' if okx__lkct == 1 else ''))
        hal__baq.append(skse__yaqjc)
        ikyx__lcdxu[f'arr_type{i}'] = arr_typ
    hal__baq = ', '.join(hal__baq)
    wvjqf__mfws = 'def impl():\n'
    cbmo__sokmy = bodo.hiframes.dataframe_impl._gen_init_df(wvjqf__mfws,
        toty.columns, hal__baq, index, ikyx__lcdxu)
    df = context.compile_internal(builder, cbmo__sokmy, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    dgcp__otz = toty.table_type
    xoi__qewli = cgutils.create_struct_proxy(dgcp__otz)(context, builder)
    xoi__qewli.parent = in_dataframe_payload.parent
    for kxtlw__tbri, lvfzn__txcbi in dgcp__otz.type_to_blk.items():
        pge__hvflf = context.get_constant(types.int64, len(dgcp__otz.
            block_to_arr_ind[lvfzn__txcbi]))
        qez__ckz, sygn__iphqz = ListInstance.allocate_ex(context, builder,
            types.List(kxtlw__tbri), pge__hvflf)
        sygn__iphqz.size = pge__hvflf
        setattr(xoi__qewli, f'block_{lvfzn__txcbi}', sygn__iphqz.value)
    for i, kxtlw__tbri in enumerate(fromty.data):
        cwson__jnl = toty.data[i]
        if kxtlw__tbri != cwson__jnl:
            acl__dovrl = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*acl__dovrl)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        rrx__mwvgl = builder.extract_value(in_dataframe_payload.data, i)
        if kxtlw__tbri != cwson__jnl:
            gnvq__jeitb = context.cast(builder, rrx__mwvgl, kxtlw__tbri,
                cwson__jnl)
            lsk__vok = False
        else:
            gnvq__jeitb = rrx__mwvgl
            lsk__vok = True
        lvfzn__txcbi = dgcp__otz.type_to_blk[kxtlw__tbri]
        rrzdi__ophew = getattr(xoi__qewli, f'block_{lvfzn__txcbi}')
        kni__smf = ListInstance(context, builder, types.List(kxtlw__tbri),
            rrzdi__ophew)
        ntcd__hdqo = context.get_constant(types.int64, dgcp__otz.
            block_offsets[i])
        kni__smf.setitem(ntcd__hdqo, gnvq__jeitb, lsk__vok)
    data_tup = context.make_tuple(builder, types.Tuple([dgcp__otz]), [
        xoi__qewli._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    hrac__ozidd = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            acl__dovrl = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*acl__dovrl)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            rrx__mwvgl = builder.extract_value(in_dataframe_payload.data, i)
            gnvq__jeitb = context.cast(builder, rrx__mwvgl, fromty.data[i],
                toty.data[i])
            lsk__vok = False
        else:
            gnvq__jeitb = builder.extract_value(in_dataframe_payload.data, i)
            lsk__vok = True
        if lsk__vok:
            context.nrt.incref(builder, toty.data[i], gnvq__jeitb)
        hrac__ozidd.append(gnvq__jeitb)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), hrac__ozidd)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    dbj__msl = fromty.table_type
    rbl__gsk = cgutils.create_struct_proxy(dbj__msl)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    wwuc__rhh = toty.table_type
    hlyw__iqo = cgutils.create_struct_proxy(wwuc__rhh)(context, builder)
    hlyw__iqo.parent = in_dataframe_payload.parent
    for kxtlw__tbri, lvfzn__txcbi in wwuc__rhh.type_to_blk.items():
        pge__hvflf = context.get_constant(types.int64, len(wwuc__rhh.
            block_to_arr_ind[lvfzn__txcbi]))
        qez__ckz, sygn__iphqz = ListInstance.allocate_ex(context, builder,
            types.List(kxtlw__tbri), pge__hvflf)
        sygn__iphqz.size = pge__hvflf
        setattr(hlyw__iqo, f'block_{lvfzn__txcbi}', sygn__iphqz.value)
    for i in range(len(fromty.data)):
        zlug__gfo = fromty.data[i]
        cwson__jnl = toty.data[i]
        if zlug__gfo != cwson__jnl:
            acl__dovrl = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*acl__dovrl)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        biv__xaz = dbj__msl.type_to_blk[zlug__gfo]
        kaipv__cidvf = getattr(rbl__gsk, f'block_{biv__xaz}')
        gwq__xfkol = ListInstance(context, builder, types.List(zlug__gfo),
            kaipv__cidvf)
        rixx__zole = context.get_constant(types.int64, dbj__msl.
            block_offsets[i])
        rrx__mwvgl = gwq__xfkol.getitem(rixx__zole)
        if zlug__gfo != cwson__jnl:
            gnvq__jeitb = context.cast(builder, rrx__mwvgl, zlug__gfo,
                cwson__jnl)
            lsk__vok = False
        else:
            gnvq__jeitb = rrx__mwvgl
            lsk__vok = True
        zqi__zze = wwuc__rhh.type_to_blk[kxtlw__tbri]
        sygn__iphqz = getattr(hlyw__iqo, f'block_{zqi__zze}')
        xvuz__qbom = ListInstance(context, builder, types.List(cwson__jnl),
            sygn__iphqz)
        yqip__qbhx = context.get_constant(types.int64, wwuc__rhh.
            block_offsets[i])
        xvuz__qbom.setitem(yqip__qbhx, gnvq__jeitb, lsk__vok)
    data_tup = context.make_tuple(builder, types.Tuple([wwuc__rhh]), [
        hlyw__iqo._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    dgcp__otz = fromty.table_type
    xoi__qewli = cgutils.create_struct_proxy(dgcp__otz)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    hrac__ozidd = []
    for i, kxtlw__tbri in enumerate(toty.data):
        zlug__gfo = fromty.data[i]
        if kxtlw__tbri != zlug__gfo:
            acl__dovrl = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*acl__dovrl)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        lvfzn__txcbi = dgcp__otz.type_to_blk[kxtlw__tbri]
        rrzdi__ophew = getattr(xoi__qewli, f'block_{lvfzn__txcbi}')
        kni__smf = ListInstance(context, builder, types.List(kxtlw__tbri),
            rrzdi__ophew)
        ntcd__hdqo = context.get_constant(types.int64, dgcp__otz.
            block_offsets[i])
        rrx__mwvgl = kni__smf.getitem(ntcd__hdqo)
        if kxtlw__tbri != zlug__gfo:
            gnvq__jeitb = context.cast(builder, rrx__mwvgl, zlug__gfo,
                kxtlw__tbri)
            lsk__vok = False
        else:
            gnvq__jeitb = rrx__mwvgl
            lsk__vok = True
        if lsk__vok:
            context.nrt.incref(builder, kxtlw__tbri, gnvq__jeitb)
        hrac__ozidd.append(gnvq__jeitb)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), hrac__ozidd)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    img__xdopb, hal__baq, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    qfzb__tkhl = ColNamesMetaType(tuple(img__xdopb))
    wvjqf__mfws = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    wvjqf__mfws += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(hal__baq, index_arg))
    sbrgr__wvi = {}
    exec(wvjqf__mfws, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': qfzb__tkhl}, sbrgr__wvi)
    sne__irs = sbrgr__wvi['_init_df']
    return sne__irs


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    jqcga__rfbdo = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(jqcga__rfbdo, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    jqcga__rfbdo = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(jqcga__rfbdo, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    fxxu__fuy = ''
    if not is_overload_none(dtype):
        fxxu__fuy = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        gvgp__xjf = (len(data.types) - 1) // 2
        imbx__bur = [kxtlw__tbri.literal_value for kxtlw__tbri in data.
            types[1:gvgp__xjf + 1]]
        data_val_types = dict(zip(imbx__bur, data.types[gvgp__xjf + 1:]))
        hrac__ozidd = ['data[{}]'.format(i) for i in range(gvgp__xjf + 1, 2 *
            gvgp__xjf + 1)]
        data_dict = dict(zip(imbx__bur, hrac__ozidd))
        if is_overload_none(index):
            for i, kxtlw__tbri in enumerate(data.types[gvgp__xjf + 1:]):
                if isinstance(kxtlw__tbri, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(gvgp__xjf + 1 + i))
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
        rcu__markb = '.copy()' if copy else ''
        kvcpd__qof = get_overload_const_list(columns)
        gvgp__xjf = len(kvcpd__qof)
        data_val_types = {qhe__zac: data.copy(ndim=1) for qhe__zac in
            kvcpd__qof}
        hrac__ozidd = ['data[:,{}]{}'.format(i, rcu__markb) for i in range(
            gvgp__xjf)]
        data_dict = dict(zip(kvcpd__qof, hrac__ozidd))
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
    hal__baq = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[qhe__zac], df_len, fxxu__fuy) for qhe__zac in
        col_names))
    if len(col_names) == 0:
        hal__baq = '()'
    return col_names, hal__baq, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for qhe__zac in col_names:
        if qhe__zac in data_dict and is_iterable_type(data_val_types[qhe__zac]
            ):
            df_len = 'len({})'.format(data_dict[qhe__zac])
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
    if all(qhe__zac in data_dict for qhe__zac in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    bfq__brb = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for qhe__zac in col_names:
        if qhe__zac not in data_dict:
            data_dict[qhe__zac] = bfq__brb


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
            kxtlw__tbri = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df
                )
            return len(kxtlw__tbri)
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
        ppcse__vgci = idx.literal_value
        if isinstance(ppcse__vgci, int):
            vca__ihapa = tup.types[ppcse__vgci]
        elif isinstance(ppcse__vgci, slice):
            vca__ihapa = types.BaseTuple.from_types(tup.types[ppcse__vgci])
        return signature(vca__ihapa, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    ywfxq__vnw, idx = sig.args
    idx = idx.literal_value
    tup, qez__ckz = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(ywfxq__vnw)
        if not 0 <= idx < len(ywfxq__vnw):
            raise IndexError('cannot index at %d in %s' % (idx, ywfxq__vnw))
        tkhy__eiqb = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        ibopf__fzhjy = cgutils.unpack_tuple(builder, tup)[idx]
        tkhy__eiqb = context.make_tuple(builder, sig.return_type, ibopf__fzhjy)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, tkhy__eiqb)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, kfay__uneg, suffix_x,
            suffix_y, is_join, indicator, qez__ckz, qez__ckz) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        qpsq__xzzzd = {qhe__zac: i for i, qhe__zac in enumerate(left_on)}
        agkbu__yet = {qhe__zac: i for i, qhe__zac in enumerate(right_on)}
        soe__kxns = set(left_on) & set(right_on)
        vwe__psk = set(left_df.columns) & set(right_df.columns)
        dmi__jbzu = vwe__psk - soe__kxns
        bfl__ulc = '$_bodo_index_' in left_on
        eiaa__aoj = '$_bodo_index_' in right_on
        how = get_overload_const_str(kfay__uneg)
        khc__rmy = how in {'left', 'outer'}
        hvzf__xjcq = how in {'right', 'outer'}
        columns = []
        data = []
        if bfl__ulc:
            ohom__qgf = bodo.utils.typing.get_index_data_arr_types(left_df.
                index)[0]
        else:
            ohom__qgf = left_df.data[left_df.column_index[left_on[0]]]
        if eiaa__aoj:
            bwwxy__yvof = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            bwwxy__yvof = right_df.data[right_df.column_index[right_on[0]]]
        if bfl__ulc and not eiaa__aoj and not is_join.literal_value:
            aaly__ihzp = right_on[0]
            if aaly__ihzp in left_df.column_index:
                columns.append(aaly__ihzp)
                if (bwwxy__yvof == bodo.dict_str_arr_type and ohom__qgf ==
                    bodo.string_array_type):
                    lzq__uvpdx = bodo.string_array_type
                else:
                    lzq__uvpdx = bwwxy__yvof
                data.append(lzq__uvpdx)
        if eiaa__aoj and not bfl__ulc and not is_join.literal_value:
            mis__ydth = left_on[0]
            if mis__ydth in right_df.column_index:
                columns.append(mis__ydth)
                if (ohom__qgf == bodo.dict_str_arr_type and bwwxy__yvof ==
                    bodo.string_array_type):
                    lzq__uvpdx = bodo.string_array_type
                else:
                    lzq__uvpdx = ohom__qgf
                data.append(lzq__uvpdx)
        for zlug__gfo, mqufn__tsml in zip(left_df.data, left_df.columns):
            columns.append(str(mqufn__tsml) + suffix_x.literal_value if 
                mqufn__tsml in dmi__jbzu else mqufn__tsml)
            if mqufn__tsml in soe__kxns:
                if zlug__gfo == bodo.dict_str_arr_type:
                    zlug__gfo = right_df.data[right_df.column_index[
                        mqufn__tsml]]
                data.append(zlug__gfo)
            else:
                if (zlug__gfo == bodo.dict_str_arr_type and mqufn__tsml in
                    qpsq__xzzzd):
                    if eiaa__aoj:
                        zlug__gfo = bwwxy__yvof
                    else:
                        ibhrz__kvam = qpsq__xzzzd[mqufn__tsml]
                        ahlm__ezk = right_on[ibhrz__kvam]
                        zlug__gfo = right_df.data[right_df.column_index[
                            ahlm__ezk]]
                if hvzf__xjcq:
                    zlug__gfo = to_nullable_type(zlug__gfo)
                data.append(zlug__gfo)
        for zlug__gfo, mqufn__tsml in zip(right_df.data, right_df.columns):
            if mqufn__tsml not in soe__kxns:
                columns.append(str(mqufn__tsml) + suffix_y.literal_value if
                    mqufn__tsml in dmi__jbzu else mqufn__tsml)
                if (zlug__gfo == bodo.dict_str_arr_type and mqufn__tsml in
                    agkbu__yet):
                    if bfl__ulc:
                        zlug__gfo = ohom__qgf
                    else:
                        ibhrz__kvam = agkbu__yet[mqufn__tsml]
                        hfgr__aphir = left_on[ibhrz__kvam]
                        zlug__gfo = left_df.data[left_df.column_index[
                            hfgr__aphir]]
                if khc__rmy:
                    zlug__gfo = to_nullable_type(zlug__gfo)
                data.append(zlug__gfo)
        bed__dzq = get_overload_const_bool(indicator)
        if bed__dzq:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        tlhqp__fyngc = False
        if bfl__ulc and eiaa__aoj and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            tlhqp__fyngc = True
        elif bfl__ulc and not eiaa__aoj:
            index_typ = right_df.index
            tlhqp__fyngc = True
        elif eiaa__aoj and not bfl__ulc:
            index_typ = left_df.index
            tlhqp__fyngc = True
        if tlhqp__fyngc and isinstance(index_typ, bodo.hiframes.
            pd_index_ext.RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        bhdra__vhelo = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(bhdra__vhelo, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    bersy__wkwjs = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return bersy__wkwjs._getvalue()


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
    emjdu__csz = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    ddpi__izbbu = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', emjdu__csz, ddpi__izbbu,
        package_name='pandas', module_name='General')
    wvjqf__mfws = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        egx__gln = 0
        hal__baq = []
        names = []
        for i, ahm__nhf in enumerate(objs.types):
            assert isinstance(ahm__nhf, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(ahm__nhf, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ahm__nhf,
                'pandas.concat()')
            if isinstance(ahm__nhf, SeriesType):
                names.append(str(egx__gln))
                egx__gln += 1
                hal__baq.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(ahm__nhf.columns)
                for jqdn__bawm in range(len(ahm__nhf.data)):
                    hal__baq.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, jqdn__bawm))
        return bodo.hiframes.dataframe_impl._gen_init_df(wvjqf__mfws, names,
            ', '.join(hal__baq), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(kxtlw__tbri, DataFrameType) for kxtlw__tbri in
            objs.types)
        hrfsd__ecj = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            hrfsd__ecj.extend(df.columns)
        hrfsd__ecj = list(dict.fromkeys(hrfsd__ecj).keys())
        syr__krlw = {}
        for egx__gln, qhe__zac in enumerate(hrfsd__ecj):
            for i, df in enumerate(objs.types):
                if qhe__zac in df.column_index:
                    syr__krlw[f'arr_typ{egx__gln}'] = df.data[df.
                        column_index[qhe__zac]]
                    break
        assert len(syr__krlw) == len(hrfsd__ecj)
        rcda__uhk = []
        for egx__gln, qhe__zac in enumerate(hrfsd__ecj):
            args = []
            for i, df in enumerate(objs.types):
                if qhe__zac in df.column_index:
                    ifnl__kpjl = df.column_index[qhe__zac]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, ifnl__kpjl))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, egx__gln))
            wvjqf__mfws += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(egx__gln, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(wvjqf__mfws,
            hrfsd__ecj, ', '.join('A{}'.format(i) for i in range(len(
            hrfsd__ecj))), index, syr__krlw)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(kxtlw__tbri, SeriesType) for kxtlw__tbri in
            objs.types)
        wvjqf__mfws += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            wvjqf__mfws += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            wvjqf__mfws += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        wvjqf__mfws += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        sbrgr__wvi = {}
        exec(wvjqf__mfws, {'bodo': bodo, 'np': np, 'numba': numba}, sbrgr__wvi)
        return sbrgr__wvi['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for egx__gln, qhe__zac in enumerate(df_type.columns):
            wvjqf__mfws += '  arrs{} = []\n'.format(egx__gln)
            wvjqf__mfws += '  for i in range(len(objs)):\n'
            wvjqf__mfws += '    df = objs[i]\n'
            wvjqf__mfws += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(egx__gln))
            wvjqf__mfws += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(egx__gln))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            wvjqf__mfws += '  arrs_index = []\n'
            wvjqf__mfws += '  for i in range(len(objs)):\n'
            wvjqf__mfws += '    df = objs[i]\n'
            wvjqf__mfws += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(wvjqf__mfws,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        wvjqf__mfws += '  arrs = []\n'
        wvjqf__mfws += '  for i in range(len(objs)):\n'
        wvjqf__mfws += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        wvjqf__mfws += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            wvjqf__mfws += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            wvjqf__mfws += '  arrs_index = []\n'
            wvjqf__mfws += '  for i in range(len(objs)):\n'
            wvjqf__mfws += '    S = objs[i]\n'
            wvjqf__mfws += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            wvjqf__mfws += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        wvjqf__mfws += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        sbrgr__wvi = {}
        exec(wvjqf__mfws, {'bodo': bodo, 'np': np, 'numba': numba}, sbrgr__wvi)
        return sbrgr__wvi['impl']
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
        jqcga__rfbdo = df.copy(index=index)
        return signature(jqcga__rfbdo, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    ogxxi__ucg = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ogxxi__ucg._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    emjdu__csz = dict(index=index, name=name)
    ddpi__izbbu = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', emjdu__csz, ddpi__izbbu,
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
        syr__krlw = (types.Array(types.int64, 1, 'C'),) + df.data
        jcig__iuqev = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, syr__krlw)
        return signature(jcig__iuqev, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    ogxxi__ucg = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ogxxi__ucg._getvalue()


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
    ogxxi__ucg = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ogxxi__ucg._getvalue()


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
    ogxxi__ucg = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return ogxxi__ucg._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    is_already_shuffled=False, _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    pwx__kdtwy = get_overload_const_bool(check_duplicates)
    cqb__alsbl = not get_overload_const_bool(is_already_shuffled)
    wsaxq__imh = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    qtz__vafn = len(value_names) > 1
    eaf__bfvhh = None
    mxfvx__drjzm = None
    eij__itqg = None
    tyzcm__jkjp = None
    hsuo__xxdzk = isinstance(values_tup, types.UniTuple)
    if hsuo__xxdzk:
        fjgxz__kfg = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        fjgxz__kfg = [to_str_arr_if_dict_array(to_nullable_type(sfkpy__fhq)
            ) for sfkpy__fhq in values_tup]
    wvjqf__mfws = 'def impl(\n'
    wvjqf__mfws += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, is_already_shuffled=False, _constant_pivot_values=None, parallel=False
"""
    wvjqf__mfws += '):\n'
    wvjqf__mfws += (
        "    ev = tracing.Event('pivot_impl', is_parallel=parallel)\n")
    if cqb__alsbl:
        wvjqf__mfws += '    if parallel:\n'
        wvjqf__mfws += (
            "        ev_shuffle = tracing.Event('shuffle_pivot_index')\n")
        ray__xiim = ', '.join([f'array_to_info(index_tup[{i}])' for i in
            range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for
            i in range(len(columns_tup))] + [
            f'array_to_info(values_tup[{i}])' for i in range(len(values_tup))])
        wvjqf__mfws += f'        info_list = [{ray__xiim}]\n'
        wvjqf__mfws += (
            '        cpp_table = arr_info_list_to_table(info_list)\n')
        wvjqf__mfws += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
        fnczl__rrkxp = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
             for i in range(len(index_tup))])
        zns__ygya = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
             for i in range(len(columns_tup))])
        ojac__wfba = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
             for i in range(len(values_tup))])
        wvjqf__mfws += f'        index_tup = ({fnczl__rrkxp},)\n'
        wvjqf__mfws += f'        columns_tup = ({zns__ygya},)\n'
        wvjqf__mfws += f'        values_tup = ({ojac__wfba},)\n'
        wvjqf__mfws += '        delete_table(cpp_table)\n'
        wvjqf__mfws += '        delete_table(out_cpp_table)\n'
        wvjqf__mfws += '        ev_shuffle.finalize()\n'
    wvjqf__mfws += '    columns_arr = columns_tup[0]\n'
    if hsuo__xxdzk:
        wvjqf__mfws += '    values_arrs = [arr for arr in values_tup]\n'
    fhv__rwow = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    wvjqf__mfws += f'    new_index_tup = ({fhv__rwow},)\n'
    wvjqf__mfws += """    ev_unique = tracing.Event('pivot_unique_index_map', is_parallel=parallel)
"""
    wvjqf__mfws += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    wvjqf__mfws += '        new_index_tup\n'
    wvjqf__mfws += '    )\n'
    wvjqf__mfws += '    n_rows = len(unique_index_arr_tup[0])\n'
    wvjqf__mfws += '    num_values_arrays = len(values_tup)\n'
    wvjqf__mfws += '    n_unique_pivots = len(pivot_values)\n'
    if hsuo__xxdzk:
        wvjqf__mfws += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        wvjqf__mfws += '    n_cols = n_unique_pivots\n'
    wvjqf__mfws += '    col_map = {}\n'
    wvjqf__mfws += '    for i in range(n_unique_pivots):\n'
    wvjqf__mfws += (
        '        if bodo.libs.array_kernels.isna(pivot_values, i):\n')
    wvjqf__mfws += '            raise ValueError(\n'
    wvjqf__mfws += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    wvjqf__mfws += '            )\n'
    wvjqf__mfws += '        col_map[pivot_values[i]] = i\n'
    wvjqf__mfws += '    ev_unique.finalize()\n'
    wvjqf__mfws += (
        "    ev_alloc = tracing.Event('pivot_alloc', is_parallel=parallel)\n")
    vzk__rpznc = False
    for i, yfwi__fruvs in enumerate(fjgxz__kfg):
        if is_str_arr_type(yfwi__fruvs):
            vzk__rpznc = True
            wvjqf__mfws += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            wvjqf__mfws += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if vzk__rpznc:
        if pwx__kdtwy:
            wvjqf__mfws += '    nbytes = (n_rows + 7) >> 3\n'
            wvjqf__mfws += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        wvjqf__mfws += '    for i in range(len(columns_arr)):\n'
        wvjqf__mfws += '        col_name = columns_arr[i]\n'
        wvjqf__mfws += '        pivot_idx = col_map[col_name]\n'
        wvjqf__mfws += '        row_idx = row_vector[i]\n'
        if pwx__kdtwy:
            wvjqf__mfws += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            wvjqf__mfws += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            wvjqf__mfws += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            wvjqf__mfws += '        else:\n'
            wvjqf__mfws += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if hsuo__xxdzk:
            wvjqf__mfws += '        for j in range(num_values_arrays):\n'
            wvjqf__mfws += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            wvjqf__mfws += '            len_arr = len_arrs_0[col_idx]\n'
            wvjqf__mfws += '            values_arr = values_arrs[j]\n'
            wvjqf__mfws += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            wvjqf__mfws += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            wvjqf__mfws += '                len_arr[row_idx] = str_val_len\n'
            wvjqf__mfws += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, yfwi__fruvs in enumerate(fjgxz__kfg):
                if is_str_arr_type(yfwi__fruvs):
                    wvjqf__mfws += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    wvjqf__mfws += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    wvjqf__mfws += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    wvjqf__mfws += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    wvjqf__mfws += f"    ev_alloc.add_attribute('num_rows', n_rows)\n"
    for i, yfwi__fruvs in enumerate(fjgxz__kfg):
        if is_str_arr_type(yfwi__fruvs):
            wvjqf__mfws += f'    data_arrs_{i} = [\n'
            wvjqf__mfws += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            wvjqf__mfws += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            wvjqf__mfws += '        )\n'
            wvjqf__mfws += '        for i in range(n_cols)\n'
            wvjqf__mfws += '    ]\n'
            wvjqf__mfws += f'    if tracing.is_tracing():\n'
            wvjqf__mfws += '         for i in range(n_cols):'
            wvjqf__mfws += f"""            ev_alloc.add_attribute('total_str_chars_out_column_{i}_' + str(i), total_lens_{i}[i])
"""
        else:
            wvjqf__mfws += f'    data_arrs_{i} = [\n'
            wvjqf__mfws += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            wvjqf__mfws += '        for _ in range(n_cols)\n'
            wvjqf__mfws += '    ]\n'
    if not vzk__rpznc and pwx__kdtwy:
        wvjqf__mfws += '    nbytes = (n_rows + 7) >> 3\n'
        wvjqf__mfws += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    wvjqf__mfws += '    ev_alloc.finalize()\n'
    wvjqf__mfws += (
        "    ev_fill = tracing.Event('pivot_fill_data', is_parallel=parallel)\n"
        )
    wvjqf__mfws += '    for i in range(len(columns_arr)):\n'
    wvjqf__mfws += '        col_name = columns_arr[i]\n'
    wvjqf__mfws += '        pivot_idx = col_map[col_name]\n'
    wvjqf__mfws += '        row_idx = row_vector[i]\n'
    if not vzk__rpznc and pwx__kdtwy:
        wvjqf__mfws += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        wvjqf__mfws += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        wvjqf__mfws += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        wvjqf__mfws += '        else:\n'
        wvjqf__mfws += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
    if hsuo__xxdzk:
        wvjqf__mfws += '        for j in range(num_values_arrays):\n'
        wvjqf__mfws += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        wvjqf__mfws += '            col_arr = data_arrs_0[col_idx]\n'
        wvjqf__mfws += '            values_arr = values_arrs[j]\n'
        wvjqf__mfws += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        wvjqf__mfws += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        wvjqf__mfws += '            else:\n'
        wvjqf__mfws += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, yfwi__fruvs in enumerate(fjgxz__kfg):
            wvjqf__mfws += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            wvjqf__mfws += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            wvjqf__mfws += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            wvjqf__mfws += f'        else:\n'
            wvjqf__mfws += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        wvjqf__mfws += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        eaf__bfvhh = index_names.meta[0]
    else:
        wvjqf__mfws += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        eaf__bfvhh = tuple(index_names.meta)
    wvjqf__mfws += f'    if tracing.is_tracing():\n'
    wvjqf__mfws += f'        index_nbytes = index.nbytes\n'
    wvjqf__mfws += f"        ev.add_attribute('index_nbytes', index_nbytes)\n"
    if not wsaxq__imh:
        eij__itqg = columns_name.meta[0]
        if qtz__vafn:
            wvjqf__mfws += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            mxfvx__drjzm = value_names.meta
            if all(isinstance(qhe__zac, str) for qhe__zac in mxfvx__drjzm):
                mxfvx__drjzm = pd.array(mxfvx__drjzm, 'string')
            elif all(isinstance(qhe__zac, int) for qhe__zac in mxfvx__drjzm):
                mxfvx__drjzm = np.array(mxfvx__drjzm, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(mxfvx__drjzm.dtype, pd.StringDtype):
                wvjqf__mfws += '    total_chars = 0\n'
                wvjqf__mfws += f'    for i in range({len(value_names)}):\n'
                wvjqf__mfws += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                wvjqf__mfws += '        total_chars += value_name_str_len\n'
                wvjqf__mfws += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                wvjqf__mfws += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                wvjqf__mfws += '    total_chars = 0\n'
                wvjqf__mfws += '    for i in range(len(pivot_values)):\n'
                wvjqf__mfws += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                wvjqf__mfws += '        total_chars += pivot_val_str_len\n'
                wvjqf__mfws += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                wvjqf__mfws += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            wvjqf__mfws += f'    for i in range({len(value_names)}):\n'
            wvjqf__mfws += '        for j in range(len(pivot_values)):\n'
            wvjqf__mfws += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            wvjqf__mfws += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            wvjqf__mfws += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            wvjqf__mfws += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    wvjqf__mfws += '    ev_fill.finalize()\n'
    dgcp__otz = None
    if wsaxq__imh:
        if qtz__vafn:
            sgre__wondv = []
            for mbj__gtse in _constant_pivot_values.meta:
                for elkez__ctggf in value_names.meta:
                    sgre__wondv.append((mbj__gtse, elkez__ctggf))
            column_names = tuple(sgre__wondv)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        tyzcm__jkjp = ColNamesMetaType(column_names)
        aix__qkpxo = []
        for sfkpy__fhq in fjgxz__kfg:
            aix__qkpxo.extend([sfkpy__fhq] * len(_constant_pivot_values))
        phgf__gsovc = tuple(aix__qkpxo)
        dgcp__otz = TableType(phgf__gsovc)
        wvjqf__mfws += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        wvjqf__mfws += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, sfkpy__fhq in enumerate(fjgxz__kfg):
            wvjqf__mfws += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {dgcp__otz.type_to_blk[sfkpy__fhq]})
"""
        wvjqf__mfws += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        wvjqf__mfws += '        (table,), index, columns_typ\n'
        wvjqf__mfws += '    )\n'
    else:
        ltroz__ressi = ', '.join(f'data_arrs_{i}' for i in range(len(
            fjgxz__kfg)))
        wvjqf__mfws += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({ltroz__ressi},), n_rows)
"""
        wvjqf__mfws += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        wvjqf__mfws += '        (table,), index, column_index\n'
        wvjqf__mfws += '    )\n'
    wvjqf__mfws += '    ev.finalize()\n'
    wvjqf__mfws += '    return result\n'
    sbrgr__wvi = {}
    qkox__uong = {f'data_arr_typ_{i}': yfwi__fruvs for i, yfwi__fruvs in
        enumerate(fjgxz__kfg)}
    dzip__ubufo = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        dgcp__otz, 'columns_typ': tyzcm__jkjp, 'index_names_lit':
        eaf__bfvhh, 'value_names_lit': mxfvx__drjzm, 'columns_name_lit':
        eij__itqg, **qkox__uong, 'tracing': tracing}
    exec(wvjqf__mfws, dzip__ubufo, sbrgr__wvi)
    impl = sbrgr__wvi['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    bvh__pwkx = {}
    bvh__pwkx['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, yui__opr in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        moq__gkf = None
        if isinstance(yui__opr, bodo.DatetimeArrayType):
            oxs__wef = 'datetimetz'
            yaegq__vllwm = 'datetime64[ns]'
            if isinstance(yui__opr.tz, int):
                hpi__nyoe = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(yui__opr.tz))
            else:
                hpi__nyoe = pd.DatetimeTZDtype(tz=yui__opr.tz).tz
            moq__gkf = {'timezone': pa.lib.tzinfo_to_string(hpi__nyoe)}
        elif isinstance(yui__opr, types.Array) or yui__opr == boolean_array:
            oxs__wef = yaegq__vllwm = yui__opr.dtype.name
            if yaegq__vllwm.startswith('datetime'):
                oxs__wef = 'datetime'
        elif is_str_arr_type(yui__opr):
            oxs__wef = 'unicode'
            yaegq__vllwm = 'object'
        elif yui__opr == binary_array_type:
            oxs__wef = 'bytes'
            yaegq__vllwm = 'object'
        elif isinstance(yui__opr, DecimalArrayType):
            oxs__wef = yaegq__vllwm = 'object'
        elif isinstance(yui__opr, IntegerArrayType):
            uafcv__uizu = yui__opr.dtype.name
            if uafcv__uizu.startswith('int'):
                oxs__wef = 'Int' + uafcv__uizu[3:]
            elif uafcv__uizu.startswith('uint'):
                oxs__wef = 'UInt' + uafcv__uizu[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, yui__opr))
            yaegq__vllwm = yui__opr.dtype.name
        elif yui__opr == datetime_date_array_type:
            oxs__wef = 'datetime'
            yaegq__vllwm = 'object'
        elif isinstance(yui__opr, (StructArrayType, ArrayItemArrayType)):
            oxs__wef = 'object'
            yaegq__vllwm = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, yui__opr))
        iqjxq__bixj = {'name': col_name, 'field_name': col_name,
            'pandas_type': oxs__wef, 'numpy_type': yaegq__vllwm, 'metadata':
            moq__gkf}
        bvh__pwkx['columns'].append(iqjxq__bixj)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            fdg__sgasf = '__index_level_0__'
            ghrtk__kzeq = None
        else:
            fdg__sgasf = '%s'
            ghrtk__kzeq = '%s'
        bvh__pwkx['index_columns'] = [fdg__sgasf]
        bvh__pwkx['columns'].append({'name': ghrtk__kzeq, 'field_name':
            fdg__sgasf, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        bvh__pwkx['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        bvh__pwkx['index_columns'] = []
    bvh__pwkx['pandas_version'] = pd.__version__
    return bvh__pwkx


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
        mapz__efk = []
        for pceab__zbjei in partition_cols:
            try:
                idx = df.columns.index(pceab__zbjei)
            except ValueError as wirmw__xxjhu:
                raise BodoError(
                    f'Partition column {pceab__zbjei} is not in dataframe')
            mapz__efk.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    aret__qeqz = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType
        )
    bkdpf__tucyd = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not aret__qeqz)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not aret__qeqz or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and aret__qeqz and not is_overload_true(_is_parallel)
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
        kgfcj__habt = df.runtime_data_types
        ilxr__ihc = len(kgfcj__habt)
        moq__gkf = gen_pandas_parquet_metadata([''] * ilxr__ihc,
            kgfcj__habt, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        uffs__rqdbx = moq__gkf['columns'][:ilxr__ihc]
        moq__gkf['columns'] = moq__gkf['columns'][ilxr__ihc:]
        uffs__rqdbx = [json.dumps(eej__iqud).replace('""', '{0}') for
            eej__iqud in uffs__rqdbx]
        yfn__nfjom = json.dumps(moq__gkf)
        urc__hdm = '"columns": ['
        rfvq__zvdnh = yfn__nfjom.find(urc__hdm)
        if rfvq__zvdnh == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        ngkfy__aqihh = rfvq__zvdnh + len(urc__hdm)
        jday__fgm = yfn__nfjom[:ngkfy__aqihh]
        yfn__nfjom = yfn__nfjom[ngkfy__aqihh:]
        mtamm__wbnda = len(moq__gkf['columns'])
    else:
        yfn__nfjom = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and aret__qeqz:
        yfn__nfjom = yfn__nfjom.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            yfn__nfjom = yfn__nfjom.replace('"%s"', '%s')
    if not df.is_table_format:
        hal__baq = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    wvjqf__mfws = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        wvjqf__mfws += '    py_table = get_dataframe_table(df)\n'
        wvjqf__mfws += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        wvjqf__mfws += '    info_list = [{}]\n'.format(hal__baq)
        wvjqf__mfws += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        wvjqf__mfws += '    columns_index = get_dataframe_column_names(df)\n'
        wvjqf__mfws += '    names_arr = index_to_array(columns_index)\n'
        wvjqf__mfws += '    col_names = array_to_info(names_arr)\n'
    else:
        wvjqf__mfws += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and bkdpf__tucyd:
        wvjqf__mfws += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        uoyg__whbzc = True
    else:
        wvjqf__mfws += '    index_col = array_to_info(np.empty(0))\n'
        uoyg__whbzc = False
    if df.has_runtime_cols:
        wvjqf__mfws += '    columns_lst = []\n'
        wvjqf__mfws += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            wvjqf__mfws += f'    for _ in range(len(py_table.block_{i})):\n'
            wvjqf__mfws += f"""        columns_lst.append({uffs__rqdbx[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            wvjqf__mfws += '        num_cols += 1\n'
        if mtamm__wbnda:
            wvjqf__mfws += "    columns_lst.append('')\n"
        wvjqf__mfws += '    columns_str = ", ".join(columns_lst)\n'
        wvjqf__mfws += ('    metadata = """' + jday__fgm +
            '""" + columns_str + """' + yfn__nfjom + '"""\n')
    else:
        wvjqf__mfws += '    metadata = """' + yfn__nfjom + '"""\n'
    wvjqf__mfws += '    if compression is None:\n'
    wvjqf__mfws += "        compression = 'none'\n"
    wvjqf__mfws += '    if df.index.name is not None:\n'
    wvjqf__mfws += '        name_ptr = df.index.name\n'
    wvjqf__mfws += '    else:\n'
    wvjqf__mfws += "        name_ptr = 'null'\n"
    wvjqf__mfws += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    dmumk__ibpnt = None
    if partition_cols:
        dmumk__ibpnt = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        jfz__wyhih = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in mapz__efk)
        if jfz__wyhih:
            wvjqf__mfws += '    cat_info_list = [{}]\n'.format(jfz__wyhih)
            wvjqf__mfws += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            wvjqf__mfws += '    cat_table = table\n'
        wvjqf__mfws += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        wvjqf__mfws += (
            f'    part_cols_idxs = np.array({mapz__efk}, dtype=np.int32)\n')
        wvjqf__mfws += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        wvjqf__mfws += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        wvjqf__mfws += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        wvjqf__mfws += (
            '                            unicode_to_utf8(compression),\n')
        wvjqf__mfws += '                            _is_parallel,\n'
        wvjqf__mfws += (
            '                            unicode_to_utf8(bucket_region),\n')
        wvjqf__mfws += '                            row_group_size,\n'
        wvjqf__mfws += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        wvjqf__mfws += '    delete_table_decref_arrays(table)\n'
        wvjqf__mfws += '    delete_info_decref_array(index_col)\n'
        wvjqf__mfws += (
            '    delete_info_decref_array(col_names_no_partitions)\n')
        wvjqf__mfws += '    delete_info_decref_array(col_names)\n'
        if jfz__wyhih:
            wvjqf__mfws += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        wvjqf__mfws += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        wvjqf__mfws += (
            '                            table, col_names, index_col,\n')
        wvjqf__mfws += '                            ' + str(uoyg__whbzc
            ) + ',\n'
        wvjqf__mfws += (
            '                            unicode_to_utf8(metadata),\n')
        wvjqf__mfws += (
            '                            unicode_to_utf8(compression),\n')
        wvjqf__mfws += (
            '                            _is_parallel, 1, df.index.start,\n')
        wvjqf__mfws += (
            '                            df.index.stop, df.index.step,\n')
        wvjqf__mfws += (
            '                            unicode_to_utf8(name_ptr),\n')
        wvjqf__mfws += (
            '                            unicode_to_utf8(bucket_region),\n')
        wvjqf__mfws += '                            row_group_size,\n'
        wvjqf__mfws += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        wvjqf__mfws += '    delete_table_decref_arrays(table)\n'
        wvjqf__mfws += '    delete_info_decref_array(index_col)\n'
        wvjqf__mfws += '    delete_info_decref_array(col_names)\n'
    else:
        wvjqf__mfws += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        wvjqf__mfws += (
            '                            table, col_names, index_col,\n')
        wvjqf__mfws += '                            ' + str(uoyg__whbzc
            ) + ',\n'
        wvjqf__mfws += (
            '                            unicode_to_utf8(metadata),\n')
        wvjqf__mfws += (
            '                            unicode_to_utf8(compression),\n')
        wvjqf__mfws += (
            '                            _is_parallel, 0, 0, 0, 0,\n')
        wvjqf__mfws += (
            '                            unicode_to_utf8(name_ptr),\n')
        wvjqf__mfws += (
            '                            unicode_to_utf8(bucket_region),\n')
        wvjqf__mfws += '                            row_group_size,\n'
        wvjqf__mfws += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        wvjqf__mfws += '    delete_table_decref_arrays(table)\n'
        wvjqf__mfws += '    delete_info_decref_array(index_col)\n'
        wvjqf__mfws += '    delete_info_decref_array(col_names)\n'
    sbrgr__wvi = {}
    if df.has_runtime_cols:
        eadwx__ooj = None
    else:
        for mqufn__tsml in df.columns:
            if not isinstance(mqufn__tsml, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        eadwx__ooj = pd.array(df.columns)
    exec(wvjqf__mfws, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': eadwx__ooj,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': dmumk__ibpnt,
        'get_dataframe_column_names': get_dataframe_column_names,
        'fix_arr_dtype': fix_arr_dtype, 'decode_if_dict_array':
        decode_if_dict_array, 'decode_if_dict_table': decode_if_dict_table},
        sbrgr__wvi)
    suncn__zqof = sbrgr__wvi['df_to_parquet']
    return suncn__zqof


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    brjlp__dpbvs = 'all_ok'
    ujucf__jbod, aaq__nqmz = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        ooee__ytqcq = 100
        if chunksize is None:
            giqy__zgqrw = ooee__ytqcq
        else:
            giqy__zgqrw = min(chunksize, ooee__ytqcq)
        if _is_table_create:
            df = df.iloc[:giqy__zgqrw, :]
        else:
            df = df.iloc[giqy__zgqrw:, :]
            if len(df) == 0:
                return brjlp__dpbvs
    rfoc__qwp = df.columns
    try:
        if ujucf__jbod == 'snowflake':
            if aaq__nqmz and con.count(aaq__nqmz) == 1:
                con = con.replace(aaq__nqmz, quote(aaq__nqmz))
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
                df.columns = [(qhe__zac.upper() if qhe__zac.islower() else
                    qhe__zac) for qhe__zac in df.columns]
            except ImportError as wirmw__xxjhu:
                brjlp__dpbvs = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return brjlp__dpbvs
        if ujucf__jbod == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            pbx__cyq = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            qqv__zvw = bodo.typeof(df)
            gblt__qra = {}
            for qhe__zac, vdc__blxm in zip(qqv__zvw.columns, qqv__zvw.data):
                if df[qhe__zac].dtype == 'object':
                    if vdc__blxm == datetime_date_array_type:
                        gblt__qra[qhe__zac] = sa.types.Date
                    elif vdc__blxm in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not pbx__cyq or pbx__cyq == '0'
                        ):
                        gblt__qra[qhe__zac] = VARCHAR2(4000)
            dtype = gblt__qra
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as gjrs__piade:
            brjlp__dpbvs = gjrs__piade.args[0]
            if ujucf__jbod == 'oracle' and 'ORA-12899' in brjlp__dpbvs:
                brjlp__dpbvs += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return brjlp__dpbvs
    finally:
        df.columns = rfoc__qwp


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
    wvjqf__mfws = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    wvjqf__mfws += f"    if con.startswith('iceberg'):\n"
    wvjqf__mfws += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    wvjqf__mfws += f'        if schema is None:\n'
    wvjqf__mfws += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    wvjqf__mfws += f'        if chunksize is not None:\n'
    wvjqf__mfws += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    wvjqf__mfws += f'        if index and bodo.get_rank() == 0:\n'
    wvjqf__mfws += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    wvjqf__mfws += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    wvjqf__mfws += f"""            warnings.warn('index_label is not supported for Iceberg tables.')
"""
    if df.is_table_format:
        wvjqf__mfws += f'        py_table = get_dataframe_table(df)\n'
        wvjqf__mfws += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        hal__baq = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        wvjqf__mfws += f'        info_list = [{hal__baq}]\n'
        wvjqf__mfws += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        wvjqf__mfws += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        wvjqf__mfws += f'        names_arr = index_to_array(columns_index)\n'
        wvjqf__mfws += f'        col_names = array_to_info(names_arr)\n'
    else:
        wvjqf__mfws += f'        col_names = array_to_info(col_names_arr)\n'
    wvjqf__mfws += """        bodo.io.iceberg.iceberg_write(
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
    wvjqf__mfws += f'        delete_table_decref_arrays(table)\n'
    wvjqf__mfws += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        eadwx__ooj = None
    else:
        for mqufn__tsml in df.columns:
            if not isinstance(mqufn__tsml, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        eadwx__ooj = pd.array(df.columns)
    wvjqf__mfws += f'    else:\n'
    wvjqf__mfws += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    wvjqf__mfws += f"        err_msg = 'unset'\n"
    wvjqf__mfws += f'        if rank != 0:\n'
    wvjqf__mfws += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    wvjqf__mfws += f'        elif rank == 0:\n'
    wvjqf__mfws += f'            err_msg = to_sql_exception_guard_encaps(\n'
    wvjqf__mfws += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    wvjqf__mfws += f'                          chunksize, dtype, method,\n'
    wvjqf__mfws += f'                          True, _is_parallel,\n'
    wvjqf__mfws += f'                      )\n'
    wvjqf__mfws += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    wvjqf__mfws += f"        if_exists = 'append'\n"
    wvjqf__mfws += f"        if _is_parallel and err_msg == 'all_ok':\n"
    wvjqf__mfws += f'            err_msg = to_sql_exception_guard_encaps(\n'
    wvjqf__mfws += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    wvjqf__mfws += f'                          chunksize, dtype, method,\n'
    wvjqf__mfws += f'                          False, _is_parallel,\n'
    wvjqf__mfws += f'                      )\n'
    wvjqf__mfws += f"        if err_msg != 'all_ok':\n"
    wvjqf__mfws += f"            print('err_msg=', err_msg)\n"
    wvjqf__mfws += (
        f"            raise ValueError('error in to_sql() operation')\n")
    sbrgr__wvi = {}
    exec(wvjqf__mfws, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_to_cpp_table':
        py_table_to_cpp_table, 'py_table_typ': df.table_type,
        'col_names_arr': eadwx__ooj, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'delete_info_decref_array':
        delete_info_decref_array, 'arr_info_list_to_table':
        arr_info_list_to_table, 'index_to_array': index_to_array,
        'pyarrow_table_schema': bodo.io.iceberg.pyarrow_schema(df),
        'to_sql_exception_guard_encaps': to_sql_exception_guard_encaps,
        'warnings': warnings}, sbrgr__wvi)
    _impl = sbrgr__wvi['df_to_sql']
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
        aeuv__sbn = get_overload_const_str(path_or_buf)
        if aeuv__sbn.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        dcztd__llvy = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(dcztd__llvy), unicode_to_utf8(
                _bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(dcztd__llvy), unicode_to_utf8(
                _bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    oqvhu__mvrly = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    ica__dshmt = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', oqvhu__mvrly, ica__dshmt,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    wvjqf__mfws = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        axq__aixn = data.data.dtype.categories
        wvjqf__mfws += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        axq__aixn = data.dtype.categories
        wvjqf__mfws += '  data_values = data\n'
    gvgp__xjf = len(axq__aixn)
    wvjqf__mfws += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    wvjqf__mfws += '  numba.parfors.parfor.init_prange()\n'
    wvjqf__mfws += '  n = len(data_values)\n'
    for i in range(gvgp__xjf):
        wvjqf__mfws += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    wvjqf__mfws += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    wvjqf__mfws += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for jqdn__bawm in range(gvgp__xjf):
        wvjqf__mfws += '          data_arr_{}[i] = 0\n'.format(jqdn__bawm)
    wvjqf__mfws += '      else:\n'
    for fzxak__zoe in range(gvgp__xjf):
        wvjqf__mfws += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            fzxak__zoe)
    hal__baq = ', '.join(f'data_arr_{i}' for i in range(gvgp__xjf))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(axq__aixn[0], np.datetime64):
        axq__aixn = tuple(pd.Timestamp(qhe__zac) for qhe__zac in axq__aixn)
    elif isinstance(axq__aixn[0], np.timedelta64):
        axq__aixn = tuple(pd.Timedelta(qhe__zac) for qhe__zac in axq__aixn)
    return bodo.hiframes.dataframe_impl._gen_init_df(wvjqf__mfws, axq__aixn,
        hal__baq, index)


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
    for nyzr__zeywj in pd_unsupported:
        lhza__rfj = mod_name + '.' + nyzr__zeywj.__name__
        overload(nyzr__zeywj, no_unliteral=True)(create_unsupported_overload
            (lhza__rfj))


def _install_dataframe_unsupported():
    for jdi__xtfr in dataframe_unsupported_attrs:
        kxyxc__ilrm = 'DataFrame.' + jdi__xtfr
        overload_attribute(DataFrameType, jdi__xtfr)(
            create_unsupported_overload(kxyxc__ilrm))
    for lhza__rfj in dataframe_unsupported:
        kxyxc__ilrm = 'DataFrame.' + lhza__rfj + '()'
        overload_method(DataFrameType, lhza__rfj)(create_unsupported_overload
            (kxyxc__ilrm))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
