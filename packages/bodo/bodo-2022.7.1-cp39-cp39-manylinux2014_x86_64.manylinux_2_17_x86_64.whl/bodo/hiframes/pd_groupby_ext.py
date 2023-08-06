"""Support for Pandas Groupby operations
"""
import operator
from enum import Enum
import numba
import numpy as np
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, get_groupby_labels, get_null_shuffle_info, get_shuffle_info, info_from_table, info_to_array, reverse_shuffle_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_call_expr_arg, get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_index_name_types, get_literal_value, get_overload_const_bool, get_overload_const_func, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, get_udf_error_msg, get_udf_out_arr_type, is_dtype_nullable, is_literal_type, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, list_cumulative, raise_bodo_error, to_nullable_type, to_numeric_index_if_range_index, to_str_arr_if_dict_array
from bodo.utils.utils import dt_err, is_expr


class DataFrameGroupByType(types.Type):

    def __init__(self, df_type, keys, selection, as_index, dropna=True,
        explicit_select=False, series_select=False, _num_shuffle_keys=-1):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df_type,
            'pandas.groupby()')
        self.df_type = df_type
        self.keys = keys
        self.selection = selection
        self.as_index = as_index
        self.dropna = dropna
        self.explicit_select = explicit_select
        self.series_select = series_select
        self._num_shuffle_keys = _num_shuffle_keys
        super(DataFrameGroupByType, self).__init__(name=
            f'DataFrameGroupBy({df_type}, {keys}, {selection}, {as_index}, {dropna}, {explicit_select}, {series_select}, {_num_shuffle_keys})'
            )

    def copy(self):
        return DataFrameGroupByType(self.df_type, self.keys, self.selection,
            self.as_index, self.dropna, self.explicit_select, self.
            series_select, self._num_shuffle_keys)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFrameGroupByType)
class GroupbyModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zwpw__gouk = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, zwpw__gouk)


make_attribute_wrapper(DataFrameGroupByType, 'obj', 'obj')


def validate_udf(func_name, func):
    if not isinstance(func, (types.functions.MakeFunctionLiteral, bodo.
        utils.typing.FunctionLiteral, types.Dispatcher, CPUDispatcher)):
        raise_bodo_error(
            f"Groupby.{func_name}: 'func' must be user defined function")


@intrinsic
def init_groupby(typingctx, obj_type, by_type, as_index_type, dropna_type,
    _num_shuffle_keys):

    def codegen(context, builder, signature, args):
        htr__kpcsq = args[0]
        scsin__zip = signature.return_type
        bopa__zhqyc = cgutils.create_struct_proxy(scsin__zip)(context, builder)
        bopa__zhqyc.obj = htr__kpcsq
        context.nrt.incref(builder, signature.args[0], htr__kpcsq)
        return bopa__zhqyc._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for myy__almr in keys:
        selection.remove(myy__almr)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    if is_overload_constant_int(_num_shuffle_keys):
        brg__czuav = get_overload_const_int(_num_shuffle_keys)
    else:
        brg__czuav = -1
    scsin__zip = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False, _num_shuffle_keys=brg__czuav)
    return scsin__zip(obj_type, by_type, as_index_type, dropna_type,
        _num_shuffle_keys), codegen


@lower_builtin('groupby.count', types.VarArg(types.Any))
@lower_builtin('groupby.size', types.VarArg(types.Any))
@lower_builtin('groupby.apply', types.VarArg(types.Any))
@lower_builtin('groupby.agg', types.VarArg(types.Any))
def lower_groupby_count_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@infer
class StaticGetItemDataFrameGroupBy(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        grpby, rpeyk__wsbb = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(rpeyk__wsbb, (tuple, list)):
                if len(set(rpeyk__wsbb).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(rpeyk__wsbb).difference(set(grpby.
                        df_type.columns))))
                selection = rpeyk__wsbb
            else:
                if rpeyk__wsbb not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(rpeyk__wsbb))
                selection = rpeyk__wsbb,
                series_select = True
            zlpi__yiz = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True,
                series_select, _num_shuffle_keys=grpby._num_shuffle_keys)
            return signature(zlpi__yiz, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, rpeyk__wsbb = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            rpeyk__wsbb):
            zlpi__yiz = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(rpeyk__wsbb)), {}).return_type
            return signature(zlpi__yiz, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    pdon__ryau = arr_type == ArrayItemArrayType(string_array_type)
    eht__ryha = arr_type.dtype
    if isinstance(eht__ryha, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {eht__ryha} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(eht__ryha, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {eht__ryha} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(eht__ryha,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(eht__ryha, (types.Integer, types.Float, types.Boolean)):
        if pdon__ryau or eht__ryha == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(eht__ryha, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not eht__ryha.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {eht__ryha} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(eht__ryha, types.Boolean) and func_name in {'cumsum',
        'sum', 'mean', 'std', 'var'}:
        return (None,
            f'groupby built-in functions {func_name} does not support boolean column'
            )
    if func_name in {'idxmin', 'idxmax'}:
        return dtype_to_array_type(get_index_data_arr_types(index_type)[0].
            dtype), 'ok'
    if func_name in {'count', 'nunique'}:
        return dtype_to_array_type(types.int64), 'ok'
    else:
        return arr_type, 'ok'


def get_pivot_output_dtype(arr_type, func_name, index_type=None):
    eht__ryha = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(eht__ryha, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(eht__ryha, types.Integer):
            return IntDtype(eht__ryha)
        return eht__ryha
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        stdsr__mzcl = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{stdsr__mzcl}'."
            )
    elif len(args) > len_args:
        raise BodoError(
            f'Groupby.{func_name}() takes {len_args + 1} positional argument but {len(args)} were given.'
            )


class ColumnType(Enum):
    KeyColumn = 0
    NumericalColumn = 1
    NonNumericalColumn = 2


def get_keys_not_as_index(grp, out_columns, out_data, out_column_type,
    multi_level_names=False):
    for myy__almr in grp.keys:
        if multi_level_names:
            nit__dbul = myy__almr, ''
        else:
            nit__dbul = myy__almr
        vzfo__nvo = grp.df_type.column_index[myy__almr]
        data = grp.df_type.data[vzfo__nvo]
        out_columns.append(nit__dbul)
        out_data.append(data)
        out_column_type.append(ColumnType.KeyColumn.value)


def get_agg_typ(grp, args, func_name, typing_context, target_context, func=
    None, kws=None):
    index = RangeIndexType(types.none)
    out_data = []
    out_columns = []
    out_column_type = []
    if func_name in ('head', 'ngroup'):
        grp.as_index = True
    if not grp.as_index:
        get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
    elif func_name in ('head', 'ngroup'):
        if grp.df_type.index == index:
            index = NumericIndexType(types.int64, types.none)
        else:
            index = grp.df_type.index
    elif len(grp.keys) > 1:
        nvtxx__gade = tuple(grp.df_type.column_index[grp.keys[hkire__yjyqo]
            ] for hkire__yjyqo in range(len(grp.keys)))
        caw__wid = tuple(grp.df_type.data[vzfo__nvo] for vzfo__nvo in
            nvtxx__gade)
        index = MultiIndexType(caw__wid, tuple(types.StringLiteral(
            myy__almr) for myy__almr in grp.keys))
    else:
        vzfo__nvo = grp.df_type.column_index[grp.keys[0]]
        tzuca__zixcf = grp.df_type.data[vzfo__nvo]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(tzuca__zixcf,
            types.StringLiteral(grp.keys[0]))
    dwxg__tast = {}
    kotrm__bif = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        dwxg__tast[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        dwxg__tast[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        anvj__ynjre = dict(ascending=ascending)
        eabfc__ogla = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', anvj__ynjre,
            eabfc__ogla, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for cjnyq__lwt in columns:
            vzfo__nvo = grp.df_type.column_index[cjnyq__lwt]
            data = grp.df_type.data[vzfo__nvo]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            puf__gyik = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                puf__gyik = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    mtv__tmgit = SeriesType(data.dtype, data, None, string_type
                        )
                    iwr__pcy = get_const_func_output_type(func, (mtv__tmgit
                        ,), {}, typing_context, target_context)
                    if iwr__pcy != ArrayItemArrayType(string_array_type):
                        iwr__pcy = dtype_to_array_type(iwr__pcy)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=cjnyq__lwt, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    kvyp__yarbf = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    vsf__ubnld = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    anvj__ynjre = dict(numeric_only=kvyp__yarbf, min_count=
                        vsf__ubnld)
                    eabfc__ogla = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        anvj__ynjre, eabfc__ogla, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    kvyp__yarbf = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    vsf__ubnld = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    anvj__ynjre = dict(numeric_only=kvyp__yarbf, min_count=
                        vsf__ubnld)
                    eabfc__ogla = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        anvj__ynjre, eabfc__ogla, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    kvyp__yarbf = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    anvj__ynjre = dict(numeric_only=kvyp__yarbf)
                    eabfc__ogla = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        anvj__ynjre, eabfc__ogla, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    ocyfd__fud = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    zxzqj__szcl = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    anvj__ynjre = dict(axis=ocyfd__fud, skipna=zxzqj__szcl)
                    eabfc__ogla = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        anvj__ynjre, eabfc__ogla, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    ldlu__gkn = args[0] if len(args) > 0 else kws.pop('ddof', 1
                        )
                    anvj__ynjre = dict(ddof=ldlu__gkn)
                    eabfc__ogla = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        anvj__ynjre, eabfc__ogla, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                iwr__pcy, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                iwr__pcy = to_str_arr_if_dict_array(iwr__pcy) if func_name in (
                    'sum', 'cumsum') else iwr__pcy
                out_data.append(iwr__pcy)
                out_columns.append(cjnyq__lwt)
                if func_name == 'agg':
                    bnv__vou = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    dwxg__tast[cjnyq__lwt, bnv__vou] = cjnyq__lwt
                else:
                    dwxg__tast[cjnyq__lwt, func_name] = cjnyq__lwt
                out_column_type.append(puf__gyik)
            else:
                kotrm__bif.append(err_msg)
    if func_name == 'sum':
        nujfb__hpr = any([(jubn__nqjq == ColumnType.NumericalColumn.value) for
            jubn__nqjq in out_column_type])
        if nujfb__hpr:
            out_data = [jubn__nqjq for jubn__nqjq, iktrc__ovytb in zip(
                out_data, out_column_type) if iktrc__ovytb != ColumnType.
                NonNumericalColumn.value]
            out_columns = [jubn__nqjq for jubn__nqjq, iktrc__ovytb in zip(
                out_columns, out_column_type) if iktrc__ovytb != ColumnType
                .NonNumericalColumn.value]
            dwxg__tast = {}
            for cjnyq__lwt in out_columns:
                if grp.as_index is False and cjnyq__lwt in grp.keys:
                    continue
                dwxg__tast[cjnyq__lwt, func_name] = cjnyq__lwt
    xzwcg__yejlf = len(kotrm__bif)
    if len(out_data) == 0:
        if xzwcg__yejlf == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(xzwcg__yejlf, ' was' if xzwcg__yejlf == 1 else
                's were', ','.join(kotrm__bif)))
    rqm__cmr = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            pna__ddcv = IntDtype(out_data[0].dtype)
        else:
            pna__ddcv = out_data[0].dtype
        ezjet__jkvjj = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        rqm__cmr = SeriesType(pna__ddcv, data=out_data[0], index=index,
            name_typ=ezjet__jkvjj)
    return signature(rqm__cmr, *args), dwxg__tast


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    bqc__zbcy = True
    if isinstance(f_val, str):
        bqc__zbcy = False
        lklmo__chtk = f_val
    elif is_overload_constant_str(f_val):
        bqc__zbcy = False
        lklmo__chtk = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        bqc__zbcy = False
        lklmo__chtk = bodo.utils.typing.get_builtin_function_name(f_val)
    if not bqc__zbcy:
        if lklmo__chtk not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {lklmo__chtk}')
        zlpi__yiz = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp
            .as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(zlpi__yiz, (), lklmo__chtk, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            slg__vuwgw = types.functions.MakeFunctionLiteral(f_val)
        else:
            slg__vuwgw = f_val
        validate_udf('agg', slg__vuwgw)
        func = get_overload_const_func(slg__vuwgw, None)
        jodr__emiv = func.code if hasattr(func, 'code') else func.__code__
        lklmo__chtk = jodr__emiv.co_name
        zlpi__yiz = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp
            .as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(zlpi__yiz, (), 'agg', typing_context,
            target_context, slg__vuwgw)[0].return_type
    return lklmo__chtk, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    krhq__dzu = kws and all(isinstance(efxu__rud, types.Tuple) and len(
        efxu__rud) == 2 for efxu__rud in kws.values())
    if is_overload_none(func) and not krhq__dzu:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not krhq__dzu:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    feo__blu = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if krhq__dzu or is_overload_constant_dict(func):
        if krhq__dzu:
            nohaf__pln = [get_literal_value(yxekk__fmipr) for yxekk__fmipr,
                ktod__pstll in kws.values()]
            mxq__aue = [get_literal_value(cdv__alh) for ktod__pstll,
                cdv__alh in kws.values()]
        else:
            hqy__ubjfh = get_overload_constant_dict(func)
            nohaf__pln = tuple(hqy__ubjfh.keys())
            mxq__aue = tuple(hqy__ubjfh.values())
        for cvmcs__dvo in ('head', 'ngroup'):
            if cvmcs__dvo in mxq__aue:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {cvmcs__dvo} cannot be mixed with other groupby operations.'
                    )
        if any(cjnyq__lwt not in grp.selection and cjnyq__lwt not in grp.
            keys for cjnyq__lwt in nohaf__pln):
            raise_bodo_error(
                f'Selected column names {nohaf__pln} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            mxq__aue)
        if krhq__dzu and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        dwxg__tast = {}
        out_columns = []
        out_data = []
        out_column_type = []
        ohzr__iauh = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for dpwk__rgxw, f_val in zip(nohaf__pln, mxq__aue):
            if isinstance(f_val, (tuple, list)):
                xsrx__gvud = 0
                for slg__vuwgw in f_val:
                    lklmo__chtk, out_tp = get_agg_funcname_and_outtyp(grp,
                        dpwk__rgxw, slg__vuwgw, typing_context, target_context)
                    feo__blu = lklmo__chtk in list_cumulative
                    if lklmo__chtk == '<lambda>' and len(f_val) > 1:
                        lklmo__chtk = '<lambda_' + str(xsrx__gvud) + '>'
                        xsrx__gvud += 1
                    out_columns.append((dpwk__rgxw, lklmo__chtk))
                    dwxg__tast[dpwk__rgxw, lklmo__chtk
                        ] = dpwk__rgxw, lklmo__chtk
                    _append_out_type(grp, out_data, out_tp)
            else:
                lklmo__chtk, out_tp = get_agg_funcname_and_outtyp(grp,
                    dpwk__rgxw, f_val, typing_context, target_context)
                feo__blu = lklmo__chtk in list_cumulative
                if multi_level_names:
                    out_columns.append((dpwk__rgxw, lklmo__chtk))
                    dwxg__tast[dpwk__rgxw, lklmo__chtk
                        ] = dpwk__rgxw, lklmo__chtk
                elif not krhq__dzu:
                    out_columns.append(dpwk__rgxw)
                    dwxg__tast[dpwk__rgxw, lklmo__chtk] = dpwk__rgxw
                elif krhq__dzu:
                    ohzr__iauh.append(lklmo__chtk)
                _append_out_type(grp, out_data, out_tp)
        if krhq__dzu:
            for hkire__yjyqo, gkt__xyld in enumerate(kws.keys()):
                out_columns.append(gkt__xyld)
                dwxg__tast[nohaf__pln[hkire__yjyqo], ohzr__iauh[hkire__yjyqo]
                    ] = gkt__xyld
        if feo__blu:
            index = grp.df_type.index
        else:
            index = out_tp.index
        rqm__cmr = DataFrameType(tuple(out_data), index, tuple(out_columns),
            is_table_format=True)
        return signature(rqm__cmr, *args), dwxg__tast
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            izvf__omfj = get_overload_const_list(func)
        else:
            izvf__omfj = func.types
        if len(izvf__omfj) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        xsrx__gvud = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        dwxg__tast = {}
        nrxx__lktk = grp.selection[0]
        for f_val in izvf__omfj:
            lklmo__chtk, out_tp = get_agg_funcname_and_outtyp(grp,
                nrxx__lktk, f_val, typing_context, target_context)
            feo__blu = lklmo__chtk in list_cumulative
            if lklmo__chtk == '<lambda>' and len(izvf__omfj) > 1:
                lklmo__chtk = '<lambda_' + str(xsrx__gvud) + '>'
                xsrx__gvud += 1
            out_columns.append(lklmo__chtk)
            dwxg__tast[nrxx__lktk, lklmo__chtk] = lklmo__chtk
            _append_out_type(grp, out_data, out_tp)
        if feo__blu:
            index = grp.df_type.index
        else:
            index = out_tp.index
        rqm__cmr = DataFrameType(tuple(out_data), index, tuple(out_columns),
            is_table_format=True)
        return signature(rqm__cmr, *args), dwxg__tast
    lklmo__chtk = ''
    if types.unliteral(func) == types.unicode_type:
        lklmo__chtk = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        lklmo__chtk = bodo.utils.typing.get_builtin_function_name(func)
    if lklmo__chtk:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, lklmo__chtk, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = to_numeric_index_if_range_index(grp.df_type.index)
    if isinstance(index, MultiIndexType):
        raise_bodo_error(
            f'Groupby.{name_operation}: MultiIndex input not supported for groupby operations that use input Index'
            )
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        ocyfd__fud = args[0] if len(args) > 0 else kws.pop('axis', 0)
        kvyp__yarbf = args[1] if len(args) > 1 else kws.pop('numeric_only',
            False)
        zxzqj__szcl = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        anvj__ynjre = dict(axis=ocyfd__fud, numeric_only=kvyp__yarbf)
        eabfc__ogla = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', anvj__ynjre,
            eabfc__ogla, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        dahh__bswf = args[0] if len(args) > 0 else kws.pop('periods', 1)
        dkq__waxny = args[1] if len(args) > 1 else kws.pop('freq', None)
        ocyfd__fud = args[2] if len(args) > 2 else kws.pop('axis', 0)
        cbpey__ckvkk = args[3] if len(args) > 3 else kws.pop('fill_value', None
            )
        anvj__ynjre = dict(freq=dkq__waxny, axis=ocyfd__fud, fill_value=
            cbpey__ckvkk)
        eabfc__ogla = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', anvj__ynjre,
            eabfc__ogla, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        xiy__djxy = args[0] if len(args) > 0 else kws.pop('func', None)
        lbl__hfh = kws.pop('engine', None)
        usrs__wxr = kws.pop('engine_kwargs', None)
        anvj__ynjre = dict(engine=lbl__hfh, engine_kwargs=usrs__wxr)
        eabfc__ogla = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', anvj__ynjre,
            eabfc__ogla, package_name='pandas', module_name='GroupBy')
    dwxg__tast = {}
    for cjnyq__lwt in grp.selection:
        out_columns.append(cjnyq__lwt)
        dwxg__tast[cjnyq__lwt, name_operation] = cjnyq__lwt
        vzfo__nvo = grp.df_type.column_index[cjnyq__lwt]
        data = grp.df_type.data[vzfo__nvo]
        gueo__evcov = (name_operation if name_operation != 'transform' else
            get_literal_value(xiy__djxy))
        if gueo__evcov in ('sum', 'cumsum'):
            data = to_str_arr_if_dict_array(data)
        if name_operation == 'cumprod':
            if not isinstance(data.dtype, (types.Integer, types.Float)):
                raise BodoError(msg)
        if name_operation == 'cumsum':
            if data.dtype != types.unicode_type and data != ArrayItemArrayType(
                string_array_type) and not isinstance(data.dtype, (types.
                Integer, types.Float)):
                raise BodoError(msg)
        if name_operation in ('cummin', 'cummax'):
            if not isinstance(data.dtype, types.Integer
                ) and not is_dtype_nullable(data.dtype):
                raise BodoError(msg)
        if name_operation == 'shift':
            if isinstance(data, (TupleArrayType, ArrayItemArrayType)):
                raise BodoError(msg)
            if isinstance(data.dtype, bodo.hiframes.datetime_timedelta_ext.
                DatetimeTimeDeltaType):
                raise BodoError(
                    f"""column type of {data.dtype} is not supported in groupby built-in function shift.
{dt_err}"""
                    )
        if name_operation == 'transform':
            iwr__pcy, err_msg = get_groupby_output_dtype(data,
                get_literal_value(xiy__djxy), grp.df_type.index)
            if err_msg == 'ok':
                data = iwr__pcy
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    rqm__cmr = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        rqm__cmr = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(rqm__cmr, *args), dwxg__tast


def resolve_gb(grp, args, kws, func_name, typing_context, target_context,
    err_msg=''):
    if func_name in set(list_cumulative) | {'shift', 'transform'}:
        return resolve_transformative(grp, args, kws, err_msg, func_name)
    elif func_name in {'agg', 'aggregate'}:
        return resolve_agg(grp, args, kws, typing_context, target_context)
    else:
        return get_agg_typ(grp, args, func_name, typing_context,
            target_context, kws=kws)


@infer_getattr
class DataframeGroupByAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameGroupByType
    _attr_set = None

    @bound_function('groupby.agg', no_unliteral=True)
    def resolve_agg(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.aggregate', no_unliteral=True)
    def resolve_aggregate(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.sum', no_unliteral=True)
    def resolve_sum(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'sum', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.count', no_unliteral=True)
    def resolve_count(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'count', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.nunique', no_unliteral=True)
    def resolve_nunique(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'nunique', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.median', no_unliteral=True)
    def resolve_median(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'median', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.mean', no_unliteral=True)
    def resolve_mean(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'mean', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.min', no_unliteral=True)
    def resolve_min(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'min', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.max', no_unliteral=True)
    def resolve_max(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'max', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.prod', no_unliteral=True)
    def resolve_prod(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'prod', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.var', no_unliteral=True)
    def resolve_var(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'var', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.std', no_unliteral=True)
    def resolve_std(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'std', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.first', no_unliteral=True)
    def resolve_first(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'first', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.last', no_unliteral=True)
    def resolve_last(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'last', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmin', no_unliteral=True)
    def resolve_idxmin(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmin', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmax', no_unliteral=True)
    def resolve_idxmax(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmax', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.size', no_unliteral=True)
    def resolve_size(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'size', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.cumsum', no_unliteral=True)
    def resolve_cumsum(self, grp, args, kws):
        msg = (
            'Groupby.cumsum() only supports columns of types integer, float, string or liststring'
            )
        return resolve_gb(grp, args, kws, 'cumsum', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cumprod', no_unliteral=True)
    def resolve_cumprod(self, grp, args, kws):
        msg = (
            'Groupby.cumprod() only supports columns of types integer and float'
            )
        return resolve_gb(grp, args, kws, 'cumprod', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummin', no_unliteral=True)
    def resolve_cummin(self, grp, args, kws):
        msg = (
            'Groupby.cummin() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummin', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummax', no_unliteral=True)
    def resolve_cummax(self, grp, args, kws):
        msg = (
            'Groupby.cummax() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummax', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.shift', no_unliteral=True)
    def resolve_shift(self, grp, args, kws):
        msg = (
            'Column type of list/tuple is not supported in groupby built-in function shift'
            )
        return resolve_gb(grp, args, kws, 'shift', self.context, numba.core
            .registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.pipe', no_unliteral=True)
    def resolve_pipe(self, grp, args, kws):
        return resolve_obj_pipe(self, grp, args, kws, 'GroupBy')

    @bound_function('groupby.transform', no_unliteral=True)
    def resolve_transform(self, grp, args, kws):
        msg = (
            'Groupby.transform() only supports sum, count, min, max, mean, and std operations'
            )
        return resolve_gb(grp, args, kws, 'transform', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.head', no_unliteral=True)
    def resolve_head(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'head', self.context, numba.core.
            registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.ngroup', no_unliteral=True)
    def resolve_ngroup(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'ngroup', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.apply', no_unliteral=True)
    def resolve_apply(self, grp, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws.pop('func', None)
        f_args = tuple(args[1:]) if len(args) > 0 else ()
        hbg__hisnz = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        wzu__cbg = isinstance(hbg__hisnz, (SeriesType, HeterogeneousSeriesType)
            ) and hbg__hisnz.const_info is not None or not isinstance(
            hbg__hisnz, (SeriesType, DataFrameType))
        if wzu__cbg:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                leuf__pkoob = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                nvtxx__gade = tuple(grp.df_type.column_index[grp.keys[
                    hkire__yjyqo]] for hkire__yjyqo in range(len(grp.keys)))
                caw__wid = tuple(grp.df_type.data[vzfo__nvo] for vzfo__nvo in
                    nvtxx__gade)
                leuf__pkoob = MultiIndexType(caw__wid, tuple(types.literal(
                    myy__almr) for myy__almr in grp.keys))
            else:
                vzfo__nvo = grp.df_type.column_index[grp.keys[0]]
                tzuca__zixcf = grp.df_type.data[vzfo__nvo]
                leuf__pkoob = bodo.hiframes.pd_index_ext.array_type_to_index(
                    tzuca__zixcf, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            tdwi__jdb = tuple(grp.df_type.data[grp.df_type.column_index[
                cjnyq__lwt]] for cjnyq__lwt in grp.keys)
            qwxm__rqt = tuple(types.literal(efxu__rud) for efxu__rud in grp
                .keys) + get_index_name_types(hbg__hisnz.index)
            if not grp.as_index:
                tdwi__jdb = types.Array(types.int64, 1, 'C'),
                qwxm__rqt = (types.none,) + get_index_name_types(hbg__hisnz
                    .index)
            leuf__pkoob = MultiIndexType(tdwi__jdb +
                get_index_data_arr_types(hbg__hisnz.index), qwxm__rqt)
        if wzu__cbg:
            if isinstance(hbg__hisnz, HeterogeneousSeriesType):
                ktod__pstll, hru__ltyv = hbg__hisnz.const_info
                if isinstance(hbg__hisnz.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    hqzhe__ubhg = hbg__hisnz.data.tuple_typ.types
                elif isinstance(hbg__hisnz.data, types.Tuple):
                    hqzhe__ubhg = hbg__hisnz.data.types
                sue__sydn = tuple(to_nullable_type(dtype_to_array_type(
                    qjx__aiqbl)) for qjx__aiqbl in hqzhe__ubhg)
                ibggi__kgb = DataFrameType(out_data + sue__sydn,
                    leuf__pkoob, out_columns + hru__ltyv)
            elif isinstance(hbg__hisnz, SeriesType):
                sxfoh__rdnwl, hru__ltyv = hbg__hisnz.const_info
                sue__sydn = tuple(to_nullable_type(dtype_to_array_type(
                    hbg__hisnz.dtype)) for ktod__pstll in range(sxfoh__rdnwl))
                ibggi__kgb = DataFrameType(out_data + sue__sydn,
                    leuf__pkoob, out_columns + hru__ltyv)
            else:
                wuiqs__rsvwx = get_udf_out_arr_type(hbg__hisnz)
                if not grp.as_index:
                    ibggi__kgb = DataFrameType(out_data + (wuiqs__rsvwx,),
                        leuf__pkoob, out_columns + ('',))
                else:
                    ibggi__kgb = SeriesType(wuiqs__rsvwx.dtype,
                        wuiqs__rsvwx, leuf__pkoob, None)
        elif isinstance(hbg__hisnz, SeriesType):
            ibggi__kgb = SeriesType(hbg__hisnz.dtype, hbg__hisnz.data,
                leuf__pkoob, hbg__hisnz.name_typ)
        else:
            ibggi__kgb = DataFrameType(hbg__hisnz.data, leuf__pkoob,
                hbg__hisnz.columns)
        zmm__ixcs = gen_apply_pysig(len(f_args), kws.keys())
        ecgql__plsy = (func, *f_args) + tuple(kws.values())
        return signature(ibggi__kgb, *ecgql__plsy).replace(pysig=zmm__ixcs)

    def generic_resolve(self, grpby, attr):
        if self._is_existing_attr(attr):
            return
        if attr not in grpby.df_type.columns:
            raise_bodo_error(
                f'groupby: invalid attribute {attr} (column not found in dataframe or unsupported function)'
                )
        return DataFrameGroupByType(grpby.df_type, grpby.keys, (attr,),
            grpby.as_index, grpby.dropna, True, True, _num_shuffle_keys=
            grpby._num_shuffle_keys)


def _get_groupby_apply_udf_out_type(func, grp, f_args, kws, typing_context,
    target_context):
    ofix__ijxz = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            dpwk__rgxw = grp.selection[0]
            wuiqs__rsvwx = ofix__ijxz.data[ofix__ijxz.column_index[dpwk__rgxw]]
            utvbv__rcdw = SeriesType(wuiqs__rsvwx.dtype, wuiqs__rsvwx,
                ofix__ijxz.index, types.literal(dpwk__rgxw))
        else:
            tbns__yqafn = tuple(ofix__ijxz.data[ofix__ijxz.column_index[
                cjnyq__lwt]] for cjnyq__lwt in grp.selection)
            utvbv__rcdw = DataFrameType(tbns__yqafn, ofix__ijxz.index,
                tuple(grp.selection))
    else:
        utvbv__rcdw = ofix__ijxz
    tthmu__imqiv = utvbv__rcdw,
    tthmu__imqiv += tuple(f_args)
    try:
        hbg__hisnz = get_const_func_output_type(func, tthmu__imqiv, kws,
            typing_context, target_context)
    except Exception as lpln__qvr:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', lpln__qvr),
            getattr(lpln__qvr, 'loc', None))
    return hbg__hisnz


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    tthmu__imqiv = (grp,) + f_args
    try:
        hbg__hisnz = get_const_func_output_type(func, tthmu__imqiv, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as lpln__qvr:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', lpln__qvr),
            getattr(lpln__qvr, 'loc', None))
    zmm__ixcs = gen_apply_pysig(len(f_args), kws.keys())
    ecgql__plsy = (func, *f_args) + tuple(kws.values())
    return signature(hbg__hisnz, *ecgql__plsy).replace(pysig=zmm__ixcs)


def gen_apply_pysig(n_args, kws):
    odl__drhfg = ', '.join(f'arg{hkire__yjyqo}' for hkire__yjyqo in range(
        n_args))
    odl__drhfg = odl__drhfg + ', ' if odl__drhfg else ''
    kqxf__luxce = ', '.join(f"{iag__uqryg} = ''" for iag__uqryg in kws)
    rfc__yhm = f'def apply_stub(func, {odl__drhfg}{kqxf__luxce}):\n'
    rfc__yhm += '    pass\n'
    avs__lwt = {}
    exec(rfc__yhm, {}, avs__lwt)
    xpug__kvwk = avs__lwt['apply_stub']
    return numba.core.utils.pysignature(xpug__kvwk)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        chg__zlkub = types.Array(types.int64, 1, 'C')
        fxcp__rxgda = _pivot_values.meta
        dzwi__jrlk = len(fxcp__rxgda)
        tzl__uadst = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        tjhl__bil = DataFrameType((chg__zlkub,) * dzwi__jrlk, tzl__uadst,
            tuple(fxcp__rxgda))
        return signature(tjhl__bil, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    rfc__yhm = 'def impl(keys, dropna, _is_parallel):\n'
    rfc__yhm += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    rfc__yhm += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{hkire__yjyqo}])' for hkire__yjyqo in range(
        len(keys.types))))
    rfc__yhm += '    table = arr_info_list_to_table(info_list)\n'
    rfc__yhm += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    rfc__yhm += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    rfc__yhm += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    rfc__yhm += '    delete_table_decref_arrays(table)\n'
    rfc__yhm += '    ev.finalize()\n'
    rfc__yhm += '    return sort_idx, group_labels, ngroups\n'
    avs__lwt = {}
    exec(rfc__yhm, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, avs__lwt)
    cxdo__emry = avs__lwt['impl']
    return cxdo__emry


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    clg__vygm = len(labels)
    ymqyq__rkqy = np.zeros(ngroups, dtype=np.int64)
    gilg__iaxer = np.zeros(ngroups, dtype=np.int64)
    otiol__dkdi = 0
    ykzi__jlmwm = 0
    for hkire__yjyqo in range(clg__vygm):
        hqt__wxtf = labels[hkire__yjyqo]
        if hqt__wxtf < 0:
            otiol__dkdi += 1
        else:
            ykzi__jlmwm += 1
            if hkire__yjyqo == clg__vygm - 1 or hqt__wxtf != labels[
                hkire__yjyqo + 1]:
                ymqyq__rkqy[hqt__wxtf] = otiol__dkdi
                gilg__iaxer[hqt__wxtf] = otiol__dkdi + ykzi__jlmwm
                otiol__dkdi += ykzi__jlmwm
                ykzi__jlmwm = 0
    return ymqyq__rkqy, gilg__iaxer


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    cxdo__emry, ktod__pstll = gen_shuffle_dataframe(df, keys, _is_parallel)
    return cxdo__emry


def gen_shuffle_dataframe(df, keys, _is_parallel):
    sxfoh__rdnwl = len(df.columns)
    zql__hdhbc = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    rfc__yhm = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        rfc__yhm += '  return df, keys, get_null_shuffle_info()\n'
        avs__lwt = {}
        exec(rfc__yhm, {'get_null_shuffle_info': get_null_shuffle_info},
            avs__lwt)
        cxdo__emry = avs__lwt['impl']
        return cxdo__emry
    for hkire__yjyqo in range(sxfoh__rdnwl):
        rfc__yhm += f"""  in_arr{hkire__yjyqo} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {hkire__yjyqo})
"""
    rfc__yhm += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    rfc__yhm += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{hkire__yjyqo}])' for hkire__yjyqo in range(
        zql__hdhbc)), ', '.join(f'array_to_info(in_arr{hkire__yjyqo})' for
        hkire__yjyqo in range(sxfoh__rdnwl)), 'array_to_info(in_index_arr)')
    rfc__yhm += '  table = arr_info_list_to_table(info_list)\n'
    rfc__yhm += (
        f'  out_table = shuffle_table(table, {zql__hdhbc}, _is_parallel, 1)\n')
    for hkire__yjyqo in range(zql__hdhbc):
        rfc__yhm += f"""  out_key{hkire__yjyqo} = info_to_array(info_from_table(out_table, {hkire__yjyqo}), keys{hkire__yjyqo}_typ)
"""
    for hkire__yjyqo in range(sxfoh__rdnwl):
        rfc__yhm += f"""  out_arr{hkire__yjyqo} = info_to_array(info_from_table(out_table, {hkire__yjyqo + zql__hdhbc}), in_arr{hkire__yjyqo}_typ)
"""
    rfc__yhm += f"""  out_arr_index = info_to_array(info_from_table(out_table, {zql__hdhbc + sxfoh__rdnwl}), ind_arr_typ)
"""
    rfc__yhm += '  shuffle_info = get_shuffle_info(out_table)\n'
    rfc__yhm += '  delete_table(out_table)\n'
    rfc__yhm += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{hkire__yjyqo}' for hkire__yjyqo in range
        (sxfoh__rdnwl))
    rfc__yhm += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    rfc__yhm += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    rfc__yhm += '  return out_df, ({},), shuffle_info\n'.format(', '.join(
        f'out_key{hkire__yjyqo}' for hkire__yjyqo in range(zql__hdhbc)))
    jvzz__exz = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    jvzz__exz.update({f'keys{hkire__yjyqo}_typ': keys.types[hkire__yjyqo] for
        hkire__yjyqo in range(zql__hdhbc)})
    jvzz__exz.update({f'in_arr{hkire__yjyqo}_typ': df.data[hkire__yjyqo] for
        hkire__yjyqo in range(sxfoh__rdnwl)})
    avs__lwt = {}
    exec(rfc__yhm, jvzz__exz, avs__lwt)
    cxdo__emry = avs__lwt['impl']
    return cxdo__emry, jvzz__exz


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        blwyf__elofs = len(data.array_types)
        rfc__yhm = 'def impl(data, shuffle_info):\n'
        rfc__yhm += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{hkire__yjyqo}])' for hkire__yjyqo in
            range(blwyf__elofs)))
        rfc__yhm += '  table = arr_info_list_to_table(info_list)\n'
        rfc__yhm += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for hkire__yjyqo in range(blwyf__elofs):
            rfc__yhm += f"""  out_arr{hkire__yjyqo} = info_to_array(info_from_table(out_table, {hkire__yjyqo}), data._data[{hkire__yjyqo}])
"""
        rfc__yhm += '  delete_table(out_table)\n'
        rfc__yhm += '  delete_table(table)\n'
        rfc__yhm += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{hkire__yjyqo}' for hkire__yjyqo in
            range(blwyf__elofs))))
        avs__lwt = {}
        exec(rfc__yhm, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, avs__lwt)
        cxdo__emry = avs__lwt['impl']
        return cxdo__emry
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            gxx__kof = bodo.utils.conversion.index_to_array(data)
            ertw__babe = reverse_shuffle(gxx__kof, shuffle_info)
            return bodo.utils.conversion.index_from_array(ertw__babe)
        return impl_index

    def impl_arr(data, shuffle_info):
        fzwzs__vgawp = [array_to_info(data)]
        atbtt__klz = arr_info_list_to_table(fzwzs__vgawp)
        vufpz__iutti = reverse_shuffle_table(atbtt__klz, shuffle_info)
        ertw__babe = info_to_array(info_from_table(vufpz__iutti, 0), data)
        delete_table(vufpz__iutti)
        delete_table(atbtt__klz)
        return ertw__babe
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    anvj__ynjre = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna
        )
    eabfc__ogla = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', anvj__ynjre, eabfc__ogla,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    lqqg__tcil = get_overload_const_bool(ascending)
    qopud__zvgbd = grp.selection[0]
    rfc__yhm = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    znarl__rhv = (
        f"lambda S: S.value_counts(ascending={lqqg__tcil}, _index_name='{qopud__zvgbd}')"
        )
    rfc__yhm += f'    return grp.apply({znarl__rhv})\n'
    avs__lwt = {}
    exec(rfc__yhm, {'bodo': bodo}, avs__lwt)
    cxdo__emry = avs__lwt['impl']
    return cxdo__emry


groupby_unsupported_attr = {'groups', 'indices'}
groupby_unsupported = {'__iter__', 'get_group', 'all', 'any', 'bfill',
    'backfill', 'cumcount', 'cummax', 'cummin', 'cumprod', 'ffill', 'nth',
    'ohlc', 'pad', 'rank', 'pct_change', 'sem', 'tail', 'corr', 'cov',
    'describe', 'diff', 'fillna', 'filter', 'hist', 'mad', 'plot',
    'quantile', 'resample', 'sample', 'skew', 'take', 'tshift'}
series_only_unsupported_attrs = {'is_monotonic_increasing',
    'is_monotonic_decreasing'}
series_only_unsupported = {'nlargest', 'nsmallest', 'unique'}
dataframe_only_unsupported = {'corrwith', 'boxplot'}


def _install_groupby_unsupported():
    for pec__mky in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, pec__mky, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{pec__mky}'))
    for pec__mky in groupby_unsupported:
        overload_method(DataFrameGroupByType, pec__mky, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{pec__mky}'))
    for pec__mky in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, pec__mky, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{pec__mky}'))
    for pec__mky in series_only_unsupported:
        overload_method(DataFrameGroupByType, pec__mky, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{pec__mky}'))
    for pec__mky in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, pec__mky, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{pec__mky}'))


_install_groupby_unsupported()
