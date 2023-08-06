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
        aaw__jcf = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, aaw__jcf)


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
        stntz__qxkjc = args[0]
        xjsko__ndepc = signature.return_type
        mfw__kga = cgutils.create_struct_proxy(xjsko__ndepc)(context, builder)
        mfw__kga.obj = stntz__qxkjc
        context.nrt.incref(builder, signature.args[0], stntz__qxkjc)
        return mfw__kga._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for ayg__hnfo in keys:
        selection.remove(ayg__hnfo)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    if is_overload_constant_int(_num_shuffle_keys):
        jga__sbkj = get_overload_const_int(_num_shuffle_keys)
    else:
        jga__sbkj = -1
    xjsko__ndepc = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False, _num_shuffle_keys=jga__sbkj)
    return xjsko__ndepc(obj_type, by_type, as_index_type, dropna_type,
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
        grpby, mlaau__ryfvb = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(mlaau__ryfvb, (tuple, list)):
                if len(set(mlaau__ryfvb).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(mlaau__ryfvb).difference(set(grpby.
                        df_type.columns))))
                selection = mlaau__ryfvb
            else:
                if mlaau__ryfvb not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(mlaau__ryfvb))
                selection = mlaau__ryfvb,
                series_select = True
            abi__noc = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True,
                series_select, _num_shuffle_keys=grpby._num_shuffle_keys)
            return signature(abi__noc, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, mlaau__ryfvb = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            mlaau__ryfvb):
            abi__noc = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(mlaau__ryfvb)), {}).return_type
            return signature(abi__noc, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    qpn__xngr = arr_type == ArrayItemArrayType(string_array_type)
    obica__ygf = arr_type.dtype
    if isinstance(obica__ygf, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {obica__ygf} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(obica__ygf, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {obica__ygf} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(obica__ygf,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(obica__ygf, (types.Integer, types.Float, types.Boolean)):
        if qpn__xngr or obica__ygf == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(obica__ygf, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not obica__ygf.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {obica__ygf} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(obica__ygf, types.Boolean) and func_name in {'cumsum',
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
    obica__ygf = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(obica__ygf, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(obica__ygf, types.Integer):
            return IntDtype(obica__ygf)
        return obica__ygf
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        ckx__cxde = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{ckx__cxde}'."
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
    for ayg__hnfo in grp.keys:
        if multi_level_names:
            nhsok__kbew = ayg__hnfo, ''
        else:
            nhsok__kbew = ayg__hnfo
        bic__kzedo = grp.df_type.column_index[ayg__hnfo]
        data = grp.df_type.data[bic__kzedo]
        out_columns.append(nhsok__kbew)
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
        cfx__liqt = tuple(grp.df_type.column_index[grp.keys[yhntn__cntl]] for
            yhntn__cntl in range(len(grp.keys)))
        ajh__gbx = tuple(grp.df_type.data[bic__kzedo] for bic__kzedo in
            cfx__liqt)
        index = MultiIndexType(ajh__gbx, tuple(types.StringLiteral(
            ayg__hnfo) for ayg__hnfo in grp.keys))
    else:
        bic__kzedo = grp.df_type.column_index[grp.keys[0]]
        lod__hmaw = grp.df_type.data[bic__kzedo]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(lod__hmaw,
            types.StringLiteral(grp.keys[0]))
    dnwd__tdwtx = {}
    pgzg__nmr = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        dnwd__tdwtx[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        dnwd__tdwtx[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        fwsur__emcqg = dict(ascending=ascending)
        smkt__nnv = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', fwsur__emcqg,
            smkt__nnv, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for gee__bbqw in columns:
            bic__kzedo = grp.df_type.column_index[gee__bbqw]
            data = grp.df_type.data[bic__kzedo]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            uvhgd__ynh = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                uvhgd__ynh = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    nket__ozk = SeriesType(data.dtype, data, None, string_type)
                    ufqu__orq = get_const_func_output_type(func, (nket__ozk
                        ,), {}, typing_context, target_context)
                    if ufqu__orq != ArrayItemArrayType(string_array_type):
                        ufqu__orq = dtype_to_array_type(ufqu__orq)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=gee__bbqw, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    xcqq__thrj = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    bpn__slzl = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    fwsur__emcqg = dict(numeric_only=xcqq__thrj, min_count=
                        bpn__slzl)
                    smkt__nnv = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwsur__emcqg, smkt__nnv, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    xcqq__thrj = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    bpn__slzl = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    fwsur__emcqg = dict(numeric_only=xcqq__thrj, min_count=
                        bpn__slzl)
                    smkt__nnv = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwsur__emcqg, smkt__nnv, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    xcqq__thrj = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    fwsur__emcqg = dict(numeric_only=xcqq__thrj)
                    smkt__nnv = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwsur__emcqg, smkt__nnv, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    lmsz__uno = args[0] if len(args) > 0 else kws.pop('axis', 0
                        )
                    dqq__attm = args[1] if len(args) > 1 else kws.pop('skipna',
                        True)
                    fwsur__emcqg = dict(axis=lmsz__uno, skipna=dqq__attm)
                    smkt__nnv = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwsur__emcqg, smkt__nnv, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    wzuu__dlopk = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    fwsur__emcqg = dict(ddof=wzuu__dlopk)
                    smkt__nnv = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        fwsur__emcqg, smkt__nnv, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                ufqu__orq, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                ufqu__orq = to_str_arr_if_dict_array(ufqu__orq
                    ) if func_name in ('sum', 'cumsum') else ufqu__orq
                out_data.append(ufqu__orq)
                out_columns.append(gee__bbqw)
                if func_name == 'agg':
                    uzpq__ogjiy = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    dnwd__tdwtx[gee__bbqw, uzpq__ogjiy] = gee__bbqw
                else:
                    dnwd__tdwtx[gee__bbqw, func_name] = gee__bbqw
                out_column_type.append(uvhgd__ynh)
            else:
                pgzg__nmr.append(err_msg)
    if func_name == 'sum':
        brnjk__revr = any([(wbci__irgob == ColumnType.NumericalColumn.value
            ) for wbci__irgob in out_column_type])
        if brnjk__revr:
            out_data = [wbci__irgob for wbci__irgob, axbs__vyxm in zip(
                out_data, out_column_type) if axbs__vyxm != ColumnType.
                NonNumericalColumn.value]
            out_columns = [wbci__irgob for wbci__irgob, axbs__vyxm in zip(
                out_columns, out_column_type) if axbs__vyxm != ColumnType.
                NonNumericalColumn.value]
            dnwd__tdwtx = {}
            for gee__bbqw in out_columns:
                if grp.as_index is False and gee__bbqw in grp.keys:
                    continue
                dnwd__tdwtx[gee__bbqw, func_name] = gee__bbqw
    btx__iwqwn = len(pgzg__nmr)
    if len(out_data) == 0:
        if btx__iwqwn == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(btx__iwqwn, ' was' if btx__iwqwn == 1 else 's were',
                ','.join(pgzg__nmr)))
    dnz__pvzn = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            qrj__irz = IntDtype(out_data[0].dtype)
        else:
            qrj__irz = out_data[0].dtype
        yysl__xio = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        dnz__pvzn = SeriesType(qrj__irz, data=out_data[0], index=index,
            name_typ=yysl__xio)
    return signature(dnz__pvzn, *args), dnwd__tdwtx


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    cefc__gauk = True
    if isinstance(f_val, str):
        cefc__gauk = False
        mhh__nzltn = f_val
    elif is_overload_constant_str(f_val):
        cefc__gauk = False
        mhh__nzltn = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        cefc__gauk = False
        mhh__nzltn = bodo.utils.typing.get_builtin_function_name(f_val)
    if not cefc__gauk:
        if mhh__nzltn not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {mhh__nzltn}')
        abi__noc = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp.
            as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(abi__noc, (), mhh__nzltn, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            dtj__vey = types.functions.MakeFunctionLiteral(f_val)
        else:
            dtj__vey = f_val
        validate_udf('agg', dtj__vey)
        func = get_overload_const_func(dtj__vey, None)
        pluwu__rrr = func.code if hasattr(func, 'code') else func.__code__
        mhh__nzltn = pluwu__rrr.co_name
        abi__noc = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp.
            as_index, grp.dropna, True, True, _num_shuffle_keys=grp.
            _num_shuffle_keys)
        out_tp = get_agg_typ(abi__noc, (), 'agg', typing_context,
            target_context, dtj__vey)[0].return_type
    return mhh__nzltn, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    xpc__std = kws and all(isinstance(ibvaw__sosxo, types.Tuple) and len(
        ibvaw__sosxo) == 2 for ibvaw__sosxo in kws.values())
    if is_overload_none(func) and not xpc__std:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not xpc__std:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    xpwm__kiver = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if xpc__std or is_overload_constant_dict(func):
        if xpc__std:
            kbhpc__uve = [get_literal_value(oxiel__bvu) for oxiel__bvu,
                zzktu__hwme in kws.values()]
            cpub__ptm = [get_literal_value(sfi__drkgk) for zzktu__hwme,
                sfi__drkgk in kws.values()]
        else:
            fgyqa__ceo = get_overload_constant_dict(func)
            kbhpc__uve = tuple(fgyqa__ceo.keys())
            cpub__ptm = tuple(fgyqa__ceo.values())
        for mpg__sgjx in ('head', 'ngroup'):
            if mpg__sgjx in cpub__ptm:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {mpg__sgjx} cannot be mixed with other groupby operations.'
                    )
        if any(gee__bbqw not in grp.selection and gee__bbqw not in grp.keys for
            gee__bbqw in kbhpc__uve):
            raise_bodo_error(
                f'Selected column names {kbhpc__uve} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            cpub__ptm)
        if xpc__std and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        dnwd__tdwtx = {}
        out_columns = []
        out_data = []
        out_column_type = []
        dcnz__emm = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for rib__gmuz, f_val in zip(kbhpc__uve, cpub__ptm):
            if isinstance(f_val, (tuple, list)):
                evvr__ian = 0
                for dtj__vey in f_val:
                    mhh__nzltn, out_tp = get_agg_funcname_and_outtyp(grp,
                        rib__gmuz, dtj__vey, typing_context, target_context)
                    xpwm__kiver = mhh__nzltn in list_cumulative
                    if mhh__nzltn == '<lambda>' and len(f_val) > 1:
                        mhh__nzltn = '<lambda_' + str(evvr__ian) + '>'
                        evvr__ian += 1
                    out_columns.append((rib__gmuz, mhh__nzltn))
                    dnwd__tdwtx[rib__gmuz, mhh__nzltn] = rib__gmuz, mhh__nzltn
                    _append_out_type(grp, out_data, out_tp)
            else:
                mhh__nzltn, out_tp = get_agg_funcname_and_outtyp(grp,
                    rib__gmuz, f_val, typing_context, target_context)
                xpwm__kiver = mhh__nzltn in list_cumulative
                if multi_level_names:
                    out_columns.append((rib__gmuz, mhh__nzltn))
                    dnwd__tdwtx[rib__gmuz, mhh__nzltn] = rib__gmuz, mhh__nzltn
                elif not xpc__std:
                    out_columns.append(rib__gmuz)
                    dnwd__tdwtx[rib__gmuz, mhh__nzltn] = rib__gmuz
                elif xpc__std:
                    dcnz__emm.append(mhh__nzltn)
                _append_out_type(grp, out_data, out_tp)
        if xpc__std:
            for yhntn__cntl, ksn__gvjp in enumerate(kws.keys()):
                out_columns.append(ksn__gvjp)
                dnwd__tdwtx[kbhpc__uve[yhntn__cntl], dcnz__emm[yhntn__cntl]
                    ] = ksn__gvjp
        if xpwm__kiver:
            index = grp.df_type.index
        else:
            index = out_tp.index
        dnz__pvzn = DataFrameType(tuple(out_data), index, tuple(out_columns
            ), is_table_format=True)
        return signature(dnz__pvzn, *args), dnwd__tdwtx
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            lbjyf__eimt = get_overload_const_list(func)
        else:
            lbjyf__eimt = func.types
        if len(lbjyf__eimt) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        evvr__ian = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        dnwd__tdwtx = {}
        wpj__eginj = grp.selection[0]
        for f_val in lbjyf__eimt:
            mhh__nzltn, out_tp = get_agg_funcname_and_outtyp(grp,
                wpj__eginj, f_val, typing_context, target_context)
            xpwm__kiver = mhh__nzltn in list_cumulative
            if mhh__nzltn == '<lambda>' and len(lbjyf__eimt) > 1:
                mhh__nzltn = '<lambda_' + str(evvr__ian) + '>'
                evvr__ian += 1
            out_columns.append(mhh__nzltn)
            dnwd__tdwtx[wpj__eginj, mhh__nzltn] = mhh__nzltn
            _append_out_type(grp, out_data, out_tp)
        if xpwm__kiver:
            index = grp.df_type.index
        else:
            index = out_tp.index
        dnz__pvzn = DataFrameType(tuple(out_data), index, tuple(out_columns
            ), is_table_format=True)
        return signature(dnz__pvzn, *args), dnwd__tdwtx
    mhh__nzltn = ''
    if types.unliteral(func) == types.unicode_type:
        mhh__nzltn = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        mhh__nzltn = bodo.utils.typing.get_builtin_function_name(func)
    if mhh__nzltn:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, mhh__nzltn, typing_context, kws)
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
        lmsz__uno = args[0] if len(args) > 0 else kws.pop('axis', 0)
        xcqq__thrj = args[1] if len(args) > 1 else kws.pop('numeric_only', 
            False)
        dqq__attm = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        fwsur__emcqg = dict(axis=lmsz__uno, numeric_only=xcqq__thrj)
        smkt__nnv = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', fwsur__emcqg,
            smkt__nnv, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        fre__xws = args[0] if len(args) > 0 else kws.pop('periods', 1)
        vgkb__xfry = args[1] if len(args) > 1 else kws.pop('freq', None)
        lmsz__uno = args[2] if len(args) > 2 else kws.pop('axis', 0)
        pyqc__cpog = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        fwsur__emcqg = dict(freq=vgkb__xfry, axis=lmsz__uno, fill_value=
            pyqc__cpog)
        smkt__nnv = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', fwsur__emcqg,
            smkt__nnv, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        hsdde__sgr = args[0] if len(args) > 0 else kws.pop('func', None)
        fueg__qlwq = kws.pop('engine', None)
        yooa__lfb = kws.pop('engine_kwargs', None)
        fwsur__emcqg = dict(engine=fueg__qlwq, engine_kwargs=yooa__lfb)
        smkt__nnv = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', fwsur__emcqg,
            smkt__nnv, package_name='pandas', module_name='GroupBy')
    dnwd__tdwtx = {}
    for gee__bbqw in grp.selection:
        out_columns.append(gee__bbqw)
        dnwd__tdwtx[gee__bbqw, name_operation] = gee__bbqw
        bic__kzedo = grp.df_type.column_index[gee__bbqw]
        data = grp.df_type.data[bic__kzedo]
        yslc__glx = (name_operation if name_operation != 'transform' else
            get_literal_value(hsdde__sgr))
        if yslc__glx in ('sum', 'cumsum'):
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
            ufqu__orq, err_msg = get_groupby_output_dtype(data,
                get_literal_value(hsdde__sgr), grp.df_type.index)
            if err_msg == 'ok':
                data = ufqu__orq
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    dnz__pvzn = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        dnz__pvzn = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(dnz__pvzn, *args), dnwd__tdwtx


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
        lkik__sdb = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        zbw__yrbvo = isinstance(lkik__sdb, (SeriesType,
            HeterogeneousSeriesType)
            ) and lkik__sdb.const_info is not None or not isinstance(lkik__sdb,
            (SeriesType, DataFrameType))
        if zbw__yrbvo:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                qqag__xex = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                cfx__liqt = tuple(grp.df_type.column_index[grp.keys[
                    yhntn__cntl]] for yhntn__cntl in range(len(grp.keys)))
                ajh__gbx = tuple(grp.df_type.data[bic__kzedo] for
                    bic__kzedo in cfx__liqt)
                qqag__xex = MultiIndexType(ajh__gbx, tuple(types.literal(
                    ayg__hnfo) for ayg__hnfo in grp.keys))
            else:
                bic__kzedo = grp.df_type.column_index[grp.keys[0]]
                lod__hmaw = grp.df_type.data[bic__kzedo]
                qqag__xex = bodo.hiframes.pd_index_ext.array_type_to_index(
                    lod__hmaw, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            afg__yjxl = tuple(grp.df_type.data[grp.df_type.column_index[
                gee__bbqw]] for gee__bbqw in grp.keys)
            gpfu__ana = tuple(types.literal(ibvaw__sosxo) for ibvaw__sosxo in
                grp.keys) + get_index_name_types(lkik__sdb.index)
            if not grp.as_index:
                afg__yjxl = types.Array(types.int64, 1, 'C'),
                gpfu__ana = (types.none,) + get_index_name_types(lkik__sdb.
                    index)
            qqag__xex = MultiIndexType(afg__yjxl + get_index_data_arr_types
                (lkik__sdb.index), gpfu__ana)
        if zbw__yrbvo:
            if isinstance(lkik__sdb, HeterogeneousSeriesType):
                zzktu__hwme, wtjal__dnwei = lkik__sdb.const_info
                if isinstance(lkik__sdb.data, bodo.libs.nullable_tuple_ext.
                    NullableTupleType):
                    vxdb__xhqti = lkik__sdb.data.tuple_typ.types
                elif isinstance(lkik__sdb.data, types.Tuple):
                    vxdb__xhqti = lkik__sdb.data.types
                vtm__oyzb = tuple(to_nullable_type(dtype_to_array_type(
                    vre__icyy)) for vre__icyy in vxdb__xhqti)
                mvnnv__ojda = DataFrameType(out_data + vtm__oyzb, qqag__xex,
                    out_columns + wtjal__dnwei)
            elif isinstance(lkik__sdb, SeriesType):
                fphsb__kvtu, wtjal__dnwei = lkik__sdb.const_info
                vtm__oyzb = tuple(to_nullable_type(dtype_to_array_type(
                    lkik__sdb.dtype)) for zzktu__hwme in range(fphsb__kvtu))
                mvnnv__ojda = DataFrameType(out_data + vtm__oyzb, qqag__xex,
                    out_columns + wtjal__dnwei)
            else:
                cllw__lek = get_udf_out_arr_type(lkik__sdb)
                if not grp.as_index:
                    mvnnv__ojda = DataFrameType(out_data + (cllw__lek,),
                        qqag__xex, out_columns + ('',))
                else:
                    mvnnv__ojda = SeriesType(cllw__lek.dtype, cllw__lek,
                        qqag__xex, None)
        elif isinstance(lkik__sdb, SeriesType):
            mvnnv__ojda = SeriesType(lkik__sdb.dtype, lkik__sdb.data,
                qqag__xex, lkik__sdb.name_typ)
        else:
            mvnnv__ojda = DataFrameType(lkik__sdb.data, qqag__xex,
                lkik__sdb.columns)
        fttr__pisq = gen_apply_pysig(len(f_args), kws.keys())
        txfka__phhn = (func, *f_args) + tuple(kws.values())
        return signature(mvnnv__ojda, *txfka__phhn).replace(pysig=fttr__pisq)

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
    cil__lzqnk = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            rib__gmuz = grp.selection[0]
            cllw__lek = cil__lzqnk.data[cil__lzqnk.column_index[rib__gmuz]]
            jxp__oghmr = SeriesType(cllw__lek.dtype, cllw__lek, cil__lzqnk.
                index, types.literal(rib__gmuz))
        else:
            wgalt__wen = tuple(cil__lzqnk.data[cil__lzqnk.column_index[
                gee__bbqw]] for gee__bbqw in grp.selection)
            jxp__oghmr = DataFrameType(wgalt__wen, cil__lzqnk.index, tuple(
                grp.selection))
    else:
        jxp__oghmr = cil__lzqnk
    sbz__mhx = jxp__oghmr,
    sbz__mhx += tuple(f_args)
    try:
        lkik__sdb = get_const_func_output_type(func, sbz__mhx, kws,
            typing_context, target_context)
    except Exception as aujhn__ugs:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', aujhn__ugs),
            getattr(aujhn__ugs, 'loc', None))
    return lkik__sdb


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    sbz__mhx = (grp,) + f_args
    try:
        lkik__sdb = get_const_func_output_type(func, sbz__mhx, kws, self.
            context, numba.core.registry.cpu_target.target_context, False)
    except Exception as aujhn__ugs:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', aujhn__ugs
            ), getattr(aujhn__ugs, 'loc', None))
    fttr__pisq = gen_apply_pysig(len(f_args), kws.keys())
    txfka__phhn = (func, *f_args) + tuple(kws.values())
    return signature(lkik__sdb, *txfka__phhn).replace(pysig=fttr__pisq)


def gen_apply_pysig(n_args, kws):
    shdl__ikcv = ', '.join(f'arg{yhntn__cntl}' for yhntn__cntl in range(n_args)
        )
    shdl__ikcv = shdl__ikcv + ', ' if shdl__ikcv else ''
    pmlp__tjqel = ', '.join(f"{nfwjy__lbog} = ''" for nfwjy__lbog in kws)
    nfhg__mfwm = f'def apply_stub(func, {shdl__ikcv}{pmlp__tjqel}):\n'
    nfhg__mfwm += '    pass\n'
    fyhwj__eqd = {}
    exec(nfhg__mfwm, {}, fyhwj__eqd)
    cwhah__cbqm = fyhwj__eqd['apply_stub']
    return numba.core.utils.pysignature(cwhah__cbqm)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        mjxrq__qpia = types.Array(types.int64, 1, 'C')
        uixeo__innb = _pivot_values.meta
        hxpd__wqlzf = len(uixeo__innb)
        quv__jnh = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        oph__ipbbp = DataFrameType((mjxrq__qpia,) * hxpd__wqlzf, quv__jnh,
            tuple(uixeo__innb))
        return signature(oph__ipbbp, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    nfhg__mfwm = 'def impl(keys, dropna, _is_parallel):\n'
    nfhg__mfwm += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    nfhg__mfwm += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{yhntn__cntl}])' for yhntn__cntl in range(len(
        keys.types))))
    nfhg__mfwm += '    table = arr_info_list_to_table(info_list)\n'
    nfhg__mfwm += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    nfhg__mfwm += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    nfhg__mfwm += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    nfhg__mfwm += '    delete_table_decref_arrays(table)\n'
    nfhg__mfwm += '    ev.finalize()\n'
    nfhg__mfwm += '    return sort_idx, group_labels, ngroups\n'
    fyhwj__eqd = {}
    exec(nfhg__mfwm, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, fyhwj__eqd)
    gnuo__yhat = fyhwj__eqd['impl']
    return gnuo__yhat


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    wimn__fabeq = len(labels)
    msyqk__err = np.zeros(ngroups, dtype=np.int64)
    cmoa__vkey = np.zeros(ngroups, dtype=np.int64)
    vfpzg__mzf = 0
    sxi__wrry = 0
    for yhntn__cntl in range(wimn__fabeq):
        ppj__rfeb = labels[yhntn__cntl]
        if ppj__rfeb < 0:
            vfpzg__mzf += 1
        else:
            sxi__wrry += 1
            if yhntn__cntl == wimn__fabeq - 1 or ppj__rfeb != labels[
                yhntn__cntl + 1]:
                msyqk__err[ppj__rfeb] = vfpzg__mzf
                cmoa__vkey[ppj__rfeb] = vfpzg__mzf + sxi__wrry
                vfpzg__mzf += sxi__wrry
                sxi__wrry = 0
    return msyqk__err, cmoa__vkey


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    gnuo__yhat, zzktu__hwme = gen_shuffle_dataframe(df, keys, _is_parallel)
    return gnuo__yhat


def gen_shuffle_dataframe(df, keys, _is_parallel):
    fphsb__kvtu = len(df.columns)
    wwgrf__wfuj = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    nfhg__mfwm = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        nfhg__mfwm += '  return df, keys, get_null_shuffle_info()\n'
        fyhwj__eqd = {}
        exec(nfhg__mfwm, {'get_null_shuffle_info': get_null_shuffle_info},
            fyhwj__eqd)
        gnuo__yhat = fyhwj__eqd['impl']
        return gnuo__yhat
    for yhntn__cntl in range(fphsb__kvtu):
        nfhg__mfwm += f"""  in_arr{yhntn__cntl} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {yhntn__cntl})
"""
    nfhg__mfwm += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    nfhg__mfwm += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{yhntn__cntl}])' for yhntn__cntl in range(
        wwgrf__wfuj)), ', '.join(f'array_to_info(in_arr{yhntn__cntl})' for
        yhntn__cntl in range(fphsb__kvtu)), 'array_to_info(in_index_arr)')
    nfhg__mfwm += '  table = arr_info_list_to_table(info_list)\n'
    nfhg__mfwm += (
        f'  out_table = shuffle_table(table, {wwgrf__wfuj}, _is_parallel, 1)\n'
        )
    for yhntn__cntl in range(wwgrf__wfuj):
        nfhg__mfwm += f"""  out_key{yhntn__cntl} = info_to_array(info_from_table(out_table, {yhntn__cntl}), keys{yhntn__cntl}_typ)
"""
    for yhntn__cntl in range(fphsb__kvtu):
        nfhg__mfwm += f"""  out_arr{yhntn__cntl} = info_to_array(info_from_table(out_table, {yhntn__cntl + wwgrf__wfuj}), in_arr{yhntn__cntl}_typ)
"""
    nfhg__mfwm += f"""  out_arr_index = info_to_array(info_from_table(out_table, {wwgrf__wfuj + fphsb__kvtu}), ind_arr_typ)
"""
    nfhg__mfwm += '  shuffle_info = get_shuffle_info(out_table)\n'
    nfhg__mfwm += '  delete_table(out_table)\n'
    nfhg__mfwm += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{yhntn__cntl}' for yhntn__cntl in range(
        fphsb__kvtu))
    nfhg__mfwm += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    nfhg__mfwm += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    nfhg__mfwm += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{yhntn__cntl}' for yhntn__cntl in range(wwgrf__wfuj)))
    gpcnw__sft = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    gpcnw__sft.update({f'keys{yhntn__cntl}_typ': keys.types[yhntn__cntl] for
        yhntn__cntl in range(wwgrf__wfuj)})
    gpcnw__sft.update({f'in_arr{yhntn__cntl}_typ': df.data[yhntn__cntl] for
        yhntn__cntl in range(fphsb__kvtu)})
    fyhwj__eqd = {}
    exec(nfhg__mfwm, gpcnw__sft, fyhwj__eqd)
    gnuo__yhat = fyhwj__eqd['impl']
    return gnuo__yhat, gpcnw__sft


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        cvauc__uhtk = len(data.array_types)
        nfhg__mfwm = 'def impl(data, shuffle_info):\n'
        nfhg__mfwm += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{yhntn__cntl}])' for yhntn__cntl in
            range(cvauc__uhtk)))
        nfhg__mfwm += '  table = arr_info_list_to_table(info_list)\n'
        nfhg__mfwm += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for yhntn__cntl in range(cvauc__uhtk):
            nfhg__mfwm += f"""  out_arr{yhntn__cntl} = info_to_array(info_from_table(out_table, {yhntn__cntl}), data._data[{yhntn__cntl}])
"""
        nfhg__mfwm += '  delete_table(out_table)\n'
        nfhg__mfwm += '  delete_table(table)\n'
        nfhg__mfwm += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{yhntn__cntl}' for yhntn__cntl in
            range(cvauc__uhtk))))
        fyhwj__eqd = {}
        exec(nfhg__mfwm, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, fyhwj__eqd)
        gnuo__yhat = fyhwj__eqd['impl']
        return gnuo__yhat
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            cgav__ieie = bodo.utils.conversion.index_to_array(data)
            wcam__yjlr = reverse_shuffle(cgav__ieie, shuffle_info)
            return bodo.utils.conversion.index_from_array(wcam__yjlr)
        return impl_index

    def impl_arr(data, shuffle_info):
        kqfty__vqwrs = [array_to_info(data)]
        kpug__pzrqw = arr_info_list_to_table(kqfty__vqwrs)
        zrvcb__ayvh = reverse_shuffle_table(kpug__pzrqw, shuffle_info)
        wcam__yjlr = info_to_array(info_from_table(zrvcb__ayvh, 0), data)
        delete_table(zrvcb__ayvh)
        delete_table(kpug__pzrqw)
        return wcam__yjlr
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    fwsur__emcqg = dict(normalize=normalize, sort=sort, bins=bins, dropna=
        dropna)
    smkt__nnv = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', fwsur__emcqg, smkt__nnv,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    qpmk__uaga = get_overload_const_bool(ascending)
    phikl__tdzij = grp.selection[0]
    nfhg__mfwm = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    wgbbb__jst = (
        f"lambda S: S.value_counts(ascending={qpmk__uaga}, _index_name='{phikl__tdzij}')"
        )
    nfhg__mfwm += f'    return grp.apply({wgbbb__jst})\n'
    fyhwj__eqd = {}
    exec(nfhg__mfwm, {'bodo': bodo}, fyhwj__eqd)
    gnuo__yhat = fyhwj__eqd['impl']
    return gnuo__yhat


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
    for frkq__yvp in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, frkq__yvp, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{frkq__yvp}'))
    for frkq__yvp in groupby_unsupported:
        overload_method(DataFrameGroupByType, frkq__yvp, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{frkq__yvp}'))
    for frkq__yvp in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, frkq__yvp, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{frkq__yvp}'))
    for frkq__yvp in series_only_unsupported:
        overload_method(DataFrameGroupByType, frkq__yvp, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{frkq__yvp}'))
    for frkq__yvp in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, frkq__yvp, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{frkq__yvp}'))


_install_groupby_unsupported()
