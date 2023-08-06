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
            wdcvs__yggw = f'{len(self.data)} columns of types {set(self.data)}'
            gzp__lyvi = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({wdcvs__yggw}, {self.index}, {gzp__lyvi}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {qjwah__jmsvp: i for i, qjwah__jmsvp in enumerate(self.columns)}

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
            qxqen__gdppb = (self.index if self.index == other.index else
                self.index.unify(typingctx, other.index))
            data = tuple(vxu__vnyxi.unify(typingctx, bpknr__liroh) if 
                vxu__vnyxi != bpknr__liroh else vxu__vnyxi for vxu__vnyxi,
                bpknr__liroh in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if qxqen__gdppb is not None and None not in data:
                return DataFrameType(data, qxqen__gdppb, self.columns, dist,
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
        return all(vxu__vnyxi.is_precise() for vxu__vnyxi in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        lleax__dwth = self.columns.index(col_name)
        gqujm__jank = tuple(list(self.data[:lleax__dwth]) + [new_type] +
            list(self.data[lleax__dwth + 1:]))
        return DataFrameType(gqujm__jank, self.index, self.columns, self.
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
        lmeud__ffko = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            lmeud__ffko.append(('columns', fe_type.df_type.runtime_colname_typ)
                )
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, lmeud__ffko)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        lmeud__ffko = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, lmeud__ffko)


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
        gjiha__fna = 'n',
        etbu__rqhpl = {'n': 5}
        zdnds__zkm, gsi__opqq = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, gjiha__fna, etbu__rqhpl)
        viis__mhjm = gsi__opqq[0]
        if not is_overload_int(viis__mhjm):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        idx__leezj = df.copy()
        return idx__leezj(*gsi__opqq).replace(pysig=zdnds__zkm)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        cbw__qujx = (df,) + args
        gjiha__fna = 'df', 'method', 'min_periods'
        etbu__rqhpl = {'method': 'pearson', 'min_periods': 1}
        vftvr__hcl = 'method',
        zdnds__zkm, gsi__opqq = bodo.utils.typing.fold_typing_args(func_name,
            cbw__qujx, kws, gjiha__fna, etbu__rqhpl, vftvr__hcl)
        uuywa__eblej = gsi__opqq[2]
        if not is_overload_int(uuywa__eblej):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        gdpa__uxx = []
        soahd__pifln = []
        for qjwah__jmsvp, vqa__lysi in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(vqa__lysi.dtype):
                gdpa__uxx.append(qjwah__jmsvp)
                soahd__pifln.append(types.Array(types.float64, 1, 'A'))
        if len(gdpa__uxx) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        soahd__pifln = tuple(soahd__pifln)
        gdpa__uxx = tuple(gdpa__uxx)
        index_typ = bodo.utils.typing.type_col_to_index(gdpa__uxx)
        idx__leezj = DataFrameType(soahd__pifln, index_typ, gdpa__uxx)
        return idx__leezj(*gsi__opqq).replace(pysig=zdnds__zkm)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        nwsm__wesx = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        uwwda__ztyo = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        rpi__wlyl = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        kiut__ottds = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        rmsz__uaqfx = dict(raw=uwwda__ztyo, result_type=rpi__wlyl)
        zsopj__rdu = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', rmsz__uaqfx, zsopj__rdu,
            package_name='pandas', module_name='DataFrame')
        lev__rwhd = True
        if types.unliteral(nwsm__wesx) == types.unicode_type:
            if not is_overload_constant_str(nwsm__wesx):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            lev__rwhd = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        xaf__wkkjv = get_overload_const_int(axis)
        if lev__rwhd and xaf__wkkjv != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif xaf__wkkjv not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        nrsd__kmx = []
        for arr_typ in df.data:
            tlwv__wpdz = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            wdn__htxue = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(tlwv__wpdz), types.int64), {}
                ).return_type
            nrsd__kmx.append(wdn__htxue)
        jvmk__lok = types.none
        mhjca__gwmq = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(qjwah__jmsvp) for qjwah__jmsvp in df.
            columns)), None)
        qqyy__spbaj = types.BaseTuple.from_types(nrsd__kmx)
        qzwyx__klf = types.Tuple([types.bool_] * len(qqyy__spbaj))
        kch__mon = bodo.NullableTupleType(qqyy__spbaj, qzwyx__klf)
        oxq__fakqs = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if oxq__fakqs == types.NPDatetime('ns'):
            oxq__fakqs = bodo.pd_timestamp_type
        if oxq__fakqs == types.NPTimedelta('ns'):
            oxq__fakqs = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(qqyy__spbaj):
            tojfu__xwyth = HeterogeneousSeriesType(kch__mon, mhjca__gwmq,
                oxq__fakqs)
        else:
            tojfu__xwyth = SeriesType(qqyy__spbaj.dtype, kch__mon,
                mhjca__gwmq, oxq__fakqs)
        ced__slepw = tojfu__xwyth,
        if kiut__ottds is not None:
            ced__slepw += tuple(kiut__ottds.types)
        try:
            if not lev__rwhd:
                kgkp__symic = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(nwsm__wesx), self.context,
                    'DataFrame.apply', axis if xaf__wkkjv == 1 else None)
            else:
                kgkp__symic = get_const_func_output_type(nwsm__wesx,
                    ced__slepw, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as mhui__ppso:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', mhui__ppso)
                )
        if lev__rwhd:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(kgkp__symic, (SeriesType, HeterogeneousSeriesType)
                ) and kgkp__symic.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(kgkp__symic, HeterogeneousSeriesType):
                pvzp__vohi, fsyh__nwt = kgkp__symic.const_info
                if isinstance(kgkp__symic.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    cow__dvd = kgkp__symic.data.tuple_typ.types
                elif isinstance(kgkp__symic.data, types.Tuple):
                    cow__dvd = kgkp__symic.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                yzdbz__wlenq = tuple(to_nullable_type(dtype_to_array_type(
                    gqzon__kla)) for gqzon__kla in cow__dvd)
                zurup__oermi = DataFrameType(yzdbz__wlenq, df.index, fsyh__nwt)
            elif isinstance(kgkp__symic, SeriesType):
                dklb__ocgxm, fsyh__nwt = kgkp__symic.const_info
                yzdbz__wlenq = tuple(to_nullable_type(dtype_to_array_type(
                    kgkp__symic.dtype)) for pvzp__vohi in range(dklb__ocgxm))
                zurup__oermi = DataFrameType(yzdbz__wlenq, df.index, fsyh__nwt)
            else:
                mce__drnhe = get_udf_out_arr_type(kgkp__symic)
                zurup__oermi = SeriesType(mce__drnhe.dtype, mce__drnhe, df.
                    index, None)
        else:
            zurup__oermi = kgkp__symic
        fdt__saobm = ', '.join("{} = ''".format(vxu__vnyxi) for vxu__vnyxi in
            kws.keys())
        pcqlb__skaxy = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {fdt__saobm}):
"""
        pcqlb__skaxy += '    pass\n'
        grax__fqnb = {}
        exec(pcqlb__skaxy, {}, grax__fqnb)
        zwpvk__evcza = grax__fqnb['apply_stub']
        zdnds__zkm = numba.core.utils.pysignature(zwpvk__evcza)
        xpapj__fky = (nwsm__wesx, axis, uwwda__ztyo, rpi__wlyl, kiut__ottds
            ) + tuple(kws.values())
        return signature(zurup__oermi, *xpapj__fky).replace(pysig=zdnds__zkm)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        gjiha__fna = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        etbu__rqhpl = {'x': None, 'y': None, 'kind': 'line', 'figsize':
            None, 'ax': None, 'subplots': False, 'sharex': None, 'sharey': 
            False, 'layout': None, 'use_index': True, 'title': None, 'grid':
            None, 'legend': True, 'style': None, 'logx': False, 'logy': 
            False, 'loglog': False, 'xticks': None, 'yticks': None, 'xlim':
            None, 'ylim': None, 'rot': None, 'fontsize': None, 'colormap':
            None, 'table': False, 'yerr': None, 'xerr': None, 'secondary_y':
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        vftvr__hcl = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        zdnds__zkm, gsi__opqq = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, gjiha__fna, etbu__rqhpl, vftvr__hcl)
        yiidw__ahhlv = gsi__opqq[2]
        if not is_overload_constant_str(yiidw__ahhlv):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        wxbdj__girge = gsi__opqq[0]
        if not is_overload_none(wxbdj__girge) and not (is_overload_int(
            wxbdj__girge) or is_overload_constant_str(wxbdj__girge)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(wxbdj__girge):
            wpky__lyglu = get_overload_const_str(wxbdj__girge)
            if wpky__lyglu not in df.columns:
                raise BodoError(f'{func_name}: {wpky__lyglu} column not found.'
                    )
        elif is_overload_int(wxbdj__girge):
            nmuc__xdy = get_overload_const_int(wxbdj__girge)
            if nmuc__xdy > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {nmuc__xdy} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            wxbdj__girge = df.columns[wxbdj__girge]
        ajwum__viqg = gsi__opqq[1]
        if not is_overload_none(ajwum__viqg) and not (is_overload_int(
            ajwum__viqg) or is_overload_constant_str(ajwum__viqg)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(ajwum__viqg):
            pbjaf__ahwo = get_overload_const_str(ajwum__viqg)
            if pbjaf__ahwo not in df.columns:
                raise BodoError(f'{func_name}: {pbjaf__ahwo} column not found.'
                    )
        elif is_overload_int(ajwum__viqg):
            bwz__negqd = get_overload_const_int(ajwum__viqg)
            if bwz__negqd > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {bwz__negqd} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            ajwum__viqg = df.columns[ajwum__viqg]
        otby__wvkq = gsi__opqq[3]
        if not is_overload_none(otby__wvkq) and not is_tuple_like_type(
            otby__wvkq):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        ssxzr__ohm = gsi__opqq[10]
        if not is_overload_none(ssxzr__ohm) and not is_overload_constant_str(
            ssxzr__ohm):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        nyswd__nvmx = gsi__opqq[12]
        if not is_overload_bool(nyswd__nvmx):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        tlx__qddh = gsi__opqq[17]
        if not is_overload_none(tlx__qddh) and not is_tuple_like_type(tlx__qddh
            ):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        oobw__pvpzt = gsi__opqq[18]
        if not is_overload_none(oobw__pvpzt) and not is_tuple_like_type(
            oobw__pvpzt):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        pjrlv__uwx = gsi__opqq[22]
        if not is_overload_none(pjrlv__uwx) and not is_overload_int(pjrlv__uwx
            ):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        anyjs__ypam = gsi__opqq[29]
        if not is_overload_none(anyjs__ypam) and not is_overload_constant_str(
            anyjs__ypam):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        iyzki__idcc = gsi__opqq[30]
        if not is_overload_none(iyzki__idcc) and not is_overload_constant_str(
            iyzki__idcc):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        rkpat__aujl = types.List(types.mpl_line_2d_type)
        yiidw__ahhlv = get_overload_const_str(yiidw__ahhlv)
        if yiidw__ahhlv == 'scatter':
            if is_overload_none(wxbdj__girge) and is_overload_none(ajwum__viqg
                ):
                raise BodoError(
                    f'{func_name}: {yiidw__ahhlv} requires an x and y column.')
            elif is_overload_none(wxbdj__girge):
                raise BodoError(
                    f'{func_name}: {yiidw__ahhlv} x column is missing.')
            elif is_overload_none(ajwum__viqg):
                raise BodoError(
                    f'{func_name}: {yiidw__ahhlv} y column is missing.')
            rkpat__aujl = types.mpl_path_collection_type
        elif yiidw__ahhlv != 'line':
            raise BodoError(
                f'{func_name}: {yiidw__ahhlv} plot is not supported.')
        return signature(rkpat__aujl, *gsi__opqq).replace(pysig=zdnds__zkm)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            rrtaz__ezbw = df.columns.index(attr)
            arr_typ = df.data[rrtaz__ezbw]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            weo__qrugj = []
            gqujm__jank = []
            yybm__phnes = False
            for i, wypr__sgjc in enumerate(df.columns):
                if wypr__sgjc[0] != attr:
                    continue
                yybm__phnes = True
                weo__qrugj.append(wypr__sgjc[1] if len(wypr__sgjc) == 2 else
                    wypr__sgjc[1:])
                gqujm__jank.append(df.data[i])
            if yybm__phnes:
                return DataFrameType(tuple(gqujm__jank), df.index, tuple(
                    weo__qrugj))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        hjg__gfxvb = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(hjg__gfxvb)
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
        qdhr__ngskv = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], qdhr__ngskv)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    pfsuv__xqhu = builder.module
    zmnnv__mirxl = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    lef__luwk = cgutils.get_or_insert_function(pfsuv__xqhu, zmnnv__mirxl,
        name='.dtor.df.{}'.format(df_type))
    if not lef__luwk.is_declaration:
        return lef__luwk
    lef__luwk.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(lef__luwk.append_basic_block())
    flou__ndvvo = lef__luwk.args[0]
    zoqo__kqsd = context.get_value_type(payload_type).as_pointer()
    blhq__gmeb = builder.bitcast(flou__ndvvo, zoqo__kqsd)
    payload = context.make_helper(builder, payload_type, ref=blhq__gmeb)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        jtksd__swt = context.get_python_api(builder)
        kvd__hvkv = jtksd__swt.gil_ensure()
        jtksd__swt.decref(payload.parent)
        jtksd__swt.gil_release(kvd__hvkv)
    builder.ret_void()
    return lef__luwk


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    nqc__qxbc = cgutils.create_struct_proxy(payload_type)(context, builder)
    nqc__qxbc.data = data_tup
    nqc__qxbc.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        nqc__qxbc.columns = colnames
    cef__emqs = context.get_value_type(payload_type)
    zyuzo__usgp = context.get_abi_sizeof(cef__emqs)
    mtmpb__jpjb = define_df_dtor(context, builder, df_type, payload_type)
    tuovl__vyca = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, zyuzo__usgp), mtmpb__jpjb)
    yws__zgd = context.nrt.meminfo_data(builder, tuovl__vyca)
    lmf__yugt = builder.bitcast(yws__zgd, cef__emqs.as_pointer())
    qsqen__leff = cgutils.create_struct_proxy(df_type)(context, builder)
    qsqen__leff.meminfo = tuovl__vyca
    if parent is None:
        qsqen__leff.parent = cgutils.get_null_value(qsqen__leff.parent.type)
    else:
        qsqen__leff.parent = parent
        nqc__qxbc.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            jtksd__swt = context.get_python_api(builder)
            kvd__hvkv = jtksd__swt.gil_ensure()
            jtksd__swt.incref(parent)
            jtksd__swt.gil_release(kvd__hvkv)
    builder.store(nqc__qxbc._getvalue(), lmf__yugt)
    return qsqen__leff._getvalue()


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
        emju__hae = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        emju__hae = [gqzon__kla for gqzon__kla in data_typ.dtype.arr_types]
    pavwn__ojvy = DataFrameType(tuple(emju__hae + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        ramb__achsj = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return ramb__achsj
    sig = signature(pavwn__ojvy, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    dklb__ocgxm = len(data_tup_typ.types)
    if dklb__ocgxm == 0:
        column_names = ()
    ugg__dunu = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(ugg__dunu, ColNamesMetaType) and isinstance(ugg__dunu
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = ugg__dunu.meta
    if dklb__ocgxm == 1 and isinstance(data_tup_typ.types[0], TableType):
        dklb__ocgxm = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == dklb__ocgxm, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    tiuna__ukyq = data_tup_typ.types
    if dklb__ocgxm != 0 and isinstance(data_tup_typ.types[0], TableType):
        tiuna__ukyq = data_tup_typ.types[0].arr_types
        is_table_format = True
    pavwn__ojvy = DataFrameType(tiuna__ukyq, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            dscmn__gtl = cgutils.create_struct_proxy(pavwn__ojvy.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = dscmn__gtl.parent
        ramb__achsj = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return ramb__achsj
    sig = signature(pavwn__ojvy, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        qsqen__leff = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, qsqen__leff.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        nqc__qxbc = get_dataframe_payload(context, builder, df_typ, args[0])
        rfe__tcfjw = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[rfe__tcfjw]
        if df_typ.is_table_format:
            dscmn__gtl = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(nqc__qxbc.data, 0))
            ixvit__vuzmp = df_typ.table_type.type_to_blk[arr_typ]
            wrv__lqt = getattr(dscmn__gtl, f'block_{ixvit__vuzmp}')
            iksat__ctcon = ListInstance(context, builder, types.List(
                arr_typ), wrv__lqt)
            sot__dimb = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[rfe__tcfjw])
            qdhr__ngskv = iksat__ctcon.getitem(sot__dimb)
        else:
            qdhr__ngskv = builder.extract_value(nqc__qxbc.data, rfe__tcfjw)
        zuo__imxpr = cgutils.alloca_once_value(builder, qdhr__ngskv)
        jkosj__swf = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, zuo__imxpr, jkosj__swf)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    tuovl__vyca = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, tuovl__vyca)
    zoqo__kqsd = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, zoqo__kqsd)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    pavwn__ojvy = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        pavwn__ojvy = types.Tuple([TableType(df_typ.data)])
    sig = signature(pavwn__ojvy, df_typ)

    def codegen(context, builder, signature, args):
        nqc__qxbc = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            nqc__qxbc.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        nqc__qxbc = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, nqc__qxbc.
            index)
    pavwn__ojvy = df_typ.index
    sig = signature(pavwn__ojvy, df_typ)
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
        idx__leezj = df.data[i]
        return idx__leezj(*args)


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
        nqc__qxbc = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(nqc__qxbc.data, 0))
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
    daua__xewhu = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{daua__xewhu})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        idx__leezj = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return idx__leezj(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        nqc__qxbc = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, nqc__qxbc.columns)
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
    qqyy__spbaj = self.typemap[data_tup.name]
    if any(is_tuple_like_type(gqzon__kla) for gqzon__kla in qqyy__spbaj.types):
        return None
    if equiv_set.has_shape(data_tup):
        uykck__xtfq = equiv_set.get_shape(data_tup)
        if len(uykck__xtfq) > 1:
            equiv_set.insert_equiv(*uykck__xtfq)
        if len(uykck__xtfq) > 0:
            mhjca__gwmq = self.typemap[index.name]
            if not isinstance(mhjca__gwmq, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(uykck__xtfq[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(uykck__xtfq[0], len(
                uykck__xtfq)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    qcmy__kjv = args[0]
    data_types = self.typemap[qcmy__kjv.name].data
    if any(is_tuple_like_type(gqzon__kla) for gqzon__kla in data_types):
        return None
    if equiv_set.has_shape(qcmy__kjv):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            qcmy__kjv)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    qcmy__kjv = args[0]
    mhjca__gwmq = self.typemap[qcmy__kjv.name].index
    if isinstance(mhjca__gwmq, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(qcmy__kjv):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            qcmy__kjv)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    qcmy__kjv = args[0]
    if equiv_set.has_shape(qcmy__kjv):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            qcmy__kjv), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    qcmy__kjv = args[0]
    if equiv_set.has_shape(qcmy__kjv):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            qcmy__kjv)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    rfe__tcfjw = get_overload_const_int(c_ind_typ)
    if df_typ.data[rfe__tcfjw] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        dsgdp__hpis, pvzp__vohi, lcgf__azy = args
        nqc__qxbc = get_dataframe_payload(context, builder, df_typ, dsgdp__hpis
            )
        if df_typ.is_table_format:
            dscmn__gtl = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(nqc__qxbc.data, 0))
            ixvit__vuzmp = df_typ.table_type.type_to_blk[arr_typ]
            wrv__lqt = getattr(dscmn__gtl, f'block_{ixvit__vuzmp}')
            iksat__ctcon = ListInstance(context, builder, types.List(
                arr_typ), wrv__lqt)
            sot__dimb = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[rfe__tcfjw])
            iksat__ctcon.setitem(sot__dimb, lcgf__azy, True)
        else:
            qdhr__ngskv = builder.extract_value(nqc__qxbc.data, rfe__tcfjw)
            context.nrt.decref(builder, df_typ.data[rfe__tcfjw], qdhr__ngskv)
            nqc__qxbc.data = builder.insert_value(nqc__qxbc.data, lcgf__azy,
                rfe__tcfjw)
            context.nrt.incref(builder, arr_typ, lcgf__azy)
        qsqen__leff = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=dsgdp__hpis)
        payload_type = DataFramePayloadType(df_typ)
        blhq__gmeb = context.nrt.meminfo_data(builder, qsqen__leff.meminfo)
        zoqo__kqsd = context.get_value_type(payload_type).as_pointer()
        blhq__gmeb = builder.bitcast(blhq__gmeb, zoqo__kqsd)
        builder.store(nqc__qxbc._getvalue(), blhq__gmeb)
        return impl_ret_borrowed(context, builder, df_typ, dsgdp__hpis)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        amgx__kkqu = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        olk__powmv = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=amgx__kkqu)
        jmgro__rpei = get_dataframe_payload(context, builder, df_typ,
            amgx__kkqu)
        qsqen__leff = construct_dataframe(context, builder, signature.
            return_type, jmgro__rpei.data, index_val, olk__powmv.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), jmgro__rpei.data)
        return qsqen__leff
    pavwn__ojvy = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(pavwn__ojvy, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    dklb__ocgxm = len(df_type.columns)
    kjp__lcxv = dklb__ocgxm
    rcoa__pppwi = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    wfb__hxbb = col_name not in df_type.columns
    rfe__tcfjw = dklb__ocgxm
    if wfb__hxbb:
        rcoa__pppwi += arr_type,
        column_names += col_name,
        kjp__lcxv += 1
    else:
        rfe__tcfjw = df_type.columns.index(col_name)
        rcoa__pppwi = tuple(arr_type if i == rfe__tcfjw else rcoa__pppwi[i] for
            i in range(dklb__ocgxm))

    def codegen(context, builder, signature, args):
        dsgdp__hpis, pvzp__vohi, lcgf__azy = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, dsgdp__hpis)
        kmhjx__lbbt = cgutils.create_struct_proxy(df_type)(context, builder,
            value=dsgdp__hpis)
        if df_type.is_table_format:
            kdhuo__jnrn = df_type.table_type
            kbdr__sfo = builder.extract_value(in_dataframe_payload.data, 0)
            eyqpu__bjr = TableType(rcoa__pppwi)
            pqojs__qcntd = set_table_data_codegen(context, builder,
                kdhuo__jnrn, kbdr__sfo, eyqpu__bjr, arr_type, lcgf__azy,
                rfe__tcfjw, wfb__hxbb)
            data_tup = context.make_tuple(builder, types.Tuple([eyqpu__bjr]
                ), [pqojs__qcntd])
        else:
            tiuna__ukyq = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != rfe__tcfjw else lcgf__azy) for i in range(
                dklb__ocgxm)]
            if wfb__hxbb:
                tiuna__ukyq.append(lcgf__azy)
            for qcmy__kjv, mvm__tte in zip(tiuna__ukyq, rcoa__pppwi):
                context.nrt.incref(builder, mvm__tte, qcmy__kjv)
            data_tup = context.make_tuple(builder, types.Tuple(rcoa__pppwi),
                tiuna__ukyq)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        qge__mctoy = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, kmhjx__lbbt.parent, None)
        if not wfb__hxbb and arr_type == df_type.data[rfe__tcfjw]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            blhq__gmeb = context.nrt.meminfo_data(builder, kmhjx__lbbt.meminfo)
            zoqo__kqsd = context.get_value_type(payload_type).as_pointer()
            blhq__gmeb = builder.bitcast(blhq__gmeb, zoqo__kqsd)
            vibm__qxc = get_dataframe_payload(context, builder, df_type,
                qge__mctoy)
            builder.store(vibm__qxc._getvalue(), blhq__gmeb)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, eyqpu__bjr, builder.
                    extract_value(data_tup, 0))
            else:
                for qcmy__kjv, mvm__tte in zip(tiuna__ukyq, rcoa__pppwi):
                    context.nrt.incref(builder, mvm__tte, qcmy__kjv)
        has_parent = cgutils.is_not_null(builder, kmhjx__lbbt.parent)
        with builder.if_then(has_parent):
            jtksd__swt = context.get_python_api(builder)
            kvd__hvkv = jtksd__swt.gil_ensure()
            lapc__zzzxt = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, lcgf__azy)
            qjwah__jmsvp = numba.core.pythonapi._BoxContext(context,
                builder, jtksd__swt, lapc__zzzxt)
            oou__eily = qjwah__jmsvp.pyapi.from_native_value(arr_type,
                lcgf__azy, qjwah__jmsvp.env_manager)
            if isinstance(col_name, str):
                szji__jcc = context.insert_const_string(builder.module,
                    col_name)
                uisbr__ywfk = jtksd__swt.string_from_string(szji__jcc)
            else:
                assert isinstance(col_name, int)
                uisbr__ywfk = jtksd__swt.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            jtksd__swt.object_setitem(kmhjx__lbbt.parent, uisbr__ywfk,
                oou__eily)
            jtksd__swt.decref(oou__eily)
            jtksd__swt.decref(uisbr__ywfk)
            jtksd__swt.gil_release(kvd__hvkv)
        return qge__mctoy
    pavwn__ojvy = DataFrameType(rcoa__pppwi, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(pavwn__ojvy, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    dklb__ocgxm = len(pyval.columns)
    tiuna__ukyq = []
    for i in range(dklb__ocgxm):
        vokeb__usuny = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            oou__eily = vokeb__usuny.array
        else:
            oou__eily = vokeb__usuny.values
        tiuna__ukyq.append(oou__eily)
    tiuna__ukyq = tuple(tiuna__ukyq)
    if df_type.is_table_format:
        dscmn__gtl = context.get_constant_generic(builder, df_type.
            table_type, Table(tiuna__ukyq))
        data_tup = lir.Constant.literal_struct([dscmn__gtl])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], wypr__sgjc) for 
            i, wypr__sgjc in enumerate(tiuna__ukyq)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    imlhg__gruu = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, imlhg__gruu])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    oos__cia = context.get_constant(types.int64, -1)
    bhvmm__mjc = context.get_constant_null(types.voidptr)
    tuovl__vyca = lir.Constant.literal_struct([oos__cia, bhvmm__mjc,
        bhvmm__mjc, payload, oos__cia])
    tuovl__vyca = cgutils.global_constant(builder, '.const.meminfo',
        tuovl__vyca).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([tuovl__vyca, imlhg__gruu])


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
        qxqen__gdppb = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        qxqen__gdppb = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, qxqen__gdppb)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        gqujm__jank = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                gqujm__jank)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), gqujm__jank)
    elif not fromty.is_table_format and toty.is_table_format:
        gqujm__jank = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        gqujm__jank = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        gqujm__jank = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        gqujm__jank = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, gqujm__jank,
        qxqen__gdppb, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    msz__tqbpx = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        xduyo__xijw = get_index_data_arr_types(toty.index)[0]
        ylk__jghb = bodo.utils.transform.get_type_alloc_counts(xduyo__xijw) - 1
        isoxc__rhih = ', '.join('0' for pvzp__vohi in range(ylk__jghb))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(isoxc__rhih, ', ' if ylk__jghb == 1 else ''))
        msz__tqbpx['index_arr_type'] = xduyo__xijw
    kix__yxjlm = []
    for i, arr_typ in enumerate(toty.data):
        ylk__jghb = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        isoxc__rhih = ', '.join('0' for pvzp__vohi in range(ylk__jghb))
        ydads__kdd = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, isoxc__rhih, ', ' if ylk__jghb == 1 else ''))
        kix__yxjlm.append(ydads__kdd)
        msz__tqbpx[f'arr_type{i}'] = arr_typ
    kix__yxjlm = ', '.join(kix__yxjlm)
    pcqlb__skaxy = 'def impl():\n'
    syjfy__yyf = bodo.hiframes.dataframe_impl._gen_init_df(pcqlb__skaxy,
        toty.columns, kix__yxjlm, index, msz__tqbpx)
    df = context.compile_internal(builder, syjfy__yyf, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    uxmhy__rlsns = toty.table_type
    dscmn__gtl = cgutils.create_struct_proxy(uxmhy__rlsns)(context, builder)
    dscmn__gtl.parent = in_dataframe_payload.parent
    for gqzon__kla, ixvit__vuzmp in uxmhy__rlsns.type_to_blk.items():
        pgou__mcsxt = context.get_constant(types.int64, len(uxmhy__rlsns.
            block_to_arr_ind[ixvit__vuzmp]))
        pvzp__vohi, bcikx__jcrx = ListInstance.allocate_ex(context, builder,
            types.List(gqzon__kla), pgou__mcsxt)
        bcikx__jcrx.size = pgou__mcsxt
        setattr(dscmn__gtl, f'block_{ixvit__vuzmp}', bcikx__jcrx.value)
    for i, gqzon__kla in enumerate(fromty.data):
        evbc__gvd = toty.data[i]
        if gqzon__kla != evbc__gvd:
            glow__wvk = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*glow__wvk)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        qdhr__ngskv = builder.extract_value(in_dataframe_payload.data, i)
        if gqzon__kla != evbc__gvd:
            klpny__sum = context.cast(builder, qdhr__ngskv, gqzon__kla,
                evbc__gvd)
            gvw__zwrh = False
        else:
            klpny__sum = qdhr__ngskv
            gvw__zwrh = True
        ixvit__vuzmp = uxmhy__rlsns.type_to_blk[gqzon__kla]
        wrv__lqt = getattr(dscmn__gtl, f'block_{ixvit__vuzmp}')
        iksat__ctcon = ListInstance(context, builder, types.List(gqzon__kla
            ), wrv__lqt)
        sot__dimb = context.get_constant(types.int64, uxmhy__rlsns.
            block_offsets[i])
        iksat__ctcon.setitem(sot__dimb, klpny__sum, gvw__zwrh)
    data_tup = context.make_tuple(builder, types.Tuple([uxmhy__rlsns]), [
        dscmn__gtl._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    tiuna__ukyq = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            glow__wvk = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*glow__wvk)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            qdhr__ngskv = builder.extract_value(in_dataframe_payload.data, i)
            klpny__sum = context.cast(builder, qdhr__ngskv, fromty.data[i],
                toty.data[i])
            gvw__zwrh = False
        else:
            klpny__sum = builder.extract_value(in_dataframe_payload.data, i)
            gvw__zwrh = True
        if gvw__zwrh:
            context.nrt.incref(builder, toty.data[i], klpny__sum)
        tiuna__ukyq.append(klpny__sum)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), tiuna__ukyq)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    kdhuo__jnrn = fromty.table_type
    kbdr__sfo = cgutils.create_struct_proxy(kdhuo__jnrn)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    eyqpu__bjr = toty.table_type
    pqojs__qcntd = cgutils.create_struct_proxy(eyqpu__bjr)(context, builder)
    pqojs__qcntd.parent = in_dataframe_payload.parent
    for gqzon__kla, ixvit__vuzmp in eyqpu__bjr.type_to_blk.items():
        pgou__mcsxt = context.get_constant(types.int64, len(eyqpu__bjr.
            block_to_arr_ind[ixvit__vuzmp]))
        pvzp__vohi, bcikx__jcrx = ListInstance.allocate_ex(context, builder,
            types.List(gqzon__kla), pgou__mcsxt)
        bcikx__jcrx.size = pgou__mcsxt
        setattr(pqojs__qcntd, f'block_{ixvit__vuzmp}', bcikx__jcrx.value)
    for i in range(len(fromty.data)):
        nvwqa__sgy = fromty.data[i]
        evbc__gvd = toty.data[i]
        if nvwqa__sgy != evbc__gvd:
            glow__wvk = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*glow__wvk)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        fssxi__nuso = kdhuo__jnrn.type_to_blk[nvwqa__sgy]
        yyp__rkzld = getattr(kbdr__sfo, f'block_{fssxi__nuso}')
        tukv__fjoyu = ListInstance(context, builder, types.List(nvwqa__sgy),
            yyp__rkzld)
        aqku__kojrr = context.get_constant(types.int64, kdhuo__jnrn.
            block_offsets[i])
        qdhr__ngskv = tukv__fjoyu.getitem(aqku__kojrr)
        if nvwqa__sgy != evbc__gvd:
            klpny__sum = context.cast(builder, qdhr__ngskv, nvwqa__sgy,
                evbc__gvd)
            gvw__zwrh = False
        else:
            klpny__sum = qdhr__ngskv
            gvw__zwrh = True
        jpo__faaj = eyqpu__bjr.type_to_blk[gqzon__kla]
        bcikx__jcrx = getattr(pqojs__qcntd, f'block_{jpo__faaj}')
        bsqfz__cqtd = ListInstance(context, builder, types.List(evbc__gvd),
            bcikx__jcrx)
        ypuu__nhiwk = context.get_constant(types.int64, eyqpu__bjr.
            block_offsets[i])
        bsqfz__cqtd.setitem(ypuu__nhiwk, klpny__sum, gvw__zwrh)
    data_tup = context.make_tuple(builder, types.Tuple([eyqpu__bjr]), [
        pqojs__qcntd._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    uxmhy__rlsns = fromty.table_type
    dscmn__gtl = cgutils.create_struct_proxy(uxmhy__rlsns)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    tiuna__ukyq = []
    for i, gqzon__kla in enumerate(toty.data):
        nvwqa__sgy = fromty.data[i]
        if gqzon__kla != nvwqa__sgy:
            glow__wvk = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*glow__wvk)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        ixvit__vuzmp = uxmhy__rlsns.type_to_blk[gqzon__kla]
        wrv__lqt = getattr(dscmn__gtl, f'block_{ixvit__vuzmp}')
        iksat__ctcon = ListInstance(context, builder, types.List(gqzon__kla
            ), wrv__lqt)
        sot__dimb = context.get_constant(types.int64, uxmhy__rlsns.
            block_offsets[i])
        qdhr__ngskv = iksat__ctcon.getitem(sot__dimb)
        if gqzon__kla != nvwqa__sgy:
            klpny__sum = context.cast(builder, qdhr__ngskv, nvwqa__sgy,
                gqzon__kla)
            gvw__zwrh = False
        else:
            klpny__sum = qdhr__ngskv
            gvw__zwrh = True
        if gvw__zwrh:
            context.nrt.incref(builder, gqzon__kla, klpny__sum)
        tiuna__ukyq.append(klpny__sum)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), tiuna__ukyq)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    hkt__qdntk, kix__yxjlm, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    jjnwc__lgzh = ColNamesMetaType(tuple(hkt__qdntk))
    pcqlb__skaxy = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    pcqlb__skaxy += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(kix__yxjlm, index_arg))
    grax__fqnb = {}
    exec(pcqlb__skaxy, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': jjnwc__lgzh}, grax__fqnb)
    zcgzi__hys = grax__fqnb['_init_df']
    return zcgzi__hys


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    pavwn__ojvy = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(pavwn__ojvy, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    pavwn__ojvy = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(pavwn__ojvy, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    kmtu__npt = ''
    if not is_overload_none(dtype):
        kmtu__npt = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        dklb__ocgxm = (len(data.types) - 1) // 2
        kikm__nnmqf = [gqzon__kla.literal_value for gqzon__kla in data.
            types[1:dklb__ocgxm + 1]]
        data_val_types = dict(zip(kikm__nnmqf, data.types[dklb__ocgxm + 1:]))
        tiuna__ukyq = ['data[{}]'.format(i) for i in range(dklb__ocgxm + 1,
            2 * dklb__ocgxm + 1)]
        data_dict = dict(zip(kikm__nnmqf, tiuna__ukyq))
        if is_overload_none(index):
            for i, gqzon__kla in enumerate(data.types[dklb__ocgxm + 1:]):
                if isinstance(gqzon__kla, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(dklb__ocgxm + 1 + i))
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
        ggqfu__ckjx = '.copy()' if copy else ''
        hbsc__jpd = get_overload_const_list(columns)
        dklb__ocgxm = len(hbsc__jpd)
        data_val_types = {qjwah__jmsvp: data.copy(ndim=1) for qjwah__jmsvp in
            hbsc__jpd}
        tiuna__ukyq = ['data[:,{}]{}'.format(i, ggqfu__ckjx) for i in range
            (dklb__ocgxm)]
        data_dict = dict(zip(hbsc__jpd, tiuna__ukyq))
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
    kix__yxjlm = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[qjwah__jmsvp], df_len, kmtu__npt) for
        qjwah__jmsvp in col_names))
    if len(col_names) == 0:
        kix__yxjlm = '()'
    return col_names, kix__yxjlm, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for qjwah__jmsvp in col_names:
        if qjwah__jmsvp in data_dict and is_iterable_type(data_val_types[
            qjwah__jmsvp]):
            df_len = 'len({})'.format(data_dict[qjwah__jmsvp])
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
    if all(qjwah__jmsvp in data_dict for qjwah__jmsvp in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    snuxf__vnhhv = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len
        , dtype)
    for qjwah__jmsvp in col_names:
        if qjwah__jmsvp not in data_dict:
            data_dict[qjwah__jmsvp] = snuxf__vnhhv


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
            gqzon__kla = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(gqzon__kla)
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
        glmc__cdu = idx.literal_value
        if isinstance(glmc__cdu, int):
            idx__leezj = tup.types[glmc__cdu]
        elif isinstance(glmc__cdu, slice):
            idx__leezj = types.BaseTuple.from_types(tup.types[glmc__cdu])
        return signature(idx__leezj, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    eodcn__gvarv, idx = sig.args
    idx = idx.literal_value
    tup, pvzp__vohi = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(eodcn__gvarv)
        if not 0 <= idx < len(eodcn__gvarv):
            raise IndexError('cannot index at %d in %s' % (idx, eodcn__gvarv))
        xje__fsuz = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        aulas__dxkl = cgutils.unpack_tuple(builder, tup)[idx]
        xje__fsuz = context.make_tuple(builder, sig.return_type, aulas__dxkl)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, xje__fsuz)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, xvs__dxf, suffix_x, suffix_y,
            is_join, indicator, pvzp__vohi, pvzp__vohi) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        nllex__ohfje = {qjwah__jmsvp: i for i, qjwah__jmsvp in enumerate(
            left_on)}
        hodng__ebp = {qjwah__jmsvp: i for i, qjwah__jmsvp in enumerate(
            right_on)}
        dhe__cvr = set(left_on) & set(right_on)
        cyrcw__udbcy = set(left_df.columns) & set(right_df.columns)
        xratn__ggp = cyrcw__udbcy - dhe__cvr
        rag__ttrxm = '$_bodo_index_' in left_on
        aakdw__pvy = '$_bodo_index_' in right_on
        how = get_overload_const_str(xvs__dxf)
        patih__jgy = how in {'left', 'outer'}
        horx__cnq = how in {'right', 'outer'}
        columns = []
        data = []
        if rag__ttrxm:
            iyxkn__uhkyo = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            iyxkn__uhkyo = left_df.data[left_df.column_index[left_on[0]]]
        if aakdw__pvy:
            sjev__aennb = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            sjev__aennb = right_df.data[right_df.column_index[right_on[0]]]
        if rag__ttrxm and not aakdw__pvy and not is_join.literal_value:
            axp__xlagy = right_on[0]
            if axp__xlagy in left_df.column_index:
                columns.append(axp__xlagy)
                if (sjev__aennb == bodo.dict_str_arr_type and iyxkn__uhkyo ==
                    bodo.string_array_type):
                    czlx__zsr = bodo.string_array_type
                else:
                    czlx__zsr = sjev__aennb
                data.append(czlx__zsr)
        if aakdw__pvy and not rag__ttrxm and not is_join.literal_value:
            ddj__zrnoy = left_on[0]
            if ddj__zrnoy in right_df.column_index:
                columns.append(ddj__zrnoy)
                if (iyxkn__uhkyo == bodo.dict_str_arr_type and sjev__aennb ==
                    bodo.string_array_type):
                    czlx__zsr = bodo.string_array_type
                else:
                    czlx__zsr = iyxkn__uhkyo
                data.append(czlx__zsr)
        for nvwqa__sgy, vokeb__usuny in zip(left_df.data, left_df.columns):
            columns.append(str(vokeb__usuny) + suffix_x.literal_value if 
                vokeb__usuny in xratn__ggp else vokeb__usuny)
            if vokeb__usuny in dhe__cvr:
                if nvwqa__sgy == bodo.dict_str_arr_type:
                    nvwqa__sgy = right_df.data[right_df.column_index[
                        vokeb__usuny]]
                data.append(nvwqa__sgy)
            else:
                if (nvwqa__sgy == bodo.dict_str_arr_type and vokeb__usuny in
                    nllex__ohfje):
                    if aakdw__pvy:
                        nvwqa__sgy = sjev__aennb
                    else:
                        cnyde__gew = nllex__ohfje[vokeb__usuny]
                        mjocj__oqboq = right_on[cnyde__gew]
                        nvwqa__sgy = right_df.data[right_df.column_index[
                            mjocj__oqboq]]
                if horx__cnq:
                    nvwqa__sgy = to_nullable_type(nvwqa__sgy)
                data.append(nvwqa__sgy)
        for nvwqa__sgy, vokeb__usuny in zip(right_df.data, right_df.columns):
            if vokeb__usuny not in dhe__cvr:
                columns.append(str(vokeb__usuny) + suffix_y.literal_value if
                    vokeb__usuny in xratn__ggp else vokeb__usuny)
                if (nvwqa__sgy == bodo.dict_str_arr_type and vokeb__usuny in
                    hodng__ebp):
                    if rag__ttrxm:
                        nvwqa__sgy = iyxkn__uhkyo
                    else:
                        cnyde__gew = hodng__ebp[vokeb__usuny]
                        dfjv__err = left_on[cnyde__gew]
                        nvwqa__sgy = left_df.data[left_df.column_index[
                            dfjv__err]]
                if patih__jgy:
                    nvwqa__sgy = to_nullable_type(nvwqa__sgy)
                data.append(nvwqa__sgy)
        stzbo__cjzf = get_overload_const_bool(indicator)
        if stzbo__cjzf:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        sxibl__wfrln = False
        if rag__ttrxm and aakdw__pvy and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            sxibl__wfrln = True
        elif rag__ttrxm and not aakdw__pvy:
            index_typ = right_df.index
            sxibl__wfrln = True
        elif aakdw__pvy and not rag__ttrxm:
            index_typ = left_df.index
            sxibl__wfrln = True
        if sxibl__wfrln and isinstance(index_typ, bodo.hiframes.
            pd_index_ext.RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        fdrjo__onxgm = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(fdrjo__onxgm, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    qsqen__leff = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return qsqen__leff._getvalue()


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
    rmsz__uaqfx = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    etbu__rqhpl = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', rmsz__uaqfx, etbu__rqhpl,
        package_name='pandas', module_name='General')
    pcqlb__skaxy = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        tdglv__tnsk = 0
        kix__yxjlm = []
        names = []
        for i, zruo__ngsu in enumerate(objs.types):
            assert isinstance(zruo__ngsu, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(zruo__ngsu, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                zruo__ngsu, 'pandas.concat()')
            if isinstance(zruo__ngsu, SeriesType):
                names.append(str(tdglv__tnsk))
                tdglv__tnsk += 1
                kix__yxjlm.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(zruo__ngsu.columns)
                for fxoti__mhv in range(len(zruo__ngsu.data)):
                    kix__yxjlm.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, fxoti__mhv))
        return bodo.hiframes.dataframe_impl._gen_init_df(pcqlb__skaxy,
            names, ', '.join(kix__yxjlm), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(gqzon__kla, DataFrameType) for gqzon__kla in
            objs.types)
        bqkvh__dlb = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            bqkvh__dlb.extend(df.columns)
        bqkvh__dlb = list(dict.fromkeys(bqkvh__dlb).keys())
        emju__hae = {}
        for tdglv__tnsk, qjwah__jmsvp in enumerate(bqkvh__dlb):
            for i, df in enumerate(objs.types):
                if qjwah__jmsvp in df.column_index:
                    emju__hae[f'arr_typ{tdglv__tnsk}'] = df.data[df.
                        column_index[qjwah__jmsvp]]
                    break
        assert len(emju__hae) == len(bqkvh__dlb)
        dob__cuxg = []
        for tdglv__tnsk, qjwah__jmsvp in enumerate(bqkvh__dlb):
            args = []
            for i, df in enumerate(objs.types):
                if qjwah__jmsvp in df.column_index:
                    rfe__tcfjw = df.column_index[qjwah__jmsvp]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, rfe__tcfjw))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, tdglv__tnsk))
            pcqlb__skaxy += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(tdglv__tnsk, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(pcqlb__skaxy,
            bqkvh__dlb, ', '.join('A{}'.format(i) for i in range(len(
            bqkvh__dlb))), index, emju__hae)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(gqzon__kla, SeriesType) for gqzon__kla in
            objs.types)
        pcqlb__skaxy += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            pcqlb__skaxy += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            pcqlb__skaxy += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        pcqlb__skaxy += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        grax__fqnb = {}
        exec(pcqlb__skaxy, {'bodo': bodo, 'np': np, 'numba': numba}, grax__fqnb
            )
        return grax__fqnb['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for tdglv__tnsk, qjwah__jmsvp in enumerate(df_type.columns):
            pcqlb__skaxy += '  arrs{} = []\n'.format(tdglv__tnsk)
            pcqlb__skaxy += '  for i in range(len(objs)):\n'
            pcqlb__skaxy += '    df = objs[i]\n'
            pcqlb__skaxy += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(tdglv__tnsk))
            pcqlb__skaxy += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(tdglv__tnsk))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            pcqlb__skaxy += '  arrs_index = []\n'
            pcqlb__skaxy += '  for i in range(len(objs)):\n'
            pcqlb__skaxy += '    df = objs[i]\n'
            pcqlb__skaxy += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(pcqlb__skaxy,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        pcqlb__skaxy += '  arrs = []\n'
        pcqlb__skaxy += '  for i in range(len(objs)):\n'
        pcqlb__skaxy += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        pcqlb__skaxy += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            pcqlb__skaxy += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            pcqlb__skaxy += '  arrs_index = []\n'
            pcqlb__skaxy += '  for i in range(len(objs)):\n'
            pcqlb__skaxy += '    S = objs[i]\n'
            pcqlb__skaxy += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            pcqlb__skaxy += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        pcqlb__skaxy += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        grax__fqnb = {}
        exec(pcqlb__skaxy, {'bodo': bodo, 'np': np, 'numba': numba}, grax__fqnb
            )
        return grax__fqnb['impl']
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
        pavwn__ojvy = df.copy(index=index)
        return signature(pavwn__ojvy, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    zlkjj__zez = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return zlkjj__zez._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    rmsz__uaqfx = dict(index=index, name=name)
    etbu__rqhpl = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', rmsz__uaqfx, etbu__rqhpl,
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
        emju__hae = (types.Array(types.int64, 1, 'C'),) + df.data
        pqg__pbo = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(columns,
            emju__hae)
        return signature(pqg__pbo, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    zlkjj__zez = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return zlkjj__zez._getvalue()


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
    zlkjj__zez = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return zlkjj__zez._getvalue()


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
    zlkjj__zez = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return zlkjj__zez._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    is_already_shuffled=False, _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    xfhp__bzwq = get_overload_const_bool(check_duplicates)
    kkc__owuy = not get_overload_const_bool(is_already_shuffled)
    nkz__lxkty = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    vychj__cvgs = len(value_names) > 1
    foewh__adcx = None
    xdt__xhx = None
    mnzyz__macqk = None
    ipn__ongdt = None
    mxli__fvpoc = isinstance(values_tup, types.UniTuple)
    if mxli__fvpoc:
        eokwm__uzl = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        eokwm__uzl = [to_str_arr_if_dict_array(to_nullable_type(mvm__tte)) for
            mvm__tte in values_tup]
    pcqlb__skaxy = 'def impl(\n'
    pcqlb__skaxy += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, is_already_shuffled=False, _constant_pivot_values=None, parallel=False
"""
    pcqlb__skaxy += '):\n'
    pcqlb__skaxy += (
        "    ev = tracing.Event('pivot_impl', is_parallel=parallel)\n")
    if kkc__owuy:
        pcqlb__skaxy += '    if parallel:\n'
        pcqlb__skaxy += (
            "        ev_shuffle = tracing.Event('shuffle_pivot_index')\n")
        gns__xukz = ', '.join([f'array_to_info(index_tup[{i}])' for i in
            range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for
            i in range(len(columns_tup))] + [
            f'array_to_info(values_tup[{i}])' for i in range(len(values_tup))])
        pcqlb__skaxy += f'        info_list = [{gns__xukz}]\n'
        pcqlb__skaxy += (
            '        cpp_table = arr_info_list_to_table(info_list)\n')
        pcqlb__skaxy += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
        ihqb__ykcyl = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
             for i in range(len(index_tup))])
        kjal__voevn = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
             for i in range(len(columns_tup))])
        ydc__xisy = ', '.join([
            f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
             for i in range(len(values_tup))])
        pcqlb__skaxy += f'        index_tup = ({ihqb__ykcyl},)\n'
        pcqlb__skaxy += f'        columns_tup = ({kjal__voevn},)\n'
        pcqlb__skaxy += f'        values_tup = ({ydc__xisy},)\n'
        pcqlb__skaxy += '        delete_table(cpp_table)\n'
        pcqlb__skaxy += '        delete_table(out_cpp_table)\n'
        pcqlb__skaxy += '        ev_shuffle.finalize()\n'
    pcqlb__skaxy += '    columns_arr = columns_tup[0]\n'
    if mxli__fvpoc:
        pcqlb__skaxy += '    values_arrs = [arr for arr in values_tup]\n'
    pcqlb__skaxy += """    ev_unique = tracing.Event('pivot_unique_index_map', is_parallel=parallel)
"""
    pcqlb__skaxy += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    pcqlb__skaxy += '        index_tup\n'
    pcqlb__skaxy += '    )\n'
    pcqlb__skaxy += '    n_rows = len(unique_index_arr_tup[0])\n'
    pcqlb__skaxy += '    num_values_arrays = len(values_tup)\n'
    pcqlb__skaxy += '    n_unique_pivots = len(pivot_values)\n'
    if mxli__fvpoc:
        pcqlb__skaxy += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        pcqlb__skaxy += '    n_cols = n_unique_pivots\n'
    pcqlb__skaxy += '    col_map = {}\n'
    pcqlb__skaxy += '    for i in range(n_unique_pivots):\n'
    pcqlb__skaxy += (
        '        if bodo.libs.array_kernels.isna(pivot_values, i):\n')
    pcqlb__skaxy += '            raise ValueError(\n'
    pcqlb__skaxy += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    pcqlb__skaxy += '            )\n'
    pcqlb__skaxy += '        col_map[pivot_values[i]] = i\n'
    pcqlb__skaxy += '    ev_unique.finalize()\n'
    pcqlb__skaxy += (
        "    ev_alloc = tracing.Event('pivot_alloc', is_parallel=parallel)\n")
    vzfxk__gxhge = False
    for i, gcd__swh in enumerate(eokwm__uzl):
        if is_str_arr_type(gcd__swh):
            vzfxk__gxhge = True
            pcqlb__skaxy += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            pcqlb__skaxy += (
                f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n')
    if vzfxk__gxhge:
        if xfhp__bzwq:
            pcqlb__skaxy += '    nbytes = (n_rows + 7) >> 3\n'
            pcqlb__skaxy += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        pcqlb__skaxy += '    for i in range(len(columns_arr)):\n'
        pcqlb__skaxy += '        col_name = columns_arr[i]\n'
        pcqlb__skaxy += '        pivot_idx = col_map[col_name]\n'
        pcqlb__skaxy += '        row_idx = row_vector[i]\n'
        if xfhp__bzwq:
            pcqlb__skaxy += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            pcqlb__skaxy += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            pcqlb__skaxy += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            pcqlb__skaxy += '        else:\n'
            pcqlb__skaxy += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if mxli__fvpoc:
            pcqlb__skaxy += '        for j in range(num_values_arrays):\n'
            pcqlb__skaxy += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            pcqlb__skaxy += '            len_arr = len_arrs_0[col_idx]\n'
            pcqlb__skaxy += '            values_arr = values_arrs[j]\n'
            pcqlb__skaxy += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            pcqlb__skaxy += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            pcqlb__skaxy += '                len_arr[row_idx] = str_val_len\n'
            pcqlb__skaxy += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, gcd__swh in enumerate(eokwm__uzl):
                if is_str_arr_type(gcd__swh):
                    pcqlb__skaxy += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    pcqlb__skaxy += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    pcqlb__skaxy += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    pcqlb__skaxy += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    pcqlb__skaxy += f"    ev_alloc.add_attribute('num_rows', n_rows)\n"
    for i, gcd__swh in enumerate(eokwm__uzl):
        if is_str_arr_type(gcd__swh):
            pcqlb__skaxy += f'    data_arrs_{i} = [\n'
            pcqlb__skaxy += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            pcqlb__skaxy += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            pcqlb__skaxy += '        )\n'
            pcqlb__skaxy += '        for i in range(n_cols)\n'
            pcqlb__skaxy += '    ]\n'
            pcqlb__skaxy += f'    if tracing.is_tracing():\n'
            pcqlb__skaxy += '         for i in range(n_cols):'
            pcqlb__skaxy += f"""            ev_alloc.add_attribute('total_str_chars_out_column_{i}_' + str(i), total_lens_{i}[i])
"""
        else:
            pcqlb__skaxy += f'    data_arrs_{i} = [\n'
            pcqlb__skaxy += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            pcqlb__skaxy += '        for _ in range(n_cols)\n'
            pcqlb__skaxy += '    ]\n'
    if not vzfxk__gxhge and xfhp__bzwq:
        pcqlb__skaxy += '    nbytes = (n_rows + 7) >> 3\n'
        pcqlb__skaxy += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    pcqlb__skaxy += '    ev_alloc.finalize()\n'
    pcqlb__skaxy += (
        "    ev_fill = tracing.Event('pivot_fill_data', is_parallel=parallel)\n"
        )
    pcqlb__skaxy += '    for i in range(len(columns_arr)):\n'
    pcqlb__skaxy += '        col_name = columns_arr[i]\n'
    pcqlb__skaxy += '        pivot_idx = col_map[col_name]\n'
    pcqlb__skaxy += '        row_idx = row_vector[i]\n'
    if not vzfxk__gxhge and xfhp__bzwq:
        pcqlb__skaxy += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        pcqlb__skaxy += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        pcqlb__skaxy += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        pcqlb__skaxy += '        else:\n'
        pcqlb__skaxy += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
    if mxli__fvpoc:
        pcqlb__skaxy += '        for j in range(num_values_arrays):\n'
        pcqlb__skaxy += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        pcqlb__skaxy += '            col_arr = data_arrs_0[col_idx]\n'
        pcqlb__skaxy += '            values_arr = values_arrs[j]\n'
        pcqlb__skaxy += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        pcqlb__skaxy += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        pcqlb__skaxy += '            else:\n'
        pcqlb__skaxy += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, gcd__swh in enumerate(eokwm__uzl):
            pcqlb__skaxy += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            pcqlb__skaxy += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            pcqlb__skaxy += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            pcqlb__skaxy += f'        else:\n'
            pcqlb__skaxy += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        pcqlb__skaxy += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        foewh__adcx = index_names.meta[0]
    else:
        pcqlb__skaxy += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        foewh__adcx = tuple(index_names.meta)
    pcqlb__skaxy += f'    if tracing.is_tracing():\n'
    pcqlb__skaxy += f'        index_nbytes = index.nbytes\n'
    pcqlb__skaxy += f"        ev.add_attribute('index_nbytes', index_nbytes)\n"
    if not nkz__lxkty:
        mnzyz__macqk = columns_name.meta[0]
        if vychj__cvgs:
            pcqlb__skaxy += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            xdt__xhx = value_names.meta
            if all(isinstance(qjwah__jmsvp, str) for qjwah__jmsvp in xdt__xhx):
                xdt__xhx = pd.array(xdt__xhx, 'string')
            elif all(isinstance(qjwah__jmsvp, int) for qjwah__jmsvp in xdt__xhx
                ):
                xdt__xhx = np.array(xdt__xhx, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(xdt__xhx.dtype, pd.StringDtype):
                pcqlb__skaxy += '    total_chars = 0\n'
                pcqlb__skaxy += f'    for i in range({len(value_names)}):\n'
                pcqlb__skaxy += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                pcqlb__skaxy += '        total_chars += value_name_str_len\n'
                pcqlb__skaxy += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                pcqlb__skaxy += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                pcqlb__skaxy += '    total_chars = 0\n'
                pcqlb__skaxy += '    for i in range(len(pivot_values)):\n'
                pcqlb__skaxy += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                pcqlb__skaxy += '        total_chars += pivot_val_str_len\n'
                pcqlb__skaxy += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                pcqlb__skaxy += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            pcqlb__skaxy += f'    for i in range({len(value_names)}):\n'
            pcqlb__skaxy += '        for j in range(len(pivot_values)):\n'
            pcqlb__skaxy += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            pcqlb__skaxy += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            pcqlb__skaxy += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            pcqlb__skaxy += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    pcqlb__skaxy += '    ev_fill.finalize()\n'
    uxmhy__rlsns = None
    if nkz__lxkty:
        if vychj__cvgs:
            hlluj__had = []
            for ueh__rcj in _constant_pivot_values.meta:
                for bqanf__cpog in value_names.meta:
                    hlluj__had.append((ueh__rcj, bqanf__cpog))
            column_names = tuple(hlluj__had)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        ipn__ongdt = ColNamesMetaType(column_names)
        awxdp__yjyvz = []
        for mvm__tte in eokwm__uzl:
            awxdp__yjyvz.extend([mvm__tte] * len(_constant_pivot_values))
        imvtk__jeil = tuple(awxdp__yjyvz)
        uxmhy__rlsns = TableType(imvtk__jeil)
        pcqlb__skaxy += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        pcqlb__skaxy += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, mvm__tte in enumerate(eokwm__uzl):
            pcqlb__skaxy += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {uxmhy__rlsns.type_to_blk[mvm__tte]})
"""
        pcqlb__skaxy += (
            '    result = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        pcqlb__skaxy += '        (table,), index, columns_typ\n'
        pcqlb__skaxy += '    )\n'
    else:
        wmsi__uvnf = ', '.join(f'data_arrs_{i}' for i in range(len(eokwm__uzl))
            )
        pcqlb__skaxy += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({wmsi__uvnf},), n_rows)
"""
        pcqlb__skaxy += """    result = bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(
"""
        pcqlb__skaxy += '        (table,), index, column_index\n'
        pcqlb__skaxy += '    )\n'
    pcqlb__skaxy += '    ev.finalize()\n'
    pcqlb__skaxy += '    return result\n'
    grax__fqnb = {}
    bskld__ihzl = {f'data_arr_typ_{i}': gcd__swh for i, gcd__swh in
        enumerate(eokwm__uzl)}
    nrr__fqke = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        uxmhy__rlsns, 'columns_typ': ipn__ongdt, 'index_names_lit':
        foewh__adcx, 'value_names_lit': xdt__xhx, 'columns_name_lit':
        mnzyz__macqk, **bskld__ihzl, 'tracing': tracing}
    exec(pcqlb__skaxy, nrr__fqke, grax__fqnb)
    impl = grax__fqnb['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    nsg__szd = {}
    nsg__szd['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, wwd__qjbw in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        tov__fjjbq = None
        if isinstance(wwd__qjbw, bodo.DatetimeArrayType):
            sxu__syrqv = 'datetimetz'
            rfchd__chydv = 'datetime64[ns]'
            if isinstance(wwd__qjbw.tz, int):
                ijb__dwn = bodo.libs.pd_datetime_arr_ext.nanoseconds_to_offset(
                    wwd__qjbw.tz)
            else:
                ijb__dwn = pd.DatetimeTZDtype(tz=wwd__qjbw.tz).tz
            tov__fjjbq = {'timezone': pa.lib.tzinfo_to_string(ijb__dwn)}
        elif isinstance(wwd__qjbw, types.Array) or wwd__qjbw == boolean_array:
            sxu__syrqv = rfchd__chydv = wwd__qjbw.dtype.name
            if rfchd__chydv.startswith('datetime'):
                sxu__syrqv = 'datetime'
        elif is_str_arr_type(wwd__qjbw):
            sxu__syrqv = 'unicode'
            rfchd__chydv = 'object'
        elif wwd__qjbw == binary_array_type:
            sxu__syrqv = 'bytes'
            rfchd__chydv = 'object'
        elif isinstance(wwd__qjbw, DecimalArrayType):
            sxu__syrqv = rfchd__chydv = 'object'
        elif isinstance(wwd__qjbw, IntegerArrayType):
            bhnwr__bbo = wwd__qjbw.dtype.name
            if bhnwr__bbo.startswith('int'):
                sxu__syrqv = 'Int' + bhnwr__bbo[3:]
            elif bhnwr__bbo.startswith('uint'):
                sxu__syrqv = 'UInt' + bhnwr__bbo[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, wwd__qjbw))
            rfchd__chydv = wwd__qjbw.dtype.name
        elif wwd__qjbw == datetime_date_array_type:
            sxu__syrqv = 'datetime'
            rfchd__chydv = 'object'
        elif isinstance(wwd__qjbw, (StructArrayType, ArrayItemArrayType)):
            sxu__syrqv = 'object'
            rfchd__chydv = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, wwd__qjbw))
        och__hbf = {'name': col_name, 'field_name': col_name, 'pandas_type':
            sxu__syrqv, 'numpy_type': rfchd__chydv, 'metadata': tov__fjjbq}
        nsg__szd['columns'].append(och__hbf)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            xhlqf__jud = '__index_level_0__'
            xoewk__vai = None
        else:
            xhlqf__jud = '%s'
            xoewk__vai = '%s'
        nsg__szd['index_columns'] = [xhlqf__jud]
        nsg__szd['columns'].append({'name': xoewk__vai, 'field_name':
            xhlqf__jud, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        nsg__szd['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        nsg__szd['index_columns'] = []
    nsg__szd['pandas_version'] = pd.__version__
    return nsg__szd


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
        nxjd__shmr = []
        for kfrmm__wthb in partition_cols:
            try:
                idx = df.columns.index(kfrmm__wthb)
            except ValueError as vhkoa__jozpo:
                raise BodoError(
                    f'Partition column {kfrmm__wthb} is not in dataframe')
            nxjd__shmr.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    teb__fbi = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType)
    enysx__ogcw = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not teb__fbi)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not teb__fbi or is_overload_true(
        _is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and teb__fbi and not is_overload_true(_is_parallel)
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
        ziy__ouzse = df.runtime_data_types
        iuf__lyd = len(ziy__ouzse)
        tov__fjjbq = gen_pandas_parquet_metadata([''] * iuf__lyd,
            ziy__ouzse, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        kkbp__ito = tov__fjjbq['columns'][:iuf__lyd]
        tov__fjjbq['columns'] = tov__fjjbq['columns'][iuf__lyd:]
        kkbp__ito = [json.dumps(wxbdj__girge).replace('""', '{0}') for
            wxbdj__girge in kkbp__ito]
        dejw__hvdk = json.dumps(tov__fjjbq)
        mdoz__lwaya = '"columns": ['
        nvlio__lgvaq = dejw__hvdk.find(mdoz__lwaya)
        if nvlio__lgvaq == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        smgmt__rpe = nvlio__lgvaq + len(mdoz__lwaya)
        aveeu__ewf = dejw__hvdk[:smgmt__rpe]
        dejw__hvdk = dejw__hvdk[smgmt__rpe:]
        uyoku__glp = len(tov__fjjbq['columns'])
    else:
        dejw__hvdk = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and teb__fbi:
        dejw__hvdk = dejw__hvdk.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            dejw__hvdk = dejw__hvdk.replace('"%s"', '%s')
    if not df.is_table_format:
        kix__yxjlm = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    pcqlb__skaxy = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        pcqlb__skaxy += '    py_table = get_dataframe_table(df)\n'
        pcqlb__skaxy += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        pcqlb__skaxy += '    info_list = [{}]\n'.format(kix__yxjlm)
        pcqlb__skaxy += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        pcqlb__skaxy += '    columns_index = get_dataframe_column_names(df)\n'
        pcqlb__skaxy += '    names_arr = index_to_array(columns_index)\n'
        pcqlb__skaxy += '    col_names = array_to_info(names_arr)\n'
    else:
        pcqlb__skaxy += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and enysx__ogcw:
        pcqlb__skaxy += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        gfhi__cjbrl = True
    else:
        pcqlb__skaxy += '    index_col = array_to_info(np.empty(0))\n'
        gfhi__cjbrl = False
    if df.has_runtime_cols:
        pcqlb__skaxy += '    columns_lst = []\n'
        pcqlb__skaxy += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            pcqlb__skaxy += f'    for _ in range(len(py_table.block_{i})):\n'
            pcqlb__skaxy += f"""        columns_lst.append({kkbp__ito[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            pcqlb__skaxy += '        num_cols += 1\n'
        if uyoku__glp:
            pcqlb__skaxy += "    columns_lst.append('')\n"
        pcqlb__skaxy += '    columns_str = ", ".join(columns_lst)\n'
        pcqlb__skaxy += ('    metadata = """' + aveeu__ewf +
            '""" + columns_str + """' + dejw__hvdk + '"""\n')
    else:
        pcqlb__skaxy += '    metadata = """' + dejw__hvdk + '"""\n'
    pcqlb__skaxy += '    if compression is None:\n'
    pcqlb__skaxy += "        compression = 'none'\n"
    pcqlb__skaxy += '    if df.index.name is not None:\n'
    pcqlb__skaxy += '        name_ptr = df.index.name\n'
    pcqlb__skaxy += '    else:\n'
    pcqlb__skaxy += "        name_ptr = 'null'\n"
    pcqlb__skaxy += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    hcjg__dal = None
    if partition_cols:
        hcjg__dal = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        mmbe__zoz = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in nxjd__shmr)
        if mmbe__zoz:
            pcqlb__skaxy += '    cat_info_list = [{}]\n'.format(mmbe__zoz)
            pcqlb__skaxy += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            pcqlb__skaxy += '    cat_table = table\n'
        pcqlb__skaxy += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        pcqlb__skaxy += (
            f'    part_cols_idxs = np.array({nxjd__shmr}, dtype=np.int32)\n')
        pcqlb__skaxy += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        pcqlb__skaxy += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        pcqlb__skaxy += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        pcqlb__skaxy += (
            '                            unicode_to_utf8(compression),\n')
        pcqlb__skaxy += '                            _is_parallel,\n'
        pcqlb__skaxy += (
            '                            unicode_to_utf8(bucket_region),\n')
        pcqlb__skaxy += '                            row_group_size,\n'
        pcqlb__skaxy += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pcqlb__skaxy += '    delete_table_decref_arrays(table)\n'
        pcqlb__skaxy += '    delete_info_decref_array(index_col)\n'
        pcqlb__skaxy += (
            '    delete_info_decref_array(col_names_no_partitions)\n')
        pcqlb__skaxy += '    delete_info_decref_array(col_names)\n'
        if mmbe__zoz:
            pcqlb__skaxy += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        pcqlb__skaxy += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        pcqlb__skaxy += (
            '                            table, col_names, index_col,\n')
        pcqlb__skaxy += '                            ' + str(gfhi__cjbrl
            ) + ',\n'
        pcqlb__skaxy += (
            '                            unicode_to_utf8(metadata),\n')
        pcqlb__skaxy += (
            '                            unicode_to_utf8(compression),\n')
        pcqlb__skaxy += (
            '                            _is_parallel, 1, df.index.start,\n')
        pcqlb__skaxy += (
            '                            df.index.stop, df.index.step,\n')
        pcqlb__skaxy += (
            '                            unicode_to_utf8(name_ptr),\n')
        pcqlb__skaxy += (
            '                            unicode_to_utf8(bucket_region),\n')
        pcqlb__skaxy += '                            row_group_size,\n'
        pcqlb__skaxy += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pcqlb__skaxy += '    delete_table_decref_arrays(table)\n'
        pcqlb__skaxy += '    delete_info_decref_array(index_col)\n'
        pcqlb__skaxy += '    delete_info_decref_array(col_names)\n'
    else:
        pcqlb__skaxy += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        pcqlb__skaxy += (
            '                            table, col_names, index_col,\n')
        pcqlb__skaxy += '                            ' + str(gfhi__cjbrl
            ) + ',\n'
        pcqlb__skaxy += (
            '                            unicode_to_utf8(metadata),\n')
        pcqlb__skaxy += (
            '                            unicode_to_utf8(compression),\n')
        pcqlb__skaxy += (
            '                            _is_parallel, 0, 0, 0, 0,\n')
        pcqlb__skaxy += (
            '                            unicode_to_utf8(name_ptr),\n')
        pcqlb__skaxy += (
            '                            unicode_to_utf8(bucket_region),\n')
        pcqlb__skaxy += '                            row_group_size,\n'
        pcqlb__skaxy += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pcqlb__skaxy += '    delete_table_decref_arrays(table)\n'
        pcqlb__skaxy += '    delete_info_decref_array(index_col)\n'
        pcqlb__skaxy += '    delete_info_decref_array(col_names)\n'
    grax__fqnb = {}
    if df.has_runtime_cols:
        htwdj__kseb = None
    else:
        for vokeb__usuny in df.columns:
            if not isinstance(vokeb__usuny, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        htwdj__kseb = pd.array(df.columns)
    exec(pcqlb__skaxy, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': htwdj__kseb,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': hcjg__dal, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, grax__fqnb)
    kscat__xmfc = grax__fqnb['df_to_parquet']
    return kscat__xmfc


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    zjhwc__cqyxm = 'all_ok'
    bprzz__wuo, kwzki__gjcw = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        ihfz__par = 100
        if chunksize is None:
            ghp__urkkd = ihfz__par
        else:
            ghp__urkkd = min(chunksize, ihfz__par)
        if _is_table_create:
            df = df.iloc[:ghp__urkkd, :]
        else:
            df = df.iloc[ghp__urkkd:, :]
            if len(df) == 0:
                return zjhwc__cqyxm
    ozsz__aab = df.columns
    try:
        if bprzz__wuo == 'snowflake':
            if kwzki__gjcw and con.count(kwzki__gjcw) == 1:
                con = con.replace(kwzki__gjcw, quote(kwzki__gjcw))
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
                df.columns = [(qjwah__jmsvp.upper() if qjwah__jmsvp.islower
                    () else qjwah__jmsvp) for qjwah__jmsvp in df.columns]
            except ImportError as vhkoa__jozpo:
                zjhwc__cqyxm = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return zjhwc__cqyxm
        if bprzz__wuo == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            tzr__itj = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            zugap__knnva = bodo.typeof(df)
            hiq__gwro = {}
            for qjwah__jmsvp, sfg__tgs in zip(zugap__knnva.columns,
                zugap__knnva.data):
                if df[qjwah__jmsvp].dtype == 'object':
                    if sfg__tgs == datetime_date_array_type:
                        hiq__gwro[qjwah__jmsvp] = sa.types.Date
                    elif sfg__tgs in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not tzr__itj or tzr__itj == '0'
                        ):
                        hiq__gwro[qjwah__jmsvp] = VARCHAR2(4000)
            dtype = hiq__gwro
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as mhui__ppso:
            zjhwc__cqyxm = mhui__ppso.args[0]
            if bprzz__wuo == 'oracle' and 'ORA-12899' in zjhwc__cqyxm:
                zjhwc__cqyxm += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return zjhwc__cqyxm
    finally:
        df.columns = ozsz__aab


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
    pcqlb__skaxy = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    pcqlb__skaxy += f"    if con.startswith('iceberg'):\n"
    pcqlb__skaxy += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    pcqlb__skaxy += f'        if schema is None:\n'
    pcqlb__skaxy += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    pcqlb__skaxy += f'        if chunksize is not None:\n'
    pcqlb__skaxy += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    pcqlb__skaxy += f'        if index and bodo.get_rank() == 0:\n'
    pcqlb__skaxy += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    pcqlb__skaxy += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    pcqlb__skaxy += f"""            warnings.warn('index_label is not supported for Iceberg tables.')
"""
    if df.is_table_format:
        pcqlb__skaxy += f'        py_table = get_dataframe_table(df)\n'
        pcqlb__skaxy += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        kix__yxjlm = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        pcqlb__skaxy += f'        info_list = [{kix__yxjlm}]\n'
        pcqlb__skaxy += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        pcqlb__skaxy += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        pcqlb__skaxy += f'        names_arr = index_to_array(columns_index)\n'
        pcqlb__skaxy += f'        col_names = array_to_info(names_arr)\n'
    else:
        pcqlb__skaxy += f'        col_names = array_to_info(col_names_arr)\n'
    pcqlb__skaxy += """        bodo.io.iceberg.iceberg_write(
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
    pcqlb__skaxy += f'        delete_table_decref_arrays(table)\n'
    pcqlb__skaxy += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        htwdj__kseb = None
    else:
        for vokeb__usuny in df.columns:
            if not isinstance(vokeb__usuny, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        htwdj__kseb = pd.array(df.columns)
    pcqlb__skaxy += f'    else:\n'
    pcqlb__skaxy += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    pcqlb__skaxy += f"        err_msg = 'unset'\n"
    pcqlb__skaxy += f'        if rank != 0:\n'
    pcqlb__skaxy += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    pcqlb__skaxy += f'        elif rank == 0:\n'
    pcqlb__skaxy += f'            err_msg = to_sql_exception_guard_encaps(\n'
    pcqlb__skaxy += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    pcqlb__skaxy += f'                          chunksize, dtype, method,\n'
    pcqlb__skaxy += f'                          True, _is_parallel,\n'
    pcqlb__skaxy += f'                      )\n'
    pcqlb__skaxy += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    pcqlb__skaxy += f"        if_exists = 'append'\n"
    pcqlb__skaxy += f"        if _is_parallel and err_msg == 'all_ok':\n"
    pcqlb__skaxy += f'            err_msg = to_sql_exception_guard_encaps(\n'
    pcqlb__skaxy += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    pcqlb__skaxy += f'                          chunksize, dtype, method,\n'
    pcqlb__skaxy += f'                          False, _is_parallel,\n'
    pcqlb__skaxy += f'                      )\n'
    pcqlb__skaxy += f"        if err_msg != 'all_ok':\n"
    pcqlb__skaxy += f"            print('err_msg=', err_msg)\n"
    pcqlb__skaxy += (
        f"            raise ValueError('error in to_sql() operation')\n")
    grax__fqnb = {}
    exec(pcqlb__skaxy, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_to_cpp_table':
        py_table_to_cpp_table, 'py_table_typ': df.table_type,
        'col_names_arr': htwdj__kseb, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'delete_info_decref_array':
        delete_info_decref_array, 'arr_info_list_to_table':
        arr_info_list_to_table, 'index_to_array': index_to_array,
        'pyarrow_table_schema': bodo.io.iceberg.pyarrow_schema(df),
        'to_sql_exception_guard_encaps': to_sql_exception_guard_encaps,
        'warnings': warnings}, grax__fqnb)
    _impl = grax__fqnb['df_to_sql']
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
        guz__lcf = get_overload_const_str(path_or_buf)
        if guz__lcf.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        ngqk__bnxpz = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(ngqk__bnxpz), unicode_to_utf8(
                _bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(ngqk__bnxpz), unicode_to_utf8(
                _bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    dyg__jkyh = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    shcia__yfuz = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', dyg__jkyh, shcia__yfuz,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    pcqlb__skaxy = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        bxi__shejd = data.data.dtype.categories
        pcqlb__skaxy += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        bxi__shejd = data.dtype.categories
        pcqlb__skaxy += '  data_values = data\n'
    dklb__ocgxm = len(bxi__shejd)
    pcqlb__skaxy += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    pcqlb__skaxy += '  numba.parfors.parfor.init_prange()\n'
    pcqlb__skaxy += '  n = len(data_values)\n'
    for i in range(dklb__ocgxm):
        pcqlb__skaxy += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    pcqlb__skaxy += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    pcqlb__skaxy += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for fxoti__mhv in range(dklb__ocgxm):
        pcqlb__skaxy += '          data_arr_{}[i] = 0\n'.format(fxoti__mhv)
    pcqlb__skaxy += '      else:\n'
    for ido__ovx in range(dklb__ocgxm):
        pcqlb__skaxy += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            ido__ovx)
    kix__yxjlm = ', '.join(f'data_arr_{i}' for i in range(dklb__ocgxm))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(bxi__shejd[0], np.datetime64):
        bxi__shejd = tuple(pd.Timestamp(qjwah__jmsvp) for qjwah__jmsvp in
            bxi__shejd)
    elif isinstance(bxi__shejd[0], np.timedelta64):
        bxi__shejd = tuple(pd.Timedelta(qjwah__jmsvp) for qjwah__jmsvp in
            bxi__shejd)
    return bodo.hiframes.dataframe_impl._gen_init_df(pcqlb__skaxy,
        bxi__shejd, kix__yxjlm, index)


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
    for uonjd__avzy in pd_unsupported:
        heuk__fch = mod_name + '.' + uonjd__avzy.__name__
        overload(uonjd__avzy, no_unliteral=True)(create_unsupported_overload
            (heuk__fch))


def _install_dataframe_unsupported():
    for ujifl__dpdw in dataframe_unsupported_attrs:
        vtvo__vdm = 'DataFrame.' + ujifl__dpdw
        overload_attribute(DataFrameType, ujifl__dpdw)(
            create_unsupported_overload(vtvo__vdm))
    for heuk__fch in dataframe_unsupported:
        vtvo__vdm = 'DataFrame.' + heuk__fch + '()'
        overload_method(DataFrameType, heuk__fch)(create_unsupported_overload
            (vtvo__vdm))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
